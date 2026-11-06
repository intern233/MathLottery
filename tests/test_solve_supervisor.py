"""Dedicated supervision keeps its own identity, capacity and recovery route."""

import json
import threading

import pytest
from test_solve_campaign import CampaignBackend, theorem

from mathlottery.config import BackendConfig, Config
from mathlottery.models import Problem, State, Workflow
from mathlottery.providers.agent_roster import AgentRoster
from mathlottery.providers.credentials import known_credential_env_names
from mathlottery.runtime import budget
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.attempts import bounded_backend
from mathlottery.solve.routes import attempt_config, route_fingerprint, validate_resume_routes
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.web.agent_roster import AgentConnections
from mathlottery.web.jobs import BusyError
from mathlottery.web.service import WebService


def dedicated_config():
    return Config.model_validate({
        "solve": {
            "coordination": "supervised", "parallel_agents": 4,
            "supervisor_backend": {"mode": "codex", "model": "supervisor-test"},
            "agent_slots": [{"id": f"research-{i}", "backend": {
                "mode": "codex", "codex_auth": "api_key", "model": "research-test",
                "codex_api_key_env": "RESEARCH_KEY_A" if i <= 2 else "RESEARCH_KEY_B",
            }} for i in range(1, 5)],
        },
        "budget": {"max_iterations": 20, "max_wall_time_minutes": 3},
    })


@pytest.mark.parametrize("timeout", [600, 1800, None])
def test_supervisor_deadline_is_explicit_and_can_allow_long_reviews(store, timeout):
    config = Config.model_validate({"solve": {
        "parallel_agents": 1, "supervisor_timeout_seconds": timeout,
    }})
    backend = CampaignBackend()
    engine = Orchestrator(store, backend)
    created = engine.create(config, Problem(id="identity", title="Identity", statement=theorem()["statement"]),
                            workflow=Workflow.SOLVE)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    supervision = [c for c in backend.calls if c["author"] == "supervisor"]
    assert len(supervision) == 2
    for call in supervision:
        assert call["timeout"] == (float("inf") if timeout is None else timeout)
        expected = "No per-call supervision deadline" if timeout is None else f"{timeout}-second deadline"
        assert expected in call["prompt"]
        assert "defer their formal review opinions to the next snapshot" in call["prompt"]
    assert not run.candidates[-1].reviews


def test_rejected_partial_acceptance_preserves_feedback_for_resume(store):
    sent_invalid = False

    def supervision(backend, payload, context, kwargs):
        nonlocal sent_invalid
        if not context["candidate_index"]:
            return
        candidate = context["candidate_index"][-1]
        payload["solution_reviews"] = [{
            "candidate_id": candidate["id"], "candidate_sha256": candidate["sha256"],
            "verdict": "needs_work" if sent_invalid else "accepted",
            "original_problem_coverage": "partial", "rationale": "The restricted result is sound.",
            "checks": [{"claim": "Restricted identity", "reasoning": "Definition", "status": "supported"}],
            "remaining_obligations": ["Prove the full original target"],
        }]
        sent_invalid = True

    config = Config.model_validate({"solve": {"parallel_agents": 1},
                                    "budget": {"max_iterations": 5}})
    backend = CampaignBackend(complete=False, supervision=supervision)
    engine = Orchestrator(store, backend)
    created = engine.create(config, Problem(id="identity", title="Identity", statement=theorem()["statement"]),
                            workflow=Workflow.SOLVE)
    paused = engine.drive(created.id)
    assert paused.state == State.PAUSED
    failed = paused.native.history[-1]
    assert "Accept only full original-problem coverage" in failed["checkpoint_error"]
    assert not paused.native.solve_team.campaign.accepted_candidate_id
    resumed = engine.resume(created.id)
    assert resumed.state == State.COMPLETED, resumed.last_error
    correction_prompt = backend.calls[3]["prompt"]
    assert failed["answer"] in correction_prompt
    assert failed["checkpoint_error"] in correction_prompt
    assert "without repeating the entire mathematical audit" in correction_prompt
    assert "sound PARTIAL or CONDITIONAL" in correction_prompt
    assert not resumed.native.solve_team.campaign.accepted_candidate_id
    assert not resumed.candidates[-1].reviews


