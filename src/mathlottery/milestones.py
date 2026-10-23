"""Transport-independent parsing and validation of research milestones."""

import json
import re
from pathlib import Path

from mathlottery.models import NativeCheckpoint, Phase, Run
from mathlottery.storage import safe_path

MAX_MILESTONE_BYTES = 2_000_000


def validate_milestone(run: Run, data: dict) -> NativeCheckpoint:
    value = NativeCheckpoint.model_validate(data)
    if (value.run_id, value.task_id) != (run.id, run.task_id):
        raise ValueError("Stale milestone: run_id and task_id must match the current turn")
    if run.phase == Phase.ORGANIZE:
        if value.kind not in {"progress", "organization", "stop"} or value.problem:
            raise ValueError("An organizing session cannot change the problem, candidate or review")
    elif value.kind == "organization":
        raise ValueError("Only an organizing session can submit an organization report")
    if (
        value.problem
        and run.problem
        and run.phase != Phase.FIND
        and value.problem.statement != run.problem.statement
    ):
        raise ValueError("A supplied problem statement must not be changed")
    if value.kind == "selection" and run.phase != Phase.FIND:
        raise ValueError("Only a finding turn can submit a selection")
    if run.phase == Phase.FIND and value.kind == "candidate":
        raise ValueError("Select problems first; solving is a separate task")
    if run.phase == Phase.VERIFY:
        if value.kind == "candidate" or value.problem:
            raise ValueError("The independent reviewer cannot replace the problem or candidate")
    elif value.kind == "review":
        raise ValueError("Only an independent review turn can submit review")
    if value.kind == "candidate" and not (run.problem or value.problem):
        raise ValueError("Select a precise problem before submitting a candidate")
    return value


def answer_milestone(run: Run, text: str):
    blocks = re.findall(r"(?ms)^```mathlottery\s*\n(.*?)^```\s*$", text)
    if len(blocks) > 1:
        raise ValueError("Use at most one mathlottery milestone block")
    if blocks and len(blocks[0].encode()) > MAX_MILESTONE_BYTES:
        raise ValueError("Milestone exceeds 2 MB; keep detailed experiments in files")
    return (
        validate_milestone(run, json.loads(blocks[0])).model_dump(mode="json") if blocks else None
    )


def read_milestone(run: Run, workspace: Path, answer: str) -> dict | None:
    """Prefer the Codex submission; accept an explicit answer block if no file was written."""
    if run.mode in {"codex", "work"}:
        path = safe_path(workspace, f"submissions/{run.task_id}.json")
        if path.exists():
            if path.stat().st_size > MAX_MILESTONE_BYTES:
                raise ValueError("Milestone exceeds 2 MB; keep detailed experiments in files")
            # An invalid existing file is an error, not permission to choose a conflicting answer.
            return validate_milestone(run, json.loads(path.read_text())).model_dump(mode="json")
    milestone = answer_milestone(run, answer)
    if milestone is None and run.mode != "manual":
        raise ValueError(
            "Missing milestone. Your answer and files are preserved. Register the existing "
            "result with the current run_id and task_id; do not repeat completed research"
        )
    return milestone
