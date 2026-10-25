"""Execute the browser's pure grouping module in Node, without a DOM or models."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "src/mathlottery/web/static/history.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute frontend grouping tests")
DRIVER = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
function freeze(value) {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}
const before = JSON.stringify(input);
freeze(input);
const api = require(process.argv[1]);
const groups = api.groupRuns(input);
if (before !== JSON.stringify(input)) throw new Error('Input mutated');
const context = {window: {}};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const browserGroups = context.window.MathLotteryHistory.groupRuns(input);
if (JSON.stringify(groups) !== JSON.stringify(browserGroups)) throw new Error('Browser/Node mismatch');
process.stdout.write(JSON.stringify(groups));
"""


def grouped(runs):
    result = subprocess.run([NODE, "-e", DRIVER, str(MODULE)], input=json.dumps(runs),
                            text=True, capture_output=True, check=True, timeout=10)
    return json.loads(result.stdout)


def run(identifier, workflow, key=None, title="Question", source=None, created=1, updated=None):
    return {"id": identifier, "workflow": workflow, "problem_key": key, "title": title,
            "discovery_run_id": source, "created_at": f"2026-01-{created:02d}T00:00:00Z",
            "updated_at": f"2026-01-{updated or created:02d}T00:00:00Z"}


def run_ids(group):
    return [item["id"] for item in group["runs"]]


def test_explicit_find_selection_joins_problem_with_verify_and_organize():
    records = [run("find", "find", title="Find an approachable problem", updated=8),
               run("solve", "solve", "exact-statement", "Selected conjecture", "find", created=2),
               run("verify", "verify", "exact-statement", "Selected conjecture", created=3),
               run("organize", "organize", "exact-statement", "Selected conjecture", created=4)]
    groups = grouped(records)
    assert len(groups) == 1
    assert groups[0]["key"] == "problem:exact-statement"
    assert groups[0]["title"] == "Selected conjecture"
    assert groups[0]["latest"]["id"] == "find"  # A newer query must not replace the problem title.
    assert run_ids(groups[0]) == ["find", "solve", "verify", "organize"]
    assert groups[0]["sharedFindIds"] == []


def test_one_find_selected_for_two_problems_is_shared_without_merging_targets():
    records = [run("find", "find", title="One shortlist"),
               run("solve-a", "solve", "A", "Problem A", "find", created=2),
               run("solve-b", "solve", "B", "Problem B", "find", created=3),
               run("verify-a", "verify", "A", "Problem A", created=4)]
    groups = grouped(records)
    assert [g["title"] for g in groups] == ["Problem A", "Problem B"]
    assert [run_ids(g) for g in groups] == [["find", "solve-a", "verify-a"], ["find", "solve-b"]]
    assert all(g["sharedFindIds"] == ["find"] for g in groups)
    assert len({item["id"] for g in groups for item in g["runs"]}) == len(records) == 4


def test_repeated_solve_retains_each_execution_but_attaches_source_only_once():
    records = [run("find", "find"), run("solve-1", "solve", "A", source="find", created=2),
               run("solve-2", "solve", "A", source="find", created=3),
               run("solve-3", "solve", "A", created=4)]
    groups = grouped(records + [records[0]])
    assert len(groups) == 1
    assert run_ids(groups[0]) == ["find", "solve-1", "solve-2", "solve-3"]


def test_unselected_find_keeps_query_title_even_when_recommendation_matches_problem():
    records = [run("find", "find", "A", title="Query: recommend a small problem"),
               run("solve", "solve", "A", title="Custom problem", created=2)]
    groups = grouped(records)
    assert {g["key"]: g["title"] for g in groups} == {
        "run:find": "Query: recommend a small problem", "problem:A": "Custom problem"}
    assert all(len(g["runs"]) == 1 for g in groups)


def test_custom_problem_groups_by_statement_identity_without_find():
    groups = grouped([run("solve", "solve", "custom", created=2),
                      run("verify", "verify", "custom", created=3)])
    assert len(groups) == 1 and run_ids(groups[0]) == ["solve", "verify"]


def test_same_title_different_statement_keys_and_missing_keys_never_merge():
    groups = grouped([run("solve-a", "solve", "A"), run("solve-b", "solve", "B"),
                      run("solve-c", "solve"), run("solve-d", "solve")])
    assert len(groups) == 4
    assert {g["key"] for g in groups} == {"problem:A", "problem:B", "run:solve-c", "run:solve-d"}


@pytest.mark.parametrize("source", ["missing", "solve-other", "solve"])
def test_missing_non_find_and_self_links_do_not_attach_or_merge(source):
    records = [run("find", "find"), run("solve-other", "solve", "B", source="find"),
               run("solve", "solve", "A", source=source)]
    groups = {g["key"]: g for g in grouped(records)}
    assert run_ids(groups["problem:A"]) == ["solve"]
    assert set(run_ids(groups["problem:B"])) == {"find", "solve-other"}


@pytest.mark.parametrize("source", ["solve", "find", "other-find", "missing"])
def test_malformed_find_upstream_or_cycle_cannot_authorize_a_link(source):
    records = [run("find", "find", source=source), run("other-find", "find"),
               run("solve", "solve", "A", source="find")]
    groups = grouped(records)
    assert len(groups) == 3
    assert all(len(g["runs"]) == 1 for g in groups)


def test_two_solve_cycle_does_not_infer_find_provenance():
    records = [run("find", "find"), run("solve-a", "solve", "A", source="solve-b"),
               run("solve-b", "solve", "B", source="solve-a")]
    assert len(grouped(records)) == 3


def test_two_explicit_finds_for_same_problem_are_both_preserved():
    groups = grouped([run("find-1", "find"), run("find-2", "find", created=2),
                      run("solve-1", "solve", "A", source="find-1", created=3),
                      run("solve-2", "solve", "A", source="find-2", created=4)])
    assert len(groups) == 1
    assert run_ids(groups[0]) == ["find-1", "find-2", "solve-1", "solve-2"]


def test_sorting_is_stable_across_input_order_and_inputs_are_deep_frozen():
    records = [run("find", "find"), run("solve-z", "solve", "Z", "Question Z", "find", created=2),
               run("solve-a", "solve", "A", "Question A", "find", created=2),
               run("verify-z", "verify", "Z", "Question Z", created=2)]
    first = grouped(records)
    assert first == grouped(list(reversed(records)))
    assert [g["key"] for g in first] == ["problem:A", "problem:Z"]


def test_ambiguous_duplicate_source_id_cannot_authorize_find_link():
    groups = grouped([run("find", "find"), run("find", "find", source="other"),
                      run("solve", "solve", "A", source="find", created=2)])
    assert len(groups) == 2
    assert all(len(g["runs"]) == 1 for g in groups)


def test_empty_history():
    assert grouped([]) == []
