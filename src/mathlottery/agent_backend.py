"""Transport selection is independent of finding, solving and verifying mathematics."""

from typing import Protocol

from mathlottery.backends import BackendResult
from mathlottery.chat_backend import ChatBackend
from mathlottery.config import BackendConfig
from mathlottery.native_backend import NativeWorkBackend


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


def research_backend(config: BackendConfig) -> ResearchBackend:
    if config.mode == "chat":
        return ChatBackend(config)
    if config.mode in {"codex", "work"}:
        return NativeWorkBackend(config)
    raise ValueError("Manual handoff has no automatic agent transport")
