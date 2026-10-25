"""Deterministic, bilingual reading guides for immutable organization snapshots.

The guide reports recorded evidence. It never infers a missing proof step, invents
an expert certification, follows a live source, or rewrites an old report.
"""

from __future__ import annotations

import html
import re
from pathlib import PurePosixPath
from urllib.parse import quote, urlsplit, urlunsplit

from mathlottery.models import digest

VERSION = "expert-brief-v2"
MARKER = "[mathlottery-expert-brief-v2]: #"
END_MARKER = "[mathlottery-expert-brief-v2-end]: #"
LEGACY_MARKER = "[mathlottery-expert-brief-v1]: #"
LEGACY_END_MARKER = "[mathlottery-expert-brief-v1-end]: #"


def text(value):
    """Render untrusted records literally, without active Markdown/HTML links."""
    value = html.escape(str(value), quote=False)
    value = re.sub(r"([\\`*_$\[\]#!|])", r"\\\1", value)
    return value.replace("\r", "").replace("\n", " ")


def code(value):
    value = str(value)
    return f"`{value}`" if re.fullmatch(r"[A-Za-z0-9_.:-]+", value) else text(value)


def safe_link(label, target):
    """Only HTTP(S) links with no credentials; encode Markdown delimiters."""
    label = text(label)
    if not isinstance(target, str) or any(ord(c) < 32 for c in target):
        return label
    try:
        parsed = urlsplit(target)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            return label
        url = urlunsplit(parsed)
    except ValueError:
        return label
    return f"[{label}]({quote(url, safe=':/?&=%#@+,-._~')})"


def material_link(context, relative, label=None):
    """Resolve only a captured portable path, never a mutable source workspace."""
    label = text(label or relative)
    if not isinstance(relative, str) or any(ord(c) < 32 for c in relative) or "\\" in relative:
        return label
    candidates = {item.path for item in context.files}
    path = relative if relative in candidates else f"{context.source_run_id}/{relative}"
    parts = PurePosixPath(path)
    if path not in candidates or parts.is_absolute() or any(p in {"..", "."} or ":" in p for p in parts.parts):
        return label
    return f"[{label}](materials/{quote(path, safe='/-._~')})"


def _value(value, name, default=None):
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def _items(values):
    return "; ".join(text(v) for v in values) or "—"


def _evidence(context, values):
    return "; ".join(safe_link(v, v) if str(v).startswith(("https://", "http://"))
                     else material_link(context, v) for v in values) or "—"


def _table(headings, rows):
    return "\n".join(["| " + " | ".join(headings) + " |", "| " + " | ".join("---" for _ in headings) + " |",
                      *["| " + " | ".join(row) + " |" for row in rows]])


