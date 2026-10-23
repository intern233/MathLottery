"""Independent Lean compilation, kernel replay and inspection of frozen inputs.

No Lake hooks or dependency downloads; no unsandboxed fallback. Natural-language
alignment remains outside this mechanical check. Prebuilt libraries are trusted.
"""

import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from pathlib import Path

from mathlottery import budget
from mathlottery.config import Config
from mathlottery.models import FormalCheckRequest, Run, digest, now
from mathlottery.review_evidence import validate
from mathlottery.storage import Store, atomic_write, json_text

IDENTIFIER = r"[A-Za-z_][A-Za-z_0-9']*"
MODULE = re.compile(rf"{IDENTIFIER}(?:\.{IDENTIFIER})*")
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def _output_budget_error(output, max_object_bytes, max_total_bytes):
    """Bound generated files during compilation, including unexpected temporary files."""
    total = 0
    for count, path in enumerate(output.rglob("*"), start=1):
        if count > 256:
            return "OUTPUT_LIMIT", "Compiler output exceeds the file/directory count limit"
        try:
            info = path.lstat()
        except FileNotFoundError:
            # The compiler may atomically replace temporary output during a poll.
            continue
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            return "ERROR", "Unexpected linked or special file in compiler output"
        if info.st_size > max_object_bytes:
            return "OUTPUT_LIMIT", "Compiler object exceeds the configured size limit"
        total += info.st_size
        if total > max_total_bytes:
            return "OUTPUT_LIMIT", "Compiler output exceeds the configured total size limit"
    return None


def _run(command, directory, name, deadline, cancelled):
    """Bound all subprocess output and kill the entire process group on every exit."""
    log = directory / f"{name}.log"
    started = time.monotonic()
    reason = None
    with log.open("wb") as stream:
        process = subprocess.Popen(
            command, stdout=stream, stderr=stream, start_new_session=True,
            env={"PATH": os.defpath, "LANG": "C.UTF-8"},
        )
        try:
            while process.poll() is None:
                if cancelled():
                    reason = "CANCELLED"
                    break
                if time.monotonic() >= deadline:
                    reason = "TIMEOUT"
                    break
                if os.fstat(stream.fileno()).st_size > 1_000_000:
                    reason = "OUTPUT_LIMIT"
                    break
                time.sleep(0.03)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    if log.stat().st_size > 1_000_000:
        reason = reason or "OUTPUT_LIMIT"
    with log.open("rb") as stream:
        log_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    with log.open("rb") as stream:
        output = stream.read(1_000_000)
    return {
        "status": reason or ("OK" if process.returncode == 0 else "ERROR"),
        "returncode": process.returncode, "elapsed_seconds": round(time.monotonic() - started, 3),
        "log": log.name, "log_sha256": log_hash,
        "output": output.decode("utf-8", errors="replace"),
    }


