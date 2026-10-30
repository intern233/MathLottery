"""Inactive connections must not donate credentials to any Codex child process."""

import json
import os
import sys
import tomllib

import pytest
import yaml

from mathlottery.config import AgentSlot, BackendConfig, ChatConfig, Config, load_config
from mathlottery.models import State, Workflow
from mathlottery.providers.agent_roster import AgentRoster, AgentRosterStore
from mathlottery.providers.base import BackendResult, BackendStatus, WorkBackend
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.credentials import known_credential_env_names
from mathlottery.providers.demo import demo_problem
from mathlottery.providers.registry import research_backend
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.attempts import bounded_backend
from mathlottery.web.agent_roster import AgentConnections
from mathlottery.web.service import WebService


@pytest.fixture
def saved_connections(tmp_path, monkeypatch):
    roster = AgentRoster(slots=[
        AgentSlot(id="inactive-codex", backend=BackendConfig(
            codex_auth="api_key", codex_api_key_env="SAVED_CODEX_CREDENTIAL")),
        AgentSlot(id="inactive-responses", backend=BackendConfig(
            mode="chat", chat=ChatConfig(api_key_env="SAVED_RESPONSES_CREDENTIAL"))),
    ])
    AgentRosterStore(tmp_path).save(roster)
    (tmp_path / "config.yaml").write_text(yaml.safe_dump({
        "backend": {"chat": {"api_key_env": "MAIN_RESPONSES_CREDENTIAL"}},
        "model_providers": {"other": {"label": "Other", "chat": {
            "api_key_env": "PROVIDER_CREDENTIAL", "base_url": "https://example.invalid/v1",
            "tools": [],
        }}},
        "solve": {"parallel_agents": 1, "agent_slots": [{"id": "unused", "backend": {
            "codex_auth": "api_key", "codex_api_key_env": "CONFIG_SLOT_CREDENTIAL",
        }}]},
    }))
    names = {
        "SAVED_CODEX_CREDENTIAL", "SAVED_RESPONSES_CREDENTIAL", "MAIN_RESPONSES_CREDENTIAL",
        "PROVIDER_CREDENTIAL", "CONFIG_SLOT_CREDENTIAL", "OWN_CREDENTIAL",
    }
    for name in names:
        monkeypatch.setenv(name, "synthetic-secret-for-" + name)
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.invalid:8080")
    return names


def assert_isolated(backend, names, auth):
    child = backend.environment()
    assert not names.intersection(child)
    assert child["HTTPS_PROXY"] == "http://proxy.example.invalid:8080"
    if auth == "api_key":
        assert child["CODEX_API_KEY"] == os.environ["OWN_CREDENTIAL"]
    else:
        assert "CODEX_API_KEY" not in child
    args = backend.authentication_overrides()
    settings = tomllib.loads("\n".join(args[1::2]))
    policy = settings["shell_environment_policy"]
    # Codex applies `set` after exclusion; stored settings cannot restore keys.
    assert all(policy["set"][name] == "" for name in names | {"CODEX_API_KEY"})
    effective_shell = {**child, **policy["set"]}
    assert not any(effective_shell.get(name) for name in names | {"CODEX_API_KEY"})
    return child


@pytest.mark.parametrize("auth", ["chatgpt", "api_key"])
def test_non_pool_process_excludes_saved_and_configured_connections(
    tmp_path, saved_connections, auth,
):
    previous = dict(os.environ)
    path = tmp_path / ".mathlottery/agents.json"
    roster_before = path.read_bytes()
    config = Config(backend=BackendConfig(codex_auth=auth, codex_api_key_env="OWN_CREDENTIAL"))
    assert not config.solve.agent_slots
    backend = NativeWorkBackend(config.backend, tmp_path)
    assert_isolated(backend, saved_connections, auth)
    assert dict(os.environ) == previous
    assert path.read_bytes() == roster_before
    assert not config.solve.agent_slots  # Reading exclusions must not select saved routes.


@pytest.mark.parametrize("auth", ["chatgpt", "api_key"])
def test_actual_cli_preflight_children_have_no_saved_credentials(
    tmp_path, saved_connections, auth, monkeypatch,
):
    cli = tmp_path / "synthetic-codex"
    cli.write_text(f"#!{sys.executable}\n" + r'''
import json, os, sys
from pathlib import Path
names = json.loads(os.environ['CHECK_ENV_NAMES'])
with Path(os.environ['CHECK_LOG']).open('a') as file:
    file.write(json.dumps({'args': sys.argv[1:], 'has_secret': any(
        name in os.environ for name in names + ['CODEX_API_KEY'])}) + '\n')
if '--version' in sys.argv:
    print('codex-test-local')
elif '--help' in sys.argv:
    print('--json --output-last-message --sandbox resume')
else:
    print('Logged in using ChatGPT')
''')
    cli.chmod(0o700)
    log = tmp_path / "probe.jsonl"
    monkeypatch.setenv("CHECK_LOG", str(log))
    monkeypatch.setenv("CHECK_ENV_NAMES", json.dumps(sorted(saved_connections)))
    backend = NativeWorkBackend(BackendConfig(
        codex_command=str(cli), codex_auth=auth, codex_api_key_env="OWN_CREDENTIAL",
    ), tmp_path)
    assert backend.check()["available"]
    probes = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(probes) >= 2 and not any(probe["has_secret"] for probe in probes)
    assert any("login" in probe["args"] for probe in probes) == (auth == "chatgpt")


