# Proof graph, archives and peer collaboration

[中文](proof-board.cn.md) · [Supervised Solve](solve-teams.md)

This is a **Solve feature on the `ai4math` branch**, available with supervised coordination and an explicit researcher cap. It adds optional shared memory and cooperation to native Codex and Responses agents. Their tools, accounts and concurrency limits stay intact; Find, Verify and Organize remain separate.

## Discover first, open proofs when needed

The board is a directed acyclic dependency graph, not a strict tree: a lemma can support several conclusions. Prerequisites point to derived results. Compact nodes expose exact statements, assumptions, outstanding obligations, version hashes and review standing. Edges link to the derived result's archived proof chain. Full bodies, proof steps, justifications and materials load on demand. These are declared dependencies, not formal proof certificates.

Native agents keep ordinary file access and can use the supplied stdlib-only helper inside their workspace:

```bash
python board_client.py search 'boundary estimate'
python board_client.py search 'boundary estimate' --archived
python board_client.py explore 'researcher:lemma' --direction premises --depth 2
python board_client.py read 'researcher:lemma'
python board_client.py material <published-sha256> --offset 0
```

Search covers keys, titles, statements, assumptions, optional `tags` and `aliases`, with Unicode/punctuation normalization. It is lexical retrieval, not mathematical equivalence detection. Explore supports `premises`, `consequences` and `both`. Check exact conditions before reusing a theorem. Responses agents use `solve_board_search/explore/read/material/publish`; initial context contains graph metadata, not every derivation. Their configured hosted tools remain available.

## Publish with feedback

Native agents can preflight a complete message before queueing it:

```bash
python board_client.py validate draft.json
python board_client.py publish draft.json
```

The helper catches missing/unknown fields and basic type errors. The controller still validates proof-step ordering, dependencies, identity and immutable content. `bulletin/publications.json` records per-file publication/rejection receipts; the supervisor also sees rejected inputs and can advise a repair. Raw outbox files remain available. Repairing an envelope must not discard mathematical assumptions or gaps. Successful publication means stored, not mathematically approved.

## Reversible curation

The supervisor can return optional `board_curation` entries with `key`, exact `content_sha256`, `action` (`archive` or `restore`) and `reason`. This is separate from mathematical review. Archive hides default discovery entries; restore makes them visible again. Neither changes proof bytes, hashes, dependencies or review opinions. No source is deleted. Archived results remain searchable/readable, and a later dependent exposes its archived prerequisites. Objections and retractions still invalidate descendants across archive boundaries.

The controller protects live prerequisites, current registered research focus and unresolved objections. It rechecks current dependencies when applying a frozen decision. Invalid or stale curation leaves the batch unchanged and records feedback without aborting valid research.

Low-use suggestions consider age, recorded reads, dependents and unresolved reviews; they never archive automatically. **Direct native filesystem reads are not fully measured. Zero recorded reads does not mean a theorem is unused or unimportant.** Quiet routes must not be discarded solely for low counts. Archiving is not retraction; restoring is not approval.

## Activity registry and voluntary channels

