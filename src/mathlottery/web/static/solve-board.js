/* Compact dependency navigation and lazy proof/channel inspection. Untrusted text stays text. */
(function (root, factory) {
  "use strict";
  const common = typeof module === "object" && module.exports;
  const api = factory(common ? require("./dom.js") : root.MathLotteryDOM);
  if (common) module.exports = api;
  if (root) root.MathLotterySolveBoard = api;
})(typeof window === "object" ? window : null, function (DOM) {
  "use strict";

  function create(panel) {
    const { node } = DOM.scope(panel);
    const cache = new Map();
    let selectedRun, query = "", archived = false;

    function render(run, language, open) {
      const zh = language === "zh", team = run.solve_team;
      if (selectedRun !== run.id) { selectedRun = run.id; query = ""; archived = false; cache.clear(); }
      const text = (cn, en) => zh ? cn : en;
      const tuning = team.coordination_policy;
      if (tuning) {
        const section = node("details", "evidence-block"); section.dataset.key = "coordination-policy";
        section.append(node("summary", "", `${text("监督机制优化", "Coordination adjustments")} · ${tuning.enabled ? text("已开启", "Enabled") : text("已关闭", "Disabled")}`));
        const labels = {
          review_interval_seconds: text("复查间隔（秒）", "Review interval (seconds)"),
          archive_min_age_seconds: text("归档候选最短保留时间（秒）", "Minimum age for archive suggestions (seconds)"),
          archive_read_threshold: text("归档候选登记读取上限", "Recorded-read ceiling for archive suggestions"),
          board_guidance: text("留言板使用建议", "Board guidance"),
          collaboration_guidance: text("合作建议", "Collaboration guidance"),
        };
        for (const [key, label] of Object.entries(labels)) {
          if (tuning.policy[key] !== "") section.append(node("p", "field-hint", `${label}: ${tuning.policy[key]}`));
        }
        section.append(node("p", "field-hint", text("策略只影响本任务。归档条件只筛选建议，不自动删除；历史建议在关闭后不再生效。", "Policy is run-local. Archive thresholds only select suggestions, never delete. Saved guidance is inactive while disabled.")));
        for (const change of [...(tuning.history || [])].reverse()) {
          const entry = node("details", "evidence-block"); entry.dataset.key = `policy-${change.task_id}`;
          const status = zh ? ({applied: "已应用", unchanged: "保持原策略", rejected: "未应用"}[change.status] || change.status) : change.status;
          entry.append(node("summary", "", `v${change.revision} · ${status} · ${change.time}`));
          for (const [key, label] of [["rationale", text("调整依据", "Rationale")], ["expected_effect", text("预期效果", "Expected effect")], ["previous_assessment", text("上次调整效果复盘", "Previous outcome assessment")], ["feedback", text("未应用原因", "Why it was not applied")]]) {
            if (change[key]) entry.append(node("p", "", `${label}: ${change[key]}`));
          }
          if (change.evidence?.length) entry.append(node("p", "field-hint", `${text("证据引用", "Evidence references")}: ${change.evidence.join(", ")}`));
          for (const [key, label] of Object.entries(labels)) {
            const show = value => value === "" || value == null ? "—" : value;
            if (change.after && change.before[key] !== change.after[key]) entry.append(node("p", "", `${label}: ${show(change.before[key])} → ${show(change.after[key])}`));
          }
          entry.open = open.has(entry.dataset.key); section.append(entry);
        }
        if (tuning.update_count) section.append(node("p", "field-hint", `${text("调整记录", "Update records")}: ${tuning.update_count} · ${text("最近 10 条；完整记录位于任务目录", "Latest 10; full history in the run directory")}: ${tuning.history_path}`));
        section.open = open.has(section.dataset.key); panel.append(section);
      }
      const board = node("details", "evidence-block"); board.dataset.key = "solve-board";
      const cards = team.messages || [];
      board.append(node("summary", "", `${text("定理依赖图与档案", "Proof graph & archive")} · ${cards.length}`));
      board.append(node("p", "field-hint", text("前提 → 结论；展开节点按需读取证明。归档不改变证明可信度。", "Premises → conclusions. Expand a node to load its derivation. Archiving does not change proof standing.")));
      if (team.curation_feedback) board.append(node("p", "field-hint", `${text("最近整理未执行", "Latest curation was not applied")}: ${team.curation_feedback}`));
      const controls = node("div", "board-controls"), search = node("input"), toggle = node("input"), label = node("label", "field-hint");
      search.type = "search"; search.placeholder = text("搜索标题、陈述、标签或别名", "Search title, statement, tags or aliases"); search.value = query;
      search.setAttribute("aria-label", search.placeholder);
      toggle.type = "checkbox"; toggle.checked = archived; label.append(toggle, document.createTextNode(text("包含归档", "Include archived")));
      controls.append(search, label); board.append(controls);
      const list = node("div", "board-nodes"); board.append(list);
      const expanded = new Set(open);

      async function load(kind, key, version) {
        const id = `${run.id}/${kind}/${key}/${version}`;
        if (!cache.has(id)) {
          const promise = fetch(`/api/runs/${encodeURIComponent(run.id)}/solve-${kind}?key=${encodeURIComponent(key)}`, {credentials: "same-origin"})
            .then(async response => { if (!response.ok) throw new Error(text("材料读取失败", "Could not load material")); return response.json(); });
          cache.set(id, promise);
          promise.catch(() => cache.delete(id));
        }
        return cache.get(id);
      }

      function proof(container, message) {
        container.replaceChildren();
        if (message.body) container.append(node("pre", "", message.body));
        if (message.theorem) {
          container.append(node("pre", "", message.theorem.statement));
          for (const step of message.theorem.proof_steps || []) container.append(node("p", "", `${step.id} ← ${step.premises.join(", ") || text("已声明前提", "declared premises")}: ${step.statement}\n${step.justification}`));
          if (message.theorem.remaining_obligations?.length) container.append(node("p", "field-hint", `${text("未完成义务", "Open obligations")}: ${message.theorem.remaining_obligations.join("; ")}`));
        }
        if (message.supervisor_review) container.append(node("pre", "", message.supervisor_review.rationale));
        if (message.curation) container.append(node("p", "field-hint", `${message.curation.action}: ${message.curation.reason}`));
        for (const artifact of message.artifacts || []) {
          const link = node("a", "text-button", `${text("下载材料", "Download material")}: ${artifact.source}`);
          link.href = `/api/runs/${encodeURIComponent(run.id)}/solve-material?sha256=${encodeURIComponent(artifact.sha256)}`;
          container.append(link);
        }
      }

      function draw() {
        list.replaceChildren();
        const visible = cards.filter(c => (archived || !c.archived) && `${c.key} ${c.title} ${c.statement || ""} ${(c.tags || []).join(" ")} ${(c.aliases || []).join(" ")}`.toLowerCase().includes(query.toLowerCase()));
        list.append(node("p", "field-hint", `${visible.length} / ${cards.length}`));
        for (const card of visible) {
          const entry = node("details", "evidence-block"); entry.dataset.key = card.key;
          const status = zh ? ({unverified: "待核验", needs_recheck: "需重新检查", retracted: "已撤回", supervisor_accepted: "监督者认可（非 Verify）", supervisor_rejected: "监督者否定"}[card.standing] || card.standing) : card.standing;
          entry.append(node("summary", "", `${card.archived ? text("[归档] ", "[Archived] ") : ""}${card.group} · ${status} · ${card.title}`));
          if (card.statement) entry.append(node("pre", "", card.statement));
          if (card.assumptions?.length) entry.append(node("p", "", `${text("假设", "Assumptions")}: ${card.assumptions.join("; ")}`));
          const navigate = (keys, caption) => {
            if (!keys.length) return;
            const row = node("div", "board-links"); row.append(node("span", "field-hint", caption));
            for (const key of keys) {
              const button = node("button", "text-button", key); button.type = "button";
              button.onclick = () => { query = key; search.value = key; archived = true; toggle.checked = true; expanded.add(key); draw(); };
              row.append(button);
            }
            entry.append(row);
          };
          navigate(card.depends_on || [], text("← 前提", "← Premises"));
          navigate(cards.filter(c => c.depends_on?.includes(card.key)).map(c => c.key), text("→ 推论", "→ Consequences"));
          navigate(card.target ? [card.target] : [], text("关联对象", "Target"));
          navigate(cards.filter(c => c.target === card.key).map(c => c.key), text("质疑／更正记录", "Objections / corrections"));
          if (card.usage) entry.append(node("p", "field-hint", `${text("已登记读取", "Recorded reads")}: ${card.usage.recorded_reads} · ${text("不包含直接文件读取", "Direct file reads are uncounted")}`));
          const content = node("div"); entry.append(content);
          let loaded = false;
          const fill = async () => {
            if (loaded || !entry.open) return;
            loaded = true;
            content.textContent = text("读取证明档案…", "Loading proof archive…");
            try { proof(content, await load("message", card.key, `${card.content_sha256}/${card.standing}/${card.archived}/${card.review_id}/${card.curation_id}`)); }
            catch (error) { loaded = false; content.textContent = error.message; }
          };
          // Old in-memory fixtures/legacy responses already carry the full content.
          if (Object.hasOwn(card, "body")) { proof(content, card); loaded = true; }
          entry.addEventListener("toggle", () => { if (entry.open) { expanded.add(card.key); fill(); } else expanded.delete(card.key); });
          entry.open = expanded.has(card.key); list.append(entry); if (entry.open) fill();
        }
      }
      search.addEventListener("input", () => { query = search.value; draw(); });
      toggle.addEventListener("change", () => { archived = toggle.checked; draw(); });
      draw(); board.open = open.has(board.dataset.key); panel.append(board);

      const cooperation = team.collaboration;
      if (!cooperation) return;
      const section = node("details", "evidence-block"); section.dataset.key = "solve-collaboration";
      section.append(node("summary", "", text("活动登记与协作通道", "Activity registry & collaboration channels")));
      section.append(node("p", "field-hint", text("运行状态来自调度器；研究意向由 agent 自报。邀请不代表已加入，讨论不代表证明通过。", "Runtime state comes from the scheduler; research intent is self-reported. Invitations are not joins; discussion is not proof acceptance.")));
      for (const agent of cooperation.agents || []) {
        const state = zh ? ({running: "执行中", idle: "待分配", completed: "本回合已返回", interrupted: "已中断"}[agent.runtime_status] || agent.runtime_status) : agent.runtime_status;
        section.append(node("p", "", `${agent.actor} · ${state}`));
        section.append(node("p", "field-hint", `${text("可选建议", "Optional suggestion")}: ${agent.objective}`));
        if (agent.report) {
          const intent = zh ? ({working: "研究中", seeking_help: "寻求协作", available: "可以协作", blocked: "遇到障碍"}[agent.report.status] || agent.report.status) : agent.report.status;
          section.append(node("p", "field-hint", `${agent.report_current ? text("当前登记", "Current report") : text("历史登记", "Past report")} · ${agent.report.time} · ${intent}: ${agent.report.summary}`));
          if (agent.report.topic) section.append(node("p", "", `${text("自主选择", "Chosen work")}: ${agent.report.topic}`));
          if (agent.report.approach) section.append(node("p", "field-hint", agent.report.approach));
          if (agent.report.overlap_reason) section.append(node("p", "field-hint", `${text("并行检查理由", "Reason for overlapping work")}: ${agent.report.overlap_reason}`));
        }
      }
      for (const channel of cooperation.channels || []) {
        const entry = node("details", "evidence-block"); entry.dataset.key = `channel-${channel.key}`;
        entry.append(node("summary", "", `${channel.closed ? text("[已关闭] ", "[Closed] ") : ""}${channel.purpose} · ${channel.event_count}`));
        entry.append(node("p", "field-hint", `${text("已加入", "Joined")}: ${channel.members.join(", ")} · ${text("邀请", "Invited")}: ${channel.invitees.join(", ")}`));
        const responses = channel.responses || {};
        for (const invitee of channel.invitees) {
          const reply = responses[invitee] || "pending";
          const label = zh ? ({pending: "待回应", deferred: "暂缓", declined: "谢绝", joined: "已加入", left: "已退出"}[reply] || reply) : reply;
          entry.append(node("p", "field-hint", `${invitee}: ${label}`));
        }
        const content = node("div"); entry.append(content);
        let loaded = false;
        const fill = async () => {
          if (loaded || !entry.open) return;
          loaded = true; content.textContent = text("读取交流记录…", "Loading discussion…");
          try {
            const transcript = await load("channel", channel.key, channel.event_count);
            content.replaceChildren();
            for (const event of transcript.events) {
              const action = zh ? ({channel_open: "创建通道", channel_join: "加入", channel_leave: "退出", channel_message: "发言", channel_close: "关闭通道", channel_ack: "已读取所见消息", channel_defer: "暂缓邀请", channel_decline: "谢绝邀请"}[event.action] || event.action) : event.action;
              content.append(node("p", "field-hint", `${event.time} · ${event.actor} · ${action}`));
              if (event.body || event.summary) content.append(node("pre", "", event.body || event.summary));
            }
          } catch (error) { loaded = false; content.textContent = error.message; }
        };
        entry.addEventListener("toggle", fill); entry.open = open.has(entry.dataset.key);
        section.append(entry); if (entry.open) fill();
      }
      section.open = open.has(section.dataset.key); panel.append(section);
    }
    return { render };
  }
  return { create };
});
