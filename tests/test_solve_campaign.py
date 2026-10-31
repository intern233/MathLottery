"""Supervised research lifecycle against deterministic agents, without model billing."""

import json
import re
import threading
import time
from dataclasses import replace

import pytest

from mathlottery.config import Config
from mathlottery.models import Problem, Run, State, Workflow
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.solve.contracts import BoardReview
from mathlottery.storage.core import atomic_write, json_text


def theorem(statement="For every natural n, n + 0 = n."):
    return {"statement": statement, "proof_steps": [{"id": "definition", "statement": statement,
             "justification": "The defining equation of addition on the second argument."}],
            "conclusion_step": "definition"}


class CampaignBackend:
    def __init__(self, *, reject_first=False, complete=True, research=None, supervision=None, agents=1):
        self.calls, self.research_turns = [], 0
        self.reject_first, self.complete = reject_first, complete
        self.research, self.supervision, self.agents = research, supervision, agents
        self.lock = threading.Lock()
        self.active = set()

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        ids = dict(re.findall(r"(?m)^(run_id|task_id): (.+)$", prompt))
        supervising = "Task: SOLVE global supervision" in prompt
        author = "supervisor" if supervising else "primary" if workspace.name == "workspace" else workspace.name
        with self.lock:
            # Supervisor and primary must never consume slot 1 concurrently.
            assert not ({author, *self.active} >= {"primary", "supervisor"})
            self.active.add(author)
            self.calls.append({"author": author, "session": kwargs.get("session_id"),
                               "prompt": prompt, "directory": directory, "workspace": workspace,
                               "timeout": timeout})
            if not supervising:
                self.research_turns += 1
            turn = self.research_turns
        try:
            kwargs["on_session"]("session-" + author)
            if supervising:
                context = json.loads((workspace / "supervision-context.json").read_text())
                candidates = {c["id"]: c for c in json.loads((workspace / "candidates.json").read_text())}
                reviews = []
                for signal in context["signals"]:
                    if signal["status"] != "claimed_complete":
                        continue
                    c = candidates[signal["candidate_id"]]
                    rejected = self.reject_first and len(candidates) == 1
                    reviews.append({"candidate_id": c["id"], "candidate_sha256": c["sha256"],
                                    "verdict": "needs_work" if rejected else "accepted",
                                    "original_problem_coverage": "partial" if rejected else "full",
                                    "rationale": "Inspect the defining equation and quantifier.",
                                    "checks": [{"claim": c["claim"], "reasoning": "Definitional reduction.",
                                                "status": "gap" if rejected else "supported"}],
                                    "remaining_obligations": ["Explain n=0"] if rejected else []})
                payload = {**ids, "rationale": "Use the definition; cover boundary cases.",
                           "groups": [{"id": "algebra", "agents": self.agents, "objective": "Prove the identity, including n=0."}],
                           "solution_reviews": reviews, "summary": "Original target and proof inspected; keep gaps explicit."}
                payload["board_reviews"] = []
                for node in context["board"]["nodes"]:
                    if node["key"] in context["required_board_reviews"]:
                        payload["board_reviews"].append({"key": node["key"],
                            "content_sha256": node["content_sha256"], "verdict": "accepted",
                            "rationale": "The sole defining equation is checked", "checked_steps": ["definition"]})
                if self.supervision:
                    self.supervision(self, payload, context, kwargs)
                text = "```solve-supervision\n" + json.dumps(payload) + "\n```\n"
            else:
                if self.research:
                    self.research(self, author, workspace, kwargs, turn)
                payload = {**ids, "kind": "candidate", "conclude": True, "summary": f"Attempt {turn} returned.",
                           "candidate": {"claim": "For every natural n, n + 0 = n.",
                                         "proof": f"By the defining equation. Version {turn}.",
                                         "scope": "COMPLETE" if self.complete else "PARTIAL",
                                         "remaining_obligations": [] if self.complete else ["Remaining case"]}}
                text = "```mathlottery\n" + json.dumps(payload) + "\n```\n"
            return BackendResult(BackendStatus.COMPLETED, text=text, invoked=True,
                                 usage={"input_tokens": 10, "output_tokens": 2})
        finally:
            with self.lock:
                self.active.remove(author)


