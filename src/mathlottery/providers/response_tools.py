"""Durable Responses function-call continuation, retaining native hosted tools.

Only explicitly injected capabilities execute locally. Unknown POST outcomes are
never retried automatically; final response usage is summed across the chain.
"""

import json
import time

from mathlottery.models import digest
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.storage.core import atomic_write, json_text


def run_tools(backend, client, response, directory, deadline, cancelled, on_session):
    while True:
        result = backend._poll_response(client, response, directory, deadline, cancelled, on_session)
        if result.pending:
            return result
        response = json.loads((directory / "response.json").read_text())
        identifier = backend._response_id(response)
        atomic_write(directory / "tool-responses" / f"{identifier}.json", json_text(response))
        calls = [item for item in response.get("output", []) if item.get("type") == "function_call"]
        if result.status != BackendStatus.COMPLETED or not calls:
            return aggregate(backend, result, directory)
        if cancelled() or time.monotonic() >= deadline:
            return BackendResult(BackendStatus.INTERRUPTED, invoked=True, pending=True,
                                 error="Tool continuation paused; resume the saved response")
        bridge = backend.local_tools
        outputs = []
        for call in calls:
            call_id = call.get("call_id")
            if not isinstance(call_id, str) or not call_id:
                raise ValueError("Missing tool call ID")
            path = directory / "tool-results" / f"{digest(identifier + ':' + call_id)}.json"
            fingerprint = digest(json_text(call))
            if path.exists():
                saved = json.loads(path.read_text())
                if saved["call_sha256"] != fingerprint:
                    raise ValueError("A stored function call changed")
                output = saved["output"]
            else:
                try:
                    arguments = call.get("arguments", "{}")
                    if not isinstance(arguments, str) or len(arguments.encode()) > 150_000:
                        raise ValueError("Tool arguments exceed 150 KB")
                    args = json.loads(arguments)
                    if not isinstance(args, dict):
                        raise ValueError("Tool arguments must be an object")
                    output = bridge.execute(call["name"], args)
                except (ValueError, KeyError, TypeError, OSError) as error:
                    output = {"error": str(error)}
                atomic_write(path, json_text({"call_sha256": fingerprint, "output": output}))
            outputs.append({"type": "function_call_output", "call_id": call_id,
                            "output": json_text(output)})
        continuation = directory / "tool-continuations" / identifier
        request_path, response_path = continuation / "request.json", continuation / "response.json"
        if request_path.exists():
            if not response_path.exists():
                return BackendResult(BackendStatus.FAILED, invoked=True, pending=True,
                                     error="Tool continuation creation outcome unknown; no automatic retry")
            response = json.loads(response_path.read_text())
        else:
            request = json.loads((directory / "request.json").read_text())
            request.update(previous_response_id=identifier, input=outputs)
            atomic_write(request_path, json_text(request))
            response = backend._request(client, "POST", "responses", deadline, json=request)
            backend._response_id(response)
            atomic_write(response_path, json_text(response))
        backend._save(directory, response)


def aggregate(backend, result, directory):
    responses = [json.loads(p.read_text()) for p in sorted((directory / "tool-responses").glob("*.json"))]
    usage = {}
    for key in ("input_tokens", "output_tokens", "cached_input_tokens"):
        values = [(r.get("usage") or {}).get(key) if key != "cached_input_tokens" else
                  ((r.get("usage") or {}).get("input_tokens_details") or {}).get("cached_tokens")
                  for r in responses]
        if all(type(v) is int and v >= 0 for v in values):
            usage[key] = sum(values)
    result.usage = usage
    result.runtime["response_count"] = len(responses)
    result.runtime["source_urls"] = sorted({url for r in responses for url in backend._sources(r)})
    from mathlottery.telemetry.search import queries_from_call

    result.runtime["search_queries"] = sorted({q for r in responses for item in r.get("output", [])
                                               if item.get("status") == "completed" for q in queries_from_call(item)})
    result.runtime["tools_observed"] = sorted({item["type"] for r in responses for item in r.get("output", [])
                                               if item.get("type", "").endswith("_call")})
    return result
