"""Local instance discovery and WSL host access without changing host networking."""

import errno
import json
import subprocess

import httpx
import pytest
from test_web import serving
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.web import network, startup
from mathlottery.web.network import LocalAccess
from mathlottery.web.server import LocalServer
from mathlottery.web.service import WebService


def test_duplicate_serve_reports_existing_workspace_and_port(tmp_path, monkeypatch, capsys):
    service = WebService(tmp_path)
    monkeypatch.setattr(startup, "detect_access", lambda *args: LocalAccess())
    monkeypatch.setattr(startup, "windows_excluded_ports", lambda: ())
    opened = []
    monkeypatch.setattr(startup.webbrowser, "open", opened.append)
    with serving(service) as (client, server):
        instance = client.get("/api/instance").json()
        assert instance["application"] == "MathLottery"
        assert str(tmp_path) not in json.dumps(instance)
        startup.serve(tmp_path, port=server.server_port, open_browser=True)
        output = capsys.readouterr().out
        assert "already running" in output
        assert f"Port: {server.server_port}" in output
        assert opened == [f"http://127.0.0.1:{server.server_port}"]
        assert client.get("/api/bootstrap").status_code == 200


@pytest.mark.parametrize("different", ["workspace", "config", "access"])
def test_busy_port_cannot_reuse_incompatible_server(tmp_path, different, capsys):
    original = WebService(tmp_path / "original")
    with serving(original) as (_, existing):
        root = tmp_path / "another" if different == "workspace" else original.store.root
        config = root / "different.yaml" if different == "config" else None
        access = LocalAccess(hosts=("127.0.0.1",)) if different == "access" else LocalAccess()
        new, port = startup.start_server(root, config, existing.server_port, access)
        try:
            assert new is not None
            assert port > existing.server_port
            assert new.service.store.root == root
            assert "is in use; trying the next port" in capsys.readouterr().out
        finally:
            new.server_close()


def test_port_exhaustion_does_not_create_workspace_or_kill_processes(tmp_path, monkeypatch):
    def occupied(*args, **kwargs):
        raise OSError(errno.EADDRINUSE, "Address already in use")

    monkeypatch.setattr("mathlottery.web.server.LocalServer", occupied)
    monkeypatch.setattr(startup, "existing_instance", lambda _: None)
    with pytest.raises(ValueError, match="choose another with --port"):
        startup.start_server(tmp_path, None, 8765, LocalAccess())
    assert not (tmp_path / ".mathlottery").exists()


