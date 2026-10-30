/* New-task roster selection; saved runs keep their own immutable connection snapshot. */
(function (root) {
  "use strict";
  function create({ root, workflow, language, request, onChange }) {
    const { $, text, notice } = MathLotteryDOM.scope(root);
    const state = { slots: [], loading: false, loaded: false, error: "" };
    const words = {
      en: { title: "Connections for parallel agents", use: "Use configured agent slots", configure: "Configure agents ↗", refresh: "Refresh", loading: "Loading agent configuration…", empty: "Configure and save at least one agent slot first.", summary: "{n} configured slots. Each uses its own model and connection; slot 1 also handles supervision and wrap-up.", hint: "Choose Codex with ChatGPT sign-in or an API key, or a separate Responses API agent. Existing tasks retain their saved configuration." },
      zh: { title: "并行 agent 的接入配置", use: "使用已配置的 agent 槽位", configure: "配置 agent ↗", refresh: "刷新", loading: "正在读取 agent 配置…", empty: "请先配置并保存至少一个 agent 槽位。", summary: "已配置 {n} 个槽位，各自使用独立的模型与接入方式；第 1 个还兼任监督和收尾。", hint: "分别配置 Codex 的 ChatGPT 登录或 API Key，或独立的 Responses API agent。已有任务保留启动时的配置。" },
    };
    const t = key => words[language() === "zh" ? "zh" : "en"][key];
    const enabled = () => workflow() === "solve" && $("#use-agent-slots").checked;
    function block() {
      if (!enabled()) return "";
      return state.loading || !state.loaded ? t("loading") : state.error || (!state.slots.length ? t("empty") : "");
    }
    function render() {
      root.hidden = workflow() !== "solve";
      text("#agent-slots-title", t("title")); text("#use-agent-slots-label", t("use"));
      text("#configure-agent-slots", t("configure")); text("#refresh-agent-slots", t("refresh"));
      text("#agent-slots-summary", state.loaded && state.slots.length ? t("summary").replace("{n}", state.slots.length) : t("hint"));
      notice("#agent-slots-error", enabled() ? block() : "");
      $("#refresh-agent-slots").disabled = state.loading;
    }
    async function refresh() {
      if (state.loading) return;
      state.loading = true; render(); onChange();
      try { const data = await request("/api/agents"); state.slots = Array.isArray(data.slots) ? data.slots : []; state.error = ""; state.loaded = true; }
      catch (error) { state.error = error.message; state.loaded = true; }
      finally { state.loading = false; render(); onChange(); }
    }
    $("#use-agent-slots").addEventListener("change", () => { render(); onChange(); if (enabled()) void refresh(); });
    $("#refresh-agent-slots").addEventListener("click", refresh);
    return { enabled, block, render, refresh, get count() { return state.slots.length; } };
  }
  root.MathLotteryAgentSlots = { create };
})(window);
