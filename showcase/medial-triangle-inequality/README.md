# A weighted distance-power inequality in a medial triangle

English | [简体中文](README.cn.md)

[All result samples](../README.md) · [Project overview](../../README.md)

**Expert reports:** [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf) · [中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf). Full bilingual exposition of the saved proof and evidence; editorial organization does not upgrade verification or novelty. [Publication manifest](organized/manifest.json).

This case presents a **complete proof and a successfully checked Lean formalization of Zeng–Fei–Yang's Conjecture 5**, extending the result to the boundary of the medial triangle. The separate AI review found no issues. Novelty remains **UNKNOWN**, so this does not establish the first solution of a currently open problem.

The problem comes from *Tracing the Origins and Generalizations of a Class of Moving Point Inequalities*, volume 19, issue 1 (2026), printed page 51, published online on 2025-11-30. [Publication record](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/view/56) · [Original paper](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/download/56/43)

For a nondegenerate triangle ABC, let a = BC ≥ b = CA ≥ c = AB. Let P lie inside the triangle formed by the three side midpoints, let x, y, z be any positive real numbers, and let n be any positive integer. Then:

```text
x·PAⁿ + y·PBⁿ + z·PCⁿ < max(x,y)·((b+c)/2)ⁿ + max(y,z)·aⁿ
```

The proof combines geometric distance bounds, a strict power-sum bound for every positive integer, and the two maximum-weight factors. The main Lean theorem starts from actual Euclidean distances, side midpoints, and their convex hull; it does not assume the intermediate distance inequalities.

- [Complete mathematical proof and statement correspondence (Chinese original)](proof.md)
- [Separate review summary](review.md)
- [Lean project and reproduction instructions](formal/README.md)
- [Main theorem source](formal/Conjecture5.lean)
- [Verification summary and file hashes](verification.json)

Native solving, independent recompilation, Lean kernel replay, and a separate Lake build all have successful records. A separate AI review compared the original problem with the formal statement, but there is no external mathematics expert certification. Relevant full texts from a 2025 predecessor and a September 2026 follow-up were not obtained, leaving open status and priority uncertain. The stored candidate level remains `SELF_CHECKED`; the actual Lean evidence is recorded separately.
