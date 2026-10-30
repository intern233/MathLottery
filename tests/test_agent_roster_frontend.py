"""Browser contracts for per-slot setup; no real accounts or model requests."""

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

import pytest

STATIC = Path(__file__).parents[1] / "src/mathlottery/web/static"


@pytest.fixture(scope="module")
def browser():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as engine:
        if not Path(engine.chromium.executable_path).is_file():
            pytest.skip("Install Playwright Chromium for browser tests")
        instance = engine.chromium.launch(headless=True)
        yield instance
        instance.close()


def slot(number, mode="codex"):
    return {
        "id": f"agent-{number}", "label": None,
        "backend": {
            "mode": mode, "execution": "native", "model": "example-model",
            "reasoning_effort": "max", "codex_identity": f"agent-{number}" if mode == "codex" else None,
            "chat": {"api_key_env": f"AGENT_{number}_API_KEY", "base_url": "https://api.example.com/v1", "tools": []},
        },
    }


@pytest.fixture
def ui(browser):
    context = browser.new_context(locale="en-US", viewport={"width": 1360, "height": 1000})
    data = {"slots": [], "calls": [], "accounts": {}, "settings": {}, "workspace_account": None, "login_url": "https://auth.openai.com/codex/device"}
    errors = []
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))

    def route(request):
        url = urlsplit(request.request.url)
        path = url.path
        if path.startswith("/api/"):
            method = request.request.method
            body = request.request.post_data_json if method == "POST" else None
            data["calls"].append((method, path, body))
            if path == "/api/agents":
                if method == "POST":
                    data["slots"] = deepcopy(body["slots"])
                result = {"slots": data["slots"], "csrf_token": "test-csrf", "key_configured": {item["id"]: True for item in data["slots"] if item["backend"]["mode"] == "chat" or item["backend"].get("codex_auth") == "api_key"}}
            elif path.startswith("/api/agents/"):
                parts = path.split("/")
                identifier = parts[3]
                account = data["accounts"].setdefault(identifier, {"available": True, "authenticated": False, "account": None, "login": None})
                if method == "POST" and parts[-1] in {"login", "switch"}:
                    account.update(authenticated=False, account=None, login={"status": "pending", "url": data["login_url"], "user_code": identifier.upper()})
                elif method == "POST":
                    account.update(authenticated=False, account=None, login=None)
                result = account
            elif path == "/api/account":
                result = data["workspace_account"] or {"available": False, "authenticated": False, "account": None, "login": None, "error": "Default account unavailable"}
            elif path == "/api/account/login":
                data["workspace_account"].update(login={"status": "pending", "url": data["login_url"], "user_code": "TEST-LOGIN"})
                result = data["workspace_account"]
            elif path == "/api/bootstrap":
                result = {"csrf_token": "test-csrf", "runs": [], "problems": [], "settings": {
                    "backend": "codex", "provider": "codex", "execution": "native", "model": "example-model", "reasoning_effort": "max",
                    "solve_parallel_agents": None, "solve_max_groups": None, "budget_minutes": 180, "max_iterations": 50,
                    **data["settings"],
                }}
            elif path == "/api/models":
                result = {"provider": "codex", "source": "configured", "models": [], "providers": [{"id": "codex", "label": "Codex", "transport": "codex", "reasoning_modes": []}]}
            elif path == "/api/runs" or path.endswith("/resume"):
                # Deliberate preflight stop: inspecting submission must not launch research.
                request.fulfill(status=400, json={"error": "Test submission captured"})
                return
            else:
                request.fulfill(status=404, json={"error": "Unexpected request"})
                return
            request.fulfill(json=result)
            return
        name = {"/": "index.html", "/agents": "agents.html"}.get(path, path.lstrip("/"))
        file = STATIC / name
        if not file.is_file():
            request.abort()
            return
        mime = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml"}[file.suffix]
        request.fulfill(body=file.read_bytes(), content_type=mime)

    context.route("**/*", route)
    yield page, data
    context.close()
    assert errors == []


