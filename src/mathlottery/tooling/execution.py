from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from mathlottery.config import ToolConfig
from mathlottery.storage.core import atomic_write, json_text


def python_exec(code: str, directory: Path, config: ToolConfig, cancelled=lambda: False) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    workspace = directory / "workspace"
    workspace.mkdir(exist_ok=True)
    atomic_write(directory / "experiment.py", code)
    payload = {
        "code": code,
        "memory_mb": config.memory_mb,
        "seconds": config.timeout_seconds,
        "output_limit": config.max_output_chars,
    }
    atomic_write(directory / "input.json", json_text(payload))
    worker = Path(__file__).with_name("sandbox_worker.py")
    environment = {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONHASHSEED": "0",
        "HOME": str(workspace),
        "TMPDIR": str(workspace),
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
    }
    started = time.monotonic()
    reason = None
    with (
        (directory / "stdout.txt").open("w+") as out,
        (directory / "stderr.txt").open("w+") as err,
        (directory / "input.json").open() as inp,
    ):
        process = subprocess.Popen(
            [sys.executable, "-I", str(worker)],
            stdin=inp,
            stdout=out,
            stderr=err,
            cwd=workspace,
            env=environment,
            start_new_session=True,
        )
        try:
            while process.poll() is None:
                if cancelled():
                    reason = "CANCELLED"
                    break
                if time.monotonic() - started >= config.timeout_seconds:
                    reason = "TIMEOUT"
                    break
                if (
                    os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size
                    > config.max_output_chars * 4
                ):
                    reason = "OUTPUT_LIMIT"
                    break
                time.sleep(0.02)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        out.seek(0)
        err.seek(0)
        stdout, stderr = out.read(config.max_output_chars), err.read(config.max_output_chars)
    status = reason or (
        "OK" if process.returncode == 0 else "UNAVAILABLE" if process.returncode == 78 else "ERROR"
    )
    return {
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "scope": "Computational experiment only; successful execution is not a general proof.",
        "isolation": "Linux Landlock + seccomp + rlimits",
    }


def sympy_code(expression: str, operation: str) -> str:
    if operation not in {"simplify", "expand", "factor", "diff"}:
        raise ValueError("Unsupported SymPy operation")
    if len(expression) > 4000:
        raise ValueError("Expression is too long")
    # sympify uses evaluation internally; it runs only inside the OS-isolated worker.
    return (
        "import sympy as s\n"
        f"expression = s.sympify({expression!r})\n"
        f"print(s.{operation}(expression))\n"
    )
