"""Small provider registry and bounded, read-only model discovery.

Catalog entries describe available configuration or reported capabilities, not a
promise that the account can run a model or that a hosted tool is supported.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future

import httpx

from mathlottery.config import Config, ModelChoice

MAX_MODELS = 256
MAX_CATALOG_BYTES = 1_048_576


def effective_provider(config: Config) -> str:
    return config.backend.provider or config.backend.mode


def _choice(item: ModelChoice) -> dict:
    return {**item.model_dump(), "label": item.label or item.id}


def configured_models(config: Config, provider: str) -> list[dict]:
    profile = config.model_providers.get(provider)
    if profile and profile.models:
        return [_choice(item) for item in profile.models]
    if effective_provider(config) == provider and config.backend.model:
        return [_choice(ModelChoice(id=config.backend.model))]
    return []


def provider_choices(config: Config) -> list[dict]:
    def tool_types(tools):
        return sorted({
            item["type"] for item in tools
            if isinstance(item.get("type"), str)
            and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", item["type"])
        })[:30]

    # An active custom provider has already replaced backend.chat. Never present
    # its connection/tool configuration as the built-in OpenAI provider.
    from mathlottery.config import ChatConfig

    chat = config.backend.chat if effective_provider(config) in {"codex", "chat"} else ChatConfig()
    result = [
        {"id": "codex", "label": "Codex", "transport": "codex",
         "reasoning_modes": [], "tool_types": ["native"]},
        {"id": "chat", "label": "OpenAI Responses API", "transport": "responses",
         "reasoning_modes": ["standard", "pro"], "tool_types": tool_types(chat.tools)},
    ]
    result.extend({
        "id": identifier, "label": profile.label, "transport": profile.transport,
        "reasoning_modes": list(profile.reasoning_modes), "tool_types": tool_types(profile.chat.tools),
    } for identifier, profile in config.model_providers.items())
    return result


def _validate_effort(config: Config, models: list[dict]):
    if config.backend.model is None or config.backend.reasoning_effort is None:
        return
    item = next((item for item in models if item["id"] == config.backend.model), None)
    if item and item["reasoning_efforts"] is not None:
        if config.backend.reasoning_effort not in item["reasoning_efforts"]:
            raise ValueError("The selected model does not support this reasoning effort")


def validate_configured_selection(config: Config):
    provider = effective_provider(config)
    if provider in config.model_providers:
        profile = config.model_providers[provider]
        if config.backend.chat.reasoning_mode and config.backend.chat.reasoning_mode not in profile.reasoning_modes:
            raise ValueError("Reasoning mode is not declared by the selected provider")
        _validate_effort(config, [_choice(item) for item in profile.models])


class CatalogError(Exception):
    """Only fixed, credential-free error messages are exposed to the browser."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def _text(value, limit, *, default=""):
    if not isinstance(value, str) or len(value) > limit or any(ord(char) < 32 for char in value):
        return default
    return value.strip()


def normalize_codex_models(value) -> list[dict]:
    rows = value.get("data", []) if isinstance(value, dict) else value
    if not isinstance(rows, list):
        raise CatalogError("CATALOG_INVALID", "The provider returned an invalid model catalog.")
    result, seen = [], set()
    for row in rows[:MAX_MODELS]:
        if not isinstance(row, dict) or row.get("hidden") is True:
            continue
        identifier = _text(row.get("model") or row.get("id"), 200)
        if not identifier or identifier in seen:
            continue
        seen.add(identifier)
        raw_efforts = row.get("supportedReasoningEfforts", row.get("supported_reasoning_efforts"))
        efforts = None
        if isinstance(raw_efforts, list):
            efforts = []
            for entry in raw_efforts[:30]:
                effort = _text(entry.get("reasoningEffort", entry.get("reasoning_effort")) if isinstance(entry, dict) else entry, 50)
                if effort and effort not in efforts:
                    efforts.append(effort)
        default = _text(row.get("defaultReasoningEffort", row.get("default_reasoning_effort")), 50) or None
        if efforts is None or default not in efforts:
            default = None
        result.append({
            "id": identifier,
            "label": _text(row.get("displayName", row.get("display_name")), 200) or identifier,
            "description": _text(row.get("description"), 1000),
            "reasoning_efforts": efforts, "default_reasoning_effort": default,
        })
    return result


