"""Real orchestration with deterministic native agents; no credentials/model billing."""

import json
import re
import threading
import time
from dataclasses import replace

import pytest

from mathlottery.config import Config
from mathlottery.models import Problem, State, Workflow
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.attempts import bounded_backend
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.web.service import Overrides, ResumeRequest, StartRequest, WebService


def problem():
    return Problem(id="addition", title="Addition", statement="For every natural n, n + 0 = n.")


class TeamBackend:
    def __init__(self, *, complete=True, plans=None, synchronize=False):
        self.complete, self.plans = complete, plans
        self.calls, self.active, self.peak = [], 0, 0
        self.lock = threading.Lock()
        self.barrier = threading.Barrier(2) if synchronize else None
        self.planning = 0

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        ids = dict(re.findall(r"(?m)^(run_id|task_id): (.+)$", prompt))
        supervisor = "Task: SOLVE resource supervision" in prompt
        session = kwargs.get("session_id") or f"session-{workspace.name}"
        kwargs["on_session"](session)
        with self.lock:
            self.calls.append({"supervisor": supervisor, "session": kwargs.get("session_id"),
                               "workspace": workspace, "prompt": prompt})
        if supervisor:
            groups = self.plans[self.planning] if self.plans else [
                {"id": "algebra", "agents": 2, "mode": "peer", "objective": "Prove the identity."},
            ]
            self.planning += 1
            payload = {**ids, "rationale": "Two explicit independent obligations.", "groups": groups}
            text = "```solve-plan\n" + json.dumps(payload) + "\n```\n"
        else:
            with self.lock:
                self.active += 1
                self.peak = max(self.peak, self.active)
            try:
                if self.barrier:
                    self.barrier.wait(timeout=5)
                atomic_write(workspace / "lemma.md", "By the defining equation of addition, n + 0 = n.")
                atomic_write(workspace / "outbox" / f"{ids['task_id']}.json", json_text({
                    "id": ids["task_id"] + "-lemma", "kind": "result", "title": "Addition lemma",
                    "body": "Check the defining equation.", "artifacts": ["lemma.md"],
                    "check_status": "author_checked",
                }))
                payload = {**ids, "kind": "candidate", "conclude": True, "summary": "Identity derived.",
                           "candidate": {"claim": problem().statement, "proof": "By definition of addition.",
                                         "scope": "COMPLETE" if self.complete else "PARTIAL",
                                         "remaining_obligations": [] if self.complete else ["One open obligation."]}}
                text = "```mathlottery\n" + json.dumps(payload) + "\n```\n"
            finally:
                with self.lock:
                    self.active -= 1
        return BackendResult(BackendStatus.COMPLETED, text=text, session_id=session, invoked=True,
                             usage={"input_tokens": 10, "output_tokens": 2})


def setup(store, backend, *, calls=3, parallel=2):
    config = Config()
    config.solve.coordination = "allocation"  # Historical checkpoint protocol remains supported.
    config.solve.parallel_agents = parallel
    config.budget.max_iterations = calls
    config.budget.finalize_minutes = 0
    engine = Orchestrator(store, backend)
    return engine, engine.create(config, problem(), workflow=Workflow.SOLVE)


def test_parallel_cap_candidates_and_separate_supervisor_accounting(store):
    backend = TeamBackend(synchronize=True)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.peak == 2 and len(backend.calls) == 3
    assert len(run.candidates) == 2 and all(not c.reviews for c in run.candidates)
    assert run.iteration == run.usage.measured_calls == 3
    assert run.usage.input_tokens == 30
    assert run.native.solve_team.supervisor_usage.input_tokens == 10
    assert run.native.solve_team.supervisor_usage.measured_calls == 1
    assert not run.native.solve_team.active_attempts and not run.native.solve_team.pending_receipts
    assert run.native.solver_session_id == "session-workspace"
    messages = SolveBoard(store, run.id).messages()
    assert len(messages) == 4
    assert all(m["standing"] == "unverified" for m in messages)
    assert any(m["check_status"] == "author_checked" for m in messages)
    detail = WebService(store.root).detail(run.id)["solve_team"]
    assert all("session_id" not in worker for worker in detail["workers"])
    assert detail["parallel_agents"] == 2


