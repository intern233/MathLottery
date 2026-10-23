# Result showcase

English | [简体中文](README.cn.md)

[Project overview](../README.md) · [Installation and usage](../docs/usage.md)

This directory presents three complete candidate solutions from local MathLottery experiments: two proofs and one counterexample. Each case includes a readable result, a complete written proof, a review summary, and compact verification records. Cases suited to formal verification also include Lean source files.

Each case documents its public sources, correctness checks, and review limits. Claims about current open status and priority remain limited by the evidence available for each case.

| Case | Mathematical result | Lean verification | Novelty assessment |
| --- | --- | --- | --- |
| [Four mesh patterns on involutions](mesh-involutions/README.md) | Written proof for all n and k | Partial: 107 theorems passed; the global bijection construction is missing | POTENTIALLY_NEW |
| [Medial-triangle moving-point inequality](medial-triangle-inequality/README.md) | Complete proof of Conjecture 5, including the boundary | Full formal statement compiled and passed kernel replay | UNKNOWN |
| [Degree sequences of stepwise irregular graphs](stepwise-irregular-graphs/README.md) | Complete counterexample to Conjecture 1 | Not formalized; includes a finite certificate checker | UNKNOWN |

All three candidates previously received `NO_ISSUES_FOUND` in separate AI reviews. This means those reviews found no substantive gaps; it is not certification by mathematics experts. `POTENTIALLY_NEW` means no complete prior solution was found in the literature checked, so the result may be new. `UNKNOWN` means the available material is insufficient to assess novelty. Literature status reflects checks through 2026-10-21. This collection does not claim three confirmed first solutions to open problems.

Start with each case's README, then read `proof.md`. The review summary explains scope and limitations; `verification.json` records result summaries, source hashes, and historical checks. Each `formal/README.md` describes formalization scope and reproduction commands. The Erdős #885 experiment produced only a partial construction and is not included among these three complete results.

These experiments used native Codex sessions with model `gpt-6-astra` and reasoning effort `max`. The controller helped prepare the environment and some proof approaches; native research and separate review sessions then performed their respective work. These were not entirely unprompted autonomous discoveries. Native solving in the mesh-pattern case stopped because of a usage limit; the controller subsequently extended the Lean work, and that full pipeline did not finish normally.

The collection contains small text files, necessary source code, and counterexample certificates. Toolchains, mathlib, build caches, databases, raw sessions, downloaded papers, and full run logs remain in local experiment archives. Original candidates are unchanged, and each verification summary describes presentation edits.

Guides, case introductions, and review summaries have English and Chinese editions. Proof artifacts retain their original language: English for mesh patterns, Chinese for the triangle inequality and graph counterexample.

Git can track this directory. Its `.gitignore` excludes generated Lean dependencies and build products. Running the Lean reproduction commands downloads toolchains and dependencies separately and may require several GiB; those dependencies are not part of the samples. Before reproducing a Lean case, read [resource requirements](../docs/resources.md) for memory and disk planning, cache reuse and concurrency controls.