def _responses_models(config: Config, provider: str) -> list[dict]:
    from mathlottery.config import ChatConfig

    profile = config.model_providers.get(provider)
    chat = profile.chat if profile else (
        config.backend.chat if effective_provider(config) in {"codex", "chat"} else ChatConfig()
    )
    key = os.environ.get(chat.api_key_env)
    if not key:
        raise CatalogError("API_KEY_MISSING", "Set the selected provider's API key in the server environment, or enter a model ID manually.")
    deadline = time.monotonic() + 15
    models, seen, cursor = [], set(), None
    with httpx.Client(
        base_url=chat.base_url + "/", headers={"Authorization": "Bearer " + key},
        follow_redirects=False,
    ) as client:
        for _ in range(5):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CatalogError("CATALOG_TIMEOUT", "Model discovery timed out; enter a model ID manually or retry.")
            params = {"limit": 100}
            if cursor:
                params["after"] = cursor
            with client.stream("GET", "models", params=params, timeout=min(remaining, 5)) as response:
                if response.status_code in {401, 403}:
                    raise CatalogError("CATALOG_AUTH_REQUIRED", "The selected API account cannot list models; check its credentials or enter a model ID manually.")
                if response.status_code in {404, 405}:
                    raise CatalogError("CATALOG_UNSUPPORTED", "This provider does not offer a model catalog; configure models or enter a model ID manually.")
                response.raise_for_status()
                content = bytearray()
                for chunk in response.iter_bytes():
                    if time.monotonic() >= deadline:
                        raise CatalogError("CATALOG_TIMEOUT", "Model discovery timed out; enter a model ID manually or retry.")
                    content.extend(chunk)
                    if len(content) > MAX_CATALOG_BYTES:
                        raise CatalogError("CATALOG_INVALID", "The provider's model catalog exceeded the response size limit.")
                value = json.loads(content)
            if not isinstance(value, dict) or not isinstance(value.get("data"), list):
                raise CatalogError("CATALOG_INVALID", "The provider returned an invalid model catalog.")
            rows = value["data"]
            for row in rows[:MAX_MODELS]:
                identifier = _text(row.get("id") if isinstance(row, dict) else None, 200)
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    # GET /models does not define reasoning or tool capabilities.
                    models.append(_choice(ModelChoice(id=identifier)))
                    if len(models) >= MAX_MODELS:
                        return models
            if value.get("has_more") is not True:
                break
            next_cursor = _text(value.get("last_id"), 200) or (
                _text(rows[-1].get("id"), 200) if rows and isinstance(rows[-1], dict) else ""
            )
            if not next_cursor or next_cursor == cursor:
                raise CatalogError("CATALOG_INVALID", "The provider returned invalid model pagination.")
            cursor = next_cursor
    return models


