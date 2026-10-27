"use strict";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const words = {
  en: {
    chooseStep: "Find → Choose → Solve", chooseHint: "Compare the shortlist and choose a problem. Find does not start solving automatically.", estimateHint: "Difficulty and Lean feasibility are reasoned estimates, not success probabilities. Check source evidence before treating a problem as open.",
    findCriteria: "Original search preferences",
    searchLimitations: "Search coverage limits (reported)",
    yourChoice: "Your choice", chooseProblem: "Choose this problem", chosen: "Selected", recommended: "Agent recommendation", clearChoice: "Clear choice", discoveryCarry: "The Find dossier, notes and sources will accompany this problem. Review your choice, then start solving.",
    difficulty: "Difficulty", leanFeasibility: "Lean feasibility", prerequisites: "Prerequisites", obstacles: "Main obstacles", initialApproach: "Possible first approach", findNotReady: "Wait for Find to finish before choosing.",
    discoveryOrigin: "Selected from Find", contextFiles: "Research files carried forward", contextOmitted: "Files not carried forward", contextScope: "A frozen research dossier in a new Solve session. This does not transfer hidden reasoning or certify the findings.",
    specialistAgents: "Specialist agents", researchMemories: "Research memories", nativeInherit: "Inherit isolated Codex settings", enabled: "Enabled", disabled: "Disabled", capabilitiesHint: "Codex settings apply within MathLottery's separate account. Review sessions always disable memories. Extra agents share the research budget and can use more tokens.",

    localLab: "LOCAL RESEARCH LAB", workflows: "WORKFLOWS", find: "Find problems", solve: "Attempt a solution", verify: "Verify a proof",
    sideNote: "One agent. A little curiosity. A result worth checking.", connecting: "Connecting…", connected: "Local workspace connected", disconnected: "Server disconnected",
    workspace: "Research workspace", eyebrow: "MATHEMATICS, WITH A LITTLE CHANCE", heroCopy: "Find a worthwhile question. Give it a serious attempt. Check what holds.",
    accountTitle: "MathLottery account", accountSignIn: "Sign in with ChatGPT", accountRefresh: "Refresh status", accountChecking: "Checking account…", accountConnected: "Signed in to MathLottery", accountSignedOut: "Sign in to MathLottery to use your ChatGPT subscription with Codex.", accountUnavailable: "Codex is unavailable. Install or configure it, then refresh.",
    accountCliMissing: "No working Codex CLI was found. Install the official CLI in the environment running MathLottery, then restart MathLottery from that environment and refresh.", accountCliBroken: "The installed Codex CLI could not run. Repair its installation in the environment running MathLottery, then refresh.", accountCliPlatform: "The Codex npm launcher is missing its platform package. Install the official CLI in the environment running MathLottery. In WSL, install the Linux CLI inside WSL, then refresh the account status.",
    accountTimeout: "Codex account request timed out; sign-in status could not be confirmed. Check the server's network/proxy settings, or configure .mathlottery/network.json, then restart and refresh. A timeout does not by itself mean the account was signed out.", accountNetworkInvalid: "Invalid local network settings. Check .mathlottery/network.json, then restart the server and refresh.",
    accountWaiting: "Waiting for you to finish signing in…", accountStarting: "Starting sign-in…", accountCancelling: "Cancelling sign-in…", accountInstructions: "Open the official sign-in page and enter this one-time code.", accountOpen: "Continue at OpenAI ↗", accountCode: "One-time code", accountCopy: "Copy", accountCopied: "Code copied.", accountSelectCode: "Code selected. Copy it with your browser's copy command.", accountCancel: "Cancel sign-in", accountInvalidLink: "No valid official sign-in link was returned. Cancel and try again.", accountReadFailed: "Could not check the Codex account. Refresh to try again.",
    accountSwitch: "Switch account", accountSignOut: "Sign out", accountSwitching: "Signing out and starting a new sign-in…", accountSigningOut: "Signing out…", accountUsingApiKey: "Codex uses an API key. Switch to ChatGPT to use your subscription.",
    accountConfirmSwitch: "Switch the MathLottery account?\n\nThis signs out of this workspace first, then starts a new ChatGPT sign-in. If you cancel or the new sign-in fails, MathLottery stays signed out. Your local Codex CLI / IDE login is unchanged.\n\nContinue?",
    accountConfirmLogout: "Sign out of MathLottery?\n\nThis workspace will need to sign in again. Your local Codex CLI / IDE login is unchanged.\n\nContinue?",
    accountNote: "This workspace has its own login. Switching or signing out leaves your local Codex CLI / IDE login unchanged. You may use the same ChatGPT account; its usage limits still apply across sessions. Chat API requires a separate API key and API billing.", accountApiKey: "API key", accountPlan: "Plan",
    totalRuns: "Run records", activeRuns: "Running now", savedProblems: "Saved problems", candidates: "Candidate proofs", newAttempt: "NEW ATTEMPT",
    findDescription: "Search public sources, compare promising questions, and keep the evidence for their status.",
    solveDescription: "Give the research agent a precise question and room to explore its own approach.",
    verifyDescription: "Ask a separate reviewer to examine the proof, its assumptions, and its novelty.",
    criteria: "What kind of problem?", criteriaPlaceholder: "For example: a precise combinatorics problem with a short statement and potential for Lean verification.",
    source: "Preferred source · optional", shortlistSize: "Shortlist size", reviewInput: "What would you like to review?", savedCandidate: "Latest candidate from a saved run", pasteProof: "A proof I provide",
    sourceRun: "Run with a candidate", separateReview: "The reviewer starts a separate session with the displayed candidate, its references, and any source files you select.", problem: "Problem", newProblem: "Enter a new problem",
    sourceRefresh: "Refresh source", sourceRefreshHint: "Refresh loads the latest candidate and clears the file selection. Background updates never change the candidate shown here.", sourceLoading: "Loading the candidate and available source files…", sourceChoose: "Select a saved run to load its candidate.", sourceMissing: "This run has no candidate to review.", sourceBusy: "Wait for the source task to finish or stop before reviewing its saved candidate.", sourceBinding: "Candidate to review", sourceFiles: "Attach proof source files · optional", sourceFilesHint: "Select the files needed to reproduce the proof. Save accompanying text, JSON/CSV certificates and Python scripts under proof/ or formal/. No files are attached by default. The reviewer must recheck these untrusted inputs; attaching them does not raise the proof level.", sourceFilesEmpty: "No eligible solver source files are available.", sourceLimits: "Up to 20 files, 1,000,000 bytes each and 2,000,000 bytes in total. Chat accepts at most 128,000 bytes in total as inline text.", sourceUnsupported: "Source attachments require native execution.", nativeExecutionRequired: "Browser research requires native execution. Set backend.execution to native in config.yaml, then refresh this page.", sourceTooLarge: "This source file exceeds the per-file limit.", sourceSelectionOver: "The selected source files exceed the count or byte limit. Deselect files before starting.", sourceSelected: "Selected files", sourceBytes: "bytes", sourceCapturedHint: "Files are copied and hashed when the review starts. The captured manifest appears in Results; later source changes do not change that snapshot.", evidenceSnapshot: "Review input snapshot", snapshotCandidate: "Source candidate", snapshotFiles: "Captured source files", snapshotEmpty: "No source files were attached; the review received the candidate text and references.", snapshotNote: "These hashes identify the captured inputs, not their correctness. The reviewer checks the copied files independently.",
    problemTitle: "Title · optional", titlePlaceholder: "Give this research attempt a name", statement: "Problem statement", statementPlaceholder: "State the question, assumptions, and what you would like to prove.",
    proof: "Proof to review", proofPlaceholder: "Paste the complete proof, including assumptions and references.", settings: "Model & budget", configDefault: "defaults from config.yaml",
    instructions: "Task instructions · optional", instructionsPlaceholder: "For example: provide Lean source files, record the compiler command and result, and check boundary cases.", instructionsHint: "Add requirements for this task, such as Lean verification. The original problem statement stays unchanged.",
    backend: "Backend", model: "Model", useConfig: "Use configuration", inherited: "Inherit backend default", effort: "Reasoning effort", chatMode: "Chat reasoning mode",
    timeBudget: "Time budget · minutes", roundBudget: "Maximum rounds", overrideHint: "Overrides apply to this task only. Credentials stay in your environment.",
    fullSolveBudget: "Use full Solve time budget", fullSolveBudgetHint: "Continue research and self-checking until the total time limit, even after a complete claim. Other limits, errors or your stop request can still interrupt work. This does not replace Verify or guarantee a solution.",
    codexHint: "Uses this MathLottery workspace's Codex login and tools.", chatHint: "Uses the Chat API and its API billing. An API key must be configured in the server environment.",
    readinessChecking: "Checking the MathLottery account before starting Codex…", readinessSignIn: "Sign in with ChatGPT in the account panel above to start Codex research. Your draft stays here.", readinessPending: "Finish signing in on the official page, then return here. Your draft stays here.", readinessUnavailable: "Codex is unavailable. Install or configure it, then refresh the account status above.", readinessUnknown: "Account status could not be checked. Refresh the account status above before starting Codex.", readinessApiKey: "Use Switch account above to sign in with ChatGPT before starting subscription-backed Codex research.",
    backgroundHint: "Runs in the background. You can close this page and return later.", notebook: "YOUR NOTEBOOK", recentRuns: "Research history",
    historyHint: "Each Find keeps its shortlist. Solve and Verify are grouped by problem; repeated runs are numbered. Agent turns include continuations.",
    stageFind: "Find", stageSolve: "Solve", stageVerify: "Verify", stagePipeline: "Full workflow", runRecords: "run records", lastUpdated: "Updated", startedAt: "Started", attempt: "Attempt {n}",
    startFind: "Start finding", startSolve: "Start solving", startVerify: "Start verification", starting: "Starting…", emptyRuns: "Your next question starts here.", emptyRunsHint: "Start a task to collect problems, proof attempts, and review evidence.",
    rounds: "agent turns", tokens: "tokens", elapsed: "active time", unknown: "unknown", stop: "Stop task", stopping: "Stop requested…", resume: "Resume / add direction", verifyLatest: "Verify latest candidate", download: "Download report ↓",
    direction: "Additional direction · optional", directionPlaceholder: "Point out an approach, ask for an edge case, or give the agent a new direction.", newTotalBudget: "New total time budget · minutes", newTotalRounds: "New total round limit",
    resumeHint: "These replace total limits, rather than adding time. The saved model settings are preserved.", continue: "Continue research", results: "Results", activity: "Activity", report: "Report",
    leanLimits: "Independent Lean check resources", leanLimitsHint: "Optional limits for this task’s independent checker. Blank fields keep the saved limits. The Lean threshold is not measured RAM usage.", leanMemory: "Lean memory threshold · MB", leanAddress: "Virtual address-space limit · MB", leanTimeout: "Total formal check timeout · seconds",
    visibleProgress: "Latest visible output", checkingEvidence: "Research output is saved; independent evidence checks are not yet complete.", events: "Recent checkpoint events", footer: "Curiosity starts the run. Evidence decides the result.", noCandidates: "No candidate runs yet — solve a problem first, or provide a proof.",
    noResults: "No results have been submitted yet.", waitingResults: "Check Activity for saved checkpoints and visible agent output.", shortlist: "Discovered problems", solveThis: "Solve this problem →", statementDetails: "Statement and sources", sourceEvidence: "Status evidence", selection: "Why this problem", feasibility: "Verification feasibility",
    fullProof: "Read full proof", claim: "Claim", review: "Independent review", novelty: "Novelty", unreviewed: "Awaiting independent review", assessmentLimit: "Task completion, proof evidence, and novelty are separate. A favorable agent review does not establish a new solution to a still-open problem.", proofLevel: "Recorded proof level", latestReview: "Latest agent review", problemStatus: "Recorded problem status", levelCandidate: "A proposed proof awaiting independent checking.", levelSelfChecked: "An agent review found no issues. Full formal verification and expert review have not been established by this level.", levelPartial: "Some evidence has been checked. This level does not establish a complete formal proof of the original statement.", levelFormal: "Recorded as formally verified. Check the verification evidence and its correspondence to the original statement.", levelExpert: "Recorded as expert reviewed. Read the review's evidence and scope.", levelRejected: "The recorded review identified supported issues in this candidate.",
    proofEvidence: "Evidence and references", leanFiles: "Proof files", leanFilesNote: "These are agent-generated source files. Their presence does not establish successful compilation or a complete proof of the original statement.", leanFileTooLarge: "Too large to download here", leanFilesTruncated: "Only part of the file list is shown. The remaining files stay in the local run directory.",
    declaredScope: "Researcher's scope", originalCoverage: "Reviewer: original problem coverage", obligations: "Remaining proof obligations", evidenceGaps: "Evidence checks and gaps", notAssessed: "Not assessed under the evidence policy", excerptMatched: "Source excerpt matched", excerptMissing: "Source excerpt not verified", searchObserved: "Observed searches", proofChecks: "Explicit proof checks", formalReceipt: "Independent Lean execution receipt", formalScope: "Checks named declarations only; equivalence to the original problem is not certified.", evidenceGate: "Evidence gate", sourceLimit: "Matching source text does not certify its interpretation or search completeness.",
    COMPLETE: "Declared complete", COUNTEREXAMPLE: "Counterexample", FULL: "Full coverage reported", PARTIAL: "Partial result", DIFFERENT: "Different statement", KERNEL_REPLAYED: "Kernel replay passed", UNAVAILABLE: "Unavailable", ERROR: "Execution error", TIMEOUT: "Time limit", OUTPUT_LIMIT: "Output limit", SUPPORTED: "Supported", CONTRADICTED: "Contradicted", UNRESOLVED: "Unresolved",
    noProgress: "No visible output has been saved yet. A long native turn can be quiet while tools are running.", truncated: "Preview truncated; the full artifact remains in the local run directory.", noReport: "The report is not available yet.",
    launched: "Task started. Progress is saved locally.", resumed: "Research resumed.", stopSent: "Stop requested. Waiting for the background task to stop; saved progress is preserved.", requestError: "Request failed. Check research history before retrying.",
    workerInterrupted: "The background worker exited without recording completion. Resume to recover the checkpoint.",
    CREATED: "Created", DISCOVERING: "Finding", SELECTING: "Selecting", SOLVING: "Solving", VERIFYING: "Verifying", REPORTING: "Reporting", COMPLETED: "Completed", PAUSED: "Paused", WAITING_FOR_USER: "Manual handoff", RATE_LIMITED: "Rate limited", FAILED: "Failed", CANCELLED: "Stopped",
    OPEN: "Open", SOLVED: "Solved", PARTIALLY_SOLVED: "Partially solved", DISPUTED: "Disputed", UNKNOWN: "Unknown", NO_ISSUES_FOUND: "Agent found no issues", ISSUES_FOUND: "Issues found", INCONCLUSIVE: "Inconclusive", CANDIDATE: "Candidate proof", SELF_CHECKED: "Agent checked", PARTIALLY_VERIFIED: "Partially verified", FORMALLY_VERIFIED: "Formally verified", EXPERT_REVIEWED: "Expert reviewed", REJECTED: "Rejected", KNOWN: "Known result", SPECIAL_CASE: "Special case", POTENTIALLY_NEW: "Potentially new",
  },
  zh: {
    chooseStep: "找题 → 用户选题 → 求解", chooseHint: "比较候选列表，选择你想研究的问题。Find 不会自动启动求解。", estimateHint: "难度和 Lean 可行性是有理由的估计，并非成功概率。问题是否仍开放，请结合来源证据判断。",
    findCriteria: "本次找题的完整要求",
    searchLimitations: "检索范围与局限（研究者说明）",
    yourChoice: "你选择的题目", chooseProblem: "选择这道题", chosen: "已选择", recommended: "Agent 推荐", clearChoice: "清除选题", discoveryCarry: "将携带这次找题的资料、笔记和来源。确认题目与设置后，点击开始求解。",
    difficulty: "求解难度", leanFeasibility: "Lean 可行性", prerequisites: "所需知识", obstacles: "主要障碍", initialApproach: "可尝试的起点", findNotReady: "请等待 Find 结束后再选题。",
    discoveryOrigin: "选题来自 Find", contextFiles: "已携带的研究文件", contextOmitted: "未携带的文件", contextScope: "在新求解会话中使用冻结的找题资料；不包含隐藏推理，也不代表资料中的结论已获认证。",
    specialistAgents: "辅助子 agent", researchMemories: "研究长期记忆", nativeInherit: "继承独立 Codex 配置", enabled: "开启", disabled: "关闭", capabilitiesHint: "仅作用于 MathLottery 独立账号环境。验真始终关闭长期记忆。子 agent 共用研究预算，可能增加 token 消耗。",

    localLab: "本地数学研究工作台", workflows: "研究流程", find: "找题", solve: "求解", verify: "验真",
    sideNote: "一个 agent，一点好奇心，一份值得检验的结果。", connecting: "正在连接…", connected: "已连接本地工作区", disconnected: "服务连接已断开",
    workspace: "数学研究工作台", eyebrow: "从一个问题开始，给发现一次机会", heroCopy: "找一个值得尝试的问题，认真探索，再检查结论是否成立。",
    accountTitle: "MathLottery 账号", accountSignIn: "使用 ChatGPT 账号登录", accountRefresh: "刷新状态", accountChecking: "正在检查账号…", accountConnected: "已登录 MathLottery", accountSignedOut: "登录 MathLottery 后，可通过 Codex 使用你的 ChatGPT 订阅。", accountUnavailable: "Codex 当前不可用，请安装或完成配置后刷新。",
    accountCliMissing: "未找到可运行的 Codex CLI。请在运行 MathLottery 的环境中安装官方 CLI，再从该环境重启 MathLottery 并刷新状态。", accountCliBroken: "已安装的 Codex CLI 无法运行。请修复运行 MathLottery 的环境中的 CLI 安装，然后刷新状态。", accountCliPlatform: "Codex 的 npm 启动器缺少当前系统的平台包。请在运行 MathLottery 的环境中安装官方 CLI；使用 WSL 时，请在 WSL 内安装 Linux 版 Codex，再刷新账号状态。",
    accountTimeout: "Codex 账号请求超时，登录状态尚未确认。请检查服务的网络或代理，也可在 .mathlottery/network.json 中配置本机网络，然后重启并刷新。超时本身不代表账号已退出。", accountNetworkInvalid: "本机网络配置无效。请检查 .mathlottery/network.json，然后重启服务并刷新。",
    accountWaiting: "等待你在官方页面完成登录…", accountStarting: "正在启动登录…", accountCancelling: "正在取消登录…", accountInstructions: "打开官方登录页面，输入下面的一次性验证码。", accountOpen: "前往 OpenAI 登录 ↗", accountCode: "一次性验证码", accountCopy: "复制", accountCopied: "验证码已复制。", accountSelectCode: "已选中验证码，请使用浏览器的复制操作。", accountCancel: "取消登录", accountInvalidLink: "未收到有效的官方登录链接，请取消后重试。", accountReadFailed: "无法检查 Codex 账号，请刷新重试。",
    accountSwitch: "切换账号", accountSignOut: "退出登录", accountSwitching: "正在退出当前账号并启动新登录…", accountSigningOut: "正在退出登录…", accountUsingApiKey: "Codex 当前使用 API Key；切换到 ChatGPT 账号后可使用订阅额度。",
    accountConfirmSwitch: "切换 MathLottery 账号？\n\n会先退出当前工作区的登录，再启动新的 ChatGPT 登录。如果取消或新登录失败，MathLottery 将保持退出状态。本地 Codex CLI / IDE 的登录不受影响。\n\n继续切换？",
    accountConfirmLogout: "退出 MathLottery 登录？\n\n当前工作区之后需要重新登录。本地 Codex CLI / IDE 的登录不受影响。\n\n继续退出？",
    accountNote: "当前工作区独立保存登录，切换或退出不影响本地 Codex CLI / IDE。可以使用同一个 ChatGPT 账号，订阅额度仍按账号共用。Chat API 仍需单独的 API Key，使用 API 计费。", accountApiKey: "API Key", accountPlan: "订阅",
    totalRuns: "执行记录", activeRuns: "正在运行", savedProblems: "已存题目", candidates: "候选证明", newAttempt: "开启一次尝试",
    findDescription: "搜索公开来源，比较值得尝试的问题，保留开放状态的证据。", solveDescription: "给研究 agent 一个明确的问题，让它自主选择方法、探索与推导。", verifyDescription: "由独立审查会话检查证明、前提与新颖性，记录依据和疑点。",
    criteria: "想找什么样的问题？", criteriaPlaceholder: "例如：找一个陈述简洁、范围较小、有希望用 Lean 验证的组合数学开放问题。",
    source: "优先检索的来源 · 可选", shortlistSize: "候选题数", reviewInput: "准备检查哪份证明？", savedCandidate: "已有任务的最新候选证明", pasteProof: "粘贴自己的证明",
    sourceRun: "选择含候选证明的任务", separateReview: "审查者使用独立会话，接收下方显示的候选证明、参考资料，以及你选择的源文件。", problem: "数学问题", newProblem: "输入一个新问题",
    sourceRefresh: "刷新来源", sourceRefreshHint: "刷新会加载最新候选并清空文件选择；后台更新不会改变这里显示的候选。", sourceLoading: "正在加载候选证明和可选源文件…", sourceChoose: "选择一个已有任务，加载其候选证明。", sourceMissing: "该任务没有可供审查的候选证明。", sourceBusy: "请等待来源任务结束或停止后，再审查其保存的候选证明。", sourceBinding: "本次审查的候选", sourceFiles: "附带证明源文件 · 可选", sourceFilesHint: "选择复现证明所需的文件；配套文本、JSON/CSV 证书和 Python 脚本请放在 proof/ 或 formal/ 下。默认不附带任何文件。审查者必须重新检查这些不可信输入；附带文件不会提升证明等级。", sourceFilesEmpty: "没有可选的求解源文件。", sourceLimits: "最多 20 个文件，单个不超过 1,000,000 字节，总计不超过 2,000,000 字节。Chat 以内联文本接收，总计不超过 128,000 字节。", sourceUnsupported: "附带源文件需要 native 执行模式。", nativeExecutionRequired: "前端研究任务需要 native 执行模式。请将 config.yaml 中的 backend.execution 设为 native，然后刷新页面。", sourceTooLarge: "该源文件超过单个文件大小限制。", sourceSelectionOver: "所选源文件超过数量或大小限制，请取消部分选择后再启动。", sourceSelected: "已选文件", sourceBytes: "字节", sourceCapturedHint: "验真启动时复制文件并计算哈希，结果区会展示捕获清单；之后修改源文件不影响这份快照。", evidenceSnapshot: "审查输入快照", snapshotCandidate: "来源候选", snapshotFiles: "已捕获源文件", snapshotEmpty: "未附带源文件，审查者接收的是候选文本和参考资料。", snapshotNote: "哈希用于确认捕获的输入内容，不代表输入正确；审查者需独立检查复制的文件。",
    problemTitle: "题目名称 · 可选", titlePlaceholder: "给这次探索起个名字", statement: "问题陈述", statementPlaceholder: "写下要研究的问题、已知条件，以及希望证明的结论。",
    proof: "待审查的证明", proofPlaceholder: "粘贴完整证明，包含所用假设和参考资料。", settings: "模型与预算", configDefault: "默认读取 config.yaml",
    instructions: "本次任务要求 · 可选", instructionsPlaceholder: "例如：提供 Lean 源文件，记录编译命令及结果，并检查边界情况。", instructionsHint: "可补充 Lean 验证等本次任务要求，原始数学命题保持不变。",
    backend: "调用方式", model: "模型", useConfig: "使用配置文件", inherited: "继承后端默认值", effort: "推理强度", chatMode: "Chat 思考模式",
    timeBudget: "时间预算 · 分钟", roundBudget: "最大轮数", overrideHint: "这里的修改仅影响本次任务。密钥仍从服务环境读取。",
    fullSolveBudget: "用满求解时间预算", fullSolveBudgetHint: "持续研究和自查至总时间上限，声称完整解决后也继续。其他限额、执行错误或你的停止请求仍可中断任务；此选项不替代 Verify，也不保证解出问题。",
    codexHint: "使用当前 MathLottery 工作区独立的 Codex 登录与工具配置。", chatHint: "使用 Chat API 及其 API 额度，需要在服务环境中配置 API Key。",
    readinessChecking: "正在检查 MathLottery 账号，完成后即可启动 Codex…", readinessSignIn: "请先在上方账号区域使用 ChatGPT 登录，再启动 Codex 研究。已填写的内容会保留。", readinessPending: "请在官方页面完成登录后回到这里，已填写的内容会保留。", readinessUnavailable: "Codex 当前不可用，请安装或完成配置，再刷新上方的账号状态。", readinessUnknown: "暂时无法确认账号状态，请刷新上方的账号状态后再启动 Codex。", readinessApiKey: "请通过上方「切换账号」登录 ChatGPT，再使用订阅额度启动 Codex 研究。",
    backgroundHint: "任务在后台运行，关闭页面后也可以随时回来查看。", notebook: "研究记录", recentRuns: "任务历史",
    historyHint: "每次 Find 保留独立候选列表；求解与验真按题目分组，同阶段多次执行单独编号。调用回合包含中断后续接。",
    stageFind: "找题", stageSolve: "求解", stageVerify: "验真", stagePipeline: "完整流程", runRecords: "条执行记录", lastUpdated: "最近更新", startedAt: "开始于", attempt: "第 {n} 次执行",
    startFind: "开始找题", startSolve: "开始求解", startVerify: "开始验真", starting: "正在启动…", emptyRuns: "下一个问题，从这里开始。", emptyRunsHint: "启动一次任务，积累题目、证明尝试和审查证据。",
    rounds: "调用回合", tokens: "tokens", elapsed: "活动耗时", unknown: "未知", stop: "停止任务", stopping: "正在停止…", resume: "继续 / 补充方向", verifyLatest: "验真最新候选", download: "下载报告 ↓",
    direction: "补充研究方向 · 可选", directionPlaceholder: "提示一种方法、要求检查边界条件，或补充新的研究方向。", newTotalBudget: "新的总时间预算 · 分钟", newTotalRounds: "新的总轮数上限",
    resumeHint: "这里设置的是新的总上限，不是追加额度；沿用该任务保存的模型配置。", continue: "继续研究", results: "结果", activity: "运行动态", report: "报告",
    leanLimits: "独立 Lean 检查资源", leanLimitsHint: "可调整本次任务的独立检查上限，留空沿用已保存的设置。Lean 内部阈值不等于实际内存占用；请结合可用资源设置。", leanMemory: "Lean 内存阈值 · MB", leanAddress: "虚拟地址空间上限 · MB", leanTimeout: "形式检查总时限 · 秒",
    visibleProgress: "最近的可见输出", checkingEvidence: "研究回复已保存，独立证据检查尚未完成。", events: "最近的检查点事件", footer: "好奇心开启尝试，证据决定结论。", noCandidates: "还没有候选证明，请先求解或选择粘贴证明。",
    noResults: "还没有提交研究结果。", waitingResults: "可以在「运行动态」查看检查点与已保存的 agent 输出。", shortlist: "找到的题目", solveThis: "求解这道题 →", statementDetails: "问题陈述与来源", sourceEvidence: "状态证据", selection: "选题理由", feasibility: "验证可行性",
    fullProof: "阅读完整证明", claim: "结论", review: "独立审查", novelty: "新颖性", unreviewed: "等待独立审查", assessmentLimit: "任务完成、证明证据和新颖性是不同结论。Agent 审查未发现问题，不代表首次解决了一个仍未解决的问题。", proofLevel: "记录的证明等级", latestReview: "最近一次 Agent 审查", problemStatus: "记录的问题状态", levelCandidate: "提出的证明，尚待独立检查。", levelSelfChecked: "Agent 审查未发现问题；这一等级尚未确立完整形式验证或专家认可。", levelPartial: "部分证据已核验，这一等级不代表原始命题已有完整形式证明。", levelFormal: "记录为已形式验证，请检查验证证据与原始命题的对应关系。", levelExpert: "记录为已获专家审查，请查看审查证据与适用范围。", levelRejected: "记录的审查指出了有证据支持的问题。",
    proofEvidence: "证据与参考资料", leanFiles: "证明文件", leanFilesNote: "这些是 agent 生成的源文件。文件存在不代表已编译通过，也不代表完整证明了原始命题。", leanFileTooLarge: "文件过大，无法在此下载", leanFilesTruncated: "这里只显示部分文件，其余文件仍保存在本地任务目录中。",
    declaredScope: "求解者声明的范围", originalCoverage: "审查者判断的原题覆盖", obligations: "尚待证明的内容", evidenceGaps: "证据核对与缺口", notAssessed: "尚未按新证据规则评估", excerptMatched: "原文摘录已核对", excerptMissing: "原文摘录未核实", searchObserved: "已记录的检索", proofChecks: "具体证明检查", formalReceipt: "独立 Lean 执行记录", formalScope: "仅检查指定定理；与原始问题的等价性尚未认证。", evidenceGate: "证据规则", sourceLimit: "原文匹配不代表引用解释正确，也不代表文献检索完整。",
    COMPLETE: "声明为完整结果", COUNTEREXAMPLE: "反例", FULL: "审查报告完整覆盖", PARTIAL: "部分结果", DIFFERENT: "不同命题", KERNEL_REPLAYED: "内核重放通过", UNAVAILABLE: "不可用", ERROR: "执行失败", TIMEOUT: "达到时间限制", OUTPUT_LIMIT: "达到输出限制", SUPPORTED: "有支持", CONTRADICTED: "发现矛盾", UNRESOLVED: "未解决",
    noProgress: "尚无保存的可见输出。原生 agent 使用工具的长回合中可能暂时没有文字更新。", truncated: "预览已截断，完整内容保留在本地任务目录。", noReport: "报告尚未生成。",
    launched: "任务已启动，进度保存在本地。", resumed: "已继续研究。", stopSent: "已请求停止，正在等待后台任务结束；已有进度会保留。", requestError: "请求失败，请先查看任务历史再重试。",
    workerInterrupted: "后台进程退出时未记录完成状态，可以继续任务以恢复检查点。",
    CREATED: "已创建", DISCOVERING: "找题中", SELECTING: "选题中", SOLVING: "求解中", VERIFYING: "验真中", REPORTING: "生成报告", COMPLETED: "已完成", PAUSED: "已暂停", WAITING_FOR_USER: "等待手动交接", RATE_LIMITED: "额度受限", FAILED: "失败", CANCELLED: "已停止",
    OPEN: "开放", SOLVED: "已解决", PARTIALLY_SOLVED: "部分解决", DISPUTED: "有争议", UNKNOWN: "未知", NO_ISSUES_FOUND: "Agent 未发现问题", ISSUES_FOUND: "发现问题", INCONCLUSIVE: "尚无定论", CANDIDATE: "候选证明", SELF_CHECKED: "Agent 已检查", PARTIALLY_VERIFIED: "部分已验证", FORMALLY_VERIFIED: "已形式验证", EXPERT_REVIEWED: "已获专家审查", REJECTED: "已否定", KNOWN: "已知结果", SPECIAL_CASE: "特殊情形", POTENTIALLY_NEW: "可能是新结果",
  },
};

