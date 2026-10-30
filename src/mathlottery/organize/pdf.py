"""Offline, untrusted-Markdown report rendering with optional browser dependencies.

Only packaged KaTeX code is executed. Report HTML is escaped, images are replaced
by text, and Chromium cannot fetch report-supplied resources. PDF generation is
presentation, not verification of any mathematical statement.
"""

from __future__ import annotations

import base64
import hashlib
import html
import io
import os
import re
import tempfile
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MAX_MARKDOWN_BYTES = 4_000_000
MAX_FORMULAS = 2_000
MAX_FORMULA_CHARS = 20_000
SETUP_HELP = (
    'Install PDF support with: pip install -e ".[reports]"; '
    "then run: python -m playwright install chromium. "
    "On Linux, Chromium may also need system libraries "
    "(python -m playwright install-deps chromium) and a CJK font for Chinese reports."
)


class PDFRenderError(RuntimeError):
    """PDF rendering failed; the Markdown report can still be retained."""


_STYLE = """
@page { size: A4; margin: 20mm 18mm 21mm; }
* { box-sizing: border-box; }
body { color: #1c2925; font: 11pt/1.7 Georgia, "Noto Serif CJK SC",
  "Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", serif;
  overflow-wrap: anywhere; margin: 0; }
h1,h2,h3,h4,h5,h6 { line-height: 1.3; break-inside: avoid; break-after: avoid; color: #173c32; }
h1 { font-size: 24pt; border-bottom: 2px solid #286450; padding-bottom: 12pt; }
h2 { font-size: 15pt; margin-top: 23pt; }
h3 { font-size: 12pt; margin-top: 17pt; }
p,li { orphans: 3; widows: 3; }
a { color: #186653; text-decoration: underline; }
blockquote { margin: 14pt 0; padding: 2pt 12pt; border-left: 3px solid #b9ccc3;
  color: #485d54; }
code,pre { font-family: "DejaVu Sans Mono", "Noto Sans Mono CJK SC", monospace; }
code { font-size: 8.8pt; }
pre { border: 1px solid #d9e2dc; background: #f4f6f3; padding: 10pt;
  white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.45; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 14pt 0;
  table-layout: fixed; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
td,th { border: 1px solid #d5dfd8; padding: 6pt; vertical-align: top; }
th { text-align: left; background: #edf3ed; }
hr { border: 0; border-top: 1px solid #d5dfd8; margin: 20pt 0; }
.report-math[data-display="true"] { display: block; margin: 14pt 0;
  break-inside: avoid; text-align: center; }
.katex { font-size: 1.05em; }
.katex-display { margin: 0; max-width: 100%; }
.math-error { color: #9e3124; font-size: 9pt; white-space: pre-wrap; }
.report-warnings { border: 1px solid #c99b4f; padding: 10pt; background: #fff8e9;
  font-size: 9pt; margin-bottom: 18pt; }
.report-warnings strong { color: #7d4d04; }
.image-omitted { color: #64716b; font-style: italic; }
"""


def _closing_delimiter(source: str, closer: str, start: int) -> int:
    """Ignore delimiters preceded by an odd number of backslashes."""
    while (position := source.find(closer, start)) >= 0:
        slash_count = 0
        cursor = position - 1
        while cursor >= 0 and source[cursor] == "\\":
            slash_count += 1
            cursor -= 1
        if slash_count % 2 == 0:
            return position
        start = position + len(closer)
    return -1


def _math_inline(state: Any, silent: bool) -> bool:
    start = state.pos
    source = state.src
    if source.startswith("\\(", start):
        opener, closer, display = "\\(", "\\)", False
    elif source.startswith("\\[", start):
        opener, closer, display = "\\[", "\\]", True
    elif source.startswith("$$", start):
        opener, closer, display = "$$", "$$", True
    elif source.startswith("$", start):
        opener, closer, display = "$", "$", False
        if start + 1 >= len(source) or source[start + 1].isspace():
            return False
    else:
        return False
    end = _closing_delimiter(source, closer, start + len(opener))
    if end < 0:
        if opener != "$" and not silent:
            state.env["warnings"].append("An unclosed math delimiter remains as source text.")
        return False
    content = source[start + len(opener):end]
    if not content or (opener == "$" and content[-1].isspace()):
        return False
    if not silent:
        token = state.push("report_math", "", 0)
        token.content = content
        token.meta = {"display": display}
    state.pos = end + len(closer)
    return True


