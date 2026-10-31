"""Run-scoped shared-board capabilities for Responses agents, without file access."""

import json

from mathlottery.solve.board import Message
from mathlottery.storage.core import safe_path


class BoardTools:
    def __init__(self, board, author, group, workspace):
        self.board, self.author, self.group, self.workspace = board, author, group, workspace

    @property
    def definitions(self):
        specs = [
            ("solve_board_search", "Search the live proof graph by words; empty query lists entries. "
             "This is lexical retrieval, not mathematical equivalence detection.",
             {"query": {"type": "string"}, "offset": {"type": "integer", "minimum": 0}}, ["query", "offset"]),
            ("solve_board_read", "Read a published message and its proof chain by exact key.",
             {"key": {"type": "string"}}, ["key"]),
            ("solve_board_material", "Read a frozen proof material in chunks, using its hash.",
             {"sha256": {"type": "string"}, "offset": {"type": "integer", "minimum": 0}}, ["sha256", "offset"]),
            ("solve_board_publish", "Publish a theorem with proof steps, or progress/objection. "
             "Supply a Message JSON string. No local file artifacts in this transport.",
             {"message_json": {"type": "string", "description": "JSON conforming to: "
                               + json.dumps(Message.model_json_schema(), ensure_ascii=False)}}, ["message_json"]),
            ("solve_board_status", "Read current admissions/review status; budget expiry does not cancel this attempt.", {}, []),
        ]
        return [{"type": "function", "name": name, "description": description, "strict": True,
                 "parameters": {"type": "object", "properties": fields, "required": required,
                                "additionalProperties": False}}
                for name, description, fields, required in specs]

    def execute(self, name, arguments):
        if name == "solve_board_status":
            path = safe_path(self.workspace, "bulletin/control.json")
            return json.loads(path.read_text()) if path.exists() else {"admissions_closed": False}
        values = self.board.messages()
        if name == "solve_board_search":
            words = str(arguments["query"]).casefold().split()
            offset = self._offset(arguments)
            ranked = []
            for value in values:
                haystack = (value["title"] + " " + value["body"] + " "
                            + (value.get("theorem") or {}).get("statement", "")).casefold()
                score = sum(word in haystack for word in words)
                if not words or score:
                    ranked.append((score, value))
            ranked.sort(key=lambda pair: -pair[0])
            return {"total": len(ranked), "next_offset": offset + 20 if offset + 20 < len(ranked) else None,
                    "messages": [{k: v[k] for k in (
                        "key", "title", "standing", "content_sha256", "depends_on"
                    )} for _, v in ranked[offset:offset + 20]]}
        if name == "solve_board_read":
            value = next((v for v in values if v["key"] == arguments["key"]), None)
            if value is None:
                raise ValueError("No such message in this run")
            return value
        if name == "solve_board_material":
            text = self.board.material(arguments["sha256"]).decode("utf-8")
            offset = self._offset(arguments)
            return {"text": text[offset:offset + 30000], "total_chars": len(text),
                    "next_offset": offset + 30000 if offset + 30000 < len(text) else None}
        if name == "solve_board_publish":
            content = arguments["message_json"]
            if len(content.encode()) > 100_000:
                raise ValueError("Message exceeds 100 KB; split the derivation into linked lemmas")
            message = Message.model_validate_json(content)
            if message.artifacts:
                raise ValueError("Publish proof_steps/body inline; this tool cannot access local files")
            created = self.board.publish(self.author, self.group, message, self.workspace)
            return {"key": f"{self.author}:{message.id}", "created": created}
        raise ValueError("Unknown shared-board tool")

    @staticmethod
    def _offset(arguments):
        value = arguments.get("offset", 0)
        if type(value) is not int or value < 0:
            raise ValueError("Offset must be a nonnegative integer")
        return value
