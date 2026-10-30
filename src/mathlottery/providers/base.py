from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from mathlottery.config import BackendConfig
from mathlottery.providers.identity import CodexIdentity
from mathlottery.storage.core import atomic_write, json_text


class BackendStatus(StrEnum):
    COMPLETED = "COMPLETED"
    PENDING_USER = "PENDING_USER"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"
    RATE_LIMITED = "RATE_LIMITED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass
class BackendResult:
    status: BackendStatus
    text: str = ""
    error: str | None = None
    usage: dict = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    invoked: bool = False
    session_id: str | None = None
    runtime: dict = field(default_factory=dict)
    pending: bool = False


class AgentBackend(ABC):
    @abstractmethod
    def capabilities(self) -> dict:
        pass

    @abstractmethod
    def invoke(
        self, prompt: str, schema: dict, directory: Path, timeout: float, cancelled=lambda: False
    ) -> BackendResult:
        pass


class ChatInteractiveBackend(AgentBackend):
    def capabilities(self):
        return {"automatic": False, "usage": False, "billing": "ChatGPT chat handoff"}

    def invoke(self, prompt, schema, directory, timeout, cancelled=lambda: False):
        directory.mkdir(parents=True, exist_ok=True)
        atomic_write(directory / "prompt.md", prompt)
        atomic_write(directory / "response.schema.json", json_text(schema))
        return BackendResult(BackendStatus.PENDING_USER, artifacts=[str(directory / "prompt.md")])


class CodexCLIError(ValueError):
    """Safe installation diagnostics, without executable paths or raw process output."""

    messages = {
        "CLI_NOT_FOUND": "No working Codex CLI found. Install the official CLI in the environment "
        "running MathLottery, then restart MathLottery from that environment and refresh.",
        "CLI_UNAVAILABLE": "The installed Codex CLI could not run. Repair the official CLI "
        "installation in the environment running MathLottery, then refresh.",
        "CLI_PLATFORM_DEPENDENCY_MISSING": "The Codex npm launcher is missing its platform package. "
        "Install the official CLI in the environment running MathLottery. In WSL, install the "
        "Linux CLI inside WSL, then refresh the account status.",
    }

    def __init__(self, code):
        self.code = code
        super().__init__(self.messages[code])


def resolve_codex(
    command: str, deadline: float | None = None, *, env: dict | None = None
) -> str:
    """Skip broken PATH shims, but never replace an explicitly configured executable."""
    candidates = [command]
    if command == "codex":
        candidates = [
            str(Path(p) / "codex") for p in os.get_exec_path(env) if (Path(p) / "codex").is_file()
        ]
    failure = "CLI_NOT_FOUND"
    for candidate in dict.fromkeys(candidates):
        available = 8 if deadline is None else min(8, deadline - time.monotonic())
        if available <= 0:
            raise subprocess.TimeoutExpired("Codex executable detection", 0)
        try:
            result = subprocess.run(
                [candidate, "--version"], capture_output=True, text=True, timeout=available,
                env=env,
            )
            if result.returncode == 0 and "codex" in result.stdout.lower():
                search_path = os.pathsep.join(os.get_exec_path(env))
                return str(Path(shutil.which(candidate, path=search_path) or candidate).absolute())
            if "Missing optional dependency @openai/codex-" in result.stderr:
                failure = "CLI_PLATFORM_DEPENDENCY_MISSING"
            elif failure != "CLI_PLATFORM_DEPENDENCY_MISSING":
                failure = "CLI_UNAVAILABLE"
        except subprocess.TimeoutExpired:
            if deadline is not None and time.monotonic() >= deadline:
                raise
            if failure != "CLI_PLATFORM_DEPENDENCY_MISSING":
                failure = "CLI_UNAVAILABLE"
            continue
        except FileNotFoundError:
            continue
        except OSError:
            if failure != "CLI_PLATFORM_DEPENDENCY_MISSING":
                failure = "CLI_UNAVAILABLE"
    raise CodexCLIError(failure)


