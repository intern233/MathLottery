"""Deterministic expert handoffs and explicitly transformed public text exports.

No model calls, compilation, evidence upgrades or mutation of frozen reports.
Original receipts apply to original bytes only, never to a redacted derivative.
"""

from __future__ import annotations

import hashlib
import html
import ipaddress
import json
import re
from collections import Counter
from pathlib import PurePosixPath
from urllib.parse import quote

from mathlottery.models import digest
from mathlottery.storage.core import json_text

VERSION = "expert-delivery-v3"
PUBLIC_VERSION = "public-text-export-v1"
_DEPENDENCY_SNAPSHOTS = {"lake-manifest.snapshot.json", "mathlib-lake-manifest.snapshot.json"}
_DEPENDENCY_FILES = {"lean-toolchain", "lake-manifest.json", "lakefile.toml", "lakefile.lean"}


def _md(value):
    value = html.escape(str(value), quote=False).replace("\n", " ").replace("\r", "")
    return re.sub(r"([\\`*_$\[\]#!|])", r"\\\1", value).replace(r"\[", "&#91;").replace(r"\]", "&#93;")


def _link(path):
    return "../materials/" + quote(path, safe="/-._~")


def build(run, materials):
    """Create a separate derived entry point; authenticate inputs at the caller."""
    context = run.organization_context
    if context is None:
        raise ValueError("An expert handoff requires a frozen organization context")
    by_hash = {}
    for item, _ in materials:
        by_hash.setdefault(item.sha256, []).append(item.path)
    formal = []
    candidates = []
    files = {}
    for number, candidate in enumerate(run.candidates, 1):
        prefix = f"handoff/candidate-{number}"
        files[prefix + ".proof.md"] = (candidate.proof + "\n").encode()
        files[prefix + ".review.json"] = json_text({
            "candidate_id": candidate.id, "candidate_sha256": candidate.sha256,
            "claim": candidate.claim, "assumptions": candidate.assumptions,
            "scope": candidate.scope, "level": candidate.level,
            "remaining_obligations": candidate.remaining_obligations,
            "reviews": [review.model_dump(mode="json") for review in candidate.reviews],
        }).encode()
        latest = candidate.reviews[-1] if candidate.reviews else None
        candidates.append({
            "id": candidate.id, "sha256": candidate.sha256, "claim": candidate.claim,
            "proof": prefix + ".proof.md", "review": prefix + ".review.json",
            "level": candidate.level, "scope": candidate.scope,
            "verdict": latest.verdict if latest else "UNASSESSED",
            "coverage": latest.original_problem_coverage if latest else "UNASSESSED",
            "novelty": latest.novelty if latest else "UNKNOWN",
            "proof_step_count": len(latest.proof_steps) if latest else 0,
            "unresolved_steps": latest.proof_coverage.unresolved_steps if latest else [],
            "remaining_obligations": candidate.remaining_obligations + (latest.remaining_obligations if latest else []),
        })
        for review_number, review in enumerate(candidate.reviews, 1):
            receipt = review.formal_receipt
            if not receipt:
                continue
            candidate_matches = receipt.get("candidate_sha256") == candidate.sha256
            sources = []
            for source in receipt.get("sources", []):
                matching = by_hash.get(source.get("sha256"), [])
                sources.append({**source, "captured_paths_with_same_sha256": matching,
                                "source_bytes_available": bool(matching)})
            formal.append({
                "candidate_id": candidate.id, "review_number": review_number,
                "status": receipt.get("status", "UNKNOWN") if candidate_matches else "INAPPLICABLE",
                "recorded_status": receipt.get("status", "UNKNOWN"),
                "candidate_sha256": receipt.get("candidate_sha256"),
                "candidate_hash_matches": candidate_matches,
                "applicability": "CANDIDATE_HASH_MATCHES" if candidate_matches else "CANDIDATE_HASH_MISSING_OR_MISMATCHED",
                "scope": receipt.get("scope", "UNKNOWN"),
                "statement_alignment": receipt.get("statement_alignment", "NOT_CERTIFIED"),
                "lean_version": receipt.get("lean_version", "NOT_RECORDED"),
                "request": receipt.get("request", {}), "sources": sources,
                "declarations": receipt.get("declarations", []),
                "recorded_steps": receipt.get("steps", []),
                "receipt_path": next((item.path for item, _ in materials
                    if item.path == f"{context.source_run_id}/{receipt.get('artifact', '')}"), None),
                "limitations": [
                    "Recorded argv use the original isolated runner filesystem; they are evidence, not a portable shell script.",
                    "Only listed declarations are covered. Other conclusions require handwritten review unless separately evidenced.",
                    "Natural-language/formal equivalence needs external evidence. This export performs no new check.",
                ],
            })
    dependencies = [{"path": item.path, "sha256": item.sha256,
                     "kind": "snapshot" if PurePosixPath(item.path).name in _DEPENDENCY_SNAPSHOTS else "project_file"}
                    for item, _ in materials
                    if PurePosixPath(item.path).name in _DEPENDENCY_FILES | _DEPENDENCY_SNAPSHOTS]
    dependency_names = {PurePosixPath(item["path"]).name for item in dependencies}
    gaps = []
    if any(not item["candidate_hash_matches"] for item in formal):
        gaps.append("A formal receipt has a missing or mismatched candidate hash and is INAPPLICABLE to this candidate; its recorded success is not formal coverage here.")
    if formal and "lean-toolchain" not in dependency_names:
        gaps.append("No lean-toolchain file was captured; consult the receipt's recorded Lean version.")
    if formal and "lake-manifest.json" not in dependency_names:
        gaps.append(
            "Only dependency manifest snapshots were captured, not a project lake-manifest.json; snapshots do not establish the lockfile or imported libraries used for the recorded compilation."
            if dependency_names & _DEPENDENCY_SNAPSHOTS else
            "No lake-manifest.json was captured; imported library revisions are not pinned by this handoff.")
    if any(not s["source_bytes_available"] for item in formal for s in item["sources"]):
        gaps.append("Some checked source bytes are absent; do not substitute a same-named file with a different hash.")
    if not formal:
        gaps.append("No formal execution receipt is recorded; this handoff does not establish Lean verification.")
    index = {
        "version": VERSION, "source_run_id": context.source_run_id,
        "source_sha256": context.source_sha256, "problem_sha256": context.problem_sha256,
        "problem": run.problem.model_dump(mode="json") if run.problem else None,
        "candidates": candidates, "formal_checks": formal, "dependency_files": dependencies,
        "dependency_binding": "NOT_CERTIFIED",
        "reproduction_gaps": gaps,
        "automatic_replay_available": False,
        "limitations": [
            "Deterministic navigation of frozen evidence, not a new review or proof.",
            "Dependency files and code are untrusted. No Lake hooks or download scripts are executed by this export.",
            "Captured project dependency files are not automatically proven identical to the libraries used by the recorded runner.",
            "File hashes authenticate captured bytes; a successful hash check does not verify mathematics.",
        ],
    }
    files["handoff/index.json"] = json_text(index).encode()
    for language in ("zh", "en"):
        files[f"handoff/START_HERE.{language}.md"] = _entry(run, index, language).encode()
    files["handoff/check_files.py"] = _CHECK_FILES.encode()
    return files


