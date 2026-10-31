"use strict";

const { $, $$, node, text, notice, options } = MathLotteryDOM.scope(document);
function preference(key, value) {
  try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch { /* Storage can be disabled. */ }
  return null;
}
const state = { language: preference("mathlottery.language") || (navigator.language.startsWith("zh") ? "zh" : "en"), workflow: "find", settings: null, runs: [], problems: [], csrf: "", selected: preference("mathlottery.run"), detail: null, resultsKey: "", discoveryChoice: null, polling: false, submitting: false, resuming: false };
// This form snapshot changes only on an explicit source choice/refresh, never a background poll.
const reviewSource = { generation: 0, runId: "", loading: false, error: "", run: null, candidate: null, files: [], selected: new Set(), filesKey: "" };
const pdfExports = new Set();
state.language = MathLotteryI18n.language(state.language);
const t = key => MathLotteryI18n.translate(state.language, key);
const compact = value => MathLotteryI18n.compact(state.language, value);
const date = value => MathLotteryI18n.date(state.language, value);

function toast(value) { notice("#toast", value); clearTimeout(toast.timer); toast.timer = setTimeout(() => { $("#toast").hidden = true; }, 5000); }
function badge(value) {
  const style = value === "COMPLETED" ? "execution-status" : value === "NO_ISSUES_FOUND" ? "success" : ["FAILED", "ISSUES_FOUND"].includes(value) ? "error" : ["PAUSED", "RATE_LIMITED", "INCONCLUSIVE", "DISPUTED"].includes(value) ? "warning" : ["DISCOVERING", "SOLVING", "VERIFYING", "ORGANIZING", "CREATED"].includes(value) ? "active" : "";
  return node("span", `badge ${style}`, t(value));
}
function executionBadge(run) {
  if (!run.busy && run.worker_state === "interrupted") {
    return node("span", "badge warning", state.language === "zh" ? "执行中断" : "Interrupted");
  }
  if (run.busy && run.finalization?.status === "running") {
    return node("span", "badge active", state.language === "zh" ? "快速收尾中" : "Wrapping up");
  }
  if (!run.busy && run.finalization?.status === "completed" && run.state === "COMPLETED") {
    return node("span", "badge execution-status", state.language === "zh" ? "已收尾" : "Wrapped up");
  }
  return run.busy && (run.resources?.state === "queued" || run.worker_state === "queued")
    ? node("span", "badge warning", state.language === "zh" ? "排队中" : "Queued") : badge(run.state);
}
function finalizationBudgetHint(settings, parallel = settings?.solve_parallel_agents) {
  if (settings?.solve_coordination === "supervised" && parallel) return state.language === "zh"
    ? "监督模式：到时停止派发新尝试，当前研究继续，返回后由监督者审核整理；实际总时长可以超过预算。"
    : "Supervised mode: the deadline stops new attempts; current research continues, followed by supervisor review. Total duration can exceed the budget.";
  const minutes = settings?.finalize_minutes ?? 5;
  if (!minutes) return state.language === "zh" ? "当前配置关闭到时收尾。" : "End-of-budget wrap-up is disabled in this configuration.";
  return state.language === "zh"
    ? `研究时间用尽后，最多额外用 ${minutes} 分钟在原会话收尾，保存完成范围和剩余问题；收尾耗时也会记录。`
    : `When research time runs out, allow up to ${minutes} extra minutes in the same session to summarize results and remaining work. Wrap-up time is recorded too.`;
}
function finalizationNotice(run) {
  const status = run.finalization?.status;
  if (status === "running") return run.busy
    ? (state.language === "zh" ? "研究时间已到，正在快速收尾。" : "Research time has ended; the agent is wrapping up.") + " " + finalizationBudgetHint(run.settings)
    : (state.language === "zh" ? "收尾执行已中断；保留已有检查点，尚未收到收尾结果。" : "Wrap-up was interrupted; existing checkpoints remain, but no wrap-up result has been received.");
  if (status === "completed") return state.language === "zh"
    ? "已保存 agent 的收尾结果。请查看求解声称的范围和剩余问题；收尾完成不代表原题已解决，也不替代 Verify。"
    : "The agent's wrap-up result is saved. Check its claimed scope and remaining work; finishing wrap-up does not establish a solution or replace Verify.";
  if (status === "incomplete") return state.language === "zh"
    ? "未获得 agent 收尾总结，已保存本地检查点摘要。摘要保留已有进展，不补造最终结果或升级证明结论。"
    : "No agent wrap-up summary was obtained. A local checkpoint summary preserves existing progress without inventing a final result or upgrading the proof claim.";
  return "";
}
function safeLink(value, title) {
  try {
    const url = new URL(value);
    if (["http:", "https:"].includes(url.protocol)) { const link = node("a", "", title || value); link.href = url.href; link.target = "_blank"; link.rel = "noopener noreferrer"; return link; }
  } catch { /* Non-URL source notes remain plain text. */ }
  return node("span", "", title || value);
}
async function api(path, body) {
  let response;
  try { response = await fetch(path, body === undefined ? { cache: "no-store" } : { method: "POST", headers: { "Content-Type": "application/json", "X-MathLottery-Token": state.csrf }, body: JSON.stringify(body) }); }
  catch { throw new Error(t("requestError")); }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}
// Components own their feature state. This controller composes workflow transitions.
const models = MathLotteryModels.create({ root: $("#task-form"), settings: () => state.settings, translate: t, request: api, onChange: updateForm });
const account = MathLotteryAccount.create({ root: $("#account-panel"), translate: t, request: api, onChange: updateExecutionControls, notify: toast, connection: () => state.settings ? models.connection() : null, reloadConnection: refresh });
const solveTeams = MathLotterySolveTeams.create($("#solve-team"));
const agentSlots = MathLotteryAgentSlots.create({ root: $("#agent-slots"), workflow: () => state.workflow, language: () => state.language, request: api, onChange: updateForm });
let manualParallel = "", rosterWasEnabled = false;

function savedAgentSlots(run) { return run?.workflow === "solve" && Boolean(run.settings?.solve_agent_slots?.length); }

