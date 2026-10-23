"""Automatic Responses API transport with hosted tools and recoverable background calls."""

from __future__ import annotations

import json
import os
import re
import time

import httpx

from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import BackendConfig
from mathlottery.search_trace import queries_from_call
from mathlottery.storage import atomic_write, json_text


class ChatBackend:
    def __init__(self, config: BackendConfig):
        self.config = config

    def capabilities(self):
        return {
            "automatic": True,
            "persistent_sessions": True,
            "billing": "OpenAI API",
            "tools": self.config.chat.tools,
        }

    def check(self):
        model = self.config.model or os.environ.get("OPENAI_MODEL")
        if not os.environ.get(self.config.chat.api_key_env):
            raise ValueError(f"Chat API requires {self.config.chat.api_key_env} in the environment")
        if not model:
            raise ValueError("Chat API requires --model, backend.model or OPENAI_MODEL")
        return {
            "configured": True,
            "authentication": "API key from environment",
            "model": model,
            "reasoning_effort": self.config.reasoning_effort,
            "reasoning_mode": self.config.chat.reasoning_mode,
            "endpoint": self.config.chat.base_url,
            "connection_tested": False,
        }

    def _client(self):
        return httpx.Client(
            base_url=self.config.chat.base_url + "/",
            headers={"Authorization": "Bearer " + os.environ[self.config.chat.api_key_env]},
            follow_redirects=False,
        )

    def _request(self, client, method, path, deadline, **kwargs):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Chat API time budget reached")
        response = client.request(
            method, path, timeout=min(self.config.chat.request_timeout_seconds, remaining), **kwargs
        )
        response.raise_for_status()
        value = response.json()
        if not isinstance(value, dict):
            raise ValueError("Responses API returned a non-object response")
        return value

    @staticmethod
    def _response_id(value):
        identifier = value.get("id", "")
        if not isinstance(identifier, str) or not re.fullmatch(r"resp_[A-Za-z0-9_-]+", identifier):
            raise ValueError("Responses API returned an invalid response ID")
        return identifier

    def _save(self, directory, response):
        self._response_id(response)
        atomic_write(directory / "response.json", json_text(response))

    @staticmethod
    def _text(response):
        return "\n\n".join(
            part["text"]
            for item in response.get("output", [])
            if item.get("type") == "message"
            for part in item.get("content", [])
            if part.get("type") == "output_text" and isinstance(part.get("text"), str)
        )

    @staticmethod
    def _sources(response):
        urls = set()
        for item in response.get("output", []):
            if item.get("type") == "web_search_call":
                action = item.get("action") or {}
                for source in action.get("sources", []):
                    if source.get("url"):
                        urls.add(source["url"])
                if action.get("url"):
                    urls.add(action["url"])
            if item.get("type") == "message":
                for part in item.get("content", []):
                    for annotation in part.get("annotations", []):
                        if annotation.get("type") == "url_citation" and annotation.get("url"):
                            urls.add(annotation["url"])
        return sorted(urls)

    def _result(self, response, directory, on_session):
        identifier = self._response_id(response)
        text = self._text(response)
        atomic_write(directory / "answer.md", text)
        usage = response.get("usage") or {}
        measured = {
            k: usage[k]
            for k in ("input_tokens", "output_tokens")
            if isinstance(usage.get(k), int) and usage[k] >= 0
        }
        cached = (usage.get("input_tokens_details") or {}).get("cached_tokens")
        if isinstance(cached, int) and cached >= 0:
            measured["cached_input_tokens"] = cached
        runtime = {
            "backend": "chat",
            "model": response.get("model"),
            "reasoning_effort": (response.get("reasoning") or {}).get("effort"),
            "reasoning_mode": (response.get("reasoning") or {}).get("mode"),
            "tools_observed": sorted(
                {
                    item["type"]
                    for item in response.get("output", [])
                    if item.get("type", "").endswith("_call")
                }
            ),
            "source_urls": self._sources(response),
            "search_queries": sorted({
                query for item in response.get("output", [])
                if item.get("status") == "completed"
                for query in queries_from_call(item)
            }),
        }
        status = response.get("status")
        if status == "completed":
            on_session(identifier)
            outcome, error = BackendStatus.COMPLETED, None
        else:
            details = response.get("error") or response.get("incomplete_details") or {}
            limited = details.get("code") in {"rate_limit_exceeded", "insufficient_quota"}
            outcome = BackendStatus.RATE_LIMITED if limited else BackendStatus.INTERRUPTED
            error = f"Chat response ended with {status}: {details.get('code') or details.get('reason') or 'see response.json'}"
        return BackendResult(
            outcome,
            text=text,
            usage=measured,
            error=error,
            invoked=True,
            session_id=identifier,
            runtime=runtime,
            artifacts=[str(directory / "response.json")],
        )

    def _poll(self, client, response, directory, deadline, cancelled, on_session):
        identifier = self._response_id(response)
        while response.get("status") in {"queued", "in_progress"}:
            if cancelled() or time.monotonic() >= deadline:
                # Cancellation is also needed server-side; closing HTTP alone does not stop work.
                response = self._request(
                    client, "POST", f"responses/{identifier}/cancel", time.monotonic() + 5
                )
                self._save(directory, response)
                if response.get("status") in {"queued", "in_progress"}:
                    return BackendResult(
                        BackendStatus.INTERRUPTED,
                        invoked=True,
                        pending=True,
                        error="Chat cancellation is pending; resume will retrieve this response",
                    )
                break
            end = min(deadline, time.monotonic() + self.config.chat.poll_interval_seconds)
            while time.monotonic() < end and not cancelled():
                time.sleep(min(0.1, max(0, end - time.monotonic())))
            if cancelled() or time.monotonic() >= deadline:
                continue
            response = self._request(client, "GET", f"responses/{identifier}", deadline)
            if self._response_id(response) != identifier:
                raise ValueError(
                    "Responses API returned a different response; refusing to mix context"
                )
            self._save(directory, response)
        return self._result(response, directory, on_session)

    def invoke_native(
        self,
        prompt,
        directory,
        workspace,
        timeout,
        session_id=None,
        reviewer=False,
        cancelled=lambda: False,
        on_session=lambda value: None,
    ):
        return self._invoke(prompt, directory, timeout, session_id, cancelled, on_session)

    def recover_native(
        self, directory, timeout, cancelled=lambda: False, on_session=lambda value: None
    ):
        return self._invoke(None, directory, timeout, None, cancelled, on_session, recover=True)

    def _invoke(self, prompt, directory, timeout, session_id, cancelled, on_session, recover=False):
        try:
            setup = self.check()
        except ValueError as error:
            return BackendResult(BackendStatus.UNSUPPORTED, error=str(error), pending=recover)
        if (cancelled() or timeout <= 0) and not recover:
            return BackendResult(
                BackendStatus.INTERRUPTED, error="Time budget exhausted", pending=recover
            )
        directory.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout
        response = None
        submitted = recover
        try:
            with self._client() as client:
                if recover:
                    path = directory / "response.json"
                    if not path.exists():
                        return BackendResult(
                            BackendStatus.FAILED,
                            pending=True,
                            error="Previous creation outcome is unknown: no response ID was received. "
                            "Check the API dashboard before starting a new run; no automatic retry.",
                        )
                    response = json.loads(path.read_text())
                    identifier = self._response_id(response)
                    # Reuse a final durable result without another model invocation.
                    if (
                        response.get("status") in {"queued", "in_progress"}
                        and not cancelled()
                        and time.monotonic() < deadline
                    ):
                        response = self._request(client, "GET", f"responses/{identifier}", deadline)
                        if self._response_id(response) != identifier:
                            raise ValueError("Responses API returned a different response")
                        self._save(directory, response)
                else:
                    if (directory / "request.json").exists():
                        raise ValueError("Chat attempt already exists; recover it instead")
                    request = {
                        "model": setup["model"],
                        "input": prompt,
                        "background": True,
                        "store": True,
                        "tools": self.config.chat.tools,
                    }
                    if session_id:
                        self._response_id({"id": session_id})
                        request["previous_response_id"] = session_id
                    reasoning = {}
                    if self.config.reasoning_effort:
                        reasoning["effort"] = self.config.reasoning_effort
                    if self.config.chat.reasoning_mode:
                        reasoning["mode"] = self.config.chat.reasoning_mode
                    if reasoning:
                        request["reasoning"] = reasoning
                    if any(t.get("type") == "web_search" for t in self.config.chat.tools):
                        request["include"] = ["web_search_call.action.sources"]
                    atomic_write(directory / "prompt.md", prompt)
                    atomic_write(directory / "request.json", json_text(request))
                    submitted = True
                    response = self._request(client, "POST", "responses", deadline, json=request)
                    self._save(directory, response)
                return self._poll(client, response, directory, deadline, cancelled, on_session)
        except KeyboardInterrupt:
            if response:
                try:
                    with self._client() as client:
                        value = self._request(
                            client,
                            "POST",
                            f"responses/{self._response_id(response)}/cancel",
                            time.monotonic() + 5,
                        )
                        self._save(directory, value)
                        return self._poll(
                            client, value, directory, time.monotonic(), lambda: True, on_session
                        )
                except (httpx.HTTPError, ValueError, TimeoutError, KeyboardInterrupt):
                    pass
            return BackendResult(
                BackendStatus.INTERRUPTED,
                invoked=submitted,
                pending=submitted,
                error="Interrupted; resume retrieves the saved API response without creating another",
            )
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            # Do not persist headers, credentials or arbitrary error bodies.
            outcome = BackendStatus.RATE_LIMITED if status == 429 else BackendStatus.FAILED
            pending = recover or response is not None or status >= 500
            return BackendResult(
                outcome,
                invoked=submitted,
                pending=pending,
                error=f"Chat API HTTP {status}; check model, tools, endpoint and API account. No fallback.",
            )
        except (httpx.HTTPError, ValueError, OSError, TimeoutError) as error:
            return BackendResult(
                BackendStatus.FAILED,
                invoked=submitted,
                pending=submitted,
                error=f"Chat API {type(error).__name__}; artifacts preserved; no automatic retry",
            )
