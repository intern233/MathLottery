"""Workspace discovery, reusable local instances and readable startup output."""

from __future__ import annotations

import errno
import http.client
import json
import tomllib
import webbrowser
from pathlib import Path

from mathlottery.providers.network import apply_network_environment
from mathlottery.web.network import detect_access, is_wsl, windows_excluded_ports
from mathlottery.web.service import WebService, workspace_key


def project_directory(path):
    manifest = path / "pyproject.toml"
    try:
        project = tomllib.loads(manifest.read_text()).get("project", {})
        return isinstance(project, dict) and project.get("name") == "mathlottery"
    except (OSError, ValueError):
        return False


def installed_project():
    # Discover an editable checkout at runtime; never persist a machine-specific default.
    return next((path for path in Path(__file__).resolve().parents if project_directory(path)), None)


def resolve_workspace(current, explicit=False):
    if explicit:
        return current.resolve()
    for path in (current.resolve(), *current.resolve().parents):
        if project_directory(path):
            return path
    return installed_project() or current.resolve()


def existing_instance(port):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
    try:
        connection.request("GET", "/api/instance")
        response = connection.getresponse()
        if response.status != 200:
            return None
        data = response.read(8193)
        return json.loads(data) if len(data) <= 8192 else None
    except (OSError, ValueError, http.client.HTTPException):
        return None
    finally:
        connection.close()


def start_server(root, config_path, preferred_port, access, excluded_ports=()):
    from mathlottery.web.server import LocalServer

    expected = {
        "application": "MathLottery", "protocol": 1,
        "workspace_key": workspace_key(root, config_path), "access": access.identity(),
    }
    port, attempts = preferred_port, 0
    while port <= 65535 and attempts < 20:
        reserved_end = max((end for start, end in excluded_ports if start <= port <= end), default=None)
        if reserved_end is not None:
            print(f"Ports {port}-{reserved_end} are reserved by Windows; trying the next port.", flush=True)
            port = reserved_end + 1
            continue
        attempts += 1
        try:
            # Bind first so a conflict/reuse does not initialize the wrong workspace.
            server = LocalServer(None, port, access=access)
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
            if existing_instance(port) == expected:
                return None, port
            print(f"Port {port} is in use; trying the next port.", flush=True)
            port += 1
            continue
        try:
            server.service = WebService(root, config_path)
        except Exception:
            server.server_close()
            raise
        return server, server.server_port
    raise ValueError(f"No available port near {preferred_port}; choose another with --port")


def serve(root, config_path=None, port=8765, open_browser=False, loopback_only=False, wsl_direct=False):
    if loopback_only and wsl_direct:
        raise ValueError("Choose either --loopback-only or --wsl-direct")
    apply_network_environment(root)
    access = detect_access(loopback_only, wsl_direct)
    excluded = windows_excluded_ports() if access.bind == "127.0.0.1" else ()
    server, actual_port = start_server(root, config_path, port, access, excluded_ports=excluded)
    url = access.url(actual_port)
    print(
        f"MathLottery {'is already running' if server is None else 'is ready'}.\n"
        f"Workspace: {root.resolve()}\nPort: {actual_port}\n"
        f"Local: {access.url(actual_port, '127.0.0.1')}", flush=True,
    )
    if access.browser_host != "127.0.0.1":
        print(f"Direct WSL access (explicitly enabled): {url}", flush=True)
    elif is_wsl():
        print(f"Windows: {access.url(actual_port, 'localhost')} (WSL localhost forwarding)", flush=True)
    if open_browser:
        webbrowser.open(url)
    if server is None:
        return
    print("Press Ctrl+C to close the UI server. Research workers keep running.", flush=True)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
