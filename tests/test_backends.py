import json
import os
import sys
import threading
import time

import pytest

from mathlottery.backends import BackendStatus, CodexCLIError, WorkBackend, resolve_codex
from mathlottery.config import BackendConfig
from mathlottery.demo import demo_problem
from mathlottery.models import State
from mathlottery.orchestrator import Orchestrator

FAKE = r"""
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
if os.environ.get('MATHLOTTERY_FAKE_ENV_LOG'):
    with Path(os.environ['MATHLOTTERY_FAKE_ENV_LOG']).open('a') as stream:
        stream.write(json.dumps({'args':args, 'home':os.environ.get('CODEX_HOME'),
            'sqlite':os.environ.get('CODEX_SQLITE_HOME'),
            'api_key_present':'OPENAI_API_KEY' in os.environ}) + '\n')
behavior = os.environ.get('MATHLOTTERY_FAKE_BEHAVIOR', 'ok')
if args == ['--version']:
    if behavior == 'slow_version':
        time.sleep(20)
    print('codex-cli fake-for-tests')
elif args[-2:] == ['login', 'status']:
    if behavior == 'slow_login':
        time.sleep(20)
    print('Logged in using API key' if behavior == 'api_auth' else 'Logged in using ChatGPT')
    sys.exit(1 if behavior == 'no_login' else 0)
elif '--help' in args:
    print('--output-schema --json --ignore-user-config --ephemeral')
else:
    if behavior == 'slow':
        time.sleep(20)
    if behavior == 'rate':
        print(json.dumps({'type':'turn.failed','error':{'message':'429 usage limit exceeded'}}))
        sys.exit(1)
    if behavior == 'error':
        print(json.dumps({'type':'turn.failed','error':{'message':'connection failed'}}))
        sys.exit(1)
    prompt = sys.stdin.read()
    fields = dict(line.split(': ', 1) for line in prompt.splitlines()
                  if line.startswith(('run_id: ', 'task_id: ', 'phase: ')))
    response = dict(fields, action='REASON', summary='A visible mathematical observation.')
    output = Path(args[args.index('--output-last-message') + 1])
    output.write_text(json.dumps(response))
    if behavior != 'no_usage':
        print(json.dumps({'type':'turn.completed','usage':{'input_tokens':17,'output_tokens':5,'cached_input_tokens':3}}))
    else:
        print(json.dumps({'type':'turn.completed'}))
"""


@pytest.fixture
def fake_codex(tmp_path):
    path = tmp_path / "codex"
    path.write_text(f"#!{sys.executable}\n" + FAKE)
    path.chmod(0o755)
    return str(path)


def test_work_invokes_real_process_and_accounts_reported_usage(store, config, fake_codex):
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    config.budget.max_iterations = 2
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.PAUSED
    assert run.iteration == 2
    assert run.usage.input_tokens == 34
    assert run.usage.cached_input_tokens == 6
    assert run.usage.output_tokens == 10
    assert run.usage.unknown_calls == 0
    commands = list(store.run_dir(run.id).glob("tasks/*/attempt-*/command.json"))
    assert len(commands) == 2
    command = json.loads(commands[0].read_text())
    assert "--ignore-user-config" in command
    assert 'forced_login_method="chatgpt"' in command
    assert "features.shell_tool=false" in command
    assert "features.multi_agent=false" in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command


@pytest.mark.parametrize("behavior", ["api_auth", "no_login"])
def test_work_requires_chatgpt_login(fake_codex, tmp_path, monkeypatch, behavior):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", behavior)
    backend = WorkBackend(BackendConfig(codex_command=fake_codex), root=tmp_path)
    with pytest.raises(ValueError, match="requires ChatGPT authentication"):
        backend.check()


def test_work_missing_installation_has_clear_error(tmp_path):
    backend = WorkBackend(BackendConfig(codex_command="/missing/codex"), root=tmp_path)
    result = backend.invoke("prompt", {}, tmp_path, 2)
    assert result.status == BackendStatus.UNSUPPORTED
    assert not result.invoked


def test_codex_lookup_uses_child_path(fake_codex, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "unrelated"))
    env = {**os.environ, "PATH": str(tmp_path)}
    assert resolve_codex("codex", env=env) == fake_codex


def test_codex_lookup_skips_broken_platform_launcher(fake_codex, tmp_path):
    shim_dir = tmp_path / "windows-npm"
    shim_dir.mkdir()
    shim = shim_dir / "codex"
    shim.write_text(f"#!{sys.executable}\nimport sys\n"
                    "sys.stderr.write('Missing optional dependency @openai/codex-linux-x64')\n"
                    "sys.exit(1)\n")
    shim.chmod(0o755)
    env = {**os.environ, "PATH": os.pathsep.join([str(shim_dir), str(tmp_path)])}
    assert resolve_codex("codex", env=env) == fake_codex
    # An explicit executable remains authoritative, even when PATH has a working alternative.
    with pytest.raises(CodexCLIError) as caught:
        resolve_codex(str(shim), env=env)
    assert caught.value.code == "CLI_PLATFORM_DEPENDENCY_MISSING"
    assert str(shim) not in str(caught.value)


def test_rate_limit_preserves_run_without_backend_switch(store, config, fake_codex, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "rate")
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.RATE_LIMITED
    assert run.mode == "work"
    assert "429" in run.last_error
    assert run.usage.unknown_calls == 1
    assert (store.run_dir(run.id) / "report.md").exists()


def test_failure_retries_are_bounded_and_charged(store, config, fake_codex, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "error")
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    config.backend.max_retries = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.FAILED
    assert run.iteration == 2
    assert run.usage.unknown_calls == 2


