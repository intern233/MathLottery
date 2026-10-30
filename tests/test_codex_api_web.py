"""Codex API-key admission and browser configuration without paid model calls."""

import json
import sys

import pytest
import yaml
from test_agent_roster_web import FakeAccount, save_roster, slot
from test_web import serving

from mathlottery.config import Config
from mathlottery.models import Problem, Workflow
from mathlottery.providers.catalog import ModelCatalog
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.service import Overrides, WebService


@pytest.fixture
def api_web(tmp_path, monkeypatch):
    executable = tmp_path / "codex-local-probe"
    executable.write_text(f"#!{sys.executable}\n" + r'''
import json, os, sys
with open(os.environ['API_PROBE_LOG'], 'a') as file:
    file.write(json.dumps({'args': sys.argv[1:], 'has_key': any(
        name in os.environ for name in ('SELECTED_CODEX_KEY', 'CODEX_API_KEY', 'OPENAI_API_KEY')
    )}) + '\n')
if sys.argv[1:] == ['--version']:
    print('codex-cli local-test')
elif '--help' in sys.argv:
    print('--json --output-last-message --sandbox')
else:
    raise SystemExit('No login, account RPC or model calls are allowed in this test')
''')
    executable.chmod(0o755)
    monkeypatch.setenv("API_PROBE_LOG", str(tmp_path / "probe.jsonl"))
    monkeypatch.setenv("SELECTED_CODEX_KEY", "synthetic-selected-api-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-default-api-secret")
    config = Config()
    config.backend.codex_command = str(executable)
    config.backend.model = "test-api-model"
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    service = WebService(tmp_path)
    launches = []
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: launches.append((args, kwargs)))
    return service, launches


def api_slot(service, identifier="api-native"):
    result = slot(identifier)
    result["backend"].update(
        codex_auth="api_key", codex_api_key_env="SELECTED_CODEX_KEY",
        codex_command=service.config().backend.codex_command,
    )
    return result


def no_account_rpc(*args, **kwargs):
    raise AssertionError("API authentication must not open a ChatGPT account RPC")


def test_main_codex_api_override_and_readiness_skip_subscription(api_web):
    service, launches = api_web
    with serving(service) as (client, server):
        server.account.status = no_account_rpc
        server.agents.account_factory = no_account_rpc
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "Synthetic API-auth task",
            "options": {"codex_auth": "api_key", "codex_api_key_env": "SELECTED_CODEX_KEY"},
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        settings = response.json()["settings"]
        assert settings["codex_auth"] == "api_key"
        assert settings["api_key_env"] == "SELECTED_CODEX_KEY"
        assert settings["api_key_configured"] is True
        assert "synthetic-selected-api-secret" not in response.text
        run = service.store.load(response.json()["id"])
        assert run.config["backend"]["codex_api_key_env"] == "SELECTED_CODEX_KEY"
        assert run.mode == "codex"
    assert len(launches) == 1
    probes = [json.loads(line) for line in (service.store.root / "probe.jsonl").read_text().splitlines()]
    assert probes and all(not probe["has_key"] for probe in probes)
    assert all("login" not in probe["args"] and "app-server" not in probe["args"] for probe in probes)


