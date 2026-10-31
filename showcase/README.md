# Publication candidates

English | [简体中文](README.cn.md)

[Project overview](../README.md) · [Usage](../docs/usage.md) · [Evidence policy](../docs/evidence.md)

The `ai4math` branch selects three mathematical results for manuscript development. Selection favors a substantive argument, an exact unbounded statement, and useful supporting evidence. It does not certify novelty, expert approval or journal acceptance. The previous general demonstration collection remains in `main` and Git history.

These are historical Solve/Verify/Organize records. They were not regenerated as an
evaluation of the new [supervised Solve workflow](../docs/solve-teams.md). Its supervisor
opinions and proof-board reviews do not retrospectively strengthen the evidence below.

| Result | Potential mathematical contribution | Saved verification | Manuscript role |
| --- | --- | --- | --- |
| [Sun beta polynomials](sun-beta-logconvexity/README.md) | Coefficientwise log-convexity for every row index; explicit positive certificates for weighted convolutions | Complete candidate; final AI review `NO_ISSUES_FOUND`, coverage `FULL`; main Lean declaration replayed; novelty `UNKNOWN` | First priority; main result of a certificate-method paper |
| [Cubic Franel tail](franel-logconvexity/README.md) | Coefficientwise log-convexity from $F_8$, with strict positivity of interior coefficients at central index $n\ge9$ | Complete candidate; AI review `NO_ISSUES_FOUND`, coverage `FULL`; no full Lean proof; novelty `UNKNOWN` | Potential companion application to beta |
| [Mesh patterns on involutions](mesh-involutions/README.md) | Inversion-compatible marked-occurrence transport and orbit weights for four-pattern equidistribution, all $n,k$ | Complete written candidate; AI review `NO_ISSUES_FOUND`; partial Lean only; novelty `POTENTIALLY_NEW` | Separate combinatorics manuscript candidate |

**The initial plan is two possible manuscripts, not three confirmed publications.** Beta and Franel share a proof strategy, but a general theorem covering both still needs to be established. If their commonality is only superficial, reconsider the manuscript structure. The mesh result has a separate combinatorial argument and literature context.

## Start with the reports

| Case | English | 中文 | Source and review |
| --- | --- | --- | --- |
| Beta | [Markdown](sun-beta-logconvexity/organized/report.en.md) · [PDF](sun-beta-logconvexity/organized/report.en.pdf) | [Markdown](sun-beta-logconvexity/organized/report.zh.md) · [PDF](sun-beta-logconvexity/organized/report.zh.pdf) | [Proof](sun-beta-logconvexity/proof.md) · [Review](sun-beta-logconvexity/review.md) · [Lean scope](sun-beta-logconvexity/formal/README.md) |
| Franel | [Markdown](franel-logconvexity/organized/report.en.md) · [PDF](franel-logconvexity/organized/report.en.pdf) | [Markdown](franel-logconvexity/organized/report.zh.md) · [PDF](franel-logconvexity/organized/report.zh.pdf) | [Proof](franel-logconvexity/proof.md) · [Review](franel-logconvexity/review.md) |
| Mesh | [Markdown](mesh-involutions/organized/report.en.md) · [PDF](mesh-involutions/organized/report.en.pdf) | [Markdown](mesh-involutions/organized/report.zh.md) · [PDF](mesh-involutions/organized/report.zh.pdf) | [Proof](mesh-involutions/proof.md) · [Review](mesh-involutions/review.md) · [Lean scope](mesh-involutions/formal/README.md) |

Each case's README gives the exact statement, possible contribution, evidence limits and work needed before submission. Organize reports explain the saved argument; they do not add a new proof review. Historical submission-time statements in proof files are retained alongside subsequent review findings.

## What still separates these results from papers

- **Beta:** independent human examination of the proof and formal statement, recovery of dependency pins, and updated comparison with prior results. A main theorem has a successful historical replay, but statement-equivalence certification remains `NOT_CERTIFIED`.
- **Franel:** recover or reconstruct the missing certificate checkers and record fresh checks; examine the complete tables and boundary arguments. No full formal proof is present.
- **Mesh:** distinguish the involution-specific contribution from the known all-permutations method, resolve the unread related-source gap, and obtain expert review. The 107 checked Lean theorems do not supply the missing global bijection.

The legacy beta and Franel records do not contain assessed structured key-step roadmaps, despite their favorable written AI reviews. A run marked complete, an AI review, finite computation and formal compilation answer different questions. None alone certifies an original mathematical contribution.

Literature judgments are historical: 2026-10-23 for beta/Franel and 2026-10-21 for mesh. This editorial selection on 2026-10-26 performs no new Solve, Verify or priority search. All cases require human responsibility for a manuscript and an accurate account of AI assistance.

## Files and provenance

The collection contains full bilingual Markdown/PDF reports, complete submitted proofs, review summaries, compact evidence records, certificate data and available Lean sources. The beta and Franel publication manifests distinguish original-source hashes from exported-file hashes, record stable identifier aliases and document omitted downloaded article full texts. Their PDFs are regenerated from public Markdown. Mesh retains its previously curated evidence and partial formal project.

Credentials, subscription details, personal paths, runtime sessions, databases, downloaded papers and build caches do not belong in this directory. Original local experiments remain unchanged. Integrity checks authenticate listed file bytes, not mathematics or novelty. See [resource requirements](../docs/resources.md) before reproducing Lean checks; source file size is not a measure of compilation memory.