def _render_v1(run, language):
    """Frozen legacy renderer: used only to authenticate existing v1 prefixes."""
    context = run.organization_context
    if context is None or run.problem is None or language not in {"zh", "en"}:
        raise ValueError("Expert briefing requires a frozen problem and a supported language")
    zh = language == "zh"
    def tr(cn, en):
        return cn if zh else en

    problem = run.problem
    sections = [LEGACY_MARKER, tr("# MathLottery 专家阅读报告", "# MathLottery expert reading report"),
                tr("> 本文仅整理冻结证据，不进行新增验证，也不提升证明等级、开放状态或新颖性。",
                   "> This organizes frozen evidence only; it adds no verification and does not upgrade proof status or certify open status or novelty."),
                tr("## 专家速览", "## Expert quick review"),
                tr("以下摘要由冻结记录直接生成；原题、候选结论及证据原文保持原语言，避免自动翻译改变命题。",
                   "This guide is generated from frozen records. Statements, candidate claims and evidence excerpts retain their source language to avoid changing a theorem through translation."),
                f"{tr('来源任务', 'Source task')}: {text(context.source_run_id)} · "
                f"{tr('冻结版本', 'Frozen revision')}: {context.source_revision} · {text(context.captured_at)}",
                f"{tr('来源快照 SHA-256', 'Source snapshot SHA-256')}: `{context.source_sha256}`\n\n"
                f"{tr('原题 SHA-256', 'Problem SHA-256')}: `{context.problem_sha256}`",
                "[Evidence manifest](manifest.json) · " + material_link(context, "dossier.json", tr("冻结审查材料", "Frozen reviewed dossier")),
                tr("### 1. 原题与候选结论", "### 1. Original problem and candidate claims"),
                f"**{text(problem.title)}**", text(problem.statement),
                f"{tr('原始出处', 'Original source')}: " + (safe_link(problem.source_url, problem.source_url)
                    if problem.source_url else tr("未提供", "not supplied")),
                f"{tr('记录的开放状态', 'Recorded open status')}: `{problem.status}` · "
                f"{tr('核查日期', 'Checked')}: {text(problem.status_checked_at or tr('未建立', 'not established'))}"]
    for candidate in run.candidates:
        snapshot = next((item for item in context.candidate_hashes if item["id"] == candidate.id), {})
        sections += [f"**{text(candidate.id)}** · `{candidate.level}` · scope `{candidate.scope}`",
                     f"SHA-256: `{candidate.sha256}`",
                     f"{tr('候选与审查快照 SHA-256', 'Candidate and review snapshot SHA-256')}: "
                     f"{code(snapshot.get('snapshot_sha256', 'UNAVAILABLE'))}", text(candidate.claim),
                     f"{tr('候选假设', 'Candidate assumptions')}: {_items(candidate.assumptions)}",
                     f"{tr('候选剩余证明义务', 'Candidate remaining proof obligations')}: {_items(candidate.remaining_obligations)}"]
    sections += [tr("### 2. 原始验证记录与关键步骤", "### 2. Recorded verification and key steps")]
    questions = []
    for candidate in run.candidates:
        sections += [f"**{text(candidate.id)}**"]
        if not candidate.reviews:
            sections.append(tr("尚无验证记录。", "No recorded review."))
            questions.append(tr("候选论证的独立检查在哪里？", "Where is an independent check of the candidate argument?"))
            continue
        rows = [[str(i), f"`{r.verdict}`", f"`{r.original_problem_coverage}`", f"`{r.novelty}`"]
                for i, r in enumerate(candidate.reviews, 1)]
        sections.append(_table([tr("审查", "Review"), tr("判断", "Verdict"), tr("原题覆盖", "Problem coverage"), tr("新颖性", "Novelty")], rows))
        # Earlier failures are evidence, even when a later review reports no issues.
        for i, review in enumerate(candidate.reviews, 1):
            for issue in review.issues:
                sections.append(f"- {tr('审查', 'Review')} {i} · {tr('记录的问题', 'recorded issue')}: {text(issue)}")
            for note in review.validation_notes:
                sections.append(f"- {tr('审查', 'Review')} {i} · {tr('证据门槛说明', 'evidence gate')}: {text(note)}")
            for check in review.checks:
                if check.result != "SUPPORTED":
                    sections.append(f"- {tr('审查', 'Review')} {i} · `{check.result}` · {text(check.id or check.method)} · "
                                    f"blocking={check.blocking}: {text(check.claim)} — {text(check.reasoning)} "
                                    f"({_evidence(context, check.evidence)})")
            if review.formal_receipt and review.formal_receipt.get("status") not in {"KERNEL_REPLAYED", "KERNEL_CHECKED"}:
                sections.append(f"- {tr('审查', 'Review')} {i} · Lean {code(review.formal_receipt.get('status', 'UNKNOWN'))}: "
                                f"{text(review.formal_receipt.get('reason', ''))}")
        review = candidate.reviews[-1]
        sections += [f"{tr('新颖性说明', 'Novelty explanation')}: {text(review.novelty_notes) or '—'}"]
        sections += [f"{tr('最新论证审查', 'Latest proof assessment')}: {text(review.proof_assessment)}",
                     f"{tr('原题对应说明', 'Statement coverage explanation')}: {text(review.coverage_explanation) or '—'}"]
        coverage = review.proof_coverage
        if coverage.policy_version:
            sections += [f"{tr('结构覆盖策略', 'Structural coverage policy')}: {code(coverage.policy_version)} · "
                         f"proof_complete={coverage.proof_complete} · statement_aligned={coverage.statement_aligned}",
                         f"{tr('未覆盖步骤', 'Unresolved steps')}: {_items(coverage.unresolved_steps)}"]
            sections.extend("- " + text(reason) for reason in coverage.reasons)
        else:
            sections.append(tr("关键步骤覆盖尚未评估；历史审查记录不自动补齐。", "Key-step coverage is unassessed; historical reviews are not retroactively completed."))
        steps = review.proof_steps
        if steps:
            rows = [[text(s.id), text(s.statement), _items(s.dependencies), _items(s.check_ids)] for s in steps[:12]]
            sections.append(_table([tr("步骤", "Step"), tr("论证路线（审查者记录）", "Proof roadmap (reviewer-recorded)"),
                                    tr("依赖", "Dependencies"), tr("检查 ID", "Check IDs")], rows))
            if len(steps) > 12:
                sections.append(tr(f"列出前 12 / {len(steps)} 步；完整路线与检查原文见冻结审查材料。",
                                   f"First 12 of {len(steps)} steps shown; the frozen reviewed dossier contains the complete roadmap and checks."))
        else:
            sections.append(tr("未记录结构化证明路线；请从冻结材料逐步重建，不能从通过标签推断完整性。",
                               "No structured proof roadmap was recorded. Reconstruct it from the frozen dossier; a verdict label does not imply completeness."))
        if review.statement_alignment:
            sections.append(_table([tr("对应维度", "Alignment facet"), tr("原题", "Original"), tr("候选", "Candidate"), tr("判断", "Assessment")],
                                   [[a.facet, text(a.original), text(a.candidate), a.assessment] for a in review.statement_alignment]))
        receipt = review.formal_receipt
        if receipt:
            sections += [f"Lean: {code(receipt.get('status', 'UNKNOWN'))} · {text(receipt.get('reason', ''))}",
                         f"{tr('声明', 'Declarations')}: {_items(_value(item, 'name', item) for item in receipt.get('declarations', []))}",
                         f"{tr('回执中的检查范围', 'Receipt check scope')}: {text(receipt.get('scope', 'UNKNOWN'))}",
                         f"{tr('回执中的命题对应状态', 'Receipt statement alignment')}: {code(receipt.get('statement_alignment', 'NOT_CERTIFIED'))}",
                         material_link(context, receipt.get("artifact", ""), tr("执行回执（若已纳入快照）", "Execution receipt (if captured)"))]
        else:
            sections.append(tr("未记录独立 Lean 执行回执。", "No independent Lean execution receipt is recorded."))
        sections.append(tr("形式检查仅覆盖回执中的声明；自然语言原题与形式命题等价性未经外部认证。",
                           "Formal checks cover the declarations in the receipt only; natural-language/formal-statement equivalence has no external certification."))
        for obligation in candidate.remaining_obligations + review.remaining_obligations:
            sections.append(f"- {tr('未完成证明义务', 'Remaining proof obligation')}: {text(obligation)}")
            questions.append(text(obligation))
        if not coverage.statement_aligned or review.original_problem_coverage != "FULL":
            questions.append(tr("原题与候选的假设、量词、定义域及边界情形是否逐项一致？",
                                "Do assumptions, quantifiers, domain and boundary cases match the original problem?"))
        questions.extend(text(item) for item in coverage.reasons)
    sections.append(tr("### 3. 文献障碍与新颖性", "### 3. Literature obstacles and novelty"))
    records = [(tr("原题开放状态", "Original open status"), problem.literature_search, problem.evidence_assessment)]
    records += [(text(c.id) + " / " + tr("审查", "review") + f" {i}", r.literature_search, r.evidence_assessment)
                for c in run.candidates for i, r in enumerate(c.reviews, 1)]
    for label, search, assessment in records:
        sections.append(f"**{label}** · {tr('证据策略', 'Evidence policy')}: {text(assessment.policy_version or 'UNASSESSED')}")
        obstacles = assessment.obstacles if assessment.policy_version else search.obstacles
        for obstacle in obstacles:
            supported = _value(obstacle, "resolution_supported", False)
            status = _value(obstacle, "status", "OPEN")
            sections += [f"- {text(_value(obstacle, 'id', ''))} · {code(status)} · "
                         f"{tr('消除证据受支持', 'Resolution evidence supported')}={supported}: "
                         f"{text(_value(obstacle, 'description', ''))}",
                         f"  {tr('影响', 'Impact')}: {text(_value(obstacle, 'impact', ''))} · "
                         f"{tr('下一步', 'Next action')}: {text(_value(obstacle, 'next_action', ''))}"]
            if _value(obstacle, "source_url"):
                sections.append("  " + safe_link(_value(obstacle, "source_url"), _value(obstacle, "source_url")))
            if _value(obstacle, "resolution"):
                sections.append(f"  {tr('记录的消除说明', 'Reported resolution')}: {text(_value(obstacle, 'resolution'))}")
            if _value(obstacle, "resolution_reason"):
                sections.append("  " + text(_value(obstacle, "resolution_reason")))
            if status != "RESOLVED" or not supported:
                questions.append(text(_value(obstacle, "next_action", "")))
        comparisons = assessment.comparisons if assessment.policy_version else search.comparisons
        for comparison in comparisons[:5]:
            sections += [f"- {tr('已有结果对照', 'Prior-result comparison')} {text(_value(comparison, 'id', ''))} · "
                         f"{code(_value(comparison, 'relation', 'UNKNOWN'))} · "
                         f"{tr('对照证据受支持', 'Comparison evidence supported')}={_value(comparison, 'supported', False)}: "
                         + safe_link(_value(comparison, "source_url", "Source"), _value(comparison, "source_url")),
                         f"  {tr('已有假设', 'Prior assumptions')}: {text(_value(comparison, 'prior_assumptions', ''))}",
                         f"  {tr('本次假设', 'Candidate assumptions')}: {text(_value(comparison, 'candidate_assumptions', ''))}",
                         f"  {tr('已有结论', 'Prior conclusion')}: {text(_value(comparison, 'prior_conclusion', ''))}",
                         f"  {tr('本次结论', 'Candidate conclusion')}: {text(_value(comparison, 'candidate_conclusion', ''))}",
                         f"  {text(_value(comparison, 'reasoning', ''))}"]
        if len(comparisons) > 5:
            sections.append(tr("其余文献比较见冻结审查材料。", "Additional comparisons are in the frozen reviewed dossier."))
        for unresolved in search.unresolved:
            sections.append(f"- {tr('原始文献缺口', 'Recorded literature gap')}: {text(unresolved)}")
        for reason in assessment.reasons:
            sections.append(f"- {tr('证据限制', 'Evidence gap')}: {text(reason)}")
        if not obstacles and not search.unresolved and not assessment.reasons:
            sections.append(tr("没有列出的具体障碍不代表检索穷尽或新颖性已确认。",
                               "No listed specific obstacle does not establish exhaustive search or novelty."))
    sections += [tr("### 4. 专家优先检查项与证据入口", "### 4. Expert review priorities and evidence navigation")]
    questions += [tr("独立阅读关键引理，检查是否循环论证、遗漏情形或只证明特例。",
                     "Independently read the key lemmas for circular reasoning, omitted cases and special-case proofs."),
                  tr("核对最接近的已有结果及其假设；LLM 审查和有限测试不构成普遍定理的证明。",
                     "Compare the closest prior results and assumptions; LLM approval and finite tests do not prove a general theorem.")]
    sections.extend(f"- {question}" for question in dict.fromkeys(questions) if question)
    groups = {"formal": [], "proof": [], "sources": []}
    for item in context.files:
        category = "formal" if item.path.endswith(".lean") or "formal" in item.path else (
            "sources" if "literature/" in item.path else "proof")
        groups[category].append(item.path)
    for key, cn, en in [("proof", "证明与审查材料", "Proof and review materials"),
                        ("formal", "形式化材料", "Formal materials"), ("sources", "文献材料", "Literature materials")]:
        paths = groups[key]
        sections.append(f"**{tr(cn, en)}** ({len(paths)}): " + (" · ".join(material_link(context, p) for p in paths[:5]) or "—"))
        if len(paths) > 5:
            sections.append(tr("其余文件及逐文件 SHA-256 见证据清单。", "See the evidence manifest for remaining files and per-file SHA-256 hashes."))
    sections += [tr("### 材料范围与限制", "### Evidence scope and limitations")]
    sections.extend("- " + text(item) for item in context.limitations)
    if context.omitted:
        sections += [tr(f"未纳入的材料：{len(context.omitted)} 项，详见清单 omitted 字段。",
                        f"Omitted material: {len(context.omitted)} entries; see omitted in the manifest.")]
    sections += [LEGACY_END_MARKER, "---", tr("## 完整整理报告", "## Full editorial report")]
    return "\n\n".join(sections) + "\n\n"


