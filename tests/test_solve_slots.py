"""Mixed transports use fixed identities without model calls or real credentials."""

import json
import os
import re
import threading
from datetime import datetime, timedelta, timezone

import pytest
from test_solve_team import problem

from mathlottery.config import AgentSlot, BackendConfig, ChatConfig, Config, SolveConfig
from mathlottery.models import State, Workflow
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.identity import CodexIdentity
from mathlottery.runtime import budget
from mathlottery.runtime.native import NativeRunner
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.attempts import bounded_backend
from mathlottery.solve.routes import attempt_config
from mathlottery.storage.core import atomic_write, json_text


def slot_config(*modes, calls=3):
    slots = [
        AgentSlot(id=f"agent-{index}", backend=BackendConfig(
            mode=mode, model=f"{mode}-test-model",
            chat=ChatConfig(api_key_env=f"TEST_AGENT_{index}_KEY"),
        )) for index, mode in enumerate(modes or ("codex", "chat"), 1)
    ]
    config = Config(solve=SolveConfig(parallel_agents=len(slots), agent_slots=slots))
    config.budget.max_iterations = calls
    config.budget.finalize_minutes = 0
    return config


class RoutedBackend:
    def __init__(self, config, calls, *, complete=True):
        self.config, self.calls, self.complete = config, calls, complete

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        ids = dict(re.findall(r"(?m)^(run_id|task_id): (.+)$", prompt))
        supervising = "resource supervision" in prompt
        role = "supervisor" if supervising else "researcher"
        identity = self.config.codex_identity or self.config.chat.api_key_env
        session = f"{self.config.mode}:{identity}:{role}"
        assert kwargs.get("session_id") in {None, session}
        kwargs["on_session"](session)
        self.calls.append({"backend": self.config, "prompt": prompt, "role": role,
                           "previous_session": kwargs.get("session_id"), "session": session,
                           "directory": directory, "workspace": workspace})
        if supervising:
            count = sum(call["role"] == "supervisor" for call in self.calls)
            groups = ([{"id": "first", "agents": 2, "objective": "Derive"}] if count == 1 else [
                {"id": "changed", "agents": 1, "objective": "Refine"},
                {"id": "challenge", "agents": 1, "objective": "Challenge"},
            ])
            payload = {**ids, "rationale": "Two routes", "groups": groups}
            text = "```solve-plan\n" + json.dumps(payload) + "\n```\n"
        else:
            payload = {**ids, "kind": "candidate", "conclude": True, "summary": "Identity derived.",
                       "candidate": {"claim": problem().statement, "proof": "By addition's definition.",
                                     "scope": "COMPLETE" if self.complete else "PARTIAL",
                                     "remaining_obligations": [] if self.complete else ["Remaining step"]}}
            if self.config.mode == "codex":
                atomic_write(workspace / "submissions" / f"{ids['task_id']}.json", json_text(payload))
                text = "Local submission saved."
            else:
                text = "```mathlottery\n" + json.dumps(payload) + "\n```\n"
        return BackendResult(BackendStatus.COMPLETED, text=text, session_id=session, invoked=True,
                             usage={"input_tokens": 10, "output_tokens": 2})


def install_routes(monkeypatch, *, complete=True, factory=None):
    calls = []
    factory = factory or (lambda config, root: RoutedBackend(config, calls, complete=complete))
    monkeypatch.setattr("mathlottery.solve.attempts.research_backend", factory)
    monkeypatch.setattr("mathlottery.runtime.native.research_backend", factory)
    monkeypatch.setattr("mathlottery.runtime.attempts.research_backend", factory)
    return calls


@pytest.mark.parametrize("invalid", ["../personal", "/absolute", "Bad Id", "", "a" * 65])
def test_slot_ids_cannot_be_paths_or_unsafe_names(invalid):
    with pytest.raises(ValueError):
        AgentSlot(id=invalid, backend=BackendConfig())
    with pytest.raises(ValueError):
        CodexIdentity(profile=invalid)