function selectedSourceFiles() { return reviewSource.files.filter((file) => reviewSource.selected.has(file.path)); }
function sourceAttachmentsSupported() { return state.settings?.execution === "native"; }
function reviewedCandidateCount(run) { return run?.reviewed_candidate_count ?? run?.candidates?.filter((candidate) => candidate.reviews?.length).length ?? 0; }
function organizeSourceBlock() {
  if (state.workflow !== "organize") return "";
  const run = state.runs.find((item) => item.id === $("#organize-from-run").value);
  if (!reviewedCandidateCount(run) || run.workflow === "organize") return t("organizeChoose");
  return run.busy ? t("sourceBusy") : "";
}
function reviewSourceBlock() {
  if (state.workflow !== "verify" || $("#verify-mode").value !== "saved") return "";
  if (!$("#from-run").value || reviewSource.runId !== $("#from-run").value) return t("sourceChoose");
  if (reviewSource.loading) return t("sourceLoading");
  if (reviewSource.error) return reviewSource.error;
  if (!reviewSource.candidate) return t("sourceMissing");
  if (reviewSource.run?.busy) return t("sourceBusy");
  const files = selectedSourceFiles();
  if (files.length && !sourceAttachmentsSupported()) return t("sourceUnsupported");
  const backend = models.backend();
  const bytes = files.reduce((sum, file) => sum + file.size, 0);
  if (files.length > 20 || bytes > (backend === "chat" ? 128000 : 2000000) || files.some((file) => file.size > 1000000)) return t("sourceSelectionOver");
  return "";
}
function renderReviewSource() {
  const candidate = reviewSource.candidate;
  $("#source-refresh").disabled = !$("#from-run").value || reviewSource.loading || state.submitting;
  $("#source-preview").hidden = !candidate;
  notice("#source-status", reviewSourceBlock());
  if (!candidate) return;
  text("#source-candidate", `${t("sourceBinding")}: ${candidate.id}\nSHA-256: ${candidate.sha256}`);
  text("#source-claim", candidate.claim);
  $("#source-files-truncated").hidden = !reviewSource.run.formal_artifacts?.truncated;
  notice("#source-attachment-support", sourceAttachmentsSupported() ? "" : t("sourceUnsupported"));
  const filesKey = JSON.stringify([reviewSource.generation, state.language, reviewSource.files, sourceAttachmentsSupported(), reviewSource.run.busy, state.submitting]);
  if (filesKey !== reviewSource.filesKey) {
    reviewSource.filesKey = filesKey;
    const list = $("#source-file-list"); list.replaceChildren();
    for (const file of reviewSource.files) {
      const label = node("label", "source-file"), checkbox = node("input");
      checkbox.type = "checkbox"; checkbox.value = file.path; checkbox.checked = reviewSource.selected.has(file.path);
      checkbox.disabled = (!sourceAttachmentsSupported() && !checkbox.checked) || !file.downloadable || file.size > 1000000 || reviewSource.run.busy || state.submitting;
      const caption = node("span", "", `${file.path}\n${new Intl.NumberFormat(state.language).format(file.size)} ${t("sourceBytes")}${!file.downloadable || file.size > 1000000 ? ` · ${t("sourceTooLarge")}` : ""}`);
      label.append(checkbox, caption);
      checkbox.addEventListener("change", () => { if (checkbox.checked) reviewSource.selected.add(file.path); else reviewSource.selected.delete(file.path); if (!sourceAttachmentsSupported() && !checkbox.checked) checkbox.disabled = true; renderReviewSource(); updateExecutionControls(); });
      list.append(label);
    }
    if (!reviewSource.files.length) list.append(node("p", "field-hint", t("sourceFilesEmpty")));
  }
  const selected = selectedSourceFiles(), bytes = selected.reduce((sum, file) => sum + file.size, 0);
  text("#source-file-selection", `${t("sourceSelected")}: ${selected.length} · ${new Intl.NumberFormat(state.language).format(bytes)} ${t("sourceBytes")}`);
}
async function loadReviewSource() {
  const runId = $("#from-run").value, generation = ++reviewSource.generation;
  Object.assign(reviewSource, { runId, loading: Boolean(runId), error: "", run: null, candidate: null, files: [], selected: new Set() });
  renderReviewSource(); updateExecutionControls();
  if (!runId) return;
  try {
    const run = await api(`/api/runs/${encodeURIComponent(runId)}`);
    if (generation !== reviewSource.generation || $("#from-run").value !== runId) return;
    const candidate = run.candidates?.at(-1);
    reviewSource.run = run;
    if (candidate?.id && /^[a-f0-9]{64}$/.test(candidate.sha256)) reviewSource.candidate = candidate;
    reviewSource.files = (run.formal_artifacts?.items || []).filter((file) => file.reviewable !== false && typeof file.path === "string" && file.path.startsWith("workspace/") && Number.isFinite(file.size) && file.size >= 0);
  } catch (error) { if (generation === reviewSource.generation) reviewSource.error = error.message; }
  finally { if (generation === reviewSource.generation) { reviewSource.loading = false; renderReviewSource(); updateExecutionControls(); } }
}
function newTaskBlock() {
  if (agentSlots.enabled()) return agentSlots.block();
  if (state.settings?.execution && state.settings.execution !== "native") return t("nativeExecutionRequired");
  if (state.workflow === "solve" && ($("#solve-groups").value || state.settings?.solve_max_groups)
      && !($("#solve-parallel").value || state.settings?.solve_parallel_agents)) return t("solveGroupsNeedParallel");
  return models.block() || account.block(models.backend(), models.connection()) || reviewSourceBlock() || organizeSourceBlock();
}
function updateExecutionControls() {
  account.ensureLoaded();
  text("#solve-full-budget-hint", `${t("fullSolveBudgetHint")} ${finalizationBudgetHint(state.settings, Number($("#solve-parallel").value) || state.settings?.solve_parallel_agents)}`);
  const block = newTaskBlock();
  $("#start").disabled = state.submitting || !state.csrf || !state.settings || Boolean(block);
  notice("#start-readiness", block);
  // Resume uses the saved run configuration, independently of the new-task form.
  const run = state.detail;
  if (run) text("#resume-full-budget-hint", `${t("fullSolveBudgetHint")} ${finalizationBudgetHint(run.settings, Number($("#resume-parallel").value) || run.settings?.solve_parallel_agents)}`);
  const resumeGroupBlock = run?.workflow === "solve" && ($("#resume-groups").value || run.settings.solve_max_groups)
    && !($("#resume-parallel").value || run.settings.solve_parallel_agents) ? t("solveGroupsNeedParallel") : "";
  const subscriptionResume = run && !savedAgentSlots(run) && ["codex", "work"].includes(run.settings.backend || run.mode) && run.settings.codex_auth !== "api_key";
  if (subscriptionResume) account.ensureLoaded(true);
  const resumeAccountBlock = run && !savedAgentSlots(run) ? account.block(run.settings.backend || run.mode, run.settings) : "";
  const resumeBlock = resumeGroupBlock || resumeAccountBlock;
  $("#resume-submit").disabled = state.resuming || !run || run.busy || !state.csrf || Boolean(resumeBlock);
  $("#resume-account").hidden = !subscriptionResume || !resumeAccountBlock || run.busy;
  notice("#resume-readiness", resumeBlock ? `${resumeBlock}${subscriptionResume && resumeAccountBlock ? ` ${t("resumeAccountHint")}` : ""}` : "");
}
function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  $$('[data-i18n]').forEach((item) => { item.textContent = t(item.dataset.i18n); });
  $$('[data-placeholder]').forEach((item) => { item.placeholder = t(item.dataset.placeholder); });
  text("#language", state.language === "zh" ? "English" : "中文");
  state.resultsKey = "";
  renderOverview(); updateForm(); account.render(Boolean(state.csrf));
  if (state.detail) renderDetail(state.detail);
}
function setWorkflow(workflow, scroll = false) {
  state.workflow = workflow;
  notice("#form-error", ""); updateForm();
  if (scroll) { $("#composer").scrollIntoView({ behavior: "smooth", block: "start" }); $(workflow === "find" ? "#query" : workflow === "verify" ? "#verify-mode" : workflow === "organize" ? "#organize-from-run" : "#problem-id").focus({ preventScroll: true }); }
}
function updateForm() {
  const flow = state.workflow, savedReview = flow === "verify" && $("#verify-mode").value === "saved";
  // Establish visibility before disabling hidden controls. Otherwise leaving
  // roster mode exposes model fields that are still disabled by the old layout.
  agentSlots.render();
  const roster = agentSlots.enabled();
  $("#task-model-settings").hidden = roster;
  $$("[data-workflow]").forEach((button) => { const active = button.dataset.workflow === flow; button.classList.toggle("selected", active); button.setAttribute("aria-pressed", active); });
  text("#form-title", t(flow)); text("#form-description", t(`${flow}Description`)); text("#form-number", { find: "01", solve: "02", verify: "03", organize: "04" }[flow]);
  text("#start-label", state.submitting ? t("starting") : t({ find: "startFind", solve: "startSolve", verify: "startVerify", organize: "startOrganize" }[flow]));
  $("#find-fields").hidden = flow !== "find"; $("#verify-fields").hidden = flow !== "verify";
  $("#organize-fields").hidden = flow !== "organize";
  const organizeSource = state.runs.find((item) => item.id === $("#organize-from-run").value);
  text("#organize-source-note", organizeSource ? t("organizeSourceCount").replace("{n}", reviewedCandidateCount(organizeSource)) : t("organizeSourceHint"));
  $("#find-options").hidden = flow !== "find";
  $("#solve-parallel-field").hidden = flow !== "solve";
  $("#solve-groups-field").hidden = flow !== "solve";
  $("#solve-team-limits").hidden = flow !== "solve";
  $("#solve-full-budget-field").hidden = flow !== "solve" || state.settings?.execution !== "native";
  $("#saved-review").hidden = !savedReview; $("#problem-fields").hidden = ["find", "organize"].includes(flow) || savedReview;
  $("#proof-fields").hidden = flow !== "verify" || savedReview;
  $("#new-problem").hidden = Boolean($("#problem-id").value);
  const choice = flow === "solve" ? state.discoveryChoice : null;
  const problem = choice?.problem.id === $("#problem-id").value ? choice.problem : state.problems.find((item) => item.id === $("#problem-id").value);
  $("#discovery-choice").hidden = !choice;
  text("#discovery-choice-title", choice ? `${choice.problem.title} · ${choice.runId.slice(-6)}` : "");
  $("#selected-problem").hidden = !problem; text("#selected-problem", problem?.statement || "");
  $("#selected-statement-risk").hidden = !problem;
  $("#selected-statement-risk").replaceChildren(...(problem ? [MathLotteryDetails.statement(problem, state.language)] : []));
  $$("#task-form input, #task-form textarea, #task-form select").forEach((input) => { if (!input.closest("#source-file-list")) input.disabled = Boolean(input.closest("[hidden]")); });
  const backend = models.backend();
  models.render();
  if (roster && !rosterWasEnabled) manualParallel = $("#solve-parallel").value;
  if (roster) $("#solve-parallel").value = agentSlots.count || "";
  else if (rosterWasEnabled) $("#solve-parallel").value = manualParallel;
  rosterWasEnabled = roster;
  $("#solve-parallel").disabled = flow !== "solve" || roster;
  $$("#task-model-settings input, #task-model-settings select").forEach(input => { if (roster) input.disabled = true; });
  $("#native-capabilities").hidden = backend !== "codex" || roster;
  $("#multi-agent").disabled = backend !== "codex" || (flow === "solve" && Boolean($("#solve-parallel").value || state.settings?.solve_parallel_agents));
  $("#memories").disabled = backend !== "codex" || roster;
  if (roster) $("#multi-agent").disabled = true;
  text("#backend-hint", t(backend === "chat" ? models.provider() === "chat" ? "chatHint" : "customProviderHint" : "codexHint"));
  renderReviewSource();
  account.render(Boolean(state.csrf));
  updateExecutionControls();
}
function workflowLabel(workflow) {
  return t({ find: "stageFind", solve: "stageSolve", verify: "stageVerify", organize: "stageOrganize", run: "stagePipeline", pipeline: "stagePipeline" }[workflow] || workflow);
}
function groupRuns(runs) {
  return MathLotteryHistory.groupRuns(runs);
}
function renderHistory() {
  const query = $("#history-search").value.trim().toLocaleLowerCase(), filter = $("#history-filter").value;
  const matches = (run, groupTitle = "") => {
    const searchable = [groupTitle, run.title, run.id, run.settings?.model, run.settings?.provider, run.mode].join(" ").toLocaleLowerCase();
    const status = filter === "all" || (filter === "running" && run.busy) || (filter === "completed" && run.state === "COMPLETED" && !run.busy)
      || (filter === "attention" && !run.busy && (run.last_error || ["FAILED", "RATE_LIMITED", "PAUSED", "WAITING_FOR_USER"].includes(run.state)));
    return Boolean(status && (!query || searchable.includes(query)));
  };
  const signature = JSON.stringify([state.language, state.selected, state.runs, query, filter]);
  if (renderHistory.signature === signature) return;
  renderHistory.signature = signature;
  const list = $("#run-list"), scrollTop = list.scrollTop;
  const focusedId = list.contains(document.activeElement) ? document.activeElement.dataset.runId : null;
  const focusedGroup = list.contains(document.activeElement) ? document.activeElement.closest("details")?.dataset.key : null;
  const expanded = new Set($$("#run-list details[open]").map((item) => item.dataset.key));
  let focusedButton;
  const content = document.createDocumentFragment();
  const groups = groupRuns(state.runs);
  const matchingCount = new Set(groups.flatMap(group => group.runs.filter(run => matches(run, group.title)).map(run => run.id))).size;
  text("#history-count", t("historyCount").replace("{n}", matchingCount).replace("{total}", new Set(state.runs.map(run => run.id)).size));
  if (!matchingCount) { const empty = node("div", "empty"); empty.append(node("p", "", t(state.runs.length ? "historyNoMatch" : "emptyRuns")), node("p", "", t(state.runs.length ? "historyNoMatchHint" : "emptyRunsHint"))); content.append(empty); }
  for (const group of groups) {
    const matchingRuns = group.runs.filter(run => matches(run, group.title));
    if (!matchingRuns.length) continue;
    const card = node("article", "run-group"); card.dataset.problemKey = group.key;
    const title = node("h3", "run-title", group.title); title.title = group.title;
    card.append(title, node("p", "group-meta", `${group.runs.length} ${t("runRecords")} · ${t("lastUpdated")} ${date(group.latest.updated_at)}`));
    const counts = new Map(), attempts = new Map(), numbers = new Map(), latest = new Map();
    for (const run of group.runs) counts.set(run.workflow, (counts.get(run.workflow) || 0) + 1);
    for (const run of group.runs) {
      attempts.set(run.workflow, (attempts.get(run.workflow) || 0) + 1);
      numbers.set(run.id, attempts.get(run.workflow));
    }
    for (const run of matchingRuns) latest.set(run.workflow, run.id);
    const older = node("details", "history-older"); older.dataset.key = group.key;
    const olderRuns = matchingRuns.filter((run) => latest.get(run.workflow) !== run.id && !run.busy && run.id !== state.selected);
    const olderIds = new Set(olderRuns.map((run) => run.id));
    older.append(node("summary", "", t("historyEarlier").replace("{n}", olderRuns.length)));
    older.open = expanded.has(group.key) || Boolean(focusedId && olderIds.has(focusedId));
    for (const run of [...matchingRuns].reverse()) {
      const attempt = counts.get(run.workflow) > 1 ? ` · ${t("attempt").replace("{n}", numbers.get(run.id))}` : "";
      const label = `${workflowLabel(run.workflow)}${attempt}`;
      const button = node("button", `run-item${run.id === state.selected ? " active" : ""}`);
      button.type = "button"; button.dataset.runId = run.id;
      const linked = run.workflow === "find" && group.key.startsWith("problem:");
      const outcome = MathLotteryOutcomes.history(run, state.language, {linked, shared: group.sharedFindIds.includes(run.id)});
      button.setAttribute("aria-label", `${group.title} · ${label} · ${executionBadge(run).textContent} · ${outcome.textContent}`);
      button.setAttribute("aria-pressed", String(run.id === state.selected));
      const top = node("div", "run-top"), stage = node("span", "run-stage");
      stage.append(node("strong", "run-workflow", label), node("span", "", run.mode));
      top.append(stage, executionBadge(run));
      const bottom = node("div", "run-bottom");
      bottom.append(node("span", "", `${t("startedAt")} ${date(run.created_at)}`), node("span", "", `${run.iteration} ${t("rounds")} · ${compact(run.usage.input_tokens)} in`));
      button.append(top, outcome, bottom); button.addEventListener("click", () => selectRun(run.id, true));
      (olderIds.has(run.id) ? older : card).append(button);
      if (run.id === focusedId) focusedButton = button;
    }
    if (olderRuns.length) card.append(older);
    if (!focusedId && focusedGroup === group.key) focusedButton = older.querySelector("summary");
    content.append(card);
  }
  list.replaceChildren(content);
  focusedButton?.focus({ preventScroll: true });
  list.scrollTop = scrollTop;
}
function renderOverview() {
  text("#count-runs", state.runs.length); text("#count-active", state.runs.filter((run) => run.busy).length);
  text("#count-problems", state.problems.length); text("#count-candidates", state.runs.reduce((sum, run) => sum + run.candidate_count, 0));
  if (state.settings) {
    models.renderPreview();
    for (const [id, value] of [["budget", state.settings.budget_minutes], ["iterations", state.settings.max_iterations]]) $("#" + id).placeholder = value ?? t("inherited");
    $("#solve-parallel").placeholder = state.settings.solve_parallel_agents ?? t("inherited");
    $("#solve-groups").placeholder = state.settings.solve_max_groups ?? t("solveGroupsDefault");
    if (!$("#solve-full-budget").dataset.touched) $("#solve-full-budget").checked = Boolean(state.settings.solve_until_budget_exhausted);
    text("#solve-full-budget-hint", `${t("fullSolveBudgetHint")} ${finalizationBudgetHint(state.settings)}`);
  }
  const availableProblems = state.problems.map((problem) => [problem.id, state.discoveryChoice?.problem.id === problem.id ? state.discoveryChoice.problem.title : problem.title]);
  if (state.discoveryChoice && !availableProblems.some(([id]) => id === state.discoveryChoice.problem.id)) availableProblems.push([state.discoveryChoice.problem.id, state.discoveryChoice.problem.title]);
  options("#problem-id", availableProblems, t("newProblem"));
  options("#from-run", state.runs.filter((run) => run.candidate_count).map((run) => [run.id, `${run.title} · ${workflowLabel(run.workflow)} · ${run.id.slice(-6)}`]), t(state.runs.some((run) => run.candidate_count) ? "sourceRun" : "noCandidates"));
  const reviewedRuns = state.runs.filter((run) => run.workflow !== "organize" && reviewedCandidateCount(run));
  options("#organize-from-run", reviewedRuns.map((run) => [run.id, `${run.title} · ${workflowLabel(run.workflow)} · ${run.id.slice(-6)}`]), t(reviewedRuns.length ? "organizeSource" : "organizeNone"));
  renderHistory();
}
function chooseDiscovery(run, problem) {
  const hash = run.shortlist_bindings?.[problem.id];
  if (run.busy || !hash || state.submitting) return;
  state.discoveryChoice = { runId: run.id, problem: structuredClone(problem), sha256: hash };
  renderOverview(); $("#problem-id").value = problem.id;
  state.resultsKey = ""; renderResults(run); setWorkflow("solve", true);
}
function renderProblem(problem, selectable = true, discoveryRun = null) {
  const card = node("article", "problem-card"), heading = node("div", "card-heading");
  heading.append(node("h3", "", problem.title), badge(problem.status)); card.append(heading);
  if (discoveryRun) {
    card.dataset.discoveryProblem = problem.id;
    if (discoveryRun.problem?.id === problem.id) card.append(node("p", "recommendation", t("recommended")));
    card.classList.toggle("chosen-problem", state.discoveryChoice?.runId === discoveryRun.id && state.discoveryChoice.problem.id === problem.id);
  }
  const metrics = node("dl", "problem-metrics");
  for (const [label, value] of [["difficulty", problem.difficulty_estimate], ["feasibility", problem.verification_feasibility], ["leanFeasibility", problem.lean_feasibility]]) {
    const item = node("div"); item.append(node("dt", "", t(label)), node("dd", "", !value || value === "unknown" ? t("unknown") : value)); metrics.append(item);
  }
  card.append(metrics, MathLotteryDetails.statement(problem, state.language));
  const details = node("details"), summary = node("summary", "", t("statementDetails")); details.append(summary, node("pre", "", problem.statement));
  if (problem.selection_reason) details.append(node("p", "", `${t("selection")}: ${problem.selection_reason}`));
  if (problem.source_url) { const p = node("p"); p.append(safeLink(problem.source_url)); details.append(p); }
  appendEvidenceList(details, t("prerequisites"), problem.prerequisites);
  appendEvidenceList(details, t("obstacles"), problem.known_obstacles);
  if (problem.initial_approach) details.append(node("p", "", `${t("initialApproach")}: ${problem.initial_approach}`));
  if (problem.status_evidence.length) { details.append(node("h3", "", t("sourceEvidence"))); const list = node("ul"); for (const item of problem.status_evidence) { const li = node("li"); li.append(safeLink(item)); list.append(li); } details.append(list); }
  for (const reference of problem.references) { const p = node("p"); p.append(safeLink(reference.url, reference.title || reference.url)); details.append(p); }
  card.append(details);
  card.append(renderSourceAssessment(problem.evidence_assessment, problem.literature_search, problem.title, state.detail?.workflow === "find"));
  if (selectable) {
    const chosen = discoveryRun && state.discoveryChoice?.runId === discoveryRun.id && state.discoveryChoice.problem.id === problem.id;
    const button = node("button", "secondary", t(chosen ? "chosen" : discoveryRun ? "chooseProblem" : "solveThis")); button.type = "button";
    button.disabled = state.submitting || Boolean(discoveryRun && (discoveryRun.busy || !discoveryRun.shortlist_bindings?.[problem.id]));
    button.setAttribute("aria-pressed", String(Boolean(chosen)));
    button.addEventListener("click", () => {
      if (discoveryRun) chooseDiscovery(discoveryRun, problem);
      else { state.discoveryChoice = null; $("#problem-id").value = problem.id; if (!$("#problem-id").value) { $("#title").value = problem.title; $("#statement").value = problem.statement; } setWorkflow("solve", true); }
    }); card.append(button);
  }
  keyDisclosures(card, `problem:${problem.id}`);
  return card;
}
function candidateAssessment(candidate, problem) {
  const summary = node("dl", "assessment-summary"), latest = candidate.reviews.at(-1);
  for (const [label, value] of [["proofLevel", candidate.level], ["latestReview", latest?.verdict || "unreviewed"], ["declaredScope", candidate.scope || "UNKNOWN"], ["originalCoverage", latest?.original_problem_coverage || "UNKNOWN"], ["problemStatus", problem?.status || "UNKNOWN"], ["novelty", latest?.novelty || "UNKNOWN"]]) {
    const item = node("div"); item.dataset.assessment = label;
    item.append(node("dt", "", t(label)), node("dd", "", t(value))); summary.append(item);
  }
  return summary;
}
function appendEvidenceList(parent, label, items) {
  if (!items?.length) return;
  parent.append(node("h4", "", label));
  const list = node("ul"); for (const item of items) list.append(node("li", "", item)); parent.append(list);
}
function prepareObstacleFollowup(item, context) {
  const run = state.detail;
  if (!run || run.busy || state.submitting || !["find", "verify"].includes(run.workflow)) return;
  const direction = state.language === "zh"
    ? `请继续核查“${context || run.title}”的新颖性障碍 ${item.id}。\n障碍：${item.description}\n影响：${item.impact}\n下一步：${item.next_action}\n来源：${item.source_url || "未指定"}\n请保留原障碍编号，用可定位的原文、独立来源证据和逐项比较支持处理结论。无法解决时保留 OPEN 并说明原因，不要仅凭未搜到结果宣称新颖。`
    : `Investigate novelty obstacle ${item.id} for “${context || run.title}”.\nObstacle: ${item.description}\nImpact: ${item.impact}\nNext action: ${item.next_action}\nSource: ${item.source_url || "not specified"}\nPreserve the obstacle ID. Support any resolution with located quotations, independent source evidence and explicit comparison. Leave unresolved items OPEN with reasons; absence of search results is not evidence of novelty.`;
  $("#direction").value = direction + (item.required_locator ? `\nRequired locator: ${item.required_locator}` : "") + (item.required_excerpt_sha256 ? `\nRequired excerpt SHA-256: ${item.required_excerpt_sha256}` : "");
  $("#resume-form").hidden = false;
  $("#direction").focus();
  $("#resume-form").scrollIntoView({behavior: "smooth", block: "center"});
  toast(state.language === "zh" ? "已填写核查方向；检查预算后点击继续研究。" : "Follow-up prepared. Review the budget, then click Continue research.");
}
function renderSourceAssessment(assessment, search, context, allowFollowup = true) {
  const section = node("details", "evidence-assessment");
  const label = assessment?.policy_version ? `${t("evidenceGaps")}${assessment.reasons?.length ? ` (${assessment.reasons.length})` : ""}` : t("notAssessed");
  section.append(node("summary", "", label));
  const canFollow = allowFollowup && state.detail && !state.detail.busy && !state.submitting && ["find", "verify"].includes(state.detail.workflow);
  section.append(MathLotteryDetails.novelty(assessment, search, state.language, safeLink, canFollow ? (item) => prepareObstacleFollowup(item, context) : null));
  if (!assessment?.policy_version) { section.append(node("p", "field-hint", t("notAssessed"))); return section; }
  section.append(node("p", "field-hint", `${assessment.policy_version} · ${assessment.assessed_at || ""}`));
  appendEvidenceList(section, t("evidenceGate"), assessment.reasons);
  appendEvidenceList(section, t("searchLimitations"), assessment.limitations);
  for (const citation of assessment.checked_citations || []) {
    const p = node("p"); p.append(safeLink(citation.url), document.createTextNode(` · ${citation.locator} · ${t(citation.verified_excerpt ? "excerptMatched" : "excerptMissing")}`)); section.append(p);
  }
  if (assessment.observed_queries?.length) {
    const queries = node("details", "observed-queries"), list = node("ul");
    queries.append(node("summary", "", `${t("searchObserved")} (${assessment.observed_queries.length})`));
    for (const query of assessment.observed_queries) list.append(node("li", "", query));
    queries.append(list); section.append(queries);
  }
  section.append(node("p", "field-hint", t("sourceLimit")));
  return section;
}
function renderReviewChecks(review, allowFollowup = false) {
  const section = node("div", "review-checks");
  section.append(node("p", "", `${t("originalCoverage")}: ${t(review.original_problem_coverage || "UNKNOWN")}\n${review.coverage_explanation || ""}`));
  appendEvidenceList(section, t("evidenceGate"), review.validation_notes);
  section.append(MathLotteryDetails.proof(review, state.language));
  if (review.checks?.length) {
    const details = node("details"); details.append(node("summary", "", t("proofChecks")));
    for (const check of review.checks) {
      details.append(node("h4", "", `${check.method} · ${t(check.result)} · ${check.claim}`), node("pre", "", check.reasoning));
      appendEvidenceList(details, t("proofEvidence"), check.evidence);
    }
    section.append(details);
  }
  section.append(renderSourceAssessment(review.evidence_assessment, review.literature_search, null, allowFollowup));
  if (review.formal_receipt) {
    const details = node("details", "formal-receipt"); details.append(node("summary", "", `${t("formalReceipt")}: ${t(review.formal_receipt.status)}`), node("p", "field-hint", t("formalScope")), node("pre", "", JSON.stringify(review.formal_receipt, null, 2))); section.append(details);
  }
  return section;
}
function renderReviewEvidence(manifest) {
  const section = node("details", "review-evidence"); section.dataset.key = "review-evidence";
  section.append(node("summary", "", t("evidenceSnapshot")), node("p", "field-hint", t("snapshotNote")));
  section.append(node("p", "source-binding", `${t("snapshotCandidate")}: ${manifest.source_run_id} / ${manifest.source_candidate_id}\nSHA-256: ${manifest.candidate_sha256}`));
  const files = Array.isArray(manifest.files) ? manifest.files : [], bytes = files.reduce((sum, file) => sum + (Number.isFinite(file.size) ? file.size : 0), 0);
  section.append(node("p", "field-hint", `${t("snapshotFiles")}: ${files.length} · ${new Intl.NumberFormat(state.language).format(bytes)} ${t("sourceBytes")}`));
  const list = node("ul", "snapshot-manifest");
  for (const file of files) {
    const item = node("li"); item.append(node("span", "", file.path), node("span", "", `${file.size} ${t("sourceBytes")}`), node("code", "", `SHA-256: ${file.sha256}`)); list.append(item);
  }
  section.append(list);
  if (!files.length) section.append(node("p", "field-hint", t("snapshotEmpty")));
  return section;
}
function keyDisclosures(container, prefix) {
  [...container.querySelectorAll("details")].forEach((item, index) => {
    if (!item.dataset.key) item.dataset.key = `${prefix}:${index}`;
  });
}
function renderOrganizedReport(run) {
  const report = run.organized_report, section = node("section", "organized-report");
  section.append(node("h3", "", t("organizeReport")), node("p", "field-hint", t("organizeScope")));
  if (report?.source_run_id) {
    const origin = node("p", "organized-origin", `${t("organizeOrigin")}: `), link = node("button", "text-button", report.source_run_id);
    link.type = "button"; link.addEventListener("click", () => selectRun(report.source_run_id, true)); origin.append(link); section.append(origin);
  }
  const reports = report?.reports || (report?.markdown_available ? { [report.language || "zh"]: report } : {});
  const available = ["zh", "en"].filter((language) => reports[language]?.markdown_available);
  if (!available.length) {
    section.append(node("p", "notice", t("organizePending")));
    return section;
  }
  if (available.length < 2) section.append(node("p", "notice", t("organizeLegacy")));
  const versions = node("div", "organized-versions");
  for (const language of ["zh", "en"]) {
    const edition = reports[language], panel = node("section", "organized-version");
    panel.dataset.language = language;
    panel.append(node("h4", "", language === "zh" ? "中文" : "English"));
    if (edition?.expert_brief_available) panel.append(node("p", "field-hint", state.language === "zh" ? "含专家速览：结论、关键步骤、验证缺口及材料索引。" : "Includes an expert briefing: conclusions, key steps, verification gaps and source index."));
    if (!edition?.markdown_available) {
      panel.append(node("p", "field-hint", t("organizeMissingLanguage"))); versions.append(panel); continue;
    }
    const downloads = node("div", "organized-downloads");
    for (const [format, label, ready, extension] of [["markdown", "organizeMarkdown", edition.markdown_available, "md"], ["pdf", "organizePdf", edition.pdf_available, "pdf"]]) {
      if (!ready) continue;
      const link = node("a", "secondary", t(label));
      link.href = `/api/runs/${encodeURIComponent(run.id)}/organized?format=${format}&language=${language}`;
      link.download = `report.${language}.${extension}`; downloads.append(link);
    }
    panel.append(downloads);
    if (!edition.pdf_available) panel.append(node("p", "notice", [t("organizePdfFailed"), edition.pdf_error].filter(Boolean).join("\n")));
    if (edition.pdf_warnings?.length) appendEvidenceList(panel, t("organizePdfWarnings"), edition.pdf_warnings);
    if (edition.markdown_sha256) {
      const provenance = node("details", "inline-help"); provenance.dataset.key = `organized-digest-${language}`;
      provenance.append(node("summary", "", t("organizeDigest")), node("p", "source-binding", edition.markdown_sha256)); panel.append(provenance);
    }
    versions.append(panel);
  }
  section.append(versions);
  if (report?.bundle_available ?? report?.markdown_available) {
    const downloads = node("div", "organized-downloads"), bundle = node("a", "secondary", t("organizeBundle"));
    bundle.href = `/api/runs/${encodeURIComponent(run.id)}/organized?format=bundle`;
    bundle.download = "expert-reports.zip"; downloads.append(bundle); section.append(downloads);
    if (report.public_bundle_available) {
      const share = node("a", "secondary", state.language === "zh" ? "脱敏文本分享包" : "Redacted text sharing bundle");
      share.href = `/api/runs/${encodeURIComponent(run.id)}/organized?format=public_bundle`;
      share.download = "expert-reports-public-text.zip"; downloads.append(share);
      section.append(node("p", "field-hint", state.language === "zh" ? "分享包包含脱敏后的中英文 Markdown、文本材料、导出映射和专家入口；不含 PDF。分享前仍请检查内容。原始材料 ZIP 保留原始证据。" : "The sharing bundle contains redacted bilingual Markdown, text materials, export mappings and the expert entry point; PDFs are omitted. Review before sharing. The original ZIP preserves the evidence."));
    }
    if (report.handoff_available) section.append(node("p", "field-hint", state.language === "zh" ? "专家可先打开 ZIP 中 handoff/START_HERE.zh.md：包含主张索引、验证缺口和复现说明。" : "Experts can start with handoff/START_HERE.en.md in the ZIP for claims, verification gaps and reproduction instructions."));
  }
  if (available.some((language) => !reports[language].pdf_available) || !report.handoff_available) {
    const retry = node("button", "secondary", pdfExports.has(run.id) ? t("organizeRetryingPdf") : state.language === "zh" ? "补齐本地交付文件" : "Complete local delivery files");
    retry.id = "retry-pdf"; retry.type = "button"; retry.disabled = run.busy || pdfExports.has(run.id);
    retry.addEventListener("click", async () => {
      if (pdfExports.has(run.id)) return;
      pdfExports.add(run.id); renderResults(run);
      try { await api(`/api/runs/${encodeURIComponent(run.id)}/organized`, {}); await refresh(); }
      catch (error) { if (state.selected === run.id) notice("#run-message", error.message); }
      finally { pdfExports.delete(run.id); if (state.detail?.id === run.id) renderResults(state.detail); }
    });
    section.append(retry, node("p", "field-hint", t("organizeRetryHint")));
  }
  return section;
}
function renderResults(run) {
  const key = JSON.stringify([state.language, run.id, run.problem, run.shortlist, run.candidates, run.formal_artifacts, run.review_evidence, run.discovery_context, run.discovery_request, run.shortlist_bindings, run.organized_report, pdfExports.has(run.id), run.busy, state.submitting, state.discoveryChoice]);
  if (state.resultsKey === key) return;
  state.resultsKey = key;
  const disclosureState = new Map($$("#results details[data-key]").map((item) => [item.dataset.key, item.open]));
  const focusedKey = $("#results").contains(document.activeElement) && document.activeElement.tagName === "SUMMARY" ? document.activeElement.parentElement.dataset.key : null;
  const results = $("#results"); results.replaceChildren();
  if (run.workflow === "organize") results.append(renderOrganizedReport(run));
  if (run.workflow === "find" && run.discovery_request) {
    const preferences = node("details", "find-preferences"); preferences.dataset.key = "find-preferences";
    preferences.append(node("summary", "", t("findCriteria")), node("p", "problem-preview", run.discovery_request));
    results.append(preferences);
  }
  if (run.shortlist.length) {
    const selection = node("section", "discovery-selection");
    selection.append(node("h3", "", t("chooseStep")), node("p", "", t("chooseHint")), node("p", "field-hint", t("estimateHint")));
    if (run.busy) selection.append(node("p", "notice", t("findNotReady")));
    for (const problem of run.shortlist) selection.append(renderProblem(problem, true, run.workflow === "find" ? run : null));
    results.append(selection);
  }
  if (run.discovery_context) {
    const context = run.discovery_context, section = node("section", "discovery-context");
    section.append(node("h3", "", t("discoveryOrigin")));
    const link = node("button", "text-button", context.source_run_id); link.type = "button"; link.addEventListener("click", () => selectRun(context.source_run_id, true)); section.append(link);
    section.append(node("p", "field-hint", t("contextScope")));
    const details = node("details"); details.dataset.key = "discovery-files"; details.append(node("summary", "", `${t("contextFiles")}: ${context.files.length}`));
    const files = node("ul"); for (const file of context.files) files.append(node("li", "", `${file.path} · ${compact(file.size)} B`)); details.append(files);
    appendEvidenceList(details, t("contextOmitted"), context.omitted); section.append(details); results.append(section);
  }
  if (!run.shortlist.length && run.problem) results.append(renderProblem(run.problem, false));
  if (run.workflow !== "organize" && !run.shortlist.length && !run.candidates.length) { const empty = node("div", "empty"); empty.append(node("p", "", t("noResults")), node("p", "", t("waitingResults"))); results.append(empty); }
  if (run.review_evidence) results.append(renderReviewEvidence(run.review_evidence));
  const displayedCandidates = run.workflow === "organize" ? [] : run.candidates;
  if (displayedCandidates.length) results.append(node("p", "field-hint", t("assessmentLimit")));
  for (const [index, candidate] of [...displayedCandidates].reverse().entries()) {
    const version = run.candidates.length - index;
    const card = node("article", "candidate-card"), heading = node("div", "card-heading");
    heading.append(node("h3", "", index ? t("candidateVersion").replace("{n}", version) : t("latestCandidate")), badge(candidate.level));
    card.append(heading, node("p", "candidate-identifier", candidate.id), candidateAssessment(candidate, run.problem));
    const levelNote = { CANDIDATE: "levelCandidate", SELF_CHECKED: "levelSelfChecked", PARTIALLY_VERIFIED: "levelPartial", FORMALLY_VERIFIED: "levelFormal", EXPERT_REVIEWED: "levelExpert", REJECTED: "levelRejected" }[candidate.level];
    if (levelNote) card.append(node("p", "proof-level-note", t(levelNote)));
    card.append(node("p", "claim-title", candidate.claim));
    appendEvidenceList(card, t("obligations"), candidate.remaining_obligations);
    const details = node("details"); details.dataset.key = candidate.id; details.append(node("summary", "", t("fullProof")));
    appendEvidenceList(details, t("assumptions"), candidate.assumptions);
    details.append(node("pre", "", candidate.proof)); card.append(details);
    const evidence = Array.isArray(candidate.evidence) ? candidate.evidence.filter((item) => typeof item === "string") : [];
    const references = Array.isArray(candidate.references) ? candidate.references : [];
    if (evidence.length || references.length) {
      const sources = node("details", "candidate-evidence"); sources.dataset.key = `${candidate.id}:sources`;
      sources.append(node("summary", "", t("proofEvidence")));
      for (const item of evidence) { const p = node("p"); p.append(safeLink(item)); sources.append(p); }
      for (const reference of references) {
        const url = typeof reference === "string" ? reference : reference?.url || reference?.artifact || "";
        const title = typeof reference === "string" ? reference : reference?.title || url;
        if (typeof url === "string" && typeof title === "string" && (url || title)) {
          const p = node("p"), referenceLink = safeLink(url, title);
          p.append(referenceLink);
          if (referenceLink.tagName !== "A" && url && title !== url) p.append(document.createTextNode(` (${url})`));
          sources.append(p);
        }
      }
      card.append(sources);
    }
    for (const [reviewIndex, review] of [...candidate.reviews].reverse().entries()) {
      const reviewNumber = candidate.reviews.length - reviewIndex;
      const section = node("div", "review"), row = node("div", "card-heading");
      row.append(node("h3", "", reviewIndex ? t("reviewVersion").replace("{n}", reviewNumber) : t("latestReview")), badge(review.verdict)); section.append(row);
      const body = node("details", "review-details"); body.dataset.key = `${candidate.id}:review:${reviewNumber}`;
      body.append(node("summary", "", t("reviewDetails")), node("p", "", review.truth_assessment), node("p", "", review.proof_assessment));
      // Keep the latest supported issues and outstanding obligations above the fold.
      const issues = reviewIndex ? body : section;
      appendEvidenceList(issues, t("ISSUES_FOUND"), review.issues);
      appendEvidenceList(issues, t("obligations"), review.remaining_obligations);
      body.append(node("p", "", `${t("novelty")}: ${t(review.novelty)}\n${review.novelty_notes}`), renderReviewChecks(review, index === 0 && reviewIndex === 0));
      for (const evidence of review.evidence) { const p = node("p"); p.append(safeLink(evidence)); body.append(p); }
      keyDisclosures(body, `${candidate.id}:review:${reviewNumber}`);
      if (reviewIndex) { body.querySelector("summary").textContent = `${t("reviewVersion").replace("{n}", reviewNumber)} · ${t(review.verdict)}`; card.append(body); }
      else { section.append(body); card.append(section); }
    }
    if (!candidate.reviews.length) card.append(node("p", "field-hint", t("unreviewed")));
    if (index) {
      const archive = node("details", "candidate-archive"); archive.dataset.key = `archive:${candidate.id}`;
      archive.append(node("summary", "", `${t("earlierCandidate").replace("{n}", version)} · ${t(candidate.level)}`), card); results.append(archive);
    } else results.append(card);
  }
  const files = run.formal_artifacts;
  if (files?.items?.length || files?.truncated) {
    const section = node("section", "formal-artifacts");
    section.append(node("h3", "", t("leanFiles")), node("p", "field-hint", t("leanFilesNote")));
    const list = node("ul");
    for (const file of files.items || []) {
      if (typeof file.path !== "string") continue;
      const item = node("li"), label = `${file.path} · ${compact(file.size)} B`;
      if (file.downloadable) {
        const link = node("a", "", label);
        link.href = `/api/runs/${encodeURIComponent(run.id)}/artifact?path=${encodeURIComponent(file.path)}`;
        link.download = file.path.split("/").pop(); item.append(link);
      } else item.append(node("span", "", `${label} — ${t("leanFileTooLarge")}`));
      list.append(item);
    }
    section.append(list);
    if (files.truncated) section.append(node("p", "field-hint", t("leanFilesTruncated")));
    results.append(section);
  }
  keyDisclosures(results, run.id);
  for (const item of results.querySelectorAll("details")) {
    if (disclosureState.has(item.dataset.key)) item.open = disclosureState.get(item.dataset.key);
    if (focusedKey === item.dataset.key) item.querySelector("summary")?.focus({ preventScroll: true });
  }
}
function renderDetail(run) {
  $("#run-detail").hidden = false;
  $("#resume-parallel-field").hidden = run.workflow !== "solve";
  $("#resume-parallel").disabled = run.workflow !== "solve" || savedAgentSlots(run);
  if (savedAgentSlots(run)) $("#resume-parallel").value = "";
  $("#resume-parallel").placeholder = run.settings.solve_parallel_agents ?? t("inherited");
  $("#resume-groups-field").hidden = run.workflow !== "solve";
  $("#resume-groups").disabled = run.workflow !== "solve";
  $("#resume-team-limits").hidden = run.workflow !== "solve";
  $("#resume-groups").placeholder = run.settings.solve_max_groups ?? t("solveGroupsDefault");
  solveTeams.render(run, state.language);
  $("#resume-full-budget-field").hidden = run.workflow !== "solve" || run.settings.execution !== "native";
  if ($("#resume-full-budget").dataset.runId !== run.id) {
    $("#resume-full-budget").checked = Boolean(run.settings.solve_until_budget_exhausted);
    $("#resume-full-budget").dataset.runId = run.id;
  }
  text("#resume-full-budget-hint", `${t("fullSolveBudgetHint")} ${finalizationBudgetHint(run.settings)}`);
  text("#detail-id", `${run.workflow.toUpperCase()} / ${run.id}`); text("#detail-title", run.title);
  const status = executionBadge(run); $("#detail-state").className = status.className; text("#detail-state", status.textContent);
  $("#run-facts").replaceChildren(...[models.summary(run.settings, run.mode), `${run.iteration} ${t("rounds")}`, `${Math.round(run.elapsed_seconds / 60 * 10) / 10} min ${t("elapsed")}`, `${compact(run.usage.input_tokens)} in / ${compact(run.usage.output_tokens)} out ${t("tokens")}`].map((fact) => node("span", "", fact)));
  const outcomeKey = JSON.stringify([run.id, run.workflow, state.language, run.research_outcome]);
  if (renderDetail.outcomeKey !== outcomeKey) {
    $("#research-outcome").replaceChildren(MathLotteryOutcomes.detail(run, state.language));
    $("#research-outcome").hidden = run.workflow === "find";
    renderDetail.outcomeKey = outcomeKey;
  }
  const interrupted = !run.busy && (["queued", "running", "interrupted"].includes(run.worker?.state) || run.worker_state === "interrupted");
  const timingNote = run.elapsed_timing_basis === "last_resource_sample"
    ? (state.language === "zh" ? "进程异常退出：耗时停在最后一次资源采样；停机期间不计入预算。恢复后接续原检查点。" : "Worker interrupted: elapsed time is bounded by the last resource sample; downtime is excluded. Resume continues the saved checkpoint.") : null;
  // Old workers may retain the recovered attempt's error until their next checkpoint.
  const currentError = run.busy && run.last_error === "Recovered an interrupted native attempt; its token usage is unknown"
    ? (state.language === "zh" ? "已续接原研究会话；上一次中断调用的 token 用量未知。" : "The original research session has resumed; token usage for the interrupted call is unknown.") : run.last_error;
  const message = [finalizationNotice(run), currentError, interrupted ? t("workerInterrupted") : run.worker?.error, timingNote, run.stop_reason, run.metrics.usage_warning].filter(Boolean).join("\n"); notice("#run-message", message);
  $("#run-message").classList.toggle("error", Boolean(run.last_error || run.worker?.error));
  $("#stop").hidden = !run.busy; $("#stop").disabled = run.stop_requested; text("#stop", t(run.stop_requested ? "stopping" : "stop"));
  $("#show-resume").hidden = run.busy || run.mode === "manual";
  updateExecutionControls();
  $("#verify-latest").hidden = run.workflow === "organize" || !run.candidates.length;
  $("#organize-reviewed").hidden = run.workflow === "organize" || !reviewedCandidateCount(run);
  $("#organize-reviewed").disabled = run.busy || state.submitting;
  $("#download").href = `/api/runs/${run.id}/report`;
  text("#download", t(run.workflow === "organize" ? "downloadTaskReport" : "download"));
  renderResults(run);
  const runtime = MathLotteryDetails.runtime(run, state.language);
  notice("#runtime-summary", runtime.summary);
  $("#runtime-details").replaceChildren(runtime.element);
  const activityDownload = node("a", "secondary small", state.language === "zh" ? "下载已记录的完整活动" : "Download all recorded activity");
  activityDownload.href = `/api/runs/${encodeURIComponent(run.id)}/activity`;
  activityDownload.download = "activity.jsonl";
  $("#runtime-details").append(activityDownload, node("p", "field-hint", state.language === "zh" ? "下载包含已保存的可见活动及执行资源记录。旧版本未记录的历史、隐藏推理和远端资源不会补造。" : "Includes saved visible events and execution resource records. Missing legacy history, hidden reasoning and remote resources are not reconstructed."));
  text("#progress", run.progress.text || t("noProgress")); text("#progress-note", [run.progress.checking_evidence ? t("checkingEvidence") : "", run.progress.truncated ? t("truncated") : ""].filter(Boolean).join(" "));
  text("#report-text", run.report.text || t("noReport")); text("#report-note", run.report.truncated ? t("truncated") : "");
  const eventList = $("#event-list"); eventList.replaceChildren();
  for (const event of run.events) { const row = node("div", "event"); const time = node("time", "", date(event.time)); row.append(time, node("span", "", `${event.phase} · ${event.event}${event.error ? ` · ${event.error}` : ""}`)); eventList.append(row); }
}
async function selectRun(id, scroll = false) {
  state.selected = id; preference("mathlottery.run", id); state.resultsKey = ""; $("#resume-form").hidden = true;
  try {
    const run = await api(`/api/runs/${id}`);
    if (state.selected !== id) return;
    delete $("#resume-full-budget").dataset.runId;
    $("#resume-budget").value = ""; $("#resume-rounds").value = ""; $("#resume-parallel").value = ""; $("#resume-groups").value = ""; $("#direction").value = "";
    state.detail = run; renderOverview(); renderDetail(run);
    $("#resume-budget").placeholder = run.settings.budget_minutes; $("#resume-rounds").placeholder = run.settings.max_iterations;
    $("#resume-lean-limits").hidden = !["verify", "run"].includes(run.workflow);
    for (const [field, selector] of Object.entries({formal_memory_mb: "#resume-lean-memory", formal_address_space_mb: "#resume-lean-address", formal_timeout_seconds: "#resume-lean-timeout"})) {
      $(selector).value = ""; $(selector).placeholder = run.settings.formal_limits?.[field] ?? "";
    }
    if (scroll) $("#run-detail").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { notice("#global-error", error.message); }
}
async function refresh() {
  if (state.polling) return;
  state.polling = true;
  const selectedAtStart = state.selected;
  try {
    const data = await api("/api/bootstrap"); state.csrf = data.csrf_token; state.settings = data.settings; state.runs = data.runs; state.problems = data.problems;
    text("#connection", t("connected")); notice("#global-error", data.config_error); renderOverview(); updateForm(); account.render(Boolean(state.csrf));
    models.ensureLoaded();
    // A poll begun before a click/start must not replace that newer selection.
    if (state.selected !== selectedAtStart) return;
    if (state.selected && state.runs.some((run) => run.id === state.selected)) {
      const id = state.selected, run = await api(`/api/runs/${id}`);
      if (state.selected === id) { state.detail = run; renderDetail(run); }
    } else if (state.runs.length) await selectRun(state.runs[0].id);
  } catch (error) { text("#connection", t("disconnected")); notice("#global-error", error.message); }
  finally { state.polling = false; }
}
function overrides() {
  const values = agentSlots.enabled() ? { use_agent_slots: true } : models.overrides();
  for (const [id, key] of [["budget", "budget_minutes"], ["iterations", "max_iterations"]]) {
    const input = $("#" + id), value = input.value.trim();
    if (value && !input.disabled) values[key] = ["budget", "iterations"].includes(id) ? Number(value) : value;
  }
  for (const [id, key] of [["multi-agent", "native_multi_agent"], ["memories", "native_memories"]]) {
    const input = $("#" + id); if (input.value && !input.disabled) values[key] = input.value === "inherit" ? null : input.value === "true";
  }
  if (!$("#solve-full-budget-field").hidden && !$("#solve-full-budget").disabled) values.solve_until_budget_exhausted = $("#solve-full-budget").checked;
  if (!$("#solve-parallel-field").hidden && !$("#solve-parallel").disabled && $("#solve-parallel").value) values.solve_parallel_agents = Number($("#solve-parallel").value);
  if (!$("#solve-groups-field").hidden && $("#solve-groups").value) values.solve_max_groups = Number($("#solve-groups").value);
  return values;
}
$("#solve-parallel").addEventListener("change", updateForm);
["solve-parallel", "solve-groups", "resume-parallel", "resume-groups"].forEach(id => $("#" + id).addEventListener("input", updateExecutionControls));
$("#solve-full-budget").addEventListener("change", () => { $("#solve-full-budget").dataset.touched = "true"; });
$$("[data-workflow]").forEach((button) => button.addEventListener("click", () => setWorkflow(button.dataset.workflow, button.classList.contains("nav-item"))));
$("#verify-mode").addEventListener("change", updateForm);
$("#problem-id").addEventListener("change", () => { state.discoveryChoice = null; state.resultsKey = ""; if (state.detail) renderResults(state.detail); updateForm(); });
$("#clear-discovery").addEventListener("click", () => { state.discoveryChoice = null; $("#problem-id").value = ""; state.resultsKey = ""; if (state.detail) renderResults(state.detail); updateForm(); });
$("#from-run").addEventListener("change", loadReviewSource);
$("#organize-from-run").addEventListener("change", updateForm);
$("#source-refresh").addEventListener("click", loadReviewSource);
$("#language").addEventListener("click", () => { state.language = state.language === "en" ? "zh" : "en"; preference("mathlottery.language", state.language); applyLanguage(); text("#connection", t(state.csrf ? "connected" : "connecting")); });
$("#refresh").addEventListener("click", refresh);
$("#history-search").addEventListener("input", renderHistory);
$("#history-filter").addEventListener("change", renderHistory);
$("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault(); if (state.submitting) return;
  const block = newTaskBlock();
  if (block || !state.csrf || !state.settings) { updateExecutionControls(); return; }
  const body = { workflow: state.workflow, options: overrides() };
  if ($("#instructions").value.trim()) body.instructions = $("#instructions").value.trim();
  if (state.workflow === "find") { body.count = Number($("#count").value); if ($("#query").value.trim()) body.query = $("#query").value.trim(); if ($("#source").value.trim()) body.source = $("#source").value.trim(); }
  else if (state.workflow === "organize") {
    body.from_run = $("#organize-from-run").value;
    body.language = state.language; // Preferred export alias; Organize always creates both languages.
  }
  else if (state.workflow === "verify" && $("#verify-mode").value === "saved") {
    body.from_run = reviewSource.runId;
    body.from_candidate_id = reviewSource.candidate.id;
    body.from_candidate_sha256 = reviewSource.candidate.sha256;
    body.source_files = selectedSourceFiles().map((file) => file.path);
  }
  else {
    if ($("#problem-id").value) body.problem_id = $("#problem-id").value;
    else { body.statement = $("#statement").value; if ($("#title").value.trim()) body.title = $("#title").value.trim(); }
    if (state.workflow === "verify") body.proof = $("#proof").value;
    if (state.workflow === "solve" && state.discoveryChoice && body.problem_id === state.discoveryChoice.problem.id) {
      body.from_discovery = state.discoveryChoice.runId; body.discovery_problem_sha256 = state.discoveryChoice.sha256;
    }
  }
  state.submitting = true; updateForm(); notice("#form-error", "");
  try { const run = await api("/api/runs", body); await refresh(); await selectRun(run.id, true); toast(t("launched")); }
  catch (error) { notice("#form-error", error.message); await account.refresh(); }
  finally { state.submitting = false; updateForm(); }
});
// Native validation must reveal an invalid optional field before focusing it.
$$("form").forEach((form) => form.addEventListener("invalid", (event) => {
  for (let details = event.target.closest("details"); details; details = details.parentElement.closest("details")) details.open = true;
}, true));
$("#stop").addEventListener("click", async () => {
  $("#stop").disabled = true;
  try { await api(`/api/runs/${state.selected}/stop`, {}); toast(t("stopSent")); await refresh(); }
  catch (error) { notice("#run-message", error.message); $("#stop").disabled = false; }
});
$("#show-resume").addEventListener("click", () => { $("#resume-form").hidden = !$("#resume-form").hidden; if (!$("#resume-form").hidden) $("#direction").focus(); });
$("#resume-account").addEventListener("click", () => account.openSubscription());
$("#resume-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const body = {};
  const run = state.detail;
  if (state.resuming || !run || run.busy || !state.csrf || (!savedAgentSlots(run) && account.block(run.settings.backend || run.mode, run.settings))) { updateExecutionControls(); return; }
  if ($("#direction").value.trim()) body.message = $("#direction").value.trim();
  if ($("#resume-budget").value) body.budget_minutes = Number($("#resume-budget").value);
  if ($("#resume-rounds").value) body.max_iterations = Number($("#resume-rounds").value);
  if (!$("#resume-parallel-field").hidden && !$("#resume-parallel").disabled && $("#resume-parallel").value) body.solve_parallel_agents = Number($("#resume-parallel").value);
  if (!$("#resume-groups-field").hidden && $("#resume-groups").value) body.solve_max_groups = Number($("#resume-groups").value);
  if (!$("#resume-full-budget-field").hidden) body.solve_until_budget_exhausted = $("#resume-full-budget").checked;
  if (!$("#resume-lean-limits").hidden) {
    for (const [field, selector] of Object.entries({formal_memory_mb: "#resume-lean-memory", formal_address_space_mb: "#resume-lean-address", formal_timeout_seconds: "#resume-lean-timeout"})) {
      if ($(selector).value) body[field] = Number($(selector).value);
    }
  }
  state.resuming = true; updateExecutionControls();
  try { await api(`/api/runs/${state.selected}/resume`, body); $("#resume-form").hidden = true; toast(t("resumed")); await refresh(); }
  catch (error) { notice("#run-message", error.message); await account.refresh(); }
  finally { state.resuming = false; updateExecutionControls(); }
});
$("#verify-latest").addEventListener("click", () => { $("#verify-mode").value = "saved"; $("#from-run").value = state.selected; setWorkflow("verify", true); loadReviewSource(); });
$("#organize-reviewed").addEventListener("click", () => {
  if (!state.detail || state.detail.busy || !reviewedCandidateCount(state.detail)) return;
  $("#organize-from-run").value = state.selected;
  setWorkflow("organize", true); toast(t("organizePrepared"));
});
$$("[data-tab]").forEach((button) => button.addEventListener("click", () => {
  $$("[data-tab]").forEach((item) => { const active = item === button; item.classList.toggle("selected", active); item.setAttribute("aria-selected", active); $("#" + item.dataset.tab).hidden = !active; });
}));
applyLanguage(); refresh(); account.refresh(); agentSlots.refresh();
setInterval(() => { if (!document.hidden) refresh(); }, 2000);
setInterval(() => { if (!document.hidden && account.pending) account.refresh(); }, 2000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) { refresh(); account.refresh(); agentSlots.refresh(); } });
window.addEventListener("focus", () => { if (state.workflow === "solve") agentSlots.refresh(); });
