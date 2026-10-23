"""Bounded independent retrieval of milestone citations, with durable receipts."""

import base64
import hashlib
import json
import time

import httpx

from mathlottery import budget
from mathlottery.config import Config
from mathlottery.evidence_policy import normalized, recent
from mathlottery.execution import python_exec
from mathlottery.models import Citation, Run, digest, now
from mathlottery.sources import WebTools, parse_page
from mathlottery.storage import Store, atomic_write, json_text, safe_path


def snapshot(web: WebTools, url: str, excerpts: list[str], directory) -> dict:
    data, final_url, kind = web.download(url, allow_pdf=True)
    sha = hashlib.sha256(data).hexdigest()
    pdf = "application/pdf" in kind or data.startswith(b"%PDF-")
    relative = f"literature/snapshots/{sha}.{'pdf' if pdf else 'txt'}"
    path = directory / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if pdf:
        # Parse untrusted PDFs in the existing bounded, network-free OS sandbox.
        encoded = base64.b64encode(data).decode("ascii")
        code = (
            "import base64, io\nfrom pypdf import PdfReader\n"
            f"reader = PdfReader(io.BytesIO(base64.b64decode({encoded!r})))\n"
            "if len(reader.pages) > 100: raise ValueError('PDF exceeds 100-page extraction limit')\n"
            "for page in reader.pages: print(page.extract_text())\n"
        )
        config = web.config.model_copy(update={
            "timeout_seconds": min(10, web.config.web_timeout_seconds),
            "memory_mb": 512, "max_output_chars": 100000,
        })
        result = python_exec(code, directory / "literature" / "pdf-parsing" / sha, config, web.cancelled)
        if result["status"] != "OK" or len(result["stdout"]) >= config.max_output_chars:
            return {
                "status": "UNAVAILABLE", "record_kind": "source_snapshot", "requested_url": url,
                "url": final_url, "retrieved_at": now(), "sha256": sha, "artifact": relative,
                "reason": f"PDF extraction {result['status']} or truncated; use a readable text source",
                "parser_artifact": f"literature/pdf-parsing/{sha}",
            }
        text = result["stdout"]
    else:
        text = parse_page(data.decode("utf-8", errors="replace"), final_url)["text"]
    atomic_write(directory / "literature" / "snapshots" / f"{sha}.extracted.txt", text)
    content = normalized(text)
    return {
        "status": "OK", "record_kind": "source_snapshot", "requested_url": url,
        "url": final_url, "retrieved_at": now(), "sha256": sha, "artifact": relative,
        "excerpt_hashes": [digest(normalized(e)) for e in excerpts if normalized(e) in content],
        "scope": "Text matches only; source interpretation and search completeness are not certified",
    }


def collect_sources(store: Store, run: Run, citations: list[Citation]) -> None:
    if not citations:
        return
    config = Config.model_validate(run.config)
    directory = store.run_dir(run.id)
    limit = config.verification
    deadline = time.monotonic() + min(limit.source_timeout_seconds, budget.remaining(run, config))

    def cancelled():
        return (time.monotonic() >= deadline or (directory / "stop.requested").exists())

    web = WebTools(directory, config.tools, cancelled)
    grouped: dict[str, list[str]] = {}
    for citation in citations:
        grouped.setdefault(citation.url, []).append(citation.excerpt)
    for number, (url, excerpts) in enumerate(grouped.items()):
        key = digest(json_text([run.task_id, url, sorted(excerpts)]))
        receipt_path = directory / "literature" / "receipts" / f"{key}.json"
        record = None
        if receipt_path.is_file():
            saved = json.loads(receipt_path.read_text())
            if saved.get("status") == "OK" and recent(saved.get("retrieved_at")):
                artifact = safe_path(directory, saved["artifact"])
                if (artifact.is_file() and artifact.stat().st_size <= config.tools.max_download_bytes
                    and hashlib.sha256(artifact.read_bytes()).hexdigest() == saved["sha256"]):
                    record = saved
        if record is None:
            reason = None
            if not limit.fetch_sources or not config.backend.native_network_access:
                reason = "Independent source retrieval is disabled by configuration"
            elif number >= limit.max_sources:
                reason = "Independent source count limit reached"
            elif cancelled():
                reason = "Source retrieval budget reached or run stopped"
            if reason:
                record = {"status": "UNAVAILABLE", "reason": reason}
            else:
                try:
                    record = snapshot(web, url, excerpts, directory)
                except Exception as error:
                    # Provider errors may contain proxy details; do not expose those in a report.
                    if isinstance(error, httpx.HTTPStatusError):
                        reason = f"Source returned HTTP {error.response.status_code}"
                    elif isinstance(error, httpx.TimeoutException):
                        reason = "Source request timed out"
                    else:
                        reason = str(error) if isinstance(error, ValueError) else type(error).__name__
                    record = {"status": "UNAVAILABLE", "reason": reason}
            record.update(record_kind="source_snapshot", requested_url=url)
            atomic_write(receipt_path, json_text(record))
        relative = str(receipt_path.relative_to(directory))
        previous = next((o for o in reversed(run.observations) if o.get("artifact") == relative), None)
        if previous is None or previous["result"] != record:
            run.observations.append({
                "phase": run.phase.value, "iteration": run.iteration,
                "tool": "source_snapshot", "artifact": relative, "result": record,
            })