def test_slots_require_matching_parallelism_unique_ids_and_isolated_native_routes():
    slot = AgentSlot(id="one", backend=BackendConfig())
    assert slot.backend.codex_identity == "one"
    with pytest.raises(ValueError, match="must match"):
        SolveConfig(parallel_agents=2, agent_slots=[slot])
    with pytest.raises(ValueError, match="unique"):
        SolveConfig(parallel_agents=2, agent_slots=[slot, slot])
    with pytest.raises(ValueError, match="own named account"):
        AgentSlot(id="one", backend=BackendConfig(codex_identity="other"))
    with pytest.raises(ValueError, match="cannot select"):
        AgentSlot(id="one", backend=BackendConfig(mode="chat", codex_identity="one"))
    with pytest.raises(ValueError, match="native Codex"):
        AgentSlot(id="one", backend=BackendConfig(execution="structured"))


@pytest.mark.parametrize("value", ["sk-not-an-env-name", "MY KEY", "x=y", "", "A" * 129])
def test_api_credentials_fields_accept_names_not_keys(value):
    with pytest.raises(ValueError):
        ChatConfig(api_key_env=value)


def test_named_identities_are_separate_from_default_and_personal(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "personal"))
    previous = dict(os.environ)
    root = tmp_path / "research"
    first, second, default = CodexIdentity(root, "one"), CodexIdentity(root, "two"), CodexIdentity(root)
    for identity in (first, second, default):
        identity.prepare()
    atomic_write(first.home / "auth.json", '{"synthetic": "one"}')
    assert first.home == root / ".mathlottery/codex-accounts/one"
    assert len({item.home for item in (first, second, default)}) == 3
    assert not (second.home / "auth.json").exists() and not (default.home / "auth.json").exists()
    assert first.environment()["CODEX_HOME"] == str(first.home)
    assert dict(os.environ) == previous
    backend = NativeWorkBackend(BackendConfig(codex_identity="one"), root)
    assert backend.identity.home == first.home


@pytest.mark.parametrize("component", [".mathlottery", ".mathlottery/codex-accounts",
                                        ".mathlottery/codex-accounts/one"])
def test_named_identity_rejects_linked_ancestors(tmp_path, component):
    target = tmp_path / "target"
    target.mkdir()
    linked = tmp_path / "research" / component
    linked.parent.mkdir(parents=True)
    linked.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic links"):
        CodexIdentity(tmp_path / "research", "one").prepare()
    assert not list(target.iterdir())


def test_codex_tools_do_not_inherit_hosted_peers_api_keys(store, monkeypatch):
    config = slot_config()
    monkeypatch.setenv("TEST_AGENT_2_KEY", "synthetic-peer-key")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.invalid:8080")
    backend = bounded_backend(config, Orchestrator(store))
    environment = backend.identity.environment()
    assert "TEST_AGENT_2_KEY" not in environment
    assert os.environ["TEST_AGENT_2_KEY"] == "synthetic-peer-key"
    assert environment["HTTPS_PROXY"] == "http://proxy.example.invalid:8080"


@pytest.mark.parametrize("modes", [("codex", "chat"), ("chat", "codex")])
def test_mixed_solve_pins_primary_and_parses_each_transport(store, monkeypatch, modes):
    calls = install_routes(monkeypatch)
    config = slot_config(*modes)
    engine = Orchestrator(store)
    created = engine.create(config, problem(), workflow=Workflow.SOLVE)
    assert created.mode == modes[0]
    assert created.config["backend"] == created.config["solve"]["agent_slots"][0]["backend"]
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert len(run.candidates) == 2 and run.usage.measured_calls == 3
    assert set(run.native.solve_team.workers) == {"primary", "slot-agent-2"}
    assert [call["backend"].mode for call in calls if call["role"] == "supervisor"] == [modes[0]]
    assert {call["backend"].mode for call in calls if call["role"] == "researcher"} == set(modes)
    for call in calls:
        assert call["backend"].native_multi_agent is False
        if call["role"] == "researcher" and call["backend"].mode == "chat":
            assert "Hosted tools cannot read local workspace paths" in call["prompt"]
    for item in run.native.history:
        assert item["slot_id"] in {"agent-1", "agent-2"}
        assert item["events"].endswith("response.json" if item["mode"] == "chat" else "codex.events.jsonl")
        assert item["model"] == f"{item['mode']}-test-model"


