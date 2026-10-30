from __future__ import annotations

import io
import re
from pathlib import Path
from urllib.parse import unquote

import pytest
from bs4 import BeautifulSoup

from mathlottery.organize import pdf as report_pdf


def test_math_delimiters_keep_equations_and_do_not_touch_code():
    source = r"""# Proof

Let $x^2$ and \(y+1\) be given; an escaped \$ is text.

$$
\sum_{k=1}^n k = \frac{n(n+1)}{2}
$$

\[x+y=2\]

```python
value = '$not math$'
```

`\(not math\)`

| Claim | Status |
| --- | --- |
| $x=1$ | conditional |
"""
    document, warnings, count = report_pdf._render_html(source, "Proof")
    soup = BeautifulSoup(document, "html.parser")
    formulas = soup.select(".report-math")
    assert count == len(formulas) == 5
    assert formulas[2].get_text() == r"\sum_{k=1}^n k = \frac{n(n+1)}{2}"
    assert len(soup.select('[data-display="true"]')) == 2
    assert "'$not math$'" in soup.pre.get_text()
    assert len(soup.select("table")) == 1
    assert warnings == []


def test_untrusted_html_links_images_and_tex_stay_inert():
    source = r"""# <img src=x onerror=alert(1)>

<script>fetch('https://example.invalid/secret')</script>

![Diagram](file:///etc/passwd)
![Remote](https://example.invalid/pixel.svg)

[Local](../private.txt) [Web](https://example.org/paper)

$\text{</span><script>alert(1)</script>}$
"""
    document, warnings, count = report_pdf._render_html(source, '</title><script>bad()</script>')
    soup = BeautifulSoup(document, "html.parser")
    assert soup.select("script,img,iframe,object,embed") == []
    assert [link["href"] for link in soup.select("a")] == ["https://example.org/paper"]
    assert len(soup.select(".image-omitted")) == 1  # file: URLs are rejected by MarkdownIt.
    assert count == 1
    assert "<script>alert(1)</script>" in soup.select_one(".report-math").get_text()
    assert any("Images are omitted" in warning for warning in warnings)
    assert "default-src 'none'" in soup.select_one('meta[http-equiv]')["content"]


def test_math_assets_are_packaged_offline_and_have_a_license():
    script, css = report_pdf._katex_assets()
    assert len(script) > 100_000
    urls = re.findall(r"url\(([^)]+)\)", css)
    assert urls and all(url.startswith("data:font/woff2;base64,") for url in urls)
    assets = report_pdf.files("mathlottery.organize").joinpath("assets", "katex")
    assert "Permission is hereby granted" in assets.joinpath("LICENSE").read_text()


def test_reading_guide_links_have_unique_safe_heading_targets():
    source = '''[Read the proof](#full-editorial-report) [完整推导](#完整整理报告)

## Full editorial report
## Full editorial report
## Full editorial report-1
## 完整整理报告
## <img src=x onerror=alert(1)>
'''
    document, _, _ = report_pdf._render_html(source, "Guide")
    soup = BeautifulSoup(document, "html.parser")
    ids = [heading["id"] for heading in soup.select("h2")]
    assert len(ids) == len(set(ids))
    for link in soup.select("a"):
        assert soup.find(id=unquote(link["href"][1:])) is not None
    assert soup.select("img,script,[onerror]") == []


def test_unclosed_formula_is_reported():
    document, warnings, count = report_pdf._render_html(r"Proof \(x^2", "Proof")
    assert count == 0
    assert "x^2" in document
    assert any("unclosed" in warning for warning in warnings)


def test_html_comments_are_hidden_outside_code_without_enabling_html():
    source = '''# Proof

<!-- internal theorem marker $not math$

still internal -->

Visible <!-- inline marker --> conclusion $x=1$.

`<!-- inline code -->`

```lean
-- <!-- fenced code -->
```

    <!-- indented code -->

<script>unsafe()</script>
'''
    document, warnings, count = report_pdf._render_html(source, "Proof")
    soup = BeautifulSoup(document, "html.parser")
    assert "internal theorem marker" not in soup.get_text()
    assert "inline marker" not in soup.get_text()
    assert "inline code" in soup.get_text() and "fenced code" in soup.get_text()
    assert "indented code" in soup.get_text()
    assert "<script>unsafe()</script>" in soup.get_text()
    assert not soup.select("script") and count == 1 and not warnings


def test_raw_tex_without_math_delimiters_is_reported_but_code_is_not():
    source = r"""\begin{align} x &= \frac{1}{2} \end{align}

`\frac{1}{2}`
"""
    _, warnings, count = report_pdf._render_html(source, "Proof")
    assert count == 0
    assert len(warnings) == 1
    assert "outside math delimiters" in warnings[0]