def _excerpt(value, limit=180):
    """Bound display only; never use excerpts to infer a proof or resolution."""
    value = " ".join(str(value or "").split())
    return text(value if len(value) <= limit else value[:limit].rstrip() + " …") or "—"


def _unique(values):
    return list(dict.fromkeys(str(value) for value in values if value))


def _group_records(records, identity, *, scoped=False):
    groups = {}
    for item, pointer, origin in records:
        scope = origin.split("/reviews/", 1)[0] if scoped else ""
        key = (scope, identity(item))
        # Records without a stable ID must not overwrite unrelated missing IDs.
        key = key if _value(item, "id") else (key, pointer)
        groups.setdefault(key, []).append((item, pointer, origin))
    return list(groups.values())


def render(run, language):
    """Compact navigation of frozen evidence, with no inferred or translated claims."""
    context = run.organization_context
    if context is None or run.problem is None or language not in {"zh", "en"}:
        raise ValueError("Expert briefing requires a frozen problem and a supported language")
    def tr(cn, en):
        return cn if language == "zh" else en

    dossier_link = material_link(context, "dossier.json", "dossier")
    dossier_target = dossier_link.split("](", 1)[1][:-1] if "](" in dossier_link else None

    def record(pointer, label=None):
        label = text(label or pointer)
        return f"[{label}][frozen-dossier]" if dossier_target else label

    def locator(pointer, label=None):
        # A JSON pointer is a reading locator, not a claim that raw JSON supports anchors.
        return record(pointer, label)

    problem = run.problem
    history_sections = []
    sections = [MARKER, tr("# MathLottery 专家阅读报告", "# MathLottery expert reading report"),
                tr("> 仅整理冻结证据，不新增验证或提升证明、新颖性等级。",
                   "> Frozen evidence only: this does not upgrade proof status or novelty, and adds no verification."),
                tr("## 专家速览", "## Expert quick review"),
                tr("下文为导航摘要，不是完整证明。省略号表示显示截短；完整原文、历史记录和逐项证据见链接的冻结材料及标注的 JSON 路径。原文不自动翻译；历史失败不会因后续通过而消失。",
                   "This is a navigation summary, not a complete proof. Ellipses mark display excerpts; frozen materials and the listed JSON paths contain full text, history and evidence. Source text is not translated; later success does not erase historical failures."),
                f"{tr('来源任务', 'Source task')}: {text(context.source_run_id)} · "
                f"{tr('冻结版本', 'Frozen revision')}: {context.source_revision} · {text(context.captured_at)}",
                f"{tr('快照 SHA-256', 'Snapshot SHA-256')}: `{context.source_sha256}`\n\n"
                f"{tr('原题 SHA-256', 'Problem SHA-256')}: `{context.problem_sha256}`",
                "[Evidence manifest](manifest.json) · " + record("", tr("冻结审查材料（全部记录）", "Frozen dossier (all records)")),
                tr("[直接阅读完整报告](#完整整理报告) · [查看证据索引](#证据索引)",
                   "[Read the full report](#full-editorial-report) · [Evidence index](#evidence-index)"),
                tr("### 1. 原题与候选结论", "### 1. Original problem and candidate claims"),
                f"**{text(problem.title)}**", _excerpt(problem.statement, 650),
                locator("/problem/statement"),
                f"{tr('开放状态', 'Open status')}: {code(problem.status)} · "
                f"{tr('核查日期', 'Checked')}: {text(problem.status_checked_at or 'UNASSESSED')}"]
    if problem.source_url:
        sections.append(safe_link(tr("原始出处", "Original source"), problem.source_url))
    for ci, candidate in enumerate(run.candidates):
        path = f"/candidates/{ci}"
        snapshot = next((v for v in context.candidate_hashes if v["id"] == candidate.id), {})
        sections += [f"**{text(candidate.id)}** · {code(candidate.level)} · scope {code(candidate.scope)}",
                     f"SHA-256: `{candidate.sha256}` · {tr('含审查快照', 'With review snapshot')}: "
                     + code(snapshot.get("snapshot_sha256", "UNAVAILABLE")),
                     _excerpt(candidate.claim, 500), locator(path),
                     f"{tr('假设', 'Assumptions')}: " + _excerpt("; ".join(candidate.assumptions), 300)]
        if candidate.reviews:
            latest = candidate.reviews[-1]
            assessment = latest.evidence_assessment
            obstacles = assessment.obstacles if assessment.policy_version else latest.literature_search.obstacles
            unresolved = _unique(_value(v, "id", "UNNAMED") for v in obstacles
                                 if _value(v, "status", "OPEN") != "RESOLVED" or _value(v, "resolution_supported", False) is not True)
            sections.append(f"**{tr('最新状态', 'Latest status')}**: {code(latest.verdict)} · "
                            f"{tr('原题覆盖', 'Coverage')}={code(latest.original_problem_coverage)} · "
                            f"Lean={code((latest.formal_receipt or {}).get('status', 'UNASSESSED'))} · "
                            f"{tr('新颖性', 'Novelty')}={code(latest.novelty)}")
            if unresolved:
                sections.append(tr(f"最新审查的未解除文献障碍 {len(unresolved)} 项（前 4 项）: ",
                                   f"Latest review: {len(unresolved)} unresolved literature obstacles (first 4): ") + _items(unresolved[:4])
                                + tr("。全部 ID、影响和下一步见第 3 节。", ". All IDs, impacts and next actions appear in section 3."))
    sections.append(tr("### 2. 验证状态、关键步骤与历史失败", "### 2. Verification, key steps and historical failures"))
    for ci, candidate in enumerate(run.candidates):
        path = f"/candidates/{ci}"
        sections.append(f"**{text(candidate.id)}**")
        if not candidate.reviews:
            sections.append(tr("尚无独立验证记录。", "No recorded independent review."))
            continue
        sections.append(_table([tr("审查", "Review"), tr("判断", "Verdict"), tr("原题覆盖", "Coverage"), tr("新颖性", "Novelty")],
                               [[str(i + 1), code(r.verdict), code(r.original_problem_coverage), code(r.novelty)]
                                for i, r in enumerate(candidate.reviews)]))
        # Deduplicate identical historical facts, never distinct failures or verdicts.
        alerts = {}
        for ri, review in enumerate(candidate.reviews):
            base = f"{path}/reviews/{ri}"
            entries = [("issue", value, f"{base}/issues/{i}") for i, value in enumerate(review.issues)]
            entries += [("evidence gate", value, f"{base}/validation_notes/{i}") for i, value in enumerate(review.validation_notes)]
            entries += [(f"{check.id or ('check-' + str(i + 1))} · {check.result} · blocking={check.blocking}",
                         check.claim + " — " + check.reasoning, f"{base}/checks/{i}")
                        for i, check in enumerate(review.checks) if check.result != "SUPPORTED"]
            receipt = review.formal_receipt
            if receipt and receipt.get("status") not in {"KERNEL_REPLAYED", "KERNEL_CHECKED"}:
                entries.append((f"Lean {receipt.get('status', 'UNKNOWN')}", receipt.get("reason", ""), f"{base}/formal_receipt"))
            for kind, value, pointer in entries:
                alerts.setdefault((kind, value), []).append((ri + 1, pointer))
        if alerts:
            sections.append(tr(f"保留 {len(alerts)} 项历史失败/未决检查，详见证据索引；后续通过未删除历史记录。",
                               f"{len(alerts)} historical issues or unresolved checks are retained in the evidence index; later success has not removed them."))
            history_sections.append(f"**{text(candidate.id)}**")
            for (kind, value), occurrences in alerts.items():
                reviews = ",".join(str(v[0]) for v in occurrences)
                history_sections.append(f"- {text(kind)} · {tr('审查', 'review')} {reviews}: {_excerpt(value, 150)} · "
                                        + locator(occurrences[0][1]))
        review = candidate.reviews[-1]
        base = f"{path}/reviews/{len(candidate.reviews) - 1}"
        coverage = review.proof_coverage
        sections += [f"{tr('最新论证审查', 'Latest proof assessment')}: {_excerpt(review.proof_assessment, 180)}",
                     f"{tr('原题对应', 'Statement coverage')}: {_excerpt(review.coverage_explanation, 160)}",
                     f"{tr('新颖性说明', 'Novelty explanation')}: {_excerpt(review.novelty_notes, 140)}",
                     f"{tr('覆盖策略', 'Coverage policy')}: {code(coverage.policy_version or 'UNASSESSED')} · "
                     f"proof_complete={coverage.proof_complete} · statement_aligned={coverage.statement_aligned}"]
        if not coverage.policy_version:
            sections.append(tr("关键步骤覆盖尚未评估，不能从通过标签推断完整性。", "Key-step coverage is unassessed; a verdict label does not imply completeness."))
        if review.proof_steps:
            sections.append(_table([tr("步骤", "Step"), tr("论证路线摘要", "Proof roadmap excerpt")],
                                   [[text(s.id), _excerpt(s.statement, 110)]
                                    for s in review.proof_steps[:6]]))
            if len(review.proof_steps) > 6:
                sections.append(tr("其余步骤 ID（完整路线见记录）: ", "Remaining step IDs (full roadmap in record): ")
                                + _items(s.id for s in review.proof_steps[6:]))
            sections.append(locator(base + "/proof_steps"))
        else:
            sections.append(tr("未记录结构化证明路线，需从完整材料重建。", "No structured proof roadmap recorded; reconstruct it from the full dossier."))
        if review.statement_alignment:
            sections.append(_table([tr("对应维度", "Alignment facet"), tr("判断", "Assessment")],
                                   [[code(a.facet), code(a.assessment)] for a in review.statement_alignment]))
            sections.append(locator(base + "/statement_alignment"))
        for obligation in _unique(candidate.remaining_obligations + review.remaining_obligations + coverage.reasons):
            sections.append(f"- {tr('未完成义务 / 覆盖限制', 'Obligation / coverage limit')}: {_excerpt(obligation, 200)}")
        if coverage.unresolved_steps:
            sections.append(tr("未覆盖步骤: ", "Unresolved steps: ") + _items(coverage.unresolved_steps))
        sections.append(locator(base))
        receipt = review.formal_receipt
        if receipt:
            sections += [f"Lean: {code(receipt.get('status', 'UNKNOWN'))} · {_excerpt(receipt.get('reason', ''), 120)}",
                         f"{tr('声明', 'Declarations')}: {_items(_value(v, 'name', v) for v in receipt.get('declarations', []))}",
                         f"{tr('检查范围', 'Check scope')}: {_excerpt(receipt.get('scope', 'UNKNOWN'), 120)} · "
                         f"{tr('命题对应', 'Statement alignment')}: {code(receipt.get('statement_alignment', 'NOT_CERTIFIED'))}"]
            if receipt.get("artifact"):
                sections.append(material_link(context, receipt["artifact"], tr("冻结执行回执", "Frozen execution receipt")))
        else:
            sections.append(tr("未记录独立 Lean 执行回执。", "No independent Lean execution receipt recorded."))
    sections.append(tr("形式检查仅覆盖回执声明；自然语言原题与形式命题等价性未经外部认证。",
                       "Formal checks cover receipt declarations only; natural-language/formal-statement equivalence has no external certification."))
    literature_summary, literature_index = _literature_brief(run, tr, locator)
    sections += literature_summary
    sections += [tr("### 4. 专家优先检查与材料入口", "### 4. Expert priorities and evidence navigation"),
                 tr("1. 阅读完整证明并复核关键引理、量词和边界；以上摘录不替代逐步检查。\n2. 逐项处理未解决障碍，比较最接近的已有定理。\n3. LLM 审查和有限测试不构成普遍定理的证明。",
                    "1. Read the full proof and check key lemmas, quantifiers and boundaries; excerpts do not replace stepwise review.\n2. Address unresolved obstacles individually and compare the closest prior theorems.\n3. LLM approval and finite tests do not prove a general theorem.")]
    navigation = [tr("### 材料入口与范围限制", "### Material navigation and scope limits")]
    groups = {"formal": [], "proof": [], "sources": []}
    for item in context.files:
        category = "formal" if item.path.endswith(".lean") or "formal" in item.path else (
            "sources" if "literature/" in item.path else "proof")
        groups[category].append(item.path)
    for key, cn, en in [("proof", "证明与审查", "Proof and reviews"), ("formal", "形式化", "Formal"), ("sources", "文献", "Literature")]:
        paths = groups[key]
        navigation.append(f"**{tr(cn, en)}** ({len(paths)}): "
                          + (" · ".join(material_link(context, p, PurePosixPath(p).name) for p in paths[:3]) or "—"))
    navigation.append(tr("全部材料路径、哈希及遗漏项见证据清单。", "The manifest lists every captured path, hash and omitted item."))
    navigation.extend("- " + text(item) for item in _unique(context.limitations))
    if context.omitted:
        navigation.append(tr(f"未纳入材料：{len(context.omitted)} 项，详见清单 omitted。",
                             f"Omitted material: {len(context.omitted)} entries; see omitted in the manifest."))
    sections += [tr("## 证据索引", "## Evidence index"),
                 tr("以下是原始记录的位置索引，不重复完整证明或文献引用；完整内容见冻结 dossier。可[跳至完整整理报告](#完整整理报告)。",
                    "The index locates original records without repeating full proofs or quotations; the frozen dossier contains complete text. [Skip to the full report](#full-editorial-report)."),
                 tr("### 历史问题与失败检查", "### Historical issues and failed checks")]
    sections += history_sections or [tr("未记录历史失败检查。", "No historical failed checks recorded.")]
    sections += literature_index
    sections += navigation
    if dossier_target:
        sections.append(f"[frozen-dossier]: {dossier_target}")
    sections += [END_MARKER, "---", tr("## 完整整理报告", "## Full editorial report")]
    prefix = "\n\n".join(sections) + "\n\n"
    # These are literal excerpts, not generated TeX. Markdown's escaped '['
    # otherwise becomes a display-math opener in the PDF parser. Entities keep
    # the text literal, including source backslashes, without changing real
    # Markdown navigation brackets or the frozen v1 renderer.
    return prefix.replace(r"\[", "&#91;").replace(r"\]", "&#93;")


