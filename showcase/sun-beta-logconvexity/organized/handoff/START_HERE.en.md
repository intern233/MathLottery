# Expert handoff: start here

This locally generated entry point adds no verification and upgrades no proof or novelty status. Full details remain in the bilingual reports and frozen materials.

[中文报告](../report.zh.md) · [English report](../report.en.md) · [Structured index](index.json) · [Evidence manifest](../source-manifest.json)

**Delivery scope: supplements or additional attachments mentioned in the reports may not be included in this bundle. Check `source-manifest.json` for frozen materials and `handoff/files.json` for actual exported files. A successful integrity check means only that the listed file bytes match; it does not establish that every referenced attachment is present. Missing attachments must be supplied separately with their provenance. This is a delivery boundary, not a new adverse mathematical finding.**

## Check the statement and conclusions first

Sun 的 beta 多项式逐系数对数凸猜想（Conjecture 4.7 第一项）

The complete statement, assumptions and sources are in `index.json → problem`; titles and summaries do not replace quantifiers, domains or boundaries.

### 1. candidate-record-002

对每个整数 n≥0，令 beta\_n(q)=Σ\_{k=0}^n binom(n,k)^2 binom(n+k,k)q^k∈Z&#91;q&#93;。对所有整数 n≥1 和 d≥0，都有 &#91;q^d&#93;(beta\_{n-1}(q)beta\_{n+1}(q)-beta\_n(q)^2)≥0。完整 Lean 主定理为 SunBeta.beta\_coeffwise\_logconvex，单一源文件 proof/SunBeta.lean。本主张是覆盖原题全部量词的候选证明，不是独立 Verify 的结论。

`PARTIALLY_VERIFIED` · scope `COMPLETE` · review `NO_ISSUES_FOUND` · coverage `FULL` · novelty `UNKNOWN`

[Proof](candidate-1.proof.md) · [All reviews and steps](candidate-1.review.json)

0 proof steps recorded; inspect their dependencies, check IDs and unresolved entries.

Remaining obligations: —

## Formal coverage and reproduction

Formal checking applies only to declarations explicitly listed in the receipts below. Additional equality cases, generalizations or optimality claims need written review unless separately listed. Successful compilation does not certify natural-language/formal equivalence.

- candidate-record-002 / review 1: `ERROR`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

- candidate-record-002 / review 2: `KERNEL_REPLAYED`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - SunBeta.beta\_coeffwise\_logconvex

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

- candidate-record-002 / review 3: `KERNEL_REPLAYED`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - SunBeta.beta\_coeffwise\_logconvex

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

1. Extract the complete bundle and run `python handoff/check_files.py` from its root; this checks file integrity only.
2. Inspect `formal_checks` in `index.json` for full declaration types, axioms, source hashes and recorded argv; isolated paths in argv are not directly runnable locally.
3. Inspect captured Lean/Lake dependency files and prepare matching versions in a separate restricted environment before replay. Resolve missing dependency pins or sources first; this is not a one-click replay claim.
4. Check the written proof, Lean declarations and original problem individually. No supplied scripts or Lake hooks are executed automatically.

### Missing reproduction conditions

- No lean-toolchain file was captured; consult the receipt's recorded Lean version.

- No lake-manifest.json was captured; imported library revisions are not pinned by this handoff.

## Novelty and expert review order

Read the proof, check its scope and key steps, then compare the closest prior results individually. `candidate-*.review.json` retains all historical checks and literature obstacles; later review does not erase earlier failures. Record correctness, statement alignment and novelty separately.

Use the separate sanitized text bundle for public sharing. The original evidence bundle preserves bytes and may contain local paths. Redacted source does not inherit the original Lean receipt.