Object.assign(words.en, {
  unsupportedChoice: "not supported by this catalog", unconfirmedChoice: "not confirmed by this catalog", unsupportedEffort: "The catalog does not support the selected reasoning effort ({value}) for this model. Your selection is preserved; choose another value before starting.", unconfirmedEffort: "The catalog does not confirm the selected reasoning effort ({value}). Your selection is preserved and will be submitted unchanged.", unsupportedMode: "The provider no longer lists reasoning mode {value}. Your selection is preserved; choose another mode or the provider default before starting.", unconfirmedMode: "The catalog does not confirm reasoning mode {value}. Your selection is preserved and will be submitted unchanged.",
  provider: "Provider", modelSettings: "Model for this task", budgetSettings: "Budget & agent settings", modelsRefresh: "Refresh models", modelIdentifier: "Model ID", effortIdentifier: "Reasoning effort value", manualModel: "Enter a model ID…", manualEffort: "Enter a reasoning value…", providerDefault: "Provider default", effectiveModel: "New task will use", modelsLoading: "Loading model catalog…", modelsLive: "Model catalog loaded from the provider.", modelsConfigured: "Models from your provider configuration.", modelsUnavailable: "Model catalog is unavailable. Configuration and manual model IDs still work.", modelsIdle: "Model catalog will load when the workspace is connected.", modelCatalogHint: "The catalog reports available choices, not guaranteed account access. You can enter an unlisted model ID.", modelScope: "Applies to new tasks only. Your config file, saved runs and account stay unchanged.", effortUnknown: "This provider has not reported reasoning capabilities for this model.", effortUnavailable: "This model reports no configurable reasoning effort.", modelRequired: "Enter a model ID, or select a model/default from the list.", effortRequired: "Enter a reasoning effort value, or choose the provider default.", modeLabel: "Mode", effortLabel: "Effort", configuredModel: "Configured model", customProviderHint: "Uses the selected provider's API and billing. Configure its API key in the server environment.",
});
Object.assign(words.zh, {
  unsupportedChoice: "当前目录不支持", unconfirmedChoice: "当前目录未确认", unsupportedEffort: "当前目录不支持这个模型使用推理强度 {value}。已保留你的选择，请重新选择后启动。", unconfirmedEffort: "当前目录无法确认推理强度 {value}。已保留你的选择，提交时会原样使用。", unsupportedMode: "提供方当前不再列出思考模式 {value}。已保留你的选择，请更换模式或选择提供方默认值后启动。", unconfirmedMode: "当前目录无法确认思考模式 {value}。已保留你的选择，提交时会原样使用。",
  provider: "模型提供方", modelSettings: "本次任务的模型", budgetSettings: "预算与 agent 设置", modelsRefresh: "刷新模型列表", modelIdentifier: "模型 ID", effortIdentifier: "推理强度值", manualModel: "手动输入模型 ID…", manualEffort: "手动输入推理强度…", providerDefault: "提供方默认值", effectiveModel: "新任务将使用", modelsLoading: "正在加载模型目录…", modelsLive: "已从提供方加载模型目录。", modelsConfigured: "显示提供方配置中的模型。", modelsUnavailable: "暂时无法获取模型目录，仍可使用配置或手动输入模型 ID。", modelsIdle: "连接工作区后加载模型目录。", modelCatalogHint: "模型目录不保证当前账号拥有调用权限。未列出的模型仍可手动输入 ID。", modelScope: "仅用于新任务，不修改配置文件、历史任务或登录账号。", effortUnknown: "提供方尚未报告这个模型支持的推理强度。", effortUnavailable: "这个模型未提供可选的推理强度。", modelRequired: "请输入模型 ID，或从列表选择模型或默认值。", effortRequired: "请输入推理强度，或选择提供方默认值。", modeLabel: "思考模式", effortLabel: "推理强度", configuredModel: "配置中的模型", customProviderHint: "使用所选提供方的 API 与计费；API Key 需要在服务环境中配置。",
});

