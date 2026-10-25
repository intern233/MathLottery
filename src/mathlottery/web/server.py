"""Local HTTP transport with packaged assets and a small JSON API."""

from __future__ import annotations

import hmac
import json
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import parse_qs, quote, urlsplit

from pydantic import ValidationError

from mathlottery.model_catalog import ModelCatalog
from mathlottery.models import Model
from mathlottery.web.account import AccountChangeRequest, CodexAccount
from mathlottery.web.artifacts import read_formal_artifact
from mathlottery.web.jobs import BusyError
from mathlottery.web.model_directory import codex_models
from mathlottery.web.network import LocalAccess
from mathlottery.web.service import ResumeRequest, StartRequest, workspace_key

ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/research-details.js": ("research-details.js", "text/javascript; charset=utf-8"),
    "/history.js": ("history.js", "text/javascript; charset=utf-8"),
    "/outcomes.js": ("outcomes.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/mark.svg": ("mark.svg", "image/svg+xml"),
}
RUN_ROUTE = re.compile(r"/api/runs/(run-[a-f0-9]{12})(?:/(resume|stop|report|artifact|organized|activity))?")


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, service, port=8765, access=None):
        self.service = service
        self.access = access or LocalAccess()
        self.csrf_token = secrets.token_urlsafe(32)
        self.account = CodexAccount(
            lambda: self.service.config().backend.codex_command,
            root=lambda: self.service.store.root,
        )
        self.catalog = ModelCatalog(
            lambda: self.service.config(),
            lambda: codex_models(self.service.config().backend.codex_command, self.service.store.root),
        )
        self.mutation_lock = threading.RLock()
        super().__init__((self.access.bind, port), Handler)
        self.origins = {self.access.url(self.server_port, host) for host in self.access.hosts}
        self.hosts = {urlsplit(origin).netloc for origin in self.origins}
        if self.server_port == 80:
            self.hosts.update(f"{host}:80" for host in self.access.hosts)

    def server_close(self):
        try:
            self.account.close()
        finally:
            super().server_close()


