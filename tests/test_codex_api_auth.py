"""Official Codex API-auth wiring, tested with synthetic keys and a scripted CLI."""

import json
import os
import select
import shutil
import subprocess
import sys
import time
import tomllib

import pytest
from test_native import FAKE_NATIVE
from test_solve_team import problem

from mathlottery.config import AgentSlot, BackendConfig, Config, SolveConfig
from mathlottery.models import State, Workflow, digest
from mathlottery.providers.base import BackendStatus
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.identity import CodexIdentity
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.solve.attempts import bounded_backend
from mathlottery.solve.routes import attempt_config, route_fingerprint, route_metadata
from mathlottery.storage.core import atomic_write, json_text

SYNTHETIC_KEY = "synthetic-api-credential-never-send-to-a-service"

API_PROBE = r'''
api_probe = {'args': args, 'home': os.environ.get('CODEX_HOME'),
             'selected_key': bool(os.environ.get('CODEX_API_KEY')),
             'original_key': 'OWN_API_KEY' in os.environ,
             'peer_key': 'PEER_KEY' in os.environ}
if 'login' in args:
    raise AssertionError('API mode must not read or mutate subscription login')
if args != ['--version'] and '--help' not in args:
    import fnmatch, tomllib
    settings = tomllib.loads('\n'.join(args[i+1] for i, value in enumerate(args) if value == '-c'))
    assert settings['forced_login_method'] == 'api'
    assert settings['model_provider'] == 'openai'
    assert settings['openai_base_url'] == 'https://api.openai.com/v1'
    assert 'openai' not in settings.get('model_providers', {})
    exclusions = settings['shell_environment_policy'].get('exclude', [])
    shell_environment = {key: value for key, value in os.environ.items()
                         if not any(fnmatch.fnmatchcase(key, pattern) for pattern in exclusions)}
    shell_environment.update(settings['shell_environment_policy']['set'])
    api_probe['shell_key'] = bool(shell_environment.get('CODEX_API_KEY'))
    assert api_probe['selected_key'] and not api_probe['original_key'] and not api_probe['peer_key']
with Path(os.environ['MATHLOTTERY_API_AUTH_PROBE']).open('a') as output:
    output.write(json.dumps(api_probe) + '\n')
'''


@pytest.fixture
def api_codex(tmp_path, monkeypatch):
    path = tmp_path / "codex-api-fixture"
    # Keep native scripted session/milestone behavior, but assert all auth boundaries.
    source = FAKE_NATIVE.replace("args = sys.argv[1:]", "args = sys.argv[1:]\n" + API_PROBE)
    path.write_text(f"#!{sys.executable}\n" + source)
    path.chmod(0o755)
    monkeypatch.setenv("OWN_API_KEY", SYNTHETIC_KEY)
    monkeypatch.setenv("PEER_KEY", "synthetic-peer-key")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-wrong-default")
    monkeypatch.setenv("CODEX_ACCESS_TOKEN", "synthetic-wrong-subscription")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://redirect.example.invalid/v1")
    monkeypatch.setenv("MATHLOTTERY_API_AUTH_PROBE", str(tmp_path / "api-probe.jsonl"))
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "progress")
    return BackendConfig(codex_command=str(path), codex_auth="api_key", codex_api_key_env="OWN_API_KEY")


def settings(arguments):
    return tomllib.loads("\n".join(arguments[i + 1] for i, value in enumerate(arguments) if value == "-c"))


def test_legacy_config_defaults_and_shared_billing_properties():
    legacy = BackendConfig.model_validate({"mode": "codex"})
    assert legacy.codex_auth == "chatgpt" and not legacy.uses_api_key
    assert legacy.api_key_env_name is None
    api = BackendConfig(codex_auth="api_key", codex_api_key_env="RESEARCH_KEY")
    assert api.uses_api_key and api.api_key_env_name == "RESEARCH_KEY"
    assert BackendConfig(mode="chat").uses_api_key
    assert BackendConfig(mode="chat").api_key_env_name == "OPENAI_API_KEY"
    assert not BackendConfig(mode="manual", codex_auth="api_key").uses_api_key


