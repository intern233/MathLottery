"""Public metadata and bounded downloads for editorial reports."""

from __future__ import annotations

import hashlib
import io
import json
import stat
import zipfile

from mathlottery.artifact_io import read_confined, validate_relative
from mathlottery.models import Workflow, digest
from mathlottery.organization import MAX_PDF_BYTES, report_documents, report_filename
from mathlottery.storage import json_text

# Two language PDFs plus the primary compatibility copy, frozen materials and Markdown.
MAX_BUNDLE_BYTES = 84_000_000


def _document_summary(store, run, language, document):
    pdf_available = False
    if document and document.pdf_status == "ready":
        root = store.run_dir(run.id)
        parent = root / "organized"
        path = parent / report_filename(run, language, "pdf")
        try:
            info = path.lstat()
            pdf_available = (not parent.is_symlink() and stat.S_ISREG(info.st_mode)
                             and info.st_nlink == 1 and 0 < info.st_size <= MAX_PDF_BYTES)
        except OSError:
            pass
    from mathlottery.expert_brief import metadata as brief_metadata

    return {
        "expert_brief_available": bool(document and brief_metadata(run, document, language)),
        "markdown_available": bool(document),
        "pdf_available": pdf_available,
        "pdf_status": document.pdf_status if document else "pending",
        "pdf_error": document.pdf_error if document else None,
        "pdf_warnings": document.pdf_details.get("warnings", []) if document else [],
        "created_at": document.created_at if document else None,
        "markdown_sha256": document.markdown_sha256 if document else None,
    }


def summary(store, run):
    context = run.organization_context
    if context is None:
        return None
    documents = report_documents(run) if run.organization_report else {}
    reports = {language: _document_summary(store, run, language, document)
               for language, document in documents.items()}
    primary = reports.get(context.language) or _document_summary(store, run, context.language, None)
    from mathlottery.expert_delivery import VERSION

    try:
        handoff = json.loads(read_confined(store.run_dir(run.id), "organized/handoff/index.json", 4_000_000))
        handoff_available = handoff.get("version") == VERSION and handoff.get("source_sha256") == context.source_sha256
    except (OSError, ValueError, AttributeError):
        handoff_available = False
    return {
        **primary,
        "source_run_id": context.source_run_id,
        "language": context.language,
        "bundle_available": bool(documents),
        "handoff_available": bool(documents) and handoff_available,
        "handoff_bundle_available": bool(documents),
        "public_bundle_available": bool(documents),
        "public_bundle_kind": "sanitized_text_derivative",
        "public_bundle_includes_pdf": False,
        "report_languages": context.report_languages or [context.language],
        "languages": list(documents),
        "bilingual_complete": set(documents) == {"zh", "en"},
        "reports": reports,
    }


def read_report(store, run_id, format, language=None):
    run = store.load(run_id)
    if run.workflow != Workflow.ORGANIZE or run.organization_report is None:
        raise ValueError("This task has no organized report yet")
    if format not in {"markdown", "pdf", "bundle", "public_bundle"}:
        raise ValueError("Report format must be markdown, pdf, bundle or public_bundle")
    if format in {"bundle", "public_bundle"}:
        if language is not None:
            raise ValueError("The bundle includes every available report language; omit language")
        return _bundle(store, run, public=format == "public_bundle")
    selected = language if language is not None else run.organization_context.language
    if selected not in {"zh", "en"}:
        raise ValueError("Report language must be zh or en")
    documents = report_documents(run)
    if selected not in documents:
        raise ValueError("This saved task does not contain the requested report language")
    if format == "markdown":
        return documents[selected].markdown.encode("utf-8")
    return _read_pdf(store, run, language)


def _read_pdf(store, run, language=None):
    selected = language if language is not None else run.organization_context.language
    document = report_documents(run)[selected]
    if document.pdf_status != "ready":
        raise ValueError("PDF is not ready; download Markdown or retry PDF export")
    try:
        filename = report_filename(run, selected, "pdf") if language is not None else "report.pdf"
        data = read_confined(store.run_dir(run.id), "organized/" + filename, MAX_PDF_BYTES)
    except (OSError, ValueError):
        raise ValueError("PDF is missing or unreadable; retry PDF export") from None
    if not data.startswith(b"%PDF-") or hashlib.sha256(data).hexdigest() != document.pdf_details.get("sha256"):
        raise ValueError("PDF failed its integrity check; retry PDF export")
    return data


def _bundle(store, run, *, public=False):
    """Export only hash-checked frozen inputs, never arbitrary workspace files."""
    from mathlottery.activity import controller_activity

    with controller_activity(store.run_dir(run.id), "report_bundle"):
        return _build_bundle(store, run, public=public)


def _build_bundle(store, run, *, public):
    from mathlottery.organization import MAX_FILES, MAX_TOTAL_BYTES, _read_files, export_manifest

    context = run.organization_context
    if context is None:
        raise ValueError("The organized report has no frozen material manifest")
    if len(context.files) > MAX_FILES or sum(item.size for item in context.files) > MAX_TOTAL_BYTES:
        raise ValueError("The frozen material bundle exceeds its file count or size limit")
    documents = report_documents(run)
    for document in documents.values():
        if digest(document.markdown) != document.markdown_sha256:
            raise ValueError("The saved organized report failed its integrity check")
    from mathlottery.expert_delivery import build, file_manifest, public_files

    materials = list(_read_files(store, run))
    if len({item.path for item, _ in materials}) != len(materials):
        raise ValueError("The bundle contains a duplicate or nonportable material path")
    files = {"report.md": run.organization_report.markdown.encode("utf-8")}
    if run.organization_report.pdf_status == "ready":
        files["report.pdf"] = _read_pdf(store, run)
    for language, document in documents.items():
        filename = report_filename(run, language, "md")
        if filename != "report.md":
            files[filename] = document.markdown.encode("utf-8")
            if document.pdf_status == "ready":
                files[report_filename(run, language, "pdf")] = _read_pdf(store, run, language)
    files.update({"materials/" + item.path: data for item, data in materials})
    files["manifest.json"] = json_text(export_manifest(run)).encode("utf-8")
    files.update(build(run, materials))
    files["handoff/files.json"] = file_manifest(files)
    if sum(map(len, files.values())) > MAX_BUNDLE_BYTES:
        raise ValueError("The expert report bundle exceeds its 84 MB export limit")
    if public:
        files = public_files(files)
    output = io.BytesIO()
    total = 0
    names = set()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        def add(name, data):
            nonlocal total
            validate_relative(name)
            if name in names or ":" in name or any(ord(char) < 32 for char in name):
                raise ValueError("The bundle contains a duplicate or nonportable material path")
            total += len(data)
            if total > MAX_BUNDLE_BYTES:
                raise ValueError("The expert report bundle exceeds its 84 MB export limit")
            names.add(name)
            # Fixed archive metadata avoids leaking local timestamps or permissions.
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o600 << 16
            archive.writestr(entry, data)

        for name, data in files.items():
            add(name, data)
    if output.tell() > MAX_BUNDLE_BYTES:
        raise ValueError("The expert report bundle exceeds its 84 MB export limit")
    return output.getvalue()
