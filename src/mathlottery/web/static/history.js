/* Pure history grouping. No title matching, inferred provenance, or DOM access. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MathLotteryHistory = api;
})(typeof window === "object" ? window : null, function () {
  "use strict";

  const text = value => typeof value === "string" ? value : "";
  const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  const updated = run => text(run.updated_at) || text(run.created_at);
  const created = run => text(run.created_at) || text(run.updated_at);
  const isFind = run => run.workflow === "find";
  const newestFirst = (a, b) => compare(updated(b), updated(a))
    || compare(created(b), created(a)) || compare(a.id, b.id);
  const oldestFirst = (a, b) => compare(created(a), created(b)) || compare(a.id, b.id);

  function groupRuns(input) {
    // Valid API summaries have unique IDs. Repeated identical summaries must not
    // become extra execution records; conflicting duplicate IDs cannot authorize
    // a Find link because there is no unambiguous provenance in this input.
    const byId = new Map();
    const ambiguous = new Set();
    for (const run of Array.isArray(input) ? input : []) {
      if (!run || typeof run !== "object" || !text(run.id)) continue;
      const previous = byId.get(run.id);
      if (previous && ["workflow", "problem_key", "discovery_run_id"].some(key => previous[key] !== run[key])) {
        ambiguous.add(run.id);
      }
      if (!previous || newestFirst(run, previous) < 0) byId.set(run.id, run);
    }

    const groups = new Map();
    for (const run of byId.values()) {
      if (isFind(run)) continue;
      const key = text(run.problem_key) ? `problem:${run.problem_key}` : `run:${run.id}`;
      if (!groups.has(key)) groups.set(key, {key, title: "", latest: run, runs: [], sharedFindIds: []});
      groups.get(key).runs.push(run);
    }

    const sourceGroups = new Map();
    for (const group of groups.values()) {
      // Prefer a problem title even when the source Find was updated more recently.
      const problemRuns = [...group.runs].sort(newestFirst);
      group.title = text(problemRuns.find(run => text(run.title).trim())?.title) || problemRuns[0].id;
      for (const run of problemRuns) {
        const source = byId.get(run.discovery_run_id);
        if (!source || !isFind(source) || source.id === run.id || source.discovery_run_id
            || ambiguous.has(run.id) || ambiguous.has(source.id)) continue;
        // Only direct, explicit references count. Never follow a Solve/Verify
        // chain or a malformed Find -> Find / Find -> Solve chain.
        if (!sourceGroups.has(source.id)) sourceGroups.set(source.id, new Set());
        sourceGroups.get(source.id).add(group.key);
      }
    }

    for (const run of byId.values()) {
      if (!isFind(run)) continue;
      const linked = sourceGroups.get(run.id);
      if (!linked?.size) {
        const key = `run:${run.id}`;
        groups.set(key, {key, title: text(run.title) || run.id, latest: run, runs: [run], sharedFindIds: []});
        continue;
      }
      for (const key of linked) {
        const group = groups.get(key);
        group.runs.push(run);
        if (linked.size > 1) group.sharedFindIds.push(run.id);
      }
    }

    for (const group of groups.values()) {
      group.runs.sort(oldestFirst);
      group.sharedFindIds.sort(compare);
      group.latest = [...group.runs].sort(newestFirst)[0];
    }
    // A shared Find is displayed in multiple groups, but is still ONE run.
    // Global execution counts must use distinct summary IDs, not group lengths.
    return [...groups.values()].sort((a, b) => newestFirst(a.latest, b.latest) || compare(a.key, b.key));
  }

  return Object.freeze({groupRuns});
});
