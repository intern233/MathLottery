# Architecture and recovery

English | [简体中文](architecture.cn.md)

[Project overview](../README.md) · [Usage](usage.md) · [Result showcase](../showcase/README.md)

MathLottery separates the **entry point** (browser or terminal), **workflow** (Find, Solve, Verify, Organize or the research pipeline), and **agent connection** (Codex or a configured Responses provider). Both entry points use the same orchestrator and workspace state. For setup rather than implementation details, start with [usage](usage.md) and [configuration](configuration.md).

## Research functions

| Workflow | Input | Output and termination |
| --- | --- | --- |
| find | Selection criteria, preferred sources, shortlist target | Ranked reusable problems with provenance and status evidence; stops before solving |
| solve | A registered problem or direct research request | Immutable candidates and progress; supervised mode reviews researcher signals before continuing or closing, without upgrading independent verification |
| verify | A problem and a proof or candidate | Independent truth, proof and novelty assessments; every review verdict ends the audit |
| organize | An idle run with at least one recorded candidate review and optional instructions | Chinese and English expert reports in Markdown and PDF, with a frozen material manifest; no evidence upgrade |
| pipeline | Optional problem or direct request | Find when needed, solve, independently review, return feedback to the same researcher |

The CLI commands find, solve, verify and organize set an explicit Workflow on the run. run composes Find/Solve/Verify without automatically organizing. Workflow and Phase are separate: the former is the user's requested function, the latter is the current stage. A resumed task retains its workflow.

Standalone Find stops at its shortlist so the user can choose a problem. The CLI's `run` command opts into automatic research-stage transitions and does not add this selection pause. The browser exposes Find, Solve, Verify and optional Organize as separate operations.

Find records the original wording, the target's scope relative to that wording, known partial results and explicit statement risks. `find/risks.py` projects missing evidence and ambiguities onto both shortlist cards and the Solve selection preview. These are selection disclosures, not semantic certification. Nonempty disclosures are bound into the frozen Find dossier; legacy records remain explicitly unassessed.

Standalone native Solve with `solve.coordination: supervised` and explicit parallelism (including 1) dispatches to `solve/campaign.py`. `campaign_receipts.py` applies signals and exact-version supervisor reviews once; `contracts.py` defines milestone evidence, and `board_reviews.py` invalidates dependent opinions. The scheduler closes admissions at its time budget and drains in-flight research before final supervision. `providers/response_tools.py` provides durable function continuations for the run-scoped `solve/board_tools.py` capabilities. Null parallelism retains native delegation; old checkpoints retain `allocation`. The composed `run` does not enter this scheduler. See [supervised Solve](solve-teams.md).

## Source layout and boundaries

The top level contains package entry points, configuration and the public model exports. Implementations live in packages grouped by responsibility. Add behavior in the package that owns it, then connect it through the existing entry point.

```text
src/mathlottery/
├── __init__.py           # Package identity and version
├── __main__.py           # python -m mathlottery entry point
├── config.py             # Shared configuration contracts and loading
├── models.py             # Public exports of domain types
├── cli/                  # Command registration, workspace, research, tasks and exports
├── domain/               # Problems, literature, proofs, protocols, sessions and runs
├── find/                 # User selection, frozen discovery context and statement risks
├── solve/                # Supervised lifecycle, legacy allocation, proof board, receipts and prompts
├── verify/               # Candidate integrity, proof/source assessments and formal checks
├── organize/             # Frozen dossiers, expert handoff, downloads and PDF/assets
├── runtime/              # Workflow lifecycle, native/structured loops, budgets and resources
├── providers/            # Agent transports, isolated identity, metadata, network and catalog
├── storage/              # SQLite checkpoints and confined artifact I/O
├── tooling/              # Source adapters, tool registry and isolated Python worker
├── telemetry/            # Activity, usage metrics, search traces and research reports
└── web/                  # Local HTTP, service operations/queries, workers and static UI
```