def test_missing_usage_stops_requested_token_budget(store, config, fake_codex, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "no_usage")
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    config.budget.max_input_tokens = 100
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.PAUSED
    assert run.usage.input_tokens is None
    assert run.iteration == 1
    assert "unknown" in run.stop_reason


def test_token_threshold_is_checked_between_calls(store, config, fake_codex):
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    config.budget.max_input_tokens = 20
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.PAUSED
    assert run.usage.input_tokens == 34  # Per-call output is not known before the call.
    assert run.iteration == 2
    assert "between calls" in run.stop_reason


def test_stop_active_work_kills_child_and_checkpoints(store, config, fake_codex, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "slow")
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    engine = Orchestrator(store)
    run = engine.create(config, demo_problem())
    thread = threading.Thread(target=engine.drive, args=(run.id,))
    thread.start()
    deadline = time.monotonic() + 3
    while not list(store.run_dir(run.id).glob("tasks/*/attempt-*/command.json")):
        assert time.monotonic() < deadline
        time.sleep(0.02)
    engine.stop(run.id)
    thread.join(timeout=4)
    assert not thread.is_alive()
    assert store.load(run.id).state == State.CANCELLED


def test_work_timeout_is_bounded(fake_codex, tmp_path, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "slow")
    backend = WorkBackend(BackendConfig(codex_command=fake_codex), root=tmp_path)
    started = time.monotonic()
    result = backend.invoke("prompt", {}, tmp_path / "attempt", 0.5)
    assert result.status == BackendStatus.INTERRUPTED
    assert time.monotonic() - started < 3


def test_api_credentials_are_not_forwarded(tmp_path, monkeypatch):
    for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_ACCESS_TOKEN"):
        monkeypatch.setenv(key, "should-not-forward")
    env = WorkBackend(BackendConfig(), root=tmp_path).environment()
    assert not any(
        key in env
        for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_ACCESS_TOKEN")
    )
    assert env.get("PATH") == os.environ.get("PATH")


@pytest.mark.parametrize("behavior", ["slow_version", "slow_login"])
def test_setup_obeys_the_same_wall_time_budget(fake_codex, tmp_path, monkeypatch, behavior):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", behavior)
    backend = WorkBackend(BackendConfig(codex_command=fake_codex), root=tmp_path)
    started = time.monotonic()
    result = backend.invoke("prompt", {}, tmp_path / "attempt", 0.3)
    assert result.status == BackendStatus.INTERRUPTED
    assert not result.invoked
    assert time.monotonic() - started < 2


def test_failed_auth_is_not_cached_as_ready(fake_codex, tmp_path, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "api_auth")
    backend = WorkBackend(BackendConfig(codex_command=fake_codex), root=tmp_path)
    for _ in range(2):
        result = backend.invoke("prompt", {}, tmp_path / "attempt", 2)
        assert result.status == BackendStatus.UNSUPPORTED
        assert not result.invoked
        assert backend.executable is None


def test_resume_keeps_previous_attempt_logs(store, config, fake_codex, monkeypatch):
    config.backend.mode = "work"
    config.backend.codex_command = fake_codex
    config.budget.max_iterations = 2
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "error")
    engine = Orchestrator(store)
    failed = engine.drive(engine.create(config, demo_problem()).id)
    first = next(store.run_dir(failed.id).glob("tasks/*/attempt-*/codex.events.jsonl"))
    contents = first.read_text()
    monkeypatch.setenv("MATHLOTTERY_FAKE_BEHAVIOR", "ok")
    resumed = engine.resume(failed.id)
    assert resumed.iteration == 2
    assert resumed.state == State.PAUSED
    assert first.read_text() == contents
    assert len(list(store.run_dir(failed.id).glob("tasks/*/attempt-*/codex.events.jsonl"))) == 2


def test_backend_cannot_reuse_stale_answer(fake_codex, tmp_path):
    directory = tmp_path / "attempt"
    directory.mkdir()
    (directory / "answer.json").write_text('{"stale":true}')
    backend = WorkBackend(BackendConfig(codex_command=fake_codex), root=tmp_path)
    result = backend.invoke("prompt", {}, directory, 2)
    assert result.status == BackendStatus.FAILED
    assert not result.invoked
    assert (directory / "answer.json").read_text() == '{"stale":true}'


def test_structured_checks_and_execution_use_workspace_account(
    store, config, fake_codex, monkeypatch,
):
    local_home = store.root / "local-codex"
    local_home.mkdir()
    sentinel = local_home / "auth.json"
    sentinel.write_text('{"fixture":"local credential must remain untouched"}')
    before = sentinel.read_bytes()
    log = store.root / "child-environments.jsonl"
    monkeypatch.setenv("CODEX_HOME", str(local_home))
    monkeypatch.setenv("CODEX_SQLITE_HOME", str(local_home / "db"))
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-forward")
    monkeypatch.setenv("MATHLOTTERY_FAKE_ENV_LOG", str(log))
    config.backend.mode = "codex"
    config.backend.codex_command = fake_codex
    config.budget.max_iterations = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.iteration == 1
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    isolated_home = store.root / ".mathlottery" / "codex-home"
    assert len(entries) == 4  # version, login status, help, research
    assert all(entry["home"] == str(isolated_home) for entry in entries)
    assert all(not entry["api_key_present"] for entry in entries)
    assert all(entry["sqlite"] != str(local_home / "db") for entry in entries)
    for entry in entries:
        if "login" in entry["args"] or "--output-schema" in entry["args"]:
            assert 'cli_auth_credentials_store="file"' in entry["args"]
    assert os.environ["CODEX_HOME"] == str(local_home)
    assert sentinel.read_bytes() == before
