"""Isolated agent settings and Web routing; no real authentication or model calls."""

import json
import os
import stat
import sys

import pytest
import yaml
from test_web import SIGNED_IN, serving
from test_web_account import SCRIPT

from mathlottery.config import Config
from mathlottery.models import Problem, Workflow
from mathlottery.providers.agent_roster import AgentRoster, AgentRosterStore
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.account import AccountRPC, CodexAccount
from mathlottery.web.service import WebService


def slot(identifier="agent-a", mode="codex"):
    return {
        "id": identifier, "label": identifier,
        "backend": {"mode": mode, "model": "test-model", "chat": {
            "api_key_env": "TEST_AGENT_API_KEY", "base_url": "https://api.example.test/v1",
            "tools": [],
        }},
    }


class FakeAccount:
    def __init__(self, command, root=None, profile=None, excluded_env=()):
        self.profile = profile
        self.excluded_env = excluded_env
        self.calls = []
        self.closed = False
        self.signed_in = True

    def status(self):
        self.calls.append("status")
        return {**SIGNED_IN, "authenticated": self.signed_in}

    def start(self):
        self.calls.append("login")
        return self.status()

    def switch(self):
        self.calls.append("switch")
        return self.status()

    def logout(self):
        self.calls.append("logout")
        self.signed_in = False
        return self.status()

    def cancel(self):
        self.calls.append("cancel")
        return self.status()

    def close(self):
        self.closed = True


def save_roster(root, slots):
    store = AgentRosterStore(root)
    store.save(AgentRoster.model_validate({"slots": slots}))
    return store


