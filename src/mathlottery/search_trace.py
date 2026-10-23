"""Search queries observed in tool inputs, never inferred from an agent's answer."""

import json
import re


def queries_from_call(item: dict) -> set[str]:
    kind = item.get("type")
    if item.get("status") in {"failed", "in_progress", "queued"} or item.get("error"):
        return set()
    if kind in {"web_search", "web_search_call"}:
        arguments = item.get("action") or {}
    elif kind in {"mcp_tool_call", "mcp_call"}:
        name = item.get("tool") or item.get("name") or ""
        result = item.get("result") or {}
        if (item.get("status") != "completed" or not isinstance(name, str) or not re.search(r"(^|[_\W])search([_\W]|$)", name)
            or isinstance(result, dict) and result.get("isError")):
            return set()
        arguments = item.get("arguments") or {}
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                return set()
    else:
        return set()

    def extract(value, depth=0):
        if not isinstance(value, dict) or depth > 4:
            return set()
        found = {q.strip() for q in (value.get("query"), value.get("q")) if isinstance(q, str) and q.strip()}
        for key in ("queries", "search_query", "search_queries", "system2_search_query"):
            entries = value.get(key)
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, str) and entry.strip():
                        found.add(entry.strip())
                    elif isinstance(entry, dict):
                        found.update(extract(entry, depth + 1))
        return found

    return extract(arguments)
