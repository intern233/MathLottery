# Coefficientwise log-convexity of the cubic Franel tail

English | [简体中文](README.cn.md)

[Publication candidates](../README.md) · [Project overview](../../README.md)

**Companion manuscript candidate.** This complete written candidate has a related positive-certificate strategy to the [Sun beta result](../sun-beta-logconvexity/README.md). Its best initial role is as a second application in a coherent methods paper, subject to expert review and a real common framework. It is not yet a submission-ready theorem, and novelty remains **UNKNOWN**.

## Exact claim

For a formal variable $q$, define

$$
F_n(q)=\sum_{k=0}^{n}\binom nk^3q^k,\qquad
c_{n,d}=[q^d]\bigl(F_{n-1}(q)F_{n+1}(q)-F_n(q)^2\bigr).
$$

The candidate claims, for every integer $n\ge9$ and $d\ge0$,

$$
c_{n,d}>0\quad(1\le d\le2n-1),\qquad
c_{n,d}=0\quad(d=0,\ d=2n,\ \text{or }d>2n).
$$

Thus the tail $(F_n)_{n\ge8}$ is coefficientwise log-convex. **The central index starts at 9, not 8.** The target is the first clause of Conjecture 1.1(i) in [Sun's dated paper, arXiv:2505.02767v4](https://arxiv.org/abs/2505.02767v4), not all polynomial families in that conjecture.

The archived review checked literature on 2026-10-23. The immediately preceding “remains open” phrase in the source concerns the different beta sequence; it must not be reassigned to Franel. Historical problem status is `UNKNOWN`, and unresolved source retrieval and search limits remain visible.

## What to read

1. [Complete submitted proof](proof.md), including the full large-degree and small-degree certificate tables.
2. Expert exposition: [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf) · [中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf).
3. [Review summary](review.md) and [full saved review](organized/handoff/candidate-1.review.json).
4. [Expert handoff](organized/handoff/START_HERE.en.md), [evidence index](organized/handoff/index.json), and [verification summary](verification.json).

The proof retains its original submission-time wording, including references to supplementary checking scripts. Those scripts are **not** present in the frozen report bundle. The explicit coefficient tables are present; there is no claim of a working one-command certificate replay.

## Why this result is selected

Palindromicity reduces the coefficient range. For all $n\ge d\ge16$, two weighted zero-sum identities and four explicit positive polynomials yield a positive-sum formula. Fifteen polynomial identities cover $1\le d\le15$ for unbounded $n$, rather than checking only finitely many values of $n$.

This supplies a second nontrivial use of weighted convolution correction. A useful manuscript would explain how the correction and certificates are constructed, their relationship to the beta argument, and precisely which families the method handles. Shared vocabulary is not a proof of a general theorem, nor a reason by itself to split the results into separate papers.

## Evidence and remaining work

| Item | Saved evidence |
| --- | --- |
| Solve claim | `COMPLETE` for this exact tail statement |
| Separate AI review | `NO_ISSUES_FOUND`; original-problem coverage `FULL` |
| Stored candidate level | `SELF_CHECKED` |
| Lean | No complete formal proof or successful formal execution receipt |
| Structured key-step coverage | Unassessed in this legacy record; no structured roadmap |
| Novelty | Final field `UNKNOWN`; the model's reported `POTENTIALLY_NEW` was not promoted |
| External expert review | None |

Before submission, recover or independently reconstruct the missing certificate checkers and record new results; verify all table entries, normalizations, endpoints and the strictness argument; compare with related polynomial log-convexity theorems; and resolve the explicit literature gaps. Consider Lean formalization after this mathematical and reproducibility review. No new mathematical verification or novelty search was performed for this export.

[Publication manifest](organized/manifest.json) records source hashes, public-file hashes, transformations and omissions. Local task identifiers are replaced by stable aliases and the PDFs are regenerated from the public Markdown. Downloaded article full texts and original runtime files are excluded. Run `python organized/handoff/check_files.py` to check exported-file integrity only.
