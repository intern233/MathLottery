/* MathLotterySolveTeams: explicit component interfaces; no application-state globals. */
(function (root, factory) {
  "use strict";
  const common = typeof module === "object" && module.exports;
  const api = factory((common ? require("./dom.js") : root.MathLotteryDOM), (common ? require("./i18n.js") : root.MathLotteryI18n));
  if (common) module.exports = api;
  if (root) root.MathLotterySolveTeams = api;
})(typeof window === "object" ? window : null, function (MathLotteryDOM, MathLotteryI18n) {
  "use strict";

  // Read-only projection of a checkpoint. Each view has its own render cache.
  function create(panel) {
    const { node } = MathLotteryDOM.scope(panel);
    let lastSignature;

    function render(run, language) {
      const team = run.solve_team, zh = language === "zh";
      const compact = value => MathLotteryI18n.compact(language, value);
      const date = value => MathLotteryI18n.date(language, value);
      panel.hidden = !team || (!(team.parallel_agents > 1) && !team.rounds);
      if (panel.hidden) return;
      const signature = JSON.stringify([run.id, run.busy, language, team, run.settings?.solve_agent_slots]);
      if (lastSignature === signature) return;
      lastSignature = signature;
      const open = new Set([...panel.querySelectorAll("details[open]")].map(d => d.dataset.key));
      panel.replaceChildren(node("h3", "", zh ? "Solve 研究组与留言板" : "Solve teams & bulletin board"));
      const running = (team.workers || []).filter(w => w.state === "running").length;
      panel.append(node("p", "field-hint", run.busy
        ? `${zh ? "求解并行" : "Research concurrency"}: ${running} / ${team.parallel_agents ?? "—"}`
        : (zh ? "任务当前未运行；下方保留最后的分组与成果。" : "Task is idle; the saved groups and findings remain available.")));
      if (team.decision) panel.append(node("p", "", team.decision));
      panel.append(node("p", "field-hint", `${zh ? "本轮分组" : "Groups in this round"}: ${(team.groups || []).length} · ${zh ? "组数上限" : "Group cap"}: ${team.max_groups ?? team.effective_max_groups ?? team.parallel_agents ?? "—"}`));
      for (const group of team.groups || []) {
        const mode = zh ? ({independent: "独立探索", peer: "同级协作", critique: "推导与质疑"}[group.mode] || group.mode) : group.mode;
        panel.append(node("p", "", `${group.id} · ${group.agents} agent · ${mode}: ${group.objective}`));
      }
      const usage = team.supervisor_usage || {};
      panel.append(node("p", "field-hint", `${zh ? "监督开销（已计入任务总量）" : "Supervision overhead (included in totals)"}: ${compact(usage.input_tokens)} in / ${compact(usage.output_tokens)} out; ${usage.unknown_calls || 0} ${zh ? "次用量未知" : "calls with unknown usage"}`));
      const workers = node("details", "evidence-block"); workers.dataset.key = "solve-workers";
      workers.append(node("summary", "", zh ? "研究者活动" : "Researcher activity"));
      for (const worker of team.workers || []) {
        const slot = run.settings?.solve_agent_slots?.find(item => item.id === worker.slot_id);
        const activity = worker.activity?.current;
        const kind = activity && (zh ? ({session: "会话", model: "模型调用", reasoning: "推理", message: "输出", search: "检索", command: "命令", file: "文件", tool: "工具", computation: "计算"}[activity.kind] || activity.kind) : activity.kind);
        const status = zh ? ({idle: "待分配", running: "执行中", completed: "本回合已返回", interrupted: "已中断"}[worker.state] || worker.state) : worker.state;
        workers.append(node("p", "", `${worker.id} · ${worker.group} · ${status}${activity ? ` · ${kind} · ${date(activity.time)}` : ""}`));
        if (slot) workers.append(node("p", "field-hint", [slot.label || slot.id, slot.backend === "chat" ? "API agent · Responses" : `Codex · ${slot.codex_auth === "api_key" ? "API Key" : "ChatGPT"}`, slot.model, slot.reasoning_effort].filter(Boolean).join(" · ")));
        if (worker.progress?.text) workers.append(node("pre", "", worker.progress.text));
        if (worker.progress?.truncated) workers.append(node("p", "field-hint", zh ? "仅显示最近调用的部分文本，完整记录保存在本地。" : "Partial text from the latest call; full records remain saved locally."));
      }
      workers.open = open.has(workers.dataset.key); panel.append(workers);
      panel.append(node("p", "field-hint", zh ? "留言与自检均为 Solve 阶段研究记录，不表示独立验证通过。" : "Messages and self-checks are Solve research records, not independent verification."));
      const board = node("details", "evidence-block"); board.dataset.key = "solve-board";
      board.append(node("summary", "", `${zh ? "跨组留言" : "Cross-group messages"} · ${(team.messages || []).length}`));
      for (const message of [...(team.messages || [])].reverse()) {
        const entry = node("details", "evidence-block"); entry.dataset.key = message.key;
        const status = zh ? ({unverified: "待核验", needs_recheck: "需重新检查", retracted: "已撤回"}[message.standing] || message.standing) : message.standing;
        entry.append(node("summary", "", `${message.group} · ${status} · ${message.title}`), node("pre", "", message.body));
        if (message.assumptions.length) entry.append(node("p", "", `${zh ? "假设" : "Assumptions"}: ${message.assumptions.join("; ")}`));
        if (message.depends_on.length) entry.append(node("p", "", `${zh ? "依赖" : "Dependencies"}: ${message.depends_on.join(", ")}`));
        for (const artifact of message.artifacts) {
          const link = node("a", "text-button", `${zh ? "下载材料" : "Download material"}: ${artifact.source}`);
          link.href = `/api/runs/${encodeURIComponent(run.id)}/solve-material?sha256=${encodeURIComponent(artifact.sha256)}`;
          entry.append(link);
        }
        entry.open = open.has(entry.dataset.key); board.append(entry);
      }
      board.open = open.has(board.dataset.key); panel.append(board);
    }

    return { render };
  }
  return { create };

});
