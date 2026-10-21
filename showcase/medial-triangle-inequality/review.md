# Review summary

English | [简体中文](review.cn.md)

[Case overview](README.md) · [All result samples](../README.md)

The separate AI review returned **NO_ISSUES_FOUND**; novelty is **UNKNOWN**. This file summarizes the historical review and a subsequent portable build. It does not report a new literature review or expert certification.

The review checked the derivation of actual geometric distance bounds, the positive-integer power-sum bound, the combination of all positive weights, and correspondence between the original problem and formal statement: the Euclidean plane, nondegenerate triangle, side ordering, interior of the midpoint convex hull, arbitrary positive real weights, arbitrary positive integer exponents, and the strict inequality. The result also covers the medial triangle's boundary.

A separate session recompiled all three Lean sources without reusing the solver's compiled modules. Module-by-module kernel replay, fresh replay including all dependencies, and an independent scope check passed. The main theorem's transitive axioms are only `propext`, `Classical.choice`, and `Quot.sound`. A later Lake build in another source directory also passed. Dependency caches left by an earlier interruption initially caused a build failure; retrieving the official cache again allowed the retry to succeed. The successful results did not replace or conceal the failed records.

Full formalization means the supplied Lean statement and proof passed kernel checking. It does not mean external experts have certified equivalence with the natural-language statement, and it does not establish novelty.

Through 2026-10-21, searches found no prior solution covering the complete original problem. However, relevant full texts of a 2025 predecessor and a September 2026 follow-up were unavailable, so overlap cannot be ruled out. A known 2019 upper bound uses different maximum-weight factors; this bound cannot be claimed smaller for every choice of weights. The case therefore demonstrates a complete proof and formal verification, without confirmed priority.

The proof used an unverified approach suggested by the controller to the research session. Those suggestions are not proof assumptions; the key steps are developed in both the written proof and Lean. See [verification.json](verification.json) for validation commands, exit codes, original review summary hashes, and sample file hashes. Raw run logs remain in local archives.
