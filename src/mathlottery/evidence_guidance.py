"""Milestone evidence requirements shared by native and compatibility prompts."""

from mathlottery.models import Phase

GUIDANCE = {
    Phase.FIND: """At selection, include citations with url, role, locator (page/theorem/problem
number), a short verbatim excerpt, explanation of relevance, source_date when known, and relation
(UNKNOWN/EQUIVALENT/SPECIAL_CASE/DIFFERENT). Roles: ORIGINAL_STATEMENT, EXPLICIT_OPEN, SOLUTION,
CORRECTION, PRIOR_RESULT. Quote the exact original statement and explicit open-status evidence;
use ORIGINAL_STATEMENT for a published conjecture and EXPLICIT_OPEN for an open-status statement.
PRIOR_RESULT and SOLUTION refer to established results, not merely a previously stated problem.
check quantifiers, parameter ranges, versions, errata, later solutions and equivalent formulations.
Use short excerpts sufficient for the point, not large copied passages. Include literature_search:
{queries: [...], conclusion: search scope and comparison of findings, unresolved: [material gaps],
limitations: [general coverage limits]}. Queries must be actual searches made with available search
tools. A specific inaccessible potential solution, conflicting status, or unclear comparison belongs
in unresolved and blocks support. General limits (searched databases/languages/dates, possible
unindexed work) belong in limitations and remain visible; never move a material gap there just to
obtain OPEN. An OPEN label is a bounded literature assessment, not proof of worldwide absence.
A recent download date does not
make an old open-status statement current. One maintained primary source can be useful; counting
websites proves nothing. The harness will independently retrieve cited URLs and check excerpts.
Copy excerpt text literally: do not replace printed formulas with LaTeX, add underscores, translate,
or paraphrase inside excerpt. Put formula transcriptions and interpretation in statement/explanation.
If PDF text extraction cannot faithfully preserve the needed passage, use an accessible primary
HTML/text version with an exact locator, or report the retrieval gap. Do not evade site access rules.
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
Use remaining_obligations only for unresolved mathematical proof or original-statement coverage
obligations, such as an unproved lemma, omitted boundary case or missing implication. If none remain,
use an empty list []; do not insert a sentence saying there are no remaining obligations.
Record pending or failed compilation in FORMAL checks and proof_assessment, with blocking=true when
essential to accepting the proof, and request formal_check where appropriate. Put specific literature
gaps in literature_search.unresolved and explain their effect in novelty_notes. Record the absence of
external expert review or formal/natural-language alignment certification in proof_assessment or
coverage_explanation; these certification limits are not themselves missing mathematical cases.
Keep actual doubts about statement alignment explicit in checks and coverage. Never reclassify an
unproved mathematical step as a tooling or certification limitation to obtain FULL coverage.

For novelty include citations: [{url, role, locator, excerpt, explanation, source_date, relation}],
using roles ORIGINAL_STATEMENT/EXPLICIT_OPEN/PRIOR_RESULT/SOLUTION/CORRECTION and a short verbatim
excerpt. A source stating the original conjecture is ORIGINAL_STATEMENT; a source explicitly
reporting it open is EXPLICIT_OPEN. Do not classify these as PRIOR_RESULT or SOLUTION merely
because their mathematical statements match the candidate. Those two roles denote established
results: an EQUIVALENT or SPECIAL_CASE relation to them tells the harness the candidate was
already proved. Explain conjecture provenance separately from prior proof comparisons.
Compare the closest results' assumptions and conclusions explicitly, including equivalent
formulations and special cases (relation: EQUIVALENT, SPECIAL_CASE, DIFFERENT, UNKNOWN).
SPECIAL_CASE means the candidate is already covered by restricting the cited theorem; if the
cited result proves only part of a stronger candidate, use DIFFERENT and explain what is new.
Include literature_search: {queries: actual search-tool queries, conclusion: coverage and findings,
unresolved: specific inaccessible relevant sources or unresolved comparisons,
limitations: general search coverage limits}. Keep material gaps in unresolved; limitations do not
override missing citations, conflicting results, or unclear comparisons. No search hit is not proof
of novelty. Copy short excerpts literally from the cited source; formula transcriptions and
paraphrases belong in explanation, not excerpt. Prefer primary HTML/text if PDF extraction is lossy.
The harness re-fetches cited sources; URL lists and model-provided timestamps are insufficient.

If immutable Lean sources were explicitly attached, you may request formal_check:
{files: ordered workspace/Module.lean paths from the supplied manifest, declarations: qualified
theorem names, module_root: optional directory relative to workspace}. The default module_root is
empty. For workspace/proof/Main.lean importing Lemmas from workspace/proof/Lemmas.lean, set
module_root to "proof" and attach both files in dependency order. For imports proof.Lemmas, keep
the default root. This only changes module resolution; no source bytes are rewritten and only
explicitly attached files are available. This requests an independent harness check after your review. The checker uses
configured prebuilt dependencies, no Lake hooks/downloads, one thread and bounded memory/time.
It checks only the requested declarations; explain their relation to the entire original problem.
Never fill formal_receipt, evidence_assessment, validation_notes or reported_* fields yourself;
they are controller-owned and are overwritten. Lack of tools or evidence must remain visible.""",
}