def test_regrouping_and_resume_keep_each_slot_conversation(store, monkeypatch):
    calls = install_routes(monkeypatch, complete=False)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(slot_config(calls=6), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.PAUSED and run.iteration == 6, run.last_error
    assert set(run.native.solve_team.workers) == {"primary", "slot-agent-2"}
    second = run.native.solve_team.workers["slot-agent-2"]
    assert second.slot_id == "agent-2" and second.group == "challenge"
    assert second.session_id is None and second.response_id.startswith("chat:")
    primary = run.native.solve_team.workers["primary"]
    assert primary.response_id is None and primary.session_id.startswith("codex:")
    assert run.native.solve_team.supervisor_session_id != primary.session_id
    config = Config.model_validate(run.config)
    config.budget.max_iterations = 9
    resumed = engine.resume(run.id, config=config)
    assert resumed.state == State.PAUSED and resumed.iteration == 9
    for mode in ("codex", "chat"):
        selected = [call for call in calls if call["role"] == "researcher" and call["backend"].mode == mode]
        assert len(selected) == 3
        assert [item["previous_session"] for item in selected] == [None, selected[0]["session"], selected[0]["session"]]


def test_saved_solve_rejects_identity_route_or_count_changes(store, monkeypatch):
    install_routes(monkeypatch, complete=False)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(slot_config(), problem(), workflow=Workflow.SOLVE).id)
    config = Config.model_validate(run.config)
    config.solve.agent_slots[1].backend.chat.api_key_env = "OTHER_ACCOUNT_KEY"
    with pytest.raises(ValueError, match="keeps its agent slots"):
        engine.resume(run.id, config=config)
    assert store.load(run.id).config == run.config
    with pytest.raises(ValueError, match="primary transport"):
        engine.resume(run.id, mode="chat")
    config = Config.model_validate(run.config)
    config.solve = SolveConfig(parallel_agents=1, agent_slots=config.solve.agent_slots[:1])
    with pytest.raises(ValueError, match="keeps its agent slots"):
        engine.resume(run.id, config=config)


def test_any_responses_slot_obeys_zero_cost_restriction(store):
    config = slot_config()
    config.budget.max_external_cost_usd = 0
    with pytest.raises(ValueError, match="max_external_cost_usd"):
        Orchestrator(store).create(config, problem(), workflow=Workflow.SOLVE)
    assert not store.list_runs()


