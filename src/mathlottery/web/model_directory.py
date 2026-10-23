"""Read Codex model metadata without changing the account panel's login flow."""

import time

from mathlottery.web.account import AccountError, AccountRPC


def codex_models(command, root, *, rpc_factory=AccountRPC):
    """Use an isolated, short-lived RPC client; never start an inference or login."""
    rpc = rpc_factory(command, root=root)
    try:
        deadline = time.monotonic() + 15
        data, cursor, seen = [], None, set()
        for _ in range(5):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AccountError("Model catalog request timed out")
            params = {"limit": 20, "includeHidden": False}
            if cursor:
                params["cursor"] = cursor
            page = rpc.call("model/list", params, timeout=remaining)
            rows = page.get("data")
            if not isinstance(rows, list) or len(rows) > 100:
                raise AccountError("Unexpected model catalog response")
            data.extend(rows)
            if len(data) > 500:
                raise AccountError("Model catalog exceeds the local limit")
            cursor = page.get("nextCursor")
            if cursor is None:
                return {"data": data}
            if not isinstance(cursor, str) or not cursor or len(cursor) > 2000 or cursor in seen:
                raise AccountError("Unexpected model catalog pagination")
            seen.add(cursor)
        raise AccountError("Model catalog exceeds the local page limit")
    finally:
        rpc.close()
