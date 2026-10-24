# Review summary

English | [简体中文](review.cn.md)

[Case overview](README.md) · [All result samples](../../../../README.md)

The historical separate AI review returned **NO_ISSUES_FOUND**, with novelty assessed as **POTENTIALLY_NEW**. It reviewed an immutable snapshot of the complete written proof. This file summarizes that result; it is not another independent review. See the [verification record](verification.json) for SHA-256 hashes of the original candidate and review report.

The reviewer independently retrieved the original paper's PDF, TeX sources, and version information. It checked the revised four patterns, strict empty-rectangle definitions, and the involution scope for all n and k. Neither the withdrawn v1 statement nor the solved version for all permutations was treated as the target problem.

The mathematical review checked the star/path structure of marked graphs, necessity and sufficiency of external conditions, single-gap nesting of components, preservation of conditions under inner and outer rotations, two-sided inverses for simultaneous rotation, and transposition compatibility for both objects and individual marked edges. It then checked orbit weights on transposition-invariant marked objects, generating-polynomial substitution, coefficientwise equality, and reverse complement. No extra assumptions, circular reasoning, or substantive gaps were found.

Independently written finite challenges all passed:

| Scope | Checks |
| --- | --- |
| All permutations with n ≤ 8 and all applicable marked subsets | 46,234 permutations; 130,354 marked objects on each of the A and B sides |
| All applicable component arrangements with n ≤ 7 | 199,630 arrangements, checking both directions of the external-condition characterization |
| All involutions with n ≤ 11 | 48,928 involutions with matching histograms for the four patterns |

These finite checks search for counterexamples and implementation errors; they do not prove the result for arbitrary n.

The main evidence for novelty is that the authors' 2026-10-11 revision retains the conjecture. [Zhang–Zhao's July paper](https://arxiv.org/abs/2607.04111) solves a related result for all permutations and provides a methodological precedent; the reviewer read its full text. The [follow-up on layered permutations](https://strathprints.strath.ac.uk/97484/) has a narrower scope. The full text of a [related preprint on alternating permutations](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7425138) was unavailable, so unread additional results cannot be excluded. No complete prior solution was identified through 2026-10-21, but worldwide priority is not guaranteed.

The controller later checked 107 Lean theorems and completed kernel replay. The separate written-proof reviewer did not review those formalization files. The global bijection construction is still missing, so the conditional theorem must not be treated as the complete original conjecture. External mathematics expert review and external certification of natural-language/formal-statement equivalence have not been obtained.
