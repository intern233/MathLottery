/* Presentation only: a solver's claim is never upgraded by a review or run state. */
(function (root) {
  "use strict";
  const words = {
    zh: {
      solve: "Solve · 求解声称", inherited: "原候选 · 求解声称", verify: "Verify · 独立审查", novelty: "新颖性",
      COMPLETE: "声称完整解决", COUNTEREXAMPLE: "声称以反例否定原题", PARTIAL: "声称部分解决", UNSOLVED: "自述尚未解决",
      UNKNOWN: "未明确声明范围", NO_CANDIDATE: "尚未提交解答",
      FULL: "覆盖完整原题", PARTIAL_COVERAGE: "仅覆盖部分原题", DIFFERENT: "与原题不一致", UNKNOWN_COVERAGE: "覆盖范围未确认",
      NO_ISSUES_FOUND: "未发现问题", ISSUES_FOUND: "发现问题", INCONCLUSIVE: "审查无定论", UNREVIEWED: "尚未审查",
      KNOWN: "已有结果", SPECIAL_CASE: "已知结果的特例", POTENTIALLY_NEW: "可能新颖", UNKNOWN_NOVELTY: "尚未确认", DISPUTED: "存在争议",
      claimNote: "仅记录求解者的声明；完备性、正确性与新颖性由 Verify 另行检查。",
      legacy: "依据旧候选开头的明确自述展示，原记录及哈希未修改。", unknown: "旧记录没有明确声明范围，请阅读候选结论。",
      reviewNote: "审查针对这份候选。未发现问题不等于完整解决原题，也不等于首次解决。",
      unreviewedNote: "本记录未附审查；若已运行 Verify，请查看同一问题组的验真记录。",
      organizeNote: "Organize 沿用来源结论，不新增证明或新颖性认证。", obligations: "尚待证明", claim: "候选结论",
      claimed: "求解声称", coverage: "审查覆盖", reviewResult: "审查结论", inheritedShort: "沿用求解声称", report: "报告",
      bilingual: "中英双版已生成", reportPending: "尚未生成双语终稿", observed: "原文自述", source: "选题来源", shared: "共享选题来源",
      shortlist: "候选题目", missing: "未记录", count: "项", pipeline: "Solve / Verify 分别记录",
      excerpt: "此处为摘录，完整内容见下方候选与审查记录。", obligationCount: "共 {n} 项待证明事项；此处仅显示部分内容。",
    },
    en: {
      solve: "Solve · researcher's claim", inherited: "Source candidate · researcher's claim", verify: "Verify · independent review", novelty: "Novelty",
      COMPLETE: "Claims a complete solution", COUNTEREXAMPLE: "Claims a counterexample", PARTIAL: "Claims a partial solution", UNSOLVED: "Reports no solution",
      UNKNOWN: "Scope not declared", NO_CANDIDATE: "No answer submitted",
      FULL: "Full original coverage", PARTIAL_COVERAGE: "Partial original coverage", DIFFERENT: "Different statement", UNKNOWN_COVERAGE: "Coverage not established",
      NO_ISSUES_FOUND: "No issues found", ISSUES_FOUND: "Issues found", INCONCLUSIVE: "Inconclusive", UNREVIEWED: "Not reviewed",
      KNOWN: "Known result", SPECIAL_CASE: "Known special case", POTENTIALLY_NEW: "Potentially new", UNKNOWN_NOVELTY: "Not established", DISPUTED: "Disputed",
      claimNote: "The researcher's statement only; Verify separately checks completeness, correctness and novelty.",
      legacy: "Shown from an explicit statement in the legacy candidate. Saved evidence and hashes are unchanged.", unknown: "This record does not declare its scope. Read the candidate claim.",
      reviewNote: "Review applies to this candidate. Finding no issues establishes neither full original coverage nor a first solution.",
      unreviewedNote: "No review is attached to this record. If Verify has run, open its record in the same problem group.",
      organizeNote: "Organize retains source conclusions; it adds no proof or novelty certification.", obligations: "Remaining proof obligations", claim: "Candidate claim",
      claimed: "Solver claim", coverage: "Review coverage", reviewResult: "Review verdict", inheritedShort: "Source claim", report: "Report",
      bilingual: "Chinese + English ready", reportPending: "Bilingual report pending", observed: "Explicit text", source: "Find source", shared: "Shared Find source",
      shortlist: "Shortlist", missing: "Not recorded", count: "items", pipeline: "Solve / Verify reported separately",
      excerpt: "Excerpt only; see the full candidate and review below.", obligationCount: "{n} proof obligations in total; only part is shown here.",
    },
  };
  function describe(run, language = "en", context = {}) {
    const w = words[language] || words.en;
    if (run.workflow === "find") return {
      items: [
        ...(context.linked ? [{label: context.shared ? w.shared : w.source, value: "", tone: "neutral"}] : []),
        {label: w.shortlist, value: `${run.shortlist_count || 0} ${w.count}`, tone: "neutral"},
      ], sections: [], note: "",
    };
    const outcome = run.research_outcome || {};
    const solve = outcome.solve || {status: "UNKNOWN"}, review = outcome.verify || {status: "UNREVIEWED"};
    const solveValue = w[solve.status] || w.UNKNOWN;
    const solveTone = ["PARTIAL", "UNSOLVED"].includes(solve.status) ? "warning" : "neutral";
    const reviewed = review.status === "REVIEWED";
    const coverageKey = review.original_problem_coverage === "PARTIAL" ? "PARTIAL_COVERAGE" : ["FULL", "DIFFERENT"].includes(review.original_problem_coverage) ? review.original_problem_coverage : "UNKNOWN_COVERAGE";
    const reviewValue = reviewed ? (w[review.verdict] || w.missing) : w.UNREVIEWED;
    const noveltyValue = reviewed ? (w[review.novelty === "UNKNOWN" ? "UNKNOWN_NOVELTY" : review.novelty] || w.UNKNOWN_NOVELTY) : w.UNREVIEWED;
    const solverItem = {label: run.workflow === "organize" ? w.inheritedShort : w.claimed, value: solveValue, tone: solveTone};
    if (solve.basis === "explicit_claim_text") solverItem.note = w.observed;
    const reviewItems = reviewed ? [
      {label: w.coverage, value: w[coverageKey], tone: review.original_problem_coverage === "FULL" ? "neutral" : "warning"},
      {label: w.reviewResult, value: reviewValue, tone: review.verdict === "ISSUES_FOUND" ? "error" : "neutral"},
      {label: w.novelty, value: noveltyValue, tone: "neutral"},
    ] : [{label: w.verify, value: w.UNREVIEWED, tone: "neutral"}];
    let items;
    if (run.workflow === "verify") items = reviewItems;
    else if (run.workflow === "organize") items = [solverItem, {label: w.report, value: run.organized_report?.bilingual_complete ? w.bilingual : w.reportPending, tone: "neutral"}];
    else if (["run", "pipeline"].includes(run.workflow)) items = [solverItem, ...reviewItems];
    else items = [solverItem];
    return {
      items,
      sections: [
        {title: run.workflow === "solve" ? w.solve : w.inherited, value: solveValue, tone: solveTone,
          note: `${w.claimNote}${solve.basis === "explicit_claim_text" ? " " + w.legacy : solve.status === "UNKNOWN" ? " " + w.unknown : ""}`,
          claim: solve.claim || "", obligations: solve.remaining_obligations || [], candidateId: solve.candidate_id,
          excerpt: solve.claim_truncated ? w.excerpt : "", obligationNotice: solve.remaining_obligations_truncated ? w.obligationCount.replace("{n}", solve.remaining_obligations_count) : ""},
        {title: w.verify, value: reviewValue, tone: review.verdict === "ISSUES_FOUND" ? "error" : "neutral",
          note: reviewed ? w.reviewNote : w.unreviewedNote, coverage: reviewed ? w[coverageKey] : w.UNREVIEWED,
          novelty: noveltyValue, obligations: review.remaining_obligations || [], candidateId: review.candidate_id,
          obligationNotice: review.remaining_obligations_truncated ? w.obligationCount.replace("{n}", review.remaining_obligations_count) : ""},
      ],
      note: run.workflow === "organize" ? w.organizeNote : "", labels: w,
    };
  }
  function element(tag, className, text) {
    const result = document.createElement(tag);
    if (className) result.className = className;
    if (text) result.textContent = text;
    return result;
  }
  function history(run, language, context) {
    const box = element("div", "run-outcomes");
    for (const item of describe(run, language, context).items) {
      const label = `${item.label}${item.value ? ": " + item.value : ""}${item.note ? " · " + item.note : ""}`;
      box.append(element("span", `outcome-tag ${item.tone}`, label));
    }
    return box;
  }
  function detail(run, language) {
    const data = describe(run, language), box = element("div", "outcome-overview");
    for (const section of data.sections) {
      const item = element("section", `outcome-card ${section.tone}`);
      item.append(element("h3", "", section.title), element("p", "outcome-value", section.value));
      if (section.coverage) item.append(element("p", "outcome-dimension", `${data.labels.coverage}: ${section.coverage}`));
      if (section.novelty) item.append(element("p", "outcome-dimension", `${data.labels.novelty}: ${section.novelty}`));
      item.append(element("p", "field-hint", section.note));
      if (section.claim || section.obligations.length) {
        const more = element("details", "outcome-more"), title = section.obligations.length ? data.labels.obligations : data.labels.claim;
        more.append(element("summary", "", title));
        if (section.claim) more.append(element("p", "", section.claim));
        if (section.excerpt) more.append(element("p", "field-hint", section.excerpt));
        if (section.obligations.length) {
          const list = element("ul");
          for (const obligation of section.obligations) list.append(element("li", "", obligation));
          more.append(list);
        }
        if (section.obligationNotice) more.append(element("p", "field-hint", section.obligationNotice));
        item.append(more);
      }
      box.append(item);
    }
    if (data.note) box.append(element("p", "outcome-note field-hint", data.note));
    return box;
  }
  const api = {describe, history, detail};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.MathLotteryOutcomes = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
