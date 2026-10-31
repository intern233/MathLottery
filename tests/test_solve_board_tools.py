"""Live Responses board tools and recovery of paid-call uncertainty, using HTTP fixtures."""

import json
import re

import httpx
import pytest
from test_solve_campaign import CampaignBackend, setup, theorem

from mathlottery.config import BackendConfig, ChatConfig
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.providers.chat import ChatBackend
from mathlottery.solve.board import SolveBoard
from mathlottery.solve.board_tools import BoardTools


def response(identifier, output):
    return {"id": identifier, "status": "completed", "model": "test-model", "output": output,
            "usage": {"input_tokens": 10, "output_tokens": 3,
                      "input_tokens_details": {"cached_tokens": 2}}}


def backend_with_tools(store, monkeypatch):
    _, run = setup(store, CampaignBackend())
    monkeypatch.setenv("MATHLOTTERY_TEST_BOARD_KEY", "synthetic-secret")
    backend = ChatBackend(BackendConfig(mode="chat", model="test-model",
                         chat=ChatConfig(api_key_env="MATHLOTTERY_TEST_BOARD_KEY")))
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    board = SolveBoard(store, run.id)
    backend.local_tools = BoardTools(board, "researcher", "algebra", workspace)
    directory = store.run_dir(run.id) / "tasks" / "tools"
    return backend, board, workspace, directory


def publication_call():
    message = {"id": "identity", "kind": "result", "title": "Identity", "body": "A defining equation",
               "theorem": theorem()}
    return {"type": "function_call", "name": "solve_board_publish", "call_id": "call_publish",
            "arguments": json.dumps({"message_json": json.dumps(message)})}


def test_responses_live_board_roundtrips_and_aggregated_usage(store, monkeypatch):
    backend, board, workspace, directory = backend_with_tools(store, monkeypatch)
    calls = []

    def serve(request):
        data = json.loads(request.content)
        calls.append(data)
        assert any(tool.get("type") == "web_search" for tool in data["tools"])
        assert any(tool.get("name") == "solve_board_read" for tool in data["tools"])
        if len(calls) == 1:
            assert data["previous_response_id"] == "resp_prior"
            return httpx.Response(200, json=response("resp_publish", [publication_call()]))
        if len(calls) == 2:
            assert data["previous_response_id"] == "resp_publish"
            assert data["input"][0]["call_id"] == "call_publish"
            assert json.loads(data["input"][0]["output"])["key"] == "researcher:identity"
            assert len(board.messages()) == 1
            return httpx.Response(200, json=response("resp_read", [{"type": "function_call",
                "name": "solve_board_read", "call_id": "call_read",
                "arguments": json.dumps({"key": "researcher:identity"})}]))
        assert json.loads(data["input"][0]["output"])["theorem"]["conclusion_step"] == "definition"
        return httpx.Response(200, json=response("resp_final", [{"type": "message", "content": [
            {"type": "output_text", "text": "Proof and milestone returned."}]}]))

    monkeypatch.setattr(backend, "_client", lambda: httpx.Client(transport=httpx.MockTransport(serve), base_url="https://api.example/"))
    result = backend.invoke_native("Research", directory, workspace, 5, session_id="resp_prior")
    assert result.status == BackendStatus.COMPLETED
    assert result.usage == {"input_tokens": 30, "output_tokens": 9, "cached_input_tokens": 6}
    assert result.runtime["response_count"] == 3
    assert len(board.messages()) == 1
    recovered = backend.recover_native(directory, 5)
    assert recovered.usage == result.usage and len(calls) == 3
    assert "synthetic-secret" not in "".join(p.read_text() for p in directory.rglob("*.json"))


def test_unknown_tool_continuation_never_reposts_or_republishes(store, monkeypatch):
    backend, board, workspace, directory = backend_with_tools(store, monkeypatch)
    calls = []

    def serve(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(200, json=response("resp_publish", [publication_call()]))
        raise httpx.ReadTimeout("unknown POST outcome", request=request)

    monkeypatch.setattr(backend, "_client", lambda: httpx.Client(transport=httpx.MockTransport(serve), base_url="https://api.example/"))
    result = backend.invoke_native("Research", directory, workspace, 5)
    assert result.pending and len(calls) == 2
    recovered = backend.recover_native(directory, 5)
    assert recovered.pending and recovered.status == BackendStatus.FAILED
    assert "unknown" in recovered.error
    assert len(calls) == 2 and len(board.messages()) == 1


def test_tools_are_run_scoped_and_cannot_read_arbitrary_files(store, monkeypatch):
    backend, board, workspace, directory = backend_with_tools(store, monkeypatch)
    bridge = backend.local_tools
    bridge.execute("solve_board_publish", json.loads(publication_call()["arguments"]))
    assert bridge.execute("solve_board_search", {"query": "identity", "offset": 0})["total"] == 1
    with pytest.raises(ValueError, match="No such"):
        bridge.execute("solve_board_read", {"key": "other:private"})
    with pytest.raises(ValueError, match="Choose a published"):
        bridge.execute("solve_board_material", {"sha256": "../config.yaml", "offset": 0})
    message = json.loads(json.loads(publication_call()["arguments"])["message_json"])
    message["artifacts"] = ["../private.txt"]
    with pytest.raises(ValueError, match="cannot access local files"):
        bridge.execute("solve_board_publish", {"message_json": json.dumps(message)})


def test_injected_transport_does_not_share_mutable_board_identity(store):
    from mathlottery.config import Config
    from mathlottery.models import SolveWorker
    from mathlottery.runtime.native import NativeRunner

    class SharedTransport:
        local_tools = None

        def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
            ids = dict(re.findall(r"(?m)^(run_id|task_id): (.+)$", prompt))
            self.local_tools.execute("solve_board_publish", json.loads(publication_call()["arguments"]))
            return BackendResult(BackendStatus.COMPLETED, invoked=True, text="```mathlottery\n" +
                                 json.dumps({**ids, "kind": "progress", "summary": "Published lemma"}) + "\n```\n")

    transport = SharedTransport()
    engine, run = setup(store, transport, parallel=2)
    coordinator = NativeRunner(engine).team
    for identifier in ("primary", "peer"):
        worker = SolveWorker(id=identifier, group="algebra", mode="peer", objective="Derive")
        run.native.solve_team.workers[identifier] = worker
        attempt = coordinator.prepare_attempt(run, worker)
        receipt = coordinator.attempts.invoke(run, attempt,
            f"run_id: {run.id}\ntask_id: {attempt['task_id']}\n", Config.model_validate(run.config))
        assert receipt["result"]["status"] == BackendStatus.COMPLETED
        assert transport.local_tools is None
    assert {m["key"] for m in SolveBoard(store, run.id).messages()} == {"primary:identity", "peer:identity"}
