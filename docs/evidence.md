# Evidence, completeness and independent checks

English | [简体中文](evidence.cn.md)

[Usage](usage.md) · [Resource requirements](resources.md) · [Result showcase](../showcase/README.md)

MathLottery records four separate questions: **does the source support an open-status assessment, is the candidate proof supported, does it cover the original problem, and what does the literature comparison support about novelty?** A completed task answers none of these automatically.

## Find: from a URL list to checkable evidence

A selection supplies `citations`, with the URL, role, exact short excerpt, locator, source date when known, and an explanation of relevance. Roles distinguish the original statement, explicit open status, later solutions, corrections and prior results. `literature_search` records actual search queries and the coverage conclusion. Its `unresolved` field records material gaps, such as an inaccessible potential solution or an unclear equivalence. Its `limitations` field separately records general coverage limits, such as searched databases, languages and dates, or the possibility of unindexed work. Both remain visible in the browser and report. A specific unresolved source or comparison must not be moved into `limitations` to obtain a positive label; previous `unresolved` entries are never automatically reclassified.

Excerpts must preserve the source text. Transcribing a printed formula as LaTeX, adding subscript underscores, translating or paraphrasing it can fail the literal match; use `statement` or `explanation` for these transcriptions. Prefer an accessible primary HTML/text version when PDF extraction loses the relevant formula. An unavailable or unmatched required passage remains an evidence gap, even if the agent says it read the PDF.

The harness independently retrieves cited public sources, respects robots policies and download limits, saves the bytes and extracted text, and checks excerpts after Unicode/whitespace normalization. For PDFs, matching also tolerates spacing around mathematical punctuation and two known extractor glyph names for slanted inequality signs; the receipt records the matching method. It preserves word boundaries, numbers, operators and quantifiers. Receipts contain SHA-256, retrieval time, requested URL and final redirect URL. It does not invent equivalence between different paper versions or accept agent-provided receipt metadata. PDF extraction requires the research dependencies and runs in the existing Python sandbox, limited to 100 pages, 512 MB, at most 10 seconds and 100,000 output characters. Extraction failures remain gaps.

An `OPEN` assessment needs a checked original statement, checked explicit-open evidence, observed search queries matching the reported search, and no material unresolved source gaps or later-solution/correction conflicts. A cited prior result with an unknown relationship also blocks it. General coverage limits are disclosed alongside this bounded assessment; they do not override failed checks. Snapshot freshness is limited to seven days; this concerns retrieval time, not the publication date. One maintained primary source may suffice for these traceability checks; two unrelated domains do not. Checked conflicting open/solution evidence becomes `DISPUTED`. Otherwise unsupported assertions become `UNKNOWN`, with reasons. The raw selection remains in the run's selection artifact.

These are **evidence requirements, not a certification that no solution exists**. The agent still interprets the passages, chooses search coverage, and compares mathematical statements. A source can be wrong or outdated; an apparently relevant search can miss another terminology or an unindexed paper. Queries exposed by native web tools and structured search tools are recorded; a shell search without a corresponding search-tool receipt remains an explicit coverage gap. Cited sources downloaded by an agent's shell can still be checked by the independent downloader.

When a native Codex turn is interrupted by a time or usage limit, successful completed searches from its confirmed session are retained with their original observation time. Resuming without another search does not erase those receipts or make them fresh again. Unfinished, failed, cancelled or unconfirmed-session searches are excluded; an interrupted turn's unfinished milestone is not accepted. Older missing receipts are not silently reconstructed.

## Solve and Verify: track the exact claim

Candidates declare `scope` (`COMPLETE`, `PARTIAL`, `COUNTEREXAMPLE`, `UNKNOWN`) and `remaining_obligations`. These are immutable candidate fields, alongside the claim, proof, assumptions and references. A complete reduction is still a partial answer if the reduced problem remains unsolved.