def test_resize_preserves_primary_and_inactive_conversations(store):
    backend = TeamBackend(complete=False, plans=[
        [{"id": "algebra", "agents": 2, "objective": "First route"}],
        [{"id": "algebra", "agents": 1, "objective": "Continue first route"},
         {"id": "alternative", "agents": 1, "mode": "critique", "objective": "Challenge the assumption"}],
    ])
    engine, created = setup(store, backend, calls=6)
    run = engine.drive(created.id)
    assert run.state == State.PAUSED and run.stop_reason == "Iteration budget reached", run.last_error
    assert run.native.solve_team.rounds == 2
    assert set(run.native.solve_team.workers) == {"primary", "algebra-2", "alternative-1"}
    primaries = [c for c in backend.calls if not c["supervisor"] and c["workspace"].name == "workspace"]
    assert [c["session"] for c in primaries] == [None, "session-workspace"]
    assert "Identity derived" in backend.calls[3]["prompt"]
    assert len(run.candidates) == 4 and run.usage.measured_calls == 6


def test_bad_supervisor_allocation_cannot_exceed_cap(store):
    backend = TeamBackend(plans=[[{"id": "oversized", "agents": 10, "objective": "Too many"}]])
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert len(backend.calls) == 2
    assert "exceeds" in run.native.solve_team.decision
    assert backend.peak == 1


def test_durable_batch_replays_without_repeating_or_double_charging(store, monkeypatch):
    backend = TeamBackend(synchronize=True)
    engine, created = setup(store, backend)
    original_save = store.save

    def crash_after_commit(run, event, **details):
        original_save(run, event, **details)
        if event == "solve_round_received":
            raise RuntimeError("simulated crash after durable receipts")

    monkeypatch.setattr(store, "save", crash_after_commit)
    paused = engine.drive(created.id)
    assert paused.state == State.FAILED
    assert len(paused.native.solve_team.pending_receipts) == 2
    assert paused.usage.measured_calls == 1
    monkeypatch.setattr(store, "save", original_save)
    resumed = engine.resume(created.id)
    assert resumed.state == State.COMPLETED, resumed.last_error
    assert len(backend.calls) == 3 and resumed.usage.measured_calls == 3
    assert len(resumed.candidates) == 2


def test_hosted_pending_response_recovers_without_resubmitting_or_losing_peer_receipts(store):
    class PendingBackend(TeamBackend):
        ready = False

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            result = super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            if workspace.name != "workspace":
                return result
            self.final_result = result
            return replace(result, status=BackendStatus.INTERRUPTED, pending=True,
                           text="Partial streamed derivation", usage=None, error="Pending remote response")

        def recover_native(self, directory, timeout, **kwargs):
            kwargs["on_session"](self.final_result.session_id)
            if not self.ready:
                return replace(self.final_result, status=BackendStatus.INTERRUPTED, pending=True,
                               text="Partial streamed derivation", usage=None, error="Pending remote response")
            return self.final_result

    backend = PendingBackend(synchronize=True)
    config = Config()
    config.backend.mode = "chat"
    config.budget.max_external_cost_usd = None
    config.budget.max_iterations = 3
    config.solve.parallel_agents = 2
    config.solve.coordination = "allocation"
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.PAUSED and run.iteration == 2
    assert len(run.candidates) == 1 and len(run.native.solve_team.active_attempts) == 1
    assert run.native.active_attempt is None
    messages = SolveBoard(store, run.id).messages()
    waiting = engine.resume(run.id)
    assert waiting.state == State.PAUSED and waiting.iteration == 2
    assert len(backend.calls) == 3
    assert SolveBoard(store, run.id).messages() == messages
    backend.ready = True
    done = engine.resume(run.id)
    assert done.state == State.COMPLETED, done.last_error
    assert len(backend.calls) == 3 and done.iteration == done.usage.measured_calls == 3
    assert done.usage.input_tokens == 30 and len(done.candidates) == 2
    assert done.native.solve_team.workers["primary"].turns == 1
    assert not done.native.solve_team.active_attempts
    # The later final answer is a new immutable publication, not a rewrite of a partial post.
    assert len(SolveBoard(store, run.id).messages()) == len(messages) + 1


def test_primary_uses_latest_single_agent_session_when_reentering_team_mode(store):
    from mathlottery.runtime.native import NativeRunner

    engine, run = setup(store, TeamBackend())
    coordinator = NativeRunner(engine).team
    config = Config.model_validate(run.config)
    first = coordinator.selected_workers(run, config, 2)[0]
    first.session_id = "old-team-session"
    run.native.solver_session_id = "latest-single-session"
    run.native.solver_response_id = "latest-single-response"
    resumed = coordinator.selected_workers(run, config, 2)[0]
    assert resumed.session_id == "latest-single-session"
    assert resumed.response_id == "latest-single-response"