def test_four_mixed_slots_roundtrip_metadata_only(ui):
    page, data = ui
    page.goto("http://mathlottery.test/agents")
    page.wait_for_selector("#agent-1-transport")
    page.locator("#agent-count").fill("4")
    page.locator("#agent-count").dispatch_event("change")
    for number in (2, 4):
        page.locator(f"#agent-{number}-transport").select_option("chat")
        page.locator(f"#agent-{number}-key-env").fill(f"RESEARCHER_{number}_KEY")
        page.locator(f"#agent-{number}-model").fill("api-model")
    page.locator("#agent-2-reasoning-mode").select_option("pro")
    page.locator("#agent-4-tools").select_option("none")
    page.locator("#agent-1-label").fill("<img src=x onerror=alert(1)>")
    page.locator("#save-agents").click()
    page.wait_for_function("document.querySelector('#save-status').textContent === 'Saved locally'")
    assert [item["backend"]["mode"] for item in data["slots"]] == ["codex", "chat", "codex", "chat"]
    assert data["slots"][1]["backend"]["chat"]["api_key_env"] == "RESEARCHER_2_KEY"
    assert data["slots"][1]["backend"]["chat"]["reasoning_mode"] == "pro"
    assert data["slots"][3]["backend"]["chat"]["tools"] == []
    assert "api_key" not in json.dumps(data["slots"]).replace("api_key_env", "env")
    assert page.locator(".agent-card img").count() == 0
    assert page.evaluate("Object.keys(localStorage)") == []
    page.reload()
    page.wait_for_selector("#agent-4-transport")
    assert page.locator("#agent-count").input_value() == "4"
    assert page.locator("#agent-2-transport").input_value() == "chat"
    page.locator("#language").click()
    assert page.locator("#page-title").text_content() == "每个 agent，独立配置。"
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_slot_login_actions_are_isolated_and_explicit(ui):
    page, data = ui
    data["slots"] = [slot(1), slot(2)]
    page.goto("http://mathlottery.test/agents")
    page.locator("#agent-1-account button[data-action=login]").click()
    page.wait_for_selector("#agent-1-account .agent-login code")
    assert page.locator("#agent-1-account code").text_content() == "AGENT-1"
    assert page.locator("#agent-2-account code").count() == 0
    assert page.get_attribute("#agent-1-account .agent-login a", "rel") == "noopener noreferrer"
    data["accounts"]["agent-1"].update(authenticated=True, login=None, account={"type": "chatgpt", "email": "a***@example.com"})
    page.locator("#agent-1-account button[data-action=status]").click()
    page.wait_for_selector("#agent-1-account button[data-action=switch]")
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#agent-1-account button[data-action=switch]").click()
    page.wait_for_selector("#agent-1-account .agent-login code")
    calls = [(path, body) for method, path, body in data["calls"] if method == "POST"]
    assert calls == [
        ("/api/agents/agent-1/account/login", {}),
        ("/api/agents/agent-1/account/switch", {"confirm_account_change": True}),
    ]
    assert not data["accounts"]["agent-2"]["authenticated"]


def test_account_link_and_environment_name_validation(ui):
    page, data = ui
    data["slots"] = [slot(1)]
    data["login_url"] = "https://auth.openai.com.attacker.example/device"
    page.goto("http://mathlottery.test/agents")
    page.locator("#agent-1-account button[data-action=login]").click()
    page.wait_for_selector("#agent-1-account .notice.error")
    assert page.locator("#agent-1-account .agent-login a").count() == 0
    assert page.locator("#agent-1-account code").count() == 0
    page.locator("#agent-1-transport").select_option("chat")
    page.locator("#agent-1-key-env").fill("sk-not-an-environment-name")
    page.locator("#save-agents").click()
    assert not any(method == "POST" and path == "/api/agents" for method, path, _ in data["calls"])


