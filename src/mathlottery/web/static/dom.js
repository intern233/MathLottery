/* Small DOM primitives; no application state, network access, or HTML insertion. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MathLotteryDOM = api;
})(typeof window === "object" ? window : null, function () {
  "use strict";

  function scope(root) {
    const document = root.ownerDocument || root;
    const $ = selector => root.matches?.(selector) ? root : root.querySelector(selector);
    const $$ = selector => [...root.querySelectorAll(selector)];
    function node(tag, className, text) {
      const item = document.createElement(tag);
      if (className) item.className = className;
      if (text != null) item.textContent = text;
      return item;
    }
    function text(selector, value) {
      const item = $(selector);
      if (item.textContent !== String(value)) item.textContent = value;
    }
    function notice(selector, value) {
      text(selector, value || "");
      $(selector).hidden = !value;
    }
    function options(selector, entries, emptyLabel) {
      const select = $(selector), previous = select.value;
      const all = [["", emptyLabel], ...entries];
      const signature = JSON.stringify(all);
      if (select.dataset.options === signature) return;
      select.replaceChildren(...all.map(([value, label]) => {
        const option = node("option", "", label);
        option.value = value;
        return option;
      }));
      select.value = all.some(([value]) => value === previous) ? previous : "";
      select.dataset.options = signature;
    }
    return { $, $$, node, text, notice, options };
  }

  return { scope };
});
