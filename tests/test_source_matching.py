"""PDF layout tolerance must not turn a different mathematical claim into a match."""

import pytest

from mathlottery.config import Config
from mathlottery.evidence_policy import normalized
from mathlottery.literature import snapshot
from mathlottery.models import digest
from mathlottery.source_matching import excerpt_match
from mathlottery.sources import WebTools


@pytest.mark.parametrize(("text", "quote"), [
    ("α, β , γ when n = 3)", "α,β,γ when n = 3)"),
    ("holds for any x1, . . . ,xn > 0 and p ≥ 0.",
     "holds for any x1,...,xn > 0 and p ≥0."),
    ("p /greaterorequalslant q + 1 and\np(q + 1)> 0, then",
     "p ⩾q + 1 and\np(q + 1) > 0, then"),
    ("x /lessorequalslantq + 1", "x ⩽ q+1"),
])
def test_pdf_layout_and_known_extractor_glyphs_match(text, quote):
    assert excerpt_match(text, quote, pdf=True) == "pdf_layout_v1"
    assert excerpt_match(text, quote) is None  # HTML is not granted PDF layout tolerance.


@pytest.mark.parametrize(("text", "quote"), [
    ("For every n ≥ 0, P(n).", "For some n ≥ 0, P(n)."),
    ("There exists p ≥ 0.", "For all p ≥ 0."),
    ("p /greaterorequalslant q + 1", "p ⩽ q+1"),
    ("p /lessorequalslant q + 1", "p ⩾ q+1"),
    ("p ≥ 0", "p >0"),
    ("p ≥ 0", "p ≥1"),
    ("p ≥ 0", "p ≤0"),
    ("p + 1 ≥ 0", "p −1≥0"),
    ("x = 1 0", "x=10"),
    ("x = 1 . 5", "x=1.5"),
    ("x = 1.5", "x=15"),
    ("α, β, γ", "αβγ"),
    ("Letf: (0,∞)→Rbe a convex function.", "Let f : (0, ∞) →R be a convex function."),
    ("The solution is nowhere known.", "The solution is now here known."),
    ("x1, x2, xn", "x1,...,xn"),
    ("Theorem 1 is not solved.", "Theorem 1 is solved."),
    ("p /unknown_glyph q", "p ≥ q"),
    ("A complete theorem.", " "),
])
def test_layout_matching_rejects_changed_claims_and_ambiguous_word_boundaries(text, quote):
    assert excerpt_match(text, quote, pdf=True) is None


def test_normal_text_and_existing_receipt_hashes_remain_compatible():
    assert excerpt_match("Question 1\nremains open.", "Question 1 remains open.") == "exact_normalized"
    assert normalized("p ≥ 0") != normalized("p≥0")


def test_pdf_receipt_records_match_mode_only_after_independent_source_parse(tmp_path, monkeypatch):
    text = "Theorem 2.1: p /greaterorequalslant q + 1 and p(q+1)>0."
    quote = "p ⩾q + 1 and p(q + 1) > 0."
    web = WebTools(tmp_path, Config().tools)
    monkeypatch.setattr(web, "download", lambda *a, **k: (
        b"%PDF-test", "https://example.org/paper.pdf", "application/pdf"))
    monkeypatch.setattr("mathlottery.literature.python_exec", lambda *a, **k: {
        "status": "OK", "stdout": text})
    result = snapshot(web, "https://example.org/paper.pdf", [quote, "p ⩽q + 1"], tmp_path)
    expected = digest(normalized(quote))
    assert result["excerpt_hashes"] == [expected]
    assert result["excerpt_matches"] == [{"sha256": expected, "method": "pdf_layout_v1"}]
    assert (tmp_path / result["artifact"]).read_bytes() == b"%PDF-test"


def test_html_receipt_does_not_apply_pdf_glyph_aliases(tmp_path, monkeypatch):
    web = WebTools(tmp_path, Config().tools)
    monkeypatch.setattr(web, "download", lambda *a, **k: (
        b"<main>p /greaterorequalslant q</main>", "https://example.org/page", "text/html"))
    result = snapshot(web, "https://example.org/page", ["p ⩾ q"], tmp_path)
    assert result["excerpt_hashes"] == []