Each independent review supplies `checks` with the checked claim, method, result, reasoning, supporting evidence and whether the check is essential to the candidate proof. The harness requires a substantive derivation, counterexample or independently checked formal result for a positive review. Empty approvals, finite tests alone, self-reported Lean success, and unresolved essential steps become `INCONCLUSIVE`; a concrete contradictory check prevents approval. These checks make the review inspectable; they cannot make a model's mathematical reasoning infallible.

`original_problem_coverage` is separate: `FULL`, `PARTIAL`, `DIFFERENT` or `UNKNOWN`, accompanied by a comparison of assumptions and quantifiers. Unfinished obligations or a declared partial candidate prevent `FULL`. A correct partial result may remain `SELF_CHECKED`, while its original problem is still unresolved. Full coverage is explicitly a **reviewer assessment**, not external certification. The pipeline uses the evidence-gated verdict for revision/completion. A standalone verify still ends after an inconclusive review and preserves its gaps.

Novelty needs checked excerpts from the closest prior results, explicit comparisons and recorded search coverage. An equivalent prior result, or one whose restriction already covers the candidate (`SPECIAL_CASE`), conflicts with a novelty claim. A prior theorem proving only part of a stronger candidate is `DIFFERENT`, with the distinction explained. `POTENTIALLY_NEW` requires comparison evidence with no unresolved gaps; it never means “proved new.” Correctness does not require a favorable novelty assessment.

Use `ORIGINAL_STATEMENT` for a paper stating the conjecture, and `EXPLICIT_OPEN` for a source reporting that it remains open, in both Find and Verify. Matching an existing conjecture is not matching an existing proof. Reserve `PRIOR_RESULT` and `SOLUTION` for established results; an `EQUIVALENT` relation to those roles means the candidate has already been proved. Citation roles and their interpretations remain visible for review.

## Proof coverage and actionable literature gaps

New reviews include a `proof_steps` dependency graph. Each lemma, reduction, essential case and final conclusion has a stable ID and references named `checks`. The controller recomputes `proof_coverage`: missing dependencies, cycles, missing check IDs, finite tests alone and unresolved essential steps prevent a positive proof review. A `FORMAL` check names its `formal_declarations`; only matching declarations in an independent receipt bound to this candidate can support that step. This tests traceability of the submitted argument, not whether the reviewer identified every mathematically necessary step.

Claiming `FULL` coverage also requires six `statement_alignment` entries: definitions, assumptions, quantifiers, domain, boundary cases and conclusion. Each needs explicit original/candidate statements, reasoning and supported check references. An unrelated Lean theorem cannot certify the original problem. Alignment remains a reviewer assessment; the controller never certifies natural-language/formal equivalence.

`literature_search.obstacles` records stable IDs, the exact source, impact and a concrete next action. `comparisons` records prior and candidate assumptions/conclusions side by side. `RESOLVED` is a proposal: a resolution requires current independently retrieved excerpts and, when relevant, a supported theorem comparison. Renaming or omitting an earlier obstacle does not discharge it. Legacy `unresolved` text must be explicitly linked with `resolves_legacy_gaps` and supported by the same evidence checks. Existing barriers also accompany a new Verify of a saved candidate, without copying earlier reviewer verdicts or sessions.

New source checks create a persistent obligation for the **exact URL, locator and excerpt hash**. A later current receipt matching that target can close the access/excerpt obligation even if the inherited agent checkbox still says `OPEN`. A different sentence in the same paper cannot close it. This establishes access to the passage, not that its mathematical interpretation is correct. Old free-text barriers without a registered target still require an explicit resolution. If an erroneous quotation is corrected, explain that correction and attach a checked quotation at the registered locator; the record distinguishes this explicit correction from an exact-excerpt match.

Missing or unsupported theorem comparisons also retain their generated IDs. Close them by supplying a supported comparison for the same source and locator, linked through `obstacle_ids`; fetching the paper alone is insufficient. Original and mirror URLs are related only when a current independent receipt actually records that redirect. Similar titles, claimed mirror URLs and different publication versions are not automatically equivalent.

