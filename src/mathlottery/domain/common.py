"""Shared model policy, identifiers, and workflow/evidence enums."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Phase(StrEnum):
    FIND = "FIND"
    SOLVE = "SOLVE"
    VERIFY = "VERIFY"
    ORGANIZE = "ORGANIZE"
    REPORT = "REPORT"


class Workflow(StrEnum):
    FIND = "find"
    SOLVE = "solve"
    VERIFY = "verify"
    ORGANIZE = "organize"
    PIPELINE = "pipeline"


class State(StrEnum):
    CREATED = "CREATED"
    DISCOVERING = "DISCOVERING"
    SELECTING = "SELECTING"
    SOLVING = "SOLVING"
    VERIFYING = "VERIFYING"
    ORGANIZING = "ORGANIZING"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RATE_LIMITED = "RATE_LIMITED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OpenStatus(StrEnum):
    OPEN = "OPEN"
    SOLVED = "SOLVED"
    PARTIALLY_SOLVED = "PARTIALLY_SOLVED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class Level(StrEnum):
    CANDIDATE = "CANDIDATE"
    SELF_CHECKED = "SELF_CHECKED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"
    EXPERT_REVIEWED = "EXPERT_REVIEWED"
    REJECTED = "REJECTED"


class Action(StrEnum):
    REASON = "REASON"
    SEARCH = "SEARCH"
    DECOMPOSE = "DECOMPOSE"
    PROPOSE_LEMMA = "PROPOSE_LEMMA"
    PROVE_LEMMA = "PROVE_LEMMA"
    TEST_CASES = "TEST_CASES"
    FIND_COUNTEREXAMPLE = "FIND_COUNTEREXAMPLE"
    RUN_CODE = "RUN_CODE"
    FORMALIZE = "FORMALIZE"
    REVISE = "REVISE"
    CHANGE_STRATEGY = "CHANGE_STRATEGY"
    SELECT_PROBLEM = "SELECT_PROBLEM"
    SUBMIT_CANDIDATE = "SUBMIT_CANDIDATE"
    REVIEW = "REVIEW"
    STOP = "STOP"