`domain/` depends only on Python/Pydantic and other domain modules. CLI and HTTP code call the shared orchestrator; neither implements a second research loop. `WebService` composes query and operation objects: operations return saved runs, and queries format them for display. The Solve coordinator composes allocation, attempt, prompt and board components; transport threads return receipts while the coordinator owns checkpoint mutations.

Proof-file access lives in `verify/artifacts.py`, shared by core review and the browser; verification does not import the Web layer. Package initializers remain lightweight so importing a utility does not initialize the research loop. Resources stay with their consumers: the trusted Lean inspector is in `verify/lean_inspector.lean`, KaTeX assets are in `organize/assets/`, and the isolated Python worker is beside its launcher in `tooling/`.

The browser loads explicitly allowlisted scripts without a build step. `app.js` connects workflow forms and history to the API; `i18n.js` owns translations, `dom.js` owns safe DOM helpers, and account/model controllers keep their own state behind small callback interfaces. `solve-teams.js` renders a supplied run without owning task execution.

The separate `/agents` page edits local connection profiles through `web/agent_roster.py` and `providers/agent_roster.py`. Selecting the roster for Solve copies it into the run configuration. `solve/routes.py` binds each researcher to that snapshot, independently of group allocation; per-attempt transport metadata controls session continuation, recovery and event-file selection. Account RPC and Codex research use the same named identity. Responses credentials are read from environment variables, never from the roster or browser.

The CLI entry point remains `mathlottery.cli:app`; commands, configuration and saved JSON retain their contracts. `mathlottery.models` remains the public model export, and the `mathlottery.storage` package exports `Store` and its existing file helpers. Internal Python imports use the new implementation paths, such as `mathlottery.runtime.orchestrator` and `mathlottery.providers.identity`; integrations importing moved modules must update those paths. Solve exports are available from `mathlottery.solve` and `mathlottery.solve.board`, without extra top-level forwarding files. New domain fields still require explicit checkpoint compatibility handling.

## Components

| Module | Responsibility |
| --- | --- |
| cli/ | Command registration, shared options, workspace setup, workflow commands and exports |
| web/server.py, web/static/ | Local HTTP boundary, packaged browser interface and polling |
| web/service.py | Composes browser operations and queries behind the public service API |
| web/requests.py, web/settings.py | Validated inputs, configuration overrides and browser-safe settings |
| web/operations.py, web/queries.py | Workflow commands and read-only research-state projections |
| web/jobs.py, web/worker.py | Detached execution, worker ownership locks and stop propagation |
| web/startup.py, web/network.py | Workspace discovery, port reuse/fallback, Windows reservations and explicit WSL access policy |
| web/account.py | Official Codex account RPC over private stdio, masked status, device-code sign-in and explicit account changes |
| providers/catalog.py, web/model_directory.py | Provider metadata, bounded model discovery, capability validation and isolated Codex model-list RPC |
| providers/identity.py | Workspace-specific Codex home, child environment and file credential storage |
| runtime/workflows.py | Function-specific instructions and ranked discovery results |
| providers/registry.py | Common research transport interface and backend selection |
| providers/chat.py | Automatic Responses API calls, hosted tools, context continuation, polling and cancellation |
| providers/codex.py | Official Codex CLI, exact session continuation, native tools and event logs |
| providers/metadata.py | Whitelisted runtime metadata and reconciliation of cumulative token counters |
| runtime/native.py | Native research loop and find/solve/review/organize transitions |
| solve/ | Optional bounded research groups, supervision, shared board and durable recovery |
| solve/campaign.py, solve/campaign_receipts.py | Event-driven scheduling, researcher signals, supervisor decisions and once-only receipt consumption |
| solve/board.py, solve/board_reviews.py, solve/contracts.py | Immutable proof publications, dependency graph, version-bound opinions and structural validation |
| solve/board_tools.py, providers/response_tools.py | Scoped live board functions and durable Responses function continuations |
| runtime/attempts.py | Invocation journal, durable receipts, session IDs, accounting and recovery |
| runtime/workspace.py | Research/review/organization workspaces, prompt preparation and complete imported answers |
| runtime/milestones.py | Transport-independent milestone parsing and validation |
| verify/candidates.py | Immutable candidate artifacts, integrity checks and separate review projections |
| organize/workflow.py | Frozen source dossiers, editorial report acceptance and reproducible exports |
| organize/downloads.py, organize/pdf.py | Safe report download projections and optional local PDF rendering |
| runtime/prompts.py | Research objectives and milestone registration, without a per-action protocol |
| runtime/orchestrator.py | Run lifecycle, execution dispatch, pause/resume and stop |
| runtime/structured.py | Legacy JSON/tool loop, accepted-response replay and manual submissions |
| telemetry/metrics.py | Measured stage returns, handoff failures, timings and review outcomes |
| storage/core.py, runtime/budget.py, telemetry/reporting.py | Checkpoints, limits, per-workflow results and evidence |
| domain/, models.py, verify/auditor.py | Domain contracts, compatibility exports and conservative verification levels |
| providers/base.py, runtime/structured_prompts.py, tooling/registry.py | Legacy structured execution and manual handoff |
| tooling/sources.py | Source adapters and evidence checks for open status |

