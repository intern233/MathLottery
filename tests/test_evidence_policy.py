"""Negative controls: URLs, agreeable reviews and compiler claims are insufficient."""

import json

import pytest

from mathlottery.auditor import audit
from mathlottery.config import Config
from mathlottery.evidence_policy import assess_problem, normalized
from mathlottery.literature import collect_sources, snapshot
from mathlottery.models import (
    Candidate,
    CandidateInput,
    Citation,
    LiteratureSearch,
    Problem,
    ProofCheck,
    Review,
    digest,
    now,
)
from mathlottery.orchestrator import Orchestrator
from mathlottery.sources import WebTools


def citations():
    return [
        Citation(url="https://example.org/problem", role="ORIGINAL_STATEMENT",
                 locator="Question 1", excerpt="For every n, P(n)?", explanation="Exact original statement."),
        Citation(url="https://example.org/problem", role="EXPLICIT_OPEN",
                 locator="Status", excerpt="Question 1 remains open.", explanation="Maintained status label."),
    ]


def records(cites=None):
    cites = cites or citations()
    return [{
        "record_kind": "source_snapshot", "status": "OK", "requested_url": c.url,
        "url": c.url, "retrieved_at": now(), "artifact": "literature/source.txt", "sha256": "a" * 64,
        "excerpt_hashes": [digest(normalized(x.excerpt)) for x in cites if x.url == c.url],
    } for c in cites] + [{"status": "OK", "query": "P(n) solution erratum equivalent theorem", "retrieved_at": now()}]


def problem():
    return Problem(id="test", title="Question", statement="For every n, P(n)?", status="OPEN",
                   source_url="https://example.org/problem", citations=citations(),
                   literature_search=LiteratureSearch(
                       queries=["P(n) solution erratum equivalent theorem"],
                       conclusion="Compared original question and later search results; limited assessment.",
                   ))


def candidate(**kwargs):
    return Candidate(id="candidate-test", sha256=digest("Claim\nProof"), claim="Claim", proof="Proof",
                     source_iteration=0, **kwargs)


def review(**kwargs):
    return Review.model_validate({
        "verdict": "NO_ISSUES_FOUND", "truth_assessment": "The precise claim holds.",
        "proof_assessment": "Base case and induction step checked.",
        "checks": [{"claim": "Induction covers n≥0", "method": "DERIVATION", "result": "SUPPORTED",
                    "reasoning": "At n=0 the sum is 0; S(n+1)=n²+2n+1=(n+1)²."}],
        **kwargs,
    })


def test_one_checked_primary_source_can_support_a_limited_open_assessment():
    checked = assess_problem(problem(), records())
    assert checked.status == "OPEN"
    assert checked.evidence_assessment.supported
    assert len(checked.status_evidence) == 1  # Counting domains is not the policy.


def test_general_search_limits_remain_visible_without_claiming_exhaustiveness():
    from mathlottery.reporting import source_assessment

    p = problem()
    p.literature_search.limitations = ["English-language indexed sources checked; unindexed work may exist."]
    checked = assess_problem(p, records())
    assert checked.status == "OPEN"
    assert checked.evidence_assessment.supported
    assert checked.evidence_assessment.limitations == p.literature_search.limitations
    assert p.literature_search.limitations[0] in source_assessment(checked.evidence_assessment)


@pytest.mark.parametrize("missing", ["quote", "search", "specific_gap"])
def test_declaring_search_limits_never_overrides_missing_evidence(missing):
    p, observed = problem(), records()
    p.literature_search.limitations = ["Search is not exhaustive."]
    if missing == "quote":
        p.citations[1].excerpt = "The model's paraphrase, absent from the source"
    elif missing == "search":
        observed = observed[:-1]
    else:
        p.literature_search.unresolved = ["A possible later solution has not been read."]
    checked = assess_problem(p, observed)
    assert checked.status == "UNKNOWN"
    assert checked.evidence_assessment.reasons
    assert checked.evidence_assessment.limitations == ["Search is not exhaustive."]


