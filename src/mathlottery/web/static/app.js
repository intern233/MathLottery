"use strict";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const words = {
  en: {
    localLab: "LOCAL RESEARCH LAB", workflows: "WORKFLOWS", find: "Find problems", solve: "Attempt a solution", verify: "Verify a proof",
    sideNote: "One agent. A little curiosity. A result worth checking.", connecting: "Connecting…", connected: "Local workspace connected", disconnected: "Server disconnected",
    workspace: "Research workspace", eyebrow: "MATHEMATICS, WITH A LITTLE CHANCE", heroCopy: "Find a worthwhile question. Give it a serious attempt. Check what holds.",
    accountTitle: "MathLottery account", accountSignIn: "Sign in with ChatGPT", accountRefresh: "Refresh status", accountChecking: "Checking account…", accountConnected: "Signed in to MathLottery", accountSignedOut: "Sign in to MathLottery to use your ChatGPT subscription with Codex.", accountUnavailable: "Codex is unavailable. Install or configure it, then refresh.",
    accountWaiting: "Waiting for you to finish signing in…", accountStarting: "Starting sign-in…", accountCancelling: "Cancelling sign-in…", accountInstructions: "Open the official sign-in page and enter this one-time code.", accountOpen: "Continue at OpenAI ↗", accountCode: "One-time code", accountCopy: "Copy", accountCopied: "Code copied.", accountSelectCode: "Code selected. Copy it with your browser's copy command.", accountCancel: "Cancel sign-in", accountInvalidLink: "No valid official sign-in link was returned. Cancel and try again.", accountReadFailed: "Could not check the Codex account. Refresh to try again.",
    accountSwitch: "Switch account", accountSignOut: "Sign out", accountSwitching: "Signing out and starting a new sign-in…", accountSigningOut: "Signing out…", accountUsingApiKey: "Codex uses an API key. Switch to ChatGPT to use your subscription.",
    accountConfirmSwitch: "Switch the MathLottery account?\n\nThis signs out of this workspace first, then starts a new ChatGPT sign-in. If you cancel or the new sign-in fails, MathLottery stays signed out. Your local Codex CLI / IDE login is unchanged.\n\nContinue?",
    accountConfirmLogout: "Sign out of MathLottery?\n\nThis workspace will need to sign in again. Your local Codex CLI / IDE login is unchanged.\n\nContinue?",
    accountNote: "This workspace has its own login. Switching or signing out leaves your local Codex CLI / IDE login unchanged. You may use the same ChatGPT account; its usage limits still apply across sessions. Chat API requires a separate API key and API billing.", accountApiKey: "API key", accountPlan: "Plan",
    totalRuns: "Research runs", activeRuns: "Running now", savedProblems: "Saved problems", candidates: "Candidate proofs", newAttempt: "NEW ATTEMPT",
    findDescription: "Search public sources, compare promising questions, and keep the evidence for their status.",
    solveDescription: "Give the research agent a precise question and room to explore its own approach.",
    verifyDescription: "Ask a separate reviewer to examine the proof, its assumptions, and its novelty.",
    criteria: "What kind of problem?", criteriaPlaceholder: "For example: a precise combinatorics problem with a short statement and potential for Lean verification.",
    source: "Preferred source · optional", shortlistSize: "Shortlist size", reviewInput: "What would you like to review?", savedCandidate: "Latest candidate from a saved run", pasteProof: "A proof I provide",
    sourceRun: "Run with a candidate", separateReview: "The reviewer starts a separate session with the displayed candidate, its references, and any source files you select.", problem: "Problem", newProblem: "Enter a new problem",
    sourceRefresh: "Refresh source", sourceRefreshHint: "Refresh loads the latest candidate and clears the file selection. Background updates never change the candidate shown here.", sourceLoading: "Loading the candidate and available source files…", sourceChoose: "Select a saved run to load its candidate.", sourceMissing: "This run has no candidate to review.", sourceBusy: "Wait for the source task to finish or stop before reviewing its saved candidate.", sourceBinding: "Candidate to review", sourceFiles: "Attach proof source files · optional", sourceFilesHint: "Select the files needed to reproduce the proof. No files are attached by default. The reviewer must recheck these untrusted inputs; attaching them does not raise the proof level.", sourceFilesEmpty: "No eligible solver source files are available.", sourceLimits: "Up to 20 files, 1,000,000 bytes each and 2,000,000 bytes in total. Chat accepts at most 128,000 bytes in total as inline text.", sourceUnsupported: "Source attachments require native execution.", nativeExecutionRequired: "Browser research requires native execution. Set backend.execution to native in config.yaml, then refresh this page.", sourceTooLarge: "This source file exceeds the per-file limit.", sourceSelectionOver: "The selected source files exceed the count or byte limit. Deselect files before starting.", sourceSelected: "Selected files", sourceBytes: "bytes", sourceCapturedHint: "Files are copied and hashed when the review starts. The captured manifest appears in Results; later source changes do not change that snapshot.", evidenceSnapshot: "Review input snapshot", snapshotCandidate: "Source candidate", snapshotFiles: "Captured source files", snapshotEmpty: "No source files were attached; the review received the candidate text and references.", snapshotNote: "These hashes identify the captured inputs, not their correctness. The reviewer checks the copied files independently.",
    problemTitle: "Title · optional", titlePlaceholder: "Give this research attempt a name", statement: "Problem statement", statementPlaceholder: "State the question, assumptions, and what you would like to prove.",
    proof: "Proof to review", proofPlaceholder: "Paste the complete proof, including assumptions and references.", settings: "Model & budget", configDefault: "defaults from config.yaml",
    instructions: "Task instructions · optional", instructionsPlaceholder: "For example: provide Lean source files, record the compiler command and result, and check boundary cases.", instructionsHint: "Add requirements for this task, such as Lean verification. The original problem statement stays unchanged.",
    backend: "Backend", model: "Model", useConfig: "Use configuration", inherited: "Inherit backend default", effort: "Reasoning effort", chatMode: "Chat reasoning mode",
    timeBudget: "Time budget · minutes", roundBudget: "Maximum rounds", overrideHint: "Overrides apply to this task only. Credentials stay in your environment.",
    codexHint: "Uses this MathLottery workspace's Codex login and tools.", chatHint: "Uses the Chat API and its API billing. An API key must be configured in the server environment.",
    readinessChecking: "Checking the MathLottery account before starting Codex…", readinessSignIn: "Sign in with ChatGPT in the account panel above to start Codex research. Your draft stays here.", readinessPending: "Finish signing in on the official page, then return here. Your draft stays here.", readinessUnavailable: "Codex is unavailable. Install or configure it, then refresh the account status above.", readinessUnknown: "Account status could not be checked. Refresh the account status above before starting Codex.", readinessApiKey: "Use Switch account above to sign in with ChatGPT before starting subscription-backed Codex research.",
    backgroundHint: "Runs in the background. You can close this page and return later.", notebook: "YOUR NOTEBOOK", recentRuns: "Research history",
    startFind: "Start finding", startSolve: "Start solving", startVerify: "Start verification", starting: "Starting…", emptyRuns: "Your next question starts here.", emptyRunsHint: "Start a task to collect problems, proof attempts, and review evidence.",
    rounds: "rounds", tokens: "tokens", elapsed: "active time", unknown: "unknown", stop: "Stop task", stopping: "Stop requested…", resume: "Resume / add direction", verifyLatest: "Verify latest candidate", download: "Download report ↓",
    direction: "Additional direction · optional", directionPlaceholder: "Point out an approach, ask for an edge case, or give the agent a new direction.", newTotalBudget: "New total time budget · minutes", newTotalRounds: "New total round limit",
    resumeHint: "These replace total limits, rather than adding time. The saved model settings are preserved.", continue: "Continue research", results: "Results", activity: "Activity", report: "Report",
    visibleProgress: "Latest visible output", events: "Recent checkpoint events", footer: "Curiosity starts the run. Evidence decides the result.", noCandidates: "No candidate runs yet — solve a problem first, or provide a proof.",
    noResults: "No results have been submitted yet.", waitingResults: "Check Activity for saved checkpoints and visible agent output.", shortlist: "Discovered problems", solveThis: "Solve this problem →", statementDetails: "Statement and sources", sourceEvidence: "Status evidence", selection: "Why this problem", feasibility: "Verification feasibility",
    fullProof: "Read full proof", claim: "Claim", review: "Independent review", novelty: "Novelty", unreviewed: "Awaiting independent review", assessmentLimit: "Task completion, proof evidence, and novelty are separate. A favorable agent review does not establish a new solution to a still-open problem.", proofLevel: "Recorded proof level", latestReview: "Latest agent review", problemStatus: "Recorded problem status", levelCandidate: "A proposed proof awaiting independent checking.", levelSelfChecked: "An agent review found no issues. Full formal verification and expert review have not been established by this level.", levelPartial: "Some evidence has been checked. This level does not establish a complete formal proof of the original statement.", levelFormal: "Recorded as formally verified. Check the verification evidence and its correspondence to the original statement.", levelExpert: "Recorded as expert reviewed. Read the review's evidence and scope.", levelRejected: "The recorded review identified supported issues in this candidate.",
    proofEvidence: "Evidence and references", leanFiles: "Lean files", leanFilesNote: "These are agent-generated source files. Their presence does not establish successful compilation or a complete proof of the original statement.", leanFileTooLarge: "Too large to download here", leanFilesTruncated: "Only part of the file list is shown. The remaining files stay in the local run directory.",
    noProgress: "No visible output has been saved yet. A long native turn can be quiet while tools are running.", truncated: "Preview truncated; the full artifact remains in the local run directory.", noReport: "The report is not available yet.",
    launched: "Task started. Progress is saved locally.", resumed: "Research resumed.", stopSent: "Stop requested. Waiting for the background task to stop; saved progress is preserved.", requestError: "Request failed. Check research history before retrying.",
    workerInterrupted: "The background worker exited without recording completion. Resume to recover the checkpoint.",
    CREATED: "Created", DISCOVERING: "Finding", SELECTING: "Selecting", SOLVING: "Solving", VERIFYING: "Verifying", REPORTING: "Reporting", COMPLETED: "Completed", PAUSED: "Paused", WAITING_FOR_USER: "Manual handoff", RATE_LIMITED: "Rate limited", FAILED: "Failed", CANCELLED: "Stopped",
    OPEN: "Open", SOLVED: "Solved", PARTIALLY_SOLVED: "Partially solved", DISPUTED: "Disputed", UNKNOWN: "Unknown", NO_ISSUES_FOUND: "Agent found no issues", ISSUES_FOUND: "Issues found", INCONCLUSIVE: "Inconclusive", CANDIDATE: "Candidate proof", SELF_CHECKED: "Agent checked", PARTIALLY_VERIFIED: "Partially verified", FORMALLY_VERIFIED: "Formally verified", EXPERT_REVIEWED: "Expert reviewed", REJECTED: "Rejected", KNOWN: "Known result", SPECIAL_CASE: "Special case", POTENTIALLY_NEW: "Potentially new",
  },
  zh: {
    localLab: "本地数学研究工作台", workflows: "研究流程", find: "找题", solve: "求解", verify: "验真",
    sideNote: "一个 agent，一点好奇心，一份值得检验的结果。", connecting: "正在连接…", connected: "已连接本地工作区", disconnected: "服务连接已断开",
    workspace: "数学研究工作台", eyebrow: "从一个问题开始，给发现一次机会", heroCopy: "找一个值得尝试的问题，认真探索，再检查结论是否成立。",
    accountTitle: "MathLottery 账号", accountSignIn: "使用 ChatGPT 账号登录", accountRefresh: "刷新状态", accountChecking: "正在检查账号…", accountConnected: "已登录 MathLottery", accountSignedOut: "登录 MathLottery 后，可通过 Codex 使用你的 ChatGPT 订阅。", accountUnavailable: "Codex 当前不可用，请安装或完成配置后刷新。",
    accountWaiting: "等待你在官方页面完成登录…", accountStarting: "正在启动登录…", accountCancelling: "正在取消登录…", accountInstructions: "打开官方登录页面，输入下面的一次性验证码。", accountOpen: "前往 OpenAI 登录 ↗", accountCode: "一次性验证码", accountCopy: "复制", accountCopied: "验证码已复制。", accountSelectCode: "已选中验证码，请使用浏览器的复制操作。", accountCancel: "取消登录", accountInvalidLink: "未收到有效的官方登录链接，请取消后重试。", accountReadFailed: "无法检查 Codex 账号，请刷新重试。",
    accountSwitch: "切换账号", accountSignOut: "退出登录", accountSwitching: "正在退出当前账号并启动新登录…", accountSigningOut: "正在退出登录…", accountUsingApiKey: "Codex 当前使用 API Key；切换到 ChatGPT 账号后可使用订阅额度。",
    accountConfirmSwitch: "切换 MathLottery 账号？\n\n会先退出当前工作区的登录，再启动新的 ChatGPT 登录。如果取消或新登录失败，MathLottery 将保持退出状态。本地 Codex CLI / IDE 的登录不受影响。\n\n继续切换？",
    accountConfirmLogout: "退出 MathLottery 登录？\n\n当前工作区之后需要重新登录。本地 Codex CLI / IDE 的登录不受影响。\n\n继续退出？",
    accountNote: "当前工作区独立保存登录，切换或退出不影响本地 Codex CLI / IDE。可以使用同一个 ChatGPT 账号，订阅额度仍按账号共用。Chat API 仍需单独的 API Key，使用 API 计费。", accountApiKey: "API Key", accountPlan: "订阅",
    totalRuns: "研究任务", activeRuns: "正在运行", savedProblems: "已存题目", candidates: "候选证明", newAttempt: "开启一次尝试",
    findDescription: "搜索公开来源，比较值得尝试的问题，保留开放状态的证据。", solveDescription: "给研究 agent 一个明确的问题，让它自主选择方法、探索与推导。", verifyDescription: "由独立审查会话检查证明、前提与新颖性，记录依据和疑点。",
    criteria: "想找什么样的问题？", criteriaPlaceholder: "例如：找一个陈述简洁、范围较小、有希望用 Lean 验证的组合数学开放问题。",
    source: "优先检索的来源 · 可选", shortlistSize: "候选题数", reviewInput: "准备检查哪份证明？", savedCandidate: "已有任务的最新候选证明", pasteProof: "粘贴自己的证明",
    sourceRun: "选择含候选证明的任务", separateReview: "审查者使用独立会话，接收下方显示的候选证明、参考资料，以及你选择的源文件。", problem: "数学问题", newProblem: "输入一个新问题",
    sourceRefresh: "刷新来源", sourceRefreshHint: "刷新会加载最新候选并清空文件选择；后台更新不会改变这里显示的候选。", sourceLoading: "正在加载候选证明和可选源文件…", sourceChoose: "选择一个已有任务，加载其候选证明。", sourceMissing: "该任务没有可供审查的候选证明。", sourceBusy: "请等待来源任务结束或停止后，再审查其保存的候选证明。", sourceBinding: "本次审查的候选", sourceFiles: "附带证明源文件 · 可选", sourceFilesHint: "选择复现证明所需的文件，默认不附带任何文件。审查者必须重新检查这些不可信输入；附带文件不会提升证明等级。", sourceFilesEmpty: "没有可选的求解源文件。", sourceLimits: "最多 20 个文件，单个不超过 1,000,000 字节，总计不超过 2,000,000 字节。Chat 以内联文本接收，总计不超过 128,000 字节。", sourceUnsupported: "附带源文件需要 native 执行模式。", nativeExecutionRequired: "前端研究任务需要 native 执行模式。请将 config.yaml 中的 backend.execution 设为 native，然后刷新页面。", sourceTooLarge: "该源文件超过单个文件大小限制。", sourceSelectionOver: "所选源文件超过数量或大小限制，请取消部分选择后再启动。", sourceSelected: "已选文件", sourceBytes: "字节", sourceCapturedHint: "验真启动时复制文件并计算哈希，结果区会展示捕获清单；之后修改源文件不影响这份快照。", evidenceSnapshot: "审查输入快照", snapshotCandidate: "来源候选", snapshotFiles: "已捕获源文件", snapshotEmpty: "未附带源文件，审查者接收的是候选文本和参考资料。", snapshotNote: "哈希用于确认捕获的输入内容，不代表输入正确；审查者需独立检查复制的文件。",
    problemTitle: "题目名称 · 可选", titlePlaceholder: "给这次探索起个名字", statement: "问题陈述", statementPlaceholder: "写下要研究的问题、已知条件，以及希望证明的结论。",
    proof: "待审查的证明", proofPlaceholder: "粘贴完整证明，包含所用假设和参考资料。", settings: "模型与预算", configDefault: "默认读取 config.yaml",
    instructions: "本次任务要求 · 可选", instructionsPlaceholder: "例如：提供 Lean 源文件，记录编译命令及结果，并检查边界情况。", instructionsHint: "可补充 Lean 验证等本次任务要求，原始数学命题保持不变。",
    backend: "调用方式", model: "模型", useConfig: "使用配置文件", inherited: "继承后端默认值", effort: "推理强度", chatMode: "Chat 思考模式",
    timeBudget: "时间预算 · 分钟", roundBudget: "最大轮数", overrideHint: "这里的修改仅影响本次任务。密钥仍从服务环境读取。",
    codexHint: "使用当前 MathLottery 工作区独立的 Codex 登录与工具配置。", chatHint: "使用 Chat API 及其 API 额度，需要在服务环境中配置 API Key。",
    readinessChecking: "正在检查 MathLottery 账号，完成后即可启动 Codex…", readinessSignIn: "请先在上方账号区域使用 ChatGPT 登录，再启动 Codex 研究。已填写的内容会保留。", readinessPending: "请在官方页面完成登录后回到这里，已填写的内容会保留。", readinessUnavailable: "Codex 当前不可用，请安装或完成配置，再刷新上方的账号状态。", readinessUnknown: "暂时无法确认账号状态，请刷新上方的账号状态后再启动 Codex。", readinessApiKey: "请通过上方「切换账号」登录 ChatGPT，再使用订阅额度启动 Codex 研究。",
    backgroundHint: "任务在后台运行，关闭页面后也可以随时回来查看。", notebook: "研究记录", recentRuns: "任务历史",
    startFind: "开始找题", startSolve: "开始求解", startVerify: "开始验真", starting: "正在启动…", emptyRuns: "下一个问题，从这里开始。", emptyRunsHint: "启动一次任务，积累题目、证明尝试和审查证据。",
    rounds: "轮", tokens: "tokens", elapsed: "活动耗时", unknown: "未知", stop: "停止任务", stopping: "正在停止…", resume: "继续 / 补充方向", verifyLatest: "验真最新候选", download: "下载报告 ↓",
    direction: "补充研究方向 · 可选", directionPlaceholder: "提示一种方法、要求检查边界条件，或补充新的研究方向。", newTotalBudget: "新的总时间预算 · 分钟", newTotalRounds: "新的总轮数上限",
    resumeHint: "这里设置的是新的总上限，不是追加额度；沿用该任务保存的模型配置。", continue: "继续研究", results: "结果", activity: "运行动态", report: "报告",
    visibleProgress: "最近的可见输出", events: "最近的检查点事件", footer: "好奇心开启尝试，证据决定结论。", noCandidates: "还没有候选证明，请先求解或选择粘贴证明。",
    noResults: "还没有提交研究结果。", waitingResults: "可以在「运行动态」查看检查点与已保存的 agent 输出。", shortlist: "找到的题目", solveThis: "求解这道题 →", statementDetails: "问题陈述与来源", sourceEvidence: "状态证据", selection: "选题理由", feasibility: "验证可行性",
    fullProof: "阅读完整证明", claim: "结论", review: "独立审查", novelty: "新颖性", unreviewed: "等待独立审查", assessmentLimit: "任务完成、证明证据和新颖性是不同结论。Agent 审查未发现问题，不代表首次解决了一个仍未解决的问题。", proofLevel: "记录的证明等级", latestReview: "最近一次 Agent 审查", problemStatus: "记录的问题状态", levelCandidate: "提出的证明，尚待独立检查。", levelSelfChecked: "Agent 审查未发现问题；这一等级尚未确立完整形式验证或专家认可。", levelPartial: "部分证据已核验，这一等级不代表原始命题已有完整形式证明。", levelFormal: "记录为已形式验证，请检查验证证据与原始命题的对应关系。", levelExpert: "记录为已获专家审查，请查看审查证据与适用范围。", levelRejected: "记录的审查指出了有证据支持的问题。",
    proofEvidence: "证据与参考资料", leanFiles: "Lean 文件", leanFilesNote: "这些是 agent 生成的源文件。文件存在不代表已编译通过，也不代表完整证明了原始命题。", leanFileTooLarge: "文件过大，无法在此下载", leanFilesTruncated: "这里只显示部分文件，其余文件仍保存在本地任务目录中。",
    noProgress: "尚无保存的可见输出。原生 agent 使用工具的长回合中可能暂时没有文字更新。", truncated: "预览已截断，完整内容保留在本地任务目录。", noReport: "报告尚未生成。",
    launched: "任务已启动，进度保存在本地。", resumed: "已继续研究。", stopSent: "已请求停止，正在等待后台任务结束；已有进度会保留。", requestError: "请求失败，请先查看任务历史再重试。",
    workerInterrupted: "后台进程退出时未记录完成状态，可以继续任务以恢复检查点。",
    CREATED: "已创建", DISCOVERING: "找题中", SELECTING: "选题中", SOLVING: "求解中", VERIFYING: "验真中", REPORTING: "生成报告", COMPLETED: "已完成", PAUSED: "已暂停", WAITING_FOR_USER: "等待手动交接", RATE_LIMITED: "额度受限", FAILED: "失败", CANCELLED: "已停止",
    OPEN: "开放", SOLVED: "已解决", PARTIALLY_SOLVED: "部分解决", DISPUTED: "有争议", UNKNOWN: "未知", NO_ISSUES_FOUND: "Agent 未发现问题", ISSUES_FOUND: "发现问题", INCONCLUSIVE: "尚无定论", CANDIDATE: "候选证明", SELF_CHECKED: "Agent 已检查", PARTIALLY_VERIFIED: "部分已验证", FORMALLY_VERIFIED: "已形式验证", EXPERT_REVIEWED: "已获专家审查", REJECTED: "已否定", KNOWN: "已知结果", SPECIAL_CASE: "特殊情形", POTENTIALLY_NEW: "可能是新结果",
  },
};