def _entry(run, index, language):
    def tr(cn, en):
        return cn if language == "zh" else en
    languages = run.organization_context.report_languages or [run.organization_context.language]
    report_links = " · ".join(
        f"[{('中文报告' if lang == 'zh' else 'English report')}](../report.{lang}.md)"
        if len(languages) > 1 else f"[{('中文报告' if lang == 'zh' else 'English report')}](../report.md)"
        for lang in languages)
    sections = [tr("# 专家交接：从这里开始", "# Expert handoff: start here"),
        tr("本页为本地自动生成的阅读入口，不新增验证，也不提升证明或新颖性等级。完整细节在双语报告和冻结材料中。",
           "This locally generated entry point adds no verification and upgrades no proof or novelty status. Full details remain in the bilingual reports and frozen materials."),
        report_links + " · [Structured index](index.json) · [Evidence manifest](../manifest.json)",
        tr("**交付范围：报告正文提及的补充材料或额外附件未必包含在本包中。请按 `manifest.json` 核对冻结材料、按 `handoff/files.json` 核对实际导出文件；完整性检查通过只表示索引所列文件的字节匹配，不保证所有被提及的附件齐全。缺失附件须另行提供并说明来源。这是交付边界，不是对数学结论的新否定。**",
           "**Delivery scope: supplements or additional attachments mentioned in the reports may not be included in this bundle. Check `manifest.json` for frozen materials and `handoff/files.json` for actual exported files. A successful integrity check means only that the listed file bytes match; it does not establish that every referenced attachment is present. Missing attachments must be supplied separately with their provenance. This is a delivery boundary, not a new adverse mathematical finding.**"),
        tr("## 先核对命题与结论", "## Check the statement and conclusions first"),
        _md(run.problem.title if run.problem else ""),
        tr("原题完整陈述、假设和来源见 `index.json → problem`；不以标题或摘要代替量词、定义域和边界。",
           "The complete statement, assumptions and sources are in `index.json → problem`; titles and summaries do not replace quantifiers, domains or boundaries.")]
    for number, candidate in enumerate(index["candidates"], 1):
        sections += [f"### {number}. {_md(candidate['id'])}",
            f"{_md(candidate['claim'])}",
            f"`{candidate['level']}` · scope `{candidate['scope']}` · review `{candidate['verdict']}` · coverage `{candidate['coverage']}` · novelty `{candidate['novelty']}`",
            f"[Proof](candidate-{number}.proof.md) · [All reviews and steps](candidate-{number}.review.json)",
            tr(f"已记录 {candidate['proof_step_count']} 个证明步骤；逐项对照依赖、检查 ID 和未覆盖项。",
               f"{candidate['proof_step_count']} proof steps recorded; inspect their dependencies, check IDs and unresolved entries."),
            tr("未完成义务：", "Remaining obligations: ") + (_md("; ".join(candidate["remaining_obligations"])) or "—")]
    sections += [tr("## 形式化覆盖与复现", "## Formal coverage and reproduction"),
        tr("只对下列回执明确列出的声明主张形式检查；等号情形、推广、最优性等附加结论若未列入，仍需书面复核。自然语言命题与 Lean 定理的对应性不是由编译成功自动确认的。",
           "Formal checking applies only to declarations explicitly listed in the receipts below. Additional equality cases, generalizations or optimality claims need written review unless separately listed. Successful compilation does not certify natural-language/formal equivalence.")]
    for receipt in index["formal_checks"]:
        sections.append(f"- {_md(receipt['candidate_id'])} / review {receipt['review_number']}: `{receipt['status']}`; alignment `{receipt['statement_alignment']}`")
        if not receipt["candidate_hash_matches"]:
            sections.append(tr(
                "  **不可适用：回执候选哈希缺失或不匹配，不能作为当前候选的形式验证证据。** 原始记录状态：",
                "  **INAPPLICABLE: the receipt candidate hash is missing or mismatched; this does not verify the current candidate.** Recorded status: ")
                + _md(receipt["recorded_status"]))
        sections.append("  Lean: " + _md(receipt["lean_version"]))
        for declaration in receipt["declarations"]:
            name = declaration.get("name", "UNNAMED") if isinstance(declaration, dict) else declaration
            sections.append("  - " + _md(name))
        for source in receipt["sources"]:
            paths = source["captured_paths_with_same_sha256"]
            links = ", ".join(f"[{_md(p)}]({_link(p)})" for p in paths)
            sections.append("  - " + (links or tr("缺少对应源码", "Matching source absent")) + "; SHA-256 `" + str(source.get("sha256", "UNKNOWN")) + "`")
    sections += [tr("1. 解压完整材料包，在包根目录运行 `python handoff/check_files.py`，只核对文件完整性。\n2. 在 `index.json` 查看 `formal_checks` 的完整定理类型、axioms、源码哈希和原始 argv；argv 中的隔离路径不能直接在本机执行。\n3. 检查冻结的 Lean/Lake 依赖文件，在独立受限环境准备对应版本，核对依赖源码后再重放。缺少依赖锁定或源码时先补齐，不能声称可一键复现。\n4. 逐项核对书面证明、Lean 声明与原题；没有自动执行任何材料中的脚本或 Lake 钩子。",
        "1. Extract the complete bundle and run `python handoff/check_files.py` from its root; this checks file integrity only.\n2. Inspect `formal_checks` in `index.json` for full declaration types, axioms, source hashes and recorded argv; isolated paths in argv are not directly runnable locally.\n3. Inspect captured Lean/Lake dependency files and prepare matching versions in a separate restricted environment before replay. Resolve missing dependency pins or sources first; this is not a one-click replay claim.\n4. Check the written proof, Lean declarations and original problem individually. No supplied scripts or Lake hooks are executed automatically.")]
    if index["dependency_files"]:
        sections += [tr("### 依赖文件与快照导航", "### Dependency files and snapshots"),
            tr("依赖快照未必是编译时实际使用的锁文件；项目文件也未自动绑定到回执中的导入库。下列链接仅供复核，环境对应关系仍为 `NOT_CERTIFIED`。",
               "Dependency snapshots may not be the lockfile actually used for compilation; project files are not automatically bound to the receipt's imported libraries either. These links support inspection only; environment correspondence remains `NOT_CERTIFIED`.")]
        for dependency in index["dependency_files"]:
            label = (tr("依赖快照", "Dependency snapshot") if dependency["kind"] == "snapshot"
                     else tr("项目依赖文件", "Project dependency file"))
            sections.append(f"- {label}: [{_md(dependency['path'])}]({_link(dependency['path'])}); SHA-256 `{dependency['sha256']}`")
    if index["reproduction_gaps"]:
        sections += [tr("### 尚缺的复现条件", "### Missing reproduction conditions")]
        sections += ["- " + _md(value) for value in index["reproduction_gaps"]]
    sections += [tr("## 新颖性与专家检查顺序", "## Novelty and expert review order"),
        tr("先读证明，再核对命题范围和关键步骤，最后逐项比较最接近的已有结果。`candidate-*.review.json` 保留全部历史检查和文献障碍；旧失败不会因新审查而消失。请分别记录数学正确性、题意对应和新颖性判断。",
           "Read the proof, check its scope and key steps, then compare the closest prior results individually. `candidate-*.review.json` retains all historical checks and literature obstacles; later review does not erase earlier failures. Record correctness, statement alignment and novelty separately."),
        tr("公开分享请使用独立的脱敏文本包；原始材料包保留原始字节，可能包含本机路径。脱敏后的源码不能直接继承原始 Lean 回执。",
           "Use the separate sanitized text bundle for public sharing. The original evidence bundle preserves bytes and may contain local paths. Redacted source does not inherit the original Lean receipt.")]
    return "\n\n".join(sections) + "\n"