@pytest.mark.parametrize("value", ["sk-not-a-variable", "KEY WITH SPACE", "", "../secret", "A" * 129])
def test_codex_api_key_selector_rejects_values_or_paths(value):
    with pytest.raises(ValueError):
        BackendConfig(codex_api_key_env=value)


@pytest.mark.parametrize("profile", [None, "agent-a"])
def test_api_auth_uses_separate_private_homes_and_cannot_mutate_subscription(tmp_path, profile):
    account = CodexIdentity(tmp_path, profile)
    account.prepare()
    sentinel = account.home / "auth.json"
    sentinel.write_text('{"synthetic": "subscription"}')
    api = CodexIdentity(tmp_path, profile, auth="api_key")
    api.prepare()
    assert api.home != account.home
    assert api.home == tmp_path / ".mathlottery" / (
        "codex-api-accounts/agent-a" if profile else "codex-api-home"
    )
    assert not (api.home / "auth.json").exists()
    assert sentinel.read_text() == '{"synthetic": "subscription"}'


def test_api_home_symlinks_cannot_alias_subscription_credentials(tmp_path):
    source = CodexIdentity(tmp_path, "agent-a")
    source.prepare()
    api = CodexIdentity(tmp_path, "agent-a", auth="api_key")
    api.home.parent.mkdir()
    api.home.symlink_to(source.home, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic links"):
        api.prepare()


def test_api_key_only_enters_exec_environment_and_shell_policy_excludes_credentials(tmp_path, api_codex):
    backend = NativeWorkBackend(api_codex, root=tmp_path)
    backend.identity.excluded_env.add("PEER_KEY")
    before = dict(os.environ)
    child = backend.environment()
    assert child["CODEX_API_KEY"] == SYNTHETIC_KEY
    assert "OWN_API_KEY" not in child and "OPENAI_API_KEY" not in child and "PEER_KEY" not in child
    assert "OPENAI_BASE_URL" not in child and "CODEX_ACCESS_TOKEN" not in child
    assert dict(os.environ) == before
    command = backend.native_command(tmp_path / "attempt", tmp_path / "workspace", None)
    options = settings(command)
    assert options["forced_login_method"] == "api"
    assert options["openai_base_url"] == "https://api.openai.com/v1"
    assert "openai" not in options.get("model_providers", {})
    assert "exclude" not in options["shell_environment_policy"]
    assert {"CODEX_API_KEY", "OWN_API_KEY", "PEER_KEY"} <= set(options["shell_environment_policy"]["set"])
    assert all(value == "" for value in options["shell_environment_policy"]["set"].values())
    assert options["features"]["shell_tool"] is True and options["web_search"] == "live"
    assert options["sandbox_mode"] == "workspace-write"
    assert SYNTHETIC_KEY not in json.dumps(command)


def test_api_preflight_uses_no_login_and_never_exposes_key_to_probes(tmp_path, api_codex):
    backend = NativeWorkBackend(api_codex, root=tmp_path)
    backend.identity.excluded_env.add("PEER_KEY")
    ready = backend.check()
    assert ready["authentication"] == "API key"
    records = [json.loads(line) for line in (tmp_path / "api-probe.jsonl").read_text().splitlines()]
    assert [item["args"] for item in records] == [["--version"], ["exec", "--help"]]
    assert all(not item["selected_key"] and not item["original_key"] and not item["peer_key"] for item in records)
    assert not list((tmp_path / ".mathlottery").rglob("auth.json"))


def test_installed_codex_loads_official_endpoint_and_blanks_profile_secrets_offline(tmp_path):
    executable = shutil.which("codex")
    if executable is None:
        pytest.skip("Optional offline config check requires an installed official Codex CLI")
    backend = NativeWorkBackend(BackendConfig(codex_auth="api_key", codex_api_key_env="OWN_API_KEY"), tmp_path)
    backend.identity.excluded_env.add("PEER_KEY")
    home = backend.identity.prepare()
    (home / "config.toml").write_text(
        'openai_base_url="https://redirect.example.invalid/v1"\n'
        '[shell_environment_policy]\nexclude=["CUSTOM_SECRET", "PRIVATE_*"]\n'
        'ignore_default_excludes=true\n'
        '[shell_environment_policy.set]\nCODEX_API_KEY="synthetic-restored"\n'
        'OWN_API_KEY="synthetic-original"\nPEER_KEY="synthetic-peer"\nKEEP_ME="retained"\n'
    )
    # No credentials or parent configs enter this process. These RPCs read local
    # configuration only; closed loopback proxies also prevent remote requests.
    environment = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL", "LD_LIBRARY_PATH"}}
    environment.update(CODEX_HOME=str(home), CODEX_SQLITE_HOME=str(home),
                       HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9",
                       ALL_PROXY="http://127.0.0.1:9", NO_PROXY="")
    process = subprocess.Popen(
        [executable, *backend.authentication_overrides(), "app-server"], cwd=tmp_path, env=environment,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, start_new_session=True,
    )

    def rpc(identifier, method, params):
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params}) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not select.select([process.stdout], [], [], max(0, deadline - time.monotonic()))[0]:
                break
            line = process.stdout.readline()
            if not line:
                break
            response = json.loads(line)
            if response.get("id") == identifier:
                assert "error" not in response, response
                return response["result"]
        pytest.fail("Installed Codex did not answer the offline configuration RPC")

    try:
        rpc(1, "initialize", {"clientInfo": {"name": "mathlottery-offline-config-check", "version": "0"}})
        configuration = rpc(2, "config/read", {"includeLayers": False})["config"]
        assert configuration["openai_base_url"] == "https://api.openai.com/v1"
        assert configuration["model_provider"] == "openai"
        assert configuration["forced_login_method"] == "api"
        injected = configuration["shell_environment_policy"]["set"]
        assert configuration["shell_environment_policy"]["exclude"] == ["CUSTOM_SECRET", "PRIVATE_*"]
        assert configuration["shell_environment_policy"]["ignore_default_excludes"] is True
        assert all(injected[name] == "" for name in ("CODEX_API_KEY", "OWN_API_KEY", "PEER_KEY"))
        assert injected["KEEP_ME"] == "retained"
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)
    assert not (home / "auth.json").exists()


