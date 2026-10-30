"""Conservative matching of quotations against independently retrieved text."""

import re

from mathlottery.verify.policy import normalized


def _pdf_layout(text: str) -> str:
    text = normalized(text)
    # These are literal glyph names emitted by PDF extractors, not prose or LaTeX.
    for name, glyph in (("/greaterorequalslant", "⩾"), ("/lessorequalslant", "⩽")):
        text = text.replace(name, glyph)
    # Preserve every dot: only the spacing inside a three-dot ellipsis changes.
    text = re.sub(r"(?<!\.)\.\s*\.\s*\.(?!\.)", "...", text)
    # Never join prose words, digits, or decimal components. In particular,
    # 'Letf' / 'Let f' and '1 0' / '10' still require a better source excerpt.
    return re.sub(r"\s*([,;:()\[\]{}=<>≤≥⩽⩾+−*/→∈])\s*", r"\1", text)


def excerpt_match(text: str, excerpt: str, *, pdf: bool = False) -> str | None:
    """Return the supported match mode; never infer semantic equivalence."""
    quote = normalized(excerpt)
    if not quote:
        return None
    if quote in normalized(text):
        return "exact_normalized"
    if pdf and _pdf_layout(quote) in _pdf_layout(text):
        return "pdf_layout_v1"
    return None
