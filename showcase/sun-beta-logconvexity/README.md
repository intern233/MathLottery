# Sun's beta polynomials: coefficientwise log-convexity

English | [简体中文](README.cn.md)

[Publication candidates](../README.md) · [Project overview](../../README.md)

**First manuscript priority.** This is a complete candidate for a specific conjectured polynomial inequality, with an explicit certificate argument and a historical Lean kernel-replay record. It is the strongest starting point in this collection for a paper on positive certificates for weighted convolutions. Novelty remains **UNKNOWN**; selection for this collection is not a finding of publishability.

## Exact claim

For the formal variable $q$, define

$$
\beta_n(q)=\sum_{k=0}^{n}\binom nk^2\binom{n+k}{k}q^k\in\mathbb Z[q].
$$

The candidate claims

$$
[q^d]\bigl(\beta_{n-1}(q)\beta_{n+1}(q)-\beta_n(q)^2\bigr)\ge0
\qquad(n\ge1,\ d\ge0).
$$

This is coefficientwise nonnegativity with unbounded indices, including every boundary case. Nonnegativity at numerical values of $q$ would be a weaker statement.

The archived original reference is Sun's Conjecture 4.7, first assertion, in [arXiv:1104.3856v8](https://arxiv.org/abs/1104.3856v8). The saved literature review also identifies a dated open-status statement in [arXiv:2505.02767v4](https://arxiv.org/abs/2505.02767v4), dated 2026-02-10. The archive's literature check is from 2026-10-23; this export does not update that search or certify priority.

## What to read

1. [Complete submitted proof](proof.md), including all certificate tables. The proof's original wording is retained; its submission-time status is distinct from later reviews.
2. Expert exposition: [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf) · [中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf).
3. [Review summary](review.md) and [full historical reviews](organized/handoff/candidate-1.review.json).
4. [Lean source and reproduction limits](formal/README.md), [positive-coefficient table](certificates/CertificateTable.md), and [certificate data](certificates/certificates.json).
5. [Expert handoff](organized/handoff/START_HERE.en.md), [evidence index](organized/handoff/index.json), and [verification summary](verification.json).

## Mathematical contribution to develop

The proof converts each coefficient into a symmetric weighted convolution. Two corrections with zero weighted sum cancel central contributions; parity-dependent polynomial identities produce nonnegative terms. The main certificates have 334 and 415 positive coefficients. Boundary cases and coefficients outside the support are addressed separately.

The possible paper contribution is the construction and justification of these certificates for the exact beta weights, together with a readable general method if one can be established. Large coefficient tables, model usage and Lean compilation alone do not establish mathematical significance. The [Franel case](../franel-logconvexity/README.md) has a related strategy and is a candidate companion application; a common theorem has **not** yet been proved in this collection.

## Evidence and remaining work

| Item | Saved evidence |
| --- | --- |
| Solve claim | `COMPLETE` |
| Latest separate AI review | `NO_ISSUES_FOUND`; original-problem coverage `FULL` |
| Stored candidate level | `PARTIALLY_VERIFIED` |
| Formal declaration | `SunBeta.beta_coeffwise_logconvex`; `KERNEL_REPLAYED` |
| Public Lean source | Byte-identical to the source named by the successful receipt |
| External statement-equivalence certification | `NOT_CERTIFIED` |
| Structured key-step coverage | Unassessed in this legacy record; no structured roadmap |
| Novelty | `UNKNOWN`; no external expert review |

Before submission:

- Have a human expert check the coefficient reduction, the two zero-sum corrections, certificate identities and boundaries, and compare the original conjecture with the Lean declaration.
- Recover and record the actual dependency lockfile. The frozen report includes neither `lean-toolchain` nor `lake-manifest.json`; a recorded Lean version does not pin the imported mathlib revision.
- Resolve the specific source-access gap retained in the reviews and update comparisons with the closest prior polynomial log-convexity results. A dated conjecture statement is not proof of present-day priority.
- Explain the certificate construction and its scope in a manuscript; evaluate a common presentation with Franel before deciding whether to split papers.

The first formal attempt failed through memory consumption; later successful replay does not erase that history. No new Lean compilation, mathematical review or literature search was performed for this export. Read [resource requirements](../../docs/resources.md) before attempting compilation.

## Publication copy

[Publication manifest](organized/manifest.json) separates archived source hashes from exported hashes. Reports use stable aliases in place of local task identifiers; PDFs are rendered from the public Markdown. Downloaded article full texts, original PDFs, credentials, sessions and caches are excluded. The original experiment archive is unchanged. Run `python organized/handoff/check_files.py` to check the listed exported bytes; this is an integrity check, not mathematical verification.