@pytest.mark.parametrize("pool", [False, True])
@pytest.mark.parametrize("issue", ["missing_key", "zero_cost"])
def test_api_admission_fails_before_saving_inputs_without_fallback(api_web, monkeypatch, pool, issue):
    service, launches = api_web
    if issue == "missing_key":
        monkeypatch.delenv("SELECTED_CODEX_KEY")
    else:
        config = service.config()
        config.budget.max_external_cost_usd = 0
        (service.store.root / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    options = {"codex_auth": "api_key", "codex_api_key_env": "SELECTED_CODEX_KEY"}
    if pool:
        save_roster(service.store.root, [api_slot(service)])
        options = {"use_agent_slots": True}
    with serving(service) as (client, server):
        server.account.status = no_account_rpc
        server.agents.account_factory = no_account_rpc
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "Do not save this input", "options": options,
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 400, response.text
        if issue == "missing_key":
            assert "SELECTED_CODEX_KEY" in response.json()["error"]
        else:
            assert "max_external_cost_usd" in response.json()["error"]
        assert "synthetic-default-api-secret" not in response.text
    assert not launches and not service.store.list_runs() and not service.store.list_problems()


def test_codex_api_pool_key_readiness_and_mixed_subscription_preflight(api_web):
    service, launches = api_web
    save_roster(service.store.root, [api_slot(service), slot("subscription")])
    with serving(service) as (client, server):
        server.account.status = no_account_rpc
        server.agents.account_factory = FakeAccount
        data = client.get("/api/agents").json()
        assert data["key_configured"] == {"api-native": True}
        assert "synthetic-selected-api-secret" not in json.dumps(data)
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "Mixed authentication pool",
            "options": {"use_agent_slots": True},
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        assert {account.profile for account in server.agents.accounts.values()} == {"subscription"}
        assert [item["codex_auth"] for item in response.json()["settings"]["solve_agent_slots"]] == ["api_key", "chatgpt"]
    assert len(launches) == 1


@pytest.mark.parametrize("action", [None, "login", "switch", "logout", "cancel"])
def test_codex_api_slot_never_uses_device_account_operations(api_web, action):
    service, _ = api_web
    save_roster(service.store.root, [api_slot(service)])
    with serving(service) as (client, server):
        server.agents.account_factory = no_account_rpc
        path = "/api/agents/api-native/account"
        if action:
            body = {"confirm_account_change": True} if action in {"switch", "logout"} else {}
            response = client.post(path + "/" + action, json=body,
                                   headers={"X-MathLottery-Token": server.csrf_token})
        else:
            response = client.get(path)
        assert response.status_code == 400
        assert "environment" in response.json()["error"]
        assert not server.agents.accounts


def test_resume_preserves_saved_codex_api_key_choice(api_web):
    service, launches = api_web
    config = Overrides(codex_auth="api_key", codex_api_key_env="SELECTED_CODEX_KEY").apply(service.config())
    run = Orchestrator(service.store).create(config, problem=Problem(
        id="api-resume", title="Resume", statement="Keep the API route",
    ), workflow=Workflow.SOLVE)
    # Current defaults still use ChatGPT; that must not change the saved task.
    assert service.config().backend.codex_auth == "chatgpt"
    with serving(service) as (client, server):
        server.account.status = no_account_rpc
        response = client.post(f"/api/runs/{run.id}/resume", json={"budget_minutes": 2},
                               headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
    assert launches[0][1]["config"]["backend"]["codex_auth"] == "api_key"
    assert launches[0][1]["config"]["backend"]["codex_api_key_env"] == "SELECTED_CODEX_KEY"


def test_api_catalog_never_queries_or_reuses_chatgpt_capabilities():
    config = Config()
    config.backend.model = "test-model"
    catalog = ModelCatalog(lambda: config, lambda: [{
        "model": "test-model", "supportedReasoningEfforts": ["low"],
    }])
    assert catalog.get()["source"] == "live"
    selected = Overrides(codex_auth="api_key", reasoning_effort="high").apply(config)
    # A subscription cache must not reject an independently selected API model/effort.
    catalog.validate_selection(selected)
    catalog.register("codex", no_account_rpc)
    api = catalog.get("codex", codex_auth="api_key", codex_api_key_env="SELECTED_CODEX_KEY")
    assert api["source"] == "configured"
    assert api["error_code"] == "CATALOG_UNSUPPORTED"
    assert api["models"][0]["reasoning_efforts"] is None


def test_api_catalog_http_form_override_does_not_probe_subscription(api_web, monkeypatch):
    service, _ = api_web
    monkeypatch.setattr("mathlottery.web.server.codex_models", no_account_rpc)
    with serving(service) as (client, _):
        response = client.get("/api/models?provider=codex&codex_auth=api_key&codex_api_key_env=SELECTED_CODEX_KEY")
        assert response.status_code == 200, response.text
        assert response.json()["source"] == "configured"
        assert response.json()["error_code"] == "CATALOG_UNSUPPORTED"
        assert "synthetic-selected-api-secret" not in response.text
        assert client.get("/api/models?provider=chat&codex_auth=api_key").status_code == 400
        assert client.get("/api/models?provider=codex&codex_auth=invalid").status_code == 400


@pytest.mark.parametrize("options", [
    {"backend": "chat", "codex_auth": "api_key"},
    {"backend": "chat", "codex_api_key_env": "OTHER_KEY"},
    {"codex_api_key_env": "sk-not-a-variable"},
])
def test_invalid_auth_overrides_are_rejected(options):
    with pytest.raises(ValueError):
        Overrides.model_validate(options).apply(Config())