def alternate_config(tmp_path, monkeypatch, auth="chatgpt", execution="native"):
    path = tmp_path / "alternate.yaml"
    path.write_text(yaml.safe_dump({
        "backend": {"codex_auth": auth, "codex_api_key_env": "OWN_CREDENTIAL",
                    "execution": execution},
        "model_providers": {"unused": {"label": "Unused", "chat": {
            "base_url": "https://unused.example.invalid/v1", "tools": [],
            "api_key_env": "ALTERNATE_ONLY_CREDENTIAL",
        }}},
        "budget": {"max_iterations": 1, "finalize_minutes": 0},
    }))
    monkeypatch.setenv("ALTERNATE_ONLY_CREDENTIAL", "synthetic-alternate-secret")
    return load_config(tmp_path, path)


def test_full_config_factory_and_solve_receive_explicit_config_keys(
    store, saved_connections, monkeypatch,
):
    config = alternate_config(store.root, monkeypatch)
    assert "ALTERNATE_ONLY_CREDENTIAL" not in known_credential_env_names(store.root)
    names = saved_connections | {"ALTERNATE_ONLY_CREDENTIAL"}
    assert_isolated(research_backend(config.backend, store.root, workspace_config=config), names, "chatgpt")
    assert_isolated(bounded_backend(config, Orchestrator(store)), names, "chatgpt")


@pytest.mark.parametrize("execution,workflow", [
    ("native", Workflow.FIND), ("native", Workflow.SOLVE), ("structured", Workflow.PIPELINE),
])
@pytest.mark.parametrize("auth", ["chatgpt", "api_key"])
def test_runtime_carries_explicit_configuration_into_actual_backend(
    store, saved_connections, monkeypatch, execution, workflow, auth,
):
    config = alternate_config(store.root, monkeypatch, auth, execution)
    observed = []

    def inspect(backend, *args, **kwargs):
        observed.append(assert_isolated(
            backend, saved_connections | {"ALTERNATE_ONLY_CREDENTIAL"}, auth,
        ))
        return BackendResult(BackendStatus.INTERRUPTED, error="Scripted interruption")

    if execution == "native":
        monkeypatch.setattr(NativeWorkBackend, "invoke_native", inspect)
    else:
        monkeypatch.setattr(WorkBackend, "invoke", inspect)
    engine = Orchestrator(store)
    run = engine.create(config, None if workflow == Workflow.FIND else demo_problem(), workflow=workflow)
    result = engine.drive(run.id)
    assert result.state == State.PAUSED
    assert len(observed) == 1
    assert not result.config["solve"]["agent_slots"]


def test_web_explicit_config_account_and_api_preflight_share_exclusions(
    tmp_path, saved_connections, monkeypatch,
):
    config = alternate_config(tmp_path, monkeypatch)
    service = WebService(tmp_path, config_path=tmp_path / "alternate.yaml")
    connections = AgentConnections(service)
    assert saved_connections | {"ALTERNATE_ONLY_CREDENTIAL"} <= set(connections.excluded_env())
    observed = []
    monkeypatch.setattr(NativeWorkBackend, "check", lambda backend: observed.append(
        assert_isolated(backend, saved_connections | {"ALTERNATE_ONLY_CREDENTIAL"}, "api_key"),
    ))
    settings = config.backend.model_copy(update={"codex_auth": "api_key"})
    connections.ensure_codex_api(settings, config)
    assert len(observed) == 1


@pytest.mark.parametrize("bad", ["api_key_env: [private-sensitive-text", "codex_api_key_env: secret-value-not-name"])
def test_malformed_settings_do_not_echo_private_input(tmp_path, bad):
    (tmp_path / "config.yaml").write_text("backend:\n  " + bad)
    with pytest.raises(ValueError) as error:
        known_credential_env_names(tmp_path)
    assert "private-sensitive-text" not in str(error.value)
    assert "secret-value-not-name" not in str(error.value)


@pytest.mark.parametrize("link", ["symlink", "hardlink"])
def test_connection_name_reader_rejects_linked_settings(tmp_path, link):
    target = tmp_path / "private.yaml"
    target.write_text("backend: {}")
    destination = tmp_path / "config.yaml"
    if link == "symlink":
        destination.symlink_to(target)
    else:
        destination.hardlink_to(target)
    with pytest.raises(ValueError, match="credential isolation"):
        known_credential_env_names(tmp_path)
