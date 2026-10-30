"""Local, credential-free Solve connection profiles.

Only connection settings and environment variable *names* are persisted here.
Codex owns subscription credentials; all API keys stay in the server environment.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from pydantic import Field, model_validator

from mathlottery.config import AgentSlot, Config
from mathlottery.models import Model
from mathlottery.providers.catalog import validate_configured_selection

MAX_ROSTER_BYTES = 200_000


class AgentRoster(Model):
    slots: list[AgentSlot] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def distinct_connections(self):
        if len({slot.id for slot in self.slots}) != len(self.slots):
            raise ValueError("Agent slot IDs must be unique")
        for slot in self.slots:
            for name in (slot.backend.chat.api_key_env, slot.backend.codex_api_key_env):
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name):
                    raise ValueError("Supply an API key environment variable name, never the API key")
            self._no_embedded_secrets(slot.backend.chat.tools)
        return self

    @staticmethod
    def _no_embedded_secrets(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if re.search(r"api.?key|authorization|password|secret|access.?token|refresh.?token", key, re.I):
                    raise ValueError("Do not store credentials in agent tool settings")
                AgentRoster._no_embedded_secrets(item)
        elif isinstance(value, list):
            for item in value:
                AgentRoster._no_embedded_secrets(item)

    def resolved(self, config: Config) -> AgentRoster:
        """Resolve provider aliases once, then freeze connection details in the run."""
        slots = []
        for slot in self.slots:
            data = config.model_dump()
            data["backend"] = slot.backend.model_dump()
            # A roster is independent of whichever Solve pool is in config.yaml.
            data["solve"]["agent_slots"] = []
            selection = Config.model_validate(data)
            validate_configured_selection(selection)
            backend = selection.backend.model_copy(deep=True)
            # Keep the original provider name for display, but freeze its resolved
            # definition alongside it in the task's existing model_providers snapshot.
            slots.append(AgentSlot(id=slot.id, label=slot.label, backend=backend))
        return AgentRoster(slots=slots)

    def apply(self, config: Config) -> Config:
        if not self.slots:
            raise ValueError("Configure at least one agent on the Agents page before using this pool")
        resolved = self.resolved(config)
        data = config.model_dump()
        data["solve"].update(
            parallel_agents=len(resolved.slots),
            agent_slots=[slot.model_dump() for slot in resolved.slots],
        )
        data["backend"] = resolved.slots[0].backend.model_dump()
        return Config.model_validate(data)


class AgentRosterStore:
    def __init__(self, root):
        self.directory = Path(root).resolve() / ".mathlottery"
        self.path = self.directory / "agents.json"

    def _check_path(self):
        if self.directory.is_symlink() or self.path.is_symlink():
            raise ValueError("Agent settings must not be symbolic links")
        if self.path.exists() and (not self.path.is_file() or self.path.stat().st_nlink != 1):
            raise ValueError("Agent settings must be an unlinked regular file")

    def load(self) -> AgentRoster:
        self._check_path()
        if not self.path.exists():
            return AgentRoster()
        if self.path.stat().st_size > MAX_ROSTER_BYTES:
            raise ValueError("Agent settings exceed the local size limit")
        return AgentRoster.model_validate_json(self.path.read_text())

    def save(self, roster: AgentRoster):
        self._check_path()
        content = roster.model_dump_json(indent=2).encode()
        if len(content) > MAX_ROSTER_BYTES:
            raise ValueError("Agent settings exceed the local size limit")
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._check_path()
        descriptor, temporary = tempfile.mkstemp(prefix=".agents-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "wb") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def public(self):
        roster = self.load()
        return {
            **json.loads(roster.model_dump_json()),
            "key_configured": {
                slot.id: bool(os.environ.get(slot.backend.api_key_env_name))
                for slot in roster.slots if slot.backend.uses_api_key
            },
        }