def setup(store, backend, *, calls=20, parallel=1):
    config = Config()
    config.solve.parallel_agents = parallel
    config.budget.max_iterations = calls
    config.budget.max_wall_time_minutes = 3
    engine = Orchestrator(store, backend)
    run = engine.create(config, Problem(id="identity", title="Identity", statement=theorem()["statement"]), workflow=Workflow.SOLVE)
    return engine, run


def test_complete_requires_supervisor_review_and_preserves_separate_verify(store):
    backend = CampaignBackend()
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    campaign = run.native.solve_team.campaign
    assert campaign.closed and campaign.accepted_candidate_id == run.candidates[-1].id
    assert campaign.candidate_reviews[-1]["verdict"] == "accepted"
    assert not run.candidates[-1].reviews
    assert backend.research_turns == 1 and run.iteration == len(backend.calls) == 3
    assert run.usage.input_tokens == 30
    assert run.native.solve_team.supervisor_usage.input_tokens == 20
    assert (store.run_dir(run.id) / campaign.summary_path).is_file()


def test_rejected_claim_gets_new_route_and_same_research_session(store):
    backend = CampaignBackend(reject_first=True)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.research_turns == 2
    assert [r["verdict"] for r in run.native.solve_team.campaign.candidate_reviews] == ["needs_work", "accepted"]
    calls = [c for c in backend.calls if c["author"] == "primary"]
    assert [c["session"] for c in calls] == [None, "session-primary"]
    assert "including n=0" in calls[-1]["prompt"]


@pytest.mark.parametrize("complete", [False, True])
def test_deadline_drains_current_attempt_then_reviews_without_relaunch(store, monkeypatch, complete):
    from mathlottery.runtime import budget

    expired = threading.Event()
    original = budget.remaining
    monkeypatch.setattr(budget, "remaining", lambda run, config: 0 if expired.is_set() else original(run, config))

    def research(backend, author, workspace, kwargs, turn):
        expired.set()
        time.sleep(0.25)
        assert not kwargs["cancelled"](), "Soft deadline must not cancel an in-flight researcher"

    backend = CampaignBackend(complete=complete, research=research)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.research_turns == 1 and len(backend.calls) == 3
    assert "Purpose: closing" in backend.calls[-1]["prompt"]
    assert bool(run.native.solve_team.campaign.accepted_candidate_id) == complete
    assert run.usage.measured_calls == 3
    assert backend.calls[1]["timeout"] == float("inf")
    assert backend.calls[-1]["timeout"] == created.config["solve"]["supervisor_timeout_seconds"]


def test_supervisor_reviews_while_peer_keeps_exploring(store):
    peer_started, reviewed = threading.Event(), threading.Event()

    def research(backend, author, workspace, kwargs, turn):
        if author == "primary":
            assert peer_started.wait(5)
        else:
            peer_started.set()
            assert reviewed.wait(5), "Supervisor must not wait for every peer's turn"

    def supervision(backend, payload, context, kwargs):
        if context["signals"]:
            reviewed.set()

    backend = CampaignBackend(agents=2, research=research, supervision=supervision)
    engine, created = setup(store, backend, parallel=2)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert reviewed.is_set() and len(run.candidates) == 2


def test_missing_solution_review_pauses_without_certifying_claim(store):
    def omit(backend, payload, context, kwargs):
        payload["solution_reviews"] = []
    backend = CampaignBackend(supervision=omit)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.PAUSED
    assert "Review every complete" in run.last_error
    assert run.native.solve_team.campaign.accepted_candidate_id is None
    assert not run.candidates[-1].reviews


