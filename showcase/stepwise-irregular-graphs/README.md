# A counterexample to the stepwise irregular degree-sequence conjecture

English | [简体中文](README.cn.md)

[All result samples](../README.md) · [Project overview](../../README.md)

This case presents a **complete counterexample to Conjecture 1** in Bera–Paul–Subramanian's *Some properties of stepwise irregular graphs*. The separate AI review returned **NO_ISSUES_FOUND**. Novelty is **UNKNOWN**, and there is no Lean formalization.

The paper appeared in EJGTA 14(1) (2026). The conjecture is on printed page 223; the simple-connected-graph convention and SI definition are on page 216. [Original paper](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357)

An SI graph requires the degrees at the ends of each edge to differ by exactly 1. The counterexample degree sequence is:

```text
(6,6,6,6, 5,5,5,5,5,5, 4, 3, 2,2,2, 1)
```

It satisfies every premise of the original conjecture and has an ordinary simple connected bipartite realization, but no SI realization. The three degree-2 vertices would require 6 incident edges to vertices of degree 1 or 3, whose total degree is only 4—a contradiction. This rules out every SI realization, independently of finite search and without requiring connectivity.

- [Complete counterexample proof and adjacency list (Chinese original)](proof.md)
- [Machine-readable 16-vertex certificate](certificate.json)
- [Certificate checker using the Python standard library](verify_certificate.py)
- [Separate review summary](review.md)
- [Verification summary and file hashes](verification.json)

With Python 3.11+, check the finite certificate from this directory:

```sh
python verify_certificate.py certificate.json
```

Expected results are 16 vertices, 34 edges, odd- and even-degree sums of 34 each, and an SI incidence demand of 6 exceeding the available neighboring degree sum of 4. The program checks integer relations and explicit graph data; the written proof establishes universal non-realizability.

The separate review found a 2022 precedent for the local capacity inequality. Some recent related full texts were inaccessible, so priority for refuting this conjecture cannot be confirmed. The stored candidate level remains `SELF_CHECKED`.