def test_new_hosted_worker_retains_pre_team_research_context(store):
    from mathlottery.runtime.native import NativeRunner

    engine, run = setup(store, TeamBackend())
    run.mode = "chat"
    run.native.solver_response_id = "existing-primary-chain"
    run.native.history.append({"task_id": "earlier", "role": "research", "answer": "tasks/earlier/answer.md"})
    atomic_write(store.run_dir(run.id) / "tasks/earlier/answer.md", "AN_EARLIER_ESTABLISHED_LEMMA")
    team = NativeRunner(engine).team
    config = Config.model_validate(run.config)
    worker = team.selected_workers(run, config, 2)[0]
    worker.response_id = None  # A newly started conversation cannot read the old chain.
    attempt = team.prepare_attempt(run, worker)
    prompt = team.researcher_prompt(run, worker, attempt, config, SolveBoard(store, run.id))
    assert "AN_EARLIER_ESTABLISHED_LEMMA" in prompt


def test_parallel_activity_and_progress_are_visible_before_any_receipt_returns(store):
    from mathlottery.models import SolveGroup
    from mathlottery.runtime.native import NativeRunner
    from mathlottery.telemetry.activity import ActivityReporter

    engine, run = setup(store, TeamBackend())
    run.native.solve_team.groups = [SolveGroup(id="algebra", agents=2, objective="Research")]
    coordinator = NativeRunner(engine).team
    workers = coordinator.selected_workers(run, Config.model_validate(run.config), 2)
    for worker, kind in zip(workers, ["search", "command"], strict=True):
        attempt = coordinator.prepare_attempt(run, worker)
        path = store.run_dir(run.id) / attempt["directory"]
        ActivityReporter(path).record(kind, "running", "PRIVATE_TOOL_INPUT")
        atomic_write(path / "progress.md", f"Visible work by {worker.id}")
    web = WebService(store.root)
    detail = web.detail(run.id)
    assert detail["progress"]["text"] == "Visible work by primary"
    assert detail["activity"]["current"]["kind"] in {"search", "command"}
    assert {w["activity"]["current"]["kind"] for w in detail["solve_team"]["workers"]} == {"search", "command"}
    archive = web.activity_archive(run.id).decode()
    assert '"search"' in archive and '"command"' in archive
    assert "PRIVATE_TOOL_INPUT" not in archive


@pytest.mark.parametrize("mode", ["codex", "chat"])
def test_every_new_researcher_receives_the_selected_problem_dossier(store, mode):
    from mathlottery.models import Phase

    config = Config()
    config.backend.mode = mode
    config.budget.max_external_cost_usd = None
    config.budget.max_iterations = 3
    config.solve.parallel_agents = 2
    config.solve.coordination = "allocation"
    backend = TeamBackend()
    engine = Orchestrator(store, backend)
    found = engine.create(config, workflow=Workflow.FIND)
    found.problem, found.shortlist = problem(), [problem()]
    found.phase, found.state = Phase.REPORT, State.COMPLETED
    atomic_write(store.run_dir(found.id) / "workspace/notes.md", "PRIOR_DISCOVERY_OBLIGATION")
    store.save(found, "selected_problem_fixture")
    created = engine.solve_discovered(config, found.id, problem().id)
    done = engine.drive(created.id)
    assert done.state == State.COMPLETED, done.last_error
    for call in backend.calls:
        if call["supervisor"]:
            continue
        assert "user explicitly chose" in call["prompt"]
        if mode == "chat":
            assert "PRIOR_DISCOVERY_OBLIGATION" in call["prompt"]
        else:
            assert (call["workspace"] / "discovery-context/workspace/notes.md").read_text() == "PRIOR_DISCOVERY_OBLIGATION"


def test_single_agent_does_not_add_supervisor_or_independent_verify(store):
    backend = TeamBackend()
    engine, created = setup(store, backend, parallel=1)
    # The existing single-agent workspace does not need an outbox to use native tools.
    (store.run_dir(created.id) / "workspace/outbox").mkdir(parents=True)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert len(backend.calls) == 1 and not backend.calls[0]["supervisor"]
    assert run.native.solve_team.supervisor_usage.measured_calls == 0