def check_snapshot(store: Store, run: Run, request: FormalCheckRequest) -> dict:
    config = Config.model_validate(run.config)
    settings = config.verification
    candidate = run.candidates[-1]
    evidence = run.review_evidence
    receipt = {
        "status": "UNAVAILABLE", "checked_at": now(), "candidate_sha256": candidate.sha256,
        "problem_sha256": digest(run.problem.statement) if run.problem else None,
        "request": request.model_dump(), "sources": [], "steps": [],
        "declarations": [], "statement_alignment": "NOT_CERTIFIED",
        "limits": {"seconds": settings.formal_timeout_seconds, "memory_mb": settings.formal_memory_mb,
                   "address_space_mb": settings.formal_address_space_mb, "thread_stack_kb": 65536,
                   "max_object_mb": settings.formal_max_object_mb,
                   "max_total_object_mb": settings.formal_max_total_object_mb,
                   "threads": 1, "memory_scope": "Lean internal threshold plus per-process RLIMIT_AS; not measured RSS or host-wide RAM"},
        "scope": "Requested theorem declarations only; imported libraries and the Lean kernel are trusted. "
                 "No independent kernel implementation or natural-language equivalence check.",
    }

    def unavailable(reason):
        receipt["reason"] = reason
        return receipt

    if not settings.formal_enabled:
        return unavailable("Independent formal checks are disabled")
    if evidence is None:
        return unavailable("No immutable proof-source snapshot was attached to this review")
    validate(evidence, candidate, run.mode)
    sources = {s.path: s for s in evidence.files}
    modules, relative_files = [], []
    module_root = request.module_root
    if module_root and not re.fullmatch(rf"{IDENTIFIER}(?:/{IDENTIFIER})*", module_root):
        return unavailable("Module root must be a plain directory path relative to the submitted workspace")
    if len(set(request.files)) != len(request.files):
        return unavailable("Formal check files must be distinct and ordered by dependencies")
    for path in request.files:
        relative = path.removeprefix("workspace/")
        if module_root:
            if not relative.startswith(module_root + "/"):
                return unavailable("Every requested Lean source must be inside the selected module root")
            relative = relative[len(module_root) + 1:]
        module = relative.removesuffix(".lean").replace("/", ".")
        if (path not in sources or not path.startswith("workspace/")
            or not path.endswith(".lean") or not MODULE.fullmatch(module)):
            return unavailable("Only attached Lean files with plain module names can be checked")
        if module.split(".")[0] in {"Init", "Lean", "Std", "Mathlib", "MathLotteryInspector"}:
            return unavailable("Submitted module would shadow a trusted library or inspector")
        modules.append(module)
        relative_files.append(relative)
        receipt["sources"].append({"path": path, "module": module, "sha256": sources[path].sha256})
    if len(set(request.declarations)) != len(request.declarations) or any(
        not MODULE.fullmatch(name) for name in request.declarations
    ):
        return unavailable("Use distinct qualified theorem names with plain identifiers")
    lean, bwrap, prlimit = (shutil.which(settings.lean_command), shutil.which("bwrap"), shutil.which("prlimit"))
    if not lean or not bwrap or not prlimit:
        return unavailable("Lean, bubblewrap and prlimit are required; no unsandboxed fallback")
    try:
        prefix = subprocess.run([lean, "--print-prefix"], capture_output=True, text=True,
                                timeout=5, check=True).stdout.strip()
        toolchain = Path(prefix).resolve(strict=True)
        if not (toolchain / "bin" / "leanchecker").is_file():
            return unavailable("This toolchain has no leanchecker for independent kernel replay")
        version = subprocess.run([lean, "--version"], capture_output=True, text=True,
                                 timeout=5, check=True).stdout.strip()
        libraries = [(store.root / p).resolve(strict=True) for p in settings.lean_library_paths]
        if any(not p.is_dir() for p in libraries):
            return unavailable("Configured prebuilt Lean libraries must be directories")
    except (OSError, subprocess.SubprocessError):
        return unavailable("Cannot resolve the configured Lean toolchain or prebuilt libraries")
    receipt["lean_version"] = version
    max_object_bytes = settings.formal_max_object_mb * 1024 * 1024
    max_total_bytes = settings.formal_max_total_object_mb * 1024 * 1024
    inspector = Path(__file__).with_name("lean_inspector.lean").read_text()
    receipt["inspector_sha256"] = digest(inspector)
    key = digest(json_text([receipt["candidate_sha256"], receipt["problem_sha256"], request.model_dump(),
                           receipt["sources"], version, receipt["inspector_sha256"], run.task_id]))
    directory = store.run_dir(run.id) / "verification" / "formal" / key
    directory.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + min(settings.formal_timeout_seconds, budget.remaining(run, config))
    def cancelled():
        return (store.run_dir(run.id) / "stop.requested").exists()
    if time.monotonic() >= deadline or cancelled():
        return unavailable("Formal check budget exhausted or run stopped")
    try:
        with tempfile.TemporaryDirectory(prefix="mathlottery-formal-") as temporary:
            root = Path(temporary)
            inputs, output = root / "inputs", root / "output"
            inputs.mkdir()
            output.mkdir()
            for path, relative in zip(request.files, relative_files, strict=True):
                destination = inputs / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(sources[path].content)
            (inputs / "MathLotteryInspector.lean").write_text(inspector)

            def command(args, writable):
                base = [prlimit, f"--as={settings.formal_address_space_mb * 1024 * 1024}",
                        f"--fsize={max_object_bytes}", "--nofile=256", "--", bwrap,
                        "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
                        "--setenv", "PATH", "/lean/bin:/usr/bin:/bin",
                        "--setenv", "LEAN_NUM_THREADS", "1",
                        "--setenv", "LEAN_STACK_SIZE_KB", "65536",
                        "--setenv", "LEAN_PATH", ":".join(["/out", *[f"/lib{i}" for i in range(len(libraries))]]),
                        "--ro-bind", str(toolchain), "/lean"]
                for system in ("/usr", "/lib", "/lib64", "/bin"):
                    if Path(system).exists():
                        base += ["--ro-bind", system, system]
                for number, library in enumerate(libraries):
                    base += ["--ro-bind", str(library), f"/lib{number}"]
                base += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                         "--ro-bind", str(inputs), "/src",
                         "--bind" if writable else "--ro-bind", str(output), "/out",
                         "--chdir", "/src", *args]
                return base

            def execute(args, label, writable=False):
                output_error = None

                def interrupted():
                    nonlocal output_error
                    if cancelled():
                        return True
                    if writable:
                        output_error = _output_budget_error(output, max_object_bytes, max_total_bytes)
                    return output_error is not None

                result = _run(command(args, writable), directory, label, deadline, interrupted)
                if writable:
                    output_error = output_error or _output_budget_error(output, max_object_bytes, max_total_bytes)
                if output_error:
                    result["status"] = output_error[0]
                receipt["steps"].append({k: v for k, v in result.items() if k != "output"} | {"argv": args})
                if result["status"] != "OK":
                    receipt.update(status=result["status"], reason=output_error[1] if output_error
                                   else f"{label} did not complete successfully")
                return result

            for index, (relative, module) in enumerate(zip(relative_files, modules, strict=True)):
                (output / relative).parent.mkdir(parents=True, exist_ok=True)
                result = execute(["/lean/bin/lean", "-j", "1", "-s", "65536", "-M", str(settings.formal_memory_mb),
                                  "-o", "/out/" + relative.removesuffix(".lean") + ".olean", relative],
                                 f"compile-{index}", True)
                if result["status"] != "OK":
                    return receipt
            # A metaprogram may have written arbitrary files to /out. Only the exact
            # expected regular object files may enter the fresh inspection sandbox.
            frozen = root / "checked"
            frozen.mkdir()
            allowed = {
                module.replace(".", "/") + suffix for module in modules
                for suffix in (".olean", ".olean.private", ".olean.server")
            }
            receipt["objects"] = []
            for path in output.rglob("*"):
                info = path.lstat()
                if stat.S_ISDIR(info.st_mode):
                    continue
                relative = path.relative_to(output).as_posix()
                if relative not in allowed or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("Unexpected file in compiler output")
                if info.st_size > max_object_bytes:
                    raise ValueError("Compiler object exceeds size limit")
                target = frozen / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target, follow_symlinks=False)
                with target.open("rb") as stream:
                    sha = hashlib.file_digest(stream, "sha256").hexdigest()
                receipt["objects"].append({"path": relative, "size": info.st_size, "sha256": sha})
            if any(not (frozen / (m.replace(".", "/") + ".olean")).is_file() for m in modules):
                raise ValueError("Compiler produced no object for a requested module")
            output = frozen
            for index, module in enumerate(modules):
                result = execute(["/lean/bin/leanchecker", module], f"replay-{index}")
                if result["status"] != "OK":
                    return receipt
            result = execute(["/lean/bin/lean", "-j", "1", "-s", "65536", "-M", str(settings.formal_memory_mb),
                              "--run", "MathLotteryInspector.lean", *modules, "--", *request.declarations],
                             "inspect")
            if result["status"] != "OK":
                return receipt
            declarations = json.loads(result["output"])
            if not isinstance(declarations, list) or [d.get("name") for d in declarations] != request.declarations:
                raise ValueError("Inspector returned mismatched declarations")
            receipt["declarations"] = declarations
            if any(set(d["axioms"]) - ALLOWED_AXIOMS for d in declarations):
                receipt.update(status="REJECTED", reason="Selected theorems depend on unapproved axioms or placeholders")
            else:
                receipt["status"] = "KERNEL_REPLAYED"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        receipt.update(status="ERROR", reason=f"Formal check failed: {type(error).__name__}")
    finally:
        receipt["artifact"] = str((directory / "receipt.json").relative_to(store.run_dir(run.id)))
        atomic_write(directory / "receipt.json", json_text(receipt))
    return receipt


def record_formal_check(store: Store, run: Run, request: FormalCheckRequest | None) -> None:
    if request is None:
        return
    result = check_snapshot(store, run, request)
    if "artifact" not in result:
        relative = f"verification/formal/{digest(json_text([run.task_id, result]))}.json"
        result["artifact"] = relative
        atomic_write(store.run_dir(run.id) / relative, json_text(result))
    run.observations.append({
        "tool": "native_formal_check", "phase": "VERIFY", "iteration": run.iteration,
        "artifact": result["artifact"], "result": result,
    })
