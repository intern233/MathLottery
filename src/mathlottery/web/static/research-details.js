/* Read-only evidence and runtime projections. All model text uses textContent. */
"use strict";
window.MathLotteryDetails = (() => {
  function view(language) {
    const zh = language === "zh", tr = (en, cn) => zh ? cn : en;
    const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
    const list = (parent, label, values) => {
      if (!values?.length) return;
      parent.append(el("h4", "", label)); const ul = el("ul");
      for (const value of values) ul.append(el("li", "", value)); parent.append(ul);
    };
    const detail = (label, cls = "evidence-block") => { const d = el("details", cls); d.append(el("summary", "", label)); return d; };
    const time = (value) => value ? new Date(value).toLocaleString(zh ? "zh-CN" : "en-US") : tr("Unavailable", "暂无记录");
    const kinds = {session: tr("Session", "会话"), model: tr("Model", "模型调用"), reasoning: tr("Reasoning", "推理"), message: tr("Visible message", "可见输出"), search: tr("Search", "检索"), command: tr("Command", "命令执行"), file: tr("File operation", "文件操作"), tool: tr("Tool", "工具调用"), computation: tr("Computation", "计算")};
    const statuses = {queued: tr("Queued", "排队中"), running: tr("Running", "运行中"), completed: tr("Completed", "已完成"), failed: tr("Failed", "失败"), cancelled: tr("Stopped", "已停止"), incomplete: tr("Incomplete", "未完成"), released: tr("Resources released", "资源已释放"), interrupted: tr("Interrupted", "已中断")};
    return {tr, el, list, detail, time, kinds, statuses};
  }
  function proof(review, language) {
    const {tr, el, list, detail} = view(language), root = el("section", "proof-map");
    const coverage = review.proof_coverage, steps = review.proof_steps || [];
    root.append(el("h4", "", tr("Key proof steps", "关键证明步骤")));
    if (!coverage?.policy_version) {
      root.append(el("p", "field-hint", tr("This review has no step-by-step coverage assessment. Run Verify again to obtain one.", "此记录尚无逐项覆盖评估；重新运行 Verify 可补充。"))); return root;
    }
    const supported = new Set(coverage.supported_steps || []);
    root.append(el("p", "evidence-headline", `${supported.size} / ${steps.length} ${tr("steps supported", "步骤已有支撑")} · ${tr("Original statement", "原题对齐")}: ${coverage.statement_aligned ? tr("matched by reviewer", "审阅者报告匹配") : tr("gaps remain", "仍有缺口")}`));
    list(root, tr("Coverage gaps", "覆盖缺口"), coverage.reasons);
    for (const step of steps) {
      const d = detail(`${supported.has(step.id) ? "✓" : "?"} ${step.id} · ${step.statement}`);
      d.dataset.stepId = step.id;
      d.append(el("p", "field-hint", `${step.kind} · ${step.essential ? tr("Essential", "必要步骤") : tr("Supporting", "辅助步骤")}`));
      list(d, tr("Depends on", "依赖步骤"), step.dependencies);
      const checks = (review.checks || []).filter((c) => step.check_ids?.includes(c.id));
      for (const check of checks) {
        d.append(el("h4", "", `${check.id} · ${check.method} · ${check.result}`), el("p", "", check.reasoning));
        list(d, tr("Evidence", "检查依据"), check.evidence);
        list(d, tr("Formal declarations", "形式化声明"), check.formal_declarations);
      }
      root.append(d);
    }
    const alignment = detail(tr("Original problem ↔ candidate: statement alignment", "原题 ↔ 候选证明：逐项对齐"));
    const facets = {DEFINITIONS: tr("Definitions", "定义"), ASSUMPTIONS: tr("Assumptions", "假设"), QUANTIFIERS: tr("Quantifiers", "量词"), DOMAIN: tr("Domain", "取值范围"), BOUNDARY_CASES: tr("Boundary cases", "边界情况"), CONCLUSION: tr("Conclusion", "结论")};
    for (const item of review.statement_alignment || []) {
      const row = el("div", "alignment-row");
      row.append(el("h4", "", `${facets[item.facet] || item.facet} · ${item.assessment}`), el("p", "", `${tr("Original", "原题")}: ${item.original}`), el("p", "", `${tr("Candidate", "候选证明")}: ${item.candidate}`), el("p", "field-hint", item.reasoning));
      if (item.formal_statement) row.append(el("pre", "", item.formal_statement));
      list(row, tr("Check references", "检查编号"), item.check_ids); alignment.append(row);
    }
    alignment.append(el("p", "field-hint", tr("Step coverage checks the submitted evidence structure. It is not an expert certification of the argument or of natural-language / Lean equivalence.", "步骤覆盖检查提交的证据结构，不等于专家认证数学论证或自然语言与 Lean 陈述等价。")));
    root.append(alignment); return root;
  }
  function novelty(assessment, search, language, safeLink, followup) {
    const {tr, el, list, detail} = view(language), root = el("section", "novelty-obstacles");
    const obstacles = assessment?.obstacles?.length ? assessment.obstacles : search?.obstacles || [];
    if (!obstacles.length && !search?.comparisons?.length && !search?.unresolved?.length) return root;
    root.append(el("h4", "", tr("Novelty obstacles", "新颖性待核查事项")));
    list(root, tr("Earlier unresolved gaps", "此前未解决的缺口"), search?.unresolved);
    for (const item of [...obstacles].sort((a, b) => Number(Boolean(a.resolution_supported)) - Number(Boolean(b.resolution_supported)))) {
      const resolved = item.resolution_supported === true;
      const d = detail(`${resolved ? "✓" : "?"} ${item.id} · ${item.description}`, "obstacle-card");
      d.dataset.obstacleId = item.id; d.open = !resolved;
      d.append(el("p", "evidence-headline", resolved ? tr("Resolution has source evidence", "处理结论有来源支撑") : tr("Evidence still required", "仍需补齐证据")));
      if (item.source_url) d.append(safeLink(item.source_url));
      for (const [en, cn, value] of [["Impact", "影响", item.impact], ["Next action", "下一步", item.next_action], ["Proposed resolution", "提交的处理结论", item.resolution], ["Evidence assessment", "证据评估", item.resolution_reason]]) if (value) d.append(el("p", "", `${tr(en, cn)}: ${value}`));
      for (const url of item.evidence_urls || []) { const p = el("p"); p.append(safeLink(url)); d.append(p); }
      if (!resolved && followup) {
        const button = el("button", "secondary small", tr("Prepare focused follow-up", "继续核查这一项")); button.type = "button";
        button.addEventListener("click", () => followup(item)); d.append(button);
      }
      root.append(d);
    }
    const compared = assessment?.comparisons?.length ? assessment.comparisons : search?.comparisons || [];
    if (compared.length) {
      const comparisons = detail(tr("Comparison with prior results", "与已有结果逐项比较"));
      for (const comparison of compared) {
        const c = el("div", "alignment-row"); c.append(el("h4", "", `${comparison.id} · ${comparison.relation}`));
        c.append(el("p", "field-hint", comparison.supported === true ? tr("Source evidence matched", "来源证据匹配") : tr("Comparison evidence not established", "比较证据尚未成立")));
        if (comparison.source_url) c.append(safeLink(comparison.source_url));
        for (const [en, cn, value] of [["Location", "定位", comparison.locator], ["Prior assumptions", "已有结果假设", comparison.prior_assumptions], ["Candidate assumptions", "候选证明假设", comparison.candidate_assumptions], ["Prior conclusion", "已有结论", comparison.prior_conclusion], ["Candidate conclusion", "候选结论", comparison.candidate_conclusion], ["Reasoning", "比较理由", comparison.reasoning]]) c.append(el("p", "", `${tr(en, cn)}: ${value}`));
        list(c, tr("Related obstacles", "关联障碍"), comparison.obstacle_ids); comparisons.append(c);
      }
      root.append(comparisons);
    }
    return root;
  }
  function runtime(run, language) {
    const {tr, el, time, kinds, statuses} = view(language), root = el("div", "runtime-details"), r = run.resources, activity = run.activity;
    let summary = "";
    if (r?.state === "queued" && run.busy) summary = `${statuses.queued}${r.queue_position ? ` · #${r.queue_position}` : ""} · ${r.reason === "low_available_memory" ? tr("Waiting for available memory", "等待可用内存") : tr("Waiting for a workspace slot", "等待工作区空闲名额")}`;
    else if (run.busy && activity?.current) summary = `${tr("Task still running", "任务仍在运行")} · ${tr("Last visible activity", "最近可见活动")}: ${kinds[activity.current.kind] || tr("Agent activity", "Agent 活动")} · ${statuses[activity.current.status] || activity.current.status}`;
    else if (run.busy) summary = tr("Task still running · Waiting for visible agent events", "任务仍在运行 · 等待 Agent 可见活动记录");
    root.append(el("h3", "", tr("Activity & resources", "活动与资源")));
    if (r) {
      root.append(el("p", "", `${statuses[r.state] || r.state} · ${tr("Updated", "更新于")} ${time(r.updated_at)}`));
      if (r.reason && !["capacity", "low_available_memory"].includes(r.reason)) root.append(el("p", "notice", r.reason));
      const m = r.memory;
      if (m?.available) {
        const metrics = el("dl", "runtime-metrics");
        for (const [label, value] of [[tr("Process tree RSS", "本任务进程树 RSS"), m.rss_mb], [tr("This execution's sampled peak", "本次执行采样峰值"), m.peak_rss_mb], [tr("System available", "系统可用内存"), m.available_mb]]) {
          const item = el("div"); item.append(el("dt", "", label), el("dd", "", Number.isFinite(value) ? `${Math.round(value)} MiB` : "—")); metrics.append(item);
        }
        root.append(metrics, el("p", "field-hint", `${tr("Sampled", "采样于")} ${time(m.sampled_at)}`));
      } else root.append(el("p", "field-hint", tr("Memory measurement unavailable", "暂不可测量内存")));
    }
    if (run.formal_resources?.state === "queued" && run.busy) root.append(el("p", "notice", tr("Independent Lean check is waiting for a formal-check slot.", "独立 Lean 检查正在等待形式化检查名额。")));
    root.append(el("p", "field-hint", tr("RSS covers local processes only and may double-count shared pages. Sampling can miss brief peaks; memory controls are cooperative, not a hard system cap.", "RSS 仅统计本地进程，共享页可能重复计算，采样可能漏掉瞬时峰值。内存控制是协作式软限制，不是系统硬上限。")));
    root.append(el("p", "field-hint", tr("The sampled peak resets when a task resumes; it does not include earlier executions of this task.", "续接任务时重新统计采样峰值，不包含本任务之前执行的峰值。")));
    root.append(el("p", "", `${tr("Last visible activity", "最近可见活动")}: ${time(activity?.last_active_at)}`));
    root.append(el("p", "field-hint", tr("No new event does not establish that the agent is stuck. Hidden reasoning and remote memory usage are not observable.", "暂时没有新事件并不能说明 Agent 卡住；隐藏推理和远程内存用量不可观测。")));
    const events = el("ol", "activity-events");
    for (const event of (activity?.recent || []).slice(-12).reverse()) events.append(el("li", "", `${time(event.time)} · ${kinds[event.kind] || event.kind} · ${statuses[event.status] || event.status}`));
    root.append(events); return {summary, element: root};
  }
  return {proof, novelty, runtime};
})();
