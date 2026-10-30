"""Feature contracts in a real DOM, without a server, accounts, or model calls."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from mathlottery.web.server import ASSETS

STATIC = Path(__file__).parents[1] / "src/mathlottery/web/static"
MODULES = ("dom.js", "i18n.js", "model-selector.js", "account-panel.js", "solve-teams.js")


def test_all_browser_scripts_are_packaged_http_assets():
    class Scripts(HTMLParser):
        def __init__(self):
            super().__init__()
            self.sources = []

        def handle_starttag(self, tag, attrs):
            if tag == "script":
                self.sources.append(dict(attrs)["src"])

    scripts = Scripts()
    scripts.feed((STATIC / "index.html").read_text())
    assert scripts.sources[-1] == "/app.js"
    assert len(scripts.sources) == len(set(scripts.sources))
    for source in scripts.sources:
        name, content_type = ASSETS[source]
        assert (STATIC / name).is_file()
        assert content_type.startswith("text/javascript")
    assert {f"/{name}" for name in MODULES} <= set(scripts.sources)


@pytest.fixture(scope="module")
def browser():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as engine:
        if not Path(engine.chromium.executable_path).is_file():
            pytest.skip("Install Playwright Chromium to run DOM component tests")
        instance = engine.chromium.launch(headless=True)
        yield instance
        instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    context.route("**/*", lambda route: route.abort())
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    # Use the real form markup. Only the feature under test owns listeners/state.
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", (STATIC / "index.html").read_text(), flags=re.S)
    page.set_content(html)
    for module in MODULES:
        page.add_script_tag(path=str(STATIC / module))
    yield page
    context.close()
    assert errors == []


def prepare_models(page):
    page.evaluate("""() => {
      window.settings = {provider: 'codex', backend: 'codex', model: 'native-model', reasoning_effort: 'max'};
      window.requests = [];
      window.models = MathLotteryModels.create({
        root: document.querySelector('#task-form'), settings: () => settings,
        translate: key => MathLotteryI18n.translate('en', key),
        request: path => new Promise((resolve, reject) => requests.push({path, resolve, reject})),
        onChange: () => models.render(),
      });
      models.render();
    }""")


def resolve_models(page, index, provider, models):
    page.evaluate("""({index, provider, models}) => requests[index].resolve({
      provider, models, source: 'live',
      providers: [{id: provider, label: provider, transport: provider === 'codex' ? 'codex' : 'responses', reasoning_modes: []}],
    })""", {"index": index, "provider": provider, "models": models})


def test_model_catalog_race_does_not_restore_previous_provider(page):
    prepare_models(page)
    page.evaluate("() => { void models.load(); }")
    page.select_option("#backend", "chat")
    resolve_models(page, 1, "chat", [{"id": "api-model", "reasoning_efforts": ["high"]}])
    resolve_models(page, 0, "codex", [{"id": "stale-native-model", "reasoning_efforts": ["max"]}])
    assert page.evaluate("models.provider()") == "chat"
    assert page.evaluate("models.backend()") == "chat"
    assert "api-model" in page.locator("#model-select").text_content()
    assert "stale-native-model" not in page.locator("#model-select").text_content()
    assert page.evaluate("models.overrides()") == {
        "provider": "chat", "model": None, "reasoning_effort": None, "reasoning_mode": None,
    }
    page.evaluate("models.ensureLoaded()")
    assert page.evaluate("requests.length") == 2


def test_model_changes_reset_inheritance_and_catalog_gaps_preserve_explicit_choices(page):
    prepare_models(page)
    page.evaluate("() => { void models.load(); }")
    resolve_models(page, 0, "codex", [
        {"id": "native-model", "reasoning_efforts": ["max"]},
        {"id": "another-model", "reasoning_efforts": ["low", "high"]},
    ])
    assert page.evaluate("models.block()") == ""
    page.select_option("#model-select", "another-model")
    assert page.evaluate("models.overrides().reasoning_effort") is None
    page.select_option("#effort-select", "high")
    page.evaluate("() => { void models.load(true); }")
    resolve_models(page, 1, "codex", [{"id": "another-model", "reasoning_efforts": ["low"]}])
    assert page.input_value("#effort-select") == "high"
    assert "high" in page.evaluate("models.block()")
    page.evaluate("() => { void models.load(true); }")
    page.evaluate("requests[2].reject(new Error('Catalog temporarily unavailable'))")
    assert page.input_value("#model-select") == "another-model"
    assert page.input_value("#effort-select") == "high"
    assert page.evaluate("models.block()") == ""
    assert "high" in page.locator("#model-capability-warning").text_content()
    assert "temporarily unavailable" in page.locator("#models-error").text_content()


def test_codex_catalogue_auth_switch_ignores_subscription_response(page):
    prepare_models(page)
    page.evaluate("() => { void models.load(); }")
    page.select_option("#codex-auth", "api_key")
    resolve_models(page, 1, "codex", [{"id": "api-model", "reasoning_efforts": ["high"]}])
    resolve_models(page, 0, "codex", [{"id": "subscription-model", "reasoning_efforts": ["max"]}])
    assert "api-model" in page.locator("#model-select").text_content()
    assert "subscription-model" not in page.locator("#model-select").text_content()
    assert page.evaluate("requests[1].path") == "/api/models?provider=codex&codex_auth=api_key&codex_api_key_env=OPENAI_API_KEY"
    assert page.evaluate("models.overrides().codex_auth") == "api_key"
    page.fill("#codex-key-env", "sk-not-a-variable-name")
    assert "variable name" in page.evaluate("models.block()")
    page.fill("#codex-key-env", "RESEARCH_API_KEY")
    assert page.evaluate("models.overrides().codex_api_key_env") == "RESEARCH_API_KEY"
    page.select_option("#backend", "chat")
    assert page.locator("#codex-auth-fields").is_hidden()
    assert "codex_auth" not in page.evaluate("models.overrides()")
    assert "codex_api_key_env" not in page.evaluate("models.overrides()")


def test_account_api_view_uses_saved_auth_for_resume_and_makes_no_subscription_requests(page):
    result = page.evaluate("""async () => {
      const calls = [];
      const account = MathLotteryAccount.create({
        root: document.querySelector('#account-panel'), translate: key => key,
        connection: () => ({backend: 'codex', codex_auth: 'api_key', codex_api_key_env: 'RESEARCH_KEY', api_key_configured: true}),
        request: async path => { calls.push(path); return {available: true, authenticated: false}; },
        onChange: () => {}, notify: () => {},
      });
      account.render(true); account.ensureLoaded(); await account.refresh();
      return {calls, apiBlock: account.block('codex', {codex_auth: 'api_key'}), subscriptionBlock: account.block('codex', {codex_auth: 'chatgpt'})};
    }""")
    assert result == {"calls": [], "apiBlock": "", "subscriptionBlock": "readinessChecking"}
    assert page.locator("#account-login").is_hidden()
    assert page.locator("#account-switch").is_hidden()
    assert page.locator("#account-details").text_content() == "apiKeyEnv: RESEARCH_KEY"


def test_account_failure_clears_old_identity_and_rechecks_workspace_status(page):
    result = page.evaluate("""async () => {
      const calls = [], signedIn = {available: true, authenticated: true, account: {type: 'chatgpt', email: 'u***@example.test'}};
      const responses = [signedIn, new Error('Account request failed'), {available: true, authenticated: false}];
      window.confirm = () => true;
      window.account = MathLotteryAccount.create({
        root: document.querySelector('#account-panel'), translate: key => key,
        request: async (path, body) => { calls.push({path, body}); const result = responses.shift(); if (result instanceof Error) throw result; return result; },
        onChange: () => {}, notify: () => {},
      });
      account.render(true);
      await account.refresh();
      const connected = account.block('codex');
      await account.refresh('logout');
      return {calls, connected, blocked: account.block('codex'), apiBlocked: account.block('chat')};
    }""")
    assert result == {"calls": [
        {"path": "/api/account", "body": None},
        {"path": "/api/account/logout", "body": {"confirm_account_change": True}},
        {"path": "/api/account", "body": None},
    ], "connected": "", "blocked": "readinessSignIn", "apiBlocked": ""}
    assert page.locator("#account-details").text_content() == ""
    assert page.locator("#account-error").text_content() == "Account request failed"
    assert not page.locator("#account-login").is_disabled()
    page.evaluate("account.render(false)")
    assert page.locator("#account-login").is_disabled()


@pytest.mark.parametrize("url", [
    "http://auth.openai.com/device", "https://auth.openai.com.evil.test/device",
    "https://user:pass@chatgpt.com/device", "https://auth.openai.com:8443/device", "javascript:alert(1)",
])
def test_account_panel_does_not_make_untrusted_login_links_clickable(page, url):
    result = page.evaluate("""async url => {
      const account = MathLotteryAccount.create({
        root: document.querySelector('#account-panel'), translate: key => key,
        request: async () => ({available: true, login: {status: 'pending', url, user_code: 'TEST-CODE'}}),
        onChange: () => {}, notify: () => {},
      });
      account.render(true);
      await account.refresh();
      return {pending: account.pending, blocked: account.block('codex')};
    }""", url)
    assert result == {"pending": True, "blocked": "readinessPending"}
    assert page.get_attribute("#account-link", "href") is None
    assert page.locator("#account-code").text_content() == ""
    assert page.locator("#account-error").text_content() == "accountInvalidLink"


def test_solve_team_view_preserves_disclosures_and_keeps_untrusted_text_inert(page):
    data = {
        "id": "example-run", "busy": True, "solve_team": {
            "parallel_agents": 4, "max_groups": 1, "rounds": 1,
            "groups": [{"id": "group-a", "agents": 4, "mode": "peer", "objective": "Check a lemma"}],
            "workers": [{"id": "worker-a", "group": "group-a", "state": "running",
                         "progress": {"text": "<img src=x onerror=alert(1)>"}}],
            "messages": [{"key": "message-a", "group": "group-a", "standing": "unverified",
                          "title": "A proposed lemma", "body": "<script>alert(1)</script>",
                          "assumptions": ["x > 0"], "depends_on": [],
                          "artifacts": [{"source": "proof.md", "sha256": "a" * 64}]}],
        },
    }
    page.evaluate("""run => {
      window.run = run;
      window.teams = MathLotterySolveTeams.create(document.querySelector('#solve-team'));
      teams.render(run, 'en');
    }""", data)
    assert "Research concurrency: 1 / 4" in page.locator("#solve-team").text_content()
    assert "Group cap: 1" in page.locator("#solve-team").text_content()
    assert page.locator("#solve-team img, #solve-team script").count() == 0
    assert "<script>alert(1)</script>" in page.locator("#solve-team").text_content()
    page.evaluate("""() => {
      document.querySelector('[data-key="solve-board"]').open = true;
      document.querySelector('[data-key="message-a"]').open = true;
      run.solve_team.rounds += 1;
      teams.render(run, 'zh');
    }""")
    assert page.locator('[data-key="solve-board"]').evaluate("node => node.open")
    assert page.locator('[data-key="message-a"]').evaluate("node => node.open")
    assert "组数上限: 1" in page.locator("#solve-team").text_content()
    assert page.get_attribute("#solve-team a", "href") == f"/api/runs/example-run/solve-material?sha256={'a' * 64}"
    # Independent panels must not share a signature cache and suppress each other.
    assert page.evaluate("""() => {
      const panel = document.createElement('section');
      MathLotterySolveTeams.create(panel).render(run, 'zh');
      return panel.textContent === document.querySelector('#solve-team').textContent;
    }""")
