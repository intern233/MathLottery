"""Run-scoped shared-board capabilities for Responses agents, without file access."""

import json
from uuid import uuid4

from mathlottery.solve.board import Message
from mathlottery.solve.bulletin import events, inbox, navigation
from mathlottery.solve.bulletin.contracts import BoardEvent
from mathlottery.solve.coordination_policy import view as policy_view
from mathlottery.storage.core import safe_path


class BoardTools:
    def __init__(self, board, author, group, workspace, *, task_id=None):
        self.board, self.author, self.group, self.workspace = board, author, group, workspace
        self.task_id = task_id

    @property
    def definitions(self):
        specs = [
            ("solve_board_search", "Search the live proof graph by words; empty query lists entries. "
             "This is lexical retrieval, not mathematical equivalence detection.",
             {"query": {"type": "string"}, "offset": {"type": "integer", "minimum": 0},
              "include_archived": {"type": "boolean"}}, ["query", "offset", "include_archived"]),
            ("solve_board_explore", "Explore prerequisite/consequence links without loading derivations. Includes archived premises.",
             {"key": {"type": "string"}, "direction": {"type": "string", "enum": ["premises", "consequences", "both"]},
              "depth": {"type": "integer", "minimum": 0, "maximum": 8}}, ["key", "direction", "depth"]),
            ("solve_board_activity", "See assigned work, dated self-reports and voluntary channels. Does not dispatch agents.", {}, []),
            ("solve_board_inbox", "Read your pending invitations, unread channels, related results and advisory work overlaps. "
             "No task locks, automatic joins or proof acceptance.", {}, []),
            ("solve_board_channel", "Read a public run-local collaboration transcript. Discussion is not a verified theorem.",
             {"key": {"type": "string"}}, ["key"]),
            ("solve_board_event", "Declare your chosen topic/approach/intent or open/join/post/leave/close a voluntary channel. "
             "channel_defer/decline responds to invitations; channel_ack cites an observed event. Identity is fixed. "
             "Use a new event ID for each update; invitation does not join another agent. JSON schema: "
             + json.dumps(BoardEvent.model_json_schema(), ensure_ascii=False),
             {"event_json": {"type": "string"}}, ["event_json"]),
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
            result = json.loads(path.read_text()) if path.exists() else {"admissions_closed": False}
            result["coordination_policy"] = policy_view(self.board.store.load(self.board.run_id))
            result["inbox"] = inbox.view(self.board, self.author)
            return result
        if name == "solve_board_inbox":
            return inbox.view(self.board, self.author)
        if name == "solve_board_activity":
            return {**self.board.collaboration(),
                    "coordination_policy": policy_view(self.board.store.load(self.board.run_id))}
        if name == "solve_board_channel":
            channel = next((c for c in events.channels(events.rows(self.board)) if c["key"] == arguments["key"]), None)
            if channel is None:
                raise ValueError("No such channel in this run")
            if channel["events"] and not channel["closed"]:
                self.board.event(self.author, self.group, BoardEvent(
                    id=uuid4().hex, action="channel_ack", channel=channel["key"],
                    through_event=channel["events"][-1]["key"],
                ), task_id=self.task_id)
            return channel
        if name == "solve_board_event":
            content = arguments["event_json"]
            if len(content.encode()) > 30000:
                raise ValueError("Board event exceeds 30 KB")
            event = BoardEvent.model_validate_json(content)
            created = self.board.event(self.author, self.group, event, task_id=self.task_id)
            return {"created": created, "key": f"{self.author}:{event.id}",
                    "inbox": inbox.view(self.board, self.author)}
        if name == "solve_board_explore":
            result = navigation.explore(self.board.cards(), arguments["key"],
                                        arguments.get("direction", "both"), arguments.get("depth", 1))
            self.record_read([arguments["key"]])
            return result
        values = self.board.messages()
        if name == "solve_board_search":
            return navigation.search([navigation.card(v) for v in values], arguments["query"],
                                     self._offset(arguments), arguments.get("include_archived", False))
        if name == "solve_board_read":
            value = next((v for v in values if v["key"] == arguments["key"]), None)
            if value is None:
                raise ValueError("No such message in this run")
            self.record_read([value["key"]])
            return value
        if name == "solve_board_material":
            text = self.board.material(arguments["sha256"]).decode("utf-8")
            offset = self._offset(arguments)
            self.record_read([v["key"] for v in values if any(
                a["sha256"] == arguments["sha256"] for a in v["artifacts"])][:30])
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

    def record_read(self, keys):
        if keys:
            self.board.event(self.author, self.group, BoardEvent(
                id=uuid4().hex, action="read", focus=keys,
            ), task_id=self.task_id)

    @staticmethod
    def _offset(arguments):
        value = arguments.get("offset", 0)
        if type(value) is not int or value < 0:
            raise ValueError("Offset must be a nonnegative integer")
        return value