class Handler(BaseHTTPRequestHandler):
    def ensure_backend_ready(self, mode, execution):
        """Reject unready browser tasks before persisting inputs or launching workers."""
        if mode not in {"codex", "work"} or execution != "native":
            return
        status = self.server.account.status()
        if not status.get("available"):
            raise ValueError(
                "MathLottery's isolated Codex backend is unavailable. Install or configure "
                "Codex, then refresh the account panel before starting research."
            )
        account = status.get("account") or {}
        if account.get("type") == "apiKey":
            raise ValueError(
                "Codex research requires a ChatGPT login, but MathLottery is using an API key. "
                "Use Switch account in the MathLottery account panel to sign in with ChatGPT."
            )
        if not status.get("authenticated") or account.get("type") not in {
            "chatgpt", "chatgptAuthTokens",
        }:
            pending = (status.get("login") or {}).get("status") == "pending"
            action = "Complete ChatGPT sign-in" if pending else "Sign in with ChatGPT"
            raise ValueError(
                f"{action} in the MathLottery account panel before starting or resuming "
                "Codex research. Your local Codex CLI / IDE login is separate."
            )

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, format, *args):
        # Requests may contain mathematical text. Keep routine local access logs quiet.
        pass

    def respond(self, status, body, content_type="application/json; charset=utf-8", **headers):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", (
            "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
        ))
        for name, value in headers.items():
            self.send_header(name.replace("_", "-"), value)
        self.end_headers()
        self.wfile.write(body)

    def allowed(self, mutating=False):
        if not self.server.access.accepts(self.client_address[0]):
            self.respond(403, {"error": "Only this computer and its Windows host are accepted"})
            return False
        if self.headers.get("Host") not in self.server.hosts:
            self.respond(403, {"error": "Unrecognized local server address"})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in self.server.origins:
            self.respond(403, {"error": "Cross-origin requests are not accepted"})
            return False
        if mutating and not hmac.compare_digest(
            self.headers.get("X-MathLottery-Token", "").encode(), self.server.csrf_token.encode(),
        ):
            self.respond(403, {"error": "Reload the page to obtain a valid request token"})
            return False
        return True

    def guarded(self, operation):
        try:
            operation()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except BusyError as exc:
            self.respond(409, {"error": str(exc)})
        except ValidationError as exc:
            self.respond(400, {"error": "; ".join(
                f"{'.'.join(map(str, e['loc'])) or 'request'}: {e['msg']}"
                for e in exc.errors(include_input=False, include_url=False)
            )})
        except (ValueError, OSError) as exc:
            self.respond(400, {"error": str(exc)})
        except Exception:
            self.respond(500, {"error": "Local server error; inspect the task state before retrying"})

    def do_GET(self):
        if self.allowed():
            self.guarded(self.get)

    def get(self):
        path = urlsplit(self.path).path
        if path in ASSETS:
            asset, content_type = ASSETS[path]
            data = files("mathlottery.web").joinpath("static", asset).read_bytes()
            self.respond(200, data, content_type)
        elif path == "/api/instance":
            service = self.server.service
            self.respond(200, {
                "application": "MathLottery", "protocol": 1,
                "workspace_key": workspace_key(service.store.root, service.config_path),
                "access": self.server.access.identity(),
            })
        elif path == "/api/bootstrap":
            self.respond(200, {**self.server.service.bootstrap(), "csrf_token": self.server.csrf_token})
        elif path == "/api/account":
            self.respond(200, self.server.account.status())
        elif path == "/api/models":
            query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            if set(query) - {"provider", "refresh"} or any(len(v) != 1 for v in query.values()):
                raise ValueError("Supply one provider and optional refresh=1")
            provider = query.get("provider", [None])[0]
            if provider is not None and (not provider or len(provider) > 100):
                raise ValueError("Invalid model provider ID")
            refresh = query.get("refresh", ["0"])[0]
            if refresh not in {"0", "1"}:
                raise ValueError("Use refresh=0 or refresh=1")
            self.respond(200, self.server.catalog.get(provider, refresh=refresh == "1"))
        elif match := RUN_ROUTE.fullmatch(path):
            run_id, action = match.groups()
            if action is None:
                self.respond(200, self.server.service.detail(run_id))
            elif action == "activity":
                if urlsplit(self.path).query:
                    raise ValueError("Activity downloads do not accept query parameters")
                self.respond(200, self.server.service.activity_archive(run_id), "application/x-ndjson; charset=utf-8",
                             Content_Disposition=f'attachment; filename="{run_id}-activity.jsonl"')
            elif action == "report":
                self.server.service.store.load(run_id)
                report = self.server.service.text_artifact(run_id, "report.md", limit=10000000)
                if report["truncated"]:
                    raise ValueError("Report exceeds the browser download limit; use mathlottery export")
                self.respond(
                    200, report["text"].encode(), "text/markdown; charset=utf-8",
                    Content_Disposition=f'attachment; filename="{run_id}.md"',
                )
            elif action == "organized":
                from mathlottery.organized_reports import read_report

                query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
                if ("format" not in query or set(query) - {"format", "language"}
                        or any(len(values) != 1 for values in query.values())):
                    raise ValueError("Supply one report format and optionally one language: zh or en")
                format = query["format"][0]
                language = query.get("language", [None])[0]
                data = read_report(self.server.service.store, run_id, format, language=language)
                extension, content_type = {
                    "pdf": ("pdf", "application/pdf"),
                    "markdown": ("md", "text/markdown; charset=utf-8"),
                    "bundle": ("zip", "application/zip"),
                    "public_bundle": ("zip", "application/zip"),
                }[format]
                suffix = f".{language}" if language is not None else ""
                if format == "public_bundle":
                    suffix = "-public-text"
                self.respond(200, data, content_type,
                             Content_Disposition=f'attachment; filename="{run_id}-expert-report{suffix}.{extension}"')
            elif action == "artifact":
                service = self.server.service
                service.store.load(run_id)
                query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
                if set(query) != {"path"} or len(query["path"]) != 1 or not query["path"][0]:
                    raise ValueError("Supply exactly one proof artifact path")
                self.respond(
                    200, read_formal_artifact(service.store.run_dir(run_id), query["path"][0]),
                    "text/plain; charset=utf-8",
                    Content_Disposition=(
                        'attachment; filename="proof-source.txt"; filename*=UTF-8\'\''
                        + quote(query["path"][0].rsplit("/", 1)[-1], safe="")
                    ),
                )
            else:
                self.respond(405, {"error": "Use POST for task actions"})
        else:
            self.respond(404, {"error": "Not found"})

    def do_POST(self):
        if self.allowed(mutating=True):
            self.guarded(self.post)

    def post(self):
        if self.headers.get_content_type() != "application/json":
            self.respond(415, {"error": "Use application/json"})
            return
        if self.headers.get("Transfer-Encoding"):
            raise ValueError("Chunked request bodies are not supported")
        length = int(self.headers.get("Content-Length", "-1"))
        if not 0 <= length <= 1_000_000:
            self.respond(413, {"error": "Request body must be at most 1 MB"})
            return
        data = json.loads(self.rfile.read(length))
        path = urlsplit(self.path).path
        if path == "/api/runs":
            with self.server.mutation_lock:
                self.respond(202, self.server.service.start(
                    StartRequest.model_validate(data), ensure_backend=self.ensure_backend_ready,
                    validate_model=self.server.catalog.validate_selection,
                ))
        elif path in {"/api/account/login", "/api/account/cancel"}:
            Model.model_validate(data)
            operation = self.server.account.start if path.endswith("/login") else self.server.account.cancel
            result = operation()
            self.server.catalog.clear()
            self.respond(200, result)
        elif path in {"/api/account/switch", "/api/account/logout"}:
            AccountChangeRequest.model_validate(data)
            with self.server.mutation_lock:
                self.server.service.ensure_account_change_allowed()
                operation = self.server.account.switch if path.endswith("/switch") else self.server.account.logout
                result = operation()
                self.server.catalog.clear()
                self.respond(200, result)
        elif match := RUN_ROUTE.fullmatch(path):
            run_id, action = match.groups()
            if action == "resume":
                with self.server.mutation_lock:
                    self.respond(202, self.server.service.resume(
                        run_id, ResumeRequest.model_validate(data),
                        ensure_backend=self.ensure_backend_ready,
                    ))
            elif action == "stop":
                Model.model_validate(data)
                self.respond(202, self.server.service.stop(run_id))
            elif action == "organized":
                Model.model_validate(data)
                with self.server.mutation_lock:
                    self.respond(200, self.server.service.export_organized(run_id))
            else:
                self.respond(405, {"error": "Unsupported task action"})
        else:
            self.respond(404, {"error": "Not found"})


def serve(root, config_path=None, port=8765, open_browser=False, loopback_only=False, wsl_direct=False):
    from mathlottery.web.startup import serve as start

    return start(root, config_path, port, open_browser, loopback_only, wsl_direct)
