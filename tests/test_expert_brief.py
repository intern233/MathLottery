"""Expert guides expose frozen evidence, including failed and absent checks."""

import hashlib
import io
import json
import zipfile

import pytest
from bs4 import BeautifulSoup
from test_organization import pdf as pdf
from test_organization import reviewed as reviewed

from mathlottery.models import (
    LiteratureObstacle,
    ProofCheck,
    ProofCoverage,
    ProofStep,
    Review,
    StatementAlignment,
    digest,
)
from mathlottery.organize import workflow as organization
from mathlottery.organize.brief import MARKER, material_link, metadata, render, safe_link
from mathlottery.organize.downloads import read_report, summary
from mathlottery.organize.pdf import _render_html
from mathlottery.storage.core import json_text


def test_brief_distinguishes_original_claim_failed_checks_and_legacy_missing_coverage(store, reviewed):
    config, engine, source = reviewed
    source.problem.statement = "For every real x, x squared is nonnegative."
    source.candidates[0].claim = "For positive integers x, x squared is positive."
    # Candidate content changes must use an immutable new candidate, not a rewritten hash.
    candidate = source.candidates.pop()
    from mathlottery.models import CandidateInput

    fresh = engine._candidate(source, CandidateInput(claim=candidate.claim, proof=candidate.proof))
    fresh.reviews = candidate.reviews
    fresh.reviews[0].checks = [ProofCheck(id="edge", claim="x=0", method="DERIVATION", result="CONTRADICTED",
                                         reasoning="Zero is excluded by the candidate.", blocking=True)]
    fresh.reviews[0].formal_receipt = {"status": "REJECTED", "reason": "Unapproved axiom"}
    store.save(source, "expert_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        assert source.problem.statement in brief and fresh.claim in brief
        assert "CONTRADICTED" in brief and "Zero is excluded" in brief
        assert "REJECTED" in brief and "Unapproved axiom" in brief
        assert "INCONCLUSIVE" in brief and "PARTIAL" in brief and "UNKNOWN" in brief
        assert fresh.sha256 in brief and run.organization_context.source_sha256 in brief
        assert "UNASSESSED" in brief
        assert "NO_ISSUES_FOUND" not in brief


def test_bilingual_brief_has_same_evidence_priorities_and_keeps_earlier_failures(store, reviewed):
    config, engine, source = reviewed
    first = source.candidates[0].reviews[0]
    first.checks = [ProofCheck(id="old", claim="Old attempted lemma", method="DERIVATION", result="UNRESOLVED",
                               reasoning="Old unresolved derivation")]
    first.formal_receipt = {"status": "TIMEOUT", "reason": "Earlier replay timed out"}
    last = Review(verdict="NO_ISSUES_FOUND", truth_assessment="Supported under hypothesis", proof_assessment="Argument checked",
                  original_problem_coverage="FULL", novelty="POTENTIALLY_NEW",
                  proof_steps=[ProofStep(id="lemma", statement="Boundary lemma", check_ids=["boundary"])],
                  checks=[ProofCheck(id="boundary", claim="Boundary lemma", method="DERIVATION", result="SUPPORTED", reasoning="Direct substitution")],
                  statement_alignment=[StatementAlignment(facet="BOUNDARY_CASES", original="All x", candidate="All x", assessment="MATCHED", reasoning="Includes zero")],
                  proof_coverage=ProofCoverage(policy_version="proof-test", proof_complete=True, statement_aligned=True),
                  formal_receipt={"status": "KERNEL_REPLAYED", "declarations": [{"name": "lemma", "axioms": []}]})
    last.literature_search.obstacles = [LiteratureObstacle(id="paper", kind="INACCESSIBLE_SOURCE", description="Missing appendix",
                                                          impact="Could contain this result", next_action="Obtain the author's public manuscript")]
    source.candidates[0].reviews.append(last)
    store.save(source, "expert_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        for value in ("Old unresolved derivation", "Earlier replay timed out", "Boundary lemma", "BOUNDARY_CASES", "Missing appendix", "Obtain the author's public manuscript", "KERNEL_REPLAYED"):
            assert value in brief
        assert "formal_alignment_certified=True" not in brief
    assert "未经外部认证" in render(run, "zh")
    assert "no external certification" in render(run, "en")


def test_generated_prefix_is_idempotent_and_exports_bind_it_without_model_call(store, reviewed, pdf):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    original = json_text(source)
    organization.accept(run, {"zh": "# 正文\n\n证明待检查。", "en": "# Exposition\n\nProof needs checking."})
    texts = {lang: doc.markdown for lang, doc in organization.report_documents(run).items()}
    organization.accept(run, texts)
    assert texts == {lang: doc.markdown for lang, doc in organization.report_documents(run).items()}
    assert all(value.count(MARKER) == 1 for value in texts.values())
    organization.export(store, run)
    before = {lang: doc.markdown_sha256 for lang, doc in organization.report_documents(run).items()}
    organization.export(store, run)
    assert before == {lang: doc.markdown_sha256 for lang, doc in organization.report_documents(run).items()}
    assert json_text(store.load(source.id)) == original
    assert all(item["expert_brief_available"] for item in summary(store, run)["reports"].values())
    with zipfile.ZipFile(io.BytesIO(read_report(store, run.id, "bundle"))) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        for language in ("zh", "en"):
            assert manifest["reports"][language]["expert_brief"]["sha256"] == digest(render(run, language))
            assert archive.read(f"report.{language}.md").decode() == texts[language]
    assert all(MARKER in markdown for markdown in pdf)


def test_brief_uses_frozen_values_when_live_source_changes(store, reviewed):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    before = render(run, "en")
    source.problem.statement = "PRIVATE_LATER_PROBLEM"
    source.candidates[0].reviews[0].issues = ["PRIVATE_LATER_ISSUE"]
    store.save(source, "later_live_change")
    assert render(run, "en") == before
    assert "PRIVATE_LATER" not in render(run, "en")


def test_old_report_is_not_silently_rewritten_to_contain_a_new_brief(store, reviewed, pdf):
    from mathlottery.models import OrganizationReport

    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    run.organization_context.report_languages = None
    run.organization_report = OrganizationReport(markdown="# Legacy report\n", markdown_sha256=digest("# Legacy report\n"), created_at="2026-01-01")
    organization.export(store, run)
    assert run.organization_report.markdown == "# Legacy report\n"
    assert metadata(run, run.organization_report, "zh") is None
    assert not summary(store, run)["expert_brief_available"]
    assert organization.export_manifest(run)["report"]["expert_brief"] is None


def test_navigation_restricts_links_to_captured_files_and_safe_web_urls(store, reviewed):
    config, engine, source = reviewed
    source.problem.statement = '<script>alert(1)</script> [go](javascript:alert(1)) ![image](https://invalid.example/x)'
    source.problem.source_url = "javascript:alert(1)"
    store.save(source, "untrusted_text")
    run = engine.organize(config, source.id)
    context = run.organization_context
    assert "materials/" in material_link(context, "dossier.json")
    assert "](materials/" not in material_link(context, "../../auth.json")
    assert "](materials/" not in material_link(context, "workspace/not-captured.md")
    for unsafe in ("javascript:alert(1)", "data:text/html,x", "file:///etc/passwd", "https://name:password@example.org/p", "https://example.org/\nerror"):
        assert "](" not in safe_link("label", unsafe)
    link = safe_link("label", "https://example.org/paper_(1)?x=a b")
    assert "paper_%281%29" in link and "a%20b" in link
    document, _, _ = _render_html(render(run, "en"), "Report")
    soup = BeautifulSoup(document, "html.parser")
    assert not soup.select("script, img, iframe, object")
    assert "mathlottery-expert-brief-v1" not in soup.get_text()
    assert all(not a.get("href", "").startswith("javascript:") for a in soup.select("a"))


def test_formal_receipt_is_frozen_and_its_link_resolves(store, reviewed):
    config, engine, source = reviewed
    path = "verification/formal/example/receipt.json"
    root = store.run_dir(source.id)
    (root / path).parent.mkdir(parents=True)
    (root / path).write_text('{"status":"REJECTED"}')
    source.candidates[0].reviews[0].formal_receipt = {"status": "REJECTED", "artifact": path}
    store.save(source, "receipt_fixture")
    run = engine.organize(config, source.id)
    assert any(item.path == f"{source.id}/{path}" for item in run.organization_context.files)
    assert f"](materials/{source.id}/{path})" in render(run, "en")


def _remove_new_defaults(candidate):
    for review in candidate["reviews"]:
        for key in ("proof_steps", "statement_alignment", "proof_coverage"):
            review.pop(key, None)
        for check in review["checks"]:
            check.pop("id", None)
            check.pop("formal_declarations", None)
        for field in ("literature_search", "evidence_assessment"):
            for key in ("obstacles", "comparisons", "unresolved_obstacle_ids"):
                review[field].pop(key, None)


def test_historical_snapshot_accepts_new_empty_defaults_but_rejects_new_evidence(store, reviewed):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    context = run.organization_context
    item = next(f for f in context.files if f.path == f"{source.id}/dossier.json")
    path = store.run_dir(run.id) / "organization-context" / item.path
    dossier = json.loads(path.read_text())
    for candidate in dossier["candidates"]:
        _remove_new_defaults(candidate)
    data = json_text(dossier).encode()
    path.write_bytes(data)
    item.size, item.sha256 = len(data), hashlib.sha256(data).hexdigest()
    context.candidate_hashes = [{"id": c["id"], "sha256": c["sha256"], "snapshot_sha256": digest(json_text(c))}
                                for c in dossier["candidates"]]
    assert list(organization._read_files(store, run))
    run.candidates[0].reviews[0].proof_steps = [ProofStep(id="new", statement="Newly invented evidence")]
    with pytest.raises(ValueError, match="candidate/review snapshot was modified"):
        list(organization._read_files(store, run))


def test_quoted_source_formulas_render_literally_without_changing_latex():
    from mathlottery.organize.brief import text

    statement = r"For $\forall x \in \mathbb{R}$, $x^2 \ge 0$."
    document, _, _ = _render_html(text(statement), "Literal source")
    assert statement in BeautifulSoup(document, "html.parser").get_text()


def test_brief_does_not_turn_reported_obstacle_resolutions_into_supported_evidence(store, reviewed):
    config, engine, source = reviewed
    assessment = source.candidates[0].reviews[0].evidence_assessment
    assessment.policy_version = "evidence-test"
    assessment.obstacles = [{"id": "missing-paper", "status": "RESOLVED", "description": "Need full appendix",
                             "impact": "Possible prior solution", "next_action": "Retrieve the appendix",
                             "resolution": "Agent reports finding it", "resolution_supported": False,
                             "resolution_reason": "No checked source quotation"}]
    assessment.comparisons = [{"id": "prior", "relation": "DIFFERENT", "supported": False,
                               "source_url": "https://example.org/prior", "prior_conclusion": "Earlier theorem"}]
    store.save(source, "unsupported_resolution")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        assert "RESOLVED" in brief and "=False" in brief
        assert "No checked source quotation" in brief and "Retrieve the appendix" in brief
        assert "Earlier theorem" in brief and "DIFFERENT" in brief
    assert "Comparison evidence supported=False" in render(run, "en")


def test_many_repeated_reviews_produce_a_compact_index_without_losing_failure_evidence(store, reviewed):
    config, engine, source = reviewed
    candidate = source.candidates[0]
    template = candidate.reviews[0].model_copy(deep=True)
    template.evidence_assessment.policy_version = "evidence-test"
    template.evidence_assessment.obstacles = [
        {"id": f"BLOCKER-{i}", "kind": "INACCESSIBLE_SOURCE", "source_url": f"https://example.org/paper-{i}",
         "status": "RESOLVED", "resolution_supported": False,
         "description": "Inaccessible full theorem. " * 100,
         "impact": "May already solve the exact claim. " * 100,
         "next_action": "Obtain and check the original theorem. " * 100,
         "resolution_reason": "No checked source quotation"}
        for i in range(3)
    ]
    template.literature_search.unresolved = ["Unique public-source gap. " * 100]
    template.evidence_assessment.reasons = ["Unresolved literature gap: " + template.literature_search.unresolved[0]]
    template.checks = [ProofCheck(id="old-failure", claim="Earlier lemma", result="CONTRADICTED",
                                 method="DERIVATION", reasoning="Original counterexample remains on record", blocking=True)]
    template.formal_receipt = {"status": "TIMEOUT", "reason": "Earlier kernel attempt timed out"}
    candidate.reviews = [template.model_copy(deep=True) for _ in range(40)]
    candidate.reviews[-1].checks[0].result = "SUPPORTED"
    candidate.reviews[-1].formal_receipt = {"status": "KERNEL_REPLAYED"}
    store.save(source, "large_repeated_review_fixture")
    run = engine.organize(config, source.id)
    before = json_text(run)
    for language in ("zh", "en"):
        brief = render(run, language)
        # The old renderer repeated hundreds of thousands of characters here.
        assert len(brief) < 16000
        for identifier in ("BLOCKER-0", "BLOCKER-1", "BLOCKER-2"):
            assert 2 <= brief.count(identifier) <= 3  # overview, action row, historical row
        for value in ("RESOLVED", "supported=False", "No checked source quotation", "CONTRADICTED",
                      "blocking=True", "old-failure", "Original counterexample remains on record",
                      "TIMEOUT", "Earlier kernel attempt timed out", "KERNEL_REPLAYED", "n=40"):
            assert value in brief
        assert brief.count("Unique public-source gap.") < 10
        assert "…" in brief and "/candidates/0/reviews/39/evidence" in brief
        assert "[frozen-dossier]: materials/" in brief
    assert "not a complete proof" in render(run, "en")
    assert "不是完整证明" in render(run, "zh")
    assert json_text(run) == before


def test_same_id_different_sources_and_late_severe_records_remain_visible(store, reviewed):
    config, engine, source = reviewed
    review = source.candidates[0].reviews[0]
    source.problem.literature_search.obstacles = [LiteratureObstacle(
        id="same-id", kind="INACCESSIBLE_SOURCE", source_url="https://example.org/first",
        description="First source still missing", impact="Possible complete prior theorem", next_action="Get the first source")]
    review.literature_search.obstacles = [LiteratureObstacle(
        id="same-id", kind="INACCESSIBLE_SOURCE", source_url="https://example.org/second",
        description="Different source also missing", impact="Different missing proof", next_action="Get the second source")]
    review.checks = [ProofCheck(id=f"check-{i}", claim=f"Lemma {i}", result="SUPPORTED", method="DERIVATION", reasoning="Checked")
                     for i in range(80)] + [ProofCheck(id="late-blocker", claim="Missing final case", result="UNRESOLVED",
                                                     method="DERIVATION", reasoning="This case remains essential", blocking=True)]
    review.checks += [ProofCheck(claim="First unnamed failure", result="CONTRADICTED", method="DERIVATION", reasoning="Counterexample"),
                      ProofCheck(claim="Second unnamed failure", result="UNRESOLVED", method="DERIVATION", reasoning="Needs proof")]
    review.evidence_assessment.policy_version = "evidence-test"
    review.evidence_assessment.obstacles = [item.model_dump() for item in review.literature_search.obstacles]
    review.evidence_assessment.comparisons = [
        {"id": f"comparison-{i}", "source_url": f"https://example.org/{i}", "relation": "DIFFERENT", "supported": True}
        for i in range(6)
    ] + [{"id": "possible-prior-solution", "source_url": "https://example.org/prior", "relation": "EQUIVALENT",
          "supported": False, "prior_conclusion": "Potentially the entire theorem"}]
    store.save(source, "late_and_collision_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        for value in ("First source still missing", "Different source also missing", "Get the first source", "Get the second source",
                      "late-blocker", "blocking=True", "First unnamed failure", "Second unnamed failure",
                      "possible-prior-solution", "EQUIVALENT", "Potentially the entire theorem"):
            assert value in brief
        assert "/problem/literature" in brief and "/candidates/0/reviews/0/evidence" in brief


def test_legacy_prefix_is_authenticated_and_only_explicit_acceptance_refreshes_it(store, reviewed, pdf):
    from mathlottery.organize.brief import LEGACY_MARKER, _render_v1

    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    organization.accept(run, {"zh": "# 中文正文\n完整论证。", "en": "# English body\nComplete argument."})
    for language, document in organization.report_documents(run).items():
        body = document.markdown[len(render(run, language)):]
        document.markdown = _render_v1(run, language) + body
        document.markdown_sha256 = digest(document.markdown)
    before = {lang: (doc.markdown, doc.markdown_sha256) for lang, doc in organization.report_documents(run).items()}
    organization.export(store, run)
    for language, document in organization.report_documents(run).items():
        assert (document.markdown, document.markdown_sha256) == before[language]
        assert metadata(run, document, language)["version"] == "expert-brief-v1"
        altered = document.model_copy(deep=True)
        altered.markdown = altered.markdown.replace("SHA-256", "ALTERED-SHA", 1)
        assert metadata(run, altered, language) is None
        rejected = organization.build_document(run, altered.markdown, language)
        # A marker or a nearly matching prefix cannot delete arbitrary supplied text.
        assert altered.markdown.strip() in rejected.markdown
    organization.accept(run, {lang: item[0] for lang, item in before.items()})
    for language, document in organization.report_documents(run).items():
        assert document.markdown.count(MARKER) == 1 and LEGACY_MARKER not in document.markdown
        assert metadata(run, document, language)["version"] == "expert-brief-v2"
        assert ("完整论证。" if language == "zh" else "Complete argument.") in document.markdown


def test_reused_id_cannot_resolve_a_different_obstacle_or_another_candidates_gap(store, reviewed):
    config, engine, source = reviewed
    first = source.candidates[0]
    review = first.reviews[0]
    review.evidence_assessment.policy_version = "evidence-test"
    open_obstacle = {"id": "reused", "kind": "INACCESSIBLE_SOURCE", "source_url": "https://example.org/paper",
                     "description": "Appendix A missing", "impact": "Essential prior theorem unavailable",
                     "next_action": "Retrieve Appendix A", "status": "OPEN", "resolution_supported": False}
    review.evidence_assessment.obstacles = [open_obstacle, {
        **open_obstacle, "description": "Different Appendix B checked", "status": "RESOLVED", "resolution_supported": True}]
    review.evidence_assessment.comparisons = [
        {"id": "same-paper", "source_url": "https://example.org/paper", "locator": "Theorem 1",
         "relation": "EQUIVALENT", "supported": False, "prior_conclusion": "First possible complete solution"},
        {"id": "same-paper", "source_url": "https://example.org/paper", "locator": "Theorem 2",
         "relation": "DIFFERENT", "supported": True, "prior_conclusion": "Different limited theorem"}]
    from mathlottery.models import CandidateInput

    other = engine._candidate(source, CandidateInput(claim="Another candidate claim", proof=first.proof))
    other.reviews = [item.model_copy(deep=True) for item in first.reviews]
    other.reviews[0].evidence_assessment.obstacles = [{**open_obstacle, "status": "RESOLVED", "resolution_supported": True}]
    store.save(source, "identity_collision_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        quick = brief.split("## 证据索引" if language == "zh" else "## Evidence index")[0]
        assert "Retrieve Appendix A" in quick and "supported=False" in quick
        for value in ("Appendix A missing", "Different Appendix B checked", "First possible complete solution",
                      "Different limited theorem", "EQUIVALENT", "DIFFERENT", "/candidates/0", "/candidates/1"):
            assert value in brief


def test_compact_rows_do_not_trust_malformed_support_values_or_activate_their_links(store, reviewed):
    config, engine, source = reviewed
    assessment = source.candidates[0].reviews[0].evidence_assessment
    assessment.policy_version = "evidence-test"
    assessment.obstacles = [{"id": "malformed", "status": "RESOLVED",
                             "resolution_supported": "[injected](https://untrusted.example/)",
                             "description": "Untrusted support value", "impact": "Still uncertain",
                             "next_action": "Check the actual receipt"}]
    store.save(source, "malformed_evidence_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        brief = render(run, language)
        quick = brief.split("## 证据索引" if language == "zh" else "## Evidence index")[0]
        assert "Check the actual receipt" in quick
        document, _, _ = _render_html(brief, "Untrusted compact fields")
        soup = BeautifulSoup(document, "html.parser")
        assert not any("untrusted.example" in a.get("href", "") for a in soup.select("a"))


def test_v2_literal_intervals_do_not_open_pdf_math_or_activate_source_links(store, reviewed):
    from urllib.parse import unquote

    from mathlottery.models import OrganizationDocument
    from mathlottery.organize.brief import _render_v1, text

    config, engine, source = reviewed
    literal = (r"x ∈ [0,∞), y ∈ [0,1]. Literal \[x\] and \\[y\\]. "
               r"[open](https://untrusted.example/link) ![image](https://untrusted.example/image)")
    source.problem.statement = literal
    source.problem.source_url = "https://example.org/source"
    store.save(source, "literal_interval_fixture")
    run = engine.organize(config, source.id)
    for language in ("zh", "en"):
        legacy = _render_v1(run, language)
        assert text(literal) in legacy and r"\[0,∞)" in legacy
        old = OrganizationDocument(markdown=legacy + "Body", markdown_sha256=digest(legacy + "Body"), created_at="2026-01-01")
        assert metadata(run, old, language)["version"] == "expert-brief-v1"
        brief = render(run, language)
        document, warnings, formulas = _render_html(brief, "Literal interval guide")
        soup = BeautifulSoup(document, "html.parser")
        assert literal in soup.get_text()
        assert not any("unclosed" in warning.lower() for warning in warnings)
        assert formulas == 0
        assert not soup.select("img, script, iframe")
        links = [a.get("href", "") for a in soup.select("a")]
        assert "https://example.org/source" in links
        assert not any("untrusted.example" in href for href in links)
        assert ("#完整整理报告" if language == "zh" else "#full-editorial-report") in [unquote(href) for href in links]
