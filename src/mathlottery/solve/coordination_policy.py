"""Opt-in, versioned coordination adjustments; never code or resource mutations."""

import json

from pydantic import Field

from mathlottery.domain.common import Model, now
from mathlottery.solve.bulletin.events import rows
from mathlottery.storage.core import json_text


class CoordinationPolicy(Model):
    review_interval_seconds: float = Field(default=300, gt=0, le=86400, allow_inf_nan=False)
    archive_min_age_seconds: int = Field(default=600, ge=60, le=86400, strict=True)
    archive_read_threshold: int = Field(default=0, ge=0, le=100, strict=True)
    board_guidance: str = Field(default="", max_length=3000)
    collaboration_guidance: str = Field(default="", max_length=4000)


class CoordinationUpdate(Model):
    base_revision: int = Field(ge=0, strict=True)
    policy: CoordinationPolicy
    evidence: list[str] = Field(min_length=1, max_length=20)
    rationale: str = Field(min_length=1, max_length=3000)
    expected_effect: str = Field(min_length=1, max_length=3000)
    previous_assessment: str = Field(min_length=1, max_length=3000)


def enabled(run):
    settings = run.config.get("solve", {})
    return bool(settings.get("adaptive_coordination", False)
                and settings.get("parallel_agents")
                and settings.get("coordination", "allocation") == "supervised")


def history(run):
    return [d["coordination_update"] for d in run.native.solve_team.campaign.decisions
            if d.get("coordination_update")]


def defaults(run):
    return CoordinationPolicy(review_interval_seconds=run.config.get("solve", {}).get(
        "board_review_interval_seconds", 300))


def view(run, *, include_history=False):
    updates = history(run)
    latest = next((u for u in reversed(updates) if u["status"] == "applied"), None)
    active = enabled(run)
    policy = CoordinationPolicy.model_validate(latest["after"]) if active and latest else defaults(run)
    result = {"enabled": active, "revision": latest["revision"] if latest else 0,
              "policy": policy.model_dump(mode="json"), "update_count": len(updates)}
    if updates:
        result["last_update"] = {k: updates[-1].get(k) for k in (
            "task_id", "time", "status", "feedback", "rationale", "expected_effect", "previous_assessment",
        )}
    if include_history:
        result["history"] = updates[-10:]
        result["history_path"] = "solve/coordination-policy.json"
    return result


def observation(board, messages=None, events=None):
    messages = board.messages() if messages is None else messages
    events = rows(board) if events is None else events
    return {"research_publications": sum(m["author"] != "supervisor" for m in messages),
            "research_events": sum(e["actor"] != "supervisor" and e["action"] != "read" for e in events)}


def needs_review(run, board):
    if not enabled(run):
        return False
    decisions = run.native.solve_team.campaign.decisions
    previous = decisions[-1].get("coordination_observation") if decisions else None
    return observation(board) != previous


def snapshot(run, board):
    result = view(run)
    messages, events = board.messages(), rows(board)
    result["observation"] = observation(board, messages, events)
    result["metrics"] = {
        "messages": len(messages), "archived": sum(m["archived"] for m in messages),
        "recorded_reads": sum(e["action"] == "read" for e in events),
        "channel_posts": sum(e["action"] == "channel_message" for e in events),
        "research_signals": len(run.native.solve_team.campaign.signals),
        "active_researchers": sum(a["role"] == "research" for a in run.native.solve_team.active_attempts),
    }
    result["evidence_refs"] = [
        "metrics", *[f"board:{m['key']}" for m in messages],
        *[f"event:{e['key']}" for e in events if e["action"] != "read"],
        *[f"signal:{s['task_id']}" for s in run.native.solve_team.campaign.signals],
    ]
    return result


def decide(run, attempt, proposal):
    """Return a receipt to commit with the supervisor decision; failures are advisory."""
    if proposal is None:
        return None
    current = view(run)
    receipt = {"task_id": attempt["task_id"], "time": now(), "status": "rejected",
               "revision": current["revision"], "before": current["policy"],
               # Keep malformed numeric input as quoted text, never non-finite API JSON.
               "proposal_json": json.dumps(proposal, ensure_ascii=False)}
    try:
        frozen = attempt.get("coordination_snapshot", {})
        if not current["enabled"] or not frozen.get("enabled"):
            raise ValueError("Adaptive coordination is disabled by the user for this review")
        if attempt["purpose"] == "closing":
            raise ValueError("Closing supervision summarizes outcomes instead of tuning a finished campaign")
        update = CoordinationUpdate.model_validate(proposal)
        if update.base_revision != current["revision"] or update.base_revision != frozen.get("revision"):
            raise ValueError("Coordination update references a stale policy revision")
        if not set(update.evidence) <= set(frozen.get("evidence_refs", [])):
            raise ValueError("Cite evidence references from this supervision snapshot")
        interval = update.policy.review_interval_seconds
        if not 30 <= interval <= 3600 and interval != defaults(run).review_interval_seconds:
            raise ValueError("Choose a review interval of 30–3600 seconds, or restore the configured default")
        if any(not value.strip() for value in (
            update.rationale, update.expected_effect, update.previous_assessment,
        )):
            raise ValueError("Describe the evidence, expected effect and previous outcome")
        after = update.policy.model_dump(mode="json")
        changed = after != current["policy"]
        receipt.update(status="applied" if changed else "unchanged", after=after,
                       revision=current["revision"] + int(changed),
                       evidence=update.evidence, rationale=update.rationale,
                       expected_effect=update.expected_effect, previous_assessment=update.previous_assessment,
                       observation=frozen.get("observation"), metrics=frozen.get("metrics"))
    except ValueError as error:
        receipt["feedback"] = str(error)
    return receipt


def supervisor_instructions(run):
    if not enabled(run):
        return ("Adaptive coordination is disabled by the user. Omit coordination_update; "
                "ordinary theorem review, archive/restore and voluntary channels remain available.\n")
    return (
        "The user enabled adaptive coordination. At normal supervision checkpoints, inspect "
        "coordination.metrics, evidence_refs, activity and discussions for concrete friction: "
        "duplicated work, unread results, excessive discussion or unmet requests for help. "
        "You may return an optional coordination_update using the schema below. State the "
        "observations, cite snapshot evidence_refs, predict an observable benefit, and assess "
        "the last change honestly (unknown is acceptable; counts are not mathematical progress). "
        "Omit the update when no change is justified. Revert to prior/default settings if worse. "
        "A policy is a full replacement, not a patch: retain settings you intend to keep. "
        "Review intervals may be 30–3600 seconds or the configured default; they are requests "
        "at natural checkpoints, not deadlines that kill a researcher. Archive thresholds only "
        "rank suggestions, never delete or auto-archive. board_guidance and collaboration_guidance "
        "are optional advice for publishing, finding reusable lemmas and voluntary cooperation; "
        "researchers keep their methods and tools. No arbitrary code/config edits, resource/account "
        "changes, weaker proof standards or compulsory channel membership. Changes are scoped to "
        "this run. Use the frozen base_revision. During closing, assess results without tuning.\n"
        + json_text(CoordinationUpdate.model_json_schema())
    )