Object.assign(words.en, {
  taskOptions: "Additional requirements", modelHelp: "Model details & help", accountManage: "Manage account",
  useConfig: "Config", historySearchLabel: "Search history",
  historySearch: "Search title, model or run ID", historyFilter: "Run status", historyAll: "All runs",
  historyRunning: "Running", historyAttention: "Needs attention", historyCompleted: "Completed runs",
  historyCount: "{n} of {total} runs", historyNoMatch: "No matching runs", historyNoMatchHint: "Try another search or status filter.",
  historyEarlier: "Earlier attempts ({n})", historyHint: "Once a problem is selected for Solve, its source Find joins the same problem group. A Find used by multiple problems is shared, counted once. Run status, solver claims and review findings are separate.", historyHelp: "How runs are grouped",
  COMPLETED: "Run completed", candidateVersion: "Candidate {n}", latestCandidate: "Latest candidate",
  earlierCandidate: "Earlier candidate {n}", reviewDetails: "Review reasoning & evidence", reviewVersion: "Review {n}",
  assumptions: "Assumptions", accountConnected: "Codex connected", accountSignedOut: "Sign in to use Codex",
  accountUnavailable: "Codex unavailable", accountReadFailed: "Account status unknown",
});
Object.assign(words.zh, {
  taskOptions: "补充要求", modelHelp: "模型详情与说明", accountManage: "管理账号",
  useConfig: "配置默认", historySearchLabel: "搜索记录",
  historySearch: "搜索题目、模型或任务 ID", historyFilter: "运行状态", historyAll: "全部任务",
  historyRunning: "正在运行", historyAttention: "需要关注", historyCompleted: "运行完成",
  historyCount: "显示 {n} / {total} 条", historyNoMatch: "没有匹配的任务", historyNoMatchHint: "试试其他关键词或状态筛选。",
  historyEarlier: "较早的尝试（{n}）", historyHint: "选题开始求解后，来源 Find 与后续步骤按问题归组。一次 Find 可作为多个问题的共享来源，执行总数只计一次。运行状态、求解声称和审查结论分别展示。", historyHelp: "任务归组说明",
  COMPLETED: "运行完成", candidateVersion: "候选证明 {n}", latestCandidate: "最新候选证明",
  earlierCandidate: "较早的候选证明 {n}", reviewDetails: "审查过程与证据", reviewVersion: "审查 {n}",
  assumptions: "前提假设", accountConnected: "Codex 已连接", accountSignedOut: "登录后使用 Codex",
  accountUnavailable: "Codex 暂不可用", accountReadFailed: "登录状态未确认",
});
Object.assign(words.en, {
  organize: "Organize the research", stageOrganize: "Organize", ORGANIZING: "Organizing",
  organizeDescription: "Turn the proof and its review into a report for a human expert, with traceable supporting materials.",
  startOrganize: "Create expert report", organizeReviewed: "Organize for expert review",
  organizeSource: "Run with a reviewed candidate", organizeLanguages: "Chinese + English · Markdown and PDF for each",
  organizeChoose: "Choose a run with at least one reviewed candidate.", organizeNone: "No reviewed candidates yet — run Verify first",
  organizeSourceHint: "Choose a completed review to organize. Unresolved findings and rejected candidates can also be documented.",
  organizeSourceCount: "{n} reviewed candidate(s). The report retains the findings and remaining gaps.",
  organizeScope: "Organizes the statement, proof, supporting materials and review findings for expert reading. This editorial step does not establish correctness or novelty.",
  organizeReport: "Expert reading report", organizeOrigin: "Source research & review", organizePending: "No expert report has been saved yet.", downloadTaskReport: "Download task summary ↓",
  organizeMarkdown: "Download Markdown", organizePdf: "Download PDF", organizeBundle: "Download report + materials (ZIP)", organizePdfFailed: "PDF is unavailable. The Markdown report is still available.",
  organizeRetryPdf: "Retry PDF export", organizeRetryingPdf: "Exporting PDF…", organizeRetryHint: "Rebuilds PDFs for all saved language versions without another model call. It does not translate missing versions.",
  organizePdfWarnings: "PDF export notes", organizeDigest: "Markdown SHA-256", organizePrepared: "Source selected. Review the model settings, then create both language versions.",
  organizeMissingLanguage: "This language version has not been generated. Start Organize from the reviewed source to create both versions.",
  organizeLegacy: "This saved report contains one language version. PDF export does not add a translation.",
});
Object.assign(words.zh, {
  organize: "整理研究材料", stageOrganize: "整理", ORGANIZING: "正在整理",
  organizeDescription: "将证明过程与审查结果整理为供人类专家阅读的报告，并保留可追溯的支持材料。",
  startOrganize: "生成专家阅读报告", organizeReviewed: "整理为专家阅读报告",
  organizeSource: "包含已审查候选证明的任务", organizeLanguages: "中文 + English · 各一份 Markdown 和 PDF",
  organizeChoose: "请选择至少包含一份已审查候选证明的任务。", organizeNone: "暂无已审查候选，请先运行验真",
  organizeSourceHint: "选择要整理的审查记录。尚存疑点或被否定的候选证明也可以整理。",
  organizeSourceCount: "包含 {n} 份已审查候选证明。报告会保留审查发现与未解决的缺口。",
  organizeScope: "整理原命题、证明、支持材料与审查结论，便于专家阅读。这一步不新增正确性或新颖性认证。",
  organizeReport: "专家阅读报告", organizeOrigin: "来源研究与审查", organizePending: "尚未保存专家阅读报告。", downloadTaskReport: "下载任务摘要 ↓",
  organizeMarkdown: "下载 Markdown", organizePdf: "下载 PDF", organizeBundle: "下载报告与材料（ZIP）", organizePdfFailed: "PDF 暂不可用，仍可下载 Markdown 报告。",
  organizeRetryPdf: "重新导出 PDF", organizeRetryingPdf: "正在导出 PDF…", organizeRetryHint: "重新导出各已保存语言版本的 PDF，不再次调用模型；不会翻译缺失的语言版本。",
  organizePdfWarnings: "PDF 导出说明", organizeDigest: "Markdown SHA-256", organizePrepared: "已选择来源。确认模型配置后，生成中英文两版报告。",
  organizeMissingLanguage: "尚未生成此语言版本。请从已审查来源启动整理，生成中英文两版报告。",
  organizeLegacy: "这份已保存的报告只有一种语言；重新导出 PDF 不会补充翻译。",
});

