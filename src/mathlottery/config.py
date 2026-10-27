from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, field_validator, model_validator

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
    provider: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]{0,63}$")
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
    finalize_minutes: float = Field(
        default=5, ge=0, le=30,
        description="Extra bounded time for one native Solve closing turn after the research "
        "time limit. Zero disables the model closing turn; hard limits still apply.",
    )
    solve_until_budget_exhausted: bool = Field(
        default=False,
        description="Native standalone Solve keeps researching until the active-time budget is "
        "exhausted, even after a complete solution claim. Other hard limits still apply.",
    )
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
    formal_timeout_seconds: float = Field(default=120, gt=0, le=1800)
    formal_memory_mb: int = Field(default=2048, ge=256, le=32768)
    formal_max_object_mb: int = Field(default=16, ge=1, le=1024)
    formal_max_total_object_mb: int = Field(default=960, ge=1, le=4096)
    # Virtual address space includes Lean startup stack reservations and mapped libraries.
    formal_address_space_mb: int = Field(default=8192, ge=1024, le=32768)


class DiscoveryConfig(Model):
    context_max_files: int = Field(default=300, ge=1, le=3000)
    context_max_file_bytes: int = Field(default=8_000_000, ge=1000, le=100_000_000)
    context_max_total_bytes: int = Field(default=32_000_000, ge=1000, le=500_000_000)
    chat_context_max_bytes: int = Field(default=256_000, ge=1000, le=4_000_000)


class ResourceConfig(Model):
    # Admission is shared by CLI and browser jobs within a workspace.
    max_concurrent_runs: int = Field(default=1, ge=1, le=32)
    max_concurrent_formal: int = Field(default=1, ge=1, le=16)
    # Cooperative protection based on sampled resident memory, not a hard OS quota.
    memory_soft_limit_mb: int | None = Field(default=None, ge=256)
    min_available_memory_mb: int = Field(default=256, ge=0)
    sample_interval_seconds: float = Field(default=2, ge=0.1, le=30)


class ModelChoice(Model):
    id: str = Field(min_length=1, max_length=200)
    label: str | None = Field(default=None, min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    # None means the provider has not supplied capability information.
    reasoning_efforts: list[str] | None = Field(default=None, max_length=30)
    default_reasoning_effort: str | None = Field(default=None, max_length=50)

    @field_validator("id", "label", "description", "default_reasoning_effort")
    @classmethod
    def plain_text(cls, value):
        if value is not None and any(ord(char) < 32 for char in value):
            raise ValueError("Model metadata must not contain control characters")
        return value

    @field_validator("reasoning_efforts")
    @classmethod
    def effort_values(cls, values):
        if values is not None and any(
            not value or len(value) > 50 or any(ord(char) < 32 for char in value)
            for value in values
        ):
            raise ValueError("Reasoning effort names must be nonempty short strings")
        return list(dict.fromkeys(values)) if values is not None else None

    @model_validator(mode="after")
    def effort_default(self):
        if self.default_reasoning_effort is not None and (
            self.reasoning_efforts is None
            or self.default_reasoning_effort not in self.reasoning_efforts
        ):
            raise ValueError("Default reasoning effort must be among the declared supported efforts")
        return self


class ModelProvider(Model):
    label: str = Field(min_length=1, max_length=200)
    transport: Literal["responses"] = "responses"
    chat: ChatConfig
    models: list[ModelChoice] = Field(default_factory=list, max_length=256)
    reasoning_modes: list[Literal["standard", "pro"]] = Field(default_factory=list, max_length=2)

    @field_validator("chat", mode="before")
    @classmethod
    def explicit_connection(cls, value):
        fields = value.model_fields_set if isinstance(value, ChatConfig) else value
        if not isinstance(fields, (set, dict)) or not {
            "base_url", "api_key_env", "tools"
        }.issubset(fields):
            raise ValueError("A custom provider must explicitly configure base_url, api_key_env and tools")
        return value

    @model_validator(mode="after")
    def consistent_choices(self):
        if len({item.id for item in self.models}) != len(self.models):
            raise ValueError("Provider model IDs must be unique")
        if self.chat.reasoning_mode and self.chat.reasoning_mode not in self.reasoning_modes:
            raise ValueError("Provider reasoning mode must be explicitly declared")
        return self


class Config(Model):
    backend: BackendConfig = Field(default_factory=BackendConfig)
    model_providers: dict[str, ModelProvider] = Field(default_factory=dict, max_length=30)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    resources: ResourceConfig = Field(default_factory=ResourceConfig)
    memory_context_chars: int = Field(default=16000, ge=1000, le=100000)

    @field_validator("model_providers")
    @classmethod
    def provider_identifiers(cls, values):
        import re

        if any(
            name in {"codex", "chat", "manual", "work"}
            or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name)
            for name in values
        ):
            raise ValueError("Custom provider IDs must be distinct from built-in backends")
        return values

    @model_validator(mode="before")
    @classmethod
    def resolve_provider(cls, value):
        if not isinstance(value, dict):
            return value
        data = dict(value)
        backend = data.get("backend") or {}
        backend = backend.model_dump(exclude_unset=True) if isinstance(backend, BackendConfig) else dict(backend)
        provider = backend.get("provider")
        if provider is None:
            return value
        profiles = data.get("model_providers") or {}
        if provider in {"codex", "chat"}:
            mode = provider
        elif provider in profiles:
            mode = "chat"
            profile = profiles[provider]
            profile = profile if isinstance(profile, ModelProvider) else ModelProvider.model_validate(profile)
            old_chat = backend.get("chat") or {}
            old_chat = old_chat.model_dump() if isinstance(old_chat, ChatConfig) else old_chat
            resolved_chat = profile.chat.model_dump()
            if "reasoning_mode" in old_chat:
                resolved_chat["reasoning_mode"] = old_chat["reasoning_mode"]
            if resolved_chat["reasoning_mode"] and resolved_chat["reasoning_mode"] not in profile.reasoning_modes:
                raise ValueError("Reasoning mode is not declared by the selected provider")
            backend["chat"] = resolved_chat
        else:
            raise ValueError("Unknown model provider; configure it before selecting it")
        if "mode" in backend and backend["mode"] != mode:
            raise ValueError("Model provider and backend mode conflict")
        backend["mode"] = mode
        data["backend"] = backend
        return data


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