def _math_block(state: Any, start: int, end: int, silent: bool) -> bool:
    position = state.bMarks[start] + state.tShift[start]
    line = state.src[position:state.eMarks[start]]
    if state.sCount[start] - state.blkIndent >= 4:
        return False
    if line.startswith("$$"):
        opener, closer = "$$", "$$"
    elif line.startswith("\\["):
        opener, closer = "\\[", "\\]"
    else:
        return False
    if silent:
        return True
    parts = [line[len(opener):]]
    characters = len(parts[0])
    next_line = start + 1
    while True:
        if characters > MAX_FORMULA_CHARS:
            raise PDFRenderError("The report exceeds the PDF formula size/count limit.")
        close = _closing_delimiter(parts[-1], closer, 0)
        if close >= 0:
            # Text after the delimiter belongs to ordinary inline Markdown.
            if parts[-1][close + len(closer):].strip():
                return False
            parts[-1] = parts[-1][:close]
            break
        if next_line >= end:
            state.env["warnings"].append("An unclosed display formula remains as source text.")
            return False
        parts.append(state.src[state.bMarks[next_line]:state.eMarks[next_line]])
        characters += len(parts[-1]) + 1
        next_line += 1
    token = state.push("report_math", "", 0)
    token.block = True
    token.content = "\n".join(parts).strip()
    token.meta = {"display": True}
    token.map = [start, next_line]
    state.line = next_line
    return True


def _comment_inline(state: Any, silent: bool) -> bool:
    """Hide complete Markdown comments, never enable arbitrary HTML."""
    if not state.src.startswith("<!--", state.pos):
        return False
    close = state.src.find("-->", state.pos + 4)
    if close < 0:
        return False
    state.pos = close + 3
    return True


def _comment_block(state: Any, start: int, end: int, silent: bool) -> bool:
    # Code fences and indented code retain comments as literal source examples.
    if state.sCount[start] - state.blkIndent >= 4:
        return False
    position = state.bMarks[start] + state.tShift[start]
    if not state.src.startswith("<!--", position):
        return False
    close = state.src.find("-->", position + 4)
    if close < 0:
        return False
    next_line = start
    while next_line < end and state.eMarks[next_line] < close + 3:
        next_line += 1
    if next_line >= end or state.src[close + 3:state.eMarks[next_line]].strip():
        return False
    if not silent:
        state.line = next_line + 1
    return True