## Code flow

```mermaid
flowchart TD
    Browser[Local browser] --> Web[WebService: validate inputs and read state]
    Web --> Worker[Background worker]
    Worker --> Engine
    CLI[CLI + configuration] --> Engine[Orchestrator: create / resume / drive]
    Engine --> Native[NativeRunner]
    Engine --> Legacy[StructuredRunner: compatibility]
    Native -->|Original workflows| Workspace[NativeWorkspace: prepare context]
    Native -->|Supervised standalone Solve| Campaign[SolveCampaign: signals and scheduling]
    Campaign <--> Supervisor[Supervisor: plan and review]
    Campaign <--> Researchers[Research attempts: persistent sessions]
    Campaign <--> Board[SolveBoard: proofs and review versions]
    Campaign --> Report
    Workspace --> Journal[NativeAttempts: persist active attempt]
    Journal --> Backend[Codex session or Chat response chain]
    Backend --> Receipt[Persist and queue receipt]
    Receipt --> Milestone[Validate milestone]
    Milestone --> Find[Selection: save ranked problems]
    Milestone --> Solve[Candidate: save immutable content]
    Milestone --> Review[Review: save separate assessment]
    Milestone --> Organize[Organize: save expert exposition]
    Find --> Native
    Solve --> Native
    Review --> Native
    Organize --> Native
    Native --> Report[Checkpoint, report and metrics]
```

1. The CLI resolves configuration and inputs. `Orchestrator.create` records the workflow and initial phase; `drive` locks the run and selects the native or compatibility runner.
2. `NativeWorkspace.prepare` checks the candidate before review, writes task inputs, and prepares the prompt. Research keeps its original session; each candidate starts a separate reviewer context. Imported answers retain their full visible content.
3. `NativeAttempts.invoke` commits the active attempt before calling a transport. Session IDs are saved as soon as they arrive. It persists the result receipt before `queue` accounts for a terminal response.
4. `NativeRunner.apply` consumes the receipt, records tool-observed sources, and dispatches a validated milestone to selection, candidate storage or review. An unsuccessful review returns to the existing research session; standalone workflows retain their own stop rules.
5. The new checkpoint is committed before generating reports. Recovery consumes saved receipts before considering another model call. `StructuredRunner` retains the old accepted-response/tool-result replay path without imposing it on native agents.

`Store` is shared infrastructure; it does not decide research strategy. `CandidateStore` owns candidate integrity and review artifacts, while `NativeAttempts` owns transport recovery. Neither module selects mathematical methods for the researcher.

For supervised Solve, `SolveCampaign` reuses `SolveCoordinator` for routes, workspaces and durable attempts, but handles each completed researcher receipt as an event. The supervisor sees the original target, signals and proof board, audits complete claims and proposes another assignment when needed. Running peers keep their sessions and objectives. Supervision waits for the primary slot to be idle and can then run alongside other peers. The scheduler reserves call capacity for final supervision and closes admissions at the active-time deadline; it does not cancel researchers to meet that deadline. Accepted complete claims may close early unless full-budget exploration is enabled. Legacy `allocation` tasks retain their round-based scheduler.

