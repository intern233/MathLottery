"""Official account protocol exercised with isolated subprocesses, never real logins."""

import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest
from test_web import serving

from mathlottery.config import Config
from mathlottery.models import Workflow
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.account import AccountRPC, AccountTimeoutError, CodexAccount
from mathlottery.web.service import WebService

SCRIPT = r'''
import json, os, sys
if '--version' in sys.argv:
    print('codex test')
    raise SystemExit
state_path = os.path.join(os.environ['CODEX_HOME'], 'auth.json')
with open(os.environ['ACCOUNT_TEST_LOG'] + '.process', 'w') as saved:
    json.dump({'argv': sys.argv, 'environment': {
        key: os.environ.get(key) for key in (
            'CODEX_HOME', 'CODEX_SQLITE_HOME', 'OPENAI_API_KEY', 'CODEX_API_KEY',
            'CODEX_AUTH_TOKEN', 'OPENAI_BASE_URL',
            'HTTPS_PROXY', 'https_proxy', 'NO_PROXY',
        )}}, saved)
if os.path.exists(state_path):
    with open(state_path) as saved:
        authenticated = json.load(saved)
else:
    authenticated = os.environ.get('ACCOUNT_TEST_SIGNED_IN') == '1'
pending = False
def emit(message):
    print(json.dumps(message), flush=True)
def save_account():
    with open(state_path, 'w') as saved:
        json.dump(authenticated, saved)
for line in sys.stdin:
    message = json.loads(line)
    if 'id' not in message:
        continue
    method = message['method']
    result = {}
    with open(os.environ['ACCOUNT_TEST_LOG'], 'a') as log:
        log.write(method + '\n')
    if method == 'account/read':
        if pending and os.environ.get('ACCOUNT_TEST_COMPLETE'):
            success = os.environ['ACCOUNT_TEST_COMPLETE'] == 'success'
            emit({'method': 'account/login/completed', 'params': {
                'loginId': 'sample-login', 'success': success, 'error': 'private-server-error'}})
            authenticated, pending = success, False
            save_account()
        result = {'account': {'type': 'chatgpt', 'email': 'sample@example.com',
                  'planType': 'pro', 'access_token': 'test-secret-token'} if authenticated else None}
    elif method == 'account/login/start':
        if os.environ.get('ACCOUNT_TEST_ERROR'):
            emit({'id': message['id'], 'error': {'message': 'test-secret-token'}})
            continue
        pending = True
        result = {'type': 'chatgptDeviceCode', 'loginId': 'sample-login',
                  'verificationUrl': os.environ.get('ACCOUNT_TEST_URL', 'https://auth.openai.com/codex/device'),
                  'userCode': 'TEST-CODE', 'access_token': 'test-secret-token'}
    elif method == 'account/login/cancel':
        pending = False
    elif method == 'account/logout':
        if os.environ.get('ACCOUNT_TEST_LOGOUT_ERROR'):
            emit({'id': message['id'], 'error': {'message': 'private-logout-token'}})
            continue
        authenticated = False
        save_account()
    emit({'id': message['id'], 'result': result})
'''


@pytest.fixture
def account(tmp_path, monkeypatch):
    executable = tmp_path / "codex-test"
    executable.write_text(f"#!{sys.executable}\n" + SCRIPT)
    executable.chmod(0o755)
    monkeypatch.setenv("ACCOUNT_TEST_LOG", str(tmp_path / "methods.log"))
    manager = CodexAccount(lambda: str(executable), root=tmp_path)
    yield manager
    manager.close()


def calls(tmp_path):
    return (tmp_path / "methods.log").read_text().splitlines()


def test_pending_login_idempotence_and_cancel(account, tmp_path):
    assert not account.status()["authenticated"]
    first = account.start()
    assert first["login"]["user_code"] == "TEST-CODE"
    assert account.start()["login"] == first["login"]
    assert calls(tmp_path).count("account/login/start") == 1
    cancelled = account.cancel()
    assert cancelled["login"] is None and not cancelled["authenticated"]
    assert "account/login/cancel" in calls(tmp_path)
    assert "test-secret-token" not in json.dumps(first)
    assert "sample-login" not in json.dumps(first)


