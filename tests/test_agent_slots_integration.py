"""HTTP admission through real mixed-slot orchestration, using scripted transports."""

import json
import threading

import pytest
from test_solve_team import TeamBackend, problem
from test_web import serving

from mathlottery.config import Config
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.service import WebService


@pytest.mark.parametrize("primary_mode", ["codex", "chat"])
@pytest.mark.parametrize("api_codex", [False, True])
def test_http_saved_slots_drive_and_resume_through_exact_original_routes(
    tmp_path, monkeypatch, primary_mode, api_codex,
):
    service = WebService(tmp_path)
    defaults = Config()
    defaults.solve.coordination = "allocation"  # Keep the historical round protocol covered.
    defaults.budget.finalize_minutes = 0
    monkeypatch.setattr(service, "config", lambda: defaults.model_copy(deep=True))
    scripted = TeamBackend(complete=False, plans=[
        [{"id": "first", "agents": 4, "objective": "Derive a partial identity"}],
        [{"id": "next-a", "agents": 2, "objective": "Check assumptions"},
         {"id": "next-b", "agents": 2, "objective": "Try another route"}],
    ])
    scripted.barrier = threading.Barrier(4)
    routed = []
    roster = []
    for index in range(4):
        mode = primary_mode if index < 2 else ("chat" if primary_mode == "codex" else "codex")
        variable = f"TEST_SLOT_API_{index + 1}"
        monkeypatch.setenv(variable, f"private-test-credential-{index}")
        roster.append({
            "id": f"agent-{index + 1}", "label": f"Researcher {index + 1}",
            "backend": {"mode": mode, "model": f"model-{index + 1}",
                        "chat": {"api_key_env": variable}},
        })
        if mode == "codex" and api_codex and index % 2 == 0:
            roster[-1]["backend"].update(codex_auth="api_key", codex_api_key_env=variable)

    checked_api_identities = []

    def check_api(backend):
        assert backend.config.codex_auth == "api_key"
        checked_api_identities.append(backend.config.codex_identity)
        return {"available": True, "authentication": "API key"}

    monkeypatch.setattr("mathlottery.web.agent_roster.NativeWorkBackend.check", check_api)

    class Transport:
        def __init__(self, settings):
            self.settings = settings

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            routed.append({
                "mode": self.settings.mode, "model": self.settings.model,
                "identity": self.settings.codex_identity,
                "key_env": self.settings.chat.api_key_env,
                "auth": self.settings.codex_auth,
                "codex_key_env": self.settings.codex_api_key_env,
                "multi_agent": self.settings.native_multi_agent,
                "supervisor": "resource supervision" in prompt,
                "session": kwargs.get("session_id"),
            })
            return scripted.invoke_native(prompt, directory, workspace, timeout, **kwargs)

    for module in ("mathlottery.solve.attempts", "mathlottery.runtime.native"):
        monkeypatch.setattr(f"{module}.research_backend", lambda settings, root: Transport(settings))

    def launch(run_id, action, **options):
        engine = Orchestrator(service.store)
        if action == "resume":
            engine.resume(run_id, config=Config.model_validate(options["config"]),
                          message=options.get("message"))
        else:
            engine.drive(run_id)

    monkeypatch.setattr(service.jobs, "launch", launch)
    checked_identities = []

    class Account:
        def __init__(self, command, *, root, profile, excluded_env=()):
            self.profile = profile
            self.excluded_env = excluded_env

        def status(self):
            checked_identities.append(self.profile)
            return {"available": True, "authenticated": True,
                    "account": {"type": "chatgpt", "email": "t***@example.test"}}

        def close(self):
            pass

    with serving(service) as (client, server):
        # This fixture executes whole rounds inside HTTP instead of the normal
        # detached queue; allow their durable fsyncs on slower local filesystems.
        client.timeout = 30
        server.agents.account_factory = Account

        def wrong_account():
            pytest.fail("Explicit slots must never preflight the default account")

        monkeypatch.setattr(server.account, "status", wrong_account)
        client.headers["X-MathLottery-Token"] = client.get("/api/agents").json()["csrf_token"]
        saved = client.post("/api/agents", json={"slots": roster})
        assert saved.status_code == 200, saved.text
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": problem().statement,
            "options": {"use_agent_slots": True, "max_iterations": 5, "solve_max_groups": 2},
        })
        assert response.status_code == 202, response.text
        run_id = response.json()["id"]
        original = service.store.load(run_id)
        assert original.state == "PAUSED", original.last_error
        assert original.iteration == original.usage.measured_calls == 5
        assert len(original.candidates) == 4 and scripted.peak == 4
        assert original.mode == primary_mode
        assert {item["model"] for item in routed if not item["supervisor"]} == {
            "model-1", "model-2", "model-3", "model-4",
        }
        assert all(item["multi_agent"] is False for item in routed)
        assert routed[0]["supervisor"] and routed[0]["model"] == "model-1"
        for item in original.native.history:
            if item.get("role") in {"research", "supervision"}:
                assert item["events"].endswith(
                    "response.json" if item["mode"] == "chat" else "codex.events.jsonl"
                )

        # A completely different saved pool must not alter an existing task's routes.
        replacement = [{"id": "replacement", "backend": {"mode": "codex", "model": "new-model"}}]
        assert client.post("/api/agents", json={"slots": replacement}).status_code == 200
        resumed = client.post(f"/api/runs/{run_id}/resume", json={"max_iterations": 10})
        assert resumed.status_code == 202, resumed.text
        finished = service.store.load(run_id)
        assert finished.state == "PAUSED", finished.last_error
        assert finished.iteration == finished.usage.measured_calls == 10
        assert finished.config["solve"]["agent_slots"] == original.config["solve"]["agent_slots"]
        assert len(finished.native.solve_team.workers) == 4
        assert len(finished.native.solve_team.groups) == 2
        for model in ("model-1", "model-2", "model-3", "model-4"):
            calls = [item for item in routed if not item["supervisor"] and item["model"] == model]
            assert len(calls) == 2 and calls[0]["session"] is None and calls[1]["session"]
            assert calls[0]["identity"] == calls[1]["identity"]
            assert calls[0]["key_env"] == calls[1]["key_env"]
            assert calls[0]["auth"] == calls[1]["auth"]
            assert calls[0]["codex_key_env"] == calls[1]["codex_key_env"]
        expected = {
            item["id"] for item in roster
            if item["backend"]["mode"] == "codex"
            and item["backend"].get("codex_auth", "chatgpt") == "chatgpt"
        }
        assert set(checked_identities) == expected
        assert set(checked_api_identities) == {
            item["id"] for item in roster
            if item["backend"].get("codex_auth") == "api_key"
        }
        public = client.get(f"/api/runs/{run_id}").text
        assert "private-test-credential" not in public
        assert "private-test-credential" not in json.dumps(finished.config)
        assert "private-test-credential" not in (tmp_path / ".mathlottery/agents.json").read_text()