`SolveCampaign` checkpoints preserve acknowledged signals, planned dispatches and exact candidate reviews. The SQLite board stores immutable publications and append-only review records; `bulletin/` files are projections. Proof dependencies, review versions and outstanding objections determine whether an opinion is still applicable. `solve/summary.md` and `solve/supervision.json` record the outcome; supervisor opinions never populate independent Verify reviews. The [Solve guide](solve-teams.md) details the protocol and its limits.

For automatic turns, a missing milestone is a recoverable handoff error: the next prompt requests registration of the saved result, rather than silently treating an unregistered answer as ordinary progress. Codex primarily submits a workspace JSON file; if it omits that file, one explicit fenced `mathlottery` block in the answer is also accepted. Both routes validate current task IDs and payloads. An invalid existing file is never bypassed by choosing an answer block. Manual answers may still omit milestones.

## Local browser execution

`mathlottery serve` starts a local HTTP server with bundled HTML, CSS and JavaScript. Startup locates an editable checkout, honors explicit workspace selection, reuses a matching service through a bounded instance probe, and tries another port for incompatible listeners. On WSL, it also skips Windows-reserved TCP ranges when they can be queried. It binds before initializing storage and prints the actual workspace and address. The default listener remains `127.0.0.1`, with Windows access through WSL localhost forwarding. Only explicit `--wsl-direct` enables the NAT-mode WSL interface and its Windows gateway peer allowlist. `--loopback-only` preserves the default behavior. No WSL, proxy, port-forwarding or firewall settings are changed.

The browser uses JSON endpoints for task creation, stop, resume and status. The server validates the peer, host, origin and write token, limits request bodies, and serves only an explicit asset/API allowlist. It does not expose a general filesystem browser. Untrusted problem, proof and agent text is inserted using DOM text nodes.

`web/account.py` opens a bounded, private stdio RPC connection to official `codex app-server`. Separate account endpoints read status, start device-code authorization, cancel a pending login, switch accounts and sign out. Account operations never create a research thread or start a model turn. Status reads and ordinary sign-in reuse an authenticated MathLottery account without automatic switching. Explicit switch and sign-out requests require `confirm_account_change: true`, in addition to the usual browser write checks; the UI explains the change applies to the current MathLottery workspace.

Every MathLottery Codex child process receives a dedicated `CODEX_HOME` and an explicit `cli_auth_credentials_store="file"` override. Default subscription calls use `.mathlottery/codex-home`; named subscription slots use `.mathlottery/codex-accounts/<slot-id>`. API authentication has separate homes described under Agent transports. Research, metadata reads and recovery use the exact selected identity. Homes are Git-ignored and created with owner-only permissions on POSIX. The parent's environment is not mutated; personal Codex credentials, configuration and sessions are never copied or selected as a fallback. Ordinary Codex CLI / IDE clients and ChatGPT website sessions retain their own login state. See the official [environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables), [authentication](https://learn.chatgpt.com/docs/auth) and [app-server](https://learn.chatgpt.com/docs/app-server) documentation.

Switching calls official `account/logout` before starting new device-code authorization. Cancelling or failing that authorization leaves the MathLottery home signed out. MathLottery neither backs up credentials nor silently restores the old account. Sign-out clears only this workspace's login without changing personal Codex storage or browser cookies. A user may sign in with the same ChatGPT account in multiple places; separate login storage does not create separate subscription quotas.

The service blocks switch and sign-out while a Codex task is running in the current workspace, checking worker and orchestrator ownership locks. Browser task creation/resume and account changes share a mutation lock so a browser task cannot start between the check and the account change. Independent local IDE sessions use different storage and are outside this workspace's task checks.

Official Codex owns credentials in the dedicated ignored home. Account responses expose only the account type, masked email and plan, plus an official verification URL and one-time code while login is pending. MathLottery keeps this response state in memory, validates the verification URL, and sends no passwords or tokens to the frontend. Account loading is separate from research bootstrap, with polling only while authorization is pending. This connects the Codex backend; the current Chat backend continues to read its API key from the environment.

