# Installation and usage

English | [简体中文](usage.cn.md)

[Project overview](../README.md) · [Result showcase](../showcase/README.md)

Run all commands from the MathLottery project root. The three research workflows are independent of the agent backend:

| Workflow | Command | Output |
| --- | --- | --- |
| Find | `find` | Ranked problems, sources, evidence of open status, and selection reasons |
| Solve | `solve` | Continuous research records, partial results, and candidate proofs |
| Verify | `verify` | Separate review verdicts, issues, evidence, and novelty assessments |
| Full pipeline | `run` | Find → solve → review, returning feedback to the original research session |

New tasks automatically read `config.yaml` in the project root for the backend, model, reasoning settings, and budget. The command only needs to specify the task and problem.

## Environment setup

Before installing Lean or starting local experiments, read [resource requirements and Lean setup](resources.md). Plan for 2–4 GiB of available RAM and 3–5 GiB of disk for a single remote workflow; with Lean/mathlib, start with 6–8 GiB available RAM and 20–30 GiB of disk. These are planning allowances, not measured minimums. Larger builds and concurrent tasks need more.

**Lean can use several GiB even for one proof check.** The guide includes a measured showcase module (about 1.99 GiB peak RSS), cache/concurrency commands, WSL memory/swap settings, and failure diagnosis. `tools.memory_mb: 512` does not limit native Codex or Lean/Lake memory.

~~~bash
conda env create -f environment.yml
conda activate mathlottery
cp config.example.yaml config.yaml
mathlottery doctor
~~~

For an existing environment, run `python -m pip install -e '.[dev,research]'`. Research dependencies include NumPy, SciPy, Matplotlib, pypdf, and SymPy/mpmath. Lean is optional and must be installed separately. You can also use `mathlottery init` to initialize local configuration and storage.

## Local browser workspace

After environment setup, start the local interface:

~~~bash
conda activate mathlottery
mathlottery serve
~~~

The terminal prints the workspace, actual port and browser address. The preferred port is `8765`. Starting again reuses a compatible MathLottery service for the same workspace and configuration and prints its address. When a port belongs to another service, startup tries the next port, up to 20 binding attempts. Under WSL, startup reads and skips Windows-reserved TCP port ranges when the Windows networking utility is available. Use `mathlottery serve --open` to open the browser automatically, or `--port 9001` to choose a different preferred port.

With an editable installation, `serve` finds the MathLottery checkout even when launched from another project directory. An explicit `mathlottery --root ./research-workspace serve` selects a different data workspace. Other CLI commands keep their existing root behavior. There is no Node.js build step or separate frontend installation. The interface supports English and Chinese and initially follows the browser language.