def test_missing_api_key_never_uses_present_subscription_login(tmp_path, api_codex, monkeypatch):
    identity = CodexIdentity(tmp_path)
    identity.prepare()
    atomic_write(identity.home / "auth.json", '{"synthetic": "signed-in"}')
    monkeypatch.delenv("OWN_API_KEY")
    backend = NativeWorkBackend(api_codex, root=tmp_path)
    result = backend.invoke_native("prompt", tmp_path / "attempt", tmp_path / "workspace", 2)
    assert result.status == BackendStatus.UNSUPPORTED and not result.invoked
    assert "OWN_API_KEY" in result.error and "fallback" in result.error
    assert not (tmp_path / "api-probe.jsonl").exists()
    assert (identity.home / "auth.json").read_text() == '{"synthetic": "signed-in"}'


def test_api_exec_continues_native_session_and_never_saves_key(store, api_codex):
    slots = [AgentSlot(id="api-research", backend=api_codex)]
    config = Config(solve=SolveConfig(coordination="allocation", parallel_agents=1, agent_slots=slots))
    config.budget.max_iterations = 2
    config.budget.finalize_minutes = 0
    # A declared but inactive Responses peer makes its key an explicit exclusion.
    config.solve.agent_slots[0].backend.chat.api_key_env = "PEER_KEY"
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.PAUSED and run.iteration == 2, run.last_error
    first_session = run.native.solver_session_id
    assert first_session
    config = Config.model_validate(run.config)
    config.budget.max_iterations = 3
    resumed = engine.resume(run.id, config=config)
    assert resumed.iteration == 3 and resumed.native.solver_session_id == first_session
    records = [json.loads(line) for line in (store.root / "api-probe.jsonl").read_text().splitlines()]
    invocations = [item for item in records if "--output-last-message" in item["args"]]
    assert len(invocations) == 3
    assert all(item["selected_key"] and not item["shell_key"] for item in invocations)
    assert "resume" not in invocations[0]["args"] and all("resume" in item["args"] for item in invocations[1:])
    for path in store.root.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".jsonl", ".yaml", ".md", ".txt"}:
            assert SYNTHETIC_KEY not in path.read_text(errors="replace"), path
    assert not list((store.root / ".mathlottery").rglob("auth.json"))


