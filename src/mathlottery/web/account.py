"""Account UI over official Codex RPC; credentials stay in Codex's own store."""

from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from urllib.parse import urlsplit

from pydantic import StrictBool, field_validator

from mathlottery.backends import resolve_codex
from mathlottery.codex_identity import CodexIdentity
from mathlottery.models import Model


class AccountChangeRequest(Model):
    confirm_account_change: StrictBool

    @field_validator("confirm_account_change")
    @classmethod
    def acknowledged(cls, value):
        if not value:
            raise ValueError("Confirm this change to the MathLottery account")
        return value


class AccountError(ValueError):
    pass


class AccountRPC:
    """A private, bounded stdio connection, never a network RPC listener."""

    def __init__(self, command, root=None):
        identity = CodexIdentity(root)
        environment = identity.environment()
        executable = resolve_codex(command, time.monotonic() + 10, env=environment)
        self.process = subprocess.Popen(
            [executable, "app-server", "--listen", "stdio://", "-c", 'model_provider="openai"',
             *identity.overrides()],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", cwd=identity.home, env=environment,
        )
        self.messages = queue.Queue(maxsize=128)
        self.notifications = []
        self.sequence = 0
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.call("initialize", {
                "clientInfo": {"name": "mathlottery", "title": "MathLottery", "version": "0.1.0"},
                "capabilities": {},
            })
            self._send({"method": "initialized"})
        except Exception:
            self.close()
            raise

    def _read(self):
        try:
            while line := self.process.stdout.readline(65537):
                if len(line) > 65536:
                    break
                message = json.loads(line)
                if not isinstance(message, dict):
                    break
                self.messages.put_nowait(message)
        except (OSError, ValueError, queue.Full):
            pass
        finally:
            try:
                self.messages.put_nowait(None)
            except queue.Full:
                pass

    def _send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method, params=None, timeout=15):
        self.sequence += 1
        request_id = self.sequence
        self._send({"id": request_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AccountError("Codex account request timed out. Refresh to retry.")
            try:
                message = self.messages.get(timeout=remaining)
            except queue.Empty:
                raise AccountError("Codex account request timed out. Refresh to retry.") from None
            if message is None:
                raise AccountError("Codex account service stopped. Refresh to reconnect.")
            if message.get("id") == request_id:
                if "error" in message:
                    # Provider errors can contain URLs, identifiers or credential details.
                    raise AccountError(
                        "Codex could not complete this account request. For device login, enable "
                        "device-code authentication in ChatGPT security settings and use a current "
                        "official Codex CLI. Retry from the MathLottery account panel."
                    )
                result = message.get("result")
                if not isinstance(result, dict):
                    raise AccountError("Unexpected Codex account response; update the official CLI.")
                return result
            if message.get("method") == "account/login/completed":
                params = message.get("params")
                if isinstance(params, dict):
                    self.notifications.append(params)
                    self.notifications = self.notifications[-8:]

    def close(self):
        try:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=2)
        except (OSError, subprocess.SubprocessError):
            pass
        finally:
            self.reader.join(timeout=1)
            for pipe in (self.process.stdin, self.process.stdout):
                try:
                    pipe.close()
                except OSError:
                    pass


def public_account(account):
    if not isinstance(account, dict):
        return None
    kind = account.get("type")
    if kind not in {"chatgpt", "apiKey", "chatgptAuthTokens"}:
        kind = "other"
    email = account.get("email")
    masked = None
    if isinstance(email, str) and "@" in email:
        local, domain = email.rsplit("@", 1)
        masked = (local[:1] + "***@" + domain)[:200]
    plan = account.get("planType")
    return {"type": kind, "email": masked, "plan_type": plan[:50] if isinstance(plan, str) else None}


class CodexAccount:
    def __init__(self, command, root=None, rpc_factory=AccountRPC):
        self.command = command
        self.root = root
        self.rpc_factory = rpc_factory
        self.rpc = None
        self.pending = None
        self.lock = threading.RLock()

    def _connect(self):
        if self.rpc is None:
            root = self.root() if callable(self.root) else self.root
            self.rpc = self.rpc_factory(self.command(), root=root)

    def _status(self):
        self._connect()
        account = public_account(self.rpc.call("account/read", {"refreshToken": False}).get("account"))
        error = None
        for event in self.rpc.notifications:
            if self.pending and event.get("loginId") == self.pending["id"]:
                if event.get("success") is not True:
                    error = "Sign-in was not completed. You can try again."
                self.pending = None
        self.rpc.notifications.clear()
        if self.pending and time.monotonic() >= self.pending["deadline"]:
            self.rpc.call("account/login/cancel", {"loginId": self.pending["id"]})
            self.pending = None
            error = "Sign-in expired. Start a new sign-in."
        authenticated = bool(account and account["type"] in {"chatgpt", "chatgptAuthTokens"})
        if account is not None and self.pending:
            # Another client of this MathLottery profile may have signed in. Retire the code
            # before dropping it so it cannot later overwrite the newly connected account.
            self.rpc.call("account/login/cancel", {"loginId": self.pending["id"]})
            self.pending = None
        return {
            "available": True, "authenticated": authenticated, "account": account,
            "login": self.pending["public"] if self.pending else None, "error": error,
        }

    def _operate(self, operation, failure_message=None):
        with self.lock:
            try:
                return operation()
            except (OSError, ValueError, subprocess.SubprocessError):
                self._close()
                return {
                    "available": False, "authenticated": False, "account": None, "login": None,
                    "error": failure_message or (
                        "Codex account access failed. Check that a current official Codex CLI "
                        "is installed. Device login requires enabling device-code authentication in "
                        "ChatGPT security settings. Sign in from the MathLottery account panel; "
                        "your normal Codex CLI login is separate."
                    ),
                }

    def status(self):
        return self._operate(self._status)

    def _start(self):
        status = self._status()
        if status["account"] is not None or self.pending:
            return status
        result = self.rpc.call("account/login/start", {"type": "chatgptDeviceCode"})
        login_id = result.get("loginId")
        # Remember the ID before validating, so a malformed login can still be cancelled.
        if isinstance(login_id, str) and 0 < len(login_id) <= 200:
            self.pending = {"id": login_id, "deadline": time.monotonic() + 900, "public": None}
        url, code = result.get("verificationUrl"), result.get("userCode")
        if not isinstance(url, str) or len(url) > 2048:
            raise AccountError("Invalid official verification URL")
        parsed = urlsplit(url)
        if (not self.pending or result.get("type") != "chatgptDeviceCode"
                or parsed.scheme != "https" or parsed.hostname not in {"auth.openai.com", "chatgpt.com"}
                or parsed.username or parsed.password or parsed.port not in {None, 443}
                or not isinstance(code, str) or not 1 <= len(code) <= 64):
            raise AccountError("Invalid official device login response")
        self.pending["public"] = {"status": "pending", "url": url, "user_code": code}
        return {**status, "login": self.pending["public"], "error": None}

    def start(self):
        return self._operate(self._start)

    def _cancel_pending(self):
        if self.pending:
            self.rpc.call("account/login/cancel", {"loginId": self.pending["id"]})
            self.pending = None

    def _logout(self):
        self._connect()
        self._cancel_pending()
        self.rpc.call("account/logout")
        status = self._status()
        if status["account"] is not None:
            raise AccountError("Codex did not confirm sign-out; refresh the account status")
        return status

    def logout(self):
        return self._operate(self._logout, "Sign-out could not be confirmed. Refresh the account "
                             "status before retrying; the previous login may still be active.")

    def switch(self):
        def operation():
            # Repeated clicks/tabs while authorization is pending share that flow.
            if self.pending:
                return self._status()
            self._logout()
            try:
                return self._start()
            except (OSError, ValueError, subprocess.SubprocessError):
                # Sign-out already happened. Never imply that failed authorization
                # restored the old credentials, and never copy credentials to do so.
                try:
                    self._cancel_pending()
                    status = self._status()
                except (OSError, ValueError, subprocess.SubprocessError):
                    self._close()
                    status = {
                        "available": False, "authenticated": False, "account": None, "login": None,
                    }
                return {
                    **status,
                    "error": "The previous login was signed out, but new sign-in could not start. "
                    "Refresh and sign in again. Device login must be enabled in ChatGPT security "
                    "settings. Use the MathLottery account panel; local Codex login is separate.",
                }
        return self._operate(operation, "Account switching could not proceed because sign-out "
                             "was not confirmed. Refresh the account status before retrying.")

    def cancel(self):
        def operation():
            self._cancel_pending()
            return self._status()
        return self._operate(operation)

    def _close(self):
        rpc, pending = self.rpc, self.pending
        self.rpc = None
        self.pending = None
        if rpc:
            try:
                if pending:
                    rpc.call("account/login/cancel", {"loginId": pending["id"]}, timeout=2)
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
            finally:
                try:
                    rpc.close()
                except (OSError, ValueError, subprocess.SubprocessError):
                    pass

    def close(self):
        with self.lock:
            self._close()