The default listener is `127.0.0.1`, including under WSL. Open the printed **Windows** `http://localhost:<port>` address from a Windows browser; WSL normally forwards localhost connections into Linux. Use the actual printed port, since a port that can bind in Linux may still be reserved on Windows. If access fails, check the Linux and Windows sides separately. [Microsoft's WSL networking guide](https://learn.microsoft.com/en-us/windows/wsl/networking)

For an explicit alternative on NAT-mode WSL, `mathlottery serve --wsl-direct` enables direct access through the WSL address and prints it. This option broadens the listener and restricts request peers to loopback, the WSL address and the Windows gateway. It is never enabled automatically. `--loopback-only` remains a supported way to select the default loopback behavior and cannot be combined with `--wsl-direct`. Startup does not modify WSL configuration, proxies, port-forwarding rules or the firewall.

1. **Find:** enter preferences, an optional source URL and a shortlist size. Compare each problem’s difficulty, verification feasibility, Lean feasibility, prerequisites, obstacles and source evidence. The agent recommendation is not a user selection. Click **Choose this problem**, review **Your choice** in the Solve form, and then click **Start solving**. Choosing alone never starts a model call.
2. **Solve:** select a saved problem or enter a statement. The result panel shows candidate proofs; **Verify latest candidate** prepares a separate review task.
3. **Verify:** select a run's latest candidate, or provide a problem and proof. Reviews retain verdicts, issues, evidence and novelty separately from the candidate's proof level.

Use the optional **Task instructions** field to request Lean formalization, compiler checks or a particular research approach from the first turn, while preserving the selected problem's statement.

New tasks read the current `config.yaml`. Expand **Model & budget** for per-task backend, model, reasoning and budget overrides; this does not edit the configuration file. Codex uses this MathLottery workspace's own login and tool configuration; Chat uses its API credentials and billing. Starting a task makes real calls to the selected backend.

For Codex, **Start** and **Continue research** require a completed ChatGPT login in the MathLottery account panel. The server checks again before saving a new task or launching a continuation, using the selected backend for a new task and the saved backend for a continuation. An unavailable CLI, pending login or API-key-only Codex account produces an actionable error without starting a worker. These checks leave local Codex credentials unchanged and do not gate Chat API tasks. Login readiness does not guarantee that the provider will accept a later model request; execution errors remain visible in the task.

History groups Solve and Verify records by saved problem ID and exact statement. Each Find remains a separate shortlist, rather than being assigned to its first recommendation. A solver started from a shortlist links back to its source Find. Multiple runs of the same stage remain visible and are numbered. Click any record to open its own results. Groups show their latest update time, while each record shows its start time. **Agent turns** count research handoffs, including interrupted calls and continuations, rather than complete attempts to solve the problem. Resuming keeps the same run record.

You can skip Find: open **Solve**, choose **Enter a new problem**, and enter a statement and optional title. Without a title, the first 100 characters of the statement become the title. The problem is saved for reuse, and its history initially contains only a Solve record. **Verify latest candidate** prepares a review in the same problem group; no Find record is created. A supplied problem starts with status **Unknown**; entering it does not establish that it is open or solved.

The history and detail panels refresh every two seconds while the page is visible. They show checkpoints, saved visible output, token usage, candidate proofs and reports; a long native call can remain quiet between checkpoints. Download the report or use **Stop task** to request cancellation and retain already saved progress. Stopping does not guarantee that the agent can finish its current submission. User cancellation and an exhausted active-time budget have distinct stop reasons; provider failures remain errors. **Resume / add direction** continues the saved session. Resume budget fields replace total limits, and the task retains its saved model settings. A completed task needs additional direction to continue.

When a research or review workspace contains Lean files, **Results** also lists downloadable `.lean`, `lean-toolchain` and `lakefile.toml` text files. Each download is limited to 1 MB; linked files, hidden directories, dependency caches and build outputs are excluded. The list is bounded and reports when it is incomplete. Downloads contain the selected source text, not a complete Lean project archive, and preserve the source filename in modern browsers; retain the displayed relative path when reconstructing the project locally. Source availability is not evidence that Lean ran successfully, that the formal statement matches the public problem, or that the result is new. The candidate's proof level is unchanged by listing or downloading these files.

When verifying a saved candidate, you can explicitly select proof source files from its research workspace. No files are selected automatically. The form retains the displayed candidate ID and checksum; if that candidate changes before submission, refresh the source before trying again. The source task must be idle. At submission, MathLottery freezes the selected file contents and records their paths, sizes and SHA256 hashes. Later source edits do not change the review input. The review's Results panel shows this manifest separately from its verdict.

Attachments are limited to 20 files, 1 MB per file and 2 MB total for native Codex. Native Chat includes the actual source text in its prompt, with a smaller 128 KB total limit. Codex receives the files under `submitted-evidence/` in its independent review workspace. Logs, previous reviews, dependency caches and login data are not included. Provide all small local Lean dependencies needed by the proof; this does not package or install mathlib. Attached sources are untrusted evidence for the reviewer to inspect and recheck, and never automatically raise the proof level.

The result summary distinguishes the proof level, latest agent review, recorded problem status and novelty. A completed task or an agent finding no issues is not a claim of complete formal verification or a confirmed new solution to an open problem.

Workers continue when the browser or UI server closes. To stop research, use **Stop task** or `mathlottery stop <run-id>`. Restarting the UI reconnects to the same local state; it does not relaunch tasks automatically. The UI and CLI share `problems/`, `runs/` and `.mathlottery/`, and per-task worker records live under `runs/<run-id>/web/`. Use the CLI for the full `run` pipeline and legacy manual handoffs.

Browser writes require a same-origin request token, and only packaged assets and selected run data are served. Agent output is displayed as text. This remains a local workspace; the Codex account connection is not multi-user access control for the web interface.

### Sign in with ChatGPT

The **MathLottery account** panel manages a login dedicated to the current workspace. Signing in, switching accounts, or signing out here leaves your ordinary local Codex CLI / IDE login unchanged. The MathLottery browser interface, MathLottery CLI commands, and background research workers all use this workspace's login.

Sign in once in MathLottery even if your local Codex is already logged in. Choose **Sign in with ChatGPT**, open the official link, and enter the one-time code. Complete authentication on OpenAI's page. You may choose the same ChatGPT account or a different account. Separate login state does not provide additional quota: sessions using the same account still use its subscription allowance. Device-code login may first need enabling in ChatGPT security settings or by a workspace administrator. [Official authentication guidance](https://learn.chatgpt.com/docs/auth)

After login, the panel shows the masked email and plan when available. **Switch account** signs out of this MathLottery workspace first, then starts a new device-code login. Cancelling or failing the new authorization leaves MathLottery signed out; sign in again to restore access. **Sign out** ends only this workspace's login. Both actions ask for confirmation and are blocked while a Codex task is running in this workspace. Reading status or using ordinary sign-in never automatically replaces an existing MathLottery login. The ChatGPT website's browser session is separate.

MathLottery sets `CODEX_HOME` only in its Codex child processes, to `.mathlottery/codex-home`, and forces `cli_auth_credentials_store="file"`. Official Codex stores credentials there; the directory is Git-ignored and owner-only on POSIX systems. The parent's environment, local Codex home, and OS credential store remain untouched. MathLottery does not copy or fall back to local Codex credentials, configuration, or sessions. Configure optional MCP servers, plugins and Codex defaults in this dedicated home when needed. Search, shell and file tools still run through official Codex. [Codex environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables)

Existing MathLottery problems, reports and checkpoints remain available after this change. A native conversation previously stored in your personal Codex home is not copied: resuming it may require a new run because its original session is absent from the dedicated home. Newly created sessions persist in the dedicated home for later continuation.

Passwords and tokens never pass through the MathLottery frontend. Only masked account details and pending device-code state are retained in application memory, not in configuration, reports or browser localStorage. Login checks do not start research. The integration uses the official [Codex app-server authentication protocol](https://learn.chatgpt.com/docs/app-server). Keep `.mathlottery/` private and excluded from Git, including its credentials and sessions.

This login connects the **codex** backend. MathLottery's current **chat** backend still requires an API key and API billing; it does not implement the separate Sign in with ChatGPT API integration.

## Choose a model in config.yaml

Common settings are grouped at the top of the configuration file. This example selects Codex, GPT-6 Astra, and Max:

~~~yaml
backend:
  mode: codex
  model: gpt-6-astra
  reasoning_effort: max
  chat:
    reasoning_mode: pro

budget:
  max_wall_time_minutes: 180
  max_iterations: 50
~~~

To use Chat Pro, change `backend.mode` to `chat` and configure an API key as described below. `backend.chat.reasoning_mode` only applies to the chat backend and accepts `pro` or `standard`; Codex uses `model` and `reasoning_effort`. Edit `model` to select a different model.

After saving the configuration, use a short command:

~~~bash
mathlottery find
mathlottery solve --prompt 'Please solve the Riemann hypothesis'
mathlottery verify --from-run <solve-run-id>
mathlottery run
~~~

These commands start finding, solving, verification, and the full pipeline respectively. Choose the one you need; there is no need to repeat model and budget settings.

| Configuration field | Purpose | Example |
| --- | --- | --- |
| `backend.mode` | Agent backend | `codex` / `chat` |
| `backend.model` | Model ID | `gpt-6-astra` |
| `backend.reasoning_effort` | Reasoning effort | `max` |
| `backend.chat.reasoning_mode` | Chat API reasoning mode | `pro` / `standard` |
| `budget.max_wall_time_minutes` | Total active time limit, in minutes | `180` |

GPT-6 Astra supports low, medium, high, xhigh, and max. The GPT-5.6 and GPT-6 families support a separate `reasoning.mode: pro` field in the Responses API. Do not append `-pro` to the model ID or put `pro` in `reasoning_effort`. Pro increases model work, latency, and token usage. [Model reference](https://developers.openai.com/api/docs/models/gpt-6-astra) · [Reasoning mode](https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode)

This configures the API's Pro execution mode. ChatGPT on the web may use different tools, system instructions, and product orchestration, so identical behavior is not guaranteed. Model, effort, and tool availability depend on the account and backend. Unsupported settings produce errors rather than an automatic downgrade. Reports distinguish requested settings from those actually reported by the backend; unreported fields remain unknown.

Use `--backend`, `--model`, `--reasoning-effort`, or `--reasoning-mode` for a temporary override without editing the file. New tasks read the current configuration. `resume` restores the configuration saved when the task was created, so later edits to `config.yaml` do not affect existing tasks. Pass explicit overrides to change a model or mode when resuming. Pending background requests are recovered first; new settings apply to the next request.

## Choose an agent backend

### codex: persistent native agent sessions

Install the official Codex CLI, then sign in through the browser workspace's **MathLottery account** panel. Running plain `codex login` signs in to your separate local Codex and does not sign in to MathLottery. MathLottery uses official `codex exec` calls and resumes the exact same session in its dedicated home. Codex supplies search, shell and file operations; optional MCP/plugin configuration belongs in the MathLottery home. Available tools depend on the machine and account.

~~~bash
mathlottery solve --prompt 'Please solve Goldbach’s conjecture'
~~~

Set `backend.mode` to `codex` in `config.yaml`. When `model` and `reasoning_effort` are `null`, they use Codex defaults from the dedicated MathLottery home; set them in the file to choose explicitly. A model selected in a separate chat interface may differ from the CLI default. Research files are written to the current research workspace using the `workspace-write` sandbox and configured network permissions.

Native calls use ordinary agent execution without the per-action JSON protocol, the legacy 15-second / 512 MB tool wrapper, or fixed-length summaries in place of native history. Codex still has its own context window and compaction behavior. [Official non-interactive usage](https://learn.chatgpt.com/docs/non-interactive-mode)

### chat: automatic Responses API calls

The chat backend calls the model API directly, waits for results, saves context, and continues to the next round. Server-hosted `web_search` and Code Interpreter are enabled by default. It requires API credentials and an explicit model. Here, `chat` means the API backend, not automation of ChatGPT's web Pro mode.

Set `backend.mode` to `chat` and `model` to a model available to your account. Store the API key in the `OPENAI_API_KEY` environment variable, not in the configuration file. This Bash command hides input and keeps the key out of command history:

~~~bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
mathlottery find --query 'Combinatorics problems suitable for a limited research budget'
~~~

If `backend.model` is unset, you can supply the model through `OPENAI_MODEL`. `doctor` checks whether Chat configuration is complete without sending billable model requests. Missing credentials, missing models, or unsupported tools produce explicit errors; the program does not switch to manual mode or another backend.

Chat uses `previous_response_id` to continue research context, while reviews start with fresh context. Long calls run in the background on the server and the program polls their status. Ctrl+C and `stop` request server-side cancellation. After a connection loss, a call with a known response ID is retrieved rather than created again. If creation fails before an ID arrives, the program preserves an uncertain state; check the API dashboard before deciding to start a new run.

Full API answers, tool results, and citation metadata are saved locally. Code Interpreter runs in a hosted container and cannot directly read local files. Containers and server-side responses have their own retention periods; local reports cannot recreate expired remote context.

References: [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state), [background calls and cancellation](https://developers.openai.com/api/docs/guides/background), [web search](https://developers.openai.com/api/docs/guides/tools-web-search), and [Code Interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter).

## Native agent capabilities

The native backend keeps official search, shell tools and persistent sessions. It adds no per-action JSON protocol or legacy memory excerpt limit. In `config.yaml`, `backend.native_multi_agent` and `backend.native_memories` accept `true`, `false` or `null`; `null` inherits the isolated Codex configuration and runtime defaults. The browser exposes both as task overrides. A continuous primary researcher remains responsible for the result. Helper agents can consume additional tokens; choosing `false` keeps a single agent. Review sessions always force memories off.

Optional MCP servers, plugins and Codex defaults belong in `.mathlottery/codex-home/config.toml` and the corresponding private home, not your personal Codex home. They are not copied automatically. A feature flag does not install tools or guarantee account support. Existing workspace isolation, network configuration and budgets still apply. Independent source/Lean checks currently share the research time budget. Chat continues to use its configured hosted tools; it does not gain local Shell/Lean access from these Codex options.

## Find problems

~~~bash
mathlottery find --query 'Prioritize precisely stated problems with recent evidence that they remain open and scope for computational experiments'
mathlottery find --source https://www.erdosproblems.com/ --count 3
mathlottery problems
~~~

The agent searches, compares problems, and checks prior progress. Finding saves reusable problems and the current ranking, then stops before solving. The terminal lists problem IDs; detailed output is in `runs/<run-id>/literature/selection.json` and `report.md`.

To choose a problem and carry its Find context forward:

~~~bash
mathlottery solve --from-find <find-run-id> --problem <problem-id>
~~~

The problem must belong to that exact shortlist. The browser also binds the displayed version by checksum, so a changed list requires a fresh choice. A new Solve session receives a frozen dossier containing the preferences, shortlist, full visible research answers, notes and supported source files. It does not share the mutable Find conversation or inherit hidden reasoning. The original Find stays unchanged, and you can choose another problem from it later. Verify does not inherit this research dossier.

The snapshot defaults to 300 files, 8 MB per file and 32 MB total. Dependency/build caches, hidden files, credentials and linked files are excluded. Supported formats are Markdown/text, JSON, CSV/TSV, Python, Lean, LaTeX/BibTeX and PDF. The manifest lists files omitted by size, scan or read limits. Chat receives up to 256 KB of text inline on its first response; binary PDFs and text beyond that limit are explicitly listed as not sent. Configure `discovery.context_max_files`, `context_max_file_bytes`, `context_max_total_bytes` and `chat_context_max_bytes` when needed. Source files remain untrusted, and old open-status evidence may need refreshing.

Find may explore examples or proof routes to estimate difficulty, but returns its list for your choice. Uncertain open status stays **Unknown**; an estimate is never a success probability. The CLI’s explicit `run` command remains the automatic full-pipeline alternative.


Each problem retains its exact statement, sources, difficulty estimate, verification feasibility, and selection reason. Open status is an agent assessment supported by evidence; ranking is not a probability of success. Only sources supported by the run record count toward status checks. Insufficient evidence leaves status at `UNKNOWN`, while the original agent assessment remains in the selection record.

## Solve a problem

Use a problem ID from discovery or provide a research goal directly:

~~~bash
mathlottery solve --problem <problem-id>
mathlottery solve --prompt 'Investigate this mathematical problem...'
~~~

You can also import your own problem:

~~~bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --problem odd-sum --budget-time 10m
~~~

The same research agent chooses the order of derivations, experiments, and tool calls. It can save partial candidates and continue exploring. Submitting a final candidate ends an independent `solve` task; the proof remains `CANDIDATE` until `verify`. Finding no proof is also a valid research outcome.

## Verify a candidate

Review the latest candidate from an existing solve run, or supply a candidate JSON file or proof file:

~~~bash
mathlottery verify --from-run <solve-run-id>
mathlottery verify --candidate runs/<run-id>/candidates/<candidate-id>.json
mathlottery verify --problem odd-sum --proof examples/odd_sum.proof.md
~~~

Candidate JSON retains its `claim`, `proof`, `assumptions`, and `references`; prior review verdicts are excluded from the new review. Without `--problem`, the JSON candidate's `claim` is the statement being checked. A plain proof file requires `--problem`.

Reviews use a separate session and workspace. The initial context contains the problem, candidate and references, plus any proof sources explicitly selected in the browser. Previous solver conversations and review verdicts are not included. Any of `NO_ISSUES_FOUND`, `ISSUES_FOUND`, or `INCONCLUSIVE` ends an independent `verify` task without starting a solver. A favorable model review can establish at most `SELF_CHECKED`; finite tests or an agent's claim that Lean passed do not automatically establish a formal proof.

New Find/Verify milestones must provide checkable excerpts, search coverage and concrete proof checks to support their conclusions. Results display **original-problem coverage**, remaining obligations and evidence gaps separately from the verdict. A correct partial result does not become a complete solution. Historical records without these fields remain unassessed under the new policy.

For an independent Lean receipt, attach the required sources in the browser and ask the reviewer to request a check of the named theorem declarations. Configure `verification` in `config.yaml`; prepare compatible Lean/leanchecker, bubblewrap, `prlimit` and prebuilt libraries first. Successful kernel replay can support `PARTIALLY_VERIFIED`, with its exact scope recorded. Missing tools, resource limits and source failures remain visible. See [evidence requirements and configuration](evidence.md).

Codex's `workspace-write` sandbox does not fully isolate file reads. Review independence here concerns the context; it is not a certified blind review.

## Run the full pipeline

~~~bash
mathlottery run
mathlottery run --problem <problem-id>
mathlottery run --prompt 'Please solve the Riemann hypothesis'
~~~

With no problem supplied, the pipeline starts by finding one; otherwise it starts solving. Candidates go to a separate reviewer, and issues or uncertainty return to the original researcher. Passing a partial result continues research. The pipeline ends when the researcher explicitly submits a final deliverable and its review finds no issues.

## Pause, resume, and inspect reports

~~~bash
mathlottery status <run-id>
mathlottery stop <run-id>
mathlottery resume <run-id>
mathlottery resume <run-id> --message 'Prioritize boundary cases and counterexamples'
mathlottery resume <run-id> --budget-time 6h --max-iterations 100
mathlottery report <run-id> --show
mathlottery export <run-id> --format json --output checkpoint.json
~~~

Budget overrides set new total limits and do not reset time already consumed. Paused time does not count as active time. `max_iterations` counts research handoffs, not native tool calls within a round. Token accounting uses actual backend reports and is checked between calls; unreported usage stays unknown.

Reports include a stage measurement table and `metrics.json`: completed returns, missing/invalid milestones, measured invocation seconds, candidate counts and review outcomes. Use these to locate time spent on discovery, solving or review, and to detect repeated handoff failures. Missing historical timing is `unknown`, not zero. These measurements do not certify mathematical success. See [code flow and recovery](architecture.md) for the module boundaries.

A finished native task can receive further guidance through `resume --message` and continue its original workflow. Use `--backend` explicitly to switch agents; pending calls must be recovered first. Each backend has separate context IDs, and switching imports recorded research answers.

Do not operate the same active session simultaneously from another Codex client.

## Configuration and usage accounting

Time and token budgets do not cap local RAM or disk. See [the scope of resource controls](resources.md#what-the-configuration-actually-limits) before increasing concurrency or launching a Lean build.

See [config.example.yaml](../config.example.yaml) for the full template. Common settings:

~~~yaml
backend:
  mode: codex
  execution: native
  model: gpt-6-astra
  reasoning_effort: max
  native_turn_timeout_seconds: null
  native_web_search: live
  native_network_access: true
  chat:
    api_key_env: OPENAI_API_KEY
    base_url: https://api.openai.com/v1
    reasoning_mode: pro
    poll_interval_seconds: 1
    request_timeout_seconds: 30
    tools:
      - type: web_search
      - type: code_interpreter
        container:
          type: auto
budget:
  max_wall_time_minutes: 180
  max_iterations: 50
  max_external_cost_usd: null
~~~

When `native_turn_timeout_seconds` is `null`, one agent call may use the remaining total time budget. `chat.request_timeout_seconds` limits a single HTTP request, not the model's total thinking time. When `chat.reasoning_mode` is `null`, that field is omitted and the API default applies; `standard` and `pro` can be selected explicitly. Configure Chat's hosted tools according to account and model support. Custom tools that require client-side execution are not yet implemented.

Chat uses API billing; Codex uses the official CLI's ChatGPT login. Authentication and billing methods are never switched automatically. This project does not estimate dollar costs, subscription balances, or third-party tool fees; set API spending controls in the provider account. The legacy setting `max_external_cost_usd: 0` blocks Chat API calls. `null` delegates spending controls to the account and does not mean free usage.

`codex_command` defaults to the command name `codex`, resolved through `PATH` at runtime. Discovered absolute paths are not written back into configuration. `config.yaml`, `.env`, IDE settings, databases, run records, and test logs are ignored local files.

## Browse result samples

The [showcase](../showcase/README.md) contains three compact case studies with proofs, review summaries, and verification records:

- [Mesh patterns on involutions](../showcase/mesh-involutions/README.md): a complete written candidate proof with partial Lean verification.
- [Medial-triangle inequality](../showcase/medial-triangle-inequality/README.md): a complete written proof and a checked Lean formalization.
- [Stepwise irregular graphs](../showcase/stepwise-irregular-graphs/README.md): a complete counterexample with an executable finite certificate.

Each case links to its reproduction instructions and states its novelty limits. Its review summary and verification records explain the evidence behind those assessments. These are research outputs; their formal verification and novelty status should be read separately.

## Local artifacts

~~~text
.mathlottery/state.sqlite3          # Authoritative state, backend context IDs, events
problems/<problem-id>/problem.json # Reusable problem statement
runs/<run-id>/
  literature/selection.json        # Ranking, status evidence, original assessment
  workspace/                       # Research workspace and full research answers
  review-workspaces/<candidate-id>/ # Separate review workspace
  tasks/<task-id>/<attempt>/        # Prompts, answers, invocation receipts
    request.json / response.json   # Chat API bodies, without authentication headers
    codex.events.jsonl             # Native Codex events
  candidates/                      # Immutable candidate proof versions
  verification/                    # Separate review results
  checkpoints/ / usage.json         # Recovery state and actual usage
  report.md                        # Workflow results and evidence
  metrics.json                     # Measured stage outcomes and invocation timing
~~~

Model and tool information comes from actual responses or session metadata; unreported fields stay unknown. External tool side effects are not guaranteed to occur exactly once. Check logs and research files during recovery.

## Legacy compatibility and development

The former manual handoff backend is now named `manual`. `work` remains an alias for `codex`, and `--mode` remains an alias for `--backend`. Old `chat` checkpoints still resume as `manual`; upgrading does not automatically send billable API requests.

~~~bash
mathlottery run --backend manual --prompt 'Investigate this mathematical problem...'
mathlottery submit --run <run-id> --file response.md
mathlottery run --backend manual --execution structured --problem odd-sum
mathlottery demo
mathlottery demo --case incorrect
pytest -q
ruff check .
~~~

Only `manual` requires a person to transfer responses. Both `chat` and `codex` call the agent automatically. `structured` is the legacy compatibility protocol; the three independent workflows use `native`.

See [architecture and recovery](architecture.md), [validation methods and scope](local-validation.md), and the [legacy protocol](protocol.md) for details. Offline demos and mock-backend tests do not measure a model's mathematical ability. The project does not automatically commit or push to GitHub.
