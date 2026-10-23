"""Workspace-scoped Codex state, independent of the user's normal CLI login."""

from __future__ import annotations

import json
import os
from pathlib import Path

from mathlottery.local_network import network_environment


class CodexIdentity:
    def __init__(self, root: Path | None = None):
        self.root = Path(root or Path.cwd()).resolve()
        self.home = self.root / ".mathlottery" / "codex-home"

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
        for path in (self.home.parent, self.home):
            if path.is_symlink():
                raise ValueError("MathLottery's private Codex directories cannot be symbolic links")
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in ("auth.json", "config.toml", "sessions", "log"):
            path = self.home / name
            if path.is_symlink() or (path.is_file() and path.stat().st_nlink > 1):
                raise ValueError("MathLottery's Codex auth, configuration and state cannot be linked")
        self.home.chmod(0o700)
        return self.home

    def environment(self):
        home = self.prepare()
        # Override only the child process, never the user's shell or global Codex settings.
        excluded = {
            "OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_ACCESS_TOKEN",
            "CODEX_AUTH_TOKEN", "CODEX_AUTH_JSON",
            "OPENAI_IDENTITY_TOKEN_FILE", "OPENAI_WORKLOAD_IDENTITY_PROVIDER",
        }
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