class WorkBackend(AgentBackend):
    required_flags = ("--output-schema", "--json", "--ignore-user-config", "--ephemeral")
    def __init__(self, config: BackendConfig, root: Path | None = None):
        self.config = config
        self.identity = CodexIdentity(
            root or Path.cwd(), profile=config.codex_identity, auth=config.codex_auth,
            excluded_env={config.codex_api_key_env, config.chat.api_key_env},
        )
        self.executable: str | None = None
        self.help_text = ""

    def capabilities(self):
        return {"automatic": True, "usage": "reported by Codex",
                "billing": "OpenAI API" if self.config.codex_auth == "api_key" else "ChatGPT Work/Codex"}

    def check(self, timeout: float = 30) -> dict:
        deadline = time.monotonic() + timeout
        self.executable = None
        self.identity.prepare()
        if self.config.codex_auth == "api_key":
            self.api_key()  # Validate availability without sending it to version/help probes.
        environment = self.identity.environment()
        executable = resolve_codex(self.config.codex_command, deadline, env=environment)

        def remaining_timeout():
            available = min(10, deadline - time.monotonic())
            if available <= 0:
                raise subprocess.TimeoutExpired("Codex setup", timeout)
            return available

        if self.config.codex_auth == "chatgpt":
            result = subprocess.run(
                [executable, *self.identity.overrides(), "login", "status"],
                text=True,
                capture_output=True,
                timeout=remaining_timeout(),
                env=environment,
            )
            status = (result.stdout + result.stderr).strip()
            if result.returncode != 0 or "chatgpt" not in status.lower():
                raise ValueError(
                    "MathLottery requires ChatGPT authentication in its isolated account storage "
                    "(not API-key auth). Sign in through MathLottery's account panel; "
                    "your local Codex login is separate."
                )
        result = subprocess.run(
            [executable, "exec", "--help"],
            text=True,
            capture_output=True,
            timeout=remaining_timeout(),
            env=environment,
        )
        self.help_text = result.stdout
        for flag in self.required_flags:
            if flag not in self.help_text:
                raise ValueError(f"Codex CLI is too old: missing {flag}; update the official CLI")
        self.executable = executable
        return {"available": True, "executable": self.executable,
                "authentication": "API key" if self.config.codex_auth == "api_key" else "ChatGPT"}

    def api_key(self) -> str:
        """Read only the explicitly selected variable; never discover or store credentials."""
        value = os.environ.get(self.config.codex_api_key_env)
        if not value or not value.strip() or any(ord(char) < 32 for char in value):
            raise ValueError(
                f"Codex API requires a valid key in {self.config.codex_api_key_env}; "
                "ChatGPT login is not an API-key fallback"
            )
        return value

    def environment(self) -> dict:
        environment = self.identity.environment()
        if self.config.codex_auth == "api_key":
            # Official exec input, set on this child only. Never run `codex login`
            # with the value or put it in command-line/configuration artifacts.
            environment["CODEX_API_KEY"] = self.api_key()
        return environment

    def authentication_overrides(self) -> list[str]:
        credentials = sorted({
            "CODEX_API_KEY", "OPENAI_API_KEY", "CODEX_ACCESS_TOKEN", "CODEX_AUTH_TOKEN",
            self.config.codex_api_key_env, self.config.chat.api_key_env,
            *self.identity.credential_env_names(),
        })
        settings = {
            "forced_login_method": "api" if self.config.codex_auth == "api_key" else "chatgpt",
            "model_provider": "openai",
        }
        result = [item for key, value in settings.items() for item in ("-c", f"{key}={json.dumps(value)}")]
        # Codex applies `set` after `exclude`, and its layered TOML merge does not
        # clear existing entries with set={}. Blank these specific entries so a
        # profile cannot restore a credential. Preserve its other environment
        # settings, including exclusions for additional user-managed secrets.
        for name in credentials:
            result.extend(["-c", f'shell_environment_policy.set.{name}=""'])
        if self.config.codex_auth == "api_key":
            # The built-in provider has reserved routing/authentication settings;
            # overriding model_providers.openai is rejected by current Codex.
            result.extend(["-c", 'openai_base_url="https://api.openai.com/v1"'])
        return result

    def command(self, directory: Path) -> list[str]:
        command = [
            self.executable,
            *self.identity.overrides(),
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--cd",
            str(directory),
            "--output-schema",
            str(directory / "schema.json"),
            "--output-last-message",
            str(directory / "answer.json"),
            *self.authentication_overrides(),
            "-c",
            'approval_policy="never"',
            "-c",
            'web_search="disabled"',
            "-c",
            "mcp_servers={}",
        ]
        for feature in (
            "shell_tool",
            "multi_agent",
            "apps",
            "plugins",
            "browser_use",
            "computer_use",
            "image_generation",
            "hooks",
            "memories",
        ):
            command.extend(["-c", f"features.{feature}=false"])
        if self.config.model:
            command += ["--model", self.config.model]
        if self.config.reasoning_effort:
            command += ["-c", "model_reasoning_effort=" + json.dumps(self.config.reasoning_effort)]
        return command + ["-"]

    def invoke(self, prompt, schema, directory, timeout, cancelled=lambda: False):
        setup_started = time.monotonic()
        try:
            if self.config.codex_auth == "api_key":
                self.api_key()
            if not self.executable:
                self.check(timeout=max(0, timeout))
        except subprocess.TimeoutExpired:
            return BackendResult(
                BackendStatus.INTERRUPTED, error="Time budget exhausted during backend setup"
            )
        except (ValueError, OSError) as error:
            return BackendResult(BackendStatus.UNSUPPORTED, error=str(error))
        timeout -= time.monotonic() - setup_started
        if timeout <= 0:
            return BackendResult(
                BackendStatus.INTERRUPTED, error="Time budget exhausted during backend setup"
            )
        directory.mkdir(parents=True, exist_ok=True)
        if any(
            (directory / name).exists()
            for name in ("answer.json", "command.json", "codex.events.jsonl")
        ):
            return BackendResult(
                BackendStatus.FAILED,
                error="Backend attempt directory already contains artifacts; use a new directory",
            )
        atomic_write(directory / "prompt.md", prompt)
        atomic_write(directory / "schema.json", json_text(schema))
        command = self.command(directory)
        atomic_write(directory / "command.json", json_text(command))
        started = time.monotonic()
        outcome = None
        process = None
        # File-backed output bounds memory. Terminate runaway event logs too.
        with (
            (directory / "codex.events.jsonl").open("w+") as stdout,
            (directory / "codex.stderr.txt").open("w+") as stderr,
            (directory / "prompt.md").open() as stdin,
        ):
            try:
                process = subprocess.Popen(
                    command,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    cwd=directory,
                    env=self.environment(),
                    start_new_session=True,
                )
                while process.poll() is None:
                    if cancelled():
                        outcome = "User requested stop"
                        break
                    if time.monotonic() - started >= timeout:
                        outcome = "Backend timeout; checkpoint preserved"
                        break
                    if (
                        os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size
                        > 20_000_000
                    ):
                        outcome = "Backend output limit reached"
                        break
                    time.sleep(0.1)
            except KeyboardInterrupt:
                outcome = "Interrupted by user"
            except OSError as error:
                return BackendResult(BackendStatus.FAILED, error=str(error))
            finally:
                if process and process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
            stdout.seek(0)
            events_text = stdout.read(20_000_000)
            stderr.seek(0)
            error_text = stderr.read(20000)
        usage = {}
        event_errors = []
        for line in events_text.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                for key, value in event["usage"].items():
                    if isinstance(value, int) and value >= 0:
                        usage[key] = usage.get(key, 0) + value
            if event.get("type") in ("error", "turn.failed"):
                event_errors.append(json.dumps(event))
        metadata = {
            "usage": usage,
            "invoked": True,
            "artifacts": [str(directory / "codex.events.jsonl")],
        }
        if outcome:
            return BackendResult(BackendStatus.INTERRUPTED, error=outcome, **metadata)
        diagnostic = "\n".join(event_errors) + "\n" + error_text
        if process.returncode != 0 or event_errors:
            limited = any(
                term in diagnostic.lower()
                for term in ("rate_limit", "rate limit", "usage limit", "quota", "429")
            )
            return BackendResult(
                BackendStatus.RATE_LIMITED if limited else BackendStatus.FAILED,
                error=diagnostic.strip()[:5000] or "Codex exited unsuccessfully",
                **metadata,
            )
        answer = directory / "answer.json"
        if not answer.exists():
            return BackendResult(
                BackendStatus.FAILED, error="Codex returned no structured answer", **metadata
            )
        return BackendResult(BackendStatus.COMPLETED, text=answer.read_text(), **metadata)
