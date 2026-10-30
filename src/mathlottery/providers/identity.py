"""Workspace-scoped Codex state, independent of the user's normal CLI login."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from mathlottery.providers.credentials import known_credential_env_names
from mathlottery.providers.network import network_environment


class CodexIdentity:
    def __init__(self, root: Path | None = None, profile: str | None = None, *, auth="chatgpt", excluded_env=()):
        if profile is not None and not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", profile):
            raise ValueError("Invalid MathLottery Codex account identity")
        if auth not in {"chatgpt", "api_key"}:
            raise ValueError("Invalid MathLottery Codex authentication method")
        self.root = Path(root or Path.cwd()).resolve()
        self.profile = profile
        self.auth = auth
        self.excluded_env = set(excluded_env)
        namespace = "codex-api" if auth == "api_key" else "codex"
        self.home = (
            self.root / ".mathlottery" / f"{namespace}-accounts" / profile
            if profile is not None else self.root / ".mathlottery" / f"{namespace}-home"
        )

    def prepare(self):
        """Never adopt, alias or copy the normal Codex credential store."""
        shared = {Path.home() / ".codex"}
        if os.environ.get("CODEX_HOME"):
            shared.add(Path(os.environ["CODEX_HOME"]).expanduser())
        for other in shared:
            other = other.resolve()
            if self.home.is_relative_to(other) or other.is_relative_to(self.home):
                raise ValueError(
                    "MathLottery's Codex directory overlaps the local Codex home. "
                    "Use a separate workspace and leave the normal CODEX_HOME unchanged."
                )
        paths = [self.root / ".mathlottery"]
        if self.profile is not None:
            paths.append(self.home.parent)
        for path in (*paths, self.home):
            if path.is_symlink():
                raise ValueError("MathLottery's private Codex directories cannot be symbolic links")
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in ("auth.json", "config.toml", "sessions", "log"):
            path = self.home / name
            if path.is_symlink() or (path.is_file() and path.stat().st_nlink > 1):
                raise ValueError("MathLottery's Codex auth, configuration and state cannot be linked")
        self.home.chmod(0o700)
        return self.home

    def credential_env_names(self):
        """Read-only exclusion policy for all known workspace connections."""
        return self.excluded_env | known_credential_env_names(self.root)

    def environment(self):
        home = self.prepare()
        # Override only the child process, never the user's shell or global Codex settings.
        excluded = self.credential_env_names()
        env = {key: value for key, value in os.environ.items() if key not in excluded}
        env["CODEX_HOME"] = str(home)
        env["CODEX_SQLITE_HOME"] = str(home)
        return network_environment(self.root, env)

    def overrides(self):
        home = self.prepare()
        # Force a private file store even if a profile or project selects a shared keyring.
        settings = {
            "cli_auth_credentials_store": "file",
            "sqlite_home": str(home),
            "log_dir": str(home / "log"),
        }
        return [item for key, value in settings.items() for item in ("-c", f"{key}={json.dumps(value)}")]
