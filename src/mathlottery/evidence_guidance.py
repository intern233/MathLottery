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
the final selection only; choose your research steps and tools freely.

Before asking the user to choose, include source_statement with the original question and quantifiers,
scope_relation (FULL_STATEMENT/EXPLICIT_SUBPROBLEM/INTERPRETATION/UNKNOWN), scope_description,
prior_work_summary, and statement_risks. Each risk has id, kind, severity, description, impact,
next_action, source_url and locator. Disclose quantifier ambiguity, missing assumptions, conflicting
versions, unavailable source text, selected subproblems and missing formalizations before Solve.
Use severity NEEDS_CLARIFICATION when source quantifiers conflict. Preserve the complete original
statement when the selected target is only a branch; do not portray that branch as the whole question.
An empty risk list means no risk was reported, not certified unambiguity. These disclosures describe
the final shortlist and do not prescribe the agent's intermediate methods or tools.""",
    Phase.SOLVE: """For each candidate, declare scope: COMPLETE, PARTIAL, COUNTEREXAMPLE or UNKNOWN,
and remaining_obligations: [...]. COMPLETE means the full original statement, with its quantifiers
and assumptions; a reduction or a proved subcase is PARTIAL until all remaining obligations are
discharged. A counterexample must satisfy every original hypothesis and negate the actual claim.
conclude means this research task ends, never that the original problem has been solved.""",
    Phase.VERIFY: """The review verdict assesses the candidate's mathematical claim and proof.
Assess novelty independently. Novelty UNKNOWN or an unavailable source used only for a novelty
comparison does not by itself require INCONCLUSIVE or invalidate established original-problem
coverage. Record such gaps in literature_search.unresolved/obstacles and novelty_notes, not as
mathematical issues or remaining_obligations. This does not justify a positive proof verdict:
choose it only when your independent mathematical checks support it, with every essential step
and claimed statement-alignment obligation checked. Never infer correctness from absent novelty
evidence. If an unavailable source prevents establishing the original problem's meaning, a
mathematical assumption or an essential proof dependency, record that concrete uncertainty in
the appropriate blocking check, retain unresolved statement alignment/coverage, and use
INCONCLUSIVE. Do not relabel a mathematical uncertainty as a novelty-only gap.

Supply explicit checks: [{id, claim, method, result, reasoning, evidence, blocking,
formal_declarations: []}]. Assign unique stable IDs for cross-references.
Methods: DERIVATION, COUNTEREXAMPLE, FINITE_TEST, FORMAL, REFERENCE. Results: SUPPORTED,
CONTRADICTED, UNRESOLVED. Give checkable mathematical derivations, exact failing steps or concrete
counterexamples. Cover all essential proof obligations, definitions, quantifiers, assumptions and
boundary cases. Blocking means essential to the submitted candidate claim. An unresolved blocking
check prevents a positive verdict. Finite tests and self-reported compilation do not prove a theorem.

At the final review milestone, include proof_steps: [{id, statement, kind: LEMMA/REDUCTION/CASE/
CONCLUSION, dependencies: [step IDs], check_ids: [check IDs], essential: true}]. Map every essential
lemma, reduction and case, including dependencies, to substantive checks. At least one supported
check.claim must reproduce each step.statement exactly (whitespace differences are allowed).
Do not omit difficult
steps or mark a dependency optional to hide it. At least one essential CONCLUSION must reproduce
the submitted candidate claim exactly. Missing proof-step/check references, circular dependencies, unchecked
essential nodes and finite tests alone block a positive verdict. A FORMAL check must list exact
formal_declarations present in a matching independent kernel receipt. A checked lemma is not a
receipt for the entire proof. Provide derivations for mathematical steps not covered by Lean.
The controller only checks structural coverage; this is not external expert certification.

Include statement_alignment: [{facet, original, candidate, assessment: MATCHED/DIFFERENT/UNRESOLVED,
reasoning, check_ids, formal_statement: ""}]. Cover each facet exactly once: DEFINITIONS,
ASSUMPTIONS, QUANTIFIERS, DOMAIN, BOUNDARY_CASES, CONCLUSION. State explicitly when a facet is
vacuous and justify it. Bind each comparison to a check. FULL original-problem coverage requires
all six matched facets; a correct partial candidate may still receive a positive proof review.
For the CONCLUSION facet, original must quote the entire registered problem.statement and candidate
must quote the entire submitted candidate.claim, without paraphrasing either target.
If Lean is used, quote its exact applicable formal statements and explain their scope. Never
confuse structural checks or kernel acceptance with certified natural-language equivalence.

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
Never fill formal_receipt, proof_coverage, evidence_assessment, validation_notes or reported_* fields yourself;
they are controller-owned and are overwritten. Lack of tools or evidence must remain visible.""",
}

LITERATURE_TASKS = """
Make specific literature barriers actionable in literature_search.obstacles:
[{id, kind: INACCESSIBLE_SOURCE/UNCLEAR_COMPARISON/CONFLICTING_STATUS/MISSING_PROVENANCE/OTHER,
source_url: URL or null, description, impact, next_action, status: OPEN/RESOLVED, resolution: "",
evidence_urls: [], resolves_legacy_gaps: []}]. Use stable IDs across attempts and preserve previous
obstacles. Omission, relabeling as a general limitation, or a RESOLVED checkbox does not discharge
them. RESOLVED requires a concrete explanation and independently checked current source excerpts;
check the exact obstacle source. When a comparison or conflicting status is involved, link the
obstacle ID to an explicit checked prior-result comparison. If resolving a historical unresolved
string, include that exact string in resolves_legacy_gaps. Old gaps otherwise continue blocking
supported novelty/open-status assessments; a novelty-only gap does not determine proof validity.

Preserve controller-generated source-/comparison-/gap- IDs and any registered required_locator
and required_excerpt_sha256. These identify the original obligation and cannot be replaced by an
easier sentence or theorem. A current checked excerpt matching the exact registered source goal
can close the access/excerpt barrier automatically; it does not certify the passage's interpretation
or novelty. If correcting an erroneous old quotation, explain the correction explicitly and attach
a checked citation at the original locator, rather than deleting the old goal. Old free-text source
barriers still need an explicit RESOLVED explanation with checked citations. For a generated
comparison goal, link its exact ID in the matching comparison.obstacle_ids and compare that same
source and locator. A mere successful download cannot close a semantic comparison or status conflict.
Use the latest controller resolution_reason to target the next action; failed or stale current
receipts may reopen an earlier resolution. Do not invent mirror equivalence: only an actually
observed independent redirect receipt connects different URLs automatically.

Compare close prior theorems in literature_search.comparisons:
[{id, source_url, locator, prior_assumptions, candidate_assumptions, prior_conclusion,
candidate_conclusion, relation: UNKNOWN/EQUIVALENT/SPECIAL_CASE/DIFFERENT, reasoning, obstacle_ids: []}].
Match source_url, locator and relation to a PRIOR_RESULT or SOLUTION citation with a literal excerpt.
Explain restrictions and implications explicitly, not just title similarity. POTENTIALLY_NEW requires
checked structured comparisons to the closest cited results and remains a bounded model assessment.
These are final evidence milestones only; choose searches, tools and intermediate work freely.
"""
GUIDANCE[Phase.FIND] += LITERATURE_TASKS
GUIDANCE[Phase.VERIFY] += LITERATURE_TASKS