def test_render_failure_does_not_overwrite_an_existing_pdf(tmp_path, monkeypatch):
    pytest.importorskip("pypdf")
    target = tmp_path / "report.pdf"
    target.write_bytes(b"previous version")
    monkeypatch.setattr(report_pdf, "_pdf_bytes", lambda *args: (b"not a PDF", []))
    with pytest.raises(report_pdf.PDFRenderError, match="valid, nonempty PDF"):
        report_pdf.render_pdf("# Proof", target)
    assert target.read_bytes() == b"previous version"
    assert list(tmp_path.iterdir()) == [target]


def test_symlinks_empty_reports_and_oversized_reports_are_rejected(tmp_path):
    original = tmp_path / "original.pdf"
    original.write_bytes(b"keep")
    link = tmp_path / "report.pdf"
    link.symlink_to(original)
    with pytest.raises(report_pdf.PDFRenderError, match="symbolic link"):
        report_pdf.render_pdf("Proof", link)
    assert original.read_bytes() == b"keep"
    with pytest.raises(report_pdf.PDFRenderError, match="empty"):
        report_pdf.render_pdf(" ", tmp_path / "empty.pdf")
    with pytest.raises(report_pdf.PDFRenderError, match="4 MB"):
        report_pdf.render_pdf("a" * (report_pdf.MAX_MARKDOWN_BYTES + 1), tmp_path / "big.pdf")


@pytest.fixture
def browser_ready():
    api = pytest.importorskip("playwright.sync_api")
    pytest.importorskip("pypdf")
    with api.sync_playwright() as driver:
        if not Path(driver.chromium.executable_path).is_file():
            pytest.skip("Optional Chromium browser is not installed")
        try:
            browser = driver.chromium.launch(headless=True)
        except api.Error:
            pytest.skip("Optional Chromium runtime dependencies are unavailable")
        browser.close()


def test_real_pdf_contains_readable_cjk_math_and_pages(tmp_path, browser_ready):
    from pypdf import PdfReader

    source = r"""# 数学证明报告

## 精确命题

对于每个自然数 $n$，奇数和满足

$$\sum_{k=1}^{n} (2k-1) = n^2.$$

归纳步骤为 \(n^2+(2n+1)=(n+1)^2\)。

| 证据 | 状态 |
| --- | --- |
| 新颖性 | 已知结果 |

```lean
example (n : Nat) : n + 0 = n := by omega
```
"""
    target = tmp_path / "expert-report.pdf"
    result = report_pdf.render_pdf(source, target, title="MathLottery proof report")
    reader = PdfReader(io.BytesIO(target.read_bytes()))
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert result["pages"] == len(reader.pages) >= 1
    assert result["formula_count"] == 3
    assert result["warnings"] == []
    assert result["bytes"] == target.stat().st_size
    assert "数学证明报告" in text
    assert "精确命题" in text
    assert "example" in text
    assert r"\sum" not in text  # Equations were typeset, not printed as raw TeX.
    assert len(result["sha256"]) == 64
    assert result["filename"] == target.name


def test_pdf_reading_guide_navigation_is_an_internal_destination(tmp_path, browser_ready):
    from pypdf import PdfReader

    target = tmp_path / "navigation.pdf"
    source = "[Skip to the proof](#full-editorial-report)\n\n"
    source += "\n\n".join(["Evidence index with unchanged frozen source references. " * 9] * 12)
    source += "\n\n## Full editorial report\n\nThe complete proof starts here.\n"
    report_pdf.render_pdf(source, target)
    reader = PdfReader(target)
    assert len(reader.pages) >= 2
    links = [item.get_object() for item in reader.pages[0].get("/Annots", [])]
    assert any("/Dest" in link or link.get("/A", {}).get("/S") == "/GoTo" for link in links)
    assert not any(link.get("/A", {}).get("/S") == "/URI" for link in links)


def test_bad_tex_and_external_resources_are_visible_pdf_warnings(tmp_path, browser_ready):
    from pypdf import PdfReader

    target = tmp_path / "warnings.pdf"
    source = r"""# Test

$\unknownMathCommand{x}$

$\includegraphics{file:///etc/passwd}$

![Remote figure](https://example.invalid/no-network.png)
"""
    result = report_pdf.render_pdf(source, target)
    text = "\n".join(page.extract_text() for page in PdfReader(target).pages)
    assert sum("could not be typeset" in item for item in result["warnings"]) == 2
    assert any("Images are omitted" in item for item in result["warnings"])
    assert "PDF rendering notes" in text
    assert "could not be typeset" in text
    assert "Image omitted" in text
