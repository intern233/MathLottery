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

~~~bash
conda env create -f environment.yml
conda activate mathlottery
cp config.example.yaml config.yaml
mathlottery doctor
~~~

For an existing environment, run `python -m pip install -e '.[dev,research]'`. Research dependencies include NumPy, SciPy, Matplotlib, pypdf, and SymPy/mpmath. Lean is optional and must be installed separately. You can also use `mathlottery init` to initialize local configuration and storage.

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

Install the official Codex CLI and run `codex login` to sign in with ChatGPT. MathLottery uses official `codex exec` calls and resumes the exact same session. Codex supplies search, shell, file operations, and existing MCP/plugin configuration. Available tools depend on the machine and account.

~~~bash
mathlottery solve --prompt 'Please solve Goldbach’s conjecture'
~~~

Set `backend.mode` to `codex` in `config.yaml`. When `model` and `reasoning_effort` are `null`, they inherit the Codex user configuration; set them in the file to choose explicitly. A model selected in a separate chat interface may differ from the CLI default. Research files are written to the current research workspace using the `workspace-write` sandbox and configured network permissions.

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

## Find problems

~~~bash
mathlottery find --query 'Prioritize precisely stated problems with recent evidence that they remain open and scope for computational experiments'
mathlottery find --source https://www.erdosproblems.com/ --count 3
mathlottery problems
~~~

The agent searches, compares problems, and checks prior progress. Finding saves reusable problems and the current ranking, then stops before solving. The terminal lists problem IDs; detailed output is in `runs/<run-id>/literature/selection.json` and `report.md`.

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

Reviews use a separate session and workspace. The initial context contains only the problem, candidate, and references. Any of `NO_ISSUES_FOUND`, `ISSUES_FOUND`, or `INCONCLUSIVE` ends an independent `verify` task without starting a solver. A favorable model review can establish at most `SELF_CHECKED`; finite tests or an agent's claim that Lean passed do not automatically establish a formal proof.

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

A finished native task can receive further guidance through `resume --message` and continue its original workflow. Use `--backend` explicitly to switch agents; pending calls must be recovered first. Each backend has separate context IDs, and switching imports recorded research answers.

Do not operate the same active session simultaneously from another Codex client.

## Configuration and usage accounting

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

Each case links to its reproduction instructions and states its novelty limits. See the [source and correctness audit](../showcase/audit-2026-10-21.md) for the evidence behind those assessments. These are research outputs; their formal verification and novelty status should be read separately.

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
