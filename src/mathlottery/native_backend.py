"""Persistent official Codex sessions with native tools and ordinary final answers."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from uuid import UUID

from mathlottery.backends import BackendResult, BackendStatus, WorkBackend
from mathlottery.storage import atomic_write, json_text, safe_path


class NativeWorkBackend(WorkBackend):
    required_flags = ("--json", "--output-last-message", "--sandbox")

    def capabilities(self):
        return {
            **super().capabilities(),
            "persistent_sessions": True,
            "native_tools": True,
            "sandbox": "workspace-write",
            "user_configuration": "inherited with explicit run overrides",
        }

    @staticmethod
    def session_runtime(session_id: str) -> dict:
        """Read only this session's whitelisted runtime metadata, never credentials/history."""
        UUID(session_id)
        sessions = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
        runtime = {}
        try:
            path = next(sessions.rglob(f"*{session_id}*.jsonl"), None)
            if path is None:
                return runtime
            with path.open("rb") as stream:
                size = stream.seek(0, os.SEEK_END)
                offset = max(0, size - 4_000_000)
                stream.seek(offset)
                if offset:
                    stream.readline()
                for line in stream:
                    if b'"turn_context"' not in line:
                        continue
                    try:
                        event = json.loads(line)
                    except (ValueError, UnicodeError):
                        continue
                    if not isinstance(event, dict) or event.get("type") != "turn_context":
                        continue
                    payload = event.get("payload") or {}
                    if not isinstance(payload, dict):
                        continue
                    if isinstance(payload.get("model"), str):
                        runtime["model"] = payload["model"]
                        runtime["model_source"] = "Codex session turn_context"
                    effort = payload.get("effort") or payload.get("reasoning_effort")
                    if isinstance(effort, str):
                        runtime["reasoning_effort"] = effort
                    policy = payload.get("sandbox_policy") or {}
                    if isinstance(policy, dict) and isinstance(policy.get("type"), str):
                        runtime["sandbox"] = policy["type"]
        except OSError:
            pass  # Session formats/storage can change; unknown is not a guessed model name.
        return runtime

    @staticmethod
    def process_start(pid: int) -> str | None:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
            return None if fields[0] == "Z" else fields[19]
        except (OSError, IndexError):
            return None

    @classmethod
    def stop_orphan(cls, directory: Path):
        """Stop only an identified child from this attempt after a runner crash (Linux)."""
        path = directory / "process.json"
        if not path.exists():
            return
        data = json.loads(path.read_text())
        pid, started = data.get("pid"), data.get("start")
        if not isinstance(pid, int) or pid <= 1 or not started:
            return
        if cls.process_start(pid) != started:
            return  # Finished or PID reused; never signal an unrelated process.
        try:
            args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
            if str(directory / "answer.md").encode() not in args or os.getpgid(pid) != pid:
                raise ValueError("Previous native process identity could not be confirmed")
            os.killpg(pid, signal.SIGTERM)
            deadline = time.monotonic() + 2
            while cls.process_start(pid) == started and time.monotonic() < deadline:
                time.sleep(0.05)
            if cls.process_start(pid) == started:
                os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def native_command(
        self, directory: Path, workspace: Path, session_id: str | None, reviewer: bool = False
    ) -> list[str]:
        command = [
            self.executable,
            "exec",
            "--cd",
            str(workspace),
            "--sandbox",
            "workspace-write",
        ]
        if self.config.codex_profile:
            command += ["--profile", self.config.codex_profile]
        if session_id:
            UUID(session_id)  # Never use --last: it can select an unrelated user's conversation.
            command.append("resume")
        command += [
            "--json",
            "--skip-git-repo-check",
            "--output-last-message",
            str(directory / "answer.md"),
        ]
        settings = {
            "forced_login_method": "chatgpt",
            "model_provider": "openai",
            "approval_policy": "never",
            "sandbox_mode": "workspace-write",
            "sandbox_workspace_write.writable_roots": [],
            "sandbox_workspace_write.network_access": self.config.native_network_access,
            "sandbox_workspace_write.exclude_tmpdir_env_var": True,
            "sandbox_workspace_write.exclude_slash_tmp": True,
            "web_search": self.config.native_web_search,
            "features.shell_tool": True,
            "features.multi_agent": False,
        }
        if reviewer:
            settings["features.memories"] = False
        if self.config.reasoning_effort is not None:
            settings["model_reasoning_effort"] = self.config.reasoning_effort
        for key, value in settings.items():
            command += ["-c", f"{key}={json.dumps(value)}"]
        if self.config.model:
            command += ["--model", self.config.model]
        if session_id:
            command.append(session_id)
        return command + ["-"]

    def invoke_native(
        self,
        prompt: str,
        directory: Path,
        workspace: Path,
        timeout: float,
        session_id: str | None = None,
        reviewer: bool = False,
        cancelled=lambda: False,
        on_session=lambda session_id: None,
    ) -> BackendResult:
        started = time.monotonic()
        try:
            if not self.executable:
                self.check(timeout=max(0, timeout))
        except subprocess.TimeoutExpired:
            return BackendResult(
                BackendStatus.INTERRUPTED, error="Codex setup exceeded time budget"
            )
        except (ValueError, OSError) as error:
            return BackendResult(BackendStatus.UNSUPPORTED, error=str(error))
        if time.monotonic() - started >= timeout:
            return BackendResult(BackendStatus.INTERRUPTED, error="Time budget exhausted in setup")
        directory.mkdir(parents=True, exist_ok=True)
        workspace.mkdir(parents=True, exist_ok=True)
        if any((directory / name).exists() for name in ("answer.md", "command.json")):
            return BackendResult(BackendStatus.FAILED, error="Attempt artifacts already exist")
        atomic_write(directory / "prompt.md", prompt)
        command = self.native_command(directory, workspace, session_id, reviewer)
        atomic_write(directory / "command.json", json_text(command))
        environment = self.environment()
        environment["PATH"] = (
            str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
        )
        temp = safe_path(workspace, ".tmp")
        temp.mkdir(exist_ok=True)
        environment["TMPDIR"] = str(temp)
        # The runner's Conda environment supplies Python/SymPy to native shell commands.
        usage, runtime, errors = {}, {}, []
        tools_used = set()
        source_urls = set()
        observed_session, last_message, outcome = session_id, "", None
        saw_session, completed = False, False
        process = None

        def consume(reader):
            nonlocal observed_session, saw_session, last_message, outcome, completed
            while True:
                position = reader.tell()
                line = reader.readline()
                if not line:
                    return
                if not line.endswith("\n"):
                    reader.seek(position)
                    return
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                kind = event.get("type")
                if kind == "thread.started":
                    value = event.get("thread_id")
                    try:
                        value = str(UUID(value))
                    except (ValueError, TypeError, AttributeError):
                        outcome = "Codex emitted an invalid session ID"
                        continue
                    if observed_session and value != observed_session:
                        outcome = "Codex resumed a different session; refusing to mix research"
                        continue
                    observed_session, saw_session = value, True
                    on_session(value)  # Commit immediately, even if the turn is later interrupted.
                if kind == "turn.completed":
                    completed = True
                    for key, value in (event.get("usage") or {}).items():
                        if isinstance(value, int) and value >= 0:
                            usage[key] = usage.get(key, 0) + value
                if kind in ("error", "turn.failed"):
                    errors.append(json.dumps(event, ensure_ascii=False))
                item = event.get("item") or {}
                if isinstance(item, dict):
                    if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                        last_message = item["text"]
                    if item.get("type") in (
                        "command_execution",
                        "web_search",
                        "mcp_tool_call",
                        "file_change",
                    ):
                        tools_used.add(item["type"])
                    if item.get("type") == "web_search":
                        action = item.get("action") or {}
                        if isinstance(action, dict):
                            records = [action, *action.get("sources", [])]
                            for record in records:
                                if isinstance(record, dict) and isinstance(record.get("url"), str):
                                    source_urls.add(record["url"])
                for key in ("model", "reasoning_effort"):
                    if isinstance(event.get(key), str):
                        runtime[key] = event[key]

        event_path = directory / "codex.events.jsonl"
        with (
            event_path.open("w") as stdout,
            event_path.open() as reader,
            (directory / "codex.stderr.txt").open("w+") as stderr,
            (directory / "prompt.md").open() as stdin,
        ):
            try:
                process = subprocess.Popen(
                    command,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    cwd=workspace,
                    env=environment,
                    start_new_session=True,
                )
                atomic_write(
                    directory / "process.json",
                    json_text(
                        {
                            "pid": process.pid,
                            "start": self.process_start(process.pid),
                        }
                    ),
                )
                while process.poll() is None:
                    consume(reader)
                    if outcome:
                        break
                    if cancelled():
                        outcome = "Stop requested or total wall-time budget reached"
                        break
                    if time.monotonic() - started >= timeout:
                        outcome = "Native turn time budget reached; resume the same session"
                        break
                    if (
                        os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size
                        > self.config.native_max_log_bytes
                    ):
                        outcome = "Native event log limit reached; artifacts preserved"
                        break
                    time.sleep(0.1)
            except KeyboardInterrupt:
                outcome = "Interrupted by user; native session preserved"
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
            consume(reader)
            stderr.seek(0)
            diagnostic = "\n".join(errors) + "\n" + stderr.read(20000)
        if observed_session:
            runtime.update(self.session_runtime(observed_session))
        runtime["tools_observed"] = sorted(tools_used)
        runtime["source_urls"] = sorted(source_urls)
        metadata = dict(
            usage=usage,
            invoked=True,
            session_id=observed_session,
            runtime=runtime,
            artifacts=[str(event_path)],
        )
        if outcome:
            return BackendResult(BackendStatus.INTERRUPTED, error=outcome, **metadata)
        if process.returncode != 0 or not completed:
            limited = any(
                word in diagnostic.lower()
                for word in (
                    "rate_limit",
                    "rate limit",
                    "usage limit",
                    "quota",
                    "429",
                )
            )
            return BackendResult(
                BackendStatus.RATE_LIMITED if limited else BackendStatus.FAILED,
                error=diagnostic.strip()[:5000] or "Codex did not complete a native turn",
                **metadata,
            )
        if not saw_session:
            return BackendResult(
                BackendStatus.FAILED,
                error="No native session ID was reported",
                **metadata,
            )
        answer = directory / "answer.md"
        text = answer.read_text() if answer.is_file() else last_message
        if not answer.exists():
            atomic_write(answer, text)
        return BackendResult(BackendStatus.COMPLETED, text=text, **metadata)