The supervisor can optionally adapt how this board and collaboration are used; see [optional coordination adjustments](#optional-coordination-adjustments) below. Ordinary review, archive/restore and channels remain available with that option off.

The registry separates actual scheduler assignments/runtime state from dated, self-reported intent. Register meaningful changes of direction, focus lemma keys and requests for help, not every tool call. Earlier-attempt reports are historical; they cannot make an idle agent appear active. No mathematical completion percentage is inferred.

Group objectives and modes are **suggestions**. At the start and when changing direction, researchers declare their chosen `topic`, `approach`, `intent` (`explore`, `extend`, `check`) and, if useful, an `overlap_reason`. This is advisory coordination, not exclusive task ownership. A personal inbox shows related results, existing channels worth considering, and possible overlaps with current peer declarations. Matching is heuristic; deliberate independent verification remains allowed.

```bash
python board_client.py status
python board_client.py inbox
python board_client.py event '{"id":"work-1","action":"activity","summary":"Checking boundary cases","status":"seeking_help","focus":[]}'
python board_client.py event '{"id":"bounds","action":"channel_open","summary":"Compare endpoint bounds","invitees":["peer"],"focus":[]}'
```

Channel keys are `<creator>:<event-id>`. A peer joins and posts voluntarily:

```bash
python board_client.py event '{"id":"join-1","action":"channel_join","channel":"primary:bounds"}'
python board_client.py event '{"id":"reply-1","action":"channel_message","channel":"primary:bounds","body":"I will check the zero-parameter case."}'
python board_client.py channel 'primary:bounds'
```

Use a fresh event ID for each update. The controller binds identity and run; spoofed identity fields are rejected. The creator joins initially; invitations do not join peers. Any agent in the run can join, members can leave, and only the creator can close. Closed transcripts remain readable. Channels are public within a run, not private/cross-run messaging. They cannot spawn agents or change accounts/resources.

Invited non-members can use `channel_defer` or `channel_decline` with a brief `summary`; joining later remains possible. The inbox distinguishes pending/deferred invitations from membership and unread messages. Reading a channel through the helper or Responses tool acknowledges only the last event actually observed, so a concurrent reply remains unread. Direct filesystem reads are not tracked. Check for an existing topic before opening another channel; invitations never force a response or block exploration.

Native events are asynchronous: `outbox-events/` is ingested by the controller. Check `bulletin/event-errors.json` for errors and `bulletin/collaboration/events.json` for durable acceptance. Continue research if nobody replies. Responses uses `solve_board_inbox/activity/channel/event` for equivalent operations. Publish useful conclusions separately as immutable theorem messages with proof chains; channel agreement is never proof acceptance.

## Observe and recover

The browser's Solve panel offers **Proof graph & archive** and **Activity registry & collaboration channels**. Search/include archived nodes, follow prerequisite/consequence links, and expand entries to load proofs or transcripts. UI inspection does not count as an agent read.

| Workspace path | Contents |
| --- | --- |
| `bulletin/graph.json`, `bulletin/index.json` | Default graph and compact cards |
| `bulletin/archive/` | Complete index/graph and full versioned message projections |
| `bulletin/materials/` | Frozen proof/source files |
| `bulletin/agents.json` | Assignments, runtime state and self-reports |
| `bulletin/inbox.json` | Personal invitations, unread channels and advisory overlap/reuse hints |
| `bulletin/publications.json` | Native publication receipts and actionable rejection feedback |
| `bulletin/collaboration/index.json` | Channel directory and participants |
| `bulletin/collaboration/channels/` | Per-channel transcripts |
| `bulletin/collaboration/events.json` | Activity, read and channel event ledger |
| `bulletin/curation.json` | Archive/restore history and advisory candidates |

SQLite is authoritative; files are reproducible projections. Old `bulletin/messages/` paths remain valid. Publications, review opinions, visibility decisions and collaboration events have separate semantics/storage. Event and receipt replay is idempotent. Research files remain under ignored `runs/` directories.

## Optional coordination adjustments

In the browser's **Solve → Budget & agent settings**, select **Let the supervisor improve coordination**. It is **off by default**, requires explicit Solve parallelism and supervised coordination, and applies only to this task. The continuation form can enable or disable it when the task is idle. CLI users can set:

```yaml
solve:
  coordination: supervised
  parallel_agents: 4
  adaptive_coordination: true
```

At regular supervision checkpoints, the supervisor can propose a replacement coordination policy based on the board, activity registrations, discussions and researcher signals:

| Setting | Effect |
| --- | --- |
| Review interval | Requests periodic supervision after new evidence or meaningful researcher activity; 30–3600 seconds, or restore the configured default. Shared-slot availability still applies. |
| Minimum age / read threshold | Selects archive suggestions: 60–86400 seconds and 0–100 recorded reads. Defaults are 600 seconds and zero reads. This never archives automatically or bypasses protected dependencies. |
| Board guidance | Advice on publishing, finding and reusing intermediate results. |
| Collaboration guidance | Advice on voluntary exchanges, comparing routes and checking each other's arguments. |

Each `coordination_update` cites the frozen policy revision and actual evidence references, explains the expected benefit, and assesses the previous change. Counts and self-reports are observations, not a mathematical progress score. The supervisor can keep or revert a policy when the benefit is unclear. Invalid, disabled, stale or final-closing adjustments are recorded as rejected without interrupting a valid mathematical review. Successful changes commit with the supervisor checkpoint; they never edit `config.yaml` or apply to other runs.

The feature reuses the existing supervisor; it adds no optimization agent. More frequent review requests can consume more of the same call/token budget. Agent limits, credential routes, deadlines, proof standards and mandatory review coverage remain fixed. Guidance is advice, not new tool permissions or compulsory channel membership. Native agents read `bulletin/policy.json`; Responses agents see the same live policy through `solve_board_status` and `solve_board_activity`.

Task details show the current policy, before/after values, evidence, expected effects, prior assessments and rejection reasons. The latest ten entries appear in the browser; complete history is in `runs/<run-id>/solve/coordination-policy.json` and each projected `bulletin/policy-history.json`. Disabling restores configured defaults and deactivates saved guidance without erasing history. Re-enabling resumes this run's latest applied policy.

Implementation: `solve/board.py` for publications, `solve/board_reviews.py` for opinions, `solve/bulletin/` for navigation/archives/events/curation, `solve/coordination_policy.py` for optional versioned policy adjustments, `solve/board_tools.py` for Responses, and `web/static/solve-board.js` for the observer UI.

## Design references and limits

- [Danus](https://arxiv.org/abs/2607.06447) separates shared fact dependencies from exploratory memory. MathLottery preserves that distinction between theorem records and discussion.
- [LLM-based Multi-Agent Blackboard System](https://arxiv.org/abs/2510.01285) uses a shared request board with voluntary responses. This motivates advisory work declarations and opt-in invitations here.
- [AgentNet](https://proceedings.neurips.cc/paper_files/paper/2025/file/9a379c1b05793d1c42dc832269834515-Paper-Conference.pdf) studies decentralized routing and evolving connections. We borrow the direction of autonomous cooperation, not its learning algorithm or performance claims.
- [AgentScope](https://arxiv.org/abs/2402.14034) emphasizes message exchange and fault tolerance. Publication preflight and explicit failure receipts address that engineering concern.

These are design influences, not evidence that this implementation improves mathematical success. Overlap hints cannot prove theorem equivalence; supervisor opinions remain fallible. Evaluation should compare equal-budget runs, actual reused dependencies, unanswered invitations, idle time and repeated work, rather than message counts alone.