`WebService` validates inputs with Pydantic, snapshots configuration through `Orchestrator.create`, and uses `CandidateStore.check` before importing a candidate for independent review. A `web.worker` process executes `drive` or `resume`; it does not add a second research loop. SQLite remains authoritative, and CLI runs are visible in the same UI.

`verify/evidence.py` captures explicitly selected proof sources while holding the idle source run's ownership lock: Lean files and supported small proof texts, certificates and scripts. The browser binds its request to the displayed candidate ID and SHA256. The new review checkpoint stores the bounded source contents, provenance and hashes separately from the immutable candidate; polling exposes only the manifest. Native Codex projects this evidence through directory descriptors without following symbolic links, and resumes restore the checkpointed bytes. Native Chat receives the same source contents inline under a smaller size limit. Neither attachment path includes solver history or prior verdicts. Attaching a file alone does not execute it or promote the proof level; see [attachment scope and independent Lean checks](evidence.md#independent-lean-receipts).

The browser groups Solve/Verify/Organize attempts by problem. A Find run joins the selected problem's history through its explicit discovery linkage; an unselected shortlist remains separate. When several problems share a Find run, history marks the shared source and global counts still count that run once. Search and task-status filters help navigate history; older attempts are expandable. A finished process is distinct from a correct proof: results expose the solver's claimed scope, proof checks, original-problem coverage and novelty separately. Polling preserves expanded sections and the current form choices.

Each worker inherits an OS ownership lock held across startup and execution. It survives server restarts, rejects duplicate browser resumes, and also respects the core run lock used by the CLI. Stop markers are propagated during startup/resume so a queued resume cannot discard a browser stop request. Worker status and logs live in the ignored run directory. Closing the UI leaves workers running; explicit stop preserves the normal recovery path. A dead worker is never automatically relaunched.

## Provider and model selection

A provider profile is separate from the research workflow and transport. The built-in `codex` profile uses official Codex sessions; `chat` uses the existing Responses configuration. Optional `model_providers` profiles select the Responses transport with an explicit endpoint, API-key environment-variable name, tools and optional model-capability declarations. `backend.provider` records the chosen ID. Find, Solve, Verify and Organize use the same selection mechanism.

`GET /api/models?provider=<id>` returns a public directory projection: provider labels and transport types, model IDs, descriptions and declared reasoning options. `refresh=1` bypasses the short-lived cache. Codex subscription discovery calls official `model/list` through the workspace's isolated app-server; Codex API authentication uses configured/manual model IDs without a subscription lookup. Responses discovery calls the selected endpoint's `/models`. Neither creates a research thread or an inference request. A custom profile with configured model entries uses that directory without remote discovery; unknown model IDs remain usable. Missing capability metadata stays unknown; it is not converted into an unsupported capability. The directory is not an account-entitlement, quota or tool-compatibility check.

The browser submits only the selected profile ID and task overrides. The server resolves the profile, validates declared capabilities and snapshots the effective settings in the new run before launching the existing worker. Endpoints and key-variable configuration are server-side; API-key values are read from the environment and never saved in task configuration. Browser continuation retains the saved settings, so a later profile edit cannot silently redirect an existing remote conversation. Selection does not mutate global configuration or any Codex login.

Catalog adapters expose model information; research transports own calls, tools, continuity, cancellation and recovery. Adding a provider with the existing Responses contract only requires configuration. A different protocol requires an explicit transport adapter and directory adapter. A generic `/chat/completions` endpoint is not equivalent to the current Responses lifecycle, and native Anthropic/Gemini support is not implemented. Provider failures do not trigger an automatic change of model, effort, tools, authentication or billing.

## Agent transports