Each new assessment records effective state, the submitted state, resolution basis and a change relative to the previous controller assessment: new, resolved, reopened or unchanged. Missing or stale current evidence can reopen an earlier supported resolution. Historical reviews, failed receipts and legacy gap text are retained; they are not rewritten when a later attempt succeeds. The evidence policy version records which rules produced the new assessment. Closing an obstacle does not automatically upgrade novelty or proof status.

Each URL in an obstacle's `evidence_urls` needs a corresponding citation and verified excerpt. Keep optional bibliography links in `references`; a landing page without a checked citation cannot help discharge an obstacle. A native search tool reading a page does not guarantee that independent retrieval will succeed: access failures remain explicit gaps.

In the browser, expand **Key proof steps** and **Novelty obstacles**. On an idle Find or Verify run, **Prepare focused follow-up** fills the resume instructions for one obstacle. Review the total budget and click **Continue research** to execute; preparing the form does not call a model. Unavailable sources remain visible until evidence supports a resolution. Resolving all recorded barriers does not prove an exhaustive literature search or novelty.

## Independent Lean receipts

In the browser, select the required small proof sources when verifying a saved candidate. They are frozen and hashed before review.

Lean sources and project files are selectable throughout the workspace. Small Markdown/text proofs, JSON/CSV certificates and Python reproduction scripts are also selectable when saved under `workspace/proof/` or `workspace/formal/`. Only explicitly selected files are copied; scripts are untrusted inputs and are not automatically executed. The existing file-count, byte-size and link restrictions apply to every attachment. Compiled objects and dependency caches are excluded.

The reviewer can request:

```json
{
  "formal_check": {
    "files": ["workspace/Lemmas.lean", "workspace/Main.lean"],
    "declarations": ["Main.target"]
  }
}
```

Files must be attached, listed in dependency order, and use plain module names. Declarations must be named theorems in submitted modules. The checker compiles the frozen bytes in a network-free bubblewrap sandbox, freezes only the expected regular object files, replays the submitted modules with `leanchecker`, and uses a harness-owned inspector to read theorem types and transitive axioms with module initializers/extensions disabled. It accepts only `propext`, `Classical.choice` and `Quot.sound` among the selected theorems' axiom dependencies. `sorryAx` and user axioms prevent a successful receipt. An unused placeholder elsewhere is not a statement about the selected theorem; consult the recorded declaration scope.

The optional `module_root` defaults to the submitted workspace. If `workspace/proof/Main.lean` uses `import Lemmas` for `workspace/proof/Lemmas.lean`, set `"module_root": "proof"` and attach both files in dependency order. If it uses `import proof.Lemmas`, leave the root empty. The root must be a plain relative directory, and every requested file must be beneath it. It changes module resolution without rewriting source bytes, reading unattached files, or allowing submitted modules to replace trusted libraries or the inspector. Receipts retain original source paths and record the derived module names.

Receipts record the original statement hash, candidate hash, source/object hashes, compiler version, commands, exits, limits, logs, declaration types and axioms. `KERNEL_REPLAYED` can support `PARTIALLY_VERIFIED`; it never automatically produces `FORMALLY_VERIFIED`, `EXPERT_REVIEWED`, or a solved problem status. Prebuilt dependencies, the compiler and Lean's own kernel remain trusted. This is not an independent kernel implementation, and natural-language/formal equivalence still needs separate review.

When a check reaches a resource limit, resume the existing Verify with instructions to retry. Its expandable **Independent Lean check resources** controls can change the saved Lean memory threshold, virtual address-space ceiling and total formal-check timeout. Blank fields preserve the saved values. A new attempt retains the earlier failure receipt and still checks the same frozen sources. During independent source/formal checks, the Activity tab keeps the saved research output and shows that evidence checks are pending.

