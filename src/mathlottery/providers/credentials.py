"""Collect credential environment *names* without resolving or changing agent routes.

Every Codex subprocess uses this exclusion set, including ordinary non-pool tasks.
Reading connection settings here does not select any account, provider, or model.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path

import yaml

AUTH_ENV_NAMES = frozenset({
    "OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_ACCESS_TOKEN",
    "CODEX_AUTH_TOKEN", "CODEX_AUTH_JSON", "OPENAI_IDENTITY_TOKEN_FILE",
    "OPENAI_WORKLOAD_IDENTITY_PROVIDER",
})


def _settings(path: Path, *, json_format=False):
    try:
        if not path.exists() and not path.is_symlink():
            return {}
        # Credential storage itself is never traversed. These two files contain
        # only declarative connection settings, and reads are strictly bounded.
        if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError
        limit = 200_000 if json_format else 4_000_000
        with path.open("rb") as file:
            content = file.read(limit + 1)
        if len(content) > limit:
            raise ValueError
        data = json.loads(content) if json_format else yaml.safe_load(content)
        if data is not None and not isinstance(data, Mapping):
            raise ValueError
        return data or {}
    except (OSError, ValueError, UnicodeError, yaml.YAMLError):
        # YAML errors may include arbitrary private input; never forward them.
        raise ValueError("Cannot read local connection settings for credential isolation") from None


def known_credential_env_names(root: Path, config=None) -> set[str]:
    """Include saved/inactive slots and configured providers, not just this task.

    ``config`` additionally supplies an already-loaded config (for example from
    an explicit config path). The selected task's immutable route is untouched.
    """
    root = Path(root)
    if (root / ".mathlottery").is_symlink():
        raise ValueError("Local connection settings must not use linked private directories")
    values = [_settings(root / "config.yaml")]
    if config is not None:
        values.append(config.model_dump() if hasattr(config, "model_dump") else config)
    roster = _settings(root / ".mathlottery" / "agents.json", json_format=True)
    names = set(AUTH_ENV_NAMES)

    def add(value):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", value):
            raise ValueError("Connection settings must name API key environment variables, never key values")
        names.add(value)

    def connection(backend):
        if not isinstance(backend, Mapping):
            return
        if "codex_api_key_env" in backend:
            add(backend["codex_api_key_env"])
        chat = backend.get("chat")
        if isinstance(chat, Mapping) and "api_key_env" in chat:
            add(chat["api_key_env"])

    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError("Invalid configuration for credential isolation")
        connection(value.get("backend"))
        providers = value.get("model_providers") or {}
        if isinstance(providers, Mapping):
            for provider in providers.values():
                connection(provider)
        solve = value.get("solve") or {}
        if isinstance(solve, Mapping):
            for slot in solve.get("agent_slots") or []:
                if isinstance(slot, Mapping):
                    connection(slot.get("backend"))
    for slot in roster.get("slots") or []:
        if isinstance(slot, Mapping):
            connection(slot.get("backend"))
    return names