`backend.codex_auth` selects `chatgpt` or `api_key` without changing the native Codex execution loop. API mode reads `codex_api_key_env`, validates it without disclosing its value, and injects `CODEX_API_KEY` only into execution, never CLI probes or device login. It pins the official OpenAI endpoint and clears known credential values from generated shell commands while preserving other shell policies. Its sessions use separate `.mathlottery/codex-api-home` / `.mathlottery/codex-api-accounts/<slot-id>` storage; subscription homes are preserved. Missing credentials never fall back to another authentication method. New configuration fields default to subscription auth, and route hashing preserves legacy snapshots that lacked those fields. Codex API model selection accepts manual IDs rather than borrowing a subscription account's model catalog.

Codex starts with codex exec and continues the exact session using codex exec resume in the dedicated MathLottery home. It uses that home's model/tool defaults, with explicit authentication, sandbox and network settings, plus optional agent/memory overrides. The researcher controls methods and tool use. No per-action output schema or legacy tool registry is imposed on native research.

Chat creates background Responses API requests with a configured model and hosted tools. The default tools are web_search and Code Interpreter; ordinary Markdown answers may contain a single machine-readable milestone at the end. Requests use previous_response_id to retain the research context. Reviewer responses form a different chain. No browser, cookie extraction or manual copying is involved.

Chat API credentials are read from an environment variable, never from Codex login storage or request files. API errors do not trigger a switch of backend or billing. Set the model in configuration or a CLI option; only the built-in `chat` profile may also use `OPENAI_MODEL`. Custom providers require their own model selection. Configured hosted tools run server-side. Supervised Solve additionally exposes a fixed set of client-executed board functions through `providers/response_tools.py`, with per-call journals and usage accumulated across continuations. These capabilities are scoped to the current run and author; they do not expose arbitrary files or user-configured functions.

The Python harness saves answers and response metadata locally. Hosted containers and remote response history have provider retention limits; local checkpoints do not recreate expired remote contexts. Codex similarly needs its original session storage for exact continuation. Old native sessions stored in a personal Codex home are not migrated; existing MathLottery checkpoints and results remain readable, but a missing original session can require a new run.

Manual handoff is an explicitly named compatibility backend. work aliases codex, and --mode aliases --backend. Saved pre-migration chat runs are loaded as manual, so upgrading cannot silently convert them to API billing.

## Discovery and evidence

A selection milestone contains the recommended Problem and an ordered shortlist. Each problem records its statement, source, status assessment, difficulty, verification feasibility and selection reason. Discovery saves the ranking and raw agent assessment in literature/selection.json and saves reusable problems in the local problem library.

`verify/literature.py` independently downloads cited passages with bounded retrieval and durable source receipts. `verify/policy.py` matches excerpts, checks source roles, observed search queries and unresolved gaps; it does not use a domain-count heuristic. Unsupported assertions remain UNKNOWN with reasons; checked contradictory open/solution claims become DISPUTED. The raw proposal remains in the selection artifact. Even supported status is an agent assessment, not certification. See [evidence policy](evidence.md).

## Review

`verify/coverage.py` validates the declared dependency graph, named checks and original-statement alignment; `verify/obstacles.py` preserves specific questions across attempts and checks receipt-backed resolutions and theorem comparisons. `CandidateStore.review` supplies the exact original statement and inherited literature tasks. Fresh reviews receive these tasks without prior verdicts. Selection carries earlier literature barriers for matching registered problems, including a problem temporarily removed from a shortlist. These are structural/evidence checks, not semantic proof certification.

Every candidate gets a fresh reviewer context and a separate writable workspace. Only the problem, candidate content and references enter the initial review prompt; solver history and prior reviews are excluded. Codex reviewer memories are disabled. Instructions prohibit reading solver files, but workspace-write is not a complete read boundary.

Independent verify tasks end after any verdict, including INCONCLUSIVE. The pipeline instead returns unsuccessful reviews to the original researcher. A passing partial result also continues unless designated as the final deliverable. Independent solve saves candidates without launching review.

