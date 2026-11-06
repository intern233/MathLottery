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


@pytest.mark.parametrize("resume_state", ["cancelled", "in_progress", "changed_route", "changed_output"])
def test_resume_after_cancelled_tool_child_retains_outputs_without_reexecution(store, monkeypatch, resume_state):
    backend, board, workspace, _ = backend_with_tools(store, monkeypatch)
    root = store.run_dir(board.run_id)
    first = root / "tasks/task-first/attempt-first"
    second = root / "tasks/task-second/attempt-second"
    turn = {"worker_id": "researcher", "slot_id": "agent-fixture", "route_sha256": "pinned"}
    for directory in (first, second):
        directory.mkdir(parents=True)
        (directory / "turn.json").write_text(json.dumps(turn))
    requests = []
    sessions = []
    executed = []
    execute = backend.local_tools.execute

    def counted(name, args):
        executed.append(name)
        return execute(name, args)

    backend.local_tools.execute = counted

    def serve(request):
        requests.append(request)
        if request.url.path.endswith("/cancel"):
            return httpx.Response(200, json={"id": "resp_child", "status": "cancelled", "output": []})
        data = json.loads(request.content)
        if len(requests) == 1:
            return httpx.Response(200, json=response("resp_parent", [publication_call()]))
        if len(requests) == 2:
            return httpx.Response(200, json={"id": "resp_child", "status": "queued", "output": []})
        assert data["previous_response_id"] == "resp_parent"
        assert data["input"][0]["type"] == "function_call_output"
        assert data["input"][0]["call_id"] == "call_publish"
        assert json.loads(data["input"][0]["output"])["key"] == "researcher:identity"
        assert data["input"][1] == {"role": "user", "content": "Continue the same research"}
        return httpx.Response(200, json=response("resp_final", [{"type": "message", "content": [
            {"type": "output_text", "text": "Continued with the original tool results."}]}]))

    monkeypatch.setattr(backend, "_client", lambda: httpx.Client(
        transport=httpx.MockTransport(serve), base_url="https://api.example/"))
    interrupted = backend.invoke_native("Research", first, workspace, 5,
                                        cancelled=lambda: len(requests) >= 2, on_session=sessions.append)
    assert interrupted.status == BackendStatus.INTERRUPTED and not interrupted.pending
    assert sessions[-1] == "resp_parent"
    assert executed == ["solve_board_publish"] and len(board.messages()) == 1
    if resume_state == "changed_route":
        (second / "turn.json").write_text(json.dumps({**turn, "route_sha256": "other-account"}))
    elif resume_state == "in_progress":
        saved = json.loads((first / "response.json").read_text())
        saved["status"] = "in_progress"
        (first / "response.json").write_text(json.dumps(saved))
    elif resume_state == "changed_output":
        path = first / "tool-continuations/resp_parent/request.json"
        saved = json.loads(path.read_text())
        saved["input"][0]["output"] = '{"forged": true}'
        path.write_text(json.dumps(saved))
    continued = backend.invoke_native("Continue the same research", second, workspace, 5,
                                      session_id=sessions[-1])
    assert executed == ["solve_board_publish"] and len(board.messages()) == 1
    if resume_state == "cancelled":
        assert continued.status == BackendStatus.COMPLETED and len(requests) == 4
        replay = json.loads((second / "resumed-tool-context.json").read_text())
        assert replay["tools_reexecuted"] is False
    else:
        assert continued.status == BackendStatus.FAILED and len(requests) == 3
        assert not continued.invoked and not continued.pending


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
