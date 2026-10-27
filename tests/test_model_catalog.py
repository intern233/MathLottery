"""Provider routing and model discovery use synthetic metadata, never inference."""

import json
import re

import httpx
import pytest
from httpx import Client as HTTPClient
from pydantic import ValidationError

from mathlottery.cli import Mode, apply_options
from mathlottery.config import Config, load_config
from mathlottery.model_catalog import ModelCatalog, normalize_codex_models
from mathlottery.web.service import (
    Overrides,
    ResumeRequest,
    StartRequest,
    WebService,
    config_summary,
)
from mathlottery.web.worker import execute


def provider_config(**backend):
    return Config.model_validate({
        "backend": backend,
        "model_providers": {
            "research": {
                "label": "Research API", "transport": "responses",
                "chat": {"base_url": "https://example.invalid/v1", "api_key_env": "RESEARCH_API_KEY", "tools": []},
                "models": [{"id": "research-model", "label": "Research model", "reasoning_efforts": ["low", "high"]}],
            },
        },
    })


def codex_models():
    return {"data": [
        {"id": "display-id", "model": "research-codex", "displayName": "Research Codex",
         "supportedReasoningEfforts": [{"reasoningEffort": "high"}, {"reasoningEffort": "max"}],
         "defaultReasoningEffort": "high", "description": "A research model", "private": "secret"},
        {"id": "no-reasoning", "supportedReasoningEfforts": []},
        {"id": "unknown-capabilities"},
    ]}


def test_provider_config_resolves_explicit_connection_and_roundtrips(tmp_path):
    config = provider_config(provider="research", model="research-model")
    assert config.backend.mode == "chat"
    assert config.backend.chat.api_key_env == "RESEARCH_API_KEY"
    assert config.backend.chat.tools == []
    assert Config.model_validate(config.model_dump()) == config
    (tmp_path / "config.yaml").write_text(json.dumps(config.model_dump()))
    assert load_config(tmp_path) == config
    summary = config_summary(config)
    assert summary["provider"] == "research"
    assert "example.invalid" not in json.dumps(summary)
    assert "RESEARCH_API_KEY" not in json.dumps(summary)


@pytest.mark.parametrize("missing", ["base_url", "api_key_env", "tools"])
def test_profiles_cannot_accidentally_inherit_openai_credentials_or_tools(missing):
    value = provider_config().model_dump()
    del value["model_providers"]["research"]["chat"][missing]
    with pytest.raises(ValidationError, match="explicitly configure"):
        Config.model_validate(value)


@pytest.mark.parametrize("transport", ["anthropic", "chat_completions", "codex"])
def test_unimplemented_transports_are_not_claimed_compatible(transport):
    value = provider_config().model_dump()
    value["model_providers"]["research"]["transport"] = transport
    with pytest.raises(ValidationError):
        Config.model_validate(value)


def test_config_and_overrides_reject_conflicting_provider_and_transport():
    with pytest.raises(ValidationError, match="conflict"):
        provider_config(provider="research", mode="codex")
    with pytest.raises(ValueError, match="conflict"):
        Overrides(provider="research", backend="codex").apply(provider_config())
    with pytest.raises(ValueError, match="Unknown"):
        Overrides(provider="missing").apply(provider_config())


def test_switch_provider_clears_incompatible_model_effort_mode_and_keeps_original():
    config = provider_config(model="research-codex", reasoning_effort="max")
    config.backend.chat.reasoning_mode = "pro"
    original = config.model_dump()
    switched = Overrides(provider="research", model="research-model").apply(config)
    assert switched.backend.model == "research-model"
    assert switched.backend.reasoning_effort is None
    assert switched.backend.chat.reasoning_mode is None
    assert switched.backend.chat.base_url == "https://example.invalid/v1"
    assert switched.backend.chat.api_key_env == "RESEARCH_API_KEY"
    assert switched.backend.chat.tools == []
    assert config.model_dump() == original
    returned = Overrides(provider="chat").apply(switched)
    assert returned.backend.model is None
    assert returned.backend.chat.base_url == "https://api.openai.com/v1"
    assert returned.backend.chat.api_key_env == "OPENAI_API_KEY"