def test_receipt_recovery_does_not_repeat_model_or_usage(store, monkeypatch):
    backend = CampaignBackend()
    engine, created = setup(store, backend)
    original = store.save
    crashed = False

    def crash(run, event, **details):
        nonlocal crashed
        original(run, event, **details)
        if event == "solve_signal_recorded" and details.get("role") == "research" and not crashed:
            crashed = True
            raise RuntimeError("Simulated crash after checkpoint commit")

    monkeypatch.setattr(store, "save", crash)
    paused = engine.drive(created.id)
    assert paused.state == State.FAILED
    monkeypatch.setattr(store, "save", original)
    run = engine.resume(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.research_turns == 1 and len(run.candidates) == 1
    assert run.usage.measured_calls == len(backend.calls) == 3


def test_legacy_saved_runs_keep_allocation_protocol():
    run = Run(id="run-000000000000", mode="codex", config={"solve": {"parallel_agents": 2}})
    assert run.config["solve"]["coordination"] == "allocation"
    assert Config().solve.coordination == "supervised"


def test_proof_graph_reviews_retraction_and_dependency_invalidation(store):
    engine, run = setup(store, CampaignBackend())
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    board = SolveBoard(store, run.id)
    board.publish("one", "algebra", Message(id="base", kind="result", title="Base", body="Base lemma", theorem=theorem()), workspace)
    board.publish("two", "algebra", Message(id="derived", kind="result", title="Derived", body="Use base", theorem=theorem(), depends_on=["one:base"]), workspace)
    for key in ["one:base", "two:derived"]:
        snapshot = {m["key"]: m["content_sha256"] for m in board.messages()}
        board.review(BoardReview(key=key, content_sha256=snapshot[key], verdict="accepted", rationale="Definition and hypotheses checked", checked_steps=["definition"]), "review-1", snapshot_hashes=snapshot)
    assert all(m["standing"] == "supervisor_accepted" for m in board.messages())
    board.publish("one", "algebra", Message(id="retract", kind="retraction", title="Retract", body="Gap found", target="one:base"), workspace)
    assert board.messages()[1]["standing"] == "needs_recheck"
    graph = board.graph()
    assert graph["edges"] == [{"from": "one:base", "to": "two:derived", "kind": "premise"}]


def test_partial_theorem_cannot_be_accepted(store):
    _, run = setup(store, CampaignBackend())
    board, workspace = SolveBoard(store, run.id), store.run_dir(run.id) / "workspace"
    board.publish("one", "algebra", Message(id="gap", kind="result", title="Gap", body="Open case",
                  theorem={**theorem(), "remaining_obligations": ["Unknown case"]}), workspace)
    message = board.messages()[0]
    with pytest.raises(ValueError, match="remaining obligations"):
        board.review(BoardReview(key=message["key"], content_sha256=message["content_sha256"],
                                 verdict="accepted", rationale="Bad approval", checked_steps=["definition"]),
                     "review-1", snapshot_hashes={message["key"]: message["content_sha256"]})


def test_periodic_board_review_is_requested_without_killing_primary(store):
    requested = threading.Event()

    def research(backend, author, workspace, kwargs, turn):
        atomic_write(workspace / "outbox" / "lemma.json", json_text({
            "id": "lemma", "kind": "result", "title": "Identity", "body": "Proof attached inline",
            "theorem": theorem(),
        }))
        end = time.monotonic() + 5
        while time.monotonic() < end:
            control = workspace / "bulletin/control.json"
            if control.exists() and json.loads(control.read_text())["supervisor_review_requested"]:
                assert not kwargs["cancelled"]()
                requested.set()
                break
            time.sleep(0.02)
        assert requested.is_set()

    backend = CampaignBackend(research=research)
    engine, created = setup(store, backend)
    created.config["solve"]["board_review_interval_seconds"] = 0.05
    store.save(created, "test_configured")
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert requested.is_set()
    assert "primary:lemma" in backend.calls[-1]["prompt"]


def test_iteration_slots_reserve_final_review(store):
    backend = CampaignBackend(agents=3, complete=False)
    engine, created = setup(store, backend, calls=4, parallel=3)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert len(backend.calls) == run.iteration == 4
    assert backend.research_turns == 2
    assert "Purpose: closing" in backend.calls[-1]["prompt"]


def test_explicit_stop_still_cancels_without_launching_review(store):
    def research(backend, author, workspace, kwargs, turn):
        atomic_write(workspace.parent / "stop.requested", "stop")
        end = time.monotonic() + 5
        while not kwargs["cancelled"]() and time.monotonic() < end:
            time.sleep(0.01)
        assert kwargs["cancelled"]()
    backend = CampaignBackend(research=research)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.CANCELLED and run.stop_reason == "Stopped by user"
    assert len(backend.calls) == 2


def test_objection_requires_explicit_resolution_then_invalidates_dependents(store):
    _, run = setup(store, CampaignBackend())
    board, workspace = SolveBoard(store, run.id), store.run_dir(run.id) / "workspace"
    board.publish("one", "algebra", Message(id="base", kind="result", title="Base", body="Identity", theorem=theorem()), workspace)
    board.publish("two", "algebra", Message(id="gap", kind="objection", title="Boundary", body="Check zero", target="one:base"), workspace)
    snapshot = {m["key"]: m["content_sha256"] for m in board.messages()}
    review = BoardReview(key="one:base", content_sha256=snapshot["one:base"], verdict="accepted",
                         rationale="Zero satisfies the same defining equation", checked_steps=["definition"])
    with pytest.raises(ValueError, match="outstanding objection"):
        board.review(review, "review-1", snapshot_hashes=snapshot)
    review.addressed_objections = ["two:gap"]
    board.review(review, "review-1", snapshot_hashes=snapshot)
    assert board.messages()[0]["standing"] == "supervisor_accepted"
    # Same receipt can be replayed without duplicating its review or charge.
    board.review(review, "review-1", snapshot_hashes=snapshot)
    board.publish("two", "algebra", Message(id="gap-2", kind="objection", title="Domain", body="Check domain", target="one:base"), workspace)
    assert board.messages()[0]["standing"] == "needs_recheck"


def test_mixed_slot_sessions_and_supervisor_use_pinned_routes(store, monkeypatch):
    from mathlottery.config import AgentSlot, BackendConfig, ChatConfig, SolveConfig

    scripted = CampaignBackend(agents=2)
    routes = []

    class Routed:
        def __init__(self, settings):
            self.settings = settings

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            routes.append((workspace.name, self.settings.mode, self.settings.model,
                           self.settings.codex_identity, kwargs.get("session_id")))
            return scripted.invoke_native(prompt, directory, workspace, timeout, **kwargs)

    monkeypatch.setattr("mathlottery.solve.attempts.research_backend", lambda settings, root: Routed(settings))
    config = Config(solve=SolveConfig(parallel_agents=2, agent_slots=[
        AgentSlot(id="primary-route", backend=BackendConfig(model="codex-model")),
        AgentSlot(id="api-route", backend=BackendConfig(mode="chat", model="api-model",
                  chat=ChatConfig(api_key_env="TEST_UNSET_API_ROUTE_KEY"))),
    ]))
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, Problem(id="mixed", title="Mixed", statement=theorem()["statement"]), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED, run.last_error
    assert all(mode == "codex" and identity == "primary-route" for name, mode, _, identity, _ in routes
               if name in {"supervisor", "workspace"})
    assert any(name == "slot-api-route" and mode == "chat" and model == "api-model"
               for name, mode, model, _, _ in routes)
    assert run.native.solve_team.workers["slot-api-route"].response_id == "session-slot-api-route"
    assert run.native.solve_team.supervisor_session_id == "session-supervisor"


def test_completed_search_evidence_uses_its_actual_receipt(store):
    class Searching(CampaignBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            result = super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            if workspace.name == "workspace":
                result.runtime = {"source_urls": ["https://example.org/theorem"], "search_queries": ["addition definition"]}
            return result
    engine, created = setup(store, Searching())
    run = engine.drive(created.id)
    research = next(h for h in run.native.history if h["role"] == "research")
    assert run.observations and all(o["artifact"] == research["events"] for o in run.observations)


def test_full_budget_option_continues_after_supervisor_acceptance(store, monkeypatch):
    from mathlottery.runtime import budget

    expired = threading.Event()
    original = budget.remaining
    monkeypatch.setattr(budget, "remaining", lambda run, config: 0 if expired.is_set() else original(run, config))

    def research(backend, author, workspace, kwargs, turn):
        if turn == 2:
            expired.set()

    backend = CampaignBackend(research=research)
    engine, created = setup(store, backend)
    created.config["budget"]["solve_until_budget_exhausted"] = True
    store.save(created, "test_full_budget")
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert backend.research_turns == 2 and len(backend.calls) == 5
    assert run.native.solve_team.campaign.accepted_candidate_id == run.candidates[-1].id


def test_supervisor_cannot_silently_skip_queued_theorems(store):
    def research(backend, author, workspace, kwargs, turn):
        atomic_write(workspace / "outbox" / "lemma.json", json_text({
            "id": "lemma", "kind": "result", "title": "Identity", "body": "Proof attached inline", "theorem": theorem(),
        }))

    def omit(backend, payload, context, kwargs):
        payload["board_reviews"] = []

    backend = CampaignBackend(research=research, supervision=omit)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.PAUSED and "queued board theorem" in run.last_error
    assert not run.native.solve_team.campaign.candidate_reviews


def test_quota_failure_preserves_peer_checkpoint_without_account_fallback(store):
    barrier = threading.Barrier(2)

    class Limited(CampaignBackend):
        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            if "global supervision" not in prompt:
                barrier.wait(timeout=5)
                if workspace.name == "workspace":
                    return BackendResult(BackendStatus.RATE_LIMITED, invoked=True,
                                         error="Scripted quota exhausted", usage={"input_tokens": 1, "output_tokens": 1})
                deadline = time.monotonic() + 5
                while not kwargs["cancelled"]() and time.monotonic() < deadline:
                    time.sleep(0.01)
                assert kwargs["cancelled"]()
            return super().invoke_native(prompt, directory, workspace, timeout, **kwargs)

    backend = Limited(agents=2, complete=False)
    engine, created = setup(store, backend, parallel=2)
    run = engine.drive(created.id)
    assert run.state == State.RATE_LIMITED, run.last_error
    assert run.last_error == "Scripted quota exhausted"
    assert len(run.candidates) == 1 and not run.candidates[-1].reviews
    assert len(run.native.history) == run.usage.measured_calls == 3
    assert not run.native.solve_team.active_attempts


def test_pending_responses_retrieved_once_and_research_not_resubmitted(store):
    class Pending(CampaignBackend):
        recoveries = 0

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            result = super().invoke_native(prompt, directory, workspace, timeout, **kwargs)
            if workspace.name == "workspace":
                self.final_result = result
                return replace(result, status=BackendStatus.INTERRUPTED, pending=True, text="",
                               error="Existing remote response pending", usage={})
            return result

        def recover_native(self, directory, timeout, **kwargs):
            self.recoveries += 1
            return self.final_result

    backend = Pending()
    engine, created = setup(store, backend)
    created.mode = "chat"
    created.config["backend"]["mode"] = "chat"
    store.save(created, "test_responses_transport")
    run = engine.drive(created.id)
    assert run.state == State.PAUSED and run.iteration == 1
    assert len(run.native.solve_team.active_attempts) == 1 and not run.candidates
    resumed = engine.resume(run.id)
    assert resumed.state == State.COMPLETED, resumed.last_error
    assert backend.recoveries == backend.research_turns == 1
    assert resumed.usage.measured_calls == len(backend.calls) == 3
    assert not resumed.native.solve_team.active_attempts and len(resumed.candidates) == 1
