# Resource requirements and Lean setup

English | [简体中文](resources.cn.md)

[Installation and usage](usage.md) · [Result showcase](../showcase/README.md)

MathLottery calls remote models. Its current backends do not require local model weights, a GPU, or CUDA. The browser workspace, agent client, files, and any tools launched locally still use your machine. Lean/mathlib checks and symbolic or numerical experiments can dominate local memory and disk use. Chat's hosted Code Interpreter uses a separate remote environment; installing Lean locally does not install it there.

Use Linux or WSL 2 for the current implementation. The environment file installs Python 3.12 and the project dependencies; the package requires Python 3.11 or newer. The Codex backend needs the official CLI. Lean and the [PDF report renderer](#reports) are optional, separate installations. The frontend has no separate Node.js build step.

Keep outbound network access available for authentication, model calls and research searches. Initial Python/Lean/mathlib setup also needs access to package, repository and cache hosts; downloads can be substantial and the extracted disk footprint is larger than the transfer size. Once prepared, a local Lean check with all dependencies present can run offline, while model-driven research still needs its backend connection and account allowance.

## Planning RAM, CPU and disk

These are **starting allowances for planning**, not measured minimum requirements or guarantees that every proof will fit. RAM below means available capacity for the workload after other applications have taken their share. On WSL, check both Windows and Linux: the host's installed RAM is not the RAM available inside WSL. Disk allowances cover a fresh environment, dependencies and some working space, excluding the OS and WSL swap.

| Workload | RAM to leave available | CPU / concurrency to start with | Free disk to reserve |
| --- | --- | --- | --- |
| Browser/CLI and one remote research session, without large local experiments | 2–4 GiB | 2 logical CPUs; one research task | 3–5 GiB |
| One Lean/mathlib proof check using existing compiled dependencies | 6–8 GiB | 2–4 logical CPUs; one Lean check at a time, starting with `-j 1` | 20–30 GiB on SSD |
| Rebuilding substantial dependencies, large symbolic proofs, or multiple local jobs | 16–24 GiB or more | Measure one job first; increase concurrency only with memory headroom | 40–60 GiB or more on SSD |

For a desktop also running an IDE and browser, 16 GiB of host RAM is a reasonable starting point for occasional cached Lean checks; 32 GiB or more leaves more room for demanding work. An 8 GiB machine can try the remote workflows and small checks, but should not start with a full mathlib source build. These are project recommendations, not an official Lean hardware specification.

More cores do not automatically make a build feasible. Concurrent compiler processes, editor Lean workers, and numerical-library threads compete for RAM. Large tactic searches or polynomial expansions can exceed the budget even with one thread. Runtime also varies with the proof, imports, filesystem cache and disk speed; allow for dependency downloads and preparation separately from model thinking time.

### A measured example

A historical check of `MedialAlgebra.lean` from the former medial-triangle showcase, on Linux x86-64 under WSL 2 with Lean 4.35.0 and that case's pinned mathlib revision, completed with the following measurements. That case is retained in `main` and Git history; these measurements are not benchmarks of the beta, Franel or mesh results selected on `ai4math`.

| Measurement | Observation |
| --- | --- |
| Compiler options | `-j 1 -M 2048 -o MedialAlgebra.olean MedialAlgebra.lean` |
| Dependency state | Compiled mathlib imports already present; no dependency build or download |
| Maximum resident memory, measured by GNU `time -v` | 2,081,860 KiB ≈ **1.99 GiB** |
| Wall time / exit status | About 34 seconds / `0` |
| Lean toolchain disk footprint | About 3.0 GiB |
| mathlib working copy, dependencies and existing build/cache files | About 7.2 GiB |

The RAM figure covers **one module's compiler process**, excluding the UI, agent, IDE and other jobs. It does not measure the whole showcase, a clean mathlib build, or peak WSL memory. The disk figures describe one installed version and cache state, not the archive download size or a fixed requirement. Other experiments have hit Lean's `-M 2048` limit during large polynomial normalization; that error records a limit being exceeded, not a measured peak RSS of 2 GiB. Keep the distinction between a configured limit and measured usage.

<a id="reports"></a>

## Optional expert report PDF setup

Organize uses the configured remote model to write both Chinese and English expert reports. Markdown is saved without a PDF renderer; PDF export runs Chromium locally. In the active MathLottery environment, from the project directory:

```bash
python -m pip install -e '.[reports]'
python -m playwright install chromium
```

If Linux reports missing browser libraries, install them with `python -m playwright install-deps chromium`; this may require administrator privileges. Chinese reports also need installed CJK fonts. For Debian/Ubuntu/WSL Ubuntu, `sudo apt-get install fonts-noto-cjk` is one option. Installing browser dependencies and fonts is a machine setup step, not a model call.

Chromium adds a platform-dependent browser download and cache occupying hundreds of MB; reserve additional disk beyond the basic Python environment. Each language export launches a local browser process tree; the two versions are rendered sequentially. Start with one task’s export at a time and measure its RAM for long reports; there is no measured universal minimum or process-tree RAM cap. Organize's model work uses its ordinary task budget; producing both complete versions requires more output tokens than a single-language report. PDF export and local retries use local CPU, RAM and disk, without another model call or a Lean compilation.

The renderer supports headings, tables, code, page numbers and common TeX mathematics in `$…$`, `$$…$$`, `\(…\)` and `\[…\]`. Mathematics assets are bundled, so rendering does not fetch scripts or fonts from a CDN. Unsupported TeX remains visible as source text with a warning. Images are replaced with descriptive text; review the captured original materials separately. Raw HTML is not executed, and embedded remote/local resources are not fetched.

If dependencies, Chromium or rendering fail, the saved Markdown remains available. Fix the environment, then click **Retry PDF export** or run `mathlottery export <organize-run-id> --format pdf`. Review export warnings and both generated PDFs before sharing, especially mathematical symbols, long formulas and Chinese text. PDF success is a formatting result, not proof validation. [Organize usage and output paths](usage.md#organize)

## Prepare Lean without rebuilding everything

Install Lean through [the official installation guide](https://lean-lang.org/install/). Use the project's `lean-toolchain` and pinned mathlib revision together. The [mesh formalization](../showcase/mesh-involutions/formal/README.md) includes a pinned project, but proves only part of its conjecture. The [beta source](../showcase/sun-beta-logconvexity/formal/README.md) has a historical main-theorem replay but lacks captured dependency pins; do not substitute another case's pins as evidence of its historical environment. MathLottery's environment setup and `doctor` do not install mathlib or benchmark its memory requirements.

Inside a Lean project that already declares mathlib as a dependency, retrieve compatible compiled artifacts before compiling proofs:

```bash
lake exe cache get
```

For a smaller import set, the cache tool also accepts module names, for example `lake exe cache get Mathlib.Algebra.Group.Basic`. This retrieves that module and its dependencies, not the imports of an arbitrary proof. Cache download/unpacking still consumes disk, network bandwidth and some local CPU/RAM. Preserve the version pins; when a matching cache is unavailable, investigate before launching a large source rebuild. [Mathlib cache documentation](https://github.com/leanprover-community/mathlib4/blob/master/Cache/README.md)

Import the modules the proof needs instead of importing all of `Mathlib` by default. Large tactics may benefit from smaller lemmas and explicit intermediate identities. For an existing `Proof.lean` with all imported modules already compiled, a conservative starting invocation from its **Lean project root** is:

```bash
env LEAN_NUM_THREADS=1 lake env lean -j 1 -M 2048 Proof.lean
```

`-j 1` sets Lean's processing threads; `-M 2048` sets Lean's internal memory threshold in MB. This is not an OS limit on the entire process tree, an exact RSS ceiling, or a promise the proof fits. Check the installed compiler's `lean --help`. If the limit is reached, inspect the proof/imports and available RAM before increasing it. `lake env lean` checks the file using the project's environment; it does not build missing imported modules. [Lake command reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)

When a build is necessary, start with `env LEAN_NUM_THREADS=1 lake build <target>` and a specific target. `LEAN_NUM_THREADS` controls Lean runtime concurrency; it is not a global RAM quota or a substitute for monitoring subprocesses. Do not assume `lake -j 1 build` is supported: Lake and Lean have different options. [Lake maintainer's concurrency guidance](https://leanprover-community.github.io/archive/stream/270676-lean4/topic/Lake.20parallel.20builds.html)

Kernel replay is a separate workload. For the already built mesh showcase project, use `env LEAN_NUM_THREADS=1 lake env leanchecker --verbose MeshPartial` initially; the module's mathematical scope remains partial. `--fresh` additionally rechecks imported dependencies and can take substantially more resources. Parallel module checks load multiple import environments, so measure before increasing threads. [Official lean-action guidance](https://github.com/leanprover/lean-action#run-leanchecker-on-a-project-with-a-mathlib-dependency)

For agent-driven work, put the desired toolchain, cache location and concurrency policy in **Task instructions**. For example: “Reuse the pinned Lean/mathlib environment; run one compiler at a time with `-j 1 -M 2048`; record peak RSS, exit status and any limit failure before attempting a larger build.” These instructions do not impose OS resource limits on native agent commands. The independent attached-source checker has the separate limits below.

## What the configuration actually limits

| Setting or control | Scope and limitation |
| --- | --- |
| `resources.max_concurrent_runs: 1` | Workspace-wide FIFO admission shared by browser and CLI research tasks. Other workspaces, IDE sessions and manually launched commands are outside this queue. Waiting does not consume the research time budget. |
| `resources.max_concurrent_formal: 1` | Separate workspace gate for the independent attached-source checker. It does not intercept Lean/Lake commands chosen by the native agent inside a run. |
| `resources.min_available_memory_mb: 256` | Wait before starting when Linux reports less `MemAvailable`. Set `0` to disable this headroom gate; unavailable measurements do not prevent admission. |
| `resources.memory_soft_limit_mb: null` | Optional cooperative stop when the sampled local executor and descendant RSS exceeds this value. Default is disabled. Not an OS quota, a strict peak bound, or a measurement of remote hosted tools. |
| `resources.sample_interval_seconds: 2` | Sampling interval for current/peak local process-tree RSS. Shared pages may be counted more than once, and peaks between samples may be missed. |
| `tools.memory_mb: 512` | Address-space limit for the legacy structured Python worker. It does **not** cap native Codex commands, Lean/Lake, the web server, or WSL. The legacy Lean checker does not use this memory setting either. |
| `tools.timeout_seconds: 15` | Legacy local tool timeout, including the legacy Lean checker; it does not impose a 15-second limit on native shell commands. |
| `verification.formal_memory_mb: 2048` | Independent attached-source checker only: Lean internal `-M` threshold. The separate `formal_address_space_mb: 8192` bounds per-process virtual address space (`RLIMIT_AS`), including reserved stacks and mapped libraries; it is not measured RAM. One Lean worker, 64 MiB thread stack, 120-second default total check timeout. Not a process-tree or WSL RSS cap. |
| `verification.formal_max_object_mb: 16` / `formal_max_total_object_mb: 960` | Independent checker compiler output: per-file size limit and monitored total size, in MiB. Proof objects can greatly exceed source size. Temporary compiled objects are deleted after checking; limits, sizes and hashes remain in the receipt. Not a quota on native research artifacts or the whole disk. |
| `verification.max_sources`, `source_timeout_seconds` | Independent citation retrieval: defaults to 12 URLs and a 60-second collection budget per milestone; in-flight requests use `tools.web_timeout_seconds`. PDFs use a 512 MB isolated parser. See [evidence configuration](evidence.md). |
| `budget.max_wall_time_minutes` / `backend.native_turn_timeout_seconds` | Active research time / individual native-turn duration, not RAM, CPU-thread or disk limits. |
| `budget.max_iterations` | Research handoffs, not the number of tool calls or child processes inside a turn. |
| `backend.native_max_log_bytes` | Limit checked against a native Codex call's event/stdout and stderr logs; not a quota for downloads, artifacts, all runs or Chat responses. |
| Lean `-M`, `-j`, and `LEAN_NUM_THREADS` | Controls on the invoked Lean runtime; not a hard limit on all tasks together. |

MathLottery prevents two workers from driving the **same run** at once and queues different runs under the workspace limits above. Each run snapshots its resource settings when created; when live requests have different concurrency settings, the strictest setting governs shared admission. Already running tasks are not forcibly terminated when a stricter request joins. Start one compute-heavy task at a time until measured headroom supports more. Closing the browser or UI server does not stop detached research workers; use **Stop task** or `mathlottery stop <run-id>`. A queued stop cancels admission without making a model call.

The task page distinguishes the current execution from cumulative resource observations:

- **Current execution:** queue position, current process-tree RSS, this execution's sampled peak and elapsed active/queue time.
- **Across resumes:** cumulative active time, cumulative queue time and the largest previously observed RSS. An execution is one admission/resume, not one model call; there can be several model calls inside it. Queued cancellation adds queue time without active time. Reported execution time includes controller work and is separate from the research budget's accounting.
- **History limits:** the projection retains the latest 20 execution summaries while totals continue accumulating. Old snapshots can recover only their last observed execution; the UI marks earlier history as incomplete. Unknown older peaks and durations are not reconstructed. Crash recovery stops timing at the last recorded sample, so time spent offline is not counted.

The activity stream combines observed agent events with controller stages such as source retrieval, formal compilation/kernel replay/declaration inspection, material capture and report rendering. Stage duration and status describe the operation, not whether the mathematical claim passed. A separate controller heartbeat records that its monitoring thread is alive; it is not new model output, a completion percentage, or evidence of useful progress. A stale heartbeat is marked separately and does not trigger a restart. The public stream is capped at 30 events and excludes shell commands, tool arguments, URLs, exception details and provider credentials. No new event does not establish that the model is stuck; hidden reasoning and hosted-tool memory are not observable. Raw research artifacts remain local.

The polling limits do not discard newly recorded history. Each native attempt appends sanitized visible events to `activity-events.jsonl`; the run appends controller starts/finishes to `controller-activity-events.jsonl` and completed/interrupted execution summaries to `resource-attempts.jsonl` and `formal-resource-attempts.jsonl`. Individual heartbeat samples are not archived. The JSONL download includes all supplied attempt streams, revalidates every field, replaces paths with stream numbers and states where older history is unavailable. It does not reconstruct old raw provider logs or claim that legacy runs were recorded completely. The default download limit is 16 MiB; oversized exports fail explicitly rather than silently truncating history. These append-only local files remain under ignored `runs/` and can grow over long campaigns.

Queue leases and status are stored in ignored `.mathlottery/resources/` and `runs/`; restarting the UI server does not lose ownership or start another invocation. A crashed executor is shown as interrupted and must be resumed explicitly. Identified orphaned local Codex processes are stopped before their slot is reclaimed; remote Chat background responses may continue until explicit resume/stop retrieves or cancels their saved response, without submitting a duplicate request.

The RSS soft limit requests cancellation through the existing checkpoint-preserving path. Detection and cancellation are asynchronous; memory can rise between samples or while a tool stops. Native agent shell commands share the run's overall measurement, but their individual parallelism is left to the agent. Applying a manual compatibility response also acquires a run slot. Local report-only PDF retries are outside the research queue. Use an OS/container limit for strict isolation.

If a hard cap for a whole process group is required, configure an OS/container resource limit that includes its descendants. MathLottery does not install such a limit automatically, and Codex's workspace sandbox is not a RAM quota. Likewise, time/token budgets do not reserve provider quota: credentials, subscription/API allowance, connectivity and local hardware are separate requirements. See [backend configuration and budgets](configuration.md).

## WSL 2 memory and swap

Check Linux's `free -h` and Windows Task Manager before starting a build. Leave capacity for Windows, the browser, IDE and other WSL workloads. WSL's `memory` cap applies to the VM across WSL 2 distributions, not just MathLottery. Swap uses disk and can reduce immediate memory pressure, but sustained swapping can make compilation very slow.

For example, on a **16 GiB host**, a starting VM configuration could be:

```ini
# Windows: %UserProfile%\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB
```

Adjust to actual free capacity and merge with existing settings. This example is not a requirement and does not guarantee large builds fit. Applying changes may require `wsl --shutdown` in PowerShell, which stops **all running WSL distributions and their jobs**; save work and stop tasks first, then restart WSL and check `free -h` again. MathLottery does not change these settings. [Microsoft WSL configuration reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)

## Measure usage and diagnose failures

On Linux/WSL, inspect current headroom and the largest resident processes without printing their command-line arguments:

```bash
free -h
df -h .
ps -eo pid,ppid,rss,comm --sort=-rss | head -n 15
du -sh .mathlottery runs audits
```

Run the last command from the MathLottery root after those directories exist. Also inspect the filesystem holding Conda/Elan if it differs from the project disk. `free`'s **available** column is more useful than **free** alone because filesystem caches can be reclaimed. `ps` RSS is a snapshot, not a peak; shared pages can be counted in more than one process. Windows' WSL memory figure includes more than the Lean process.

For an actual single-file measurement, install GNU `time` if `/usr/bin/time` is absent, enter the Lean project with cached dependencies, and replace `Proof.lean` with the intended file:

```bash
env LEAN_NUM_THREADS=1 /usr/bin/time -v lake env lean -j 1 -M 2048 Proof.lean
```

Read `Maximum resident set size (kbytes)`, elapsed time and exit status. On Linux, divide that RSS value by 1,048,576 for GiB. A timed Lake build's reported maximum is not the sum of all simultaneously running subprocesses; monitor the whole workload separately when comparing it with a VM limit. Keep raw logs and machine diagnostics in a new ignored `audits/codex_audits/<timestamp>/` directory, following the [local audit convention](local-validation.md#local-experiment-audits).

| Symptom | What to check next |
| --- | --- |
| `lean::memory_exception` / `excessive memory consumption` | Lean's own threshold and tactic/import costs; reduce the work or adjust the threshold within available RAM. |
| `Killed`, signal 9, or exit 137 | Check the permitted kernel/container/WSL logs for an OOM kill; the exit code alone does not establish the cause. |
| High swap activity and very slow progress | Reduce concurrent research/compiler/editor workers and inspect available RAM. |
| `No space left on device` | Check the project disk, toolchain disk, download caches, temporary storage and WSL host disk. |
| Missing `.olean` files or incompatible toolchain | Restore dependencies for the pinned versions before rebuilding. |

A resource failure is an incomplete check. Retain its exit status and log; it is neither a successful Lean verification nor evidence that the mathematical statement is false.

## Disk growth and cleanup

Toolchains, mathlib `.lake/` trees, compressed caches, source-build artifacts and repeated dependency versions can occupy many GiB. Research histories, downloaded papers, event logs and numerical outputs grow with use. There is no automatic total disk quota or retention policy. Budget for extracted files as well as downloads; extra environments or independent checkouts may duplicate dependencies.

Measure before deleting. Once all users of a cache have stopped, remove only identified, reproducible cache/build directories or unused toolchain versions. Keep the pinned sources and evidence needed to reproduce results. **Do not delete all of `.mathlottery/` to clear a build cache**: it also contains the state database, isolated account credentials and native sessions. Keep `problems/` and `runs/` if you want to retain research history. A Git ignore rule does not remove local files or reduce disk usage.

The [showcase](../showcase/README.md) contains compact source/evidence samples. Reproducing a Lean example downloads its large dependencies separately; those files are not bundled with the samples.
