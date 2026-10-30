"""Per-slot account clients and admission checks for the local Agents page."""

from __future__ import annotations

import subprocess
import threading

from mathlottery.providers.agent_roster import AgentRoster, AgentRosterStore
from mathlottery.providers.chat import ChatBackend
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.credentials import known_credential_env_names
from mathlottery.web.account import CodexAccount


class AgentConnections:
    def __init__(self, service, *, account_factory=CodexAccount):
        # Startup binds its socket before loading a workspace. As with the
        # default account/catalog, resolve the service only when it is used.
        self._service = service
        self.account_factory = account_factory
        self.accounts = {}
        self.lock = threading.RLock()

    @property
    def service(self):
        return self._service() if callable(self._service) else self._service

    @property
    def store(self):
        return AgentRosterStore(self.service.store.root)

    def slot(self, identifier):
        for slot in self.store.load().resolved(self.service.config()).slots:
            if slot.id == identifier:
                return slot
        raise ValueError("Unknown agent slot; save its configuration first")

    def excluded_env(self, config=None):
        config = config or self.service.config()
        return tuple(sorted(known_credential_env_names(self.service.store.root, config)))

    def account(self, slot, config=None):
        if slot.backend.mode != "codex" or slot.backend.codex_auth != "chatgpt":
            raise ValueError("API-key slots use server environment keys, not ChatGPT login")
        key = (slot.id, slot.backend.codex_command)
        excluded_env = self.excluded_env(config)
        with self.lock:
            previous = self.accounts.get(key)
            if previous is not None and not set(excluded_env).issubset(
                getattr(previous, "excluded_env", ())
            ):
                self.accounts.pop(key).close()
            if key not in self.accounts:
                command = slot.backend.codex_command
                self.accounts[key] = self.account_factory(
                    lambda: command, root=self.service.store.root, profile=slot.id,
                    excluded_env=excluded_env,
                )
            return self.accounts[key]

    def save(self, roster):
        # Fail before writing if a named provider is missing or capabilities conflict.
        roster = roster.resolved(self.service.config())
        with self.lock:
            self.store.save(roster)
            current = {
                (slot.id, slot.backend.codex_command)
                for slot in roster.slots
                if slot.backend.mode == "codex" and slot.backend.codex_auth == "chatgpt"
            }
            for key in list(self.accounts):
                if key not in current:
                    self.accounts.pop(key).close()
        return self.store.public()

    def operate(self, slot, action="status", *, config=None):
        """Only a pending device login needs a persistent app-server connection."""
        account = self.account(slot, config)
        try:
            operation = account.start if action == "login" else getattr(account, action)
            return operation()
        finally:
            release = getattr(account, "release_idle", None)
            if release is not None:
                release()

    def ensure_ready(self, config):
        """Use the task snapshot, including when the editable roster has since changed."""
        roster = AgentRoster(slots=config.solve.agent_slots).resolved(config)
        if config.budget.max_external_cost_usd == 0 and any(
            slot.backend.uses_api_key for slot in roster.slots
        ):
            raise ValueError("API-key agent slots are blocked by max_external_cost_usd: 0")
        for slot in roster.slots:
            if slot.backend.mode == "codex" and slot.backend.codex_auth == "api_key":
                try:
                    self.ensure_codex_api(slot.backend, config)
                except ValueError as error:
                    raise ValueError(f"Agent {slot.id}: {error}") from None
                continue
            if slot.backend.mode == "chat":
                try:
                    ChatBackend(slot.backend).check()
                except ValueError as error:
                    # check() is local configuration validation, never an API request.
                    raise ValueError(f"Agent {slot.id}: {error}") from None
                continue
            status = self.operate(slot, config=config)
            if not status.get("available"):
                raise ValueError(
                    f"Agent {slot.id}: Codex account is unavailable; refresh this slot on the Agents page"
                )
            if not status.get("authenticated") or (status.get("account") or {}).get("type") not in {
                "chatgpt", "chatgptAuthTokens",
            }:
                raise ValueError(f"Agent {slot.id}: complete ChatGPT sign-in on the Agents page")

    def ensure_codex_api(self, backend_config, config):
        """Check local CLI/key configuration without account RPC or a model request."""
        backend = NativeWorkBackend(backend_config, self.service.store.root)
        backend.identity.excluded_env.update(self.excluded_env(config))
        try:
            backend.check()
        except (OSError, subprocess.SubprocessError):
            raise ValueError("Codex CLI is unavailable or timed out; check its local installation") from None

    def close(self):
        with self.lock:
            for account in self.accounts.values():
                account.close()
            self.accounts.clear()
