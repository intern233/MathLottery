"""Evidence continuity across workflow boundaries, without reviewer anchoring."""

import threading
import time

from mathlottery.config import Config
from mathlottery.models import CandidateInput, LiteratureSearch, NativeCheckpoint, Review, Workflow
from mathlottery.providers.demo import demo_problem
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.runtime.prompts import build_native_prompt
from mathlottery.runtime.resources import Coordinator
from mathlottery.runtime.workflows import record_selection
from mathlottery.verify.candidates import CandidateStore
from mathlottery.web.service import StartRequest, WebService


def gap():
    return LiteratureSearch(obstacles=[{
        "id": "prior-proof", "kind": "INACCESSIBLE_SOURCE",
        "source_url": "https://example.org/prior-proof", "description": "Relevant appendix unavailable",
        "impact": "May already prove this statement", "next_action": "Locate an accessible primary version",
    }])


def test_find_cannot_forget_gap_by_temporarily_dropping_a_problem(store):
    config = Config()
    run = Orchestrator(store).create(config, workflow=Workflow.FIND)
    problem = demo_problem()
    problem.literature_search = gap()

    def select(value):
        checkpoint = NativeCheckpoint(run_id=run.id, task_id="task-fixture", kind="selection",
                                      summary="Selection", problem=value, shortlist=[value])
        record_selection(store, run, checkpoint, prepared=True)

    select(problem)
    select(demo_problem("hidden-assumption"))
    select(demo_problem())
    assert run.problem.literature_search.obstacles[0].id == "prior-proof"
    assert "prior-proof" in run.problem.evidence_assessment.unresolved_obstacle_ids


def test_new_web_verify_carries_literature_but_not_old_verdict(tmp_path, monkeypatch):
    service = WebService(tmp_path)
    config = Config()
    source = Orchestrator(service.store).create(
        config, problem=demo_problem(), workflow=Workflow.VERIFY,
        candidate=CandidateInput(claim=demo_problem().statement, proof="Induction argument"),
    )
    source.candidates[-1].reviews.append(Review(
        verdict="INCONCLUSIVE", truth_assessment="PRIVATE_PRIOR_REVIEW_OPINION",
        proof_assessment="PRIVATE_PRIOR_PROOF_OPINION", literature_search=gap(),
    ))
    service.store.save(source, "review_fixture")
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: None)
    result = service.start(StartRequest(workflow="verify", from_run=source.id))
    run = service.store.load(result["id"])
    assert not run.candidates[-1].reviews
    assert run.review_literature[0].obstacles[0].id == "prior-proof"
    prompt = build_native_prompt(run, 60)
    assert "Relevant appendix unavailable" in prompt
    assert "PRIVATE_PRIOR_REVIEW_OPINION" not in prompt
    assert "PRIVATE_PRIOR_PROOF_OPINION" not in prompt
    # Omitting the obstacle in the next model review cannot clear it.
    CandidateStore(service.store).review(run, Review(
        verdict="INCONCLUSIVE", truth_assessment="Needs checking", proof_assessment="Missing evidence",
    ), prepared=True)
    assessment = run.candidates[-1].reviews[-1].evidence_assessment
    assert "prior-proof" in assessment.unresolved_obstacle_ids


def test_orchestrator_admission_waits_without_active_budget_or_backend_call(store, monkeypatch):
    config = Config(resources={"min_available_memory_mb": 0, "sample_interval_seconds": 0.1})
    engine = Orchestrator(store)
    first = engine.create(config, workflow=Workflow.FIND)
    second = engine.create(config, workflow=Workflow.FIND)
    invoked = []
    monkeypatch.setattr(engine, "_drive", lambda run: invoked.append(run.id) or run)
    coordinator = Coordinator(store)
    results = []
    with coordinator.admission(first, config):
        worker = threading.Thread(target=lambda: results.append(engine.drive(second.id)))
        worker.start()
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not coordinator.snapshot(second.id):
                time.sleep(0.02)
            assert coordinator.snapshot(second.id)["state"] == "queued"
            waiting = store.load(second.id)
            assert waiting.active_since is None and waiting.elapsed_seconds == 0
            assert not invoked
            engine.stop(second.id)
            worker.join(timeout=5)
            assert not worker.is_alive()
            assert not invoked
            assert results[0].elapsed_seconds == 0
            assert coordinator.snapshot(second.id)["state"] == "cancelled"
        finally:
            (store.run_dir(second.id) / "stop.requested").touch()
            worker.join(timeout=5)
