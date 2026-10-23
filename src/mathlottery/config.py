from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, field_validator

from mathlottery.models import Model


class ChatConfig(Model):
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str = "https://api.openai.com/v1"
    reasoning_mode: Literal["standard", "pro"] | None = None
    poll_interval_seconds: float = Field(default=1, gt=0, le=30)
    request_timeout_seconds: float = Field(default=30, gt=0, le=60)
    tools: list[dict] = Field(
        default_factory=lambda: [
            {"type": "web_search"},
            {"type": "code_interpreter", "container": {"type": "auto"}},
        ]
    )

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, value):
        from urllib.parse import urlsplit

        url = urlsplit(value)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username
            or url.password
            or url.query
            or url.fragment
        ):
            raise ValueError("API base URL must be HTTP(S), without credentials, query or fragment")
        return value.rstrip("/")


class BackendConfig(Model):
    mode: Literal["chat", "codex", "work", "manual"] = "codex"
    execution: Literal["native", "structured"] = "native"
    chat: ChatConfig = Field(default_factory=ChatConfig)
    codex_command: str = "codex"
    model: str | None = None
    reasoning_effort: str | None = None
    codex_profile: str | None = None
    native_turn_timeout_seconds: float | None = Field(default=None, gt=0)
    native_web_search: Literal["live", "cached", "disabled"] = "live"
    native_network_access: bool = True
    # None inherits the isolated Codex configuration; reviews always disable memories.
    native_multi_agent: bool | None = None
    native_memories: bool | None = None
    native_max_log_bytes: int = Field(default=100_000_000, ge=100000)
    timeout_seconds: int = Field(default=300, gt=0)
    max_retries: int = Field(default=2, ge=0, le=5)


class BudgetConfig(Model):
    max_wall_time_minutes: float = Field(default=180, gt=0)
    max_iterations: int = Field(default=50, gt=0)
    max_input_tokens: int | None = Field(default=None, gt=0)
    max_output_tokens: int | None = Field(default=None, gt=0)
    # Legacy zero-cost restriction; null delegates API spending limits to the provider account.
    max_external_cost_usd: Literal[0] | None = None


class ToolConfig(Model):
    timeout_seconds: float = Field(default=15, gt=0, le=300)
    memory_mb: int = Field(default=512, ge=128, le=8192)
    max_output_chars: int = Field(default=20000, ge=100, le=100000)
    web_timeout_seconds: float = Field(default=15, gt=0, le=60)
    web_interval_seconds: float = Field(default=3, ge=0)
    max_download_bytes: int = Field(default=2000000, ge=1000, le=10000000)
    lean_command: str = "lean"


class VerificationConfig(Model):
    fetch_sources: bool = True
    max_sources: int = Field(default=12, ge=1, le=30)
    source_timeout_seconds: float = Field(default=60, gt=0, le=300)
    formal_enabled: bool = True
    lean_command: str = "lean"
    # Trusted prebuilt libraries only; no Lake build or dependency download.
    lean_library_paths: list[str] = Field(default_factory=list, max_length=20)
    formal_timeout_seconds: float = Field(default=120, gt=0, le=600)
    formal_memory_mb: int = Field(default=2048, ge=256, le=8192)
    # Virtual address space includes Lean startup stack reservations and mapped libraries.
    formal_address_space_mb: int = Field(default=8192, ge=1024, le=32768)


class DiscoveryConfig(Model):
    context_max_files: int = Field(default=300, ge=1, le=3000)
    context_max_file_bytes: int = Field(default=8_000_000, ge=1000, le=100_000_000)
    context_max_total_bytes: int = Field(default=32_000_000, ge=1000, le=500_000_000)
    chat_context_max_bytes: int = Field(default=256_000, ge=1000, le=4_000_000)


class Config(Model):
    backend: BackendConfig = Field(default_factory=BackendConfig)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    memory_context_chars: int = Field(default=16000, ge=1000, le=100000)


def load_config(root: Path, path: Path | None = None) -> Config:
    path = path or root / "config.yaml"
    return (
        Config.model_validate(yaml.safe_load(path.read_text()) or {}) if path.exists() else Config()
    )


def duration_minutes(value: str) -> float:
    import re

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)", value.strip())
    if not match or float(match[1]) <= 0:
        raise ValueError("Use a positive duration such as 30s, 20m or 3h")
    return float(match[1]) * {"s": 1 / 60, "m": 1, "h": 60}[match[2]]
