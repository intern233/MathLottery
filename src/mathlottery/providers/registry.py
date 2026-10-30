"""Transport selection is independent of finding, solving and verifying mathematics."""

from pathlib import Path
from typing import Protocol

from mathlottery.config import BackendConfig, Config
from mathlottery.providers.base import BackendResult, WorkBackend
from mathlottery.providers.chat import ChatBackend
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.credentials import known_credential_env_names


class ResearchBackend(Protocol):
    def invoke_native(
        self,
        prompt,
        directory,
        workspace,
        timeout,
        session_id=None,
        reviewer=False,
        cancelled=lambda: False,
        on_session=lambda value: None,
    ) -> BackendResult: ...


def isolate_credentials(backend, config: Config, root: Path):
    """Carry full/frozen configuration exclusions even with an explicit config path."""
    if isinstance(backend, WorkBackend):
        backend.identity.excluded_env.update(known_credential_env_names(root, config))
    return backend


def research_backend(config: BackendConfig, root: Path | None = None, *,
                     workspace_config: Config | None = None) -> ResearchBackend:
    if config.mode == "chat":
        return ChatBackend(config)
    if config.mode in {"codex", "work"}:
        backend = NativeWorkBackend(config, root=root)
        return isolate_credentials(backend, workspace_config, root or Path.cwd()) if (
            workspace_config is not None
        ) else backend
    raise ValueError("Manual handoff has no automatic agent transport")