def test_uncompared_prior_result_blocks_open_even_without_a_declared_gap():
    p = problem()
    p.literature_search.limitations = ["Some equivalent terminology may be missing."]
    p.citations.append(Citation(
        url="https://example.org/related", role="PRIOR_RESULT", locator="Theorem 3",
        excerpt="A related theorem.", explanation="Its implication for this question is unclear.",
        relation="UNKNOWN",
    ))
    checked = assess_problem(p, records(p.citations))
    assert checked.status == "UNKNOWN"
    assert any("unresolved relationship" in reason for reason in checked.evidence_assessment.reasons)


def test_old_unresolved_gaps_are_not_reclassified_as_general_limits():
    p = problem()
    p.literature_search = LiteratureSearch.model_validate({
        "queries": p.literature_search.queries, "conclusion": "Previous limited search.",
        "unresolved": ["Unindexed work may exist."],
    })
    checked = assess_problem(p, records())
    assert checked.status == "UNKNOWN"
    assert not checked.evidence_assessment.limitations
    assert checked.evidence_assessment.reasons == ["Unresolved literature gap: Unindexed work may exist."]


def test_primary_source_redirect_and_fragment_do_not_erase_verified_evidence():
    p = problem()
    p.source_url = "https://example.org/current#question-1"
    observed = records()
    for item in observed[:-1]:
        item["url"] = "https://example.org/current"
    assert assess_problem(p, observed).status == "OPEN"
    p.source_url = "https://example.org/current?v=2"
    assert assess_problem(p, observed).status == "UNKNOWN"  # A different version was not retrieved.


@pytest.mark.parametrize("change", ["metadata", "quote", "old", "future", "no_search", "gap"])
def test_open_status_requires_current_traceable_content_and_search(change):
    p, observed = problem(), records()
    if change == "metadata":
        for r in observed:
            r.pop("record_kind", None)
    elif change == "quote":
        p.citations[1].excerpt = "Fabricated open status"
    elif change in {"old", "future"}:
        for r in observed:
            r["retrieved_at"] = "2000-01-01T00:00:00+00:00" if change == "old" else "2999-01-01T00:00:00+00:00"
    elif change == "no_search":
        observed = observed[:-1]
    else:
        p.literature_search.unresolved = ["Potential solution full text unavailable"]
    checked = assess_problem(p, observed)
    assert checked.status == "UNKNOWN"
    assert checked.evidence_assessment.reasons


def test_checked_later_solution_conflicts_with_open_label():
    p = problem()
    p.citations.append(Citation(url="https://example.org/solution", role="SOLUTION", locator="Theorem 1",
                                excerpt="P(n) holds for all n.", explanation="Same quantifiers and hypotheses.",
                                relation="EQUIVALENT"))
    checked = assess_problem(p, records(p.citations))
    assert checked.status == "DISPUTED"
    assert not checked.evidence_assessment.supported


def test_equivalent_prior_theorem_cannot_be_hidden_by_a_different_source_role():
    p = problem()
    p.citations.append(Citation(url="https://example.org/prior", role="PRIOR_RESULT", locator="Theorem 1",
                                excerpt="The general theorem implies P(n).", explanation="Restrict the general result.",
                                relation="SPECIAL_CASE"))
    assert assess_problem(p, records(p.citations)).status == "DISPUTED"


def test_checked_solution_to_a_different_problem_does_not_block_open_assessment():
    p = problem()
    p.citations.append(Citation(url="https://example.org/other", role="SOLUTION", locator="Theorem 2",
                                excerpt="An answer under an extra assumption.", explanation="The extra hypothesis excludes this question.",
                                relation="DIFFERENT"))
    assert assess_problem(p, records(p.citations)).status == "OPEN"