def test_builtin_switch_keeps_explicit_chat_connection_but_clears_pro():
    config = Config()
    config.backend.chat.base_url = "https://configured.example.invalid/v1"
    config.backend.chat.reasoning_mode = "pro"
    switched = Overrides(backend="chat").apply(config)
    assert switched.backend.chat.base_url == config.backend.chat.base_url
    assert switched.backend.chat.reasoning_mode is None


def test_omission_inherits_explicit_null_clears_and_model_change_resets_effort():
    config = Config()
    config.backend.model = "original"
    config.backend.reasoning_effort = "high"
    config.backend.chat.reasoning_mode = "pro"
    assert Overrides().apply(config).backend == config.backend
    cleared = Overrides(model=None, reasoning_effort=None, reasoning_mode=None).apply(config)
    assert cleared.backend.model is None
    assert cleared.backend.reasoning_effort is None
    assert cleared.backend.chat.reasoning_mode is None
    changed = Overrides(model="new-model").apply(config)
    assert changed.backend.reasoning_effort is None
    assert changed.backend.chat.reasoning_mode is None
    explicit = Overrides(model="new-model", reasoning_effort="max").apply(config)
    assert explicit.backend.reasoning_effort == "max"


def test_configured_capabilities_validated_without_blocking_unlisted_models():
    config = provider_config(provider="research", model="research-model")
    assert Overrides(reasoning_effort="high").apply(config).backend.reasoning_effort == "high"
    with pytest.raises(ValueError, match="does not support"):
        Overrides(reasoning_effort="max").apply(config)
    with pytest.raises(ValueError, match="not declared"):
        Overrides(reasoning_mode="pro").apply(config)
    assert Overrides(model="manually-added", reasoning_effort="custom").apply(config).backend.model == "manually-added"


def test_normalization_exposes_only_bounded_model_metadata():
    value = codex_models()
    value["data"].extend([
        {"id": "hidden-model", "hidden": True},
        {"id": "bad\nmodel"}, {"id": "a" * 201},
        {"id": "unknown-capabilities"},
        {"id": "long-label", "description": "x" * 1001, "displayName": "x" * 201},
    ])
    models = normalize_codex_models(value)
    assert models[0] == {
        "id": "research-codex", "label": "Research Codex", "description": "A research model",
        "reasoning_efforts": ["high", "max"], "default_reasoning_effort": "high",
    }
    assert models[1]["reasoning_efforts"] == []
    assert models[2]["reasoning_efforts"] is None
    assert models[3]["description"] == ""
    assert models[3]["label"] == "long-label"
    assert len(models) == 4
    assert "secret" not in json.dumps(models)


def test_live_catalog_cache_refresh_and_config_change():
    config = Config()
    calls = []
    catalog = ModelCatalog(lambda: config, lambda: calls.append(True) or codex_models())
    first = catalog.get()
    assert first["source"] == "live"
    first["models"].clear()
    assert catalog.get()["models"]
    assert len(calls) == 1
    catalog.get(refresh=True)
    assert len(calls) == 2
    config.backend.codex_command = "changed-command"
    catalog.get()
    assert len(calls) == 3
    catalog.clear()
    catalog.get()
    assert len(calls) == 4


def test_selection_checks_cached_capabilities_without_io_or_config_reread():
    config = Config()
    calls = []
    catalog = ModelCatalog(lambda: config, lambda: calls.append(True) or codex_models())
    catalog.get()
    catalog.config_callback = lambda: pytest.fail("Selection must use the already resolved run config")
    selection = Overrides(model="research-codex", reasoning_effort="low").apply(config)
    with pytest.raises(ValueError, match="does not support"):
        catalog.validate_selection(selection)
    catalog.validate_selection(Overrides(model="research-codex", reasoning_effort="max").apply(config))
    catalog.validate_selection(Overrides(model="unlisted", reasoning_effort="new-effort").apply(config))
    assert len(calls) == 1
    selection.backend.codex_command = "different-connection"
    catalog.validate_selection(selection)
    catalog.ttl_seconds = -1
    catalog.validate_selection(Overrides(model="research-codex", reasoning_effort="low").apply(config))


