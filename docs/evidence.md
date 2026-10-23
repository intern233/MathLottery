# Evidence, completeness and independent checks

English | [简体中文](evidence.cn.md)

[Usage](usage.md) · [Resource requirements](resources.md) · [Result showcase](../showcase/README.md)

MathLottery records four separate questions: **does the source support an open-status assessment, is the candidate proof supported, does it cover the original problem, and what does the literature comparison support about novelty?** A completed task answers none of these automatically.

## Find: from a URL list to checkable evidence

A selection supplies `citations`, with the URL, role, exact short excerpt, locator, source date when known, and an explanation of relevance. Roles distinguish the original statement, explicit open status, later solutions, corrections and prior results. `literature_search` records actual search queries, the coverage conclusion, and unresolved gaps such as inaccessible papers or unclear equivalences.

The harness independently retrieves cited public sources, respects robots policies and download limits, saves the bytes and extracted text, and checks excerpts after Unicode/whitespace normalization. Receipts contain SHA-256, retrieval time, requested URL and final redirect URL. It does not invent equivalence between different paper versions or accept agent-provided receipt metadata. PDF extraction requires the research dependencies and runs in the existing Python sandbox, limited to 100 pages, 512 MB, at most 10 seconds and 100,000 output characters. Extraction failures remain gaps.

An `OPEN` assessment needs a checked original statement, checked explicit-open evidence, observed search queries matching the reported search, and no unresolved source gaps or later-solution/correction conflicts. Snapshot freshness is limited to seven days; this concerns retrieval time, not the publication date. One maintained primary source may suffice for these traceability checks; two unrelated domains do not. Checked conflicting open/solution evidence becomes `DISPUTED`. Otherwise unsupported assertions become `UNKNOWN`, with reasons. The raw selection remains in the run's selection artifact.

These are **evidence requirements, not a certification that no solution exists**. The agent still interprets the passages, chooses search coverage, and compares mathematical statements. A source can be wrong or outdated; an apparently relevant search can miss another terminology or an unindexed paper. Queries exposed by native web tools and structured search tools are recorded; a shell search without a corresponding search-tool receipt remains an explicit coverage gap. Cited sources downloaded by an agent's shell can still be checked by the independent downloader.

## Solve and Verify: track the exact claim

Candidates declare `scope` (`COMPLETE`, `PARTIAL`, `COUNTEREXAMPLE`, `UNKNOWN`) and `remaining_obligations`. These are immutable candidate fields, alongside the claim, proof, assumptions and references. A complete reduction is still a partial answer if the reduced problem remains unsolved.

Each independent review supplies `checks` with the checked claim, method, result, reasoning, supporting evidence and whether the check is essential to the candidate proof. The harness requires a substantive derivation, counterexample or independently checked formal result for a positive review. Empty approvals, finite tests alone, self-reported Lean success, and unresolved essential steps become `INCONCLUSIVE`; a concrete contradictory check prevents approval. These checks make the review inspectable; they cannot make a model's mathematical reasoning infallible.

`original_problem_coverage` is separate: `FULL`, `PARTIAL`, `DIFFERENT` or `UNKNOWN`, accompanied by a comparison of assumptions and quantifiers. Unfinished obligations or a declared partial candidate prevent `FULL`. A correct partial result may remain `SELF_CHECKED`, while its original problem is still unresolved. Full coverage is explicitly a **reviewer assessment**, not external certification. The pipeline uses the evidence-gated verdict for revision/completion. A standalone verify still ends after an inconclusive review and preserves its gaps.

Novelty needs checked excerpts from the closest prior results, explicit comparisons and recorded search coverage. An equivalent prior result, or one whose restriction already covers the candidate (`SPECIAL_CASE`), conflicts with a novelty claim. A prior theorem proving only part of a stronger candidate is `DIFFERENT`, with the distinction explained. `POTENTIALLY_NEW` requires comparison evidence with no unresolved gaps; it never means “proved new.” Correctness does not require a favorable novelty assessment.

## Independent Lean receipts

In the browser, select the required small proof sources when verifying a saved candidate. They are frozen and hashed before review. The reviewer can request:

```json
{
  "formal_check": {
    "files": ["workspace/Lemmas.lean", "workspace/Main.lean"],
    "declarations": ["Main.target"]
  }
}
```

Files must be attached, listed in dependency order, and use plain module names. Declarations must be named theorems in submitted modules. The checker compiles the frozen bytes in a network-free bubblewrap sandbox, freezes only the expected regular object files, replays the submitted modules with `leanchecker`, and uses a harness-owned inspector to read theorem types and transitive axioms with module initializers/extensions disabled. It accepts only `propext`, `Classical.choice` and `Quot.sound` among the selected theorems' axiom dependencies. `sorryAx` and user axioms prevent a successful receipt. An unused placeholder elsewhere is not a statement about the selected theorem; consult the recorded declaration scope.

Receipts record the original statement hash, candidate hash, source/object hashes, compiler version, commands, exits, limits, logs, declaration types and axioms. `KERNEL_REPLAYED` can support `PARTIALLY_VERIFIED`; it never automatically produces `FORMALLY_VERIFIED`, `EXPERT_REVIEWED`, or a solved problem status. Prebuilt dependencies, the compiler and Lean's own kernel remain trusted. This is not an independent kernel implementation, and natural-language/formal equivalence still needs separate review.

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
```

For example, a prepared Lean project may need its `.lake/build/lib/lean` and each dependency's corresponding build directory. Paths must match the configured compiler version. Use your own local configuration; no machine-specific paths are discovered and persisted. The receipt inspector is exercised with Lean 4.35.0; an incompatible toolchain must report failure rather than silently skip inspection.

These defaults cap source collection at 12 distinct URLs per selection/review milestone. Source collection checks its time/stop budget between requests/chunks; an in-flight request can last until `tools.web_timeout_seconds`. Overall active time still counts. Source retrieval also honors `backend.native_network_access: false`. Formal checks share the remaining task time, use one Lean worker and a 64 MiB thread stack, and apply a 2,048 MB Lean `-M` threshold plus a separate 8,192 MB per-process virtual-address-space limit (`RLIMIT_AS`). Reserved stacks and mapped libraries count toward address space; the 8 GiB ceiling is not 8 GiB of allocated RAM or a peak RSS measurement. The separate ceiling accommodates [Lean startup stack reservations](https://github.com/leanprover/lean4/blob/v4.35.0/src/runtime/thread.cpp). These are **not a global RSS cap on native agent commands, subprocess trees, WSL or Windows**. Timeouts and resource failures are incomplete checks, not mathematical disproofs. See [resources](resources.md) before increasing limits.

## Results and old records

The browser and Markdown report show candidate scope, original-problem coverage, remaining obligations, concrete checks, source gaps and independent formal receipts separately. New reports retain the raw agent verdict/novelty when the gate changes them. Historical checkpoints remain readable and retain their recorded verdicts; missing new evidence is shown as unassessed. Re-run verify to obtain a new assessment under the current policy, rather than silently rewriting history.

Sources and execution receipts stay in the ignored run directory (`literature/` and `verification/`). Development audits belong under the ignored `audits/codex_audits/<timestamp>/`. Curated [showcase results](../showcase/README.md) retain their explicitly documented historical verification scope.

Completed native web searches and identifiable MCP search tool calls can supply observed query receipts. Queries are extracted from tool inputs, not from agent-written search claims. Failed calls and arbitrary shell output do not count. MCP receipts still require independently retrieved primary-source excerpts; they do not certify novelty.