function preference(key, value) {
  try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch { /* Storage can be disabled. */ }
  return null;
}
const state = { language: preference("mathlottery.language") || (navigator.language.startsWith("zh") ? "zh" : "en"), workflow: "find", settings: null, runs: [], problems: [], csrf: "", selected: preference("mathlottery.run"), detail: null, resultsKey: "", polling: false, submitting: false, resuming: false };
// Account identity and device codes stay in memory, separate from saved UI preferences.
const accountState = { data: null, busy: false, operation: "status", error: "" };
// This form snapshot changes only on an explicit source choice/refresh, never a background poll.
const reviewSource = { generation: 0, runId: "", loading: false, error: "", run: null, candidate: null, files: [], selected: new Set(), filesKey: "" };
if (!words[state.language]) state.language = "en";
const t = (key) => words[state.language][key] || key;
const compact = (value) => value == null ? t("unknown") : new Intl.NumberFormat(state.language, { notation: "compact", maximumFractionDigits: 1 }).format(value);
const date = (value) => new Date(value).toLocaleString(state.language === "zh" ? "zh-CN" : "en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

function node(tag, className, text) { const item = document.createElement(tag); if (className) item.className = className; if (text != null) item.textContent = text; return item; }
function text(selector, value) { const item = $(selector); if (item.textContent !== String(value)) item.textContent = value; }
function notice(selector, value) { text(selector, value || ""); $(selector).hidden = !value; }
function toast(value) { notice("#toast", value); clearTimeout(toast.timer); toast.timer = setTimeout(() => { $("#toast").hidden = true; }, 5000); }
function badge(value) {
  const style = ["COMPLETED", "NO_ISSUES_FOUND"].includes(value) ? "success" : ["FAILED", "ISSUES_FOUND"].includes(value) ? "error" : ["PAUSED", "RATE_LIMITED", "INCONCLUSIVE", "DISPUTED"].includes(value) ? "warning" : ["DISCOVERING", "SOLVING", "VERIFYING", "CREATED"].includes(value) ? "active" : "";
  return node("span", `badge ${style}`, t(value));
}
function options(selector, entries, emptyLabel) {
  const select = $(selector), previous = select.value;
  const all = [["", emptyLabel], ...entries];
  const signature = JSON.stringify(all);
  if (select.dataset.options === signature) return;
  select.replaceChildren(...all.map(([value, label]) => { const option = node("option", "", label); option.value = value; return option; }));
  select.value = all.some(([value]) => value === previous) ? previous : "";
  select.dataset.options = signature;
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
function officialLoginUrl(value) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:" && ["auth.openai.com", "chatgpt.com"].includes(url.hostname) && !url.username && !url.password && !url.port) return url.href;
  } catch { /* Only official HTTPS login URLs are clickable. */ }
  return null;
}
function executionBlock(backend) {
  if (!["codex", "work"].includes(backend)) return "";
  const data = accountState.data;
  if (accountState.busy) return t("readinessChecking");
  if (!data) return t(accountState.error ? "readinessUnknown" : "readinessChecking");
  if (!data.available) return t("readinessUnavailable");
  if (data.authenticated && ["chatgpt", "chatgptAuthTokens"].includes(data.account?.type)) return "";
  if (data.account?.type === "apiKey") return t("readinessApiKey");
  return t(data.login?.status === "pending" ? "readinessPending" : "readinessSignIn");
}
function selectedSourceFiles() { return reviewSource.files.filter((file) => reviewSource.selected.has(file.path)); }
function sourceAttachmentsSupported() { return state.settings?.execution === "native"; }
function reviewSourceBlock() {
  if (state.workflow !== "verify" || $("#verify-mode").value !== "saved") return "";
  if (!$("#from-run").value || reviewSource.runId !== $("#from-run").value) return t("sourceChoose");
  if (reviewSource.loading) return t("sourceLoading");
  if (reviewSource.error) return reviewSource.error;
  if (!reviewSource.candidate) return t("sourceMissing");
  if (reviewSource.run?.busy) return t("sourceBusy");
  const files = selectedSourceFiles();
  if (files.length && !sourceAttachmentsSupported()) return t("sourceUnsupported");
  const backend = $("#backend").value || state.settings?.backend;
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
  if (state.settings?.execution && state.settings.execution !== "native") return t("nativeExecutionRequired");
  return executionBlock($("#backend").value || state.settings?.backend) || reviewSourceBlock();
}
function updateExecutionControls() {
  const block = newTaskBlock();
  $("#start").disabled = state.submitting || !state.csrf || !state.settings || Boolean(block);
  notice("#start-readiness", block);
  // Resume uses the saved run configuration, independently of the new-task form.
  const run = state.detail, resumeBlock = run ? executionBlock(run.settings.backend || run.mode) : "";
  $("#resume-submit").disabled = state.resuming || !run || run.busy || !state.csrf || Boolean(resumeBlock);
  notice("#resume-readiness", resumeBlock);
}
function renderAccount() {
  const data = accountState.data, connected = Boolean(data?.available && (data.authenticated || data.account)), pending = data?.available && data.login?.status === "pending" && !connected;
  let status = !data ? "accountChecking" : !data.available ? "accountUnavailable" : connected ? data.account?.type === "apiKey" ? "accountUsingApiKey" : "accountConnected" : pending ? "accountWaiting" : "accountSignedOut";
  if (accountState.busy && accountState.operation !== "status") status = ({ login: "accountStarting", cancel: "accountCancelling", switch: "accountSwitching", logout: "accountSigningOut" })[accountState.operation];
  else if (!data && accountState.error) status = "accountReadFailed";
  text("#account-status", t(status));
  const account = connected ? data.account : null;
  const details = account ? [["chatgpt", "chatgptAuthTokens"].includes(account.type) ? "ChatGPT" : account.type === "apiKey" ? t("accountApiKey") : account.type, account.email, account.plan_type ? `${t("accountPlan")}: ${account.plan_type}` : null].filter(Boolean).join(" · ") : "";
  text("#account-details", details); $("#account-details").hidden = !details;
  $("#account-login").hidden = Boolean(connected || pending);
  $("#account-login").disabled = accountState.busy || !data?.available || !state.csrf;
  ["#account-switch", "#account-logout"].forEach((selector) => {
    $(selector).hidden = !connected;
    $(selector).disabled = accountState.busy || !state.csrf;
  });
  $("#account-refresh").disabled = accountState.busy;
  $("#account-panel").setAttribute("aria-busy", accountState.busy);
  const url = pending ? officialLoginUrl(data.login.url) : null;
  const code = pending && typeof data.login.user_code === "string" ? data.login.user_code.slice(0, 64) : "";
  $("#account-pending").hidden = !pending;
  text("#account-code", url ? code : "");
  $("#account-copy").disabled = !url || !code;
  $("#account-cancel").disabled = accountState.busy || !state.csrf;
  const link = $("#account-link");
  if (url) link.href = url;
  else link.removeAttribute("href");
  link.hidden = !url;
  notice("#account-error", accountState.error || data?.error || (pending && (!url || !code) ? t("accountInvalidLink") : ""));
  updateExecutionControls();
}
async function refreshAccount(operation = "status") {
  if (accountState.busy) return;
  const accountChange = ["switch", "logout"].includes(operation);
  if (accountChange && !window.confirm(t(operation === "switch" ? "accountConfirmSwitch" : "accountConfirmLogout"))) return;
  accountState.busy = true; accountState.operation = operation; accountState.error = ""; renderAccount();
  try { accountState.data = await api(operation === "status" ? "/api/account" : `/api/account/${operation}`, operation === "status" ? undefined : accountChange ? { confirm_account_change: true } : {}); }
  catch (error) {
    accountState.error = error.message;
    accountState.data = null;
    // A failed mutation may still have signed out. Re-read without hiding its error.
    if (operation !== "status") {
      try { accountState.data = await api("/api/account"); }
      catch { /* Unknown state must not look like the previous connected account. */ }
    }
  }
  finally { accountState.busy = false; renderAccount(); }
}
function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  $$('[data-i18n]').forEach((item) => { item.textContent = t(item.dataset.i18n); });
  $$('[data-placeholder]').forEach((item) => { item.placeholder = t(item.dataset.placeholder); });
  text("#language", state.language === "zh" ? "English" : "中文");
  state.resultsKey = "";
  renderOverview(); updateForm(); renderAccount();
  if (state.detail) renderDetail(state.detail);
}
function setWorkflow(workflow, scroll = false) {
  state.workflow = workflow;
  notice("#form-error", ""); updateForm();
  if (scroll) { $("#composer").scrollIntoView({ behavior: "smooth", block: "start" }); $(workflow === "find" ? "#query" : workflow === "verify" ? "#verify-mode" : "#problem-id").focus({ preventScroll: true }); }
}
function updateForm() {
  const flow = state.workflow, savedReview = flow === "verify" && $("#verify-mode").value === "saved";
  $$("[data-workflow]").forEach((button) => { const active = button.dataset.workflow === flow; button.classList.toggle("selected", active); button.setAttribute("aria-pressed", active); });
  text("#form-title", t(flow)); text("#form-description", t(`${flow}Description`)); text("#form-number", { find: "01", solve: "02", verify: "03" }[flow]);
  text("#start-label", state.submitting ? t("starting") : t({ find: "startFind", solve: "startSolve", verify: "startVerify" }[flow]));
  $("#find-fields").hidden = flow !== "find"; $("#verify-fields").hidden = flow !== "verify";
  $("#saved-review").hidden = !savedReview; $("#problem-fields").hidden = flow === "find" || savedReview;
  $("#proof-fields").hidden = flow !== "verify" || savedReview;
  $("#new-problem").hidden = Boolean($("#problem-id").value);
  const problem = state.problems.find((item) => item.id === $("#problem-id").value);
  $("#selected-problem").hidden = !problem; text("#selected-problem", problem?.statement || "");
  $$("#task-form input, #task-form textarea, #task-form select").forEach((input) => { if (!input.closest("#source-file-list")) input.disabled = Boolean(input.closest("[hidden]")); });
  const backend = $("#backend").value || state.settings?.backend;
  $("#reasoning-mode").disabled = backend !== "chat";
  text("#backend-hint", t(backend === "chat" ? "chatHint" : "codexHint"));
  renderReviewSource();
  updateExecutionControls();
}
function renderOverview() {
  text("#count-runs", state.runs.length); text("#count-active", state.runs.filter((run) => run.busy).length);
  text("#count-problems", state.problems.length); text("#count-candidates", state.runs.reduce((sum, run) => sum + run.candidate_count, 0));
  if (state.settings) {
    text("#model-chip", `${state.settings.backend} · ${state.settings.model || t("inherited")}`);
    for (const [id, value] of [["model", state.settings.model], ["effort", state.settings.reasoning_effort], ["budget", state.settings.budget_minutes], ["iterations", state.settings.max_iterations]]) $("#" + id).placeholder = value ?? t("inherited");
  }
  options("#problem-id", state.problems.map((problem) => [problem.id, problem.title]), t("newProblem"));
  options("#from-run", state.runs.filter((run) => run.candidate_count).map((run) => [run.id, `${run.title} · ${run.id.slice(-6)}`]), t(state.runs.some((run) => run.candidate_count) ? "sourceRun" : "noCandidates"));
  const list = $("#run-list");
  list.replaceChildren();
  if (!state.runs.length) { const empty = node("div", "empty"); empty.append(node("div", "empty-symbol", "∅"), node("p", "", t("emptyRuns")), node("p", "", t("emptyRunsHint"))); list.append(empty); }
  for (const run of state.runs) {
    const button = node("button", `run-item${run.id === state.selected ? " active" : ""}`); button.type = "button"; button.dataset.runId = run.id;
    const top = node("div", "run-top"); top.append(node("span", "", `${run.workflow.toUpperCase()} · ${run.mode}`), badge(run.state));
    const bottom = node("div", "run-bottom"); bottom.append(node("span", "", date(run.created_at)), node("span", "", `${run.iteration} ${t("rounds")} · ${compact(run.usage.input_tokens)} in`));
    button.append(top, node("span", "run-title", run.title), bottom); button.addEventListener("click", () => selectRun(run.id, true)); list.append(button);
  }
}
function renderProblem(problem, selectable = true) {
  const card = node("article", "problem-card"), heading = node("div", "card-heading");
  heading.append(node("h3", "", problem.title), badge(problem.status)); card.append(heading);
  if (problem.selection_reason) card.append(node("p", "", `${t("selection")}: ${problem.selection_reason}`));
  const details = node("details"), summary = node("summary", "", t("statementDetails")); details.append(summary, node("pre", "", problem.statement));
  if (problem.source_url) { const p = node("p"); p.append(safeLink(problem.source_url)); details.append(p); }
  if (problem.verification_feasibility && problem.verification_feasibility !== "unknown") details.append(node("p", "", `${t("feasibility")}: ${problem.verification_feasibility}`));
  if (problem.status_evidence.length) { details.append(node("h3", "", t("sourceEvidence"))); const list = node("ul"); for (const item of problem.status_evidence) { const li = node("li"); li.append(safeLink(item)); list.append(li); } details.append(list); }
  for (const reference of problem.references) { const p = node("p"); p.append(safeLink(reference.url, reference.title || reference.url)); details.append(p); }
  card.append(details);
  if (selectable) { const button = node("button", "secondary", t("solveThis")); button.type = "button"; button.addEventListener("click", () => { $("#problem-id").value = problem.id; if (!$("#problem-id").value) { $("#title").value = problem.title; $("#statement").value = problem.statement; } setWorkflow("solve", true); }); card.append(button); }
  return card;
}
function candidateAssessment(candidate, problem) {
  const summary = node("dl", "assessment-summary"), latest = candidate.reviews.at(-1);
  for (const [label, value] of [["proofLevel", candidate.level], ["latestReview", latest?.verdict || "unreviewed"], ["problemStatus", problem?.status || "UNKNOWN"], ["novelty", latest?.novelty || "UNKNOWN"]]) {
    const item = node("div"); item.dataset.assessment = label;
    item.append(node("dt", "", t(label)), node("dd", "", t(value))); summary.append(item);
  }
  return summary;
}
function renderReviewEvidence(manifest) {
  const section = node("section", "review-evidence");
  section.append(node("h3", "", t("evidenceSnapshot")), node("p", "field-hint", t("snapshotNote")));
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
function renderResults(run) {
  const key = JSON.stringify([state.language, run.id, run.problem, run.shortlist, run.candidates, run.formal_artifacts, run.review_evidence]);
  if (state.resultsKey === key) return;
  state.resultsKey = key;
  const open = new Set($$("#results details[open]").map((item) => item.dataset.key).filter(Boolean));
  const results = $("#results"); results.replaceChildren();
  if (run.shortlist.length) { results.append(node("h3", "", t("shortlist"))); for (const problem of run.shortlist) results.append(renderProblem(problem)); }
  else if (run.problem) results.append(renderProblem(run.problem, false));
  if (!run.shortlist.length && !run.candidates.length) { const empty = node("div", "empty"); empty.append(node("p", "", t("noResults")), node("p", "", t("waitingResults"))); results.append(empty); }
  if (run.review_evidence) results.append(renderReviewEvidence(run.review_evidence));
  if (run.candidates.length) results.append(node("p", "field-hint", t("assessmentLimit")));
  for (const candidate of [...run.candidates].reverse()) {
    const card = node("article", "candidate-card"), heading = node("div", "card-heading"); heading.append(node("h3", "", candidate.id), badge(candidate.level)); card.append(heading, candidateAssessment(candidate, run.problem));
    const levelNote = { CANDIDATE: "levelCandidate", SELF_CHECKED: "levelSelfChecked", PARTIALLY_VERIFIED: "levelPartial", FORMALLY_VERIFIED: "levelFormal", EXPERT_REVIEWED: "levelExpert", REJECTED: "levelRejected" }[candidate.level];
    if (levelNote) card.append(node("p", "proof-level-note", t(levelNote)));
    card.append(node("p", "", candidate.claim));
    const details = node("details"); details.dataset.key = candidate.id; details.open = open.has(candidate.id); details.append(node("summary", "", t("fullProof")), node("pre", "", candidate.proof)); card.append(details);
    if (candidate.assumptions.length) card.append(node("p", "", candidate.assumptions.join("\n")));
    const evidence = Array.isArray(candidate.evidence) ? candidate.evidence.filter((item) => typeof item === "string") : [];
    const references = Array.isArray(candidate.references) ? candidate.references : [];
    if (evidence.length || references.length) {
      card.append(node("h4", "", t("proofEvidence")));
      for (const item of evidence) { const p = node("p"); p.append(safeLink(item)); card.append(p); }
      for (const reference of references) {
        const url = typeof reference === "string" ? reference : reference?.url || reference?.artifact || "";
        const title = typeof reference === "string" ? reference : reference?.title || url;
        if (typeof url === "string" && typeof title === "string" && (url || title)) {
          const p = node("p"), referenceLink = safeLink(url, title);
          p.append(referenceLink);
          if (referenceLink.tagName !== "A" && url && title !== url) p.append(document.createTextNode(` (${url})`));
          card.append(p);
        }
      }
    }
    for (const review of candidate.reviews) {
      const section = node("div", "review"), row = node("div", "card-heading"); row.append(node("h3", "", t("review")), badge(review.verdict)); section.append(row, node("p", "", review.truth_assessment), node("p", "", review.proof_assessment));
      if (review.issues.length) { const list = node("ul"); for (const issue of review.issues) list.append(node("li", "", issue)); section.append(list); }
      section.append(node("p", "", `${t("novelty")}: ${t(review.novelty)}\n${review.novelty_notes}`));
      for (const evidence of review.evidence) { const p = node("p"); p.append(safeLink(evidence)); section.append(p); }
      card.append(section);
    }
    if (!candidate.reviews.length) card.append(node("p", "field-hint", t("unreviewed")));
    results.append(card);
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
}
function renderDetail(run) {
  $("#run-detail").hidden = false;
  text("#detail-id", `${run.workflow.toUpperCase()} / ${run.id}`); text("#detail-title", run.title);
  const status = badge(run.state); $("#detail-state").className = status.className; text("#detail-state", status.textContent);
  $("#run-facts").replaceChildren(...[`${run.mode} · ${run.settings.model || t("inherited")}`, `${run.iteration} ${t("rounds")}`, `${Math.round(run.elapsed_seconds / 60 * 10) / 10} min ${t("elapsed")}`, `${compact(run.usage.input_tokens)} in / ${compact(run.usage.output_tokens)} out ${t("tokens")}`].map((fact) => node("span", "", fact)));
  const interrupted = !run.busy && ["queued", "running"].includes(run.worker?.state);
  const message = [run.last_error, run.worker?.error, interrupted ? t("workerInterrupted") : null, run.stop_reason, run.metrics.usage_warning].filter(Boolean).join("\n"); notice("#run-message", message);
  $("#run-message").classList.toggle("error", Boolean(run.last_error || run.worker?.error));
  $("#stop").hidden = !run.busy; $("#stop").disabled = run.stop_requested; text("#stop", t(run.stop_requested ? "stopping" : "stop"));
  $("#show-resume").hidden = run.busy || run.mode === "manual";
  updateExecutionControls();
  $("#verify-latest").hidden = !run.candidates.length;
  $("#download").href = `/api/runs/${run.id}/report`;
  renderResults(run);
  text("#progress", run.progress.text || t("noProgress")); text("#progress-note", run.progress.truncated ? t("truncated") : "");
  text("#report-text", run.report.text || t("noReport")); text("#report-note", run.report.truncated ? t("truncated") : "");
  const eventList = $("#event-list"); eventList.replaceChildren();
  for (const event of run.events) { const row = node("div", "event"); const time = node("time", "", date(event.time)); row.append(time, node("span", "", `${event.phase} · ${event.event}${event.error ? ` · ${event.error}` : ""}`)); eventList.append(row); }
}
async function selectRun(id, scroll = false) {
  state.selected = id; preference("mathlottery.run", id); state.resultsKey = ""; $("#resume-form").hidden = true;
  try {
    const run = await api(`/api/runs/${id}`);
    if (state.selected !== id) return;
    state.detail = run; renderOverview(); renderDetail(run);
    $("#resume-budget").value = ""; $("#resume-rounds").value = ""; $("#direction").value = "";
    $("#resume-budget").placeholder = run.settings.budget_minutes; $("#resume-rounds").placeholder = run.settings.max_iterations;
    if (scroll) $("#run-detail").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { notice("#global-error", error.message); }
}
async function refresh() {
  if (state.polling) return;
  state.polling = true;
  const selectedAtStart = state.selected;
  try {
    const data = await api("/api/bootstrap"); state.csrf = data.csrf_token; state.settings = data.settings; state.runs = data.runs; state.problems = data.problems;
    text("#connection", t("connected")); notice("#global-error", data.config_error); renderOverview(); updateForm(); renderAccount();
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
  const values = {};
  for (const [id, key] of [["backend", "backend"], ["model", "model"], ["effort", "reasoning_effort"], ["reasoning-mode", "reasoning_mode"], ["budget", "budget_minutes"], ["iterations", "max_iterations"]]) {
    const input = $("#" + id), value = input.value.trim();
    if (value && !input.disabled) values[key] = ["budget", "iterations"].includes(id) ? Number(value) : value;
  }
  return values;
}
$$("[data-workflow]").forEach((button) => button.addEventListener("click", () => setWorkflow(button.dataset.workflow, button.classList.contains("nav-item"))));
for (const selector of ["#verify-mode", "#problem-id", "#backend"]) $(selector).addEventListener("change", updateForm);
$("#from-run").addEventListener("change", loadReviewSource);
$("#source-refresh").addEventListener("click", loadReviewSource);
$("#language").addEventListener("click", () => { state.language = state.language === "en" ? "zh" : "en"; preference("mathlottery.language", state.language); applyLanguage(); text("#connection", t(state.csrf ? "connected" : "connecting")); });
$("#refresh").addEventListener("click", refresh);
$("#account-login").addEventListener("click", () => refreshAccount("login"));
$("#account-switch").addEventListener("click", () => refreshAccount("switch"));
$("#account-logout").addEventListener("click", () => refreshAccount("logout"));
$("#account-refresh").addEventListener("click", () => refreshAccount());
$("#account-cancel").addEventListener("click", () => refreshAccount("cancel"));
$("#account-copy").addEventListener("click", async () => {
  const value = $("#account-code").textContent;
  if (!value) return;
  try { await navigator.clipboard.writeText(value); toast(t("accountCopied")); }
  catch { const range = document.createRange(); range.selectNodeContents($("#account-code")); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); toast(t("accountSelectCode")); }
});
$("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault(); if (state.submitting) return;
  const block = newTaskBlock();
  if (block || !state.csrf || !state.settings) { updateExecutionControls(); return; }
  const body = { workflow: state.workflow, options: overrides() };
  if ($("#instructions").value.trim()) body.instructions = $("#instructions").value.trim();
  if (state.workflow === "find") { body.count = Number($("#count").value); if ($("#query").value.trim()) body.query = $("#query").value.trim(); if ($("#source").value.trim()) body.source = $("#source").value.trim(); }
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
  }
  state.submitting = true; updateForm(); notice("#form-error", "");
  try { const run = await api("/api/runs", body); await refresh(); await selectRun(run.id, true); toast(t("launched")); }
  catch (error) { notice("#form-error", error.message); await refreshAccount(); }
  finally { state.submitting = false; updateForm(); }
});
$("#stop").addEventListener("click", async () => {
  $("#stop").disabled = true;
  try { await api(`/api/runs/${state.selected}/stop`, {}); toast(t("stopSent")); await refresh(); }
  catch (error) { notice("#run-message", error.message); $("#stop").disabled = false; }
});
$("#show-resume").addEventListener("click", () => { $("#resume-form").hidden = !$("#resume-form").hidden; if (!$("#resume-form").hidden) $("#direction").focus(); });
$("#resume-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const body = {};
  const run = state.detail;
  if (state.resuming || !run || run.busy || !state.csrf || executionBlock(run.settings.backend || run.mode)) { updateExecutionControls(); return; }
  if ($("#direction").value.trim()) body.message = $("#direction").value.trim();
  if ($("#resume-budget").value) body.budget_minutes = Number($("#resume-budget").value);
  if ($("#resume-rounds").value) body.max_iterations = Number($("#resume-rounds").value);
  state.resuming = true; updateExecutionControls();
  try { await api(`/api/runs/${state.selected}/resume`, body); $("#resume-form").hidden = true; toast(t("resumed")); await refresh(); }
  catch (error) { notice("#run-message", error.message); await refreshAccount(); }
  finally { state.resuming = false; updateExecutionControls(); }
});
$("#verify-latest").addEventListener("click", () => { $("#verify-mode").value = "saved"; $("#from-run").value = state.selected; setWorkflow("verify", true); loadReviewSource(); });
$$("[data-tab]").forEach((button) => button.addEventListener("click", () => {
  $$("[data-tab]").forEach((item) => { const active = item === button; item.classList.toggle("selected", active); item.setAttribute("aria-selected", active); $("#" + item.dataset.tab).hidden = !active; });
}));
applyLanguage(); refresh(); refreshAccount();
setInterval(() => { if (!document.hidden) refresh(); }, 2000);
setInterval(() => { if (!document.hidden && accountState.data?.login?.status === "pending") refreshAccount(); }, 2000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) { refresh(); refreshAccount(); } });
