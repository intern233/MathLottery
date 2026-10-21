# Architecture and recovery

English | [简体中文](architecture.cn.md)

[Project overview](../README.md) · [Usage](usage.md) · [Result showcase](../showcase/README.md)

MathLottery separates **what the agent does** from **how the agent is invoked**. Finding, solving and verifying are independent workflows; both Chat API and Codex can execute any of them.

## Research functions

| Workflow | Input | Output and termination |
| --- | --- | --- |
| find | Selection criteria, preferred sources, shortlist target | Ranked reusable problems with provenance and status evidence; stops before solving |
| solve | A registered problem or direct research request | Research progress and immutable candidates; a final candidate ends solving without self-approval |
| verify | A problem and a proof or candidate | Independent truth, proof and novelty assessments; every review verdict ends the audit |
| pipeline | Optional problem or direct request | Find when needed, solve, independently review, return feedback to the same researcher |

The CLI commands find, solve and verify set an explicit Workflow on the run. run composes the pipeline. Workflow and Phase are separate: the former is the user's requested function, the latter is the current stage. A resumed task retains its workflow.

## Components

| Module | Responsibility |
| --- | --- |
| workflows.py | Function-specific instructions and ranked discovery results |
| agent_backend.py | Common research transport interface and backend selection |
| chat_backend.py | Automatic Responses API calls, hosted tools, context continuation, polling and cancellation |
| native_backend.py | Official Codex CLI, exact session continuation, native tools and event logs |
| native.py | Shared milestones, persistent receipts and workflow transitions |
| native_prompts.py | Research objectives and milestone registration, without a per-action protocol |
| orchestrator.py | Run creation, compatibility dispatch, pause/resume, candidate integrity |
| storage.py, budget.py, reporting.py | Checkpoints, limits, per-workflow results and evidence |
| models.py, auditor.py | Domain types, immutable candidates and conservative verification levels |
| backends.py, prompts.py, tools.py | Legacy structured execution and manual handoff |
| sources.py | Source adapters and evidence checks for open status |

## Agent transports

Codex starts with codex exec and continues the exact session using codex exec resume. It inherits user model/tool configuration, with explicit authentication, sandbox, network and single-agent settings. The researcher controls methods and tool use. No per-action output schema or legacy tool registry is imposed on native research.

Chat creates background Responses API requests with a configured model and hosted tools. The default tools are web_search and Code Interpreter; ordinary Markdown answers may contain a single machine-readable milestone at the end. Requests use previous_response_id to retain the research context. Reviewer responses form a different chain. No browser, cookie extraction or manual copying is involved.

Chat API credentials are read from an environment variable, never from Codex login storage or request files. API errors do not trigger a switch of backend or billing. Chat model selection must be explicit through configuration, a CLI option or OPENAI_MODEL. API-native tool execution is server-hosted; client-executed custom function tools are not implemented.

The Python harness saves answers and response metadata locally. Hosted containers and remote response history have provider retention limits; local checkpoints do not recreate expired remote contexts. Codex similarly needs its original session storage for exact continuation.

Manual handoff is an explicitly named compatibility backend. work aliases codex, and --mode aliases --backend. Saved pre-migration chat runs are loaded as manual, so upgrading cannot silently convert them to API billing.

## Discovery and evidence

A selection milestone contains the recommended Problem and an ordered shortlist. Each problem records its statement, source, status assessment, difficulty, verification feasibility and selection reason. Discovery saves the ranking and raw agent assessment in literature/selection.json and saves reusable problems in the local problem library.

Open-status evidence is checked against source URLs reported by backend tools. Unsupported status assertions remain UNKNOWN in the problem library; the original proposal is retained in the selection artifact. The existing conservative policy requires recent evidence from at least two domains, including the problem's primary source. Even supported status is an agent assessment, not certification.

## Review

Every candidate gets a fresh reviewer context and a separate writable workspace. Only the problem, candidate content and references enter the initial review prompt; solver history and prior reviews are excluded. Codex reviewer memories are disabled. Instructions prohibit reading solver files, but workspace-write is not a complete read boundary.

Independent verify tasks end after any verdict, including INCONCLUSIVE. The pipeline instead returns unsuccessful reviews to the original researcher. A passing partial result also continues unless designated as the final deliverable. Independent solve saves candidates without launching review.

Candidates retain their claim, assumptions and references when imported for a new audit. A checksum protects the stored claim and proof. Model approval and finite experiments never become FORMALLY_VERIFIED or EXPERT_REVIEWED.

## Persistence and recovery

SQLite is authoritative. Runs snapshot their workflow, backend, strategy, settings, problems, candidates and separate Codex session / Chat response identifiers. Reports and other artifacts are projections.

The active attempt is committed before invocation. Codex session identifiers are recorded immediately when reported. Chat saves the response object, including its identifier, as soon as it is received. A durable result receipt is queued before accounting and milestone application.

If a runner crashes after an API response was saved, recovery retrieves that response or replays its terminal local result; it does not create a second response. Pending background calls are accounted when their terminal result arrives. A failed creation with no known response ID is kept unresolved, since automatically retrying could duplicate work.

Ctrl+C, timeout and stop request server-side cancellation for Chat. Cancellation failures preserve the pending attempt for recovery. A stop issued after a connection failure also attempts to cancel detached remote work. Codex interruption stops its subprocess group; recovery identifies orphan processes before signalling them. No unrelated process or session is selected.

Switching transports while an invocation is pending is rejected. Otherwise each transport retains its own continuation identifiers, and recorded research answers from the other transport are imported. An additional direction arriving during recovery is preserved for the following turn.

## Budgets and verification

Time budgets count active research time; paused and manual waiting time is excluded. Rounds count research handoffs, not native tool calls. Token limits use actual backend reports and are checked between calls; a single call may exceed a threshold.

API dollar costs, subscription balance and third-party services are not metered. A legacy max_external_cost_usd value of zero blocks Chat API calls; null delegates spending control to the provider account. No backend fallback bypasses this setting.

Contract tests use a mock Responses transport and a scripted Codex executable. They verify orchestration and recovery, not mathematical ability. Real model evaluations require configured credentials and a separately chosen research budget.

For setup and commands, see [installation and usage](usage.md). The [validation guide](local-validation.md) covers reproducible checks; the [showcase](../showcase/README.md) presents research outputs and their evidence limits.
