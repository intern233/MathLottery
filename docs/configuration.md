# Backend and model configuration

English | [简体中文](configuration.cn.md)

[Quickstart and commands](usage.md) · [Resources and Lean](resources.md) · [Result showcase](../showcase/README.md)

Use this reference after the [browser quickstart](usage.md#local-browser-workspace) or when configuring terminal workflows. Both entry points use the selected workspace's `config.yaml`; choose the agent connection independently of Find, Solve or Verify. `mathlottery init` creates local defaults. [config.example.yaml](../config.example.yaml) is a fuller field reference whose example model settings must be adapted to your account. Keep local settings private and change only the sections you need.

[Models](#models) · [API providers](#providers) · [Codex account and tools](#account) · [Network](#network) · [Budgets](#budgets) · [Evidence](#evidence) · [Recovery](#recovery) · [Compatibility](#legacy)

<a id="models"></a>
## Models and configuration precedence

For Codex, a model ID and reasoning effort are separate settings:

```yaml
backend:
  mode: codex
  model: gpt-6-astra
  reasoning_effort: max
```

Use a model and effort supported by your account. This is a configuration example, not a guarantee of model access. The browser's **Model for this task** panel reads the selected provider's directory and keeps manual input available for unlisted models. The Codex subscription directory supplies advertised effort options; a Responses directory may only supply model IDs. Codex API authentication uses configured or manually entered model IDs without consulting the subscription directory. Missing capability information remains unknown. Refresh the directory with **Refresh models**; listing a model does not test inference, quota or tools.

| Field | Meaning and unset behavior |
| --- | --- |
| `backend.mode` | `codex` for official Codex sessions; `chat` for Responses calls. |
| `backend.codex_auth` | Codex only: `chatgpt` (default, subscription login) or `api_key` (OpenAI API billing). Both use the native Codex agent. |
| `backend.codex_api_key_env` | Codex API only: environment variable **name**, default `OPENAI_API_KEY`. Never put a key value here. |
| `backend.provider` | Optional profile ID: `codex`, `chat`, or a configured name such as `research-api`. Omit it or use `null` for the mode's built-in connection. |
| `backend.model` | Exact model ID, without an appended effort such as ` max`. `null` uses Codex's dedicated-home default; built-in Chat may use `OPENAI_MODEL`. Custom API profiles require an explicit model. |
| `backend.reasoning_effort` | Optional provider-supported value such as `max`; `null` leaves it to the backend. |
| `backend.chat.reasoning_mode` | Optional Responses setting: `pro`, `standard`, or `null` to omit it. Applies only to `chat`, and only when supported by that provider/model. |

Do not put `pro` in `reasoning_effort` or infer a model ID by adding `-pro`. The API setting is not a promise of identical behavior to ChatGPT's web product. Unsupported combinations produce errors; MathLottery does not silently substitute another model or lower effort. Reports distinguish requested settings from backend-reported settings.

**New tasks:** application defaults → `config.yaml` (or the file selected with global `--config`) → explicit CLI or browser task overrides. For example, `mathlottery --config alternate.yaml find` uses that file. `--backend`, `--model`, `--reasoning-effort` and `--reasoning-mode` override the relevant fields without editing it. When changing backends manually, clear old incompatible model/effort/mode settings; the browser resets these when switching providers.

**Existing tasks:** `resume` starts from the saved configuration snapshot. Later edits to `config.yaml` or a provider profile do not redirect the saved conversation. Browser continuation preserves its model settings; CLI continuation accepts explicit model/backend overrides. Pending calls must be recovered first. See [recovery](#recovery).

<a id="providers"></a>
## API credentials and additional providers

Agent execution and authentication are separate choices. **Codex agent** supports ChatGPT subscription login or an OpenAI API key. **API agent** retains the independent Responses harness for compatible providers and future protocol adapters; its historical configuration name is `chat`. An API key alone does not specify which harness runs.

### Codex agent with an OpenAI API key

Keep `mode: codex` to retain Codex's native terminal, files, tools and session continuation:

```yaml
backend:
  mode: codex
  execution: native
  codex_auth: api_key
  codex_api_key_env: OPENAI_API_KEY
  model: your-api-model-id
  reasoning_effort: null
```

Set the named environment variable in the server/CLI's launching terminal using the key-entry command below. On the Agents page, choose **Codex agent**, then **API Key**. This selects official OpenAI API billing; it does not consume the ChatGPT subscription allowance. No device login is needed, and the key is not saved through `codex login`. MathLottery supplies it only to the Codex execution process and clears known credential values from its shell tools. Some ChatGPT workspace integrations may require subscription authentication even though native terminal/file tools remain available. See [official authentication](https://learn.chatgpt.com/docs/auth).

API-mode Codex state uses `.mathlottery/codex-api-home`, or `.mathlottery/codex-api-accounts/<slot-id>` for a slot. Subscription authentication and sessions remain separate. Resume keeps the saved authentication choice and environment variable name; start a new task to select another route. Presence of a key is only a local configuration check, not confirmation of account access or model availability. Enter API model IDs manually; the subscription model catalog is not reused for API authentication.

### Independent API agent (Responses)

The built-in `chat` connection uses the OpenAI Responses API. It requires its own API key and API billing; the MathLottery Codex login does not supply these credentials.

```yaml
backend:
  mode: chat
  provider: chat
  model: your-api-model-id
  reasoning_effort: null
  chat:
    api_key_env: OPENAI_API_KEY
    base_url: https://api.openai.com/v1
    reasoning_mode: null
    poll_interval_seconds: 1
    request_timeout_seconds: 30
    tools:
      - type: web_search
      - type: code_interpreter
        container: {type: auto}
```

Replace `your-api-model-id` and choose tools your API model supports. In Bash, enter the key without placing it in command history, then start MathLottery from that terminal:

```bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
```

`doctor` checks local configuration without a billable model call; it does not establish API entitlement. Keys are read from the environment and are not saved in configuration or reports. `.env` is Git-ignored but **is not automatically loaded**: use your shell or a trusted environment manager. For built-in `chat` only, `OPENAI_MODEL` is used when `backend.model` is unset.

For another provider, replace the following placeholders in your local configuration:

```yaml
backend:
  mode: chat
  provider: research-api
  model: provider-model-id
  reasoning_effort: null
  chat:
    reasoning_mode: null

model_providers:
  research-api:
    label: Research API
    transport: responses
    chat:
      base_url: https://api.example.invalid/v1
      api_key_env: RESEARCH_API_KEY
      tools: []
    models:
      - id: provider-model-id
        label: Research model
        reasoning_efforts: null
    reasoning_modes: []
```

Export `RESEARCH_API_KEY` in the starting terminal. Each profile must explicitly specify `base_url`, `api_key_env` and `tools`; OpenAI credentials and tools are not inherited. **`tools: []` enables no hosted search or code execution.** Add only tools supported by the provider before relying on Find/Verify to search current literature. The browser chooses a configured profile ID; it never receives API keys or asks for an endpoint URL. Keep real private endpoints and credentials outside version control.

An optional nonempty `models` list supplies the local directory instead of requesting `/models`. Omit it for remote discovery. For each model, omitted/`null` `reasoning_efforts` means unknown; `[]` means no effort values are declared. To declare support, use, for example, `reasoning_efforts: [low, high]` and `default_reasoning_effort: high`. Declare `reasoning_modes` only if the provider implements the separate Responses mode field. Select a named profile in the browser or set `backend.provider` in configuration; there is no CLI `--provider` option.

**Compatibility requires the full Responses lifecycle:** background requests, stored responses, retrieval, cancellation, `previous_response_id` continuation, and the configured tools. An endpoint offering only `/chat/completions` is insufficient. Native Anthropic/Gemini protocols and client-executed custom function tools are not implemented. A new protocol needs explicit research and model-directory adapters; failures never trigger a change of provider, authentication or billing. Hosted Code Interpreter cannot directly access local files or a locally installed Lean environment.

<a id="account"></a>
## Codex account, isolation and native tools

Parallel Solve can use a separate connection per researcher. The [Agent configuration page](agents.md) manages Codex authentication and independent API settings. Subscription logins live under `.mathlottery/codex-accounts/<slot-id>`; the default account described below remains separate. The login instructions in this section apply to `codex_auth: chatgpt`.

Install the official Codex CLI in the same Linux/WSL environment as MathLottery; confirm `codex --version` works there. Installation options are documented in the [official CLI guide](https://learn.chatgpt.com/docs/cli) and [Codex repository](https://github.com/openai/codex). A Windows launcher inherited through WSL's `PATH` may be the wrong executable; check `command -v node`, `command -v npm` and `command -v codex` if it cannot start.

Sign in once through the browser's **MathLottery account** panel, even if ordinary Codex is already logged in. Device-code authentication may need enabling in ChatGPT security settings or by an administrator. Complete authorization on the official page, not in MathLottery. [Official authentication guidance](https://learn.chatgpt.com/docs/auth)

For a terminal-only setup, activate the MathLottery environment and run this **from the intended project/workspace root**, after installing `codex`:

```bash
python - <<'PY'
from pathlib import Path
import subprocess
from mathlottery.providers.identity import CodexIdentity

identity = CodexIdentity(Path.cwd())
subprocess.run(
    ["codex", *identity.overrides(), "login", "--device-auth"],
    env=identity.environment(),
    check=True,
)
PY
```

Follow the printed authorization instructions once. This uses MathLottery's identity helper and affects only its child process; do not globally export `CODEX_HOME`. Plain `codex login` without this helper operates on your ordinary Codex login instead. The browser, MathLottery CLI and research workers share the workspace's isolated login.

| Item | Scope |
| --- | --- |
| Login and sessions | `.mathlottery/codex-home`, with file credential storage and owner-only home permissions on POSIX. No personal Codex credentials, configuration or sessions are copied or used as a fallback. |
| Switch account / Sign out | Current MathLottery workspace only. Browser confirmation is required; changes are blocked while a Codex task runs here. Switching signs out first, so cancelled or failed new authorization leaves this workspace signed out. |
| Subscription allowance | Using the same ChatGPT account still shares that account's allowance; isolated login storage creates no extra quota. |
| MCP, plugins and Codex defaults | Configure the dedicated `.mathlottery/codex-home/config.toml` and private home. The personal CLI/IDE setup is not automatically inherited. |

The frontend receives masked account details and pending device-code state, not account tokens. Keep `.mathlottery/` private. The dedicated-home mechanism uses Codex's documented [`CODEX_HOME` setting](https://learn.chatgpt.com/docs/config-file/environment-variables).

Optional native settings:

```yaml
backend:
  mode: codex
  execution: native
  codex_command: codex
  native_web_search: live
  native_network_access: true
  native_multi_agent: null
  native_memories: null
```

`native_web_search` accepts `live`, `cached` or `disabled`. Multi-agent and memory settings accept `true`, `false` or `null`; `null` inherits isolated Codex/runtime defaults. A continuous primary researcher remains responsible; helpers can increase usage. Independent reviewers always have memories disabled. These flags do not install tools or guarantee account support. Native Codex retains its own context/compaction and workspace-write sandbox; no legacy per-action JSON or 512 MB tool limit is imposed. `codex_command` is resolved through `PATH` at runtime, without saving discovered machine paths.

<a id="network"></a>
## Network and proxy configuration

MathLottery and its Codex children use the environment of the terminal that starts them. An IDE extension's working connection does not prove that this terminal has the same proxy settings. For a required proxy, configure your terminal or the ignored workspace file `.mathlottery/network.json`:

```json
{
  "HTTP_PROXY": "http://proxy.example.invalid:8080",
  "HTTPS_PROXY": "http://proxy.example.invalid:8080",
  "NO_PROXY": "localhost,127.0.0.1,::1"
}
```

Replace the placeholder with your reachable proxy and restrict the file with `chmod 600 .mathlottery/network.json`. Only `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` and their lowercase forms are accepted. An existing environment variable wins over its uppercase/lowercase pair in this file, including an explicit empty value. The file is limited to 16 KiB and must be a regular, unlinked file; do not add account tokens or `CODEX_HOME`.

CLI, server and worker startup load these defaults for their own processes. They do not change the parent terminal, copy network settings into reports, or alter Windows/WSL networking. **Restart the existing server after changing its environment or network defaults**; running `serve` again can merely print the already-running instance's address. Existing research workers keep their process environment. A status timeout does not erase the login or establish that signing in again is necessary.

Keep loopback traffic direct with `NO_PROXY`. **The proxy address is for outbound requests, not the browser workspace.** Open the UI address printed by `serve`:

- The default listener is `127.0.0.1`, preferring port `8765`. A matching service is reused; occupied ports cause retries on subsequent ports, up to 20 binding attempts. WSL startup also skips Windows-reserved ports when that information is available. Use the actual printed port, or choose a preferred one with `mathlottery serve --port 9001`. `--open` asks to open the browser.
- Windows browsers normally use the printed `http://localhost:<port>` address through WSL forwarding. Diagnose both sides separately: in Linux, run `curl --noproxy '*' http://localhost:9001/`; in Windows PowerShell, use `curl.exe --noproxy '*' http://localhost:9001/`. Replace `9001` with the actual port. Linux-local success alone does not establish Windows reachability.
- `mathlottery serve --wsl-direct` explicitly broadens the listener and prints a direct WSL address, with allowed peers limited to loopback, that WSL address and its Windows gateway. It is optional; `--loopback-only` retains the default and cannot be combined with it. MathLottery does not automatically change port mappings, firewall rules, WSL settings or proxy configuration.

See the [troubleshooting checklist](usage.md#troubleshooting) for other startup errors.

<a id="budgets"></a>
## Budgets and usage

```yaml
budget:
  max_wall_time_minutes: 180
  max_iterations: 50
  solve_until_budget_exhausted: false
  finalize_minutes: 5
  max_input_tokens: null
  max_output_tokens: null
  max_external_cost_usd: null
backend:
  native_turn_timeout_seconds: null
```

| Control | What it means |
| --- | --- |
| Active-time budget | Includes research and independent evidence checks; excludes paused time. Resume values replace the total limit, not add more time. |
| `max_iterations` | Research handoffs, not each native tool call or an entire attempt to solve the problem. |
| `solve_until_budget_exhausted` | Native standalone Solve only. When `true`, save every candidate and continue research and self-checking until the active-time limit, including after a complete claim. Defaults to `false`. |
| `finalize_minutes` | At the time limit, native Solve gets one final call in the same research session, with up to this many extra minutes. Defaults to `5`; `0` disables it. Also applies when native `run` reaches its time limit in the Solve phase. |
| Input/output token limits | Use actual backend reports, checked between calls. A call can exceed the threshold; unreported usage remains unknown. |
| `native_turn_timeout_seconds: null` | A native call may use the remaining overall time budget. |
| `chat.request_timeout_seconds` | Timeout for one HTTP request, not the total time the remote model may think. |
| `max_external_cost_usd` | Only `null` or legacy `0`; `0` blocks API-funded calls, including Codex API and paid Solve slots. `null` delegates spending controls to the provider account and does not mean free usage. |

In native Solve, a `PARTIAL` or `UNKNOWN` candidate, or one with unresolved mathematical obligations, is a saved checkpoint: research continues in the same session while budget remains. By default, a candidate can finish standalone Solve early only with `conclude: true`, an explicit `COMPLETE` or `COUNTEREXAMPLE` scope, and an empty `remaining_obligations` list. This records the solver's claim; correctness, original-problem coverage and novelty still require Verify. In `run`, partial candidates can receive independent reviews, but even a positive review does not end research as a full solution.

Enable **Use full Solve time budget** in the browser's budget settings or Resume form to keep standalone Solve researching and checking its own candidate after a complete claim. It reuses the saved research session and immutable candidate history; it does not launch Verify or Organize. Other limits and interruptions below still apply. Resume preserves this setting when omitted, and its time value remains a cumulative total: `360` minutes means six hours including previously recorded active time.

For a new CLI Solve task, set `budget.solve_until_budget_exhausted: true` in `config.yaml`. CLI resume preserves the saved value; use the browser Resume form to change it for an existing task.

When the research time expires, the browser shows **Wrapping up**. The agent must stop exploring and save its current result, supporting materials, remaining obligations and a clear scope such as partial or unresolved. This is one bounded call, not an open-ended extension: a `360`-minute research budget with `finalize_minutes: 5` permits at most five additional minutes for wrap-up. Its active time and reported usage are still recorded. A submitted wrap-up candidate ends execution without automatically starting Verify or Organize or upgrading correctness or novelty. **Wrapped up** means the result was saved, not that the original problem was solved.

If the agent cannot submit a wrap-up result within that allowance, MathLottery saves a local checkpoint summary and explicitly reports that no agent wrap-up summary was obtained. This fallback does not invent a final proof or claim completion. User stop requests, provider failures and other hard limits can interrupt wrap-up too; it does not bypass them. Configure the allowance in `config.yaml` before creating a task; existing tasks retain their saved configuration.

A model's `stop` milestone during regular Solve saves progress and continues. The user's **Stop task** or CLI stop request is still honored. Iteration or token limits, provider quota, timeouts and errors can interrupt work before the configured research time is used. More time does not guarantee a solution. These continuation and wrap-up rules apply to native execution; the legacy structured protocol retains its existing termination behavior.

MathLottery does not estimate dollar costs, subscription balances or third-party tool fees. Configure API spending controls with the provider. Time/token budgets do not cap RAM, disk or all subprocesses. In particular, `tools.memory_mb: 512` applies to the legacy Python worker, not native Codex or Lean/Lake. Read [resource controls and measured Lean usage](resources.md) before increasing concurrency or compiler limits.

<a id="evidence"></a>
## Discovery context and proof evidence

### Carry Find into Solve

Choose a shortlist entry in the browser, or use `solve --from-find <find-run-id> --problem <problem-id>`. This captures a frozen Find dossier for the selected problem, including source assessments, research notes and permitted working files. Plain `solve --problem` reuses the statement without this explicit dossier handoff. Credential storage, binary caches and mutable sessions are not shared; omissions are recorded.

| `discovery` setting | Default |
| --- | --- |
| `context_max_files` | 300 files |
| `context_max_file_bytes` | 8,000,000 bytes per file |
| `context_max_total_bytes` | 32,000,000 bytes total |
| `chat_context_max_bytes` | 256,000 bytes of inline text for Chat |

Codex receives the frozen files in `discovery-context/`; Chat receives bounded text inline because hosted tools cannot read local files. Find assessments and omitted material remain visible, rather than becoming proof or a guarantee that the problem is open.

### Attach sources to an independent Verify

**CLI `verify --from-run` copies the candidate, not the solver workspace.** In the browser, select required proof files explicitly before starting Verify. The source task must be idle, and the displayed candidate ID/checksum must still match. Selected bytes are frozen and hashed; later edits cannot alter that review's input.

| Evidence | Supported scope |
| --- | --- |
| Lean/project sources | `.lean`, `lean-toolchain`, `lakefile.toml` inside the solver's `workspace/`. |
| Proof texts and certificates | `.md`, `.txt`, `.json`, `.csv`, `.py` under `workspace/proof/` or `workspace/formal/`. Scripts are not automatically executed. |
| Size limits | Up to 20 files; 1,000,000 bytes each; 2,000,000 bytes total for Codex or 128,000 bytes of inline source for Chat. |
| Excluded | Linked files, hidden/cache/build directories, credentials, solver history and previous reviews. |

Codex receives attachments under `submitted-evidence/` in its separate review workspace. Results can also list allowed files from review workspaces for downloading, but these are not automatically selectable as new solver attachments. Downloads are individual text files, not an archive of a complete Lean installation.

For independent Lean checks, prepare compatible Lean, `leanchecker`, bubblewrap, `prlimit` and prebuilt libraries. The reviewer must request the attached modules and named theorem declarations. Configure trusted library paths with `verification.lean_library_paths`; the checker never installs dependencies or executes submitted Lake hooks.

| `verification` setting | Default limit |
| --- | --- |
| `max_sources` / `source_timeout_seconds` | 12 cited URLs / 60-second collection budget per milestone; an in-flight request uses `tools.web_timeout_seconds`. |
| `formal_timeout_seconds` | 120 seconds total, configurable up to 1,800 seconds and bounded by remaining task time. |
| `formal_memory_mb` | 2,048 MB Lean internal threshold; one worker and a 64 MiB thread stack. |
| `formal_address_space_mb` | 8,192 MB per-process virtual-address-space ceiling, including reserved/mapped memory; not measured RAM or a global RSS cap. |
| `formal_max_object_mb` / `formal_max_total_object_mb` | 16 MiB per compiled file / 960 MiB monitored total output; temporary outputs are removed after checking. |

Successful kernel replay records the checked declarations and trust assumptions; it can support `PARTIALLY_VERIFIED`, not automatically certify a full new solution. Natural-language/formal equivalence and novelty remain separate. Missing tools, timeouts or resource failures are incomplete checks. For the full configuration, allowed axioms, module layout and source-receipt policy, see [evidence requirements](evidence.md).

<a id="recovery"></a>
## Saved sessions and recovery

Use [stop, resume and report commands](usage.md#operations) to continue existing work. SQLite in `.mathlottery/` is authoritative; candidate versions are immutable. Reports and `metrics.json` summarize checkpoints, stage timings, handoff failures, usage and review outcomes. Missing historical measurements remain unknown.

- Codex resumes its exact session in the dedicated home. Do not drive that active session simultaneously from another Codex client. A session absent from that home is not recovered by copying a personal login.
- Chat polls background responses and continues with `previous_response_id`. If a response ID was saved before a connection failure, recovery retrieves it instead of creating a second response. Failure before an ID arrives remains uncertain; inspect provider records before deciding to create a new run.
- Stop/Ctrl+C request cancellation. Saved output survives, but stopping does not guarantee a complete candidate submission or immediate remote cancellation. Pending requests must be recovered before changing backend.
- Browser workers continue when the page or UI server closes. Restarting the UI reconnects to saved state and does not automatically relaunch dead workers. Use an explicit stop request to stop research.
- Shutting down or restarting the host/WSL stops local workers. Restart `mathlottery serve`, then resume the existing task. For an interrupted native Codex worker with a matching resource snapshot, elapsed time is bounded by the last saved sample, excluding subsequent downtime; the final unsampled interval is unknown. This does not freeze remote Chat responses that may still be running, or invent missing measurements for older runs.
- Hosted responses/containers have retention limits; local checkpoints cannot recreate expired remote context. External tool side effects are not guaranteed exactly once; inspect recorded files and receipts during recovery.

`resume --message` adds direction to the original workflow. CLI backend changes retain separate backend context IDs and pass recorded research answers forward; they do not create identical tool environments. Independent reviews start separate contexts without the solver's conversation. See [architecture and recovery](architecture.md) for implementation details.

<a id="legacy"></a>
## Compatibility, offline demos and development

Ordinary research uses `execution: native`. `manual` is the explicitly named handoff backend; `work` aliases `codex`, and `--mode` aliases `--backend`. Historical handoff `chat` checkpoints remain manual on recovery and never silently become paid API calls.

```bash
mathlottery run --backend manual --prompt 'Investigate this mathematical problem...'
mathlottery submit --run <run-id> --file response.md
```

For the legacy JSON/tool protocol, import the educational problem first, then submit the generated task's response format:

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery run --backend manual --execution structured --problem odd-sum
mathlottery submit --run <run-id> --file response.json
```

The [protocol reference](protocol.md) describes the schema. Only `manual` requires transferring answers by hand; `codex` and `chat` invoke the agent automatically.

With development dependencies installed, offline checks can run without model usage:

```bash
mathlottery demo
mathlottery demo --case incorrect
pytest -q
ruff check .
```

Demos use fixed review fixtures and do not measure a model's mathematical ability. Follow [validation methods](local-validation.md) for integration checks; keep local audit scripts and logs in ignored `audits/codex_audits/<timestamp>/` directories. Curated, compact examples belong in the [showcase](../showcase/README.md). MathLottery does not automatically commit or push research files.