_CHECK_FILES = '''"""Check exported bytes only; never execute supplied research or build scripts."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / "handoff/files.json").read_text(encoding="utf-8"))
failures = []
for entry in manifest["files"]:
    relative = Path(entry["path"])
    target = root / relative
    if relative.is_absolute() or ".." in relative.parts or any(
        path.is_symlink() for path in [target, *target.parents] if path != root.parent
    ) or not target.is_file():
        failures.append(str(relative))
        continue
    if target.stat().st_size != entry["size"] or hashlib.sha256(target.read_bytes()).hexdigest() != entry["sha256"]:
        failures.append(str(relative))
if failures:
    raise SystemExit("File integrity check failed: " + ", ".join(failures))
print("All listed file hashes match. This does not verify mathematics or certify novelty.")
'''


def file_manifest(files):
    return json_text({"version": VERSION, "scope": "Listed bytes only; the manifest is not a signature or a proof.",
                      "files": [{"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                                for path, data in sorted(files.items()) if path != "handoff/files.json"]}).encode()


_REDACTIONS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)),
    ("home_path", re.compile(r"(?:/(?:home|Users)/[^\s<>\"'`)\],;]+|/root(?:/[^\s<>\"'`)\],;]*)?|[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][^\s<>\"'`)\],;]+)")),
    ("encoded_home_path", re.compile(r"(?i)(?:%2f(?:home|users)%2f|[A-Z]%3a%5cusers%5c)[^\s<>\"'`)\],;]+")),
    ("email", re.compile(r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+\b")),
    ("api_token", re.compile(r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("authorization", re.compile(r"(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9+/_.=-]{8,}")),
    ("url_credentials", re.compile(r"(?i)(?:https?|socks5h?)://[^\s/@]+:[^\s/@]+@[^\s<>\"'`]+")),
    ("url_token", re.compile(r"(?i)([?&](?:token|key|api_key|access_token|auth|signature)=)[^\s&<>\"'`]+")),
    ("secret_assignment", re.compile(r"(?im)\b(?:access_token|refresh_token|id_token|api_key|openai_api_key|authorization|password|client_secret|account_id|chatgpt_account_id)\b[\"']?\s*[:=]\s*[\"']?[^\s\"',;}]+")),
]
_IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
_IPV6 = re.compile(r"(?<![\w:])(?:[A-Fa-f0-9]{0,4}:){2,}[A-Fa-f0-9:.]*(?:%[A-Za-z0-9_-]+)?(?![\w:])")
_SECRET_KEYS = re.compile(r"(?i)(?:token|password|secret|credential|api.?key|authorization|cookie|account.?id|subscription|plan_type)")


def sanitize(value, counts=None):
    """Redact supported personal/credential patterns, retaining no secret previews."""
    counts = Counter() if counts is None else counts
    for category, pattern in _REDACTIONS:
        value, number = pattern.subn("REDACTED_" + category.upper(), value)
        counts[category] += number
    def private_ip(match):
        try:
            address = ipaddress.ip_address(match[0].split("%", 1)[0])
        except ValueError:
            return match[0]
        if address.is_private or address.is_loopback or address.is_link_local:
            counts["private_ip"] += 1
            return "REDACTED_PRIVATE_IP"
        return match[0]
    value = _IPV4.sub(private_ip, value)
    value = _IPV6.sub(private_ip, value)
    return value, {key: count for key, count in counts.items() if count}


def _sanitize_json(value, counts):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            clean_key = sanitize(key, counts)[0]
            if clean_key in result:
                raise ValueError("Public export cannot safely preserve colliding sanitized JSON keys")
            if _SECRET_KEYS.search(key):
                result[clean_key] = "REDACTED_PRIVATE_FIELD"
                counts["private_field"] += 1
            else:
                result[clean_key] = _sanitize_json(child, counts)
        return result
    if isinstance(value, list):
        return [_sanitize_json(item, counts) for item in value]
    return sanitize(value, counts)[0] if isinstance(value, str) else value


def public_files(originals):
    """Produce bounded text derivatives; never copy opaque PDFs or arbitrary binaries."""
    from mathlottery.organize.workflow import EXTENSIONS, PRIVATE_NAMES

    result, entries, omitted = {}, [], []
    mapping = {}
    for path in originals:
        clean = sanitize(path)[0]
        mapping[path] = clean
        if clean in mapping.values() and list(mapping.values()).count(clean) > 1:
            raise ValueError("Public export cannot safely preserve colliding sanitized paths")
    for path, data in originals.items():
        destination = mapping[path]
        basename = PurePosixPath(path).name
        identity = {"path": destination, "original_path_sha256": digest(path),
                    "original_sha256": hashlib.sha256(data).hexdigest()}
        if path == "handoff/files.json":
            continue  # Regenerate against derivative bytes below.
        if (basename.casefold() in PRIVATE_NAMES or basename.startswith(".")
                or any(part.casefold() in {"auth", "credentials", "codex-home", "sessions", ".env"}
                       for part in PurePosixPath(path).parts)
                or (PurePosixPath(path).suffix.lower() not in EXTENSIONS and basename != "lean-toolchain")):
            omitted.append({**identity, "reason": "Private name or non-text/unsupported format; original PDFs are deliberately omitted."})
            continue
        try:
            text = data.decode("utf-8")
            if "\0" in text:
                raise UnicodeError("binary")
        except UnicodeError:
            omitted.append({**identity, "reason": "Not plain UTF-8 text"})
            continue
        counts = Counter()
        if path.endswith(".json"):
            try:
                sanitized = _sanitize_json(json.loads(text), counts)
                if any(counts.values()):
                    text = json_text(sanitized)
            except json.JSONDecodeError:
                omitted.append({**identity, "reason": "Invalid JSON cannot be safely transformed"})
                continue
        else:
            text = sanitize(text, counts)[0]
        if re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text):
            omitted.append({**identity, "reason": "Incomplete private-key material could not be safely transformed"})
            continue
        for old, new in mapping.items():
            if old != new:
                text = text.replace(quote(old, safe="/-._~"), quote(new, safe="/-._~"))
        transformed = text.encode()
        result[destination] = transformed
        entries.append({**identity, "export_sha256": hashlib.sha256(transformed).hexdigest(),
                        "size": len(transformed), "byte_identical": data == transformed,
                        "redactions": {key: count for key, count in counts.items() if count}})
    result["public-export.json"] = json_text({
        "version": PUBLIC_VERSION, "kind": "sanitized_text_derivative", "files": entries, "omitted": omitted,
        "source_evidence_unchanged": True, "original_receipts_apply_to_original_hashes_only": True,
        "screening": [category for category, _ in _REDACTIONS] + ["private_ip", "private_json_fields", "private_filenames"],
        "limitations": [
            "This is a derivative, not the immutable evidence archive. Redactions and omissions can reduce reproducibility.",
            "Original PDFs and binaries are omitted; inspect the sanitized Markdown instead.",
            "Modified Lean sources do not inherit original kernel receipts. Compare original_sha256 and export_sha256.",
            "Automated screening covers the listed patterns, not every possible private fact. Review the derivative before publishing.",
        ],
    }).encode()
    result["PUBLIC_README.md"] = (
        "# Sanitized public text package / 脱敏公开文本包\n\n"
        "Start with [中文入口](handoff/START_HERE.zh.md) or [English entry](handoff/START_HERE.en.md).\n\n"
        "`public-export.json` maps original hashes to exported hashes and lists redactions and omissions. "
        "Original PDFs are omitted; the bilingual Markdown remains. The original evidence is unchanged. "
        "Altered Lean sources cannot inherit original check receipts. Review this derivative before publishing.\n\n"
        "公开包保留中英文 Markdown；原始 PDF 不复制。请查看转换清单，核对删改及遗漏。"
        "原始证据未修改，脱敏后的 Lean 源码不能直接继承原来的验证回执。\n"
    ).encode()
    result["handoff/files.json"] = file_manifest(result)
    return result
