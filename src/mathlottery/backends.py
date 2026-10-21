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
from mathlottery.storage import atomic_write, json_text


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


def resolve_codex(command: str, deadline: float | None = None) -> str:
    """Skip broken PATH shims, but never replace an explicitly configured executable."""
    candidates = [command]
    if command == "codex":
        candidates = [
            str(Path(p) / "codex") for p in os.get_exec_path() if (Path(p) / "codex").is_file()
        ]
    for candidate in dict.fromkeys(candidates):
        available = 8 if deadline is None else min(8, deadline - time.monotonic())
        if available <= 0:
            raise subprocess.TimeoutExpired("Codex executable detection", 0)
        try:
            result = subprocess.run(
                [candidate, "--version"], capture_output=True, text=True, timeout=available
            )
            if result.returncode == 0 and "codex" in result.stdout.lower():
                return str(Path(shutil.which(candidate) or candidate).absolute())
        except subprocess.TimeoutExpired:
            if deadline is not None and time.monotonic() >= deadline:
                raise
            continue
        except OSError:
            continue
    raise ValueError(
        "No working Codex CLI found. Install the Linux Codex CLI, then run codex login."
    )


class WorkBackend(AgentBackend):
    required_flags = ("--output-schema", "--json", "--ignore-user-config", "--ephemeral")
    def __init__(self, config: BackendConfig):
        self.config = config
        self.executable: str | None = None
        self.help_text = ""

    def capabilities(self):
        return {"automatic": True, "usage": "reported by Codex", "billing": "ChatGPT Work/Codex"}

    def check(self, timeout: float = 30) -> dict:
        deadline = time.monotonic() + timeout
        self.executable = None
        executable = resolve_codex(self.config.codex_command, deadline)

        def remaining_timeout():
            available = min(10, deadline - time.monotonic())
            if available <= 0:
                raise subprocess.TimeoutExpired("Codex setup", timeout)
            return available

        result = subprocess.run(
            [executable, "login", "status"],
            text=True,
            capture_output=True,
            timeout=remaining_timeout(),
            env=self.environment(),
        )
        status = (result.stdout + result.stderr).strip()
        if result.returncode != 0 or "chatgpt" not in status.lower():
            raise ValueError(
                "Work mode requires ChatGPT authentication (not API-key auth). "
                f"Run: {executable} login"
            )
        result = subprocess.run(
            [executable, "exec", "--help"],
            text=True,
            capture_output=True,
            timeout=remaining_timeout(),
        )
        self.help_text = result.stdout
        for flag in self.required_flags:
            if flag not in self.help_text:
                raise ValueError(f"Codex CLI is too old: missing {flag}; update the official CLI")
        self.executable = executable
        return {"available": True, "executable": self.executable, "authentication": "ChatGPT"}

    @staticmethod
    def environment() -> dict:
        # Auth remains with the official CLI. Never read its credentials or use API-key fallback.
        return {
            k: v
            for k, v in os.environ.items()
            if k not in {"OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_ACCESS_TOKEN"}
        }

    def command(self, directory: Path) -> list[str]:
        command = [
            self.executable,
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
            "-c",
            'forced_login_method="chatgpt"',
            "-c",
            'model_provider="openai"',
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
