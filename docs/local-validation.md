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
- Local browser HTTP boundaries, background find/solve/verify, candidate integrity, temporary model overrides, worker recovery across server restarts, and stop/resume.
- Loopback startup, Windows-reserved ports, explicit WSL direct access, and Codex account status, device-code login and explicit account-change boundaries.

Automated backend tests use explicitly identified fake CLIs and `httpx.MockTransport`; they do not consume real model usage. Isolation tests do run real subprocesses. Manual handoff tests cover only the `manual` compatibility backend and do not describe how `chat` works. Use the current command output for test counts and timings. Save any raw test output in ignored directories such as `.mathlottery/`.

## Browser checks

Run `pytest -q tests/test_web.py tests/test_web_startup.py tests/test_web_account.py tests/test_web_artifacts.py tests/test_review_evidence.py` for local HTTP, startup, account, proof-source downloads and background-worker integration checks. They use fake account RPC responses, a scripted Codex executable and real subprocesses, without model calls. Startup checks cover instance reuse, conflicting ports/workspaces, Windows-reserved TCP ranges, runtime project discovery, default loopback access and the explicit WSL direct-access policy.

When using WSL, request the printed Windows `localhost` address from an actual Windows process, such as Windows PowerShell or `curl.exe`. Check the page and an API response using the actual selected port. A Linux-local HTTP success alone does not establish Windows browser reachability. Check `--wsl-direct` separately if using it; it must not be enabled implicitly or alter system networking settings.

For the **MathLottery account** panel, check signed-out, pending, authenticated, cancelled and unavailable states, masked identity fields, official-link validation and the absence of credentials or device codes in browser localStorage. Confirm account errors do not block research history, and that status requests and ordinary sign-in never start research or replace an existing MathLottery login.

Check that Codex submission and continuation require an available ChatGPT login, including after a status refresh fails. The HTTP preflight must reject unsigned, pending, unavailable, API-key-only and unsupported accounts before saving a problem, creating a run or launching a worker. Exercise per-task backend overrides, continuation with a saved backend that differs from current defaults, and a login that disappears between rendering and submission. Chat API tasks must not query Codex authentication. A rejected submission should retain its error, refresh account status and never automatically repeat the request. Existing task records and personal Codex credentials must remain unchanged.

Create synthetic `.lean`, `lean-toolchain` and `lakefile.toml` files under a research or review workspace and verify they appear in **Results** and download as plain text. Check the 1 MB read limit, bounded listing, UTF-8 validation, and rejection of hidden/cache/build paths, traversal, symbolic links and hard links. Swap a parent directory for a symlink between validation and opening to verify that the reader still refuses access. The endpoint must not expose arbitrary run files or change proof levels. Source presence alone is not a Lean result or a certificate of statement equivalence or novelty; a real mathematical audit must separately record the exact formal statement, compiler outcome and trust assumptions.

For review-source handoff, verify that the form selects no files by default and keeps its candidate ID/checksum stable during polling. Submissions must reject a changed candidate, busy source, disallowed path, duplicated selection or oversized bundle before creating a review. After capture, edit or delete the original files and resume the review: its checkpointed contents and hashes must remain unchanged. Test symbolic-link parents during projection, metadata-only HTTP responses, Codex file delivery and actual Chat inline content with its 128 KB limit. A manifest or favorable agent review must not imply complete formal verification or current open status in either language.

Test **Switch account** and **Sign out** against an isolated scripted Codex process, with simulated browser responses. Check that declining confirmation sends no request, the server rejects a missing or false `confirm_account_change` value, and switching invokes official logout before starting device authorization. Exercise successful replacement, explicit sign-out, cancellation and login failure after logout; the latter two must leave the simulated account signed out without restoring credentials. Both languages must describe the workspace's independent login and unchanged local Codex login; using one account still shares its subscription allowance.

Set a fake personal `CODEX_HOME` containing sentinel authentication, configuration and session files, then exercise MathLottery account reads and changes, native research, structured compatibility and workers. Check every Codex child receives the workspace's dedicated `.mathlottery/codex-home` and forced file credential storage; no operation may touch or copy the sentinel files. Verify parent environment preservation, owner-only home permissions, distinct homes for distinct workspaces and no fallback when a personal session is absent from the isolated home. Inspect metadata and continuation paths as well as initial invocation.

Check that running Codex workers and CLI-held run locks in the current workspace block account changes before any logout RPC. Confirm the guard permits changes once those tasks stop. Independent local IDE clients use their separate storage.

Keep real-account checks read-only unless the account owner explicitly chooses to change the login. Mock authorization success establishes UI/protocol behavior only: completing real device authorization requires the account owner's interaction and must be recorded separately. An empty MathLottery home should show signed out even while local Codex is logged in. Read-only `codex login status` in the original environment can verify the local login remains present; it is not the status of MathLottery's separate home. Do not read or log credential contents.

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

## Local experiment audits

Use `audits/codex_audits/<timestamp>/` at the project root as the working directory for each Codex audit, keeping audit scripts, logs, English and Chinese reports, and JSON summaries together. Name new directories `YYYY-MM-DD_HH-MM-SS`; historical reports with only a known date may use `YYYY-MM-DD`. The entire `audits/` directory is ignored by Git. Public documentation links to reusable methods and curated showcase evidence. The [graph pipeline script](../scripts/experiment_graph_pipeline.py) provides a reproducible starting point for new integration experiments.

## Evidence in the showcase

The [result showcase](../showcase/README.md) links to each case's written proof, review summary, verification metadata, and reproduction instructions. These records distinguish public sources, open status, mathematical correctness, and novelty.

The mesh-pattern case has partial Lean verification, the medial-triangle case has a checked full formal statement, and the graph case has an executable finite certificate supporting its written counterexample proof. Read each case's stated scope before interpreting a successful check.