def test_source_receipt_is_generated_from_actual_text(tmp_path, monkeypatch):
    config = Config()
    web = WebTools(tmp_path, config.tools)
    monkeypatch.setattr(web, "download", lambda *a, **k: (
        b"<main>Question 1 remains open.</main>", "https://example.org/redirected", "text/html"))
    record = snapshot(web, "https://example.org/problem", ["Question 1 remains open.", "A fake theorem"], tmp_path)
    assert record["requested_url"] != record["url"]
    assert record["excerpt_hashes"] == [digest("Question 1 remains open.")]
    assert (tmp_path / record["artifact"]).is_file()


def test_disabled_fetch_is_an_explicit_gap_and_never_uses_agent_receipt(store, monkeypatch):
    config = Config()
    config.backend.native_network_access = False
    run = Orchestrator(store).create(config, problem())
    monkeypatch.setattr(WebTools, "download", lambda *a, **kw: pytest.fail("network must be disabled"))
    collect_sources(store, run, citations())
    assert len(run.observations) == 1
    assert run.observations[0]["result"]["status"] == "UNAVAILABLE"
    assert "disabled" in run.observations[0]["result"]["reason"]


def test_forged_positive_review_is_inconclusive():
    result = audit(candidate(), Review(verdict="NO_ISSUES_FOUND", truth_assessment="", proof_assessment=""), [])
    assert result.level == "CANDIDATE"
    assert result.reviews[-1].verdict == "INCONCLUSIVE"
    assert result.reviews[-1].reported_verdict == "NO_ISSUES_FOUND"


@pytest.mark.parametrize("method", ["FINITE_TEST", "REFERENCE", "FORMAL"])
def test_tests_citations_and_self_reported_lean_do_not_prove_a_claim(method):
    proposed = review()
    proposed.checks[0].method = method
    proposed.formal_receipt = {"status": "KERNEL_REPLAYED"}  # Untrusted model input is overwritten.
    result = audit(candidate(), proposed, [])
    assert result.reviews[-1].verdict == "INCONCLUSIVE"
    assert result.reviews[-1].formal_receipt is None


def test_unresolved_critical_step_blocks_approval():
    proposed = review()
    proposed.checks[0].result = "UNRESOLVED"
    assert audit(candidate(), proposed, []).reviews[-1].verdict == "INCONCLUSIVE"


def test_contradiction_overrides_agreeable_verdict():
    proposed = review()
    proposed.checks[0].result = "CONTRADICTED"
    assert audit(candidate(), proposed, []).level == "REJECTED"


def test_correct_partial_result_does_not_become_full_solution():
    result = audit(candidate(scope="PARTIAL", remaining_obligations=["All remaining prime classes"]),
                   review(original_problem_coverage="FULL", coverage_explanation="Claims full coverage"), [])
    accepted = result.reviews[-1]
    assert result.level == "SELF_CHECKED"
    assert accepted.original_problem_coverage == "PARTIAL"
    assert accepted.remaining_obligations == ["All remaining prime classes"]
    assert accepted.validation_notes


def test_review_mathematical_obligation_prevents_full_coverage_of_complete_candidate():
    proposed = review(original_problem_coverage="FULL", coverage_explanation="All parameter ranges compared.",
                      remaining_obligations=["The endpoint x = 0 still needs a proof."])
    accepted = audit(candidate(scope="COMPLETE"), proposed, []).reviews[-1]
    assert accepted.original_problem_coverage == "PARTIAL"
    assert accepted.remaining_obligations == proposed.remaining_obligations
    assert "Full coverage conflicts" in accepted.validation_notes[-1]


