"""Model selection reaches immutable task settings without running an agent."""

import json

import pytest
import yaml
from test_web import SIGNED_IN, serving

from mathlottery.config import BackendConfig, Config
from mathlottery.providers.chat import ChatBackend
from mathlottery.web.account import AccountError
from mathlottery.web.model_directory import codex_models
from mathlottery.web.service import WebService

CATALOG = {"data": [{
    "id": "catalog-id", "model": "gpt-6-astra", "displayName": "GPT-6 Astra",
    "supportedReasoningEfforts": [{"reasoningEffort": "high"}, {"reasoningEffort": "max"}],
    "defaultReasoningEffort": "high", "isDefault": True,
    "account_id": "secret-account-detail", "access_token": "secret-provider-token",
}]}


class FakeRPC:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []
        self.closed = False

    def call(self, method, params, timeout):
        self.calls.append((method, params, timeout))
        page = next(self.pages)
        if isinstance(page, Exception):
            raise page
        return page

    def close(self):
        self.closed = True


def test_codex_catalog_reads_pages_without_account_or_inference_calls(tmp_path):
    rpc = FakeRPC([{"data": [{"model": "first"}], "nextCursor": "next-page"},
                   {"data": [{"model": "second"}], "nextCursor": None}])
    factory_args = []

    def factory(command, *, root):
        factory_args.append((command, root))
        return rpc

    result = codex_models("configured-codex", tmp_path, rpc_factory=factory)
    assert result == {"data": [{"model": "first"}, {"model": "second"}]}
    assert factory_args == [("configured-codex", tmp_path)]
    assert [call[0] for call in rpc.calls] == ["model/list", "model/list"]
    assert rpc.calls[1][1]["cursor"] == "next-page"
    assert all(0 < call[2] <= 15 for call in rpc.calls)
    assert rpc.closed


@pytest.mark.parametrize("pages", [
    [{"data": "invalid"}],
    [{"data": [], "nextCursor": "loop"}, {"data": [], "nextCursor": "loop"}],
    [{"data": [], "nextCursor": ""}],
    [AccountError("private provider error")],
])
def test_codex_catalog_failures_close_only_the_catalog_rpc(tmp_path, pages):
    rpc = FakeRPC(pages)
    with pytest.raises(AccountError):
        codex_models("codex", tmp_path, rpc_factory=lambda *args, **kwargs: rpc)
    assert rpc.closed
    assert all(call[0] == "model/list" for call in rpc.calls)


@pytest.mark.parametrize("payload", [
    {"workflow": "find", "query": "small problems"},
    {"workflow": "solve", "statement": "A synthetic mathematical question"},
    {"workflow": "verify", "statement": "A synthetic mathematical question", "proof": "A synthetic proof"},
])
def test_models_route_and_selection_are_private_and_reach_run(tmp_path, monkeypatch, payload):
    config = Config()
    config.backend.model = "configured-model"
    config.backend.reasoning_effort = "high"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config.model_dump(mode="json")))
    before = config_path.read_bytes()
    service = WebService(tmp_path)
    launched = []
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: launched.append((args, kwargs)))
    monkeypatch.setattr("mathlottery.web.server.codex_models", lambda *args: CATALOG)
    with serving(service, account_status=SIGNED_IN) as (client, _):
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        response = client.get("/api/models?provider=codex&refresh=1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["provider"] == "codex"
        assert data["models"][0]["id"] == "gpt-6-astra"
        assert data["models"][0]["reasoning_efforts"] == ["high", "max"]
        assert "secret-account-detail" not in response.text
        assert "secret-provider-token" not in response.text
        invalid = client.post("/api/runs", json={**payload,
            "options": {"provider": "codex", "model": "gpt-6-astra", "reasoning_effort": "unsupported"}})
        assert invalid.status_code == 400, invalid.text
        assert not launched and not service.store.list_runs()
        response = client.post("/api/runs", json={**payload,
            "options": {"provider": "codex", "model": "gpt-6-astra", "reasoning_effort": "max"}})
        assert response.status_code == 202, response.text
        run = service.store.load(response.json()["id"])
        assert run.config["backend"]["model"] == "gpt-6-astra"
        assert run.config["backend"]["reasoning_effort"] == "max"
        assert run.mode == "codex"
        assert len(launched) == 1
    assert config_path.read_bytes() == before


@pytest.mark.parametrize("action", ["login", "cancel", "switch", "logout"])
def test_account_actions_invalidate_model_catalog(tmp_path, monkeypatch, action):
    service = WebService(tmp_path)
    calls = []
    monkeypatch.setattr("mathlottery.web.server.codex_models", lambda *args: calls.append(1) or CATALOG)
    with serving(service, account_status=SIGNED_IN) as (client, server):
        method = "start" if action == "login" else action
        monkeypatch.setattr(server.account, method, lambda: SIGNED_IN)
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        assert client.get("/api/models").status_code == 200
        assert client.get("/api/models").status_code == 200
        assert len(calls) == 1
        body = {"confirm_account_change": True} if action in {"switch", "logout"} else {}
        assert client.post(f"/api/account/{action}", json=body).status_code == 200
        assert client.get("/api/models").status_code == 200
        assert len(calls) == 2


def test_catalog_local_origin_and_query_validation(tmp_path, monkeypatch):
    service = WebService(tmp_path)
    monkeypatch.setattr("mathlottery.web.server.codex_models", lambda *args: CATALOG)
    with serving(service) as (client, _):
        assert client.get("/api/models", headers={"Origin": "https://external.example"}).status_code == 403
        for query in ("provider=codex&provider=chat", "refresh=oops", "provider=", "endpoint=https://external.example"):
            assert client.get("/api/models?" + query).status_code == 400


def test_custom_provider_does_not_inherit_openai_model(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "openai-only-model")
    monkeypatch.setenv("OTHER_API_KEY", "test-only-key")
    config = BackendConfig.model_validate({"mode": "chat", "provider": "other",
        "chat": {"api_key_env": "OTHER_API_KEY", "base_url": "https://api.example.invalid/v1", "tools": []}})
    with pytest.raises(ValueError, match="model"):
        ChatBackend(config).check()
    config.model = "other-model"
    assert ChatBackend(config).check()["model"] == "other-model"
    assert ChatBackend(config).capabilities()["billing"] == "Provider API"
    assert "test-only-key" not in json.dumps(ChatBackend(config).check())