def test_dedicated_supervision_reviews_four_busy_researchers_then_drains(store, monkeypatch):
    expired, inspected = threading.Event(), threading.Event()
    started = threading.Barrier(4, action=expired.set)
    original = budget.remaining
    monkeypatch.setattr(budget, "remaining", lambda run, config: 0 if expired.is_set() else original(run, config))
    observed = []

    def research(backend, author, workspace, kwargs, turn):
        started.wait(5)
        if author == "primary":
            atomic_write(workspace / "outbox/lemma.json", json_text({
                "id": "lemma", "kind": "result", "title": "Identity", "body": "Proof inline",
                "theorem": theorem(),
            }))
        assert inspected.wait(5), "Dedicated supervision must run with all four researchers busy"
        assert not kwargs["cancelled"](), "The soft deadline must not kill current research"

    def supervision(backend, payload, context, kwargs):
        if context["required_board_reviews"]:
            assert len(backend.active) == 5
            assert "primary" in backend.active
            inspected.set()

    delegate = CampaignBackend(agents=4, dedicated=True, complete=False,
                               research=research, supervision=supervision)

    class CapturingBackend:
        def __init__(self, settings):
            self.settings = settings

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            observed.append((self.settings, "global supervision" in prompt, directory))
            return delegate.invoke_native(prompt, directory, workspace, timeout, **kwargs)

    monkeypatch.setattr("mathlottery.solve.attempts.research_backend",
                        lambda settings, root: CapturingBackend(settings))
    config = dedicated_config()
    config.solve.board_review_interval_seconds = 0.01
    engine = Orchestrator(store)
    created = engine.create(config, Problem(id="identity", title="Identity", statement=theorem()["statement"]),
                            workflow=Workflow.SOLVE)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert inspected.is_set() and delegate.research_turns == 4
    assert run.native.solve_team.campaign.closed
    assert not run.native.solve_team.campaign.accepted_candidate_id
    assert all(not candidate.reviews for candidate in run.candidates)
    assert run.usage.measured_calls == len(observed)
    assert run.native.solve_team.supervisor_usage.measured_calls == sum(s for _, s, _ in observed)
    assert config.solve.invocation_limit == 5
    for settings, supervising, directory in observed:
        attempt = json.loads((directory / "turn.json").read_text())
        assert settings.native_multi_agent is False
        if supervising:
            assert settings.model == "supervisor-test" and settings.codex_auth == "chatgpt"
            assert settings.codex_identity is None
            assert attempt["route_kind"] == "supervisor" and attempt["slot_id"] is None
        else:
            assert settings.codex_auth == "api_key" and settings.model == "research-test"
            index = int(settings.codex_identity.rsplit("-", 1)[1])
            assert settings.codex_api_key_env == ("RESEARCH_KEY_A" if index <= 2 else "RESEARCH_KEY_B")
            assert attempt["slot_id"] == settings.codex_identity
    supervisors = [c for c in delegate.calls if c["author"] == "supervisor"]
    assert supervisors[0]["session"] is None
    assert all(c["session"] == "session-supervisor" for c in supervisors[1:])
    assert "Purpose: closing" in supervisors[-1]["prompt"]


@pytest.mark.parametrize("changes,error", [
    ({"coordination": "allocation"}, "supervised Solve"),
    ({"agent_slots": []}, "configured researcher slots"),
    ({"supervisor_backend": {"mode": "manual"}}, "native Codex"),
    ({"supervisor_backend": {"mode": "chat", "codex_identity": "supervisor"}}, "cannot select"),
    ({"supervisor_backend": {"mode": "codex", "codex_auth": "api_key",
                             "codex_identity": "research-1"}}, "separate Codex"),
])
def test_dedicated_supervision_rejects_ambiguous_or_shared_routes(changes, error):
    data = dedicated_config().model_dump()
    data["solve"].update(changes)
    with pytest.raises(ValueError, match=error):
        Config.model_validate(data)


def test_saved_supervisor_route_cannot_fall_back_or_move_account():
    config = dedicated_config()
    attempt = {"role": "supervision", "route_kind": "supervisor", "slot_id": None,
               "route_sha256": route_fingerprint(config.solve.supervisor_backend)}
    selected = attempt_config(config, attempt)
    assert selected.backend == config.solve.supervisor_backend
    assert config.backend != selected.backend
    changed = config.model_copy(deep=True)
    changed.solve.supervisor_backend.codex_identity = "other"
    with pytest.raises(ValueError, match="route changed"):
        attempt_config(changed, attempt)
    with pytest.raises(ValueError, match="supervisor account and model"):
        validate_resume_routes(config, changed)
    changed.solve.supervisor_backend = None
    with pytest.raises(ValueError, match="unavailable"):
        attempt_config(changed, attempt)
    with pytest.raises(ValueError, match="shared supervisor"):
        attempt_config(config, {"role": "supervision", "slot_id": "research-1"})
    with pytest.raises(ValueError, match="incomplete"):
        attempt_config(config, {"role": "supervision", "route_kind": "supervisor"})
    with pytest.raises(ValueError, match="unavailable"):
        attempt_config(config, {**attempt, "role": "research"})


