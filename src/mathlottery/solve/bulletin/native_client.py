"""Copied into each native workspace: read local projections, submit identity-bound events."""

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path


def main():
    # The helper's root is its own workspace, never the caller's current directory.
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    import _board_navigation as nav
    import _board_validation as validation

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["search", "explore", "read", "material", "status", "inbox",
                                          "channel", "event", "publish", "validate"])
    parser.add_argument("value", nargs="?", default="")
    parser.add_argument("--archived", action="store_true")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--direction", default="both")
    parser.add_argument("--query", help="Alias for the search query positional argument")
    args = parser.parse_args()

    def read(path):
        return json.loads((root / path).read_text())

    def emit(event, folder_name="outbox-events"):
        # No user-controlled path component; the controller validates the full event.
        folder = root / folder_name
        folder.mkdir(exist_ok=True)
        # Keep creation order when the controller scans a final batch: join must
        # precede post, and the latest activity must remain the latest report.
        name = f"{time.time_ns():020d}-{hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()}"
        temporary = folder / f".{uuid.uuid4().hex}.tmp"
        temporary.write_text(json.dumps(event, ensure_ascii=False))
        os.replace(temporary, folder / f"{name}.json")

    def receipt(keys):
        if keys:
            emit({"id": uuid.uuid4().hex, "action": "read", "focus": keys[:30]})

    cards = read("bulletin/archive/index.json")
    if args.action == "search":
        result = nav.search(cards, args.query if args.query is not None else args.value, args.offset, args.archived)
    elif args.action == "explore":
        result = nav.explore(cards, args.value, args.direction, args.depth)
        receipt([args.value])
    elif args.action == "read":
        if args.value not in {c["key"] for c in cards}:
            raise ValueError("No such message in this run")
        result = read(nav.archive_path(args.value))
        receipt([args.value])
    elif args.action == "material":
        if len(args.value) != 64 or any(c not in "0123456789abcdef" for c in args.value):
            raise ValueError("Supply a published SHA256")
        if args.offset < 0:
            raise ValueError("Offset must be nonnegative")
        content = (root / f"bulletin/materials/{args.value}.txt").read_bytes()
        if hashlib.sha256(content).hexdigest() != args.value:
            raise ValueError("Published material no longer matches its frozen hash")
        text = content.decode("utf-8")
        result = {"text": text[args.offset:args.offset + 30000], "total_chars": len(text),
                  "next_offset": args.offset + 30000 if args.offset + 30000 < len(text) else None}
        owners = [c["key"] for c in cards if any(a["sha256"] == args.value
                  for a in read(c["path"])["artifacts"])]
        receipt(owners)
    elif args.action == "status":
        result = read("bulletin/collaboration/index.json")
        result["inbox"] = read("bulletin/inbox.json")
        control = root / "bulletin/control.json"
        result["control"] = json.loads(control.read_text()) if control.exists() else {}
    elif args.action == "inbox":
        result = read("bulletin/inbox.json")
    elif args.action == "channel":
        digest = hashlib.sha256(args.value.encode()).hexdigest()
        result = read(f"bulletin/collaboration/channels/{digest}.json")
        if result["events"] and not result["closed"]:
            emit({"id": uuid.uuid4().hex, "action": "channel_ack", "channel": args.value,
                  "through_event": result["events"][-1]["key"]})
    else:
        publication = args.action in {"publish", "validate"}
        limit = 100000 if publication else 30000
        content = args.value
        if not content.lstrip().startswith("{"):
            path = (root / content.removeprefix("@")).resolve()
            path.relative_to(root)
            if path.stat().st_size > limit:
                raise ValueError("Input exceeds the board size limit")
            with path.open("rb") as stream:
                content = stream.read(limit + 1).decode("utf-8")
        if len(content.encode()) > limit:
            raise ValueError("Input exceeds the board size limit")
        value = json.loads(content)
        schema = read("board-message.schema.json" if publication else "board-event.schema.json")
        problems = validation.errors(value, schema)
        if problems:
            raise ValueError("Preflight rejected: " + "; ".join(problems[:20]) +
                             ". Nothing was queued; fix the input and retry. See bulletin/README.md.")
        if publication:
            for relative in value.get("artifacts", []):
                path = (root / relative).resolve()
                path.relative_to(root)
                if path.stat().st_size > 2000000:
                    raise ValueError("Proof material exceeds 2 MB")
                with path.open("rb") as stream:
                    material = stream.read(2000001)
                if len(material) > 2000000:
                    raise ValueError("Proof material grew beyond 2 MB")
                material.decode("utf-8")
        if args.action != "validate":
            emit(value, "outbox" if publication else "outbox-events")
        result = {"queued": args.action != "validate", "preflight": "passed", "id": value["id"],
                  "note": "Controller validation is still required. Confirm in bulletin/publications.json "
                          "or bulletin/event-errors.json; preflight is not proof approval."}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(1) from error