def test_unrelated_listener_does_not_look_like_mathlottery(tmp_path):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    class OtherApp(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html>Another local application</html>")

        def log_message(self, *args):
            pass

    other = ThreadingHTTPServer(("127.0.0.1", 0), OtherApp)
    thread = Thread(target=other.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    try:
        new, port = startup.start_server(tmp_path, None, other.server_port, LocalAccess())
        try:
            assert new is not None and port > other.server_port
        finally:
            new.server_close()
    finally:
        other.shutdown()
        other.server_close()
        thread.join(timeout=2)


def test_editable_checkout_is_found_from_an_unrelated_directory(tmp_path, monkeypatch):
    checkout, other = tmp_path / "MathLottery", tmp_path / "other-project"
    checkout.mkdir()
    other.mkdir()
    (checkout / "pyproject.toml").write_text('[project]\nname = "mathlottery"\n')
    monkeypatch.setattr(startup, "installed_project", lambda: checkout)
    monkeypatch.chdir(other)
    calls = []
    monkeypatch.setattr("mathlottery.web.server.serve", lambda *args: calls.append(args))
    result = CliRunner().invoke(app, ["serve"])
    assert result.exit_code == 0, result.output
    assert calls[0][0] == checkout
    assert not (other / ".mathlottery").exists()
    result = CliRunner().invoke(app, ["--root", ".", "serve", "--loopback-only"])
    assert result.exit_code == 0, result.output
    assert calls[-1][0] == other
    assert calls[-1][-2:] == (True, False)
    result = CliRunner().invoke(app, ["serve", "--wsl-direct"])
    assert result.exit_code == 0, result.output
    assert calls[-1][-2:] == (False, True)


def test_nearest_project_or_explicit_root_wins(tmp_path, monkeypatch):
    project = tmp_path / "checkout"
    nested = project / "docs"
    nested.mkdir(parents=True)
    (project / "pyproject.toml").write_text('[project]\nname = "mathlottery"\n')
    monkeypatch.setattr(startup, "installed_project", lambda: tmp_path / "installed")
    assert startup.resolve_workspace(nested) == project
    assert startup.resolve_workspace(nested, explicit=True) == nested
    monkeypatch.setattr(startup, "installed_project", lambda: None)
    assert startup.resolve_workspace(tmp_path) == tmp_path


def mock_wsl(monkeypatch, mode="nat"):
    monkeypatch.setattr(network.platform, "release", lambda: "test-microsoft-standard-WSL2")
    monkeypatch.setattr(network.shutil, "which", lambda command: command)

    def output(command, **kwargs):
        if command[0] == "wslinfo":
            return mode
        return json.dumps([{"prefsrc": "172.20.0.2", "gateway": "172.20.0.1"}])

    monkeypatch.setattr(network.subprocess, "check_output", output)


def test_wsl_nat_accepts_only_local_machine_and_windows_host(monkeypatch):
    mock_wsl(monkeypatch)
    access = network.detect_access(wsl_direct=True)
    assert access.bind == "0.0.0.0"
    assert access.url(8765) == "http://172.20.0.2:8765"
    assert access.accepts("172.20.0.1")
    assert access.accepts("172.20.0.2")
    assert access.accepts("127.0.0.1")
    assert not access.accepts("172.20.0.3")
    assert not access.accepts("192.168.1.5")
    assert not access.accepts("8.8.8.8")
    assert network.detect_access() == LocalAccess()
    assert network.detect_access(loopback_only=True, wsl_direct=True) == LocalAccess()


@pytest.mark.parametrize("mode", ["mirrored", "none", "virtioproxy"])
def test_other_network_modes_keep_loopback(monkeypatch, mode):
    mock_wsl(monkeypatch, mode)
    assert network.detect_access(wsl_direct=True) == LocalAccess()


def test_detection_failure_keeps_loopback(monkeypatch):
    mock_wsl(monkeypatch)
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("wslinfo", 2)
    monkeypatch.setattr(network.subprocess, "check_output", timeout)
    assert network.detect_access(wsl_direct=True) == LocalAccess()


def test_startup_prints_the_actual_wsl_port_and_browser_address(tmp_path, monkeypatch, capsys):
    mock_wsl(monkeypatch)
    monkeypatch.setattr(LocalServer, "serve_forever", lambda *a, **k: None)
    opened = []
    monkeypatch.setattr(startup.webbrowser, "open", opened.append)
    startup.serve(tmp_path, port=0, open_browser=True, wsl_direct=True)
    output = capsys.readouterr().out
    port = int(next(line for line in output.splitlines() if line.startswith("Port: ")).split()[1])
    assert port > 0
    assert f"Direct WSL access (explicitly enabled): http://172.20.0.2:{port}" in output
    assert opened == [f"http://172.20.0.2:{port}"]


def test_http_rejects_unlisted_peer_even_with_valid_host_and_token(tmp_path):
    with serving(WebService(tmp_path)) as (_, server):
        with httpx.Client(
            transport=httpx.HTTPTransport(local_address="127.0.0.2"), trust_env=False,
        ) as client:
            response = client.get(f"http://127.0.0.1:{server.server_port}/api/bootstrap")
        assert response.status_code == 403
        assert "Windows host" in response.json()["error"]


def test_non_wsl_default_does_not_probe_external_commands(monkeypatch):
    monkeypatch.setattr(network.platform, "release", lambda: "Linux-generic")
    monkeypatch.setattr(network.subprocess, "check_output", lambda *a, **k: pytest.fail("Unexpected command"))
    assert network.detect_access() == LocalAccess()
    assert network.windows_excluded_ports() == ()


def test_wsl_default_does_not_inspect_private_routing(monkeypatch):
    mock_wsl(monkeypatch)
    monkeypatch.setattr(network.subprocess, "check_output", lambda *a, **k: pytest.fail("Unexpected command"))
    assert network.detect_access() == LocalAccess()


def test_windows_reserved_ports_parser_ignores_localized_headers_and_invalid_rows(monkeypatch):
    mock_wsl(monkeypatch)
    output = "协议 TCP 端口排除范围\n开始端口 结束端口\n------- -------\n 8667 8766\n 50000 50059 *\n 0 99\n 900 800\n 65535 65536\n".encode()
    commands = []
    def query(command, **kwargs):
        commands.append(command)
        assert kwargs["timeout"] <= 3
        return output
    monkeypatch.setattr(network.subprocess, "check_output", query)
    assert network.windows_excluded_ports() == ((8667, 8766), (50000, 50059))
    assert commands == [["netsh.exe", "interface", "ipv4", "show", "excludedportrange", "protocol=tcp"]]


def test_windows_reservation_query_failure_leaves_port_selection_available(monkeypatch):
    mock_wsl(monkeypatch)
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("netsh.exe", 3)
    monkeypatch.setattr(network.subprocess, "check_output", timeout)
    assert network.windows_excluded_ports() == ()


def test_windows_reservation_skips_whole_range_before_binding_or_workspace_initialization(tmp_path, monkeypatch, capsys):
    calls = []
    sentinel = object()
    class FakeServer:
        server_port = 9001
        def __init__(self, service, port, access):
            calls.append(port)
    monkeypatch.setattr("mathlottery.web.server.LocalServer", FakeServer)
    monkeypatch.setattr(startup, "WebService", lambda *args: sentinel)
    server, port = startup.start_server(tmp_path, None, 8765, LocalAccess(), ((8600, 9000),))
    assert calls == [9001] and port == 9001 and server.service is sentinel
    assert "Ports 8765-9000 are reserved by Windows" in capsys.readouterr().out
    assert not (tmp_path / ".mathlottery").exists()


def test_default_wsl_startup_prints_and_opens_loopback_url(tmp_path, monkeypatch, capsys):
    mock_wsl(monkeypatch)
    monkeypatch.setattr(startup, "windows_excluded_ports", lambda: ())
    monkeypatch.setattr(LocalServer, "serve_forever", lambda *a, **k: None)
    opened = []
    monkeypatch.setattr(startup.webbrowser, "open", opened.append)
    startup.serve(tmp_path, port=0, open_browser=True)
    output = capsys.readouterr().out
    port = int(next(line for line in output.splitlines() if line.startswith("Port: ")).split()[1])
    assert opened == [f"http://127.0.0.1:{port}"]
    assert f"Windows: http://localhost:{port}" in output
    assert "172.20.0.2" not in output


def test_conflicting_access_flags_fail_before_starting_a_server(tmp_path):
    with pytest.raises(ValueError, match="Choose either"):
        startup.serve(tmp_path, loopback_only=True, wsl_direct=True)
    assert not (tmp_path / ".mathlottery").exists()


def test_editable_discovery_uses_runtime_paths(tmp_path, monkeypatch):
    project = tmp_path / "checkout"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nname = "mathlottery"\n')
    monkeypatch.setattr(startup, "__file__", str(project / "src/mathlottery/web/startup.py"))
    assert startup.installed_project() == project
    (project / "pyproject.toml").unlink()
    assert startup.installed_project() is None
