"""Optional board actions. Identity and permissions come from the caller, not JSON."""

from typing import Literal

from pydantic import Field, model_validator

from mathlottery.domain.common import Model


class Curation(Model):
    key: str
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    action: Literal["archive", "restore"]
    reason: str = Field(min_length=1, max_length=3000)


class BoardEvent(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    action: Literal["activity", "read", "channel_open", "channel_join", "channel_leave",
                    "channel_message", "channel_close", "channel_ack", "channel_defer", "channel_decline"]
    summary: str = Field(default="", max_length=3000)
    status: Literal["working", "seeking_help", "available", "blocked"] = "working"
    focus: list[str] = Field(
        default_factory=list, max_length=30,
        description="Existing board message keys, e.g. author:lemma-id, never free-text topics. "
        "Use [] when there is no published message yet; describe the topic in summary.",
    )
    channel: str | None = Field(default=None, max_length=200)
    invitees: list[str] = Field(default_factory=list, max_length=32)
    body: str = Field(default="", max_length=12000)
    topic: str = Field(default="", max_length=300)
    approach: str = Field(default="", max_length=1000)
    intent: Literal["explore", "extend", "check"] = "explore"
    overlap_reason: str = Field(default="", max_length=1000)
    through_event: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def meaningful_event(self):
        if self.action in {"activity", "channel_open"} and not self.summary.strip():
            raise ValueError("Describe the current work or channel purpose")
        if self.action == "read" and not self.focus:
            raise ValueError("Read receipts identify exact message keys")
        if self.action.startswith("channel_") and self.action != "channel_open" and not self.channel:
            raise ValueError("Supply an existing channel key")
        if self.action == "channel_message" and not self.body.strip():
            raise ValueError("A channel message cannot be empty")
        if self.action == "channel_ack" and not self.through_event:
            raise ValueError("A read acknowledgement must cite the last observed channel event key")
        if self.action in {"channel_defer", "channel_decline"} and not self.summary.strip():
            raise ValueError("Briefly explain the invitation response")
        return self