def test_removed_key_is_not_cached_after_successful_preflight(tmp_path, api_codex, monkeypatch):
    backend = NativeWorkBackend(api_codex, root=tmp_path)
    backend.identity.excluded_env.add("PEER_KEY")
    backend.check()
    monkeypatch.delenv("OWN_API_KEY")
    result = backend.invoke_native("prompt", tmp_path / "attempt", tmp_path / "workspace", 2)
    assert result.status == BackendStatus.UNSUPPORTED and not result.invoked
    assert not (tmp_path / "attempt/command.json").exists()


def test_bounded_codex_removes_api_key_peers_for_both_transports(store, monkeypatch):
    config = Config(solve=SolveConfig(parallel_agents=3, agent_slots=[
        AgentSlot(id="subscription", backend=BackendConfig()),
        AgentSlot(id="codex-api", backend=BackendConfig(codex_auth="api_key", codex_api_key_env="CODEX_PEER")),
        AgentSlot(id="hosted-api", backend=BackendConfig(mode="chat", chat={"api_key_env": "HOSTED_PEER"})),
    ]))
    monkeypatch.setenv("CODEX_PEER", "synthetic-codex-peer")
    monkeypatch.setenv("HOSTED_PEER", "synthetic-hosted-peer")
    backend = bounded_backend(config, Orchestrator(store))
    assert not {"CODEX_PEER", "HOSTED_PEER"} & backend.environment().keys()
    injected = settings(backend.authentication_overrides())["shell_environment_policy"]["set"]
    assert all(injected[name] == "" for name in ("CODEX_PEER", "HOSTED_PEER"))


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.SOLVE, Workflow.PIPELINE])
def test_zero_cost_restriction_blocks_codex_api_before_creation(store, workflow):
    config = Config(backend=BackendConfig(codex_auth="api_key"))
    config.budget.max_external_cost_usd = 0
    with pytest.raises(ValueError, match="max_external_cost_usd"):
        Orchestrator(store).create(config, None if workflow == Workflow.FIND else problem(), workflow=workflow)
    assert store.list_runs() == []


def test_zero_cost_restriction_blocks_codex_api_peer_of_subscription_primary(store):
    config = Config(solve=SolveConfig(parallel_agents=2, agent_slots=[
        AgentSlot(id="subscription", backend=BackendConfig()),
        AgentSlot(id="paid", backend=BackendConfig(codex_auth="api_key")),
    ]))
    config.budget.max_external_cost_usd = 0
    with pytest.raises(ValueError, match="API-funded agent slots"):
        Orchestrator(store).create(config, problem(), workflow=Workflow.SOLVE)


def test_native_resume_rejects_authentication_change(store):
    engine = Orchestrator(store)
    run = engine.create(Config(), problem(), workflow=Workflow.SOLVE)
    config = Config.model_validate(run.config)
    config.backend.codex_auth = "api_key"
    with pytest.raises(ValueError, match="change Codex authentication"):
        engine.resume(run.id, config=config)
    assert store.load(run.id).config == run.config


def test_route_hash_preserves_old_default_checkpoints_but_pins_api_changes():
    legacy = BackendConfig().model_dump(mode="json")
    del legacy["codex_auth"], legacy["codex_api_key_env"]
    old_hash = digest(json_text(legacy))
    backend = BackendConfig.model_validate(legacy)
    assert route_fingerprint(backend) == old_hash
    config = Config(solve=SolveConfig(parallel_agents=1, agent_slots=[AgentSlot(id="old", backend=backend)]))
    old_route = config.solve.agent_slots[0].backend.model_dump(mode="json")
    del old_route["codex_auth"], old_route["codex_api_key_env"]
    receipt = {"slot_id": "old", "route_sha256": digest(json_text(old_route))}
    assert attempt_config(config, receipt).backend.codex_auth == "chatgpt"
    assert route_metadata(config, "old")["route_sha256"] == receipt["route_sha256"]
    config.solve.agent_slots[0].backend.codex_auth = "api_key"
    with pytest.raises(ValueError, match="route changed"):
        attempt_config(config, receipt)
