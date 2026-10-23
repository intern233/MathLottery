"""Proxy persistence must not leak into exports, override explicit settings or affect auth."""

import json
import os

import pytest
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.codex_identity import CodexIdentity
from mathlottery.config import load_config
from mathlottery.local_network import PROXY_KEYS, NetworkConfigError, network_environment
from mathlottery.web import startup
from mathlottery.web.network import LocalAccess


def save(root, data):
    path = root / ".mathlottery" / "network.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    path.chmod(0o600)
    return path


@pytest.fixture
def no_proxy_env(monkeypatch):
    for key in PROXY_KEYS:
        # Register restoration even for variables which were originally absent.
        monkeypatch.setenv(key, os.environ.get(key, ""))
        monkeypatch.delenv(key)


def test_absent_settings_preserve_environment_and_do_not_create_files(tmp_path):
    before = {"PATH": "/bin", "CODEX_HOME": "personal-placeholder"}
    result = network_environment(tmp_path, before)
    assert result == before and result is not before
    assert not list(tmp_path.iterdir())


def test_workspace_defaults_reach_isolated_codex_without_parent_or_config_changes(tmp_path, no_proxy_env):
    proxy = "http://proxy.example.invalid:8080"
    save(tmp_path, {"HTTPS_PROXY": proxy, "NO_PROXY": "localhost,127.0.0.1,::1"})
    before = dict(os.environ)
    identity = CodexIdentity(tmp_path)
    child = identity.environment()
    assert child["HTTPS_PROXY"] == child["https_proxy"] == proxy
    assert child["NO_PROXY"] == child["no_proxy"] == "localhost,127.0.0.1,::1"
    assert child["CODEX_HOME"] == str(identity.home)
    assert dict(os.environ) == before
    assert proxy not in load_config(tmp_path).model_dump_json()
    assert not (identity.home / "auth.json").exists()


@pytest.mark.parametrize("key", ["HTTPS_PROXY", "https_proxy"])
@pytest.mark.parametrize("value", ["", "http://explicit.example.invalid:9000"])
def test_explicit_environment_wins_over_saved_opposite_case(tmp_path, key, value):
    opposite = "https_proxy" if key.isupper() else "HTTPS_PROXY"
    save(tmp_path, {opposite: "http://saved.example.invalid:8080"})
    result = network_environment(tmp_path, {key: value})
    assert result == {key: value}


@pytest.mark.parametrize("data", [
    {"CODEX_HOME": "private-profile"}, {"OPENAI_API_KEY": "private-secret"},
    {"HTTPS_PROXY": 123}, ["private-secret"],
    {"HTTPS_PROXY": "private\nsecret"}, {"NO_PROXY": "private\0secret"},
    {"HTTPS_PROXY": "private-one", "https_proxy": "private-two"},
])
def test_invalid_settings_fail_without_exposing_contents(tmp_path, data):
    save(tmp_path, data)
    with pytest.raises(NetworkConfigError) as raised:
        network_environment(tmp_path, {})
    assert "private" not in str(raised.value) and str(tmp_path) not in str(raised.value)


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "directory", "large", "invalid_json"])
def test_unsafe_or_unreadable_network_file_is_rejected(tmp_path, kind):
    path = save(tmp_path, {})
    if kind in {"symlink", "hardlink"}:
        other = tmp_path / "other.json"
        other.write_text('{"HTTPS_PROXY":"private-secret"}')
        path.unlink()
        path.symlink_to(other) if kind == "symlink" else path.hardlink_to(other)
    elif kind == "directory":
        path.unlink()
        path.mkdir()
    else:
        path.write_text("private-secret" * 2000 if kind == "large" else "{private-secret}")
    with pytest.raises(NetworkConfigError) as raised:
        network_environment(tmp_path, {})
    assert "private-secret" not in str(raised.value)


def test_serve_from_other_directory_uses_resolved_workspace_network(tmp_path, monkeypatch, no_proxy_env):
    root, other = tmp_path / "checkout", tmp_path / "other"
    other.mkdir()
    proxy = "http://workspace-proxy.example.invalid:8080"
    save(root, {"HTTPS_PROXY": proxy})
    monkeypatch.chdir(other)
    monkeypatch.setattr(startup, "installed_project", lambda: root)
    monkeypatch.setattr(startup, "detect_access", lambda *args: LocalAccess())
    monkeypatch.setattr(startup, "windows_excluded_ports", lambda: ())
    monkeypatch.setattr(startup, "is_wsl", lambda: False)
    calls = []

    def start(resolved, *args, **kwargs):
        calls.append((resolved, os.environ.get("HTTPS_PROXY")))
        return None, 9876

    monkeypatch.setattr(startup, "start_server", start)
    result = CliRunner().invoke(app, ["serve"])
    assert result.exit_code == 0, result.output
    assert calls == [(root, proxy)]
    assert proxy not in result.output
    assert not (other / ".mathlottery").exists()