def test_private_roster_roundtrip_contains_env_names_never_values(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_AGENT_API_KEY", "synthetic-private-key")
    store = save_roster(tmp_path, [slot(), slot("agent-b", "chat")])
    assert stat.S_IMODE(store.path.stat().st_mode) == 0o600
    assert len(store.load().slots) == 2
    assert store.public()["key_configured"] == {"agent-b": True}
    assert "synthetic-private-key" not in store.path.read_text()
    assert "synthetic-private-key" not in json.dumps(store.public())
    assert store.load().slots[0].backend.codex_identity == "agent-a"


@pytest.mark.parametrize("link", ["directory", "symlink", "hardlink"])
def test_roster_rejects_linked_settings(tmp_path, link):
    store = AgentRosterStore(tmp_path)
    if link == "directory":
        target = tmp_path / "elsewhere"
        target.mkdir()
        store.directory.symlink_to(target, target_is_directory=True)
    else:
        store.directory.mkdir()
        target = tmp_path / "elsewhere.json"
        target.write_text('{"slots":[]}')
        if link == "symlink":
            store.path.symlink_to(target)
        else:
            os.link(target, store.path)
    with pytest.raises(ValueError):
        store.load()
    with pytest.raises(ValueError):
        store.save(AgentRoster())


@pytest.mark.parametrize("change", [
    {"id": "../elsewhere"},
    {"backend": {"mode": "chat", "chat": {"api_key_env": "sk-not-an-env-name"}}},
    {"backend": {"mode": "chat", "chat": {"api_key": "private"}}},
    {"backend": {"mode": "chat", "chat": {"tools": [{"authorization": "private"}]}}},
    {"backend": {"mode": "chat", "chat": {"base_url": "https://user:password@example.test"}}},
])
def test_invalid_connections_do_not_persist(tmp_path, change):
    with pytest.raises(ValueError):
        save_roster(tmp_path, [{**slot(), **change}])
    assert not AgentRosterStore(tmp_path).path.exists()


def test_roster_http_csrf_and_account_scope(tmp_path):
    service = WebService(tmp_path)
    with serving(service) as (client, server):
        server.agents.account_factory = FakeAccount
        data = client.get("/api/agents").json()
        headers = {"X-MathLottery-Token": data["csrf_token"]}
        payload = {"slots": [slot(), slot("agent-b")]}
        assert client.post("/api/agents", json=payload).status_code == 403
        assert client.post("/api/agents", json=payload, headers={
            **headers, "Origin": "https://example.com",
        }).status_code == 403
        saved = client.post("/api/agents", json=payload, headers=headers)
        assert saved.status_code == 200
        assert saved.headers["cache-control"] == "no-store"
        for identifier in ("agent-a", "agent-b"):
            response = client.get(f"/api/agents/{identifier}/account")
            assert response.json()["authenticated"]
        accounts = list(server.agents.accounts.values())
        assert {item.profile for item in accounts} == {"agent-a", "agent-b"}
        assert client.post("/api/agents/agent-a/account/logout", json={}, headers=headers).status_code == 400
        assert client.post("/api/agents/agent-a/account/logout", json={
            "confirm_account_change": True,
        }, headers=headers).status_code == 200
        assert not client.get("/api/agents/agent-a/account").json()["authenticated"]
        assert client.get("/api/agents/agent-b/account").json()["authenticated"]
        assert client.get("/api/agents/unknown/account").status_code == 400
    assert all(account.closed for account in accounts)


def test_mixed_start_uses_each_slot_and_ignores_default_login(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_AGENT_API_KEY", "synthetic-private-key")
    service = WebService(tmp_path)
    save_roster(tmp_path, [slot("api-first", "chat"), slot("codex-second")])
    launched = []
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: launched.append((args, kwargs)))
    with serving(service) as (client, server):
        server.agents.account_factory = FakeAccount
        server.account.status = lambda: pytest.fail("Must not use the default login")
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "Synthetic test proposition",
            "options": {"use_agent_slots": True},
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        run = service.store.load(response.json()["id"])
        assert run.mode == "chat"
        assert run.config["backend"]["chat"]["api_key_env"] == "TEST_AGENT_API_KEY"
        assert run.config["solve"]["parallel_agents"] == 2
        assert [item["id"] for item in run.config["solve"]["agent_slots"]] == ["api-first", "codex-second"]
        assert response.json()["settings"]["solve_agent_slots"][1]["backend"] == "codex"
        assert "synthetic-private-key" not in response.text
    assert len(launched) == 1


@pytest.mark.parametrize("failure", ["missing_key", "missing_model", "zero_cost", "signed_out", "count_mismatch", "model_override", "find"])
def test_pool_preflight_rejects_before_problem_or_run_creation(tmp_path, monkeypatch, failure):
    monkeypatch.setenv("TEST_AGENT_API_KEY", "synthetic-private-key")
    service = WebService(tmp_path)
    save_roster(tmp_path, [slot(), slot("agent-b", "chat")])
    monkeypatch.setattr(service.jobs, "launch", lambda *a, **kw: pytest.fail("Must not launch"))
    payload = {"workflow": "solve", "statement": "Do not persist", "options": {"use_agent_slots": True}}
    if failure == "missing_key":
        monkeypatch.delenv("TEST_AGENT_API_KEY")
    elif failure == "missing_model":
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        missing = slot("agent-b", "chat")
        missing["backend"]["model"] = None
        save_roster(tmp_path, [slot(), missing])
    elif failure == "zero_cost":
        config = Config()
        config.budget.max_external_cost_usd = 0
        (tmp_path / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    elif failure == "count_mismatch":
        payload["options"]["solve_parallel_agents"] = 3
    elif failure == "model_override":
        payload["options"]["model"] = "unexpected-model"
    elif failure == "find":
        payload = {"workflow": "find", "options": {"use_agent_slots": True}}
    with serving(service) as (client, server):
        server.agents.account_factory = FakeAccount
        if failure == "signed_out":
            server.agents.account(server.agents.slot("agent-a")).signed_in = False
        response = client.post("/api/runs", json=payload, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 400, response.text
        assert "synthetic-private-key" not in response.text
    assert not service.store.list_runs()
    assert not service.store.list_problems()


def test_resume_uses_saved_pool_after_roster_edited_or_removed(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_AGENT_API_KEY", "synthetic-private-key")
    service = WebService(tmp_path)
    store = save_roster(tmp_path, [slot("api-first", "chat"), slot("codex-second")])
    config = store.load().apply(Config())
    run = Orchestrator(service.store).create(config, problem=Problem(
        id="snapshot", title="Snapshot", statement="Test statement",
    ), workflow=Workflow.SOLVE)
    store.save(AgentRoster())
    launched = []
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: launched.append((args, kwargs)))
    with serving(service) as (client, server):
        server.agents.account_factory = FakeAccount
        server.account.status = lambda: pytest.fail("Must not use the default login")
        response = client.post(f"/api/runs/{run.id}/resume", json={"budget_minutes": 2},
                               headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        assert {account.profile for account in server.agents.accounts.values()} == {"codex-second"}
        assert [item["id"] for item in launched[0][1]["config"]["solve"]["agent_slots"]] == ["api-first", "codex-second"]


def test_browser_without_pool_selection_does_not_implicitly_use_yaml_slots(tmp_path, monkeypatch):
    roster = AgentRoster.model_validate({"slots": [slot("api-slot", "chat")]})
    config = roster.apply(Config())
    # CLI's pool remains configured, but Web's visible default is a separate model.
    config.backend = Config().backend
    config.backend.model = "visible-default-model"
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    service = WebService(tmp_path)
    monkeypatch.setattr(service.jobs, "launch", lambda *a, **kw: None)
    with serving(service, account_status=SIGNED_IN) as (client, server):
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "Explicit browser choice",
            "options": {"model": "visible-selection"},
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        run = service.store.load(response.json()["id"])
        assert not run.config["solve"]["agent_slots"]
        assert run.config["backend"]["model"] == "visible-selection"
        assert run.mode == "codex"
    assert service.config().solve.agent_slots


@pytest.mark.parametrize("action", ["login", "cancel", "switch", "logout"])
def test_mixed_chat_primary_blocks_used_codex_account_changes(tmp_path, monkeypatch, action):
    service = WebService(tmp_path)
    store = save_roster(tmp_path, [slot("api-first", "chat"), slot("codex-second")])
    run = Orchestrator(service.store).create(store.load().apply(Config()), problem=Problem(
        id="active", title="Active", statement="Test statement",
    ), workflow=Workflow.SOLVE)
    monkeypatch.setattr(service.jobs, "running", lambda identifier: identifier == run.id)
    with serving(service) as (client, server):
        server.agents.account_factory = FakeAccount
        payload = {"confirm_account_change": True} if action in {"switch", "logout"} else {}
        response = client.post(f"/api/agents/codex-second/account/{action}", json=payload,
                               headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 409
        assert not server.agents.accounts


def test_named_rpc_credentials_are_separate_from_workspace_and_sibling(tmp_path, monkeypatch):
    executable = tmp_path / "scripted-codex"
    executable.write_text(f"#!{sys.executable}\n" + SCRIPT)
    executable.chmod(0o755)
    monkeypatch.setenv("ACCOUNT_TEST_LOG", str(tmp_path / "methods.log"))
    monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", "success")
    default = CodexAccount(lambda: str(executable), root=tmp_path)
    first = CodexAccount(lambda: str(executable), root=tmp_path, profile="first")
    second = CodexAccount(lambda: str(executable), root=tmp_path, profile="second")
    try:
        assert first.start()["login"]
        assert first.status()["authenticated"]
        assert not default.status()["authenticated"]
        assert not second.status()["authenticated"]
        assert second.start()["login"]
        assert second.status()["authenticated"]
        assert not second.logout()["authenticated"]
        first.close()
        assert first.status()["authenticated"]
        assert (tmp_path / ".mathlottery/codex-accounts/first/auth.json").exists()
        assert not (tmp_path / ".mathlottery/codex-home/auth.json").exists()
    finally:
        for account in (default, first, second):
            account.close()


def test_account_rpc_strips_other_agents_api_key_environment(tmp_path, monkeypatch):
    executable = tmp_path / "scripted-codex"
    executable.write_text(f"#!{sys.executable}\n" + SCRIPT.replace(
        "'HTTPS_PROXY', 'https_proxy', 'NO_PROXY',", "'TEST_AGENT_API_KEY', 'HTTPS_PROXY', 'https_proxy', 'NO_PROXY',",
    ))
    executable.chmod(0o755)
    monkeypatch.setenv("ACCOUNT_TEST_LOG", str(tmp_path / "methods.log"))
    monkeypatch.setenv("TEST_AGENT_API_KEY", "synthetic-private-key")
    service = WebService(tmp_path)
    codex = slot()
    codex["backend"]["codex_command"] = str(executable)
    save_roster(tmp_path, [codex, slot("api-agent", "chat")])
    with serving(service) as (client, _):
        assert client.get("/api/agents/agent-a/account").status_code == 200
        metadata = json.loads((tmp_path / "methods.log.process").read_text())
        assert metadata["environment"]["TEST_AGENT_API_KEY"] is None
        assert os.environ["TEST_AGENT_API_KEY"] == "synthetic-private-key"


@pytest.mark.parametrize("completion", ["success", "cancel"])
def test_slot_rpc_releases_idle_process_but_preserves_pending_login(tmp_path, monkeypatch, completion):
    executable = tmp_path / "scripted-codex"
    executable.write_text(f"#!{sys.executable}\n" + SCRIPT)
    executable.chmod(0o755)
    monkeypatch.setenv("ACCOUNT_TEST_LOG", str(tmp_path / "methods.log"))
    monkeypatch.delenv("ACCOUNT_TEST_SIGNED_IN", raising=False)
    monkeypatch.delenv("ACCOUNT_TEST_COMPLETE", raising=False)
    if completion == "success":
        monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", "success")
    service = WebService(tmp_path)
    configured = slot()
    configured["backend"]["codex_command"] = str(executable)
    save_roster(tmp_path, [configured])
    processes = []

    class TrackedRPC(AccountRPC):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            processes.append(self.process)

    def account_factory(command, **kwargs):
        return CodexAccount(command, rpc_factory=TrackedRPC, **kwargs)

    with serving(service) as (client, server):
        server.agents.account_factory = account_factory
        headers = {"X-MathLottery-Token": server.csrf_token}
        account_path = "/api/agents/agent-a/account"
        assert not client.get(account_path).json()["authenticated"]
        assert len(processes) == 1 and processes[0].poll() is not None
        started = client.post(account_path + "/login", json={}, headers=headers).json()
        assert started["login"]["user_code"] == "TEST-CODE"
        pending = processes[-1]
        assert pending.poll() is None
        if completion == "cancel":
            assert client.get(account_path).json()["login"]
            assert pending.poll() is None
            completed = client.post(account_path + "/cancel", json={}, headers=headers).json()
        else:
            completed = client.get(account_path).json()
        assert completed["login"] is None
        assert completed["authenticated"] is (completion == "success")
        assert pending.poll() is not None
        assert all(account.rpc is None for account in server.agents.accounts.values())
        # The next read reconnects, preserving the credential file rather than logging out.
        assert client.get(account_path).json()["authenticated"] is (completion == "success")
        assert all(process.poll() is not None for process in processes)
        assert "account/logout" not in (tmp_path / "methods.log").read_text()