def test_native_nested_delegation_is_disabled_only_for_bounded_solve(store, monkeypatch):
    captured = []
    monkeypatch.setattr("mathlottery.solve.attempts.research_backend", lambda config, root: captured.append(config))
    config = Config()
    config.backend.native_multi_agent = True
    config.backend.native_memories = True
    bounded_backend(config, Orchestrator(store))
    assert captured[0].native_multi_agent is False
    assert captured[0].native_memories is True
    assert captured[0].native_web_search == config.backend.native_web_search
    assert config.backend.native_multi_agent is True


def test_board_freezes_sources_and_propagates_retraction(store):
    engine, run = setup(store, TeamBackend())
    board = SolveBoard(store, run.id)
    work = store.run_dir(run.id) / "workspace"
    work.mkdir()
    (work / "proof.md").write_text("original proof")
    board.publish("a", "group-a", Message(id="lemma", kind="result", title="Lemma", body="Under H",
                  artifacts=["proof.md"]), work)
    board.publish("b", "group-b", Message(id="derived", kind="result", title="Corollary", body="Using lemma",
                  depends_on=["a:lemma"]), work)
    (work / "proof.md").write_text("changed proof")
    with pytest.raises(ValueError, match="immutable"):
        board.publish("a", "group-a", Message(id="lemma", kind="result", title="Lemma", body="Under H",
                      artifacts=["proof.md"]), work)
    with pytest.raises(ValueError, match="own message"):
        board.publish("b", "group-b", Message(id="bad", kind="retraction", title="No", body="No",
                      target="a:lemma"), work)
    board.publish("a", "group-a", Message(id="withdraw", kind="retraction", title="Gap found", body="H missing",
                  target="a:lemma"), work)
    messages = board.messages()
    assert [m["standing"] for m in messages] == ["retracted", "needs_recheck", "unverified"]
    source = store.run_dir(run.id) / messages[0]["artifacts"][0]["path"]
    assert source.read_text() == "original proof"
    assert "original proof" in board.context(hosted=True)
    board.project(work)
    index = json.loads((work / "bulletin/index.json").read_text())
    published = json.loads((work / index[0]["path"]).read_text())
    assert (work / published["artifacts"][0]["local_path"]).read_text() == "original proof"
    with pytest.raises(ValueError):
        board.publish("a", "group-a", Message(id="escape", kind="result", title="Bad", body="Bad",
                      artifacts=["../outside.md"]), work)


def test_material_download_is_run_scoped_and_checks_the_frozen_hash(store):
    from test_web import serving

    engine, run = setup(store, TeamBackend())
    other = engine.create(Config(), problem(), workflow=Workflow.SOLVE)
    board = SolveBoard(store, run.id)
    workspace = store.run_dir(run.id) / "workspace"
    atomic_write(workspace / "proof.md", "original proof")
    board.publish("a", "group", Message(id="proof", kind="result", title="Proof", body="Read the proof",
                                        artifacts=["proof.md"]), workspace)
    artifact = board.messages()[0]["artifacts"][0]
    query = {"sha256": artifact["sha256"]}
    with serving(WebService(store.root)) as (client, _):
        url = f"/api/runs/{run.id}/solve-material"
        response = client.get(url, params=query)
        assert response.status_code == 200 and response.text == "original proof"
        assert "attachment" in response.headers["Content-Disposition"]
        assert client.get(f"/api/runs/{other.id}/solve-material", params=query).status_code == 400
        assert client.get(url, params={"sha256": "../auth.json"}).status_code == 400
        assert client.get(url, params={**query, "path": "anything"}).status_code == 400
        atomic_write(store.run_dir(run.id) / artifact["path"], "mutated")
        assert client.get(url, params=query).status_code == 400


@pytest.mark.parametrize("value", [0, -1, 33, True, 2.5, "2"])
def test_parallelism_is_a_bounded_integer(value):
    with pytest.raises(ValueError):
        Overrides(solve_parallel_agents=value)


def test_web_solve_parallelism_is_per_task_and_resume_preserves_omitted_value(store, monkeypatch):
    web = WebService(store.root)
    monkeypatch.setattr(web, "config", Config)
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launches.append((args, kwargs)))
    summary = web.start(StartRequest(workflow="solve", statement=problem().statement,
                                    options=Overrides(solve_parallel_agents=4)))
    run = store.load(summary["id"])
    assert summary["settings"]["solve_parallel_agents"] == 4
    web.resume(run.id, ResumeRequest())
    assert launches[-1][1]["config"]["solve"]["parallel_agents"] == 4
    web.resume(run.id, ResumeRequest(solve_parallel_agents=2))
    assert launches[-1][1]["config"]["solve"]["parallel_agents"] == 2
    assert store.load(run.id).config["solve"]["parallel_agents"] == 4
    with pytest.raises(ValueError, match="only to Solve"):
        web.start(StartRequest(workflow="find", options=Overrides(solve_parallel_agents=2)))