Candidates retain their claim, assumptions and references when imported for a new audit. The historical checksum still covers claim and proof; integrity checks additionally compare all immutable candidate fields against the authoritative checkpoint, including assumptions, references and identity. Both the review prompt and its `candidate.json` exclude prior verdicts and verification levels. Reviews are written separately, leaving the original candidate file unchanged. Model approval and finite experiments never become FORMALLY_VERIFIED or EXPERT_REVIEWED.

Candidate scope and remaining obligations are immutable too. `verify/auditor.py` gates positive verdicts on explicit proof checks and separates original-problem coverage from correctness and novelty. Both runners use the accepted verdict when choosing whether to return to solving. `verify/native_formal.py` checks explicitly attached frozen sources in bubblewrap, with bounded compilation, submitted-module kernel replay and a trusted declaration/axiom inspector. It never runs submitted Lake hooks or substitutes a self-reported compiler result. Receipts bind source bytes to the candidate and original problem; they do not certify statement equivalence. Missing new fields in historical records default to unassessed, with no retroactive reclassification.

## Expert report organization

`organize/brief.py` produces a deterministic bilingual report prefix from the hash-checked frozen dossier: exact problem and claim, declared proof map, alignment, historical failed checks, formal receipt scope, novelty barriers and prioritized expert questions. Material links resolve within the captured bundle. The manifest binds the prefix hash and its source; exports preserve old report text rather than retroactively inserting new content.

Organize is a standalone native workflow with a fresh session and `organization-workspace/`. Codex memories are disabled for this session. It accepts any recorded review verdict, including unresolved or negative findings, and preserves the original problem, candidate versions, reviews and verification levels. Selecting a source only prepares the form; creating the task is an explicit model invocation using its own configuration snapshot and budget.

`organize/workflow.py` captures an idle source under its ownership lock, records its revision and hash, and freezes the exact problem/candidate/review dossier plus supported visible answers, notes, proof sources and literature receipts. An earlier Solve run is included only through persisted review provenance or attachment provenance with a matching candidate; historical records without this link are not matched by title. Full Find workspaces, binary dependencies and caches are not copied. The manifest records limitations and omitted files.

The snapshot allows up to 150 files, 1,000,000 bytes per ordinary file and 16,000,000 bytes in total. The required exact dossier may be up to 4,000,000 bytes. Chat's complete inline snapshot is limited to 512,000 bytes; essential proofs are rejected if they do not fit, rather than silently truncated. File hashes are checked when restoring source copies. The organizer writes explanatory prose from visible evidence; it does not expose hidden reasoning or overwrite a source run.

Both language versions use the same frozen source and retain the same mathematical scope and evidence limitations. The harness prefixes each exposition with the recorded verdicts, coverage and novelty assessments. Saved outputs are `organized/report.zh.md`, `organized/report.en.md`, matching `.pdf` files when available, `organized/manifest.json` and `organized/materials/`. `report.md` and `report.pdf` remain compatibility aliases for the preferred language. The browser can download both versions and their shared materials as one ZIP that preserves relative links. ZIP contents are limited to 84,000,000 uncompressed bytes, including both language versions, preferred-language compatibility copies and the bounded material snapshot. SQLite retains each version’s text, hash and PDF status. Legacy single-language checkpoints remain readable without fabricating the missing version. PDF rendering is a local projection with bundled mathematics assets and no remote resource loading; missing dependencies or export errors preserve the Markdown reports and record failure per language. `export --format pdf` and the browser retry rebuild the saved report without a model call. Layout, fluent explanation and PDF success do not establish proof correctness, formal equivalence or novelty.

## Persistence and recovery

`runtime/resources.py` uses OS-held leases and a persistent FIFO queue to coordinate CLI and browser executors in one workspace. Admission precedes active research accounting. Independent formal checks use their own gate within the active budget. Dead local workers are reconciled without restarting model calls; identified orphan Codex children use the existing identity checks before termination. Memory sampling covers the local process tree and may request a cooperative stop. `telemetry/activity.py` projects bounded tool categories and statuses from native events, excluding tool arguments and raw command/output text. The browser exposes these projections separately from checkpoint history. See [resource scope and limits](resources.md).