def _render_html(markdown: str, title: str) -> tuple[str, list[str], int]:
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise PDFRenderError(SETUP_HELP) from exc
    warnings: list[str] = []
    context: dict[str, Any] = {"warnings": warnings, "formulas": 0, "links": []}
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table")
    parser.inline.ruler.before("html_inline", "report_comment", _comment_inline)
    parser.block.ruler.before("paragraph", "report_comment", _comment_block,
                              {"alt": ["paragraph", "reference", "blockquote", "list"]})
    parser.inline.ruler.before("escape", "report_math", _math_inline)
    parser.block.ruler.before(
        "fence", "report_math", _math_block,
        {"alt": ["paragraph", "reference", "blockquote", "list"]},
    )

    def math_token(tokens: Any, index: int, options: Any, env: dict[str, Any]) -> str:
        token = tokens[index]
        env["formulas"] += 1
        if env["formulas"] > MAX_FORMULAS or len(token.content) > MAX_FORMULA_CHARS:
            raise PDFRenderError("The report exceeds the PDF formula size/count limit.")
        display = "true" if token.meta["display"] else "false"
        tag = "div" if token.block else "span"
        return (
            f'<{tag} class="report-math" data-display="{display}">'
            f"{html.escape(token.content)}</{tag}>"
        )

    def image_token(tokens: Any, index: int, options: Any, env: dict[str, Any]) -> str:
        env["warnings"].append("Images are omitted; inspect the attached source materials.")
        description = tokens[index].content or "image"
        return f'<span class="image-omitted">[Image omitted: {html.escape(description)}]</span>'

    def link_open(tokens: Any, index: int, options: Any, env: dict[str, Any]) -> str:
        href = tokens[index].attrGet("href") or ""
        safe = urlsplit(href).scheme.lower() in {"http", "https", "mailto"} or href.startswith("#")
        env["links"].append(safe)
        if not safe:
            return "<span>"
        return f'<a href="{html.escape(href, quote=True)}" rel="noreferrer">'

    def link_close(tokens: Any, index: int, options: Any, env: dict[str, Any]) -> str:
        return "</a>" if env["links"].pop() else "</span>"

    parser.renderer.rules.update({
        "report_math": math_token, "image": image_token,
        "link_open": link_open, "link_close": link_close,
    })
    tokens = parser.parse(markdown, context)
    # Portable heading anchors make the reading guide usable in the PDF too.
    # IDs are derived from text, never accepted as raw HTML attributes.
    heading_ids: set[str] = set()
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open":
            continue
        slug = re.sub(r"[^\w -]", "", tokens[index + 1].content.lower()).replace(" ", "-")[:160] or "section"
        anchor, suffix = slug, 1
        while anchor in heading_ids:
            anchor, suffix = f"{slug}-{suffix}", suffix + 1
        heading_ids.add(anchor)
        token.attrSet("id", anchor)
    for token in tokens:
        for child in token.children or []:
            if child.type == "text" and re.search(
                r"\\(?:begin|end)\{(?:equation|align|aligned|gather|multline|split)\*?\}"
                r"|\\(?:frac|dfrac|sum|prod|sqrt|int|lim)\b", child.content,
            ):
                warnings.append(
                    "Possible TeX outside math delimiters remains as text; "
                    "use $...$, $$...$$, \\( ... \\), or \\[ ... \\]."
                )
    body = parser.renderer.render(tokens, parser.options, context)
    # Content has no HTML execution path; CSP is additional protection. The only
    # evaluated script is our packaged KaTeX, passed separately to Playwright.
    csp = (
        "default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; "
        "font-src data:; img-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'"
    )
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
        f"<title>{html.escape(title)}</title><style>{_STYLE}</style>"
        f"</head><body><main>{body}</main></body></html>"
    )
    return document, list(dict.fromkeys(warnings)), context["formulas"]


def _katex_assets() -> tuple[str, str]:
    assets = files("mathlottery.organize").joinpath("assets", "katex")
    try:
        script = assets.joinpath("katex.min.js").read_text(encoding="utf-8")
        css = assets.joinpath("katex.min.css").read_text(encoding="utf-8")

        def embed_font(match: re.Match[str]) -> str:
            name = match.group(1)
            data = assets.joinpath("fonts", name).read_bytes()
            encoded = base64.b64encode(data).decode("ascii")
            return f'src:url(data:font/woff2;base64,{encoded}) format("woff2")'

        css = re.sub(r"src:url\(fonts/([^/()]+\.woff2)\)[^}]+", embed_font, css)
    except (OSError, ValueError) as exc:
        raise PDFRenderError("Packaged PDF math assets are missing; reinstall MathLottery.") from exc
    return script, css


_RENDER_MATH = r"""() => {
  const warnings = [];
  document.querySelectorAll('.report-math').forEach((element, index) => {
    const source = element.textContent;
    try {
      if (/\\(?:includegraphics|href|url|html\w+)\b/.test(source)) {
        throw new Error('External resources and HTML/link commands are disabled in formulas');
      }
      katex.render(source, element, {
        displayMode: element.dataset.display === 'true', throwOnError: true,
        trust: false, maxExpand: 1000, maxSize: 20, output: 'htmlAndMathml',
        strict: (code) => { warnings.push(`Formula ${index + 1}: KaTeX warning (${code}).`); return 'ignore'; },
      });
    } catch (error) {
      element.classList.add('math-error');
      element.textContent = `[Formula ${index + 1} could not be typeset] ${source}`;
      warnings.push(`Formula ${index + 1} could not be typeset; inspect the Markdown source.`);
    }
  });
  return warnings;
}"""

