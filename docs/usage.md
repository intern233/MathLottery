# Installation and usage

English | [简体中文](usage.cn.md)

[Browser quickstart](#local-browser-workspace) · [Terminal workflows](#cli) · [Backend setup](#backends) · [Troubleshooting](#troubleshooting)

MathLottery has two entry points. Both use the same workspace, configuration, accounts and saved results.

| Entry point | Use it for |
| --- | --- |
| **Browser: `mathlottery serve`** | Find problems, choose one to solve, review candidates, and organize reports. Start here. |
| **Terminal: `find`, `solve`, `verify`, `organize`, `run`** | Run individual stages or automate the research pipeline. |

The entry point is separate from the model connection: **Codex** uses the official CLI and a dedicated MathLottery login; **Chat** uses an API key and the Responses API. [Compatible providers](configuration.md#providers) are also configurable.

## Local browser workspace

<a id="install"></a>

### 1. Install MathLottery

Use **Linux or WSL 2**, with Git and Conda installed. In WSL, run these commands in the Linux terminal. If you already have the repository, enter its directory and skip the clone step.

```bash
git clone https://github.com/intern233/MathLottery.git
cd MathLottery
conda env create -f environment.yml
conda activate mathlottery
mathlottery init
```

The environment file installs Python and the project dependencies, including the research tools. `init` creates local storage and a default `config.yaml` if it is missing; it does not overwrite an existing file. Initial diagnostics may report that Codex is not installed/signed in or that Chat has no API key. Configure the backend you will use in the next step.

For an existing `mathlottery` environment, update the project installation with `python -m pip install -e '.[dev,research]'`.

**Lean is optional for the first run.** For planning, reserve 2–4 GiB of available RAM and 3–5 GiB of disk for one remote workflow; a Lean/mathlib setup needs substantially more. These are allowances, not measured minimums. Read [resource requirements](resources.md) before installing Lean or starting large local experiments.

### 2. Prepare Codex

The default backend is Codex. Install the [official Codex CLI](https://learn.chatgpt.com/docs/cli) in the **same Linux/WSL environment**, then check `codex --version`. If Node.js/npm is already installed there, one installation option is:

```bash
npm install --global --prefix "$CONDA_PREFIX" @openai/codex
hash -r
codex --version
```

Conda must be activated for this command. Node.js/npm is not included in `environment.yml`; the official CLI page also provides installation without npm. [Official package instructions](https://github.com/openai/codex#installing-and-running-codex-cli)

Already have a working CLI? Skip installation. Prefer an API instead? Skip Codex setup and follow [Chat API configuration](#chat-api) before starting the server.

### 3. Start the page and sign in

```bash
mathlottery serve
```

Open the **address printed in the terminal**. The preferred port is `8765`; the actual port may differ. On WSL, use the printed `http://localhost:<port>` address in your Windows browser. Keep the server terminal open. There is no separate frontend build or installation.

In the **MathLottery account** panel, choose **Sign in with ChatGPT** and complete authorization on the official page. Your ordinary Codex CLI / IDE login stays separate. The same account can be used, but its quota is shared. Device-code login may need enabling in ChatGPT security settings. [Authentication guidance](https://learn.chatgpt.com/docs/auth)

Select the provider, model and reasoning effort in **Model for this task**. For example, `gpt-6-astra` is a model ID and `max` is a separate effort setting, when supported by your account. Starting a task uses the selected backend's quota or API billing. For a first test, reduce the time budget under **Budget & agent settings**.

### 4. Run a workflow

| Stage | What you do | What you get |
| --- | --- | --- |
| **Find** | Enter preferences, for example: “Find a precisely stated public open problem with recent status evidence, a small scope, and potential for Lean verification.” | A shortlist with sources, open-status evidence, difficulty, verification and Lean feasibility estimates. |
| **Choose → Solve** | Click **Choose this problem**, check **Your choice**, then **Start solving**. Add task instructions if needed. | Research records and candidate proofs, or a recorded partial/unsuccessful attempt. Choosing alone does not start solving. |
| **Verify** | Click **Verify latest candidate**, select any needed proof source files, choose review settings, then start verification. | A separate review with issues, evidence gaps and the scope actually checked. |
| **Organize · optional** | After a review, click **Organize for expert review**. Choose the model, then **Create expert report**. | Chinese and English reports, each in Markdown and PDF, explaining the argument, its materials and the review findings. [Report setup](#organize) |

You can also skip Find: in **Solve**, choose **Enter a new problem** and supply its statement. For a small first test, try “Prove that the sum of the first n positive odd integers is n² for every nonnegative integer n.” This tests the workflow using a known result; it is not an open-problem discovery.

History groups Solve, Verify and Organize attempts by problem; a Find shortlist remains its own entry. Select a record to inspect its results. **Run completed** describes task execution, not proof correctness or novelty. Read the coverage, proof evidence, review issues and remaining obligations together. See [how to interpret evidence](evidence.md) and the [result showcase](../showcase/README.md).

Closing the page or UI server does **not** stop background research. Use **Stop task** or `mathlottery stop <run-id>`. Starting the server again reconnects to saved state without automatically restarting stopped tasks.

The **Activity** tab shows recent observable tool events, the last activity time and sampled local process-tree memory. A queued task shows its queue position. New tasks share the workspace resource limits; the default is one run and one independent formal check at a time. Queue waiting before a run starts does not consume research time. [Resource controls](resources.md)

For review follow-up, expand **Key proof steps** or **Novelty obstacles** in the results. **Prepare focused follow-up** on an idle Find/Verify fills a targeted instruction; check the budget and explicitly continue the task. Old results without these assessments remain marked as unassessed. [Evidence requirements](evidence.md)

<a id="cli"></a>

## Terminal workflows

Activate the environment and run commands from the **MathLottery project directory**. Complete [backend setup](#backends) once; no running browser server is needed for terminal research.

| Command | Behavior |
| --- | --- |
| `mathlottery find` | Find and save a shortlist, then stop for your choice. |
| `mathlottery solve --problem <problem-id>` | Solve a saved problem. Use `--prompt` for a new statement. |
| `mathlottery verify --from-run <solve-run-id>` | Independently review the latest candidate from a Solve run. |
| `mathlottery organize --from-run <verify-run-id> --language en` | Create Chinese and English expert reports; prefer English for default exports. |
| `mathlottery run` | Automatically find a problem, solve and review; it does not pause for your selection. |

### Find → choose → solve → verify

```bash
mathlottery find --query 'Find a small, precisely stated open problem suitable for Lean; check original sources and later work' --count 3
mathlottery problems
mathlottery solve --from-find <find-run-id> --problem <problem-id>
mathlottery verify --from-run <solve-run-id>
```

Run these **one at a time**. Replace `<find-run-id>`, `<problem-id>` and `<solve-run-id>` with the IDs printed by the preceding commands; do not paste the angle-bracket placeholders literally. Inspect the Find report before selecting. `--from-find` passes the selected problem's frozen research dossier to a new Solve session, while preserving the original Find record.

`verify --from-run` includes the candidate, statement and references; it does not automatically copy workspace proof files. To include Lean or other proof sources as frozen attachments, use the browser Verify form. [Evidence inputs and limits](configuration.md#evidence)

### Supply your own problem

```bash
mathlottery solve --prompt 'Prove that the sum of the first n positive odd integers is n squared for every nonnegative integer n' --budget-time 10m
```

Or import the bundled example and reuse its problem ID:

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --problem odd-sum --budget-time 10m
mathlottery verify --problem odd-sum --proof examples/odd_sum.proof.md
```

That last command reviews the supplied example proof. Use `verify --from-run <solve-run-id>` to review your solver's candidate instead. A supplied problem is not automatically classified as open or new.

<a id="organize"></a>

### After Verify: organize an expert reading report

Choose **Organize** in the browser, or run:

```bash
mathlottery organize --from-run <verify-run-id> --language en
mathlottery export <organize-run-id> --format markdown --language en --output report.en.md
mathlottery export <organize-run-id> --format pdf --language zh
mathlottery export <organize-run-id> --format bundle --output expert-reports.zip
```

Replace the run-ID placeholders with actual IDs. Organize always generates **both Chinese and English** versions from the same evidence. Its `--language en|zh` option selects the default export language; it does not restrict the generated versions. On `export`, `--language` selects one saved version. `--instructions` can specify an audience or emphasis. Organize uses the same model configuration and `--backend`, `--model`, `--reasoning-effort`, `--reasoning-mode`, `--budget-time` and `--max-iterations` overrides as research commands. It starts a separate model task and uses quota; merely selecting a source does not.

The source must be idle and contain a recorded review. An inconclusive or negative review is also eligible. The report explains the statement, assumptions, proof strategy, lemmas and derivations, and preserves review issues, formal-check scope and novelty uncertainty. It reconstructs saved visible work; it is not hidden model reasoning or a new verification.

New reports begin with a deterministic **Expert briefing**, generated from the frozen dossier in both languages. It summarizes the problem, candidate, proof roadmap, Lean evidence and outstanding issues, followed by an evidence index. Long records are explicitly excerpted; the complete statements and checks remain in the full report and linked frozen dossier. Repeated obstacles are grouped without hiding historical failures or unresolved IDs. Use the navigation links to jump to the full exposition, including in the PDF. Exporting an old report preserves its content and briefing version. To revise a report, resume its Organize task; this calls the model again.

For PDF output, install the [optional report dependencies](resources.md#reports) once. Both entry points save reports under `runs/<organize-run-id>/organized/`:

| Language | Markdown | PDF, when export succeeds |
| --- | --- | --- |
| Chinese | `report.zh.md` | `report.zh.pdf` |
| English | `report.en.md` | `report.en.pdf` |

`report.md` and `report.pdf` remain aliases for the preferred export language. The adjacent `manifest.json` records provenance, hashes and omissions; `materials/` holds the captured small source files. Binary dependencies, caches and historical Solve records without an explicit source link may be absent—check the manifest before sharing.

For handoff, use **Download report + materials (ZIP)** in the browser, or share the whole `organized/` directory. One bundle includes both saved language versions, their available PDFs and shared materials, preserving relative links. Downloading only Markdown or PDF does not include the referenced source files.

If one PDF export fails, both saved Markdown versions remain available and the other PDF can still succeed. After fixing the renderer, use **Retry PDF export** or the PDF export command above to rebuild the saved versions; this does **not** call the model again. Markdown export returns the expert report; `mathlottery report <organize-run-id>` continues to produce the task summary.

Older single-language reports remain readable and are labeled accordingly. PDF export does not translate them; start Organize from the reviewed source to create both versions.

### Automate the stages

```bash
mathlottery run
```

Without a supplied problem, `run` starts by finding one and proceeds automatically. Use `run --problem <problem-id>` or `run --prompt 'Your problem statement'` to start directly with solving. Review feedback can return to the original researcher. Budget exhaustion, errors or failure to find a proof can end the attempt; more time does not guarantee a solution.

`run` does not automatically start Organize. Request it explicitly after reviewing the result.

<a id="backends"></a>

## Configure the model connection

Both entry points read the workspace's **`config.yaml` for new tasks**. Edit the existing `backend` section instead of appending a duplicate YAML key. The browser can override settings for a new task without changing this file.

| Connection | What you need | Where to configure it |
| --- | --- | --- |
| **Codex** (default) | Official CLI and a MathLottery ChatGPT login | `backend.mode: codex`; sign in once through MathLottery |
| **Chat / OpenAI API** | API key and a supported model | `backend.mode: chat`; key in an environment variable |
| **Other Responses provider** | Compatible API endpoint, key and model | Named `model_providers` profile and `backend.provider` |

### Codex: use the same login for browser and terminal

The configuration created by `init` uses Codex with its default model settings. This minimal backend section is enough:

```yaml
backend:
  mode: codex
  execution: native
  model: null
  reasoning_effort: null
```

`null` uses defaults from **MathLottery's isolated Codex home**, not your personal CLI / IDE configuration. To choose explicitly, set `model` and `reasoning_effort`, for example `gpt-6-astra` and `max` if available. You do not need long model flags on every command.

Sign in through `mathlottery serve` once, then use the terminal commands with the same workspace. For login without the MathLottery page, use the [isolated terminal login instructions](configuration.md#account). Plain `codex login` signs into your ordinary Codex, not MathLottery.

<a id="chat-api"></a>

### Chat: use an API key

Replace the backend section below with your chosen model ID. `your-model-id` is a placeholder. The default hosted tools are web search and Code Interpreter; the model and account must support them.

```yaml
backend:
  mode: chat
  execution: native
  model: your-model-id
  reasoning_effort: null
  chat:
    reasoning_mode: null
    api_key_env: OPENAI_API_KEY
```

In the terminal that will launch MathLottery, enter the API key without displaying it or putting it in shell history:

```bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
```

Now start `mathlottery serve` or run a terminal workflow. Restart an existing server to pick up new environment variables. `.env` files are **not loaded automatically**. Keys belong in the environment, never in YAML or proof files.

`chat` is an automatic Responses API backend, not the ChatGPT website's Pro interface. The MathLottery Codex login does not authenticate Chat API calls. Optional `backend.chat.reasoning_mode: pro` is sent only when configured; use it only if the selected API model supports it. [Models, tools and provider configuration](configuration.md#models)

### Other providers

Configure a named Responses provider, then select it in the browser or through `backend.provider` in YAML. See the [complete provider example and compatibility requirements](configuration.md#providers). CLI `--backend` chooses the transport (`codex` or `chat`), not a vendor name; there is no `--provider` flag. Other vendors' native protocols require an adapter.

<a id="operations"></a>

## Inspect, stop and continue

Replace `<run-id>` with an actual task ID.

| Action | Command |
| --- | --- |
| Inspect saved status | `mathlottery status <run-id>` |
| Stop a task | `mathlottery stop <run-id>` |
| Continue an interrupted task | `mathlottery resume <run-id>` |
| Add direction, including to a completed task | `mathlottery resume <run-id> --message 'Check boundary cases and missing assumptions'` |
| Increase total limits | `mathlottery resume <run-id> --budget-time 6h --max-iterations 100` |
| Read the report | `mathlottery report <run-id> --show` |
| Export saved state | `mathlottery export <run-id> --format json --output checkpoint.json` |

Resume uses the task's **saved configuration**. Editing `config.yaml` or the browser model picker does not change an existing task. Budget overrides replace the **total limit**, not add more time; paused time does not count. A completed task needs `--message` to continue. [Budgets and recovery](configuration.md#budgets)

Terminal research runs in the foreground; browser tasks use background workers. Do not operate the same active task simultaneously from multiple clients.

<a id="files"></a>

## Where results are saved

| Path | Contents |
| --- | --- |
| `problems/<problem-id>/` | Reusable problem statements |
| `runs/<run-id>/report.md` | Result and evidence summary |
| `runs/<run-id>/candidates/` / `verification/` | Candidate versions and review records |
| `runs/<run-id>/workspace/` | Research files and visible answers |
| `runs/<organize-run-id>/organized/` | Chinese and English reports, per-version PDF status, source manifest and captured materials |
| `.mathlottery/` | Local state, sessions and the isolated Codex login |

These working directories and `config.yaml` are Git-ignored. The browser offers reports and small proof-source downloads; a source file alone does not establish successful formal verification. Curated, compact examples live in the versioned [showcase](../showcase/README.md).

<a id="troubleshooting"></a>

## Common setup issues

| Symptom | Next step |
| --- | --- |
| Codex unavailable / missing Linux dependency in WSL | Check `codex --version` in the server's terminal; install the Linux CLI there. [Installation and account details](configuration.md#account) |
| Login times out | Check that terminal's network/proxy, then restart the server. A timeout does not establish that the saved login expired. [Network setup](configuration.md#network) |
| Browser connection refused / port busy | Use the actual printed address; try `mathlottery serve --port 9001`. [WSL and port details](configuration.md#network) |
| Chat has no key or model | Export the API key in the launching terminal and configure a model; restart the server. [Chat setup](#chat-api) |
| Model or reasoning setting rejected | Choose one supported by the account/provider; MathLottery does not silently substitute another. [Model settings](configuration.md#models) |
| Lean fails or uses too much memory | Check the pinned toolchain, libraries, available RAM and concurrency. [Resource guide](resources.md) |
| Markdown is ready but PDF is unavailable | Install report dependencies, Chromium and needed fonts, then retry PDF export. [PDF setup](resources.md#reports) |

`mathlottery doctor` checks setup for both built-in backends without model inference. An unconfigured unused backend is not a reason to change the one you selected. Chat diagnostics check configuration, not connectivity, quota, model access or tool support.

CLI commands normally use the current directory. To select a workspace/configuration explicitly, put global options **before** the subcommand: `mathlottery --root ./research-workspace --config ./my-config.yaml find`. A relative `--config` path is resolved from the launching terminal's directory, not `--root`; without it, the default is `<root>/config.yaml`. `serve` can locate an editable checkout automatically; other commands do not. Use `mathlottery --help` or `mathlottery solve --help` for available options.

<a id="next"></a>

## Further reading

- [Configuration reference](configuration.md): providers, accounts, network, budgets, attachments and legacy modes.
- [Resource requirements](resources.md): Lean installation, RAM/disk planning and WSL.
- [Evidence policy](evidence.md) and [result showcase](../showcase/README.md): what a result actually establishes.
- [Architecture](architecture.md) and [local validation](local-validation.md): implementation, checks and recovery.
