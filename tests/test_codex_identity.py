"""Credential isolation checks use only synthetic temporary Codex profiles."""

import os
import stat
import tomllib

import pytest

from mathlottery.providers.identity import CodexIdentity


@pytest.fixture
def personal_profile(tmp_path, monkeypatch):
    user_home = tmp_path / "user"
    personal = user_home / ".codex"
    personal.mkdir(parents=True)
    (personal / "auth.json").write_text('{"tokens":"synthetic-personal-credentials"}\n')
    (personal / "config.toml").write_text('cli_auth_credentials_store = "keyring"\n')
    monkeypatch.setenv("HOME", str(user_home))
    monkeypatch.setenv("CODEX_HOME", str(personal))
    yield personal
    assert (personal / "auth.json").read_text() == '{"tokens":"synthetic-personal-credentials"}\n'
    assert (personal / "config.toml").read_text() == 'cli_auth_credentials_store = "keyring"\n'


def test_new_profile_neither_imports_nor_mutates_personal_state(tmp_path, personal_profile):
    identity = CodexIdentity(tmp_path / "workspace")
    profile = identity.prepare()
    assert profile == tmp_path / "workspace" / ".mathlottery" / "codex-home"
    assert profile.is_dir() and not list(profile.iterdir())
    assert stat.S_IMODE(profile.stat().st_mode) == 0o700
    profile.chmod(0o755)
    assert identity.prepare() == profile
    assert stat.S_IMODE(profile.stat().st_mode) == 0o700


def test_child_environment_is_private_without_mutating_parent(tmp_path, personal_profile, monkeypatch):
    excluded = (
        "OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_AUTH_TOKEN", "CODEX_ACCESS_TOKEN",
        "OPENAI_BASE_URL", "OPENAI_IDENTITY_TOKEN_FILE", "OPENAI_WORKLOAD_IDENTITY_PROVIDER",
    )
    for key in excluded:
        monkeypatch.setenv(key, "synthetic-inherited-value")
    monkeypatch.setenv("CODEX_SQLITE_HOME", str(personal_profile / "sqlite"))
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.invalid:8080")
    parent_environment = dict(os.environ)

    identity = CodexIdentity(tmp_path / "workspace")
    child = identity.environment()
    assert child["CODEX_HOME"] == str(identity.home)
    assert child["CODEX_SQLITE_HOME"] == str(identity.home)
    assert not set(excluded) & child.keys()
    assert child["HTTPS_PROXY"] == parent_environment["HTTPS_PROXY"]
    assert dict(os.environ) == parent_environment
    child["CODEX_HOME"] = "changed-child-value"
    assert os.environ["CODEX_HOME"] == str(personal_profile)


def test_overrides_force_file_credentials_and_workspace_state(tmp_path, personal_profile):
    identity = CodexIdentity(tmp_path / "workspace with spaces")
    arguments = identity.overrides()
    assert arguments[::2] == ["-c"] * (len(arguments) // 2)
    settings = tomllib.loads("\n".join(arguments[1::2]))
    assert settings["cli_auth_credentials_store"] == "file"
    assert settings["sqlite_home"] == str(identity.home)
    assert settings["log_dir"] == str(identity.home / "log")
    assert not (identity.home / "config.toml").exists()


@pytest.mark.parametrize("shared_position", ["same", "ancestor", "descendant"])
def test_rejects_overlap_with_inherited_codex_home(tmp_path, personal_profile, monkeypatch, shared_position):
    identity = CodexIdentity(tmp_path / "workspace")
    shared = {
        "same": identity.home,
        "ancestor": identity.home.parent,
        "descendant": identity.home / "nested-codex",
    }[shared_position]
    monkeypatch.setenv("CODEX_HOME", str(shared))
    with pytest.raises(ValueError, match="overlaps"):
        identity.prepare()
    assert not identity.home.exists()


def test_rejects_workspace_inside_default_codex_home_even_with_override(personal_profile, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(personal_profile.parent / "other-personal-profile"))
    identity = CodexIdentity(personal_profile / "research")
    with pytest.raises(ValueError, match="overlaps"):
        identity.prepare()
    assert not identity.home.exists()


@pytest.mark.parametrize("component", [".mathlottery", ".mathlottery/codex-home"])
def test_rejects_symlinked_state_directories(tmp_path, personal_profile, component):
    workspace = tmp_path / "workspace"
    linked = workspace / component
    linked.parent.mkdir(parents=True, exist_ok=True)
    linked.symlink_to(personal_profile, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic links"):
        CodexIdentity(workspace).prepare()
    assert linked.is_symlink()


@pytest.mark.parametrize("name", ["auth.json", "config.toml", "sessions", "log"])
def test_rejects_linked_private_profile_entries(tmp_path, personal_profile, name):
    identity = CodexIdentity(tmp_path / "workspace")
    identity.prepare()
    linked = identity.home / name
    target = personal_profile / name
    linked.symlink_to(target, target_is_directory=name in {"sessions", "log"})
    with pytest.raises(ValueError, match="cannot be linked"):
        identity.environment()
    assert linked.is_symlink()


@pytest.mark.parametrize("name", ["auth.json", "config.toml"])
def test_rejects_hardlinked_credentials_and_configuration(tmp_path, personal_profile, name):
    identity = CodexIdentity(tmp_path / "workspace")
    identity.prepare()
    (identity.home / name).hardlink_to(personal_profile / name)
    with pytest.raises(ValueError, match="cannot be linked"):
        identity.overrides()


def test_each_workspace_has_its_own_empty_profile(tmp_path, personal_profile):
    first, second = (CodexIdentity(tmp_path / name) for name in ("one", "two"))
    first.prepare()
    (first.home / "auth.json").write_text('{"tokens":"synthetic-workspace-login"}\n')
    second.prepare()
    assert second.home != first.home
    assert not (second.home / "auth.json").exists()
    assert first.environment()["CODEX_HOME"] != second.environment()["CODEX_HOME"]