def test_solve_roster_bypasses_default_account_and_strips_model_overrides(ui):
    page, data = ui
    data["slots"] = [slot(1), slot(2, "chat"), slot(3), slot(4, "chat")]
    page.goto("http://mathlottery.test/")
    page.locator("button[data-workflow=solve]").click()
    page.wait_for_function("document.querySelector('#agent-slots-summary').textContent.includes('4 configured')")
    assert page.locator("#start").is_disabled()
    page.locator("#native-capabilities").evaluate("el => { el.closest('details').open = true; }")
    page.locator("#memories").select_option("true")
    page.locator("#solve-parallel").fill("3")
    page.locator("#use-agent-slots").check()
    page.wait_for_function("!document.querySelector('#start').disabled")
    assert page.locator("#task-model-settings").is_hidden()
    assert page.locator("#solve-parallel").is_disabled()
    assert page.locator("#solve-parallel").input_value() == "4"
    page.locator("#statement").fill("An example mathematical question.")
    page.locator("#start").click()
    page.wait_for_selector("#form-error:not([hidden])")
    body = next(body for method, path, body in data["calls"] if method == "POST" and path == "/api/runs")
    assert body["workflow"] == "solve"
    assert body["options"]["use_agent_slots"] is True
    assert not ({"provider", "backend", "model", "reasoning_effort", "native_multi_agent", "native_memories", "solve_parallel_agents"} & body["options"].keys())
    page.locator("button[data-workflow=find]").click()
    assert page.locator("#agent-slots").is_hidden()
    assert page.locator("#task-model-settings").is_visible()
    assert page.locator("#backend").is_enabled()
    assert page.locator("#model-select").is_enabled()

    assert page.locator("#start").is_disabled()
    page.locator("button[data-workflow=solve]").click()
    page.locator("#use-agent-slots").uncheck()
    assert page.locator("#solve-parallel").input_value() == "3"
    assert page.locator("#backend").is_enabled()
    assert page.locator("#model-select").is_enabled()


def test_codex_api_and_responses_slots_keep_separate_authentication(ui):
    page, data = ui
    data["slots"] = [slot(1), slot(2), slot(3, "chat")]
    data["slots"][1]["backend"].update(codex_auth="api_key", codex_api_key_env="CODEX_RESEARCH_KEY")
    page.goto("http://mathlottery.test/agents")
    page.wait_for_selector("#agent-2-key-env")
    assert page.locator("#agent-2-auth").input_value() == "api_key"
    assert page.locator("#agent-2-account button").count() == 0
    assert "access has not been tested" in page.locator("#agent-2-account").text_content()
    assert page.locator("#agent-2-base-url").count() == 0
    assert page.locator("#agent-3-base-url").is_visible()
    assert [path for _, path, _ in data["calls"] if "/account" in path] == ["/api/agents/agent-1/account"]
    page.locator("#agent-2-key-env").fill("ANOTHER_CODEX_KEY")
    assert "Save the configuration" in page.locator("#agent-2-account").text_content()
    page.locator("#save-agents").click()
    page.wait_for_function("document.querySelector('#save-status').textContent === 'Saved locally'")
    saved = data["slots"][1]["backend"]
    assert saved["mode"] == "codex" and saved["codex_auth"] == "api_key"
    assert saved["codex_api_key_env"] == "ANOTHER_CODEX_KEY"
    page.reload()
    page.wait_for_selector("#agent-2-key-env")
    assert page.locator("#agent-2-key-env").input_value() == "ANOTHER_CODEX_KEY"
    page.locator("#agent-2-auth").select_option("chatgpt")
    assert page.locator("#agent-2-account button[data-action=login]").is_disabled()
    page.locator("#agent-2-auth").select_option("api_key")
    assert page.locator("#agent-2-account button").count() == 0
    assert not any("agent-2/account" in path for _, path, _ in data["calls"])
    assert page.evaluate("Object.keys(localStorage)") == []