def _literature_brief(run, tr, locator):
    """Group stable identities, retaining unsupported resolutions and every gap."""
    records = [("/problem", run.problem)]
    records += [(f"/candidates/{ci}/reviews/{ri}", review)
                for ci, candidate in enumerate(run.candidates) for ri, review in enumerate(candidate.reviews)]
    obstacles, comparisons, gaps = [], [], {}
    policies = []
    for base, item in records:
        search, assessment = item.literature_search, item.evidence_assessment
        policies.append(assessment.policy_version or "UNASSESSED")
        selected = assessment if assessment.policy_version else search
        branch = "/evidence_assessment" if assessment.policy_version else "/literature_search"
        obstacles += [(v, f"{base}{branch}/obstacles/{i}", base) for i, v in enumerate(selected.obstacles)]
        comparisons += [(v, f"{base}{branch}/comparisons/{i}", base) for i, v in enumerate(selected.comparisons)]
        for field, values in [("literature_search/unresolved", search.unresolved), ("evidence_assessment/reasons", assessment.reasons),
                              ("literature_search/limitations", search.limitations), ("evidence_assessment/limitations", assessment.limitations)]:
            for i, value in enumerate(values):
                # This exact controller wrapper adds no additional evidence.
                key = value.removeprefix("Unresolved literature gap: ")
                gaps.setdefault(key, []).append(f"{base}/{field}/{i}")
    sections = [tr("### 3. 文献障碍与新颖性", "### 3. Literature obstacles and novelty"),
                tr("按稳定 ID、类型、来源归并；不同来源保留独立条目。历史状态保留，不代表所有旧问题仍未解决。每项链接标注冻结 JSON 路径。",
                   "Grouped by stable ID, kind and source; different sources stay separate. Historical states remain visible, without implying every old issue is still unresolved. Links identify frozen JSON paths."),
                f"{tr('证据策略', 'Evidence policy')}: " + _items(_unique(policies))]
    scoped = len(run.candidates) > 1
    obstacle_groups = _group_records(obstacles, lambda v: (_value(v, "id"), _value(v, "kind"), _value(v, "source_url"),
                                                           _value(v, "description")), scoped=scoped)
    comparison_groups = _group_records(comparisons, lambda v: (_value(v, "id"), _value(v, "source_url"),
                                                               _value(v, "locator")), scoped=scoped)
    known_ids = {_value(group[-1][0], "id") for group in obstacle_groups + comparison_groups}
    related_reasons = {}
    for value in list(gaps):
        match = re.fullmatch(r"Literature obstacle ([A-Za-z0-9_-]+): (.+)", value)
        comparison = re.fullmatch(r"Prior-result comparison ([A-Za-z0-9_-]+) (lacks a checked matching theorem and explicit comparison)", value)
        match = match or comparison
        if match and match[1] in known_ids:
            targets = [group for group in obstacle_groups + comparison_groups
                       if _value(group[-1][0], "id") == match[1]
                       and any(pointer.startswith(origin + "/") for pointer in gaps[value] for _, _, origin in group)]
            # Ambiguous reused IDs remain standalone gaps; do not assign one
            # source's failure to a different source or candidate.
            if len(targets) == 1:
                related_reasons.setdefault(id(targets[0]), []).append(match[2])
                del gaps[value]
    notes = {}

    def note_refs(values):
        ids = []
        for value in _unique(values):
            notes.setdefault(value, f"E{len(notes) + 1}")
            ids.append(notes[value])
        return ", ".join(ids) or "—"

    unresolved_rows, history_rows = [], []
    for group in obstacle_groups:
        item, pointer, _ = group[-1]
        identifier = _value(item, "id", "UNNAMED")
        states = _unique(f"{_value(v, 'status', 'OPEN')} / supported={_value(v, 'resolution_supported', False)}" for v, _, _ in group)
        supported = _value(item, "resolution_supported", False)
        status = _value(item, "status", "OPEN")
        limits = note_refs([_value(v, "resolution_reason", "") for v, _, _ in group] + related_reasons.get(id(group), []))
        history = _items(states) + f"; n={len(group)}; " + tr("限制", "limits") + ": " + limits
        refs = locator(pointer)
        if group[0][1] != pointer:
            refs += " · " + locator(group[0][1])
        label = text(identifier) + (" · " + text(group[-1][2].split("/reviews/", 1)[0]) if scoped else "")
        history_rows.append([label, history, _excerpt(_value(item, "description", ""), 80), refs])
        if status != "RESOLVED" or supported is not True:
            unresolved_rows.append([locator(pointer, identifier) if not scoped else label, code(status) + f" / supported={text(supported)}",
                                    tr("影响: ", "Impact: ") + _excerpt(_value(item, "impact", ""), 60)
                                    + "; " + tr("下一步: ", "Next action: ") + _excerpt(_value(item, "next_action", ""), 90)])
    if unresolved_rows:
        sections += [tr("**仍需处理（包含声称 RESOLVED 但消除证据不受支持的项）**",
                        "**Needs attention (including reported RESOLVED with unsupported evidence)**"),
                     _table(["ID", tr("记录状态 / 历史", "Recorded states / history"),
                             tr("影响与下一步（完整路径见索引）", "Impact and next action (full paths in index)")], unresolved_rows)]
    details = [tr("### 文献障碍历史（全部 ID）", "### Literature obstacle history (all IDs)")]
    if history_rows:
        details.append(_table(["ID", tr("记录状态 / 历史", "Recorded states / history"), tr("描述摘要", "Description excerpt"),
                               tr("完整记录", "Full records")], history_rows))
    if not obstacle_groups:
        sections.append(tr("没有列出的具体障碍不代表检索穷尽或新颖性已确认。", "No listed obstacle establishes exhaustive search or novelty."))
    rows = []
    for group in comparison_groups:
        item, pointer, _ = group[-1]
        identifier = _value(item, "id", "UNNAMED")
        states = _unique(f"{_value(v, 'relation', 'UNKNOWN')} / supported={_value(v, 'supported', False)}" for v, _, _ in group)
        current = code(_value(item, "relation", "UNKNOWN")) + " / " + tr("对照证据受支持", "Comparison evidence supported") + "=" + text(_value(item, "supported", False))
        if len(states) > 1:
            current += "; " + tr("历史: ", "History: ") + _items(states)
        # Keep every comparison, including potentially equivalent results after the first five.
        label = text(identifier) + (" · " + text(group[-1][2].split("/reviews/", 1)[0]) if scoped else "")
        rows.append([label, current,
                     _excerpt(_value(item, "prior_conclusion", ""), 120),
                     note_refs(related_reasons.get(id(group), [])), locator(pointer)])
    if rows:
        details += [tr("**已有结果对照（全部 ID；supported 表示对照证据受支持）**",
                        "**Prior-result comparisons (all IDs; supported indicates matching evidence)**"),
                     _table(["ID", tr("关系 / 历史", "Relation / history"), tr("已有结论摘要", "Prior conclusion excerpt"),
                             tr("限制", "Limits"), tr("完整记录", "Full record")], rows)]
    if notes:
        details += [tr("**证据限制索引（相同理由仅列一次）**", "**Evidence-limit index (each reason once)**"),
                     _table(["ID", tr("限制摘要", "Limit excerpt")], [[identifier, _excerpt(value, 160)] for value, identifier in notes.items()])]
    if gaps:
        details += [tr("**其它检索缺口与范围限制（去重，全部保留）**", "**Other search gaps and scope limits (deduplicated, all retained)**"),
                     _table([tr("摘要", "Excerpt"), tr("完整记录", "Full record")],
                            [[_excerpt(value, 130), locator(pointers[-1])] for value, pointers in gaps.items()])]
    sections.append(tr(f"证据索引保留全部 {len(obstacle_groups)} 个障碍条目、{len(comparison_groups)} 项已有结果对照及 {len(gaps)} 项其它缺口/范围限制；未解除项的来源与比较仍需逐项检查。",
                       f"The evidence index retains all {len(obstacle_groups)} obstacle entries, {len(comparison_groups)} prior-result comparisons and {len(gaps)} other gaps/scope limits; sources and comparisons for unresolved entries still need individual review."))
    return sections, details


def matched_prefix(run, markdown, language):
    """Authenticate old/new guides exactly; markers alone cannot remove user text."""
    for version, marker, renderer in [(VERSION, MARKER, render), ("expert-brief-v1", LEGACY_MARKER, _render_v1)]:
        if markdown.startswith(marker + "\n"):
            prefix = renderer(run, language)
            return (version, prefix) if markdown.startswith(prefix) else None
    return None


def metadata(run, document, language):
    """Old immutable reports stay old; only an exact generated prefix is advertised."""
    match = matched_prefix(run, document.markdown, language)
    if match is None:
        return None
    version, prefix = match
    return {"version": version, "sha256": digest(prefix), "source_sha256": run.organization_context.source_sha256,
            "placement": "report_prefix", "source_language_preserved": True}