SQLite is authoritative. Runs snapshot their workflow, backend, strategy, settings, problems, candidates and separate Codex session / Chat response identifiers. Reports and other artifacts are projections.

The active attempt is committed before invocation. Codex session identifiers are recorded immediately when reported. Chat saves the response object, including its identifier, as soon as it is received. A durable result receipt is queued before accounting and milestone application.

If a runner crashes after an API response was saved, recovery retrieves that response or replays its terminal local result; it does not create a second response. Pending background calls are accounted when their terminal result arrives. A failed creation with no known response ID is kept unresolved, since automatically retrying could duplicate work.

Ctrl+C, timeout and stop request server-side cancellation for Chat. Cancellation failures preserve the pending attempt for recovery. A stop issued after a connection failure also attempts to cancel detached remote work. Codex interruption stops its subprocess group; recovery identifies orphan processes before signalling them. No unrelated process or session is selected.

Codex's completed visible messages are also saved to `progress.md`. If an interrupted call has no final answer, those messages become its saved partial answer, while the call remains interrupted and no candidate or review is accepted from that turn. Resuming or switching transports can use that visible work. A submission file left by an interrupted process is not, by itself, proof that the backend completed successfully.

Switching transports while an invocation is pending is rejected. Otherwise each transport retains its own continuation identifiers, and recorded research answers from the other transport are imported. An additional direction arriving during recovery is preserved for the following turn.

## Budgets and verification

Time budgets count active research time; paused and manual waiting time is excluded. In supervised Solve, they stop new assignments while active attempts finish, followed by supervisor review. The original native/`allocation` workflow instead uses bounded wrap-up. `max_iterations` counts researcher and supervisor handoffs in supervised mode, not individual native tool calls. Token limits use actual backend reports and are checked between calls; concurrent calls can exceed a threshold before returning.

Codex can report cumulative session usage at the end of a turn. For resumed calls, the transport compares that report with the same session's before/after counters and charges only the increment. Confirmed per-turn reports are also supported. Missing or inconsistent counters remain unknown, rather than being added as if they were per-turn measurements. Historical checkpoints keep their recorded totals; reports flag unreconciled old records instead of silently rewriting them.

Each report projects `metrics.json` from the saved state: returns and completed turns by phase, missing/invalid milestones, measured invocation time, candidates and latest review verdicts. Historical records without phase or timing stay unknown. Pending/recovered calls can have multiple returns, so returns are not a billable-call count. These measurements expose workflow failures; they do not measure proof correctness or novelty.

API dollar costs, subscription balance and third-party services are not metered. A legacy max_external_cost_usd value of zero blocks all API-key billing, including Codex API and paid Solve slots; null delegates spending control to the provider account. No backend fallback bypasses this setting.

Contract tests use a mock Responses transport and a scripted Codex executable. They verify orchestration and recovery, not mathematical ability. Real model evaluations require configured credentials and a separately chosen research budget.

For setup and commands, see [installation and usage](usage.md). The [validation guide](local-validation.md) covers reproducible checks; the [showcase](../showcase/README.md) presents research outputs and their evidence limits.

## User selection and discovery context

Standalone Find finishes with a ranked shortlist; its recommended `problem` is not a user selection. The browser binds the chosen entry to the Find run and a fingerprint. `Orchestrator.solve_discovered` locks the source, validates membership and version, and creates a new Solve run with a frozen `DiscoveryContext`. `find/discovery.py` captures supported notes, full visible answers and sources within configurable limits. `storage/artifacts.py` reads and projects files without following symlinks. SQLite retains the manifest; hashes detect later snapshot changes. Source and solver sessions remain independent. Review workspaces never receive this dossier. The explicit CLI `run` workflow retains automatic selection.

`native_multi_agent` and `native_memories` are nullable overrides; absent overrides preserve the isolated Codex defaults, while review memories are always disabled. `telemetry/search.py` records completed native web and identifiable MCP search inputs without inferring queries from generated answers. This observation does not certify source claims; independent retrieval still checks cited excerpts. Arbitrary shell scripts are not parsed as search receipts.
