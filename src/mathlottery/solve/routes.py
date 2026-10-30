"""Fixed researcher routes, independent of supervision's changing research groups."""

from __future__ import annotations

from mathlottery.config import BackendConfig, Config
from mathlottery.models import digest
from mathlottery.storage.core import json_text


def primary_config(config: Config) -> Config:
    """Pin standalone Solve's supervisor, primary researcher and closing turn to slot 1."""
    if not config.solve.agent_slots:
        return config
    return config.model_copy(
        deep=True, update={"backend": config.solve.agent_slots[0].backend.model_copy(deep=True)}
    )


def slot_config(config: Config, slot_id: str | None) -> Config:
    if slot_id is None:
        if config.solve.agent_slots:
            raise ValueError("Configured Solve attempts must identify their pinned agent slot")
        return config
    slot = next((slot for slot in config.solve.agent_slots if slot.id == slot_id), None)
    if slot is None:
        raise ValueError("The saved Solve agent slot is unavailable; refusing account fallback")
    return config.model_copy(deep=True, update={"backend": slot.backend.model_copy(deep=True)})


def route_metadata(config: Config, slot_id: str | None) -> dict:
    backend = slot_config(config, slot_id).backend
    return {
        "slot_id": slot_id,
        "mode": backend.mode,
        "model": backend.model,
        "provider": backend.provider or backend.mode,
        "codex_auth": backend.codex_auth if backend.mode in {"codex", "work"} else None,
        "route_sha256": route_fingerprint(backend),
    }


def route_fingerprint(backend: BackendConfig) -> str:
    """Keep pre-auth-option checkpoints resumable, without hiding a changed auth route."""
    value = backend.model_dump(mode="json")
    for field, default in (("codex_auth", "chatgpt"), ("codex_api_key_env", "OPENAI_API_KEY")):
        if value[field] == default:
            del value[field]
    return digest(json_text(value))


def attempt_config(config: Config, attempt: dict) -> Config:
    """Recover only through the route that originally created this conversation."""
    selected = slot_config(config, attempt.get("slot_id"))
    expected = attempt.get("route_sha256")
    if expected and expected != route_fingerprint(selected.backend):
        raise ValueError("The saved Solve route changed; refusing to resume with another account")
    return selected


def validate_resume_routes(previous: Config, requested: Config, mode: str | None = None):
    """A continuation may change budgets/groups but never move a session across identities."""
    old = previous.solve.agent_slots
    new = requested.solve.agent_slots
    if not (old or new):
        return
    old_routes = [(slot.id, slot.backend.model_dump(mode="json")) for slot in old]
    new_routes = [(slot.id, slot.backend.model_dump(mode="json")) for slot in new]
    if old_routes != new_routes or requested.solve.parallel_agents != previous.solve.parallel_agents:
        raise ValueError("A saved Solve keeps its agent slots and accounts; start a new Solve to change them")
    if mode and mode != old[0].backend.mode:
        raise ValueError("A saved Solve's primary transport is pinned to its first agent slot")
    if requested.backend != old[0].backend:
        raise ValueError("A saved Solve's primary backend must remain its first agent slot")
