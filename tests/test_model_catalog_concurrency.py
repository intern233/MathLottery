"""Model discovery must not serialize unrelated tasks or reuse old account results."""

import threading
from concurrent.futures import Future, ThreadPoolExecutor

import pytest

from mathlottery.config import Config
from mathlottery.model_catalog import ModelCatalog


def configuration(*, active_custom=False):
    return Config.model_validate({
        "backend": {"provider": "research"} if active_custom else {},
        "model_providers": {
            "research": {
                "label": "Research API",
                "chat": {
                    "base_url": "https://example.invalid/v1",
                    "api_key_env": "RESEARCH_API_KEY", "tools": [],
                },
            },
            "offline": {
                "label": "Configured models",
                "chat": {
                    "base_url": "https://offline.example.invalid/v1",
                    "api_key_env": "OFFLINE_API_KEY", "tools": [],
                },
                "models": [{"id": "local-choice"}],
            },
        },
    })


def rows(identifier):
    return {"data": [{"id": identifier}]}


def track_follower(monkeypatch):
    waiting = threading.Event()

    class ObservedFuture(Future):
        def result(self, timeout=None):
            waiting.set()
            return super().result(timeout)

    monkeypatch.setattr("mathlottery.model_catalog.Future", ObservedFuture)
    return waiting


def test_slow_network_does_not_block_other_providers_validation_or_clear():
    config = configuration()
    started, release = threading.Event(), threading.Event()

    def slow():
        started.set()
        assert release.wait(5)
        return rows("remote-choice")

    catalog = ModelCatalog(lambda: config, slow)
    with ThreadPoolExecutor(max_workers=2) as pool:
        remote = pool.submit(catalog.get, "codex")
        try:
            assert started.wait(1)
            local = pool.submit(catalog.get, "offline").result(timeout=1)
            assert local["models"][0]["id"] == "local-choice"
            pool.submit(catalog.validate_selection, config).result(timeout=1)
            pool.submit(catalog.clear).result(timeout=1)
            assert not remote.done()
        finally:
            release.set()
        remote.result(timeout=1)
    assert not catalog._cache


def test_same_key_requests_share_one_fetch_and_receive_independent_results(monkeypatch):
    config = configuration()
    started, release = threading.Event(), threading.Event()
    waiting = track_follower(monkeypatch)
    calls = []

    def slow():
        calls.append(True)
        started.set()
        assert release.wait(5)
        return rows("shared-choice")

    catalog = ModelCatalog(lambda: config, slow)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(catalog.get, "codex")
        try:
            assert started.wait(1)
            second = pool.submit(catalog.get, "codex", True)
            assert waiting.wait(1)
        finally:
            release.set()
        first_result, second_result = first.result(timeout=1), second.result(timeout=1)
    assert len(calls) == 1
    first_result["models"].clear()
    assert second_result["models"][0]["id"] == "shared-choice"
    assert catalog.get("codex")["models"][0]["id"] == "shared-choice"


def test_clear_starts_new_request_without_waiting_and_old_result_cannot_repopulate():
    config = configuration()
    started, release = threading.Event(), threading.Event()
    calls = []

    def accounts():
        calls.append(True)
        if len(calls) == 1:
            started.set()
            assert release.wait(5)
            return rows("old-account-model")
        return rows("new-account-model")

    catalog = ModelCatalog(lambda: config, accounts)
    with ThreadPoolExecutor(max_workers=2) as pool:
        old = pool.submit(catalog.get, "codex")
        try:
            assert started.wait(1)
            pool.submit(catalog.clear).result(timeout=1)
            new = pool.submit(catalog.get, "codex", True).result(timeout=1)
            assert new["models"][0]["id"] == "new-account-model"
            assert not old.done()
        finally:
            release.set()
        assert old.result(timeout=1)["models"][0]["id"] == "old-account-model"
    assert catalog.get("codex")["models"][0]["id"] == "new-account-model"
    assert len(calls) == 2


def test_register_replaces_loader_without_waiting_for_previous_generation():
    config = configuration()
    started, release = threading.Event(), threading.Event()

    def old_loader(*_):
        started.set()
        assert release.wait(5)
        return [{"id": "old-adapter-model"}]

    catalog = ModelCatalog(lambda: config, lambda: rows("unused"))
    catalog.register("responses", old_loader)
    with ThreadPoolExecutor(max_workers=2) as pool:
        old = pool.submit(catalog.get, "research")
        try:
            assert started.wait(1)
            pool.submit(catalog.register, "responses", lambda *_: [{"id": "new-adapter-model"}]).result(timeout=1)
            new = pool.submit(catalog.get, "research").result(timeout=1)
            assert new["models"][0]["id"] == "new-adapter-model"
        finally:
            release.set()
        old.result(timeout=1)
    assert catalog.get("research")["models"][0]["id"] == "new-adapter-model"


@pytest.mark.parametrize("abrupt", [False, True])
def test_failed_fetch_releases_followers_and_allows_retry(monkeypatch, abrupt):
    class AdapterAbort(BaseException):
        pass

    config = configuration()
    started, release = threading.Event(), threading.Event()
    waiting = track_follower(monkeypatch)
    calls = []

    def failing():
        calls.append(True)
        if len(calls) == 1:
            started.set()
            assert release.wait(5)
            if abrupt:
                raise AdapterAbort()
            raise RuntimeError("private-error-value")
        return rows("recovered-choice")

    catalog = ModelCatalog(lambda: config, failing)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(catalog.get, "codex")
        try:
            assert started.wait(1)
            second = pool.submit(catalog.get, "codex")
            assert waiting.wait(1)
        finally:
            release.set()
        for request in (first, second):
            if abrupt:
                with pytest.raises(AdapterAbort):
                    request.result(timeout=1)
            else:
                result = request.result(timeout=1)
                assert result["error_code"] == "CATALOG_UNAVAILABLE"
                assert "private-error-value" not in str(result)
    assert not catalog._inflight
    assert catalog.get("codex", refresh=True)["models"][0]["id"] == "recovered-choice"
    assert len(calls) == 2


def test_builtin_chat_cache_tracks_its_key_while_custom_profile_is_active(monkeypatch):
    config = configuration(active_custom=True)
    monkeypatch.setenv("RESEARCH_API_KEY", "synthetic-custom-key")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-first-key")
    calls = []
    catalog = ModelCatalog(lambda: config, lambda: rows("unused"))

    def loader(*_):
        calls.append(True)
        return [{"id": f"choice-{len(calls)}"}]

    catalog.register("responses", loader)
    assert catalog.get("chat")["models"][0]["id"] == "choice-1"
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-second-key")
    assert catalog.get("chat")["models"][0]["id"] == "choice-2"
    monkeypatch.setenv("RESEARCH_API_KEY", "synthetic-other-custom-key")
    assert catalog.get("chat")["models"][0]["id"] == "choice-2"
    assert len(calls) == 2
