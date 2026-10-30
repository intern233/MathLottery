"""Public workspace settings, excluding credentials and provider connection details."""

from __future__ import annotations

import os
from pathlib import Path

from mathlottery.config import Config
from mathlottery.models import digest
from mathlottery.providers.catalog import effective_provider


def config_summary(config: Config):
    return {
        "backend": config.backend.mode,
        "provider": effective_provider(config),
        "model": config.backend.model,
        "reasoning_effort": config.backend.reasoning_effort,
        "reasoning_mode": config.backend.chat.reasoning_mode,
        "codex_auth": config.backend.codex_auth,
        "codex_api_key_env": config.backend.codex_api_key_env,
        # Responses provider connection details remain private in run summaries.
        # Codex's editable auth selector needs only its explicit env-variable name.
        "api_key_env": config.backend.codex_api_key_env if (
            config.backend.mode == "codex" and config.backend.codex_auth == "api_key"
        ) else None,
        "api_key_configured": (
            bool(os.environ.get(config.backend.api_key_env_name))
            if config.backend.uses_api_key else None
        ),
        "execution": config.backend.execution,
        "budget_minutes": config.budget.max_wall_time_minutes,
        "max_iterations": config.budget.max_iterations,
        "solve_until_budget_exhausted": config.budget.solve_until_budget_exhausted,
        "solve_parallel_agents": config.solve.parallel_agents,
        "solve_max_groups": config.solve.max_groups,
        "solve_agent_slots": [
            {"id": slot.id, "label": slot.label, "backend": slot.backend.mode,
             "provider": slot.backend.provider or slot.backend.mode,
             "model": slot.backend.model, "reasoning_effort": slot.backend.reasoning_effort,
             "codex_auth": slot.backend.codex_auth}
            for slot in config.solve.agent_slots
        ],
        "finalize_minutes": config.budget.finalize_minutes,
        "native_multi_agent": config.backend.native_multi_agent,
        "native_memories": config.backend.native_memories,
        "native_web_search": config.backend.native_web_search,
        "formal_limits": config.verification.model_dump(
            include={
                "formal_memory_mb",
                "formal_address_space_mb",
                "formal_timeout_seconds",
            }
        ),
        "resource_limits": config.resources.model_dump(),
    }


def workspace_key(root, config_path=None):
    root = Path(root).resolve()
    config_path = (config_path or root / "config.yaml").resolve()
    return digest(str(root) + "\n" + str(config_path))