class ModelCatalog:
    def __init__(self, config_callback: Callable[[], Config], codex_models_callback: Callable,
                 *, ttl_seconds: float = 30):
        self.config_callback = config_callback
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._inflight = {}
        self._generation = 0
        self._lock = threading.RLock()
        self._loaders = {
            "codex": lambda config, provider: normalize_codex_models(codex_models_callback()),
            "responses": _responses_models,
        }

    def register(self, transport: str, loader: Callable[[Config, str], list[dict]]):
        """Register a read-only catalog adapter when adding a transport implementation."""
        with self._lock:
            self._loaders[transport] = loader
            self.clear()

    def clear(self):
        with self._lock:
            self._generation += 1
            self._cache.clear()
            # Existing callers can finish, but a new account/configuration must
            # never join their requests or reuse their eventual results.
            self._inflight.clear()

    @staticmethod
    def _signature(config: Config, provider: str, connection_signature: str | None = None):
        # Include credential rotation without storing or exposing the key.
        connection_signature = connection_signature or ModelCatalog._connection_signature(config, provider)
        value = config.model_dump_json() + "\n" + connection_signature
        return hashlib.sha256(value.encode()).hexdigest(), provider

    @staticmethod
    def _connection_signature(config: Config, provider: str):
        from mathlottery.config import ChatConfig

        if provider == "codex":
            data = {
                "command": config.backend.codex_command, "profile": config.backend.codex_profile,
                "identity": config.backend.codex_identity,
                "auth": config.backend.codex_auth, "key_env": config.backend.codex_api_key_env,
            }
            credential = os.environ.get(config.backend.codex_api_key_env, "") if (
                config.backend.codex_auth == "api_key"
            ) else ""
        else:
            profile = config.model_providers.get(provider)
            chat = profile.chat if profile else (
                config.backend.chat if effective_provider(config) in {"codex", "chat"} else ChatConfig()
            )
            data = chat.model_dump(exclude={"reasoning_mode"})
            credential = os.environ.get(chat.api_key_env, "")
            if profile:
                data["models"] = [item.model_dump() for item in profile.models]
        return hashlib.sha256((json.dumps(data, sort_keys=True) + "\n" + credential).encode()).hexdigest()

    def validate_selection(self, config: Config):
        """Use configured capabilities and fresh cached metadata; never perform I/O."""
        validate_configured_selection(config)
        provider = effective_provider(config)
        signature = self._connection_signature(config, provider)
        with self._lock:
            for key, cached in self._cache.items():
                if key[1] == provider and cached[2] == signature and time.monotonic() - cached[0] < self.ttl_seconds:
                    _validate_effort(config, cached[1]["models"])

    def get(self, provider: str | None = None, refresh: bool = False, *,
            codex_auth: str | None = None, codex_api_key_env: str | None = None) -> dict:
        try:
            config = self.config_callback()
        except (ValueError, OSError):
            return {
                "providers": [], "provider": provider, "models": [], "source": "unavailable",
                "error": "Model configuration is invalid; check the local configuration file.",
                "error_code": "CONFIG_INVALID",
            }
        provider = provider or effective_provider(config)
        if codex_auth is not None or codex_api_key_env is not None:
            if provider != "codex":
                raise ValueError("Codex catalog authentication applies only to the Codex provider")
            backend = config.backend.model_dump()
            if codex_auth is not None:
                backend["codex_auth"] = codex_auth
            if codex_api_key_env is not None:
                backend["codex_api_key_env"] = codex_api_key_env
            from mathlottery.config import BackendConfig

            config = config.model_copy(update={"backend": BackendConfig.model_validate(backend)})
        providers = provider_choices(config)
        choice = next((item for item in providers if item["id"] == provider), None)
        if choice is None:
            raise ValueError("Unknown model provider; configure it before selecting it")
        connection_signature = self._connection_signature(config, provider)
        key = self._signature(config, provider, connection_signature)
        with self._lock:
            cached = self._cache.get(key)
            if not refresh and cached and time.monotonic() - cached[0] < self.ttl_seconds:
                return copy.deepcopy(cached[1])
            future = self._inflight.get(key)
            leader = future is None
            if leader:
                future = Future()
                self._inflight[key] = future
                generation = self._generation
                loader = self._loaders.get(choice["transport"])
        if not leader:
            return copy.deepcopy(future.result())
        try:
            # Network calls hold no catalog lock: unrelated providers, task
            # validation and account changes remain responsive.
            result = self._load(config, provider, providers, loader)
            with self._lock:
                if generation == self._generation:
                    self._cache = {
                        old_key: entry for old_key, entry in self._cache.items()
                        if old_key[1] != provider and time.monotonic() - entry[0] < self.ttl_seconds
                    }
                    if len(self._cache) >= 32:
                        self._cache.clear()
                    self._cache[key] = (
                        time.monotonic(), copy.deepcopy(result), connection_signature,
                    )
            future.set_result(result)
            return copy.deepcopy(result)
        except BaseException as exc:
            # Release followers even if an adapter aborts outside ordinary
            # provider-error handling. The HTTP boundary still sanitizes errors.
            future.set_exception(exc)
            raise
        finally:
            with self._lock:
                if self._inflight.get(key) is future:
                    del self._inflight[key]

    @staticmethod
    def _load(config, provider, providers, loader):
        fallback = configured_models(config, provider)
        result = {"providers": providers, "provider": provider, "models": fallback,
                  "source": "configured" if fallback else "unavailable",
                  "error": None, "error_code": None}
        profile = config.model_providers.get(provider)
        if profile and profile.models:
            return result
        if provider == "codex" and config.backend.codex_auth == "api_key":
            # Subscription-only app-server metadata must not describe an API-key run.
            # CLI/API model compatibility remains the provider's decision at invocation.
            result.update(
                error="Codex API-key model discovery is not available here; enter an API model ID.",
                error_code="CATALOG_UNSUPPORTED",
            )
            return result
        try:
            if loader is None:
                raise CatalogError("CATALOG_UNSUPPORTED", "Model discovery is not implemented for this transport.")
            models = loader(config, provider)
            # Adapters cannot expose provider-specific unknown fields.
            result["models"] = [_choice(ModelChoice.model_validate({
                key: value for key, value in item.items() if key in ModelChoice.model_fields
            })) for item in models[:MAX_MODELS]]
            result["source"] = "live"
        except Exception as exc:
            if isinstance(exc, CatalogError):
                error = exc
            elif isinstance(exc, (TimeoutError, httpx.TimeoutException)):
                error = CatalogError("CATALOG_TIMEOUT", "Model discovery timed out; enter a model ID manually or retry.")
            else:
                error = CatalogError("CATALOG_UNAVAILABLE", "Model discovery is unavailable; enter a model ID manually or retry.")
            result.update(error=str(error), error_code=error.code)
        return result
