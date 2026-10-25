"""Execute outcome wording in Node: solver claims and independent findings stay separate."""

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "src/mathlottery/web/static/outcomes.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute frontend outcome tests")
DRIVER = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const request = JSON.parse(fs.readFileSync(0, 'utf8'));
const before = JSON.stringify(request);
function freeze(value) {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}
freeze(request);
const api = require(process.argv[1]);
const result = api.describe(request.run, request.language, request.context);
const context = {};
context.window = context;
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const browser = context.MathLotteryOutcomes.describe(request.run, request.language, request.context);
if (JSON.stringify(result) !== JSON.stringify(browser)) throw new Error('Browser/Node mismatch');
if (JSON.stringify(request) !== before) throw new Error('Input changed');
process.stdout.write(JSON.stringify(result));
"""
LABELS = {
    "en": {"complete": "Claims a complete solution", "partial": "Claims a partial solution",
           "unsolved": "Reports no solution", "absent": "No answer submitted", "unknown": "Scope not declared",
           "issues": "Issues found", "clean": "No issues found", "unknown_coverage": "Coverage not established",
           "partial_coverage": "Partial original coverage", "unknown_novelty": "Not established",
           "new": "Potentially new", "known": "Known result", "unreviewed": "Not reviewed"},
    "zh": {"complete": "声称完整解决", "partial": "声称部分解决", "unsolved": "自述尚未解决",
           "absent": "尚未提交解答", "unknown": "未明确声明范围", "issues": "发现问题", "clean": "未发现问题",
           "unknown_coverage": "覆盖范围未确认", "partial_coverage": "仅覆盖部分原题",
           "unknown_novelty": "尚未确认", "new": "可能新颖", "known": "已有结果", "unreviewed": "尚未审查"},
}


def describe(run, language, context=None):
    result = subprocess.run([NODE, "-e", DRIVER, str(MODULE)],
                            input=json.dumps({"run": run, "language": language, "context": context or {}}),
                            text=True, capture_output=True, timeout=10, check=True)
    return json.loads(result.stdout)


def record(*, workflow="solve", scope="COMPLETE", verdict="NO_ISSUES_FOUND", coverage="FULL", novelty="UNKNOWN"):
    return {"workflow": workflow, "state": "COMPLETED", "research_outcome": {
        "solve": {"status": scope, "basis": "candidate_scope", "candidate_id": "candidate-one",
                  "claim": "A precise submitted claim", "remaining_obligations": []},
        "verify": {"status": "REVIEWED", "candidate_id": "candidate-one", "verdict": verdict,
                   "original_problem_coverage": coverage, "novelty": novelty, "remaining_obligations": []},
    }}


@pytest.mark.parametrize("language", ["en", "zh"])
def test_solver_complete_claim_remains_a_claim_when_verify_finds_issues(language):
    run = record(verdict="ISSUES_FOUND", coverage="UNKNOWN", novelty="KNOWN")
    result = describe(run, language)
    words = LABELS[language]
    assert result["items"][0]["value"] == result["sections"][0]["value"] == words["complete"]
    assert result["sections"][1]["value"] == words["issues"]
    assert result["sections"][1]["coverage"] == words["unknown_coverage"]
    assert result["sections"][1]["novelty"] == words["known"]
    assert result["sections"][1]["tone"] == "error"
    assert result["sections"][0]["tone"] != "success"


@pytest.mark.parametrize("language", ["en", "zh"])
def test_positive_review_and_potential_novelty_never_upgrade_partial_solver_scope(language):
    run = record(workflow="run", scope="PARTIAL", coverage="PARTIAL", novelty="POTENTIALLY_NEW")
    run["research_outcome"]["solve"]["remaining_obligations"] = ["Prove interval connectivity"]
    result = describe(run, language)
    words = LABELS[language]
    assert result["items"][0]["value"] == words["partial"]
    assert result["sections"][0]["obligations"] == ["Prove interval connectivity"]
    assert result["sections"][1]["value"] == words["clean"]
    assert result["sections"][1]["coverage"] == words["partial_coverage"]
    assert result["sections"][1]["novelty"] == words["new"]
    assert words["complete"] not in [item["value"] for item in result["items"]]


@pytest.mark.parametrize("language", ["en", "zh"])
def test_unsolved_candidate_and_no_candidate_are_distinct(language):
    unsolved = record(scope="UNSOLVED")
    absent = record(scope="NO_CANDIDATE")
    unsolved["research_outcome"]["verify"] = {"status": "UNREVIEWED"}
    absent["research_outcome"]["verify"] = {"status": "NO_CANDIDATE"}
    first, second = describe(unsolved, language), describe(absent, language)
    assert first["items"][0]["value"] == LABELS[language]["unsolved"]
    assert second["items"][0]["value"] == LABELS[language]["absent"]
    assert first["items"][0]["value"] != second["items"][0]["value"]
    assert first["sections"][1]["value"] == second["sections"][1]["value"] == LABELS[language]["unreviewed"]


@pytest.mark.parametrize("language", ["en", "zh"])
def test_explicit_legacy_basis_is_disclosed_and_does_not_rewrite_saved_scope(language):
    run = record(scope="PARTIAL")
    run["research_outcome"]["solve"].update(basis="explicit_claim_text", declared_scope="UNKNOWN")
    result = describe(run, language)
    assert result["items"][0]["value"] == LABELS[language]["partial"]
    assert result["items"][0]["note"] == ("Explicit text" if language == "en" else "原文自述")
    assert ("hashes are unchanged" if language == "en" else "哈希未修改") in result["sections"][0]["note"]
    assert run["research_outcome"]["solve"]["declared_scope"] == "UNKNOWN"


@pytest.mark.parametrize("language", ["en", "zh"])
def test_verify_no_issues_never_infers_full_coverage_or_novelty(language):
    run = record(workflow="verify", coverage="UNKNOWN", novelty="UNKNOWN")
    result = describe(run, language)
    words = LABELS[language]
    assert [item["value"] for item in result["items"]] == [words["unknown_coverage"], words["clean"], words["unknown_novelty"]]
    assert result["sections"][1]["coverage"] == words["unknown_coverage"]
    assert result["sections"][1]["novelty"] == words["unknown_novelty"]


@pytest.mark.parametrize("language", ["en", "zh"])
def test_organize_inherits_partial_claim_and_negative_review_even_with_finished_reports(language):
    run = record(workflow="organize", scope="PARTIAL", verdict="ISSUES_FOUND", coverage="PARTIAL")
    run["organized_report"] = {"bilingual_complete": True}
    result = describe(run, language)
    assert result["items"][0]["value"] == LABELS[language]["partial"]
    assert result["items"][0]["label"] == ("Source claim" if language == "en" else "沿用求解声称")
    assert result["items"][1]["value"] == ("Chinese + English ready" if language == "en" else "中英双版已生成")
    assert result["sections"][1]["value"] == LABELS[language]["issues"]
    assert result["sections"][1]["coverage"] == LABELS[language]["partial_coverage"]
    assert ("adds no proof" if language == "en" else "不新增证明") in result["note"]


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("linked,shared", [(False, False), (True, False), (True, True)])
def test_find_shows_only_shortlist_and_explicit_source_role_never_a_math_claim(language, linked, shared):
    run = record(workflow="find", scope="COMPLETE")
    run["shortlist_count"] = 3
    result = describe(run, language, {"linked": linked, "shared": shared})
    assert result["sections"] == []
    assert result["items"][-1]["value"].startswith("3 ")
    assert len(result["items"]) == (2 if linked else 1)
    assert LABELS[language]["complete"] not in json.dumps(result, ensure_ascii=False)
    if linked:
        expected = ("Shared Find source" if shared else "Find source") if language == "en" else (
            "共享选题来源" if shared else "选题来源")
        assert result["items"][0]["label"] == expected


@pytest.mark.parametrize("language", ["en", "zh"])
def test_runtime_status_changes_do_not_change_mathematical_outcome_labels(language):
    run = record(scope="UNKNOWN", coverage="UNKNOWN")
    expected = describe(run, language)
    for state in ("RUNNING", "FAILED", "RATE_LIMITED", "PAUSED"):
        changed = copy.deepcopy(run)
        changed["state"], changed["busy"] = state, state == "RUNNING"
        assert describe(changed, language) == expected
    assert expected["sections"][0]["value"] == LABELS[language]["unknown"]


def test_missing_old_outcome_payload_does_not_infer_success_from_completed_run():
    result = describe({"workflow": "solve", "state": "COMPLETED", "candidate_count": 1}, "en")
    assert result["items"][0]["value"] == "Scope not declared"
    assert result["sections"][1]["value"] == "Not reviewed"


@pytest.mark.parametrize("language", ["en", "zh"])
def test_truncated_candidate_claim_keeps_preview_and_explicit_full_text_pointer(language):
    run = record(scope="PARTIAL")
    preview = "A" * 600
    run["research_outcome"]["solve"].update(claim=preview, claim_truncated=True)
    result = describe(run, language)
    assert result["sections"][0]["claim"] == preview
    excerpt = result["sections"][0]["excerpt"]
    assert ("Excerpt only" if language == "en" else "此处为摘录") in excerpt
    assert ("full candidate and review" if language == "en" else "完整内容见下方候选与审查记录") in excerpt
    assert result["sections"][0]["value"] == LABELS[language]["partial"]


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("many_items", [True, False])
def test_both_solver_and_reviewer_obligation_previews_disclose_true_total(language, many_items):
    run = record(scope="PARTIAL", coverage="PARTIAL")
    for name, total in (("solve", 13 if many_items else 1), ("verify", 17 if many_items else 1)):
        preview = [f"Obligation {n}" for n in range(10)] if many_items else ["B" * 300]
        run["research_outcome"][name].update(remaining_obligations=preview,
            remaining_obligations_count=total, remaining_obligations_truncated=True)
    result = describe(run, language)
    for section, name in zip(result["sections"], ("solve", "verify"), strict=True):
        source = run["research_outcome"][name]
        assert section["obligations"] == source["remaining_obligations"]
        notice = section["obligationNotice"]
        total = source["remaining_obligations_count"]
        assert (f"{total} proof obligations in total" if language == "en" else f"共 {total} 项") in notice
        assert ("only part is shown" if language == "en" else "仅显示部分内容") in notice
        assert "undefined" not in notice and "{n}" not in notice


@pytest.mark.parametrize("language", ["en", "zh"])
def test_untruncated_previews_do_not_invent_omissions(language):
    run = record(scope="PARTIAL", coverage="PARTIAL")
    run["research_outcome"]["solve"]["claim_truncated"] = False
    for source in run["research_outcome"].values():
        source.update(remaining_obligations=["One short obligation"], remaining_obligations_count=1,
                      remaining_obligations_truncated=False)
    result = describe(run, language)
    assert result["sections"][0]["excerpt"] == ""
    assert all(section["obligationNotice"] == "" for section in result["sections"])


@pytest.mark.parametrize("language", ["en", "zh"])
def test_unreviewed_record_points_to_separate_verify_without_inventing_a_review(language):
    run = record(scope="PARTIAL")
    run["research_outcome"]["verify"] = {"status": "UNREVIEWED"}
    review = describe(run, language)["sections"][1]
    assert review["value"] == LABELS[language]["unreviewed"]
    assert review["coverage"] == review["novelty"] == LABELS[language]["unreviewed"]
    assert ("same problem group" if language == "en" else "同一问题组") in review["note"]
    assert ("If Verify has run" if language == "en" else "若已运行 Verify") in review["note"]