@pytest.mark.parametrize("formal_is_essential,expected_coverage", [(False, "FULL"), (True, "UNKNOWN")])
def test_separate_formal_and_literature_limits_do_not_invent_missing_mathematical_cases(
    formal_is_essential, expected_coverage,
):
    proposed = review(
        original_problem_coverage="FULL", coverage_explanation="Both quantifier ranges and endpoints match.",
        remaining_obligations=[], novelty="UNKNOWN",
        novelty_notes="A possible prior solution is unavailable.",
        proof_assessment="The derivation was checked. No external expert certification is recorded.",
        literature_search=LiteratureSearch(unresolved=["A possible prior solution is unavailable."]),
    )
    proposed.checks.append(ProofCheck(
        claim="Independent formal execution", method="FORMAL", result="UNRESOLVED",
        reasoning="The controller compilation receipt is pending.", blocking=formal_is_essential,
    ))
    accepted = audit(candidate(scope="COMPLETE"), proposed, []).reviews[-1]
    assert accepted.original_problem_coverage == expected_coverage
    assert accepted.remaining_obligations == []
    assert accepted.novelty == "UNKNOWN"
    assert accepted.literature_search.unresolved == proposed.literature_search.unresolved
    assert accepted.checks[-1].result == "UNRESOLVED"
    if formal_is_essential:
        assert accepted.verdict == "INCONCLUSIVE"
    else:
        assert accepted.verdict == "NO_ISSUES_FOUND"
    assert "No external expert certification" in accepted.proof_assessment


def test_different_problem_finding_is_not_overwritten_by_solver_partial_label():
    accepted = audit(candidate(scope="PARTIAL"), review(original_problem_coverage="DIFFERENT"), []).reviews[-1]
    assert accepted.original_problem_coverage == "DIFFERENT"


def test_full_coverage_requires_explicit_statement_comparison():
    result = audit(candidate(scope="COMPLETE"), review(original_problem_coverage="FULL"), [])
    assert result.reviews[-1].original_problem_coverage == "UNKNOWN"


def test_one_unrelated_url_does_not_establish_novelty():
    proposed = review(novelty="POTENTIALLY_NEW", novelty_references=[{"url": "https://example.org/unrelated"}])
    result = audit(candidate(), proposed, [{"phase": "VERIFY", "tool": "native_source",
                                           "result": {"status": "OK", "url": "https://example.org/unrelated"}}])
    assert result.reviews[-1].novelty == "UNKNOWN"
    assert result.reviews[-1].evidence_assessment.reasons


def test_checked_equivalent_prior_result_overrides_claimed_novelty():
    prior = Citation(url="https://example.org/prior", role="PRIOR_RESULT", locator="Theorem 1",
                     excerpt="The same theorem.", explanation="All assumptions and conclusions agree.",
                     relation="EQUIVALENT")
    proposed = review(novelty="POTENTIALLY_NEW", citations=[prior])
    result = audit(candidate(), proposed, [{"phase": "VERIFY", "result": r} for r in records([prior])])
    assert result.reviews[-1].novelty == "KNOWN"


def test_matching_published_conjectures_are_not_classified_as_existing_proofs():
    original = [c.model_copy(update={"relation": "EQUIVALENT"}) for c in citations()]
    prior = Citation(url="https://example.org/prior", role="PRIOR_RESULT", locator="Theorem 2",
                     excerpt="Result for even n.", explanation="Only the even case is proved.",
                     relation="DIFFERENT")
    cites = [*original, prior]
    proposed = review(novelty="POTENTIALLY_NEW", citations=cites,
                      literature_search=problem().literature_search)
    observed = [{"phase": "VERIFY", "result": r} for r in records(cites)]
    accepted = audit(candidate(), proposed, observed).reviews[-1]
    assert accepted.novelty == "POTENTIALLY_NEW"
    assert accepted.evidence_assessment.supported
    assert len(accepted.evidence_assessment.checked_citations) == 3


def test_novelty_requires_comparisons_with_checked_prior_results_and_recent_search():
    prior = Citation(url="https://example.org/prior", role="PRIOR_RESULT", locator="Theorem 2",
                     excerpt="Result for even n.", explanation="Candidate also covers odd n, beyond this result.",
                     relation="DIFFERENT")
    proposed = review(novelty="POTENTIALLY_NEW", citations=[prior], literature_search=problem().literature_search)
    observed = records([prior])
    accepted = audit(candidate(), proposed, [{"phase": "VERIFY", "result": r} for r in observed]).reviews[-1]
    assert accepted.novelty == "POTENTIALLY_NEW"
    observed[-1]["retrieved_at"] = "2000-01-01T00:00:00+00:00"
    accepted = audit(candidate(), proposed, [{"phase": "VERIFY", "result": r} for r in observed]).reviews[-1]
    assert accepted.novelty == "UNKNOWN"


