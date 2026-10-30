/* MathLotteryModels: explicit component interfaces; no application-state globals. */
(function (root, factory) {
  "use strict";
  const common = typeof module === "object" && module.exports;
  const api = factory((common ? require("./dom.js") : root.MathLotteryDOM));
  if (common) module.exports = api;
  if (root) root.MathLotteryModels = api;
})(typeof window === "object" ? window : null, function (MathLotteryDOM) {
  "use strict";

  // The component owns selection and catalog races; callers own execution/configuration.
  // onChange re-renders the workflow form and its start/resume readiness.
  function create({ root, settings, translate: t, request, onChange }) {
    const { $, text, notice, options } = MathLotteryDOM.scope(root);
    const modelState = { providers: [], data: null, generation: 0, requestedProvider: "", loading: false, error: "", initialized: false };

    function configuredProvider() { return settings()?.provider || settings()?.backend || "codex"; }
    function selectedProvider() { return $("#backend").value || configuredProvider(); }
    function providers() {
      const entries = new Map([
        ["codex", { id: "codex", label: "Codex", transport: "codex", reasoning_modes: [] }],
        ["chat", { id: "chat", label: "OpenAI API", transport: "responses", reasoning_modes: [] }],
      ]);
      if (!entries.has(configuredProvider())) entries.set(configuredProvider(), { id: configuredProvider(), label: configuredProvider(), transport: settings()?.backend === "chat" ? "responses" : settings()?.backend, reasoning_modes: [] });
      for (const provider of modelState.providers) entries.set(provider.id, provider);
      return [...entries.values()];
    }
    function selectedProviderInfo() { return providers().find((provider) => provider.id === selectedProvider()); }
    function selectedBackend() { return selectedProviderInfo()?.transport === "responses" ? "chat" : selectedProviderInfo()?.transport || settings()?.backend; }
    function selectedCodexAuth() { return $("#codex-auth").value || settings()?.codex_auth || "chatgpt"; }
    function selectedCodexKeyEnv() { return $("#codex-key-env").value.trim() || settings()?.codex_api_key_env || "OPENAI_API_KEY"; }
    function selectedConnection() {
      const configured = settings() || {}, backend = selectedBackend();
      const same = selectedProvider() === configuredProvider();
      const auth = selectedCodexAuth(), env = selectedCodexKeyEnv();
      return {
        backend, codex_auth: auth, codex_api_key_env: env,
        api_key_env: backend === "codex" ? env : same ? configured.api_key_env : null,
        api_key_configured: same && (backend !== "codex" || (auth === (configured.codex_auth || "chatgpt") && env === (configured.codex_api_key_env || "OPENAI_API_KEY"))) ? configured.api_key_configured : undefined,
      };
    }
    function catalogKey() { return selectedBackend() === "codex" ? `${selectedProvider()}:${selectedCodexAuth()}:${selectedCodexKeyEnv()}` : selectedProvider(); }
    function selectedModelId() {
      const value = $("#model-select").value;
      if (value === "__manual") return $("#model").value.trim() || null;
      if (value === "__default") return null;
      return value || (selectedProvider() === configuredProvider() ? settings()?.model : null);
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
      if (selectedBackend() === "codex") {
        if ($("#codex-auth").value) values.codex_auth = selectedCodexAuth();
        if (selectedCodexAuth() === "api_key" && $("#codex-key-env").value.trim()) values.codex_api_key_env = selectedCodexKeyEnv();
      }
      return values;
    }
    function selectedReasoningModes() {
      // A missing metadata response means unknown capabilities, not an empty list.
      const metadata = modelState.data?.provider === selectedProvider() ? modelState.data.providers?.find((item) => item.id === selectedProvider()) : null;
      return Array.isArray(metadata?.reasoning_modes) ? metadata.reasoning_modes : null;
    }
    function modelCapabilityIssues() {
      const overrides = modelOverrides();
      const effort = Object.hasOwn(overrides, "reasoning_effort") ? overrides.reasoning_effort : settings()?.reasoning_effort;
      const mode = Object.hasOwn(overrides, "reasoning_mode") ? overrides.reasoning_mode : settings()?.reasoning_mode;
      const efforts = selectedModelInfo()?.reasoning_efforts, modes = selectedReasoningModes(), issues = [];
      if (effort && (!Array.isArray(efforts) || !efforts.includes(effort))) issues.push({ blocking: Array.isArray(efforts), message: t(Array.isArray(efforts) ? "unsupportedEffort" : "unconfirmedEffort").replace("{value}", effort) });
      if (selectedBackend() === "chat" && mode && (!modes || !modes.includes(mode))) issues.push({ blocking: Boolean(modes), message: t(modes ? "unsupportedMode" : "unconfirmedMode").replace("{value}", mode) });
      return issues;
    }
    function modelSelectionBlock() {
      if (selectedBackend() === "codex" && selectedCodexAuth() === "api_key" && !/^[A-Za-z_][A-Za-z0-9_]{0,127}$/.test(selectedCodexKeyEnv())) return t("apiEnvInvalid");
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
      const auth = ["codex", "work"].includes(backend) ? t(settings.codex_auth === "api_key" ? "codexApiAuthShort" : "codexChatGPTAuthShort") : "";
      return [provider, auth, settings.model || t("providerDefault"), `${t("effortLabel")}: ${settings.reasoning_effort || t("providerDefault")}`, showMode ? `${t("modeLabel")}: ${settings.reasoning_mode}` : ""].filter(Boolean).join(" · ");
    }
    function renderModelPreview() {
      if (!settings()) return;
      const overrides = modelOverrides();
      const selected = { provider: selectedProvider(), backend: selectedBackend(), codex_auth: selectedCodexAuth(), model: selectedModelId(), reasoning_effort: Object.hasOwn(overrides, "reasoning_effort") ? overrides.reasoning_effort : settings().reasoning_effort, reasoning_mode: Object.hasOwn(overrides, "reasoning_mode") ? overrides.reasoning_mode : settings().reasoning_mode };
      const summary = modelSummary(selected);
      text("#model-preview", summary);
    }
    function renderModels() {
      const provider = selectedProvider();
      options("#backend", providers().map((item) => [item.id, item.id === "codex" ? t("codexEngine") : item.id === "chat" ? t("responsesEngine") : item.label]), `${t("useConfig")} · ${configuredProvider()}`);
      const codex = selectedBackend() === "codex";
      options("#codex-auth", [["chatgpt", t("codexChatGPTAuth")], ["api_key", t("codexApiAuth")]], `${t("useConfig")} · ${t(settings()?.codex_auth === "api_key" ? "codexApiAuthShort" : "codexChatGPTAuthShort")}`);
      $("#codex-auth-fields").hidden = !codex;
      $("#codex-auth").disabled = !codex;
      $("#codex-key-field").hidden = !codex || selectedCodexAuth() !== "api_key";
      $("#codex-key-env").disabled = $("#codex-key-field").hidden;
      $("#codex-key-env").placeholder = settings()?.codex_api_key_env || "OPENAI_API_KEY";
      text("#codex-auth-hint", t(selectedCodexAuth() === "api_key" ? "codexApiHint" : "codexSubscriptionHint"));
      const catalog = modelState.data?.provider === provider ? modelState.data.models : [];
      const entries = [["__default", t("providerDefault")], ...catalog.map((model) => [model.id, model.label && model.label !== model.id ? `${model.label} · ${model.id}` : model.id])];
      const configuredModel = provider === configuredProvider() ? settings()?.model : null;
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
      options("#effort-select", effortEntries, `${t("useConfig")}${!$("#model-select").value && provider === configuredProvider() && settings()?.reasoning_effort ? ` · ${settings().reasoning_effort}` : ""}`);
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
      const inheritedMode = !previousMode && selectedBackend() === "chat" && settings()?.reasoning_mode;
      const showMode = Boolean(modes.length || inheritedMode || (previousMode && previousMode !== "__default"));
      $("#reasoning-mode-field").hidden = !showMode;
      $("#reasoning-mode").disabled = !showMode;
      const details = [model?.description, Array.isArray(efforts) ? (!efforts.length ? t("effortUnavailable") : "") : t("effortUnknown")].filter(Boolean).join(" ");
      text("#model-description", details); $("#model-description").hidden = !details;
      const source = modelState.data?.provider === provider ? modelState.data.source : null;
      text("#models-status", t(modelState.loading ? "modelsLoading" : !modelState.initialized ? "modelsIdle" : source === "live" ? "modelsLive" : source === "configured" ? "modelsConfigured" : "modelsUnavailable"));
      notice("#models-error", modelState.error);
      notice("#model-capability-warning", modelCapabilityIssues().map((issue) => issue.message).join("\n"));
      $("#models-refresh").disabled = modelState.loading || !settings();
      renderModelPreview();
    }
    async function loadModels(refreshCatalog = false) {
      if (!settings()) return;
      const provider = selectedProvider(), key = catalogKey(), generation = ++modelState.generation;
      modelState.initialized = true; modelState.requestedProvider = key; modelState.loading = true; modelState.error = "";
      if (modelState.data?.provider !== provider) modelState.data = null;
      renderModels();
      try {
        const authQuery = selectedBackend() === "codex" ? `&codex_auth=${encodeURIComponent(selectedCodexAuth())}&codex_api_key_env=${encodeURIComponent(selectedCodexKeyEnv())}` : "";
        const data = await request(`/api/models?provider=${encodeURIComponent(provider)}${authQuery}${refreshCatalog ? "&refresh=1" : ""}`);
        if (generation !== modelState.generation || key !== catalogKey()) return;
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
        if (generation !== modelState.generation || key !== catalogKey()) return;
        modelState.data = { provider, models: [], source: "unavailable" }; modelState.error = error.message;
      } finally {
        if (generation === modelState.generation) { modelState.loading = false; onChange(); }
      }
    }

    $("#backend").addEventListener("change", () => {
      $("#model-select").value = $("#backend").value ? "__default" : ""; $("#model").value = ""; $("#effort").value = "";
      $("#effort-select").value = $("#reasoning-mode").value = $("#backend").value ? "__default" : "";
      modelState.data = null; onChange(); void loadModels();
    });
    $("#model-select").addEventListener("change", () => {
      $("#model").value = "";
      if (!$("#model-select").value) { $("#effort-select").value = ""; $("#effort").value = ""; $("#reasoning-mode").value = ""; }
      else resetReasoningSelection();
      onChange();
    });
    $("#model").addEventListener("input", () => { resetReasoningSelection(); onChange(); });
    $("#effort-select").addEventListener("change", () => { $("#effort").value = ""; onChange(); });
    $("#effort").addEventListener("input", () => { onChange(); });
    $("#reasoning-mode").addEventListener("change", () => { onChange(); });
    $("#codex-auth").addEventListener("change", () => { modelState.data = null; onChange(); void loadModels(); });
    $("#codex-key-env").addEventListener("input", () => { onChange(); });
    $("#codex-key-env").addEventListener("change", () => { modelState.data = null; if (!modelSelectionBlock()) void loadModels(); });
    $("#models-refresh").addEventListener("click", () => loadModels(true));

    function ensureLoaded() {
      if (!modelState.initialized || modelState.requestedProvider !== catalogKey()) void loadModels();
    }
    return {
      provider: selectedProvider, backend: selectedBackend, connection: selectedConnection, overrides: modelOverrides,
      block: modelSelectionBlock, summary: modelSummary, render: renderModels,
      renderPreview: renderModelPreview, load: loadModels, ensureLoaded,
    };
  }
  return { create };

});
