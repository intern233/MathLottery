"""Milestone evidence requirements shared by native and compatibility prompts."""

from mathlottery.models import Phase

GUIDANCE = {
    Phase.FIND: """At selection, include citations with url, role, locator (page/theorem/problem
number), a short verbatim excerpt, explanation of relevance, source_date when known, and relation
(UNKNOWN/EQUIVALENT/SPECIAL_CASE/DIFFERENT). Roles: ORIGINAL_STATEMENT, EXPLICIT_OPEN, SOLUTION,
CORRECTION, PRIOR_RESULT. Quote the exact original statement and explicit open-status evidence;
check quantifiers, parameter ranges, versions, errata, later solutions and equivalent formulations.
Use short excerpts sufficient for the point, not large copied passages. Include literature_search:
{queries: [...], conclusion: search scope and comparison of findings, unresolved: [specific gaps]}.
Queries must be actual searches made with available search tools. Describe inaccessible full texts
and unclear equivalences as unresolved, never silently omit them. A recent download date does not
make an old open-status statement current. One maintained primary source can be useful; counting
websites proves nothing. The harness will independently retrieve cited URLs and check excerpts.
Retain UNKNOWN if the evidence cannot support an open-status assessment. These fields structure
the final selection only; choose your research steps and tools freely.""",
    Phase.SOLVE: """For each candidate, declare scope: COMPLETE, PARTIAL, COUNTEREXAMPLE or UNKNOWN,
and remaining_obligations: [...]. COMPLETE means the full original statement, with its quantifiers
and assumptions; a reduction or a proved subcase is PARTIAL until all remaining obligations are
discharged. A counterexample must satisfy every original hypothesis and negate the actual claim.
conclude means this research task ends, never that the original problem has been solved.""",
    Phase.VERIFY: """Supply explicit checks: [{claim, method, result, reasoning, evidence, blocking}].
Methods: DERIVATION, COUNTEREXAMPLE, FINITE_TEST, FORMAL, REFERENCE. Results: SUPPORTED,
CONTRADICTED, UNRESOLVED. Give checkable mathematical derivations, exact failing steps or concrete
counterexamples. Cover all essential proof obligations, definitions, quantifiers, assumptions and
boundary cases. Blocking means essential to the submitted candidate claim. An unresolved blocking
check prevents a positive verdict. Finite tests and self-reported compilation do not prove a theorem.

Assess original_problem_coverage separately: FULL, PARTIAL, DIFFERENT or UNKNOWN. Include a
coverage_explanation comparing the exact candidate claim to the original problem, and list
remaining_obligations. Distinguish a correct partial result from a complete solution. Use UNKNOWN
when the comparison cannot be established. Do not accept the solver's scope label without checking.

For novelty include citations: [{url, role, locator, excerpt, explanation, source_date, relation}],
using roles PRIOR_RESULT/SOLUTION/CORRECTION and a short verbatim excerpt from the relevant result.
Compare the closest results' assumptions and conclusions explicitly, including equivalent
formulations and special cases (relation: EQUIVALENT, SPECIAL_CASE, DIFFERENT, UNKNOWN).
SPECIAL_CASE means the candidate is already covered by restricting the cited theorem; if the
cited result proves only part of a stronger candidate, use DIFFERENT and explain what is new.
Include literature_search: {queries: actual search-tool queries, conclusion: coverage and findings,
unresolved: inaccessible sources or unresolved comparisons}. No search hit is not proof of novelty.
The harness re-fetches cited sources; URL lists and model-provided timestamps are insufficient.

If immutable Lean sources were explicitly attached, you may request formal_check:
{files: ordered workspace/Module.lean paths from the supplied manifest, declarations: qualified
theorem names}. This requests an independent harness check after your review. The checker uses
configured prebuilt dependencies, no Lake hooks/downloads, one thread and bounded memory/time.
It checks only the requested declarations; explain their relation to the entire original problem.
Never fill formal_receipt, evidence_assessment, validation_notes or reported_* fields yourself;
they are controller-owned and are overwritten. Lack of tools or evidence must remain visible.""",
}