def test_source_receipt_recovery_checks_the_archived_bytes(store, monkeypatch):
    run = Orchestrator(store).create(Config(), problem())
    run.task_id = "task-recovery"
    calls = []

    def download(self, url, **kwargs):
        calls.append(url)
        return b"<main>For every n, P(n)? Question 1 remains open.</main>", url, "text/html"

    monkeypatch.setattr(WebTools, "download", download)
    collect_sources(store, run, citations())
    original = run.observations[0]["result"]
    collect_sources(store, run, citations())
    assert len(calls) == 1
    (store.run_dir(run.id) / original["artifact"]).write_text("tampered bytes")
    collect_sources(store, run, citations())
    assert len(calls) == 2


def test_failed_refetch_does_not_leave_a_tampered_snapshot_accepted(store, monkeypatch):
    run = Orchestrator(store).create(Config(), problem())
    run.task_id = "task-corrupt-cache"
    monkeypatch.setattr(WebTools, "download", lambda *a, **kw: (
        b"For every n, P(n)? Question 1 remains open.", "https://example.org/problem", "text/plain"))
    collect_sources(store, run, citations())
    (store.run_dir(run.id) / run.observations[0]["result"]["artifact"]).write_text("tampered")

    def unavailable(*args, **kwargs):
        raise ValueError("Source no longer available")

    monkeypatch.setattr(WebTools, "download", unavailable)
    collect_sources(store, run, citations())
    assessment = assess_problem(problem(), [o["result"] for o in run.observations])
    assert assessment.status == "UNKNOWN"
    assert all(not c["verified_excerpt"] for c in assessment.evidence_assessment.checked_citations)


def test_pdf_extraction_failure_keeps_the_source_hash_and_diagnostic_path(tmp_path, monkeypatch):
    web = WebTools(tmp_path, Config().tools)
    monkeypatch.setattr(web, "download", lambda *a, **kw: (b"%PDF-fixture", "https://example.org/p.pdf", "application/pdf"))
    monkeypatch.setattr("mathlottery.literature.python_exec", lambda *a: {"status": "TIMEOUT", "stdout": ""})
    result = snapshot(web, "https://example.org/p.pdf", ["Theorem"], tmp_path)
    assert result["status"] == "UNAVAILABLE"
    assert result["sha256"] == digest("%PDF-fixture")
    assert (tmp_path / result["artifact"]).is_file()
    assert result["parser_artifact"] and "TIMEOUT" in result["reason"]


def test_old_records_remain_loadable_and_unassessed():
    old = candidate().model_dump(exclude={"scope", "remaining_obligations"})
    old["level"] = "SELF_CHECKED"
    old["reviews"] = [{"verdict": "NO_ISSUES_FOUND", "truth_assessment": "Old", "proof_assessment": "Old"}]
    restored = Candidate.model_validate(old)
    assert restored.level == "SELF_CHECKED"
    assert restored.scope == "UNKNOWN"
    assert restored.reviews[0].evidence_assessment.policy_version is None


def test_scope_is_immutable_and_new_evidence_is_saved_in_projection(store):
    engine = Orchestrator(store)
    run = engine.create(Config(), problem(), candidate=CandidateInput(claim="Claim", proof="Proof", scope="PARTIAL"))
    path = engine.candidates.path(run, run.candidates[-1])
    original = path.read_text()
    checked = engine.candidates.review(run, review())
    assert path.read_text() == original
    assert checked.reviews[-1].original_problem_coverage == "PARTIAL"
    changed = json.loads(original)
    changed["scope"] = "COMPLETE"
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="modified"):
        engine.candidates.check(run)