def test_empty_efforts_reject_setting_but_unknown_efforts_allow_manual_input():
    config = Config()
    catalog = ModelCatalog(lambda: config, codex_models)
    catalog.get()
    with pytest.raises(ValueError, match="does not support"):
        catalog.validate_selection(Overrides(model="no-reasoning", reasoning_effort="max").apply(config))
    catalog.validate_selection(Overrides(model="unknown-capabilities", reasoning_effort="max").apply(config))


def test_failure_falls_back_to_configured_id_without_leaking_exception():
    config = Config()
    config.backend.model = "local-choice"

    def failure():
        raise RuntimeError("Bearer secret-forbidden https://private.invalid/account")

    catalog = ModelCatalog(lambda: config, failure)
    result = catalog.get()
    assert result["source"] == "configured"
    assert result["models"][0]["id"] == "local-choice"
    assert result["error_code"] == "CATALOG_UNAVAILABLE"
    assert "secret-forbidden" not in json.dumps(result)
    assert "private.invalid" not in json.dumps(result)


def test_configured_profiles_never_discover_or_expose_connection_secrets(monkeypatch):
    monkeypatch.setenv("RESEARCH_API_KEY", "secret-test-value")
    config = provider_config()
    catalog = ModelCatalog(lambda: config, lambda: pytest.fail("No Codex discovery needed"))
    catalog.register("responses", lambda *_: pytest.fail("Static choices need no network"))
    result = catalog.get("research")
    assert result["source"] == "configured"
    assert result["models"][0]["reasoning_efforts"] == ["low", "high"]
    assert result["providers"][-1] == {
        "id": "research", "label": "Research API", "transport": "responses",
        "reasoning_modes": [], "tool_types": [],
    }
    serialized = json.dumps(result)
    for value in ("secret-test-value", "RESEARCH_API_KEY", "example.invalid", "base_url"):
        assert value not in serialized


def mock_http(monkeypatch, handler):
    monkeypatch.setattr("mathlottery.model_catalog.httpx.Client", lambda **kwargs: HTTPClient(
        **kwargs, transport=httpx.MockTransport(handler), trust_env=False,
    ))


