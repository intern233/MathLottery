<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/mathlottery-logo-dark.svg">
    <img src="assets/mathlottery-logo.svg" width="720" alt="MathLottery">
  </picture>
</p>

<h2 align="center">Token is all you need.</h2>

<p align="center">
  English | <a href="README.cn.md">简体中文</a>
</p>

<p align="center">
  <a href="docs/usage.md">Usage</a> · <a href="showcase/README.md">Result showcase</a>
</p>

**One agent. One shot at a mathematical discovery.**

MathLottery is a local mathematics research project: let an agent find public problems, attempt solutions, and review its results. We want to see whether people without a mathematics background or large computing resources can use AI to produce something new in mathematics.

The idea came from a collection of mathematical research results published by OpenAI. OpenAI reported that each result used, on average, compute equivalent to roughly three hours of ChatGPT Pro thinking; the results were produced by internal models. That comparison makes us want to try, but it does not mean the publicly available Pro mode already has the same capabilities. [Source: OpenAI's mathematics progress report](https://openai.com/index/sharing-ai-progress-in-mathematics/)

Our goal is simple: **give one agent a serious chance to explore and aim for a mathematical result worth checking.**

## What we want to do

### 1. Find: which problems are worth trying?

> I am not a mathematician. Even finding publicly stated, unsolved problems is difficult.

Start by asking the agent.

Let it search the web, read original papers and problem lists, and check the exact statements, existing progress, and whether a solution has already appeared. It should then explain why a problem is worth attempting, given its scope, the available tools, and the research budget.

You can also give it a problem you care about. Start with a small lemma or ask it to “solve Goldbach's conjecture.” You choose the research goal; the reasons for choosing a problem and the evidence for its unsolved status need traceable sources.

**Find → your choice → Solve:** compare the shortlist’s difficulty, verification and Lean feasibility, then choose a problem yourself. The solver receives the selected Find dossier and research notes; the recommendation never starts solving automatically.

### 2. Solve: one agent is enough to get started

> I do not have the resources for thousands of parallel agents. I can let one agent keep working.

Give it a problem, some time, and access to tools. Let it decide how to proceed: search the literature, break down the problem, derive lemmas, write programs, run experiments, look for counterexamples, and change direction when an approach fails.

We built a harness—the framework that runs and records this research process. It preserves sessions, files, and intermediate results, supports pausing and resuming, and lets you add guidance so the same research agent can build on its earlier work.

The “lottery” refers to the uncertainty of research. An attempt might produce a complete proof, a partial result, a counterexample, or an approach that has been ruled out. Each outcome deserves an honest record.

### 3. Verify: did we actually win?

> The agent wrote a proof, but I cannot follow it or tell whether it is correct.

Ask an agent to review it in a separate review session. It checks the problem, candidate proof, and references for missing assumptions, circular reasoning, calculation errors, and counterexamples. It also checks whether the supposedly new result already exists.

When it finds a problem, send specific feedback back to the original research session for revision. When it cannot reach a conclusion, keep that uncertainty in the record.

**Passing an agent review is only preliminary evidence.** Finite experiments and model approval cannot replace a mathematical proof. Calling a candidate a reliable new result requires stronger proof checking, with formal verification where suitable and review by mathematics experts.

## What the harness provides

We want to preserve as much of GPT's native agent capability as possible, leaving research methods and tool choices to the agent. MathLottery organizes each attempt into a research record that can be resumed, revisited, and checked:

- **Continuous research:** preserve the same research session and working files, resume after interruptions, and add guidance along the way.
- **Native tools:** use official Codex search, shell, computation, and file tools, with a dedicated MathLottery login and tool configuration.
- **Research budgets:** set limits such as time and record the usage actually reported by the backend, giving each attempt a defined scope.
- **Results and review:** save candidate proof versions, references, review feedback, and research reports, distinguishing progress, conjectures, and verification evidence.
- **Evidence checks:** independently retrieve quoted sources, record missing evidence and original-problem coverage, and recheck attached Lean sources with bounded execution receipts. See the [evidence policy](docs/evidence.md).
- **Local browser workspace:** launch `mathlottery serve` to find problems, start solutions, review proofs, and manage research history from your browser.

The code provides three independent workflows: **`find`, `solve`, and `verify`**. The `run` workflow connects them into a full research pipeline. Finding produces reusable problem statements, solving saves candidate proofs, and verification produces a separate review.

Each workflow supports two ways to connect an agent: **`codex`** uses persistent official Codex sessions and native tools; **`chat`** automatically calls the OpenAI Responses API with persistent context, web search, and code execution. The Chat API requires separate credential and model configuration; available capabilities depend on the account and tool setup.

Contributions to the harness are welcome: improve problem selection, reduce repeated exploration, strengthen reviews, or try your own research strategy.

## Result showcase

[Explore three experimental case studies](showcase/README.md): an equidistribution proof for four mesh patterns on involutions, a medial-triangle inequality proof involving a moving point, and a counterexample to a conjecture on stepwise irregular graphs. The samples include complete written proofs, review summaries, compact verification records, and the available Lean source files or counterexample checkers. Large dependencies and runtime caches are excluded.

Each case states its formal verification scope and novelty status. The mesh-pattern proof has partial Lean verification, the triangle inequality has full formal verification, and the graph counterexample includes an executable certificate. Novelty remains “potentially new” or “unknown”; an independent AI review is not expert certification. Each case's review summary and verification records explain the evidence behind these assessments.

## Take your first shot

Choose the backend, model, and reasoning mode in `config.yaml`, then specify the research task when you run the system. Installation, configuration, and commands are covered in separate guides:

For the [browser interface](docs/usage.md#local-browser-workspace), run `mathlottery serve` and open the printed local address. It starts on loopback, preferring port `8765` and skipping occupied or Windows-reserved ports; Windows browsers use the printed `localhost` address through WSL forwarding. The **MathLottery account** panel supports official ChatGPT device-code sign-in with login state isolated from your local Codex CLI / IDE. Sign in once in MathLottery; you may use the same account, with the same account usage limits. The interface shares the MathLottery CLI's local problems, checkpoints, and reports.

- [Installation and usage](docs/usage.md): environment setup, the three workflows, Chat API / Codex configuration, and pausing and resuming.
- [Resource requirements](docs/resources.md): RAM, disk and CPU planning, measured Lean usage, caches, and WSL settings.
- [Architecture and recovery](docs/architecture.md): persistent sessions, saved state, and separate reviews.
- [Validation methods and scope](docs/local-validation.md): how to check the system and what those checks establish.
- [Legacy structured protocol](docs/protocol.md): compatibility with old checkpoints and offline demos.

You now know how to enter the lottery for an “AI mathematics result.”
