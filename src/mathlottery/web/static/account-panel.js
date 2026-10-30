/* MathLotteryAccount: explicit component interfaces; no application-state globals. */
(function (root, factory) {
  "use strict";
  const common = typeof module === "object" && module.exports;
  const api = factory((common ? require("./dom.js") : root.MathLotteryDOM));
  if (common) module.exports = api;
  if (root) root.MathLotteryAccount = api;
})(typeof window === "object" ? window : null, function (MathLotteryDOM) {
  "use strict";

  function officialLoginUrl(value) {
    try {
      const url = new URL(value);
      if (url.protocol === "https:" && ["auth.openai.com", "chatgpt.com"].includes(url.hostname) && !url.username && !url.password && !url.port) return url.href;
    } catch { /* Only official HTTPS login URLs are clickable. */ }
    return null;
  }

  // Login/account state never leaves this component or enters persistent UI storage.
  // request is the workspace-scoped HTTP client; render(ready) receives CSRF readiness.
  function create({ root, translate: t, request, onChange, notify, connection, reloadConnection }) {
    const { $, text, notice } = MathLotteryDOM.scope(root);
    const document = root.ownerDocument || root, window = document.defaultView;
    const navigator = window.navigator;
    const accountState = { data: null, busy: false, operation: "status", error: "" };
    let ready = false;
    let attempted = false;
    let subscriptionView = false;
    const apiConnection = route => route && (route.backend === "chat" || (["codex", "work"].includes(route.backend) && route.codex_auth === "api_key"));

    function executionBlock(backend, route = connection?.()) {
      if (!["codex", "work"].includes(backend)) return "";
      if (route?.codex_auth === "api_key") return ""; // Selected environment is checked by server admission.
      const data = accountState.data;
      if (accountState.busy) return t("readinessChecking");
      if (!data) return t(accountState.error ? "readinessUnknown" : "readinessChecking");
      if (!data.available) return t(["ACCOUNT_TIMEOUT", "NETWORK_CONFIG_INVALID"].includes(data.error_code) ? "readinessUnknown" : "readinessUnavailable");
      if (data.authenticated && ["chatgpt", "chatgptAuthTokens"].includes(data.account?.type)) return "";
      if (data.account?.type === "apiKey") return t("readinessApiKey");
      return t(data.login?.status === "pending" ? "readinessPending" : "readinessSignIn");
    }

    function renderAccount(canMutate = ready) {
      ready = canMutate;
      const route = connection?.();
      $("#account-resume-context").hidden = !subscriptionView;
      if (apiConnection(route) && !subscriptionView) {
        text("#account-title", t(route.backend === "chat" ? "accountApiAgentTitle" : "accountCodexApiTitle"));
        text("#account-status", t(route.api_key_configured === true ? "apiKeyConfigured" : route.api_key_configured === false ? "apiKeyMissing" : "apiKeyUnchecked"));
        const env = route.backend === "chat" ? route.api_key_env : route.codex_api_key_env;
        text("#account-details", env ? `${t("apiKeyEnv")}: ${env}` : "");
        $("#account-details").hidden = !env;
        ["#account-login", "#account-switch", "#account-logout", "#account-pending"].forEach(selector => { $(selector).hidden = true; });
        $("#account-refresh").disabled = !ready;
        $("#account-panel").setAttribute("aria-busy", false);
        text("#account-code", ""); $("#account-link").removeAttribute("href");
        notice("#account-error", "");
        if ($("#account-note")) text("#account-note", t("accountApiNote"));
        onChange();
        return;
      }
      text("#account-title", t("accountTitle"));
      if ($("#account-note")) text("#account-note", t("accountNote"));
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
      $("#account-login").disabled = accountState.busy || !data?.available || !ready;
      ["#account-switch", "#account-logout"].forEach((selector) => {
        $(selector).hidden = !connected;
        $(selector).disabled = accountState.busy || !ready;
      });
      $("#account-refresh").disabled = accountState.busy;
      $("#account-panel").setAttribute("aria-busy", accountState.busy);
      const url = pending ? officialLoginUrl(data.login.url) : null;
      const code = pending && typeof data.login.user_code === "string" ? data.login.user_code.slice(0, 64) : "";
      $("#account-pending").hidden = !pending;
      text("#account-code", url ? code : "");
      $("#account-copy").disabled = !url || !code;
      $("#account-cancel").disabled = accountState.busy || !ready;
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
      onChange();
    }
    async function refreshAccount(operation = "status", forceSubscription = false) {
      const route = connection?.();
      if (connection && !route) return;
      if (apiConnection(route) && !subscriptionView && !forceSubscription) {
        if (operation === "status" && reloadConnection) await reloadConnection();
        renderAccount();
        return;
      }
      if (accountState.busy) return;
      attempted = true;
      const accountChange = ["switch", "logout"].includes(operation);
      if (accountChange && !window.confirm(t(operation === "switch" ? "accountConfirmSwitch" : "accountConfirmLogout"))) return;
      accountState.busy = true; accountState.operation = operation; accountState.error = ""; renderAccount();
      try { accountState.data = await request(operation === "status" ? "/api/account" : `/api/account/${operation}`, operation === "status" ? undefined : accountChange ? { confirm_account_change: true } : {}); }
      catch (error) {
        accountState.error = error.message;
        accountState.data = null;
        // A failed mutation may still have signed out. Re-read without hiding its error.
        if (operation !== "status") {
          try { accountState.data = await request("/api/account"); }
          catch { /* Unknown state must not look like the previous connected account. */ }
        }
      }
      finally { accountState.busy = false; renderAccount(); }
    }

    $("#account-login").addEventListener("click", () => refreshAccount("login"));
    $("#account-switch").addEventListener("click", () => refreshAccount("switch"));
    $("#account-logout").addEventListener("click", () => refreshAccount("logout"));
    $("#account-refresh").addEventListener("click", () => refreshAccount());
    $("#account-cancel").addEventListener("click", () => refreshAccount("cancel"));
    $("#account-follow-selection").addEventListener("click", () => { subscriptionView = false; renderAccount(); });
    $("#account-copy").addEventListener("click", async () => {
      const value = $("#account-code").textContent;
      if (!value) return;
      try { await navigator.clipboard.writeText(value); notify(t("accountCopied")); }
      catch { const range = document.createRange(); range.selectNodeContents($("#account-code")); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); notify(t("accountSelectCode")); }
    });

    return {
      render: renderAccount, refresh: refreshAccount, block: executionBlock,
      openSubscription() {
        subscriptionView = true;
        renderAccount();
        $("#account-panel").open = true;
        $("#account-panel").scrollIntoView({ behavior: "smooth", block: "center" });
        void refreshAccount("status", true);
      },
      ensureLoaded(forceSubscription = false) {
        const route = connection?.();
        if ((connection && !route) || (apiConnection(route) && !forceSubscription)) return;
        if (!attempted && !accountState.busy) void refreshAccount("status", forceSubscription);
      },
      get pending() { return (subscriptionView || !apiConnection(connection?.())) && accountState.data?.login?.status === "pending"; },
    };
  }
  return { create, officialLoginUrl };

});
