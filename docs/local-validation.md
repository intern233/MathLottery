# Validation methods and scope

English | [简体中文](local-validation.cn.md)

[Project overview](../README.md) · [Usage](usage.md) · [Result showcase](../showcase/README.md)

This guide provides reusable validation steps. Machine paths, account information, real session IDs, and raw run logs stay in ignored local run directories, outside repository documentation.

## Automated checks

From the MathLottery project root, with development dependencies installed:

```bash
conda activate mathlottery
pytest -q
ruff check .
python -m compileall -q src
python -m pip check
```

Tests cover both native and structured execution, including:

- Exact session continuation, ordinary Markdown handoffs, and feedback across execution modes.
- Independent termination of find, solve, and verify, and the full pipeline composed by run.
- Chat Responses API request bodies, hosted tools, persistent research context, and separate review context.
- Model and Max settings on Codex session continuation, separate Chat Pro/standard parameters, and CLI overrides across research commands.
- Chat background polling, connection recovery, remote cancellation, actual usage fields, and credentials never being written to disk.
- Separate reviews, further research after inconclusive verdicts, and continued exploration after a partial result passes.
- Interruptions, rate limits, budgets, receipt recovery, and orphan subprocess identification.
- Candidate proof integrity, path isolation, and run metadata.
- Offline mathematical experiments, literature source adapters, and missing optional formal verification tools.

Automated backend tests use explicitly identified fake CLIs and `httpx.MockTransport`; they do not consume real model usage. Isolation tests do run real subprocesses. Manual handoff tests cover only the `manual` compatibility backend and do not describe how `chat` works. Use the current command output for test counts and timings. Save any raw test output in ignored directories such as `.mathlottery/`.

## Offline workflows

```bash
mathlottery demo
mathlottery demo --case incorrect
mathlottery demo --case hidden-assumption
mathlottery demo --case finite-only
```

These cases cover a correct proof, division by zero, missing assumptions, and replacing a general proof with finite tests. Demo reviews are fixed test fixtures, not evidence that a model can detect arbitrary mathematical errors.

## Real Codex integration checks

Start with `mathlottery doctor` to check the executable, ChatGPT login, and local tools. Diagnostic output is for local troubleshooting and should not be copied into public documentation.

Import the educational example and run it with an explicit budget:

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --backend codex --problem odd-sum --budget-time 3m --max-iterations 5
```

Use the run ID printed by the command to inspect its report:

```bash
mathlottery status <run-id>
mathlottery report <run-id> --show
```

Check that candidate proofs were saved and that model information, tool calls, and token usage come from actual run records. `solve` does not launch a review. Verify its candidate separately:

```bash
mathlottery verify --backend codex --from-run <solve-run-id> --budget-time 3m
```

Check that the review uses a separate session without inheriting the solver's trajectory. A favorable LLM review establishes at most `SELF_CHECKED`, not a formal proof.

Next, check continuation of the same research session:

```bash
mathlottery resume <run-id> --message 'Check the n=0 boundary case and preserve existing research results' --budget-time 6m --max-iterations 10
```

Budget arguments set new total limits. Compare research session IDs before and after resuming, and confirm that files remain readable. Native shell, web search, and workspace write boundaries can be checked separately in controlled integration tasks. Do not bypass the sandbox to make a check pass.

Reports and raw events are in `runs/<run-id>/`; the database is in `.mathlottery/`. These are local artifacts excluded from the repository. Real calls use the account's subscription allowance. Results and usage need not reproduce word for word.

## Validation limits

Real Chat API checks require an API key and model configuration; see [installation and usage](usage.md). Change the backend in the commands above to `chat`, then use `find` to inspect selection results and status evidence. Automated HTTP contract tests do not establish that a real account has access to a model, search, or code execution.

Historical integration checks covered native shell, file persistence, exact session continuation, web search, candidate submission, and separate review. They establish that the execution path works. They are not comparative evaluations of mathematical ability against ChatGPT Pro or native Codex, and do not establish that an open conjecture was solved.

Optional tools such as Lean must be installed separately. Missing tools or external evidence must be recorded as unavailable or unverified, never as a pass.

## Evidence in the showcase

The [result showcase](../showcase/README.md) links to each case's written proof, review summary, verification metadata, and reproduction instructions. The [2026-10-21 audit](../showcase/audit-2026-10-21.md) distinguishes public sources, open status, mathematical correctness, and novelty.

The mesh-pattern case has partial Lean verification, the medial-triangle case has a checked full formal statement, and the graph case has an executable finite certificate supporting its written counterexample proof. Read each case's stated scope before interpreting a successful check.