function preference(key, value) {
  try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch { /* Storage can be disabled. */ }
  return null;
}
const state = { language: preference("mathlottery.language") || (navigator.language.startsWith("zh") ? "zh" : "en"), workflow: "find", settings: null, runs: [], problems: [], csrf: "", selected: preference("mathlottery.run"), detail: null, resultsKey: "", discoveryChoice: null, polling: false, submitting: false, resuming: false };
// Model choices stay in this form; do not restore stale selections from localStorage.
const modelState = { providers: [], data: null, generation: 0, requestedProvider: "", loading: false, error: "", initialized: false };
// Account identity and device codes stay in memory, separate from saved UI preferences.
const accountState = { data: null, busy: false, operation: "status", error: "" };
// This form snapshot changes only on an explicit source choice/refresh, never a background poll.
const reviewSource = { generation: 0, runId: "", loading: false, error: "", run: null, candidate: null, files: [], selected: new Set(), filesKey: "" };
const pdfExports = new Set();
if (!words[state.language]) state.language = "en";
const t = (key) => words[state.language][key] || key;
const compact = (value) => value == null ? t("unknown") : new Intl.NumberFormat(state.language, { notation: "compact", maximumFractionDigits: 1 }).format(value);
const date = (value) => new Date(value).toLocaleString(state.language === "zh" ? "zh-CN" : "en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

function node(tag, className, text) { const item = document.createElement(tag); if (className) item.className = className; if (text != null) item.textContent = text; return item; }
function text(selector, value) { const item = $(selector); if (item.textContent !== String(value)) item.textContent = value; }
function notice(selector, value) { text(selector, value || ""); $(selector).hidden = !value; }
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
function finalizationBudgetHint(settings) {
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
function configuredProvider() { return state.settings?.provider || state.settings?.backend || "codex"; }
function selectedProvider() { return $("#backend").value || configuredProvider(); }
function providers() {
  const entries = new Map([
    ["codex", { id: "codex", label: "Codex", transport: "codex", reasoning_modes: [] }],
    ["chat", { id: "chat", label: "OpenAI API", transport: "responses", reasoning_modes: [] }],
  ]);
  if (!entries.has(configuredProvider())) entries.set(configuredProvider(), { id: configuredProvider(), label: configuredProvider(), transport: state.settings?.backend === "chat" ? "responses" : state.settings?.backend, reasoning_modes: [] });
  for (const provider of modelState.providers) entries.set(provider.id, provider);
  return [...entries.values()];
}
function selectedProviderInfo() { return providers().find((provider) => provider.id === selectedProvider()); }
function selectedBackend() { return selectedProviderInfo()?.transport === "responses" ? "chat" : selectedProviderInfo()?.transport || state.settings?.backend; }
function selectedModelId() {
  const value = $("#model-select").value;
  if (value === "__manual") return $("#model").value.trim() || null;
  if (value === "__default") return null;
  return value || (selectedProvider() === configuredProvider() ? state.settings?.model : null);
}
function selectedModelInfo() {
  if (modelState.data?.provider !== selectedProvider()) return null;
  return modelState.data.models.find((model) => model.id === selectedModelId()) || null;
}
function modelOverrides() {
  const values = {}, provider = $("#backend").value, model = $("#model-select").value;
  if (provider) values.provider = provider;
  if (model) values.model = selectedModelId();
  const effort = $("#effort-select").value;
  if (effort) values.reasoning_effort = effort === "__default" ? null : effort === "__manual" ? $("#effort").value.trim() || null : effort;
  const mode = $("#reasoning-mode").value;
  if (mode) values.reasoning_mode = mode === "__default" ? null : mode;
  return values;
}
function selectedReasoningModes() {
  // A missing metadata response means unknown capabilities, not an empty list.
  const metadata = modelState.data?.provider === selectedProvider() ? modelState.data.providers?.find((item) => item.id === selectedProvider()) : null;
  return Array.isArray(metadata?.reasoning_modes) ? metadata.reasoning_modes : null;
}
function modelCapabilityIssues() {
  const overrides = modelOverrides();
  const effort = Object.hasOwn(overrides, "reasoning_effort") ? overrides.reasoning_effort : state.settings?.reasoning_effort;
  const mode = Object.hasOwn(overrides, "reasoning_mode") ? overrides.reasoning_mode : state.settings?.reasoning_mode;
  const efforts = selectedModelInfo()?.reasoning_efforts, modes = selectedReasoningModes(), issues = [];
  if (effort && (!Array.isArray(efforts) || !efforts.includes(effort))) issues.push({ blocking: Array.isArray(efforts), message: t(Array.isArray(efforts) ? "unsupportedEffort" : "unconfirmedEffort").replace("{value}", effort) });
  if (selectedBackend() === "chat" && mode && (!modes || !modes.includes(mode))) issues.push({ blocking: Boolean(modes), message: t(modes ? "unsupportedMode" : "unconfirmedMode").replace("{value}", mode) });
  return issues;
}
function modelSelectionBlock() {
  if ($("#model-select").value === "__manual" && !$("#model").value.trim()) return t("modelRequired");
  if ($("#effort-select").value === "__manual" && !$("#effort").value.trim()) return t("effortRequired");
  return modelCapabilityIssues().find((issue) => issue.blocking)?.message || "";
}
function resetReasoningSelection() {
  $("#effort-select").value = "__default"; $("#effort").value = "";
  $("#reasoning-mode").value = "__default";
}
function modelSummary(settings, fallbackProvider) {
  const provider = settings.provider || settings.backend || fallbackProvider;
  // Saved configs may retain dormant chat settings while executing with Codex.
  const backend = settings.backend || providers().find((item) => item.id === provider)?.transport || fallbackProvider;
  const showMode = ["chat", "responses"].includes(backend) && settings.reasoning_mode;
  return [provider, settings.model || t("providerDefault"), `${t("effortLabel")}: ${settings.reasoning_effort || t("providerDefault")}`, showMode ? `${t("modeLabel")}: ${settings.reasoning_mode}` : ""].filter(Boolean).join(" · ");
}
function renderModelPreview() {
  if (!state.settings) return;
  const overrides = modelOverrides();
  const selected = { provider: selectedProvider(), backend: selectedBackend(), model: selectedModelId(), reasoning_effort: Object.hasOwn(overrides, "reasoning_effort") ? overrides.reasoning_effort : state.settings.reasoning_effort, reasoning_mode: Object.hasOwn(overrides, "reasoning_mode") ? overrides.reasoning_mode : state.settings.reasoning_mode };
  const summary = modelSummary(selected);
  text("#model-preview", summary);
}
function renderModels() {
  const provider = selectedProvider();
  options("#backend", providers().map((item) => [item.id, item.label]), `${t("useConfig")} · ${configuredProvider()}`);
  const catalog = modelState.data?.provider === provider ? modelState.data.models : [];
  const entries = [["__default", t("providerDefault")], ...catalog.map((model) => [model.id, model.label && model.label !== model.id ? `${model.label} · ${model.id}` : model.id])];
  const configuredModel = provider === configuredProvider() ? state.settings?.model : null;
  if (configuredModel && !entries.some(([id]) => id === configuredModel)) entries.push([configuredModel, `${configuredModel} · ${t("configuredModel")}`]);
  // A refreshed catalog must not silently erase an explicitly chosen model.
  const current = $("#model-select").value;
  if (current && !["__manual", "__default"].includes(current) && !entries.some(([id]) => id === current)) entries.push([current, current]);
  entries.push(["__manual", t("manualModel")]);
  options("#model-select", entries, `${t("useConfig")}${configuredModel ? ` · ${configuredModel}` : ""}`);
  const inheritModel = $("#model-select").options[0];
  inheritModel.hidden = inheritModel.disabled = provider !== configuredProvider();
  if (inheritModel.disabled && !$("#model-select").value) $("#model-select").value = "__default";
  $("#manual-model").hidden = $("#model-select").value !== "__manual";
  $("#model").disabled = $("#manual-model").hidden;
  const model = selectedModelInfo(), efforts = model?.reasoning_efforts;
  const effortEntries = [["__default", t("providerDefault")], ...(Array.isArray(efforts) ? efforts.map((effort) => [effort, effort]) : [["__manual", t("manualEffort")]])];
  const currentEffort = $("#effort-select").value;
  if (currentEffort && !effortEntries.some(([value]) => value === currentEffort)) {
    const label = currentEffort === "__manual" ? t("manualEffort") : `${currentEffort} · ${t(Array.isArray(efforts) ? "unsupportedChoice" : "unconfirmedChoice")}`;
    effortEntries.push([currentEffort, label]);
  }
  options("#effort-select", effortEntries, `${t("useConfig")}${!$("#model-select").value && provider === configuredProvider() && state.settings?.reasoning_effort ? ` · ${state.settings.reasoning_effort}` : ""}`);
  // A newly selected model never borrows another model's configured effort.
  const inheritEffort = $("#effort-select").options[0];
  inheritEffort.hidden = inheritEffort.disabled = Boolean($("#model-select").value);
  if (inheritEffort.disabled && !$("#effort-select").value) $("#effort-select").value = "__default";
  $("#manual-effort").hidden = $("#effort-select").value !== "__manual";
  $("#effort").disabled = $("#manual-effort").hidden;
  const knownModes = selectedReasoningModes(), modes = knownModes || [];
  const previousMode = $("#reasoning-mode").value;
  const modeEntries = [["__default", t("providerDefault")], ...modes.map((mode) => [mode, mode === "pro" ? "Pro" : mode === "standard" ? "Standard" : mode])];
  if (previousMode && !modeEntries.some(([value]) => value === previousMode)) modeEntries.push([previousMode, `${previousMode} · ${t(knownModes ? "unsupportedChoice" : "unconfirmedChoice")}`]);
  options("#reasoning-mode", modeEntries, t("useConfig"));
  const inheritMode = $("#reasoning-mode").options[0];
  inheritMode.hidden = inheritMode.disabled = Boolean($("#model-select").value);
  if (inheritMode.disabled && !$("#reasoning-mode").value) $("#reasoning-mode").value = "__default";
  const inheritedMode = !previousMode && selectedBackend() === "chat" && state.settings?.reasoning_mode;
  const showMode = Boolean(modes.length || inheritedMode || (previousMode && previousMode !== "__default"));
  $("#reasoning-mode-field").hidden = !showMode;
  $("#reasoning-mode").disabled = !showMode;
  const details = [model?.description, Array.isArray(efforts) ? (!efforts.length ? t("effortUnavailable") : "") : t("effortUnknown")].filter(Boolean).join(" ");
  text("#model-description", details); $("#model-description").hidden = !details;
  const source = modelState.data?.provider === provider ? modelState.data.source : null;
  text("#models-status", t(modelState.loading ? "modelsLoading" : !modelState.initialized ? "modelsIdle" : source === "live" ? "modelsLive" : source === "configured" ? "modelsConfigured" : "modelsUnavailable"));
  notice("#models-error", modelState.error);
  notice("#model-capability-warning", modelCapabilityIssues().map((issue) => issue.message).join("\n"));
  $("#models-refresh").disabled = modelState.loading || !state.settings;
  renderModelPreview();
}
async function loadModels(refreshCatalog = false) {
  if (!state.settings) return;
  const provider = selectedProvider(), generation = ++modelState.generation;
  modelState.initialized = true; modelState.requestedProvider = provider; modelState.loading = true; modelState.error = "";
  if (modelState.data?.provider !== provider) modelState.data = null;
  renderModels();
  try {
    const data = await api(`/api/models?provider=${encodeURIComponent(provider)}${refreshCatalog ? "&refresh=1" : ""}`);
    if (generation !== modelState.generation || provider !== selectedProvider()) return;
    if (Array.isArray(data.providers)) {
      // Keep transport identities through temporary metadata gaps; capability
      // checks above use only the current response, never these cached entries.
      const known = new Map(modelState.providers.map((item) => [item.id, item]));
      for (const item of data.providers) known.set(item.id, item);
      modelState.providers = [...known.values()];
    }
    modelState.data = { ...data, provider, models: Array.isArray(data.models) ? data.models : [] };
    modelState.error = typeof data.error === "string" ? data.error : "";
  } catch (error) {
    if (generation !== modelState.generation || provider !== selectedProvider()) return;
    modelState.data = { provider, models: [], source: "unavailable" }; modelState.error = error.message;
  } finally {
    if (generation === modelState.generation) { modelState.loading = false; updateForm(); }
  }
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
  if (!data.available) return t(["ACCOUNT_TIMEOUT", "NETWORK_CONFIG_INVALID"].includes(data.error_code) ? "readinessUnknown" : "readinessUnavailable");
  if (data.authenticated && ["chatgpt", "chatgptAuthTokens"].includes(data.account?.type)) return "";
  if (data.account?.type === "apiKey") return t("readinessApiKey");
  return t(data.login?.status === "pending" ? "readinessPending" : "readinessSignIn");
}
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
  const backend = selectedBackend();
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
  return modelSelectionBlock() || executionBlock(selectedBackend()) || reviewSourceBlock() || organizeSourceBlock();
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
  if (!data?.available && ["ACCOUNT_TIMEOUT", "NETWORK_CONFIG_INVALID"].includes(data?.error_code)) status = "accountReadFailed";
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
  const errorKey = ({ CLI_NOT_FOUND: "accountCliMissing", CLI_UNAVAILABLE: "accountCliBroken", CLI_PLATFORM_DEPENDENCY_MISSING: "accountCliPlatform", ACCOUNT_TIMEOUT: "accountTimeout", NETWORK_CONFIG_INVALID: "accountNetworkInvalid" })[data?.error_code];
  notice("#account-error", accountState.error || (errorKey ? t(errorKey) : data?.error) || (pending && (!url || !code) ? t("accountInvalidLink") : ""));
  // Open on a new actionable state, without fighting the user's manual toggle.
  const attention = accountState.error || data?.error_code || data?.error || (pending ? "pending" : data && (!data.available || !connected || account?.type === "apiKey") ? status : "");
  if (attention && accountState.attention !== attention) $("#account-panel").open = true;
  accountState.attention = attention;
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
  if (scroll) { $("#composer").scrollIntoView({ behavior: "smooth", block: "start" }); $(workflow === "find" ? "#query" : workflow === "verify" ? "#verify-mode" : workflow === "organize" ? "#organize-from-run" : "#problem-id").focus({ preventScroll: true }); }
}
function updateForm() {
  const flow = state.workflow, savedReview = flow === "verify" && $("#verify-mode").value === "saved";
  $$("[data-workflow]").forEach((button) => { const active = button.dataset.workflow === flow; button.classList.toggle("selected", active); button.setAttribute("aria-pressed", active); });
  text("#form-title", t(flow)); text("#form-description", t(`${flow}Description`)); text("#form-number", { find: "01", solve: "02", verify: "03", organize: "04" }[flow]);
  text("#start-label", state.submitting ? t("starting") : t({ find: "startFind", solve: "startSolve", verify: "startVerify", organize: "startOrganize" }[flow]));
  $("#find-fields").hidden = flow !== "find"; $("#verify-fields").hidden = flow !== "verify";
  $("#organize-fields").hidden = flow !== "organize";
  const organizeSource = state.runs.find((item) => item.id === $("#organize-from-run").value);
  text("#organize-source-note", organizeSource ? t("organizeSourceCount").replace("{n}", reviewedCandidateCount(organizeSource)) : t("organizeSourceHint"));
  $("#find-options").hidden = flow !== "find";
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
  const backend = selectedBackend();
  renderModels();
  $("#native-capabilities").hidden = backend !== "codex";
  $("#multi-agent").disabled = $("#memories").disabled = backend !== "codex";
  text("#backend-hint", t(backend === "chat" ? selectedProvider() === "chat" ? "chatHint" : "customProviderHint" : "codexHint"));
  renderReviewSource();
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
    renderModelPreview();
    for (const [id, value] of [["budget", state.settings.budget_minutes], ["iterations", state.settings.max_iterations]]) $("#" + id).placeholder = value ?? t("inherited");
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
  $("#resume-full-budget-field").hidden = run.workflow !== "solve" || run.settings.execution !== "native";
  if ($("#resume-full-budget").dataset.runId !== run.id) {
    $("#resume-full-budget").checked = Boolean(run.settings.solve_until_budget_exhausted);
    $("#resume-full-budget").dataset.runId = run.id;
  }
  text("#resume-full-budget-hint", `${t("fullSolveBudgetHint")} ${finalizationBudgetHint(run.settings)}`);
  text("#detail-id", `${run.workflow.toUpperCase()} / ${run.id}`); text("#detail-title", run.title);
  const status = executionBadge(run); $("#detail-state").className = status.className; text("#detail-state", status.textContent);
  $("#run-facts").replaceChildren(...[modelSummary(run.settings, run.mode), `${run.iteration} ${t("rounds")}`, `${Math.round(run.elapsed_seconds / 60 * 10) / 10} min ${t("elapsed")}`, `${compact(run.usage.input_tokens)} in / ${compact(run.usage.output_tokens)} out ${t("tokens")}`].map((fact) => node("span", "", fact)));
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
    state.detail = run; renderOverview(); renderDetail(run);
    $("#resume-budget").value = ""; $("#resume-rounds").value = ""; $("#direction").value = "";
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
    text("#connection", t("connected")); notice("#global-error", data.config_error); renderOverview(); updateForm(); renderAccount();
    if (!modelState.initialized || modelState.requestedProvider !== selectedProvider()) void loadModels();
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
  const values = modelOverrides();
  for (const [id, key] of [["budget", "budget_minutes"], ["iterations", "max_iterations"]]) {
    const input = $("#" + id), value = input.value.trim();
    if (value && !input.disabled) values[key] = ["budget", "iterations"].includes(id) ? Number(value) : value;
  }
  for (const [id, key] of [["multi-agent", "native_multi_agent"], ["memories", "native_memories"]]) {
    const input = $("#" + id); if (input.value && !input.disabled) values[key] = input.value === "inherit" ? null : input.value === "true";
  }
  if (!$("#solve-full-budget-field").hidden && !$("#solve-full-budget").disabled) values.solve_until_budget_exhausted = $("#solve-full-budget").checked;
  return values;
}
$("#solve-full-budget").addEventListener("change", () => { $("#solve-full-budget").dataset.touched = "true"; });
$$("[data-workflow]").forEach((button) => button.addEventListener("click", () => setWorkflow(button.dataset.workflow, button.classList.contains("nav-item"))));
$("#verify-mode").addEventListener("change", updateForm);
$("#backend").addEventListener("change", () => {
  $("#model-select").value = $("#backend").value ? "__default" : ""; $("#model").value = ""; $("#effort").value = "";
  $("#effort-select").value = $("#reasoning-mode").value = $("#backend").value ? "__default" : "";
  modelState.data = null; updateForm(); void loadModels();
});
$("#model-select").addEventListener("change", () => {
  $("#model").value = "";
  if (!$("#model-select").value) { $("#effort-select").value = ""; $("#effort").value = ""; $("#reasoning-mode").value = ""; }
  else resetReasoningSelection();
  updateForm();
});
$("#model").addEventListener("input", () => { resetReasoningSelection(); updateForm(); });
$("#effort-select").addEventListener("change", () => { $("#effort").value = ""; updateForm(); });
$("#effort").addEventListener("input", () => { renderModels(); updateExecutionControls(); });
$("#reasoning-mode").addEventListener("change", () => { renderModels(); updateExecutionControls(); });
$("#models-refresh").addEventListener("click", () => loadModels(true));
$("#problem-id").addEventListener("change", () => { state.discoveryChoice = null; state.resultsKey = ""; if (state.detail) renderResults(state.detail); updateForm(); });
$("#clear-discovery").addEventListener("click", () => { state.discoveryChoice = null; $("#problem-id").value = ""; state.resultsKey = ""; if (state.detail) renderResults(state.detail); updateForm(); });
$("#from-run").addEventListener("change", loadReviewSource);
$("#organize-from-run").addEventListener("change", updateForm);
$("#source-refresh").addEventListener("click", loadReviewSource);
$("#language").addEventListener("click", () => { state.language = state.language === "en" ? "zh" : "en"; preference("mathlottery.language", state.language); applyLanguage(); text("#connection", t(state.csrf ? "connected" : "connecting")); });
$("#refresh").addEventListener("click", refresh);
$("#history-search").addEventListener("input", renderHistory);
$("#history-filter").addEventListener("change", renderHistory);
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
  catch (error) { notice("#form-error", error.message); await refreshAccount(); }
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
$("#resume-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const body = {};
  const run = state.detail;
  if (state.resuming || !run || run.busy || !state.csrf || executionBlock(run.settings.backend || run.mode)) { updateExecutionControls(); return; }
  if ($("#direction").value.trim()) body.message = $("#direction").value.trim();
  if ($("#resume-budget").value) body.budget_minutes = Number($("#resume-budget").value);
  if ($("#resume-rounds").value) body.max_iterations = Number($("#resume-rounds").value);
  if (!$("#resume-full-budget-field").hidden) body.solve_until_budget_exhausted = $("#resume-full-budget").checked;
  if (!$("#resume-lean-limits").hidden) {
    for (const [field, selector] of Object.entries({formal_memory_mb: "#resume-lean-memory", formal_address_space_mb: "#resume-lean-address", formal_timeout_seconds: "#resume-lean-timeout"})) {
      if ($(selector).value) body[field] = Number($(selector).value);
    }
  }
  state.resuming = true; updateExecutionControls();
  try { await api(`/api/runs/${state.selected}/resume`, body); $("#resume-form").hidden = true; toast(t("resumed")); await refresh(); }
  catch (error) { notice("#run-message", error.message); await refreshAccount(); }
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
applyLanguage(); refresh(); refreshAccount();
setInterval(() => { if (!document.hidden) refresh(); }, 2000);
setInterval(() => { if (!document.hidden && accountState.data?.login?.status === "pending") refreshAccount(); }, 2000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) { refresh(); refreshAccount(); } });
