from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from mathlottery.config import ToolConfig
from mathlottery.models import Model, Phase, Run, ToolCall, now
from mathlottery.storage.core import atomic_write, json_text, safe_path
from mathlottery.tooling.execution import python_exec, sympy_code
from mathlottery.tooling.sources import WebTools
from mathlottery.verify.formal import lean_check


class SearchArgs(Model):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=10)


class FetchArgs(Model):
    url: str = Field(min_length=8, max_length=3000)


class PythonArgs(Model):
    code: str = Field(min_length=1, max_length=50000)


class SympyArgs(Model):
    expression: str = Field(min_length=1, max_length=4000)
    operation: Literal["simplify", "expand", "factor", "diff"] = "simplify"


class LeanArgs(Model):
    proof: str = Field(min_length=1, max_length=40000)


class ReadArgs(Model):
    path: str = Field(min_length=1, max_length=500)


class WriteArgs(ReadArgs):
    content: str = Field(max_length=100000)


class MemoryArgs(Model):
    query: str = Field(min_length=1, max_length=1000)


ARGUMENTS = {
    "web_search": SearchArgs,
    "web_fetch": FetchArgs,
    "python_exec": PythonArgs,
    "sympy_compute": SympyArgs,
    "lean_check": LeanArgs,
    "read_artifact": ReadArgs,
    "write_artifact": WriteArgs,
    "search_memory": MemoryArgs,
}


class ToolRegistry:
    def __init__(self, directory: Path, config: ToolConfig, cancelled=lambda: False):
        self.directory = directory
        self.config = config
        self.cancelled = cancelled
        self.web = WebTools(directory, config, cancelled)

    def execute(self, call: ToolCall, run: Run, number: int) -> dict:
        task = run.task_id or f"iteration-{run.iteration}"
        relative = f"experiments/{task}-{number}"
        folder = self.directory / relative
        try:
            args = ARGUMENTS[call.name].model_validate_json(call.arguments_json)
            if self.cancelled():
                result = {"status": "CANCELLED", "reason": "Stop or time limit requested"}
            elif call.name == "web_fetch":
                result = self.web.fetch(args.url)
            elif call.name == "web_search":
                result = self.web.search(args.query, args.limit)
            elif call.name == "python_exec":
                result = python_exec(args.code, folder, self.config, self.cancelled)
            elif call.name == "sympy_compute":
                result = python_exec(
                    sympy_code(args.expression, args.operation), folder, self.config, self.cancelled
                )
            elif call.name == "lean_check":
                result = lean_check(
                    args.proof,
                    run.problem.formal_target if run.problem else None,
                    folder,
                    self.config,
                )
            elif call.name == "write_artifact":
                path = safe_path(self.directory / "artifacts", args.path)
                atomic_write(path, args.content)
                result = {"status": "OK", "path": f"artifacts/{args.path}"}
            elif call.name == "read_artifact":
                if run.phase == Phase.VERIFY:
                    raise ValueError("Independent review cannot read solver artifacts")
                path = safe_path(self.directory / "artifacts", args.path)
                if path.stat().st_size > 100000:
                    raise ValueError("Artifact exceeds text size limit")
                result = {
                    "status": "OK",
                    "content": path.read_text()[: self.config.max_output_chars],
                }
            elif call.name == "search_memory":
                if run.phase == Phase.VERIFY:
                    raise ValueError("Independent review cannot read solver memory")
                result = {
                    "status": "OK",
                    "items": [
                        m.model_dump(mode="json")
                        for m in run.memory
                        if args.query.lower() in m.content.lower()
                    ][-20:],
                }
        except Exception as error:
            result = {"status": "ERROR", "error": f"{type(error).__name__}: {error}"}
        record = {
            "tool": call.name,
            "arguments": json.loads(call.arguments_json),
            "result": result,
            "phase": str(run.phase),
            "time": now(),
            "iteration": run.iteration,
            "artifact": relative + ".json",
        }
        atomic_write(self.directory / record["artifact"], json_text(record))
        return record