def test_main_codex_api_configuration_skips_subscription_login_and_submits_override(ui):
    page, data = ui
    data["settings"] = {"codex_auth": "api_key", "codex_api_key_env": "SERVER_CODEX_KEY", "api_key_configured": True}
    page.goto("http://mathlottery.test/")
    page.wait_for_function("document.querySelector('#model-preview').textContent.includes('API key')")
    assert page.locator("#account-title").text_content() == "Codex agent · API key"
    assert page.locator("#account-login").is_hidden()
    assert "SERVER_CODEX_KEY" in page.locator("#account-details").text_content()
    assert page.locator("#start").is_enabled()
    assert not any(path == "/api/account" for _, path, _ in data["calls"])
    page.locator("#codex-auth").select_option("api_key")
    page.locator("#codex-key-env").fill("TASK_CODEX_KEY")
    page.locator("#query").fill("Find an example mathematical question")
    page.locator("#start").click()
    page.wait_for_selector("#form-error:not([hidden])")
    body = next(body for method, path, body in data["calls"] if method == "POST" and path == "/api/runs")
    assert body["options"]["codex_auth"] == "api_key"
    assert body["options"]["codex_api_key_env"] == "TASK_CODEX_KEY"
    assert not any(path == "/api/account" for _, path, _ in data["calls"])
    page.locator("#codex-auth").select_option("chatgpt")
    page.wait_for_function("!document.querySelector('#account-login').hidden")
    assert page.locator("#start").is_disabled()
    assert any(path == "/api/account" for _, path, _ in data["calls"])


def test_saved_subscription_login_can_be_managed_without_changing_new_api_task(ui):
    page, data = ui
    data["settings"] = {"codex_auth": "api_key", "codex_api_key_env": "SERVER_CODEX_KEY", "api_key_configured": True}
    data["workspace_account"] = {"available": True, "authenticated": False, "account": None, "login": None}
    page.goto("http://mathlottery.test/")
    page.wait_for_function("document.querySelector('#model-preview').textContent.includes('API key')")
    page.locator("#codex-auth").select_option("api_key")
    page.locator("#codex-key-env").fill("NEW_TASK_KEY")
    # Restore an old subscription task's resume form; API form stays a separate draft.
    page.evaluate("""() => {
      state.selected = 'run-saved-subscription';
      state.detail = {id: state.selected, workflow: 'solve', mode: 'codex', busy: false,
        settings: {backend: 'codex', execution: 'native', codex_auth: 'chatgpt'}};
      document.querySelector('#run-detail').hidden = false;
      document.querySelector('#resume-form').hidden = false;
      updateExecutionControls();
    }""")
    page.wait_for_function("document.querySelector('#resume-readiness').textContent.includes('Sign in')")
    assert page.locator("#resume-submit").is_disabled()
    assert page.locator("#account-login").is_hidden()
    page.locator("#resume-account").click()
    assert page.locator("#account-resume-context").is_visible()
    assert "New task settings stay unchanged" in page.locator("#account-resume-context").text_content()
    page.locator("#account-login").click()
    page.wait_for_function("document.querySelector('#account-code').textContent === 'TEST-LOGIN'")
    assert page.evaluate("account.pending")
    assert page.locator("#start").is_enabled()
    assert page.locator("#codex-auth").input_value() == "api_key"
    assert page.locator("#codex-key-env").input_value() == "NEW_TASK_KEY"
    data["workspace_account"].update(authenticated=True, login=None, account={"type": "chatgpt", "email": "u***@example.test"})
    page.locator("#account-refresh").click()
    page.wait_for_function("!document.querySelector('#resume-submit').disabled")
    page.locator("#account-follow-selection").click()
    assert page.locator("#account-login").is_hidden()
    assert page.locator("#account-title").text_content() == "Codex agent · API key"
    assert page.locator("#account-resume-context").is_hidden()
    page.locator("#resume-submit").click()
    page.wait_for_selector("#run-message:not([hidden])")
    resume = next(body for method, path, body in data["calls"] if method == "POST" and path.endswith("/resume"))
    assert not {"provider", "model", "codex_auth", "codex_api_key_env", "use_agent_slots"} & resume.keys()
    assert page.locator("#codex-auth").input_value() == "api_key"
    assert page.locator("#codex-key-env").input_value() == "NEW_TASK_KEY"
    assert [(path, body) for method, path, body in data["calls"] if method == "POST" and "/account" in path] == [("/api/account/login", {})]