def test_user_stop_joins_all_researchers_and_records_their_usage(store):
    class StoppingBackend(TeamBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "resource supervision" in prompt:
                return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            with self.lock:
                self.active += 1
            try:
                atomic_write(store.run_dir(created.id) / "stop.requested", "user stop")
                limit = time.monotonic() + 3
                while not kwargs["cancelled"]() and time.monotonic() < limit:
                    time.sleep(0.01)
                return BackendResult(BackendStatus.INTERRUPTED, invoked=True,
                                     usage={"input_tokens": 3, "output_tokens": 1})
            finally:
                with self.lock:
                    self.active -= 1
    backend = StoppingBackend()
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.CANCELLED, run.last_error
    assert backend.active == 0
    assert run.usage.measured_calls == 3
    assert not run.native.solve_team.active_attempts


def test_rate_limit_cancels_remaining_workers_and_keeps_the_rate_limit_reason(store):
    barrier = threading.Barrier(2)

    class LimitedBackend(TeamBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "resource supervision" in prompt:
                return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            barrier.wait(timeout=5)
            if workspace.name == "workspace":
                return BackendResult(BackendStatus.RATE_LIMITED, invoked=True, error="429 fixture")
            limit = time.monotonic() + 5
            while not kwargs["cancelled"]() and time.monotonic() < limit:
                time.sleep(0.01)
            assert kwargs["cancelled"](), "Sibling failure must cancel outstanding work"
            return BackendResult(BackendStatus.INTERRUPTED, invoked=True)

    engine, created = setup(store, LimitedBackend())
    run = engine.drive(created.id)
    assert run.state == State.RATE_LIMITED and run.last_error == "429 fixture"
    assert run.usage.unknown_calls == 2 and run.iteration == 3
    assert not run.native.solve_team.active_attempts


@pytest.mark.parametrize("mode", ["codex", "chat"])
def test_parallel_time_limit_uses_existing_single_closing_turn(store, mode, monkeypatch):
    from test_solve_continuation import clock

    advance = clock(monkeypatch)
    # Preparation/host load must not spend this test's research budget. Expire it
    # exactly once, only after both researchers have entered their native calls.
    research_started = threading.Barrier(2, action=lambda: advance(0.7))

    class BudgetExpiringBackend(TeamBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "Solve researcher:" in prompt:
                research_started.wait(timeout=5)
            return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)

    backend = BudgetExpiringBackend(complete=False)
    engine, created = setup(store, backend, calls=10)
    config = Config.model_validate(created.config)
    config.backend.mode = created.mode = mode
    config.budget.max_external_cost_usd = None
    config.budget.max_wall_time_minutes = 0.01
    config.budget.finalize_minutes = 1
    created.config = config.model_dump(mode="json")
    store.save(created, "short_time_fixture")
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert run.native.finalization.status == "completed"
    assert run.native.finalization.started_elapsed_seconds == pytest.approx(0.7)
    assert run.candidates[-1].scope == "PARTIAL"
    assert len(backend.calls) == 4
    assert sum("Solve researcher:" in call["prompt"] for call in backend.calls) == 2
    assert "SOLVE finalization" in backend.calls[-1]["prompt"]
    assert backend.calls[-1]["session"] == "session-workspace"
    assert "multiple researchers' results" in backend.calls[-1]["prompt"]
    assert ("Identity derived" if mode == "chat" else "bulletin/index.json") in backend.calls[-1]["prompt"]


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.VERIFY])
def test_parallel_configuration_does_not_change_other_stages(store, workflow):
    from test_solve_continuation import ScriptedBackend

    backend = ScriptedBackend({"kind": "stop", "summary": "Stage concluded."})
    config = Config()
    config.solve.parallel_agents = 4
    kwargs = {"problem": problem(), "proof": "Submitted proof"} if workflow == Workflow.VERIFY else {}
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(config, workflow=workflow, **kwargs).id)
    assert run.state == State.COMPLETED and len(backend.calls) == 1
    assert run.native.solve_team.rounds == 0
