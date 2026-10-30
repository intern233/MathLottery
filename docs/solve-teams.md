# Solve research teams

[中文](solve-teams.cn.md) · [Usage](usage.md)

In the browser, open **Solve → Budget & agent settings** and set **Solve parallelism**
and optionally **Maximum research groups**. Parallelism caps simultaneous researchers
across all groups, including peer checks; the group limit caps active groups. For example,
6 researchers and 2 groups allows two groups of 3, or one group of up to 6. Neither cap
must be filled. Supervision is separate overhead and uses no research-group slot.
The settings apply to this task; Resume can change them at the next invocation when using a shared backend.

To give each researcher its own Codex login, Codex API key or independent Responses API connection, open the separate **Agent configuration** page (`/agents`), then enable **Use configured agent slots** in Solve. [Configure slots](agents.md). Each slot keeps its connection and session across regrouping. The first slot also supplies supervision before the round and wrap-up after it. A task with explicit slots keeps its saved roster on resume; changing its size or connections requires a new task.

For new CLI tasks, set the project configuration:

```yaml
solve:
  parallel_agents: 6
  max_groups: 2
  supervisor_timeout_seconds: 120
```

Or use `mathlottery solve --problem <problem-id> --parallel-agents 6 --max-groups 2`.
For an existing task: `mathlottery resume <run-id> --max-groups 1`.

`max_groups` accepts 1–32 and requires an explicit `parallel_agents` setting. When
`max_groups` is `null`, groups are limited only by the total researcher count. Each
active group needs at least one researcher, so the effective limit is the smaller
of the two caps. This is an active-group limit, not a lifetime limit on saved groups;
inactive sessions and findings remain available after reducing it. Blank browser
fields keep the applicable configuration or saved task values.

For `parallel_agents`:

- `null` (the compatibility default) preserves existing native delegation settings.
- `1` uses the original continuous researcher, without an additional supervisor.
- `2`–`32` enables supervised groups. This is a ceiling, not a promise to fill every slot.
- This release supports standalone native `solve` through Codex or Chat/Responses.
  Other workflows, the composed `run` workflow, and manual/structured execution do
  not gain this scheduler. The browser rejects Solve overrides on other workflows.

## Scheduling and context

At natural round boundaries, a persistent supervisor reads the original problem,
recorded research claims, obstacles and usage. It proposes group sizes, stable group
IDs, objectives and a collaboration mode: independent exploration, peer cooperation,
or derivation with criticism. Modes guide native researchers; they do not prescribe
every tool call or require fixed specialist roles. A continuous primary research
session is preserved, while inactive group sessions and files remain available.

The host validates both allocation limits. An invalid plan cannot raise either cap;
a planning timeout retains the saved allocation subject to both current limits, including
after reducing the group limit on resume.
Reallocation waits for the current researchers' natural checkpoints or the existing
time/stop limits. It does **not** currently resize groups during an in-flight native
turn. The supervisor does not provide a calibrated mathematical completion percentage.

With an explicit cap, nested native agent spawning is disabled. Extra researchers must
be requested through this scheduler, so they cannot bypass the cap. Shell, search,
configured research memory, native conversation continuity and compaction remain with
the backend. Claims, self-checks and peer checks remain Solve evidence, not independent
verification or novelty certification.

## Cross-group bulletin board

Researchers may publish results, questions, objections, failed routes, intentions and
retractions as `outbox/<unique-id>.json`, following `board-message.schema.json` in their
workspace. Messages include assumptions, dependency keys and optional local proof/source
paths. The coordinator records messages in the workspace SQLite database, freezes cited
UTF-8 files, and projects an index and materials into each researcher's `bulletin/`.
Workers browse the index and open relevant material as needed. Authors may retract
their own messages; another author's claim can be challenged with an objection.
Affected dependent messages are marked for rechecking, never silently deleted.

Messages are immutable. Correct a publication using a new ID and explicit references.
`author_checked` is the author's assertion; no message becomes certified by being posted.
Materials are limited to 2 MB each and message files to 100 KB. Build products and large
datasets should stay in the researcher's local workspace. Rejected posts are explained
in `bulletin/publication-errors.json`.

Codex workers see new posts during execution. Chat's hosted tools cannot read these local
files: messages and a bounded set of frozen source texts are sent inline at checkpoints;
omitted materials are listed explicitly. Chat sharing is therefore at checkpoint
boundaries, not live. The original full answers and sources remain saved locally.

## Budgets, recovery and observations

All research and supervision calls count toward the existing total time, token and call
budgets. Supervisor usage is also broken out in the browser. The call limit is reserved
before dispatch, including each researcher in a parallel round. Expand **Researcher activity**
to see each worker's last visible action and output; full activity downloads include active
parallel attempts. This displays observed activity, not hidden reasoning or a success percentage.

Token usage is checked between calls; in-flight parallel calls can exceed a token threshold before they return.
Unknown usage remains unknown. Agent count is not a CPU, RAM or monetary limit; use the
existing workspace resource controls and provider spending limits too.

Stopping or interrupting waits for local workers to terminate. Each worker has a durable
attempt, receipt and session reference. Completed receipts are applied once after recovery;
unresolved hosted responses must be recovered before new work begins. The existing bounded
closing turn can gather the saved results after time expires. A complete candidate remains
a solver claim. Find, independent Verify and Organize retain their existing behavior.

Run `pytest -q tests/test_solve_team.py` for deterministic scheduler and recovery tests.
They exercise scripted native agents, not mathematical ability or paid-model quality.