@pytest.mark.parametrize("mode", ["codex", "chat"])
def test_single_configured_slot_uses_account_without_supervisor(store, monkeypatch, mode):
    calls = install_routes(monkeypatch)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(slot_config(mode), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED, run.last_error
    assert len(calls) == 1 and calls[0]["role"] == "researcher"
    assert calls[0]["backend"].mode == mode
    assert calls[0]["backend"].codex_identity == ("agent-1" if mode == "codex" else None)


@pytest.mark.parametrize("modes", [("codex", "chat"), ("chat", "codex")])
def test_mixed_finalization_uses_first_slot_and_existing_primary_session(store, monkeypatch, modes):
    from test_solve_continuation import clock

    advance = clock(monkeypatch)
    started = threading.Barrier(2, action=lambda: advance(0.7))
    calls = []

    class ExpiringBackend(RoutedBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "Solve researcher:" in prompt:
                started.wait(timeout=5)
            return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)

    install_routes(monkeypatch, factory=lambda config, root: ExpiringBackend(config, calls, complete=False))
    config = slot_config(*modes, calls=10)
    config.budget.max_wall_time_minutes = 0.01
    config.budget.finalize_minutes = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED, run.last_error
    assert run.native.finalization.status == "completed" and len(calls) == 4
    closing = calls[-1]
    assert "SOLVE finalization" in closing["prompt"]
    assert closing["backend"].mode == modes[0]
    assert closing["previous_session"] == next(
        call["session"] for call in calls
        if call["role"] == "researcher" and call["backend"].mode == modes[0]
    )
    assert run.native.history[-1]["slot_id"] == "agent-1"


def test_pending_hosted_peer_is_recovered_through_its_original_route(store, monkeypatch):
    config = slot_config()
    engine = Orchestrator(store)
    run = engine.create(config, problem(), workflow=Workflow.SOLVE)
    coordinator = NativeRunner(engine).team
    workers = coordinator.selected_workers(run, Config.model_validate(run.config), 2)
    attempt = coordinator.prepare_attempt(run, workers[1])
    atomic_write(store.run_dir(run.id) / attempt["directory"] / "session.json", json_text({"id": "response-saved"}))
    recovered = []

    class RecoveryBackend:
        def recover_native(self, directory, timeout, **kwargs):
            recovered.append(directory)
            kwargs["on_session"]("response-saved")
            return BackendResult(BackendStatus.INTERRUPTED, invoked=True, pending=True,
                                 session_id="response-saved", error="Still running")

    def factory(settings, root):
        assert settings.mode == "chat" and settings.chat.api_key_env == "TEST_AGENT_2_KEY"
        return RecoveryBackend()

    monkeypatch.setattr("mathlottery.solve.attempts.research_backend", factory)
    receipt = coordinator.attempts.recover(run, attempt, Config.model_validate(run.config))
    assert len(recovered) == 1 and receipt["result"]["pending"]
    coordinator.attempts.remember(run, attempt)
    assert workers[1].response_id == "response-saved" and workers[1].session_id is None
    config = Config.model_validate(run.config)
    config.solve.agent_slots[1].backend.model = "different-model"
    with pytest.raises(ValueError, match="route changed"):
        attempt_config(config, attempt)


def test_custom_registered_provider_is_resolved_for_slot_and_frozen(store):
    raw = slot_config().model_dump(mode="json")
    raw["model_providers"] = {"research_api": {
        "label": "Research API", "chat": {
            "base_url": "https://api.example.invalid/v1", "api_key_env": "RESEARCH_API_KEY", "tools": [],
        },
    }}
    raw["solve"]["agent_slots"][1]["backend"]["provider"] = "research_api"
    config = Config.model_validate(raw)
    api = config.solve.agent_slots[1].backend
    assert api.mode == "chat" and api.chat.tools == []
    assert api.chat.api_key_env == "RESEARCH_API_KEY"
    run = Orchestrator(store).create(config, problem(), workflow=Workflow.SOLVE)
    config.model_providers["research_api"].chat.base_url = "https://changed.example.invalid/v1"
    restored = Config.model_validate(store.load(run.id).config)
    assert restored.solve.agent_slots[1].backend.chat.base_url == "https://api.example.invalid/v1"
    # Parent-field assignment must not degrade sibling nested models into raw dicts.
    config.backend = BackendConfig(model="global")
    assert isinstance(config.solve, SolveConfig)
    config.solve = config.solve.model_copy(deep=True)
    assert isinstance(config.backend, BackendConfig)


def test_mixed_pending_research_does_not_discount_remote_time(store):
    run = Orchestrator(store).create(slot_config(), problem(), workflow=Workflow.SOLVE)
    start = datetime.now(timezone.utc) - timedelta(seconds=10)
    run.active_since = start.isoformat()
    resources = {"state": "interrupted", "started_at": start.isoformat(),
                 "updated_at": (start + timedelta(seconds=2)).isoformat()}
    assert budget.interrupted_elapsed(run, resources) == pytest.approx(2)
    run.native.solve_team.active_attempts = [{"mode": "chat"}]
    assert budget.interrupted_elapsed(run, resources) is None


def test_mixed_rate_limit_stops_without_switching_accounts(store, monkeypatch):
    calls, barrier = [], threading.Barrier(2)

    class LimitedBackend(RoutedBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "resource supervision" in prompt:
                return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            calls.append({"mode": self.config.mode, "key": self.config.chat.api_key_env})
            barrier.wait(timeout=5)
            if self.config.mode == "chat":
                return BackendResult(BackendStatus.RATE_LIMITED, invoked=True, error="Rate limit fixture")
            return BackendResult(BackendStatus.INTERRUPTED, invoked=True)

    install_routes(monkeypatch, factory=lambda config, root: LimitedBackend(config, []))
    engine = Orchestrator(store)
    run = engine.drive(engine.create(slot_config(), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.RATE_LIMITED, run.last_error
    assert run.last_error == "Rate limit fixture"
    assert len(calls) == 2 and {call["mode"] for call in calls} == {"codex", "chat"}


def test_other_workflows_keep_global_route_even_when_slots_configured(store):
    config = slot_config("chat", "codex")
    config.backend = BackendConfig(model="global-model")
    run = Orchestrator(store).create(config, workflow=Workflow.FIND)
    assert run.mode == "codex" and run.config["backend"]["model"] == "global-model"
