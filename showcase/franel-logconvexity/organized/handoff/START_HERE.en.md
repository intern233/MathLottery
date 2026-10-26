# Expert handoff: start here

This locally generated entry point adds no verification and upgrades no proof or novelty status. Full details remain in the bilingual reports and frozen materials.

[中文报告](../report.zh.md) · [English report](../report.en.md) · [Structured index](index.json) · [Evidence manifest](../source-manifest.json)

**Delivery scope: supplements or additional attachments mentioned in the reports may not be included in this bundle. Check `source-manifest.json` for frozen materials and `handoff/files.json` for actual exported files. A successful integrity check means only that the listed file bytes match; it does not establish that every referenced attachment is present. Missing attachments must be supplied separately with their provenance. This is a delivery boundary, not a new adverse mathematical finding.**

## Check the statement and conclusions first

三次 Franel 多项式从 F\_8 起的逐系数对数凸性

The complete statement, assumptions and sources are in `index.json → problem`; titles and summaries do not replace quantifiers, domains or boundaries.

### 1. candidate-record-002

令 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k。对所有整数 n&gt;=9、d&gt;=0，有 &#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0；更强地，当 1&lt;=d&lt;=2n-1 时该系数严格为正，在 d=0、d=2n 或 d&gt;2n 时为零。因此原题从 F\_8 开始的尾序列逐系数 q-log-convex。

`SELF_CHECKED` · scope `COMPLETE` · review `NO_ISSUES_FOUND` · coverage `FULL` · novelty `UNKNOWN`

[Proof](candidate-1.proof.md) · [All reviews and steps](candidate-1.review.json)

0 proof steps recorded; inspect their dependencies, check IDs and unresolved entries.

Remaining obligations: —

## Formal coverage and reproduction

Formal checking applies only to declarations explicitly listed in the receipts below. Additional equality cases, generalizations or optimality claims need written review unless separately listed. Successful compilation does not certify natural-language/formal equivalence.

1. Extract the complete bundle and run `python handoff/check_files.py` from its root; this checks file integrity only.
2. Inspect `formal_checks` in `index.json` for full declaration types, axioms, source hashes and recorded argv; isolated paths in argv are not directly runnable locally.
3. Inspect captured Lean/Lake dependency files and prepare matching versions in a separate restricted environment before replay. Resolve missing dependency pins or sources first; this is not a one-click replay claim.
4. Check the written proof, Lean declarations and original problem individually. No supplied scripts or Lake hooks are executed automatically.

### Missing reproduction conditions

- No formal execution receipt is recorded; this handoff does not establish Lean verification.

## Novelty and expert review order

Read the proof, check its scope and key steps, then compare the closest prior results individually. `candidate-*.review.json` retains all historical checks and literature obstacles; later review does not erase earlier failures. Record correctness, statement alignment and novelty separately.

Use the separate sanitized text bundle for public sharing. The original evidence bundle preserves bytes and may contain local paths. Redacted source does not inherit the original Lean receipt.