def test_responses_discovery_is_bounded_paginated_get_without_inventing_efforts(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-api-key")
    requests = []

    def handler(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.headers["authorization"] == "Bearer synthetic-api-key"
        assert request.url.path == "/v1/models"
        assert request.content == b""
        if len(requests) == 1:
            return httpx.Response(200, json={
                "data": [{"id": "first", "owned_by": "private-owner", "reasoning_efforts": ["invented"]}],
                "has_more": True, "last_id": "first", "next": "https://untrusted.invalid/steal",
            })
        assert request.url.params["after"] == "first"
        return httpx.Response(200, json={"data": [{"id": "second"}], "has_more": False})

    mock_http(monkeypatch, handler)
    catalog = ModelCatalog(Config, codex_models)
    result = catalog.get("chat")
    assert result["source"] == "live"
    assert [item["id"] for item in result["models"]] == ["first", "second"]
    assert all(item["reasoning_efforts"] is None for item in result["models"])
    assert "private-owner" not in json.dumps(result)
    assert "invented" not in json.dumps(result)


def test_responses_catalog_does_not_follow_redirect_with_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-api-key")
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(302, headers={"location": "https://other.invalid/models"})

    mock_http(monkeypatch, handler)
    result = ModelCatalog(Config, codex_models).get("chat")
    assert result["source"] == "unavailable"
    assert len(requests) == 1


@pytest.mark.parametrize("status,code", [(401, "CATALOG_AUTH_REQUIRED"), (404, "CATALOG_UNSUPPORTED"), (500, "CATALOG_UNAVAILABLE")])
def test_api_errors_never_surface_response_body_or_key(monkeypatch, status, code):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-api-key")
    mock_http(monkeypatch, lambda _: httpx.Response(status, text="private-ip-and-token"))
    result = ModelCatalog(Config, codex_models).get("chat")
    assert result["error_code"] == code
    assert "private-ip-and-token" not in json.dumps(result)
    assert "synthetic-api-key" not in json.dumps(result)


def test_missing_key_preserves_manual_model_entry(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = Config.model_validate({"backend": {"mode": "chat", "model": "manual-choice"}})
    result = ModelCatalog(lambda: config, codex_models).get()
    assert result["error_code"] == "API_KEY_MISSING"
    assert result["source"] == "configured"
    assert result["models"][0]["id"] == "manual-choice"


def test_oversize_and_invalid_pagination_are_safe(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-api-key")
    mock_http(monkeypatch, lambda _: httpx.Response(200, content=b"x" * 1_048_577))
    assert ModelCatalog(Config, codex_models).get("chat")["error_code"] == "CATALOG_INVALID"
    mock_http(monkeypatch, lambda _: httpx.Response(200, json={"data": [], "has_more": True}))
    assert ModelCatalog(Config, codex_models).get("chat")["error_code"] == "CATALOG_INVALID"


def test_model_preflight_rejection_does_not_save_problem_or_launch(tmp_path, monkeypatch):
    web = WebService(tmp_path)
    monkeypatch.setattr(web.jobs, "launch", lambda *_: pytest.fail("Must not launch"))

    def reject(config):
        raise ValueError("unsupported model effort")

    with pytest.raises(ValueError, match="unsupported"):
        web.start(StartRequest(workflow="solve", statement="A new mathematical question"), validate_model=reject)
    assert web.store.list_runs() == []
    assert web.store.list_problems() == []


def test_invalid_private_config_is_not_echoed_by_bootstrap_or_catalog(tmp_path):
    value = provider_config().model_dump()
    value["model_providers"]["research"]["chat"]["base_url"] = "https://user:private-secret@private.invalid/v1"
    (tmp_path / "config.yaml").write_text(json.dumps(value))
    web = WebService(tmp_path)
    bootstrap = web.bootstrap()
    catalog = ModelCatalog(web.config, codex_models).get()
    assert bootstrap["config_error"]
    assert catalog["error_code"] == "CONFIG_INVALID"
    for result in (bootstrap, catalog):
        assert "private-secret" not in json.dumps(result)
        assert "private.invalid" not in json.dumps(result)


def test_custom_selection_reaches_responses_and_resume_uses_saved_provider_snapshot(tmp_path, monkeypatch):
    """Only HTTP and process dispatch are mocked; run persistence and the agent path are real."""
    monkeypatch.setenv("RESEARCH_API_KEY", "old-synthetic-research-key")
    monkeypatch.setenv("NEW_RESEARCH_API_KEY", "new-synthetic-research-key")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key-that-must-not-be-used")
    value = provider_config().model_dump()
    value["model_providers"]["research"]["chat"]["tools"] = [{"type": "web_search"}]
    value["budget"]["max_iterations"] = 4
    (tmp_path / "config.yaml").write_text(json.dumps(value))
    requests = []

    def handler(request):
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == "https://example.invalid/v1/responses"
        assert request.headers["authorization"] == "Bearer old-synthetic-research-key"
        payload = json.loads(request.content)
        assert payload["model"] == "research-model"
        assert payload["reasoning"] == {"effort": "high"}
        assert payload["tools"] == [{"type": "web_search"}]
        assert payload["include"] == ["web_search_call.action.sources"]
        assert payload["background"] is True and payload["store"] is True
        fields = dict(re.findall(r"^(run_id|task_id): (.+)$", payload["input"], re.MULTILINE))
        checkpoint = {
            **fields, "kind": "candidate", "conclude": True,
            "candidate": {"claim": "For every natural n, n + 0 = n.",
                          "proof": "Synthetic transport fixture.", "scope": "COMPLETE"},
        }
        return httpx.Response(200, json={
            "id": f"resp_provider_fixture_{len(requests)}", "status": "completed",
            "model": payload["model"], "output": [{
                "type": "message", "role": "assistant",
                "content": [{"type": "output_text", "text": "```mathlottery\n" + json.dumps(checkpoint) + "\n```"}],
            }], "usage": {"input_tokens": 20, "output_tokens": 10},
        })

    # The shared httpx module is replaced, preserving ChatBackend._client(),
    # including its actual endpoint and environment-key selection logic.
    mock_http(monkeypatch, handler)
    web = WebService(tmp_path)

    def synchronous_worker(run_id, action, **options):
        execute(web.store, run_id, {"action": action, **options})

    monkeypatch.setattr(web.jobs, "launch", synchronous_worker)
    started = web.start(StartRequest(
        workflow="solve", statement="For every natural n, n + 0 = n.",
        options={"provider": "research", "model": "research-model", "reasoning_effort": "high"},
    ))
    run = web.store.load(started["id"])
    assert run.state == "COMPLETED", run.last_error
    assert run.config["backend"]["provider"] == "research"
    assert len(requests) == 1
    assert "previous_response_id" not in json.loads(requests[0].content)

    changed = provider_config(provider="research", model="changed-default").model_dump()
    changed["model_providers"]["research"]["chat"].update({
        "base_url": "https://new-provider.example.invalid/api", "api_key_env": "NEW_RESEARCH_API_KEY",
        "tools": [],
    })
    changed["model_providers"]["research"]["models"] = [{"id": "changed-default"}]
    (tmp_path / "config.yaml").write_text(json.dumps(changed))
    assert web.config().backend.chat.base_url == "https://new-provider.example.invalid/api"
    assert web.config().backend.model == "changed-default"
    resumed = web.resume(run.id, ResumeRequest(message="Check the saved statement once more."))
    resumed_run = web.store.load(run.id)
    assert resumed["state"] == "COMPLETED", resumed_run.last_error
    assert len(requests) == 2
    assert json.loads(requests[1].content)["previous_response_id"] == "resp_provider_fixture_1"
    assert resumed_run.config["backend"] == run.config["backend"]
    assert resumed_run.config["model_providers"] == run.config["model_providers"]
    assert len(resumed_run.candidates) == 2
    for path in web.store.run_dir(run.id).rglob("*"):
        if path.is_file():
            content = path.read_bytes()
            for secret in (
                b"old-synthetic-research-key", b"new-synthetic-research-key",
                b"synthetic-key-that-must-not-be-used",
            ):
                assert secret not in content


@pytest.mark.parametrize("mode", [Mode.codex, Mode.manual])
def test_cli_switch_away_from_custom_provider_clears_connection_and_model(mode):
    config = provider_config(provider="research", model="research-model", reasoning_effort="high")
    apply_options(config, mode, None, None)
    assert config.backend.mode == mode.value
    assert config.backend.provider is None
    assert config.backend.model is None
    assert config.backend.reasoning_effort is None
    assert config.backend.chat.reasoning_mode is None
    assert config.backend.chat.base_url == "https://api.openai.com/v1"
    assert config.backend.chat.api_key_env == "OPENAI_API_KEY"
    assert config.backend.chat.tools
    assert Config.model_validate(config.model_dump()).backend == config.backend


def test_cli_same_chat_transport_preserves_custom_provider_and_connection():
    config = provider_config(provider="research", model="research-model", reasoning_effort="high")
    original = config.backend.model_dump()
    apply_options(config, Mode.chat, "2h", 4)
    assert config.backend.model_dump() == original
    assert config.budget.max_wall_time_minutes == 120
    assert config.budget.max_iterations == 4