def test_existing_account_not_replaced_and_only_public_fields_returned(account, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    state = account.start()
    assert state["authenticated"] and state["login"] is None
    assert state["account"] == {"type": "chatgpt", "email": "s***@example.com", "plan_type": "pro"}
    assert "account/login/start" not in calls(tmp_path)
    assert "account/logout" not in calls(tmp_path)
    assert "test-secret-token" not in json.dumps(state)


@pytest.mark.parametrize("pending", [False, True])
def test_existing_api_key_account_is_preserved_including_external_sign_in(account, monkeypatch, tmp_path, pending):
    account.start() if pending else account.status()
    rpc_call = account.rpc.call

    def api_key_account(method, params=None, **kwargs):
        if method == "account/read":
            return {"account": {"type": "apiKey", "apiKey": "test-secret-token"}}
        return rpc_call(method, params, **kwargs)

    monkeypatch.setattr(account.rpc, "call", api_key_account)
    state = account.start()
    assert state["available"] and not state["authenticated"]
    assert state["account"]["type"] == "apiKey" and state["login"] is None
    assert calls(tmp_path).count("account/login/start") == int(pending)
    assert calls(tmp_path).count("account/login/cancel") == int(pending)
    assert "account/logout" not in calls(tmp_path)
    assert "test-secret-token" not in json.dumps(state)


@pytest.mark.parametrize("outcome", ["success", "failure"])
def test_notifications_clear_code_and_hide_provider_error(account, monkeypatch, outcome):
    monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", outcome)
    assert account.start()["login"]
    state = account.status()
    assert state["login"] is None
    assert state["authenticated"] is (outcome == "success")
    assert bool(state["error"]) is (outcome == "failure")
    assert "private-server-error" not in json.dumps(state)


@pytest.mark.parametrize("url", [
    "http://auth.openai.com/codex/device", "https://auth.openai.com.evil.example/",
    "https://sample:password@auth.openai.com/", "https://chatgpt.com:9999/",
])
def test_rejects_bad_login_url_and_cancels_pending(account, monkeypatch, tmp_path, url):
    monkeypatch.setenv("ACCOUNT_TEST_URL", url)
    state = account.start()
    assert not state["available"] and state["login"] is None
    assert "account/login/cancel" in calls(tmp_path)
    assert account.rpc is None
    assert url not in json.dumps(state)


def test_provider_errors_never_exposed(account, monkeypatch):
    monkeypatch.setenv("ACCOUNT_TEST_ERROR", "1")
    result = account.start()
    assert result["error"]
    assert "test-secret-token" not in json.dumps(result)


def test_expired_login_and_server_shutdown_cancel(account, tmp_path):
    account.start()
    account.pending["deadline"] = time.monotonic() - 1
    assert "expired" in account.status()["error"]
    assert account.pending is None
    account.start()
    process = account.rpc.process
    account.close()
    assert calls(tmp_path).count("account/login/cancel") == 2
    assert process.poll() is not None


def test_http_account_routes_require_local_origin_and_csrf(tmp_path, account):
    with serving(WebService(tmp_path)) as (client, server):
        server.account = account
        assert client.get("/api/account").json()["available"]
        assert client.post("/api/account/login", json={}).status_code == 403
        headers = {"X-MathLottery-Token": server.csrf_token}
        assert client.post("/api/account/login", json={}, headers={
            **headers, "Origin": "https://example.com",
        }).status_code == 403
        assert client.post("/api/account/login", json={"password": "dummy"}, headers=headers).status_code == 400
        result = client.post("/api/account/login", json={}, headers=headers)
        assert result.status_code == 200 and result.json()["login"]
        assert "test-secret-token" not in result.text
        assert result.headers["cache-control"] == "no-store"
        assert client.post("/api/account/cancel", json={}, headers=headers).json()["login"] is None
        assert client.post("/api/account/logout", json={}, headers=headers).status_code == 400
        assert server.service.store.list_runs() == []


def test_missing_cli_returns_safe_status(tmp_path):
    account = CodexAccount(lambda: "not-a-codex-executable", root=tmp_path)
    status = account.status()
    assert not status["available"]
    assert status["error_code"] == "CLI_NOT_FOUND"
    assert "device-code" not in status["error"]
    account.close()


@pytest.mark.parametrize("platform_missing", [False, True])
def test_broken_cli_diagnostic_is_safe_and_preserves_credentials(tmp_path, platform_missing):
    executable = tmp_path / "broken-codex"
    message = "private-machine-path private-token-value"
    if platform_missing:
        message += " Missing optional dependency @openai/codex-linux-x64"
    executable.write_text(f"#!{sys.executable}\nimport sys\n"
                          f"sys.stderr.write({message!r})\nsys.exit(1)\n")
    executable.chmod(0o755)
    home = tmp_path / ".mathlottery" / "codex-home"
    home.mkdir(parents=True)
    auth = home / "auth.json"
    auth.write_text('{"fixture":"preserve-existing-login"}')
    before = auth.read_bytes()
    account = CodexAccount(lambda: str(executable), root=tmp_path)
    try:
        status = account.status()
        assert not status["available"] and status["login"] is None
        assert status["error_code"] == (
            "CLI_PLATFORM_DEPENDENCY_MISSING" if platform_missing else "CLI_UNAVAILABLE"
        )
        assert "private-" not in json.dumps(status)
        assert str(tmp_path) not in json.dumps(status)
        assert "device-code" not in status["error"]
        assert auth.read_bytes() == before
    finally:
        account.close()


def test_rpc_handles_dead_process_and_strips_api_environment(tmp_path, account, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-unused-key")
    account.status()
    process = account.rpc.process
    process.terminate()
    process.wait(timeout=2)
    assert not account.status()["available"]
    assert account.rpc is None


def test_rpc_timeout_is_bounded(tmp_path, monkeypatch):
    executable = tmp_path / "slow-codex"
    executable.write_text(f"#!{sys.executable}\n" + SCRIPT.replace(
        "method = message['method']", "method = message['method']\n    if method == 'never': continue",
    ))
    executable.chmod(0o755)
    monkeypatch.setenv("ACCOUNT_TEST_LOG", str(tmp_path / "methods.log"))
    rpc = AccountRPC(str(executable), root=tmp_path)
    try:
        with pytest.raises(ValueError, match="timed out"):
            rpc.call("never", timeout=0.05)
    finally:
        rpc.close()


@pytest.mark.parametrize("timeout", [
    AccountTimeoutError(), subprocess.TimeoutExpired("private-program", 1, output="private-token"),
])
def test_account_timeout_explains_service_environment_without_leaking_details(account, monkeypatch, timeout):
    account.status()

    def timed_out(*args, **kwargs):
        raise timeout

    monkeypatch.setattr(account.rpc, "call", timed_out)
    status = account.status()
    assert not status["available"]
    assert status["error_code"] == "ACCOUNT_TIMEOUT"
    assert "network/proxy" in status["error"]
    assert "private-" not in json.dumps(status)
    assert account.rpc is None


def test_saved_proxy_reaches_account_service_without_replacing_login(account, tmp_path, monkeypatch):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    folder = tmp_path / ".mathlottery"
    folder.mkdir()
    proxy = "http://proxy.example.invalid:8080"
    (folder / "network.json").write_text(json.dumps({"HTTPS_PROXY": proxy}))
    status = account.status()
    assert status["available"] and status["authenticated"]
    recorded = json.loads((tmp_path / "methods.log.process").read_text())
    assert recorded["environment"]["HTTPS_PROXY"] == proxy
    assert recorded["environment"]["https_proxy"] == proxy
    assert "HTTPS_PROXY" not in os.environ and "https_proxy" not in os.environ
    assert not {"account/logout", "account/login/start"}.intersection(calls(tmp_path))
    assert proxy not in json.dumps(status)


def test_invalid_network_file_has_distinct_safe_account_error(account, tmp_path):
    folder = tmp_path / ".mathlottery"
    folder.mkdir()
    (folder / "network.json").write_text('{"OPENAI_API_KEY":"private-secret"}')
    status = account.status()
    assert status["error_code"] == "NETWORK_CONFIG_INVALID"
    assert not status["available"] and account.rpc is None
    assert "private-secret" not in json.dumps(status)
    assert not (tmp_path / "methods.log").exists()


def test_external_cli_sign_in_cancels_our_pending_code(account, tmp_path, monkeypatch):
    assert account.start()["login"]
    rpc_call = account.rpc.call

    def external_account(method, params=None, **kwargs):
        if method == "account/read":
            return {"account": {"type": "chatgpt", "email": "other@example.com", "planType": "plus"}}
        return rpc_call(method, params, **kwargs)

    monkeypatch.setattr(account.rpc, "call", external_account)
    state = account.status()
    assert state["authenticated"] and state["login"] is None
    assert state["account"]["email"] == "o***@example.com"
    assert calls(tmp_path).count("account/login/cancel") == 1
    # Refreshing or clicking sign-in again must preserve the externally connected account.
    assert account.start()["authenticated"]
    assert calls(tmp_path).count("account/login/start") == 1
    assert "account/logout" not in calls(tmp_path)


def test_malformed_notification_does_not_break_pending_login(account, tmp_path):
    executable = tmp_path / "codex-test"
    executable.write_text(executable.read_text().replace(
        "if method == 'account/read':",
        "if method == 'account/read':\n        emit({'method': 'account/login/completed', "
        "'params': ['private-malformed-event']})",
    ))
    pending = account.start()["login"]
    state = account.status()
    assert state["available"] and state["login"] == pending
    assert "private-malformed-event" not in json.dumps(state)


def test_cleanup_failure_is_redacted_and_allows_reconnect(account, monkeypatch):
    account.status()
    rpc = account.rpc
    real_close = rpc.close

    def failed_call(*args, **kwargs):
        raise OSError("private-request-details")

    def failed_close():
        real_close()
        raise OSError("private-cleanup-details")

    monkeypatch.setattr(rpc, "call", failed_call)
    monkeypatch.setattr(rpc, "close", failed_close)
    state = account.status()
    assert not state["available"]
    assert "private-" not in json.dumps(state)
    assert account.rpc is None and account.pending is None
    assert rpc.process.poll() is not None
    assert account.status()["available"]


def test_concurrent_tabs_share_one_pending_login(account, tmp_path):
    with ThreadPoolExecutor(max_workers=4) as pool:
        states = list(pool.map(lambda _: account.start(), range(4)))
    assert all(state["login"] == states[0]["login"] for state in states)
    assert states[0]["login"]
    assert calls(tmp_path).count("account/login/start") == 1


def test_switch_logs_out_before_starting_device_login_and_is_idempotent(account, tmp_path, monkeypatch):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    assert account.status()["authenticated"]
    state = account.switch()
    assert not state["authenticated"] and state["account"] is None
    assert state["login"]["user_code"] == "TEST-CODE"
    assert calls(tmp_path).index("account/logout") < calls(tmp_path).index("account/login/start")
    with ThreadPoolExecutor(max_workers=4) as pool:
        states = list(pool.map(lambda _: account.switch(), range(4)))
    assert all(other["login"] == state["login"] for other in states)
    assert calls(tmp_path).count("account/logout") == 1
    assert calls(tmp_path).count("account/login/start") == 1
    assert "test-secret-token" not in json.dumps(states)
    # Cancelling replacement does not silently restore the account that was logged out.
    cancelled = account.cancel()
    assert not cancelled["authenticated"] and cancelled["account"] is None
    assert cancelled["login"] is None


@pytest.mark.parametrize("outcome", ["success", "failure"])
def test_switch_completion_removes_device_code(account, monkeypatch, outcome):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", outcome)
    assert account.switch()["login"]
    state = account.status()
    assert state["authenticated"] is (outcome == "success")
    assert bool(state["error"]) is (outcome == "failure")
    assert state["login"] is None
    assert "private-server-error" not in json.dumps(state)


def test_switch_failure_after_logout_does_not_claim_old_account_survives(account, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    monkeypatch.setenv("ACCOUNT_TEST_ERROR", "1")
    state = account.switch()
    assert state["error"] and not state["authenticated"]
    assert state["account"] is None and state["login"] is None
    assert calls(tmp_path).index("account/logout") < calls(tmp_path).index("account/login/start")
    assert "test-secret-token" not in json.dumps(state)
    # RPC reconnection must read this workspace's store, never a cached old account.
    assert not account.status()["authenticated"]


def test_logout_failure_does_not_start_replacement_login(account, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    monkeypatch.setenv("ACCOUNT_TEST_LOGOUT_ERROR", "1")
    state = account.switch()
    assert state["error"] and state["login"] is None
    assert "account/logout" in calls(tmp_path)
    assert "account/login/start" not in calls(tmp_path)
    assert "private-logout-token" not in json.dumps(state)
    # A rejected logout does not prove the account is gone; a fresh read is authoritative.
    assert account.status()["authenticated"]


def test_logout_cancels_pending_before_clearing_account(account, tmp_path):
    assert account.start()["login"]
    state = account.logout()
    assert state["available"] and not state["authenticated"]
    assert state["account"] is None and state["login"] is None
    assert calls(tmp_path).index("account/login/cancel") < calls(tmp_path).index("account/logout")
    # Repeating logout while signed out is harmless and never starts a sign-in.
    assert not account.logout()["authenticated"]
    assert calls(tmp_path).count("account/login/start") == 1
    assert calls(tmp_path).count("account/login/cancel") == 1


def test_logout_clears_signed_in_account(account, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCOUNT_TEST_SIGNED_IN", "1")
    assert account.status()["authenticated"]
    state = account.logout()
    assert state["available"] and not state["authenticated"]
    assert state["account"] is None and state["login"] is None
    assert not account.status()["authenticated"]
    assert "account/logout" in calls(tmp_path)
    assert "account/login/start" not in calls(tmp_path)


@pytest.mark.parametrize("action", ["switch", "logout"])
def test_http_account_changes_require_explicit_strict_confirmation(tmp_path, account, action):
    with serving(WebService(tmp_path)) as (client, server):
        server.account = account
        path = f"/api/account/{action}"
        confirmed = {"confirm_account_change": True}
        headers = {"X-MathLottery-Token": server.csrf_token}
        assert client.post(path, json=confirmed).status_code == 403
        assert client.post(path, json=confirmed, headers={
            **headers, "Origin": "https://example.com",
        }).status_code == 403
        for payload in (
            {}, {"confirm_account_change": False}, {"confirm_account_change": "true"},
            {"confirm_account_change": 1}, {"confirm_account_change": None},
            {"confirm_shared_account": True},
            {**confirmed, "password": "must-never-reach-provider"},
        ):
            response = client.post(path, json=payload, headers=headers)
            assert response.status_code == 400, (payload, response.text)
        assert not (tmp_path / "methods.log").exists()
        response = client.post(path, json=confirmed, headers=headers)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        assert "account/logout" in calls(tmp_path)
        assert bool(response.json()["login"]) is (action == "switch")


@pytest.mark.parametrize("action", ["switch", "logout"])
@pytest.mark.parametrize("mode", ["codex", "work", "chat"])
def test_active_codex_workers_block_workspace_account_changes(tmp_path, account, monkeypatch, action, mode):
    service = WebService(tmp_path)
    config = Config()
    config.backend.mode = mode
    run = Orchestrator(service.store).create(config, workflow=Workflow.FIND)
    monkeypatch.setattr(service.jobs, "running", lambda run_id: run_id == run.id)
    with serving(service) as (client, server):
        server.account = account
        response = client.post(f"/api/account/{action}", json={"confirm_account_change": True},
                               headers={"X-MathLottery-Token": server.csrf_token})
        if mode in {"codex", "work"}:
            assert response.status_code == 409
            assert not (tmp_path / "methods.log").exists()
        else:
            assert response.status_code == 200


@pytest.mark.parametrize("task_action", ["start", "resume"])
def test_account_switch_and_task_start_are_serialized(tmp_path, account, monkeypatch, task_action):
    service = WebService(tmp_path)
    switching, release_switch, task_started = threading.Event(), threading.Event(), threading.Event()

    def switch():
        switching.set()
        assert release_switch.wait(timeout=5)
        return {"authenticated": False, "login": None}

    def task(*args, **kwargs):
        task_started.set()
        return {"id": "run-000000000001"}

    monkeypatch.setattr(account, "switch", switch)
    monkeypatch.setattr(service, task_action, task)
    with serving(service) as (client, server), ThreadPoolExecutor(max_workers=2) as pool:
        server.account = account
        headers = {"X-MathLottery-Token": server.csrf_token}
        request = pool.submit(client.post, "/api/account/switch",
                              json={"confirm_account_change": True}, headers=headers)
        try:
            assert switching.wait(timeout=2)
            path = "/api/runs" if task_action == "start" else "/api/runs/run-000000000001/resume"
            payload = {"workflow": "find"} if task_action == "start" else {}
            task_request = pool.submit(client.post, path, json=payload, headers=headers)
            with pytest.raises(TimeoutError):
                task_request.result(timeout=0.15)
            assert not task_started.is_set()
        finally:
            release_switch.set()
        assert request.result(timeout=2).status_code == 200
        assert task_request.result(timeout=2).status_code == 202
        assert task_started.is_set()


def test_account_authentication_is_private_and_survives_restart(account, tmp_path, monkeypatch):
    """The same user may log into the workspace without importing their CLI login."""
    personal = tmp_path / "personal-codex"
    personal.mkdir()
    (personal / "auth.json").write_text('{"tokens": "synthetic-personal-login"}')
    (personal / "config.toml").write_text('cli_auth_credentials_store = "keyring"\n')
    before = {path.name: path.read_bytes() for path in personal.iterdir()}
    monkeypatch.setenv("CODEX_HOME", str(personal))
    monkeypatch.setenv("CODEX_SQLITE_HOME", str(personal))
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-openai-key")
    monkeypatch.setenv("CODEX_API_KEY", "synthetic-codex-key")
    monkeypatch.setenv("CODEX_AUTH_TOKEN", "synthetic-codex-token")
    parent_environment = dict(os.environ)
    monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", "success")

    assert not account.status()["authenticated"]
    assert account.start()["login"]
    assert account.status()["authenticated"]
    isolated_auth = tmp_path / ".mathlottery" / "codex-home" / "auth.json"
    assert json.loads(isolated_auth.read_text()) is True
    metadata = json.loads((tmp_path / "methods.log.process").read_text())
    assert metadata["environment"]["CODEX_HOME"] == str(isolated_auth.parent)
    assert metadata["environment"]["CODEX_SQLITE_HOME"].startswith(str(isolated_auth.parent))
    for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_AUTH_TOKEN"):
        assert metadata["environment"][key] is None
    assert 'cli_auth_credentials_store="file"' in metadata["argv"]

    account.close()
    assert account.status()["authenticated"]
    assert account.switch()["login"]
    assert account.status()["authenticated"]
    assert not account.logout()["authenticated"]
    account.close()
    assert not account.status()["authenticated"]
    assert {path.name: path.read_bytes() for path in personal.iterdir()} == before
    for key in ("CODEX_HOME", "CODEX_SQLITE_HOME", "OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_AUTH_TOKEN"):
        assert os.environ[key] == parent_environment[key]


def test_separate_workspaces_can_use_same_account_without_sharing_login(account, tmp_path, monkeypatch):
    monkeypatch.setenv("ACCOUNT_TEST_COMPLETE", "success")
    other_root = tmp_path / "other-workspace"
    other = CodexAccount(lambda: str(tmp_path / "codex-test"), root=other_root)
    try:
        assert account.start()["login"]
        first = account.status()
        assert first["authenticated"]
        assert not other.status()["authenticated"]
        assert other.start()["login"]
        second = other.status()
        assert second["authenticated"] and second["account"] == first["account"]
        assert not other.logout()["authenticated"]
        # Reconnect to make sure a fresh subprocess still sees the first workspace's login.
        account.close()
        assert account.status()["authenticated"]
        assert not other.status()["authenticated"]
    finally:
        other.close()


def test_deferred_workspace_is_used_when_first_connecting(tmp_path, monkeypatch):
    root = None
    seen = []

    class FakeRPC:
        notifications = []

        def __init__(self, command, root=None):
            seen.append((command, root))

        def call(self, method, *args, **kwargs):
            return {"account": None}

        def close(self):
            pass

    manager = CodexAccount(lambda: "fake-codex", root=lambda: root, rpc_factory=FakeRPC)
    assert not seen
    root = tmp_path
    try:
        assert manager.status()["available"]
        assert seen == [("fake-codex", tmp_path)]
    finally:
        manager.close()
