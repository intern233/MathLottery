"""Validated browser requests and explicit, temporary configuration overrides."""

from __future__ import annotations

from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, StrictBool, model_validator

from mathlottery.config import ChatConfig, Config
from mathlottery.models import Model
from mathlottery.providers.catalog import effective_provider, validate_configured_selection


class Overrides(Model):
    use_agent_slots: StrictBool = False
    backend: Literal["codex", "chat"] | None = None
    provider: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]{0,63}$")
    model: str | None = Field(default=None, min_length=1, max_length=200)
    reasoning_effort: str | None = Field(default=None, min_length=1, max_length=50)
    reasoning_mode: Literal["standard", "pro"] | None = None
    budget_minutes: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    max_iterations: int | None = Field(default=None, gt=0)
    solve_until_budget_exhausted: bool | None = None
    solve_parallel_agents: int | None = Field(default=None, ge=1, le=32, strict=True)
    solve_max_groups: int | None = Field(default=None, ge=1, le=32, strict=True)
    native_multi_agent: bool | None = None
    native_memories: bool | None = None
    codex_auth: Literal["chatgpt", "api_key"] | None = None
    codex_api_key_env: str | None = Field(default=None, pattern=r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")

    def apply(self, config: Config) -> Config:
        original_provider = effective_provider(config)
        provider = self.provider or self.backend or original_provider
        mode = provider if provider in {"codex", "chat", "work", "manual"} else "chat"
        unchanged_legacy = provider in {"work", "manual"} and not self.provider and not self.backend
        if (
            provider not in {"codex", "chat"}
            and provider not in config.model_providers
            and not unchanged_legacy
        ):
            raise ValueError("Unknown model provider; configure it before selecting it")
        if self.backend and self.backend != mode:
            raise ValueError("Model provider and backend override conflict")
        data = config.model_dump()
        backend = data["backend"]
        provider_changed = provider != original_provider
        model_changed = "model" in self.model_fields_set and self.model != backend["model"]
        if provider_changed:
            backend["provider"] = provider
            backend["mode"] = mode
            backend["model"] = None
            # Switching away from a custom profile must never inherit its endpoint/key/tools.
            if provider in config.model_providers:
                backend["chat"] = config.model_providers[provider].chat.model_dump()
            elif original_provider in config.model_providers:
                backend["chat"] = ChatConfig().model_dump()
        elif self.provider:
            backend["provider"] = provider
        if provider_changed or model_changed:
            backend["reasoning_effort"] = None
            backend["chat"]["reasoning_mode"] = None
        for field in ("model", "reasoning_effort"):
            if field in self.model_fields_set:
                backend[field] = getattr(self, field)
        for field in ("codex_auth", "codex_api_key_env"):
            value = getattr(self, field)
            if value is not None:
                if mode != "codex":
                    raise ValueError("Codex authentication settings apply only to the Codex backend")
                backend[field] = value
        if "reasoning_mode" in self.model_fields_set:
            if mode != "chat" and self.reasoning_mode is not None:
                raise ValueError("Pro/standard reasoning mode applies only to the chat backend")
            backend["chat"]["reasoning_mode"] = self.reasoning_mode
        config = Config.model_validate(data)
        if self.budget_minutes is not None:
            config.budget.max_wall_time_minutes = self.budget_minutes
        if self.max_iterations is not None:
            config.budget.max_iterations = self.max_iterations
        if self.solve_until_budget_exhausted is not None:
            config.budget.solve_until_budget_exhausted = self.solve_until_budget_exhausted
        if self.solve_parallel_agents is not None:
            config.solve.parallel_agents = self.solve_parallel_agents
        if self.solve_max_groups is not None:
            config.solve.max_groups = self.solve_max_groups
        for field in ("native_multi_agent", "native_memories"):
            if field in self.model_fields_set:
                if config.backend.mode != "codex":
                    raise ValueError("Native agent capabilities apply only to Codex")
                setattr(config.backend, field, getattr(self, field))
        validate_configured_selection(config)
        return config


class StartRequest(Model):
    workflow: Literal["find", "solve", "verify", "organize"]
    language: Literal["en", "zh"] | None = None
    query: str | None = Field(default=None, max_length=30000)
    source: str | None = Field(default=None, max_length=2048)
    count: int = Field(default=5, ge=1, le=50)
    problem_id: str | None = Field(default=None, max_length=100)
    statement: str | None = Field(default=None, max_length=30000)
    title: str | None = Field(default=None, max_length=200)
    proof: str | None = Field(default=None, max_length=100000)
    instructions: str | None = Field(default=None, max_length=30000)
    from_run: str | None = Field(default=None, pattern=r"^run-[a-f0-9]{12}$")
    from_discovery: str | None = Field(default=None, pattern=r"^run-[a-f0-9]{12}$")
    discovery_problem_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    from_candidate_id: str | None = Field(default=None, pattern=r"^candidate-[a-f0-9]{12}$")
    from_candidate_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    source_files: list[str] = Field(default_factory=list, max_length=20)
    options: Overrides = Field(default_factory=Overrides)

    @model_validator(mode="after")
    def inputs(self):
        if self.language is not None and self.workflow != "organize":
            raise ValueError("Report language applies only to organize")
        if self.workflow == "organize":
            if not self.from_run or any(
                (
                    self.problem_id,
                    self.statement,
                    self.proof,
                    self.query,
                    self.source,
                    self.from_discovery,
                    self.discovery_problem_sha256,
                    self.from_candidate_id,
                    self.from_candidate_sha256,
                    self.source_files,
                )
            ):
                raise ValueError(
                    "Organize requires only a reviewed source run, optional language and instructions"
                )
            return self
        if self.from_discovery:
            if (
                self.workflow != "solve"
                or not self.problem_id
                or any((self.from_run, self.statement, self.proof))
            ):
                raise ValueError("Choose a problem ID from Find for a separate Solve task")
            if not self.discovery_problem_sha256:
                raise ValueError("Bind the selected Find problem to its displayed SHA256")
        elif self.discovery_problem_sha256:
            raise ValueError("A discovery problem binding requires a Find run")
        if bool(self.from_candidate_id) != bool(self.from_candidate_sha256):
            raise ValueError("Supply both the source candidate ID and SHA256")
        if (self.from_candidate_id or self.source_files) and not (
            self.workflow == "verify" and self.from_run
        ):
            raise ValueError(
                "Source candidate binding and proof sources require verify from a saved run"
            )
        if any(not path or len(path) > 2048 for path in self.source_files):
            raise ValueError(
                "Each proof source must have a nonempty relative path of at most 2048 characters"
            )
        if self.source:
            url = urlsplit(self.source)
            if (
                url.scheme not in {"https", "http"}
                or not url.hostname
                or url.username
                or url.password
            ):
                raise ValueError("Source must be an HTTP(S) URL without credentials")
        if self.workflow == "find":
            if any((self.problem_id, self.statement, self.proof, self.from_run)):
                raise ValueError("Find accepts selection criteria, not a problem or proof")
        else:
            if self.query or self.source:
                raise ValueError("Selection criteria and source apply only to find")
            if self.from_run:
                if self.workflow != "verify" or any((self.problem_id, self.statement, self.proof)):
                    raise ValueError("Verify from a saved run or a supplied proof, not both")
            else:
                if bool(self.problem_id) == bool(self.statement and self.statement.strip()):
                    raise ValueError("Select a saved problem or enter a nonempty problem statement")
                if self.workflow == "verify" and not (self.proof and self.proof.strip()):
                    raise ValueError("Verification requires a nonempty proof")
                if self.workflow == "solve" and self.proof is not None:
                    raise ValueError("Use verify to review an existing proof")
        return self


class ResumeRequest(Model):
    message: str | None = Field(default=None, max_length=30000)
    budget_minutes: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    max_iterations: int | None = Field(default=None, gt=0)
    solve_until_budget_exhausted: bool | None = None
    solve_parallel_agents: int | None = Field(default=None, ge=1, le=32, strict=True)
    solve_max_groups: int | None = Field(default=None, ge=1, le=32, strict=True)
    formal_memory_mb: int | None = Field(default=None, ge=256, le=32768)
    formal_address_space_mb: int | None = Field(default=None, ge=1024, le=32768)
    formal_timeout_seconds: float | None = Field(default=None, ge=1, le=1800, allow_inf_nan=False)