_LAYOUT_MATH = """async () => {
  await document.fonts.ready;
  const warnings = [];
  document.querySelectorAll('.report-math[data-display="true"]').forEach((element, index) => {
    const formula = element.querySelector('.katex');
    if (!formula) return;
    const content = formula.getBoundingClientRect().width;
    const available = element.getBoundingClientRect().width;
    if (content > available) {
      const factor = Math.max(0.6, available / content);
      element.style.fontSize = `${parseFloat(getComputedStyle(element).fontSize) * factor}px`;
      if (content * factor > available + 1) {
        warnings.push(`Display formula ${index + 1} is wider than the page; split it in the Markdown source.`);
      }
    }
  });
  return warnings;
}"""


def _pdf_bytes(document: str, warnings: list[str], title: str) -> tuple[bytes, list[str]]:
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError as exc:
        raise PDFRenderError(SETUP_HELP) from exc
    script, css = _katex_assets()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, timeout=30_000)
            try:
                context = browser.new_context(
                    service_workers="block", accept_downloads=False, offline=True,
                    viewport={"width": 658, "height": 900},
                )
                context.route("**/*", lambda route: route.abort())
                page = context.new_page()
                page.set_default_timeout(30_000)
                page.set_content(document, wait_until="load")
                page.add_style_tag(content=css)
                page.evaluate(script)
                warnings.extend(page.evaluate(_RENDER_MATH))
                warnings.extend(page.evaluate(_LAYOUT_MATH))
                warnings = list(dict.fromkeys(warnings))
                if warnings:
                    page.evaluate("""warnings => {
                      const notice = document.createElement('aside');
                      notice.className = 'report-warnings';
                      const title = document.createElement('strong');
                      title.textContent = 'PDF rendering notes / 排版提示';
                      notice.appendChild(title);
                      const list = document.createElement('ul');
                      for (const warning of warnings) {
                        const item = document.createElement('li');
                        item.textContent = warning; list.appendChild(item);
                      }
                      notice.appendChild(list); document.body.prepend(notice);
                    }""", warnings)
                footer = (
                    '<div style="font:8px sans-serif;width:100%;text-align:center;color:#637168">'
                    f'{html.escape(title[:90])} · <span class="pageNumber"></span>'
                    ' / <span class="totalPages"></span></div>'
                )
                result = page.pdf(
                    format="A4", print_background=True, prefer_css_page_size=True,
                    display_header_footer=True, header_template="<span></span>",
                    footer_template=footer, tagged=True, outline=True,
                )
                return result, warnings
            finally:
                browser.close()
    except Error as exc:
        raise PDFRenderError(f"Chromium could not render the PDF. {SETUP_HELP}") from exc


def render_pdf(markdown: str, destination: Path, *, title: str = "MathLottery") -> dict[str, Any]:
    """Write a real PDF atomically and return page count, digest and layout warnings.

    The caller owns output-directory confinement. Existing destination symlinks
    are rejected; renderer failures leave an existing destination untouched.
    Runtime browser downloads and untrusted external resources are never used.
    """
    if not markdown.strip():
        raise PDFRenderError("Cannot render an empty Markdown report.")
    if len(markdown.encode("utf-8")) > MAX_MARKDOWN_BYTES:
        raise PDFRenderError("The Markdown report exceeds the 4 MB PDF rendering limit.")
    destination = Path(destination)
    if destination.is_symlink():
        raise PDFRenderError("The PDF destination must not be a symbolic link.")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise PDFRenderError(SETUP_HELP) from exc
    document, warnings, formula_count = _render_html(markdown, title)
    payload, warnings = _pdf_bytes(document, warnings, title)
    try:
        reader = PdfReader(io.BytesIO(payload), strict=True)
        page_count = len(reader.pages)
        if not payload.startswith(b"%PDF-") or not page_count:
            raise ValueError("Empty PDF")
    except Exception as exc:
        raise PDFRenderError("The renderer did not produce a valid, nonempty PDF.") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".pdf", delete=False) as out:
            temporary = out.name
            out.write(payload)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return {
        "filename": destination.name,
        "pages": page_count,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "renderer": "chromium+katex-0.19.0",
        "formula_count": formula_count,
        "warnings": warnings,
    }