def test_api_supervisor_obeys_zero_cost_restriction(store):
    config = dedicated_config()
    for slot in config.solve.agent_slots:
        slot.backend.codex_auth = "chatgpt"
    config.solve.supervisor_backend.codex_auth = "api_key"
    config.budget.max_external_cost_usd = 0
    with pytest.raises(ValueError, match="max_external_cost_usd"):
        Orchestrator(store).create(config, Problem(id="test", title="Test", statement="Test"),
                                   workflow=Workflow.SOLVE)
    assert not store.list_runs()


def test_supervisor_key_is_excluded_from_research_environment(store, monkeypatch):
    config = dedicated_config()
    config.solve.supervisor_backend = BackendConfig(
        codex_auth="api_key", codex_api_key_env="SUPERVISOR_CREDENTIAL")
    monkeypatch.setenv("SUPERVISOR_CREDENTIAL", "synthetic-supervisor-secret")
    names = known_credential_env_names(store.root, config)
    assert {"SUPERVISOR_CREDENTIAL", "RESEARCH_KEY_A", "RESEARCH_KEY_B"} <= names
    backend = bounded_backend(config, Orchestrator(store))
    assert "SUPERVISOR_CREDENTIAL" not in backend.environment()
    assert "synthetic-supervisor-secret" not in str(backend.authentication_overrides())


def test_supervisor_provider_is_resolved_and_roster_can_be_applied():
    data = dedicated_config().model_dump()
    data["model_providers"] = {"other": {"label": "Other", "chat": {
        "api_key_env": "SUPERVISOR_CREDENTIAL", "base_url": "https://example.invalid/v1", "tools": [],
    }}}
    data["solve"]["supervisor_backend"] = {"provider": "other", "model": "test"}
    config = Config.model_validate(data)
    assert config.solve.supervisor_backend.mode == "chat"
    assert config.solve.supervisor_backend.api_key_env_name == "SUPERVISOR_CREDENTIAL"
    resolved = AgentRoster(slots=config.solve.agent_slots).apply(config)
    assert resolved.solve.supervisor_backend == config.solve.supervisor_backend
    assert resolved.solve.agent_slots == config.solve.agent_slots


def test_running_dedicated_supervisor_blocks_only_its_account_changes(store, monkeypatch):
    config = dedicated_config()
    config.solve.supervisor_backend.codex_identity = "supervisor"
    service = WebService(store.root)
    run = Orchestrator(service.store).create(
        config, Problem(id="test", title="Test", statement="Test"), workflow=Workflow.SOLVE)
    monkeypatch.setattr(service.jobs, "running", lambda run_id: run_id == run.id)
    with pytest.raises(BusyError):
        service.ensure_account_change_allowed("supervisor")
    service.ensure_account_change_allowed()  # The default login is unused.
    service.ensure_account_change_allowed("research-1")  # API routes do not use subscription auth.


def test_web_preflight_checks_supervisor_before_research_slots(store, monkeypatch):
    from mathlottery.providers.codex import NativeWorkBackend

    config = dedicated_config()
    checked = []

    def inspect(backend):
        checked.append(backend.config.model_copy(deep=True))
        assert {"RESEARCH_KEY_A", "RESEARCH_KEY_B"} <= backend.identity.excluded_env
        return {"available": True}

    monkeypatch.setattr(NativeWorkBackend, "check", inspect)
    connections = AgentConnections(WebService(store.root))
    connections.ensure_ready(config)
    assert checked[0] == config.solve.supervisor_backend
    assert len(checked) == 5
    assert checked[1:] == [slot.backend for slot in config.solve.agent_slots]

    monkeypatch.setattr(NativeWorkBackend, "check", lambda backend: (_ for _ in ()).throw(ValueError("Missing login")))
    with pytest.raises(ValueError, match="Supervisor: Missing login"):
        connections.ensure_ready(config)
