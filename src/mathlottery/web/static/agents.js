/* Agent configuration contains connection metadata only. Never collect or persist API keys. */
(function () {
  "use strict";
  const { $, $$, node, text, notice } = MathLotteryDOM.scope(document);
  const words = {
    en: {
      back: "← Research workspace", eyebrow: "SOLVE · YOUR RESEARCH TEAM", title: "One slot. One connection.",
      intro: "Choose an agent engine, then its authentication. Codex supports ChatGPT sign-in or an API key; API agents use a separate Responses connection.",
      count: "Maximum parallel agents", countNote: "Each researcher keeps its connection when groups change. Slot 1 also handles supervision and wrap-up, outside the parallel research round.",
      save: "Save configuration", saving: "Saving…", saved: "Saved locally", changed: "Unsaved changes", loading: "Loading configuration…",
      nextTitle: "Start a Solve task", next: "Return to the workspace and select “Use configured agent slots”. Existing runs keep their saved connections.",
      privacyTitle: "Local, separate sign-ins", privacy: "Codex subscription logins and API execution profiles stay separate from each other and your normal CLI / IDE. API keys remain in server environment variables. Account usage limits still apply; a limit never triggers an automatic account switch.",
      agent: "Agent", primary: "Supervision + wrap-up", label: "Label · optional", connection: "Agent engine", codex: "Codex agent", responses: "API agent · Responses",
      auth: "Authentication & billing", chatgptAuth: "ChatGPT sign-in · subscription usage", apiAuth: "API key · API billing", codexApiHint: "Runs the same native Codex agent with its tools. Uses an OpenAI API key and API billing, in a separate workspace profile; your ChatGPT login stays unchanged.",
      model: "Model ID", modelPlaceholder: "Provider default", apiModelPlaceholder: "Model ID, or server OPENAI_MODEL", effort: "Reasoning effort", effortPlaceholder: "Provider default; e.g. max", modelHint: "Use a model ID and effort supported by this account or endpoint. Saving configuration does not test model access.",
      reasoningMode: "API reasoning mode", defaultMode: "Endpoint default", standardMode: "Standard", proMode: "Pro · supported models only",
      endpoint: "API base URL", env: "API key environment variable", envHint: "Enter a variable name, never the key itself. Set its value in the terminal that starts MathLottery, then restart the server. API connections use the selected key and API billing.",
      tools: "Hosted tools", toolsOpenAI: "Web search + code interpreter", toolsNone: "None", toolsCustom: "Preserve configured tools", toolsHint: "For another Responses-compatible provider, use only tools that its endpoint supports.",
      keyReady: "Environment variable is set; access has not been tested.", keyMissing: "Environment variable is not set in the running server.", saveKeyFirst: "Save the configuration to check this environment variable.",
      signIn: "Sign in with ChatGPT", signOut: "Sign out", switchAccount: "Switch account", refresh: "Refresh status", cancel: "Cancel sign-in", copy: "Copy code", copied: "Copied", open: "Continue at OpenAI ↗",
      checking: "Checking this slot…", unconfirmed: "Sign-in status has not been checked.", signedOut: "Not signed in", connected: "Signed in", unavailable: "Account status unavailable", pending: "Waiting for sign-in", saveFirst: "Save the configuration before managing this slot’s login.",
      codeHint: "Open the official page and enter this one-time code. Status refreshes while sign-in is pending.", invalidLink: "The sign-in link was not an official OpenAI HTTPS URL. Refresh this slot and retry.",
      confirmSwitch: "Switch this slot’s ChatGPT account? Its previous login will be signed out. Other slots and your local Codex login stay unchanged.",
      confirmLogout: "Sign out this slot? Other slots and your local Codex login stay unchanged.", requestError: "Could not reach the local MathLottery server. Refresh and retry.",
      discard: "Reload the saved configuration and discard unsaved changes?", reload: "Reload saved configuration", countRange: "Choose a whole number from 1 to 32.",
    },
    zh: {
      back: "← 返回研究工作台", eyebrow: "SOLVE · 配置研究团队", title: "每个 agent，独立配置。",
      intro: "先选择 agent 执行方式，再选择认证方式。Codex 支持 ChatGPT 登录或 API Key；API agent 使用独立的 Responses 接口。",
      count: "最大并行 agent 数", countNote: "调整分组时，各研究者保持自己的接入配置。第 1 个槽位还负责监督和收尾，与并行研究分时执行。",
      save: "保存配置", saving: "正在保存…", saved: "已保存到本地", changed: "有未保存的修改", loading: "正在读取配置…",
      nextTitle: "开始一次求解", next: "回到工作台，勾选「使用已配置的 agent 槽位」。已有任务继续使用启动时保存的配置。",
      privacyTitle: "登录独立保存在本地", privacy: "Codex 的订阅登录与 API 执行状态分别保存，并与本地 CLI / IDE 隔离。API Key 只从服务端环境变量读取。账号使用限制仍然适用，触发限制后不会自动切换账号。",
      agent: "Agent", primary: "兼任监督与收尾", label: "备注名称 · 可选", connection: "Agent 执行方式", codex: "Codex agent", responses: "API agent · Responses",
      auth: "认证与计费", chatgptAuth: "ChatGPT 账号登录 · 订阅额度", apiAuth: "API Key · API 计费", codexApiHint: "运行同一个原生 Codex agent，保留其工具能力。使用 OpenAI API Key 和 API 计费，运行状态独立保存，不改变已有 ChatGPT 登录。",
      model: "模型 ID", modelPlaceholder: "由接入方选择默认模型", apiModelPlaceholder: "模型 ID，或服务端 OPENAI_MODEL", effort: "推理强度", effortPlaceholder: "接入方默认，例如 max", modelHint: "填写该账号或接口支持的模型 ID 和推理强度。保存配置不代表模型权限已验证。",
      reasoningMode: "API 推理模式", defaultMode: "接口默认", standardMode: "Standard", proMode: "Pro · 仅限支持的模型",
      endpoint: "API 基础地址", env: "API Key 环境变量名", envHint: "这里只填变量名，不要填密钥。在启动 MathLottery 的终端中配置该变量的值，再重启服务。API 接入使用所选密钥，并按 API 计费。",
      tools: "托管工具", toolsOpenAI: "网络搜索 + 代码解释器", toolsNone: "不启用", toolsCustom: "保留已配置的工具", toolsHint: "使用其他兼容 Responses 的接口时，仅选择该接口支持的工具。",
      keyReady: "运行中的服务已设置此环境变量；尚未测试接口权限。", keyMissing: "运行中的服务尚未设置此环境变量。", saveKeyFirst: "先保存配置，再检查此环境变量是否已设置。",
      signIn: "使用 ChatGPT 登录", signOut: "退出登录", switchAccount: "切换账号", refresh: "刷新状态", cancel: "取消登录", copy: "复制验证码", copied: "已复制", open: "前往 OpenAI 登录 ↗",
      checking: "正在查询此槽位…", unconfirmed: "尚未检查登录状态。", signedOut: "尚未登录", connected: "已登录", unavailable: "无法确认账号状态", pending: "等待完成登录", saveFirst: "先保存配置，再管理此槽位的登录。",
      codeHint: "打开官方页面并输入一次性验证码。等待登录期间，状态会自动刷新。", invalidLink: "登录链接不是 OpenAI 官方 HTTPS 地址，请刷新此槽位后重试。",
      confirmSwitch: "切换这个槽位的 ChatGPT 账号？会先退出当前账号，其他槽位及本地 Codex 登录不受影响。",
      confirmLogout: "退出这个槽位的账号？其他槽位及本地 Codex 登录不受影响。", requestError: "无法连接本地 MathLottery 服务，请刷新后重试。",
      discard: "重新读取已保存的配置，并放弃未保存的修改？", reload: "重新读取已保存配置", countRange: "请选择 1 到 32 之间的整数。",
    },
  };
  let language;
  try { language = localStorage.getItem("mathlottery.language"); } catch { /* Optional preference. */ }
  language = language || (navigator.language.startsWith("zh") ? "zh" : "en");
  if (!words[language]) language = "en";
  const t = key => words[language][key] || key;
  const state = { slots: [], saved: [], cached: [], accounts: new Map(), keyConfigured: {}, csrf: "", busy: false, dirty: false };
  const defaultTools = () => [{ type: "web_search" }, { type: "code_interpreter", container: { type: "auto" } }];
  const clone = value => JSON.parse(JSON.stringify(value));
  const subscription = backend => backend?.mode === "codex" && (backend.codex_auth || "chatgpt") === "chatgpt";
  const keyEnv = backend => backend?.mode === "codex" ? backend.codex_api_key_env || "OPENAI_API_KEY" : backend?.chat?.api_key_env;

  async function request(path, body) {
    let response;
    try {
      response = await fetch(path, body === undefined ? { cache: "no-store" } : {
        method: "POST", headers: { "Content-Type": "application/json", "X-MathLottery-Token": state.csrf }, body: JSON.stringify(body),
      });
    } catch { throw new Error(t("requestError")); }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
  }

  function updateStatus() {
    text("#save-agents", t(state.busy ? "saving" : "save"));
    $("#save-agents").disabled = state.busy || !state.csrf;
    $("#agent-count").disabled = state.busy || !state.csrf;
    $$(".agent-card input, .agent-card select").forEach(item => { item.disabled = state.busy; });
    text("#save-status", t(state.busy ? "saving" : state.dirty ? "changed" : state.csrf ? "saved" : "loading"));
    for (const slot of state.slots) renderAccount(slot);
  }
  function changed() {
    state.dirty = true;
    notice("#page-error", "");
    updateStatus();
  }
  function field(parent, caption, control) {
    const wrap = node("div"), label = node("label", "", t(caption));
    label.htmlFor = control.id;
    wrap.append(label, control); parent.append(wrap); return wrap;
  }
  function input(slot, name, value, onInput, options = {}) {
    const item = node("input"); item.id = `${slot.id}-${name}`; item.value = value || "";
    Object.assign(item, { autocomplete: "off", spellcheck: false, maxLength: 200, ...options });
    item.addEventListener("input", () => { onInput(item.value); changed(); });
    return item;
  }
  function select(slot, name, entries, value, onChange) {
    const item = node("select"); item.id = `${slot.id}-${name}`;
    for (const [key, caption] of entries) { const option = node("option", "", t(caption)); option.value = key; item.append(option); }
    item.value = value;
    item.addEventListener("change", () => { onChange(item.value); changed(); }); return item;
  }
  function renderCards() {
    const list = $("#agent-cards"); list.replaceChildren();
    state.slots.forEach((slot, index) => {
      const backend = slot.backend;
      const card = node("article", "agent-card"); card.dataset.slotId = slot.id;
      const header = node("header"), identity = node("div");
      identity.append(node("h2", "", `${t("agent")} ${index + 1}`), node("p", "", slot.id));
      header.append(node("span", "agent-number", String(index + 1).padStart(2, "0")), identity);
      if (index === 0) header.append(node("span", "badge", t("primary")));
      card.append(header);
      field(card, "label", input(slot, "label", slot.label, value => { slot.label = value || null; }, { maxLength: 100 }));
      field(card, "connection", select(slot, "transport", [["codex", "codex"], ["chat", "responses"]], backend.mode, value => {
        backend.mode = value; backend.provider = null; backend.execution = "native";
        backend.codex_identity = value === "codex" ? slot.id : null;
        if (value === "chat") backend.chat ||= { api_key_env: "OPENAI_API_KEY", base_url: "https://api.openai.com/v1", tools: defaultTools() };
        renderCards();
      }));
      if (backend.mode === "codex") {
        field(card, "auth", select(slot, "auth", [["chatgpt", "chatgptAuth"], ["api_key", "apiAuth"]], backend.codex_auth || "chatgpt", value => {
          backend.codex_auth = value; backend.codex_api_key_env ||= "OPENAI_API_KEY";
          renderCards();
        }));
        if (!subscription(backend)) {
          field(card, "env", input(slot, "key-env", keyEnv(backend), value => { backend.codex_api_key_env = value.trim(); }, { required: true, maxLength: 128, pattern: "[A-Za-z_][A-Za-z0-9_]*", placeholder: "OPENAI_API_KEY" }));
          card.append(node("p", "agent-api-note", t("envHint")), node("p", "field-hint", t("codexApiHint")));
        }
      }
      const models = node("div", "fields-row");
      field(models, "model", input(slot, "model", backend.model, value => { backend.model = value.trim() || null; }, { placeholder: t(backend.mode === "chat" ? "apiModelPlaceholder" : "modelPlaceholder") }));
      const effort = input(slot, "effort", backend.reasoning_effort, value => { backend.reasoning_effort = value.trim() || null; }, { placeholder: t("effortPlaceholder"), maxLength: 50 });
      effort.setAttribute("list", "reasoning-values"); field(models, "effort", effort);
      card.append(models, node("p", "field-hint", t("modelHint")));
      if (backend.mode === "chat") {
        backend.chat ||= { api_key_env: "OPENAI_API_KEY", base_url: "https://api.openai.com/v1", tools: defaultTools() };
        field(card, "env", input(slot, "key-env", backend.chat.api_key_env, value => { backend.chat.api_key_env = value.trim(); backend.provider = null; }, { required: true, pattern: "[A-Za-z_][A-Za-z0-9_]*", placeholder: "OPENAI_API_KEY" }));
        card.append(node("p", "agent-api-note", t("envHint")));
        field(card, "endpoint", input(slot, "base-url", backend.chat.base_url, value => { backend.chat.base_url = value.trim(); backend.provider = null; }, { required: true, type: "url", maxLength: 2048, placeholder: "https://api.openai.com/v1" }));
        field(card, "reasoningMode", select(slot, "reasoning-mode", [["", "defaultMode"], ["standard", "standardMode"], ["pro", "proMode"]], backend.chat.reasoning_mode || "", value => { backend.chat.reasoning_mode = value || null; backend.provider = null; }));
        const configured = JSON.stringify(backend.chat.tools ?? defaultTools());
        const standard = configured === JSON.stringify(defaultTools());
        const entries = [["standard", "toolsOpenAI"], ["none", "toolsNone"]];
        if (!standard && backend.chat.tools?.length) entries.push(["custom", "toolsCustom"]);
        field(card, "tools", select(slot, "tools", entries, standard ? "standard" : backend.chat.tools?.length ? "custom" : "none", value => {
          if (value !== "custom") backend.chat.tools = value === "standard" ? defaultTools() : [];
          backend.provider = null;
        }));
        card.append(node("p", "field-hint", t("toolsHint")));
      }
      const account = node("div", "agent-account"); account.id = `${slot.id}-account`; card.append(account); list.append(card);
      renderAccount(slot);
    });
  }
  function renderAccount(slot) {
    // A status request can return after this card changes transport or is removed.
    slot = state.slots.find(item => item.id === slot.id);
    if (!slot) return;
    const panel = document.getElementById(`${slot.id}-account`); if (!panel) return;
    panel.replaceChildren();
    const saved = state.saved.find(item => item.id === slot.id);
    if (!subscription(slot.backend)) {
      const matching = saved?.backend.mode === slot.backend.mode && !subscription(saved.backend) && keyEnv(saved.backend) === keyEnv(slot.backend);
      if (matching && typeof state.keyConfigured[slot.id] === "boolean") panel.append(node("p", `agent-api-state${state.keyConfigured[slot.id] ? "" : " missing"}`, t(state.keyConfigured[slot.id] ? "keyReady" : "keyMissing")));
      else panel.append(node("p", "field-hint", t("saveKeyFirst")));
      return;
    }
    const account = state.accounts.get(slot.id) || {}, data = account.data;
    const connected = Boolean(data?.available && data.authenticated && ["chatgpt", "chatgptAuthTokens"].includes(data.account?.type));
    const pending = data?.login?.status === "pending" && !connected;
    const status = account.busy ? "checking" : !data ? "unconfirmed" : !data.available ? "unavailable" : connected ? "connected" : pending ? "pending" : "signedOut";
    let caption = t(status);
    if (connected && data.account.email) caption += ` · ${data.account.email}`;
    panel.append(node("p", "agent-account-status", caption));
    const actions = node("div", "account-actions");
    const unsaved = state.dirty || !subscription(saved?.backend);
    const buttons = connected ? [["switch", "switchAccount", "secondary"], ["logout", "signOut", "text-button danger"]] : [["login", "signIn", "secondary"]];
    buttons.push(["status", "refresh", "text-button"]);
    for (const [operation, caption, style] of buttons) {
      const button = node("button", style, t(caption)); button.type = "button"; button.dataset.action = operation;
      button.disabled = Boolean(account.busy || state.busy || !state.csrf || (operation === "status" ? !subscription(saved?.backend) : unsaved || (pending && operation === "login")));
      button.addEventListener("click", () => accountAction(slot, operation)); actions.append(button);
    }
    panel.append(actions);
    if (unsaved) panel.append(node("p", "field-hint", t("saveFirst")));
    if (pending) {
      const url = MathLotteryAccount.officialLoginUrl(data.login.url);
      if (!url) panel.append(node("p", "notice error", t("invalidLink")));
      else {
        const box = node("div", "agent-login"), code = node("code", "", data.login.user_code);
        box.append(node("p", "", t("codeHint")));
        const codeRow = node("div", "agent-login-code"), copy = node("button", "text-button", t("copy")); copy.type = "button";
        copy.addEventListener("click", async () => {
          try { await navigator.clipboard.writeText(code.textContent); copy.textContent = t("copied"); }
          catch { const range = document.createRange(); range.selectNodeContents(code); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); }
        });
        codeRow.append(code, copy); box.append(codeRow);
        const links = node("div", "agent-login-actions"), link = node("a", "account-link", t("open"));
        link.href = url; link.target = "_blank"; link.rel = "noopener noreferrer";
        const cancel = node("button", "text-button", t("cancel")); cancel.type = "button"; cancel.disabled = Boolean(account.busy || state.busy || unsaved);
        cancel.addEventListener("click", () => accountAction(slot, "cancel")); links.append(link, cancel); box.append(links); panel.append(box);
      }
    }
    const error = account.error || data?.error;
    if (error) { const warning = node("p", "notice error", error); warning.setAttribute("role", "alert"); panel.append(warning); }
  }
  async function accountAction(slot, action = "status") {
    if (!subscription(state.slots.find(item => item.id === slot.id)?.backend)) return;
    const account = state.accounts.get(slot.id) || { data: null, busy: false, error: "" };
    if (account.busy || state.busy) return;
    const change = ["switch", "logout"].includes(action);
    if (change && !window.confirm(t(action === "switch" ? "confirmSwitch" : "confirmLogout"))) return;
    account.busy = true; account.error = ""; state.accounts.set(slot.id, account); renderAccount(slot);
    const base = `/api/agents/${encodeURIComponent(slot.id)}/account`;
    try { account.data = await request(action === "status" ? base : `${base}/${action}`, action === "status" ? undefined : change ? { confirm_account_change: true } : {}); }
    catch (error) {
      account.error = error.message; account.data = null;
      if (action !== "status") { try { account.data = await request(base); } catch { /* Status is unknown. */ } }
    } finally { account.busy = false; renderAccount(slot); }
  }
  function newSlot() {
    const ids = new Set([...state.slots, ...state.cached].map(slot => slot.id));
    let number = 1; while (ids.has(`agent-${number}`)) number += 1;
    return { id: `agent-${number}`, label: null, backend: { mode: "codex", execution: "native", model: null, reasoning_effort: null, codex_identity: `agent-${number}` } };
  }
  function resize() {
    const count = Number($("#agent-count").value);
    if (!Number.isInteger(count) || count < 1 || count > 32) { notice("#page-error", t("countRange")); return; }
    if (count === state.slots.length) return;
    if (count < state.slots.length) state.cached.unshift(...state.slots.splice(count));
    while (state.slots.length < count) state.slots.push(state.cached.shift() || newSlot());
    changed(); renderCards();
  }
  async function load() {
    try {
      const data = await request("/api/agents");
      state.csrf = data.csrf_token || (await request("/api/bootstrap")).csrf_token;
      state.saved = clone(data.slots || []); state.slots = clone(state.saved); state.cached = []; state.accounts.clear();
      state.keyConfigured = data.key_configured || {};
      if (!state.slots.length) state.slots.push(newSlot());
      state.dirty = !state.saved.length;
      $("#agent-count").value = state.slots.length;
      notice("#page-error", ""); renderCards(); updateStatus();
      // Check sequentially so opening a long roster does not start 32 account processes at once.
      for (const slot of state.saved) if (subscription(slot.backend)) await accountAction(slot);
    } catch (error) { notice("#page-error", error.message); }
  }
  function translate() {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.title = `MathLottery · ${language === "zh" ? "Agent 配置" : "Agent setup"}`;
    $$('[data-text]').forEach(item => { item.textContent = t(item.dataset.text); });
    text("#language", language === "zh" ? "English" : "中文"); renderCards(); updateStatus();
  }
  $("#agent-count").addEventListener("input", resize);
  $("#agent-count").addEventListener("change", resize);
  $("#agents-form").addEventListener("submit", async event => {
    event.preventDefault(); if (state.busy) return;
    resize(); if (!$("#agents-form").reportValidity()) return;
    state.busy = true; updateStatus();
    // Preserve explicit metadata, but never accept account status or key material as configuration.
    const slots = state.slots.map(({ id, label, backend }) => ({ id, label, backend: clone(backend) }));
    try {
      const data = await request("/api/agents", { slots });
      state.saved = clone(data.slots || slots); state.slots = clone(state.saved); state.keyConfigured = data.key_configured || {};
      state.dirty = false; notice("#page-error", ""); renderCards();
    } catch (error) { notice("#page-error", error.message); }
    finally { state.busy = false; updateStatus(); }
  });
  $("#language").addEventListener("click", () => {
    language = language === "en" ? "zh" : "en";
    try { localStorage.setItem("mathlottery.language", language); } catch { /* Optional preference. */ }
    translate();
  });
  window.addEventListener("beforeunload", event => { if (state.dirty) { event.preventDefault(); event.returnValue = ""; } });
  setInterval(async () => {
    if (document.hidden || state.busy) return;
    for (const slot of state.slots) if (subscription(slot.backend) && state.accounts.get(slot.id)?.data?.login?.status === "pending") await accountAction(slot);
  }, 3000);
  translate(); void load();
})();