A continued native review receives that run's controller source assessment, validation notes and matching formal receipt, so it can reassess the outcome after checks finish. It can reuse a successful receipt for the unchanged candidate without recompiling. This feedback omits prior agent opinions and solver history; starting a new Verify still starts an independent review without these earlier results.

The checker never executes submitted Lake configuration, downloads dependencies or builds mathlib. Install compatible Lean, `leanchecker`, bubblewrap and `prlimit` (Linux/WSL); environments that prohibit bubblewrap namespaces report failure without falling back to unrestricted execution. Prepare compatible prebuilt libraries separately and configure them in `config.yaml`:

```yaml
verification:
  fetch_sources: true
  max_sources: 12
  source_timeout_seconds: 60
  formal_enabled: true
  lean_command: lean
  lean_library_paths: []  # Explicit prebuilt library directories, relative to the project.
  formal_timeout_seconds: 120
  formal_memory_mb: 2048
  formal_address_space_mb: 8192
  formal_max_object_mb: 16
  formal_max_total_object_mb: 960
```

For example, a prepared Lean project may need its `.lake/build/lib/lean` and each dependency's corresponding build directory. Paths must match the configured compiler version. Use your own local configuration; no machine-specific paths are discovered and persisted. The receipt inspector is exercised with Lean 4.35.0; an incompatible toolchain must report failure rather than silently skip inspection.

Generated compiler objects have separate size limits: `formal_max_object_mb` defaults to 16 MiB per file, enforced with `RLIMIT_FSIZE`; `formal_max_total_object_mb` defaults to 960 MiB across compiler output. The total is monitored during compilation and checked again before acceptance; this is not a host-wide disk quota. Temporary compiler output is limited to 256 file/directory entries, and only expected regular object files can reach replay and inspection. Small sources can produce much larger proof objects, so adjust these local limits from measured compiler output when needed. `formal_timeout_seconds` may be configured up to 1,800 seconds for larger proofs, while still sharing the remaining run budget. Receipts record limits, object sizes and hashes. Temporary compiled objects are removed after checking; receipt metadata and logs remain in the run.

These defaults cap source collection at 12 distinct URLs per selection/review milestone. Source collection checks its time/stop budget between requests/chunks; an in-flight request can last until `tools.web_timeout_seconds`. Overall active time still counts. Source retrieval also honors `backend.native_network_access: false`. Formal checks share the remaining task time, use one Lean worker and a 64 MiB thread stack, and apply a 2,048 MB Lean `-M` threshold plus a separate 8,192 MB per-process virtual-address-space limit (`RLIMIT_AS`). Reserved stacks and mapped libraries count toward address space; the 8 GiB ceiling is not 8 GiB of allocated RAM or a peak RSS measurement. The separate ceiling accommodates [Lean startup stack reservations](https://github.com/leanprover/lean4/blob/v4.35.0/src/runtime/thread.cpp). These are **not a global RSS cap on native agent commands, subprocess trees, WSL or Windows**. Timeouts and resource failures are incomplete checks, not mathematical disproofs. See [resources](resources.md) before increasing limits.

## Results and old records

The browser and Markdown report show candidate scope, original-problem coverage, remaining obligations, concrete checks, source gaps and independent formal receipts separately. New reports retain the raw agent verdict/novelty when the gate changes them. Historical checkpoints remain readable and retain their recorded verdicts; missing new evidence is shown as unassessed. Re-run verify to obtain a new assessment under the current policy, rather than silently rewriting history.

Sources and execution receipts stay in the ignored run directory (`literature/` and `verification/`). Development audits belong under the ignored `audits/codex_audits/<timestamp>/`. Curated [showcase results](../showcase/README.md) retain their explicitly documented historical verification scope.

Completed native web searches and identifiable MCP search tool calls can supply observed query receipts. Queries are extracted from tool inputs, not from agent-written search claims. Failed calls and arbitrary shell output do not count. MCP receipts still require independently retrieved primary-source excerpts; they do not certify novelty.
