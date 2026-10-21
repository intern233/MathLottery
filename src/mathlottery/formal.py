"""Optional Lean check of a user-pinned statement; never assert informal equivalence."""

import os
import re
import shutil
import subprocess
from pathlib import Path

from mathlottery.config import ToolConfig
from mathlottery.models import digest
from mathlottery.storage import atomic_write


def lean_check(proof: str, target: str | None, directory: Path, config: ToolConfig) -> dict:
    if not target:
        return {"status": "UNAVAILABLE", "reason": "No user-pinned formal_target for this problem"}
    # The model supplies only a proof term, never the trusted theorem declaration.
    forbidden = r"\b(sorry|sorryAx|admit|axiom|unsafe|set_option|run_tac|run_elab|elab|macro|syntax|opaque|import|theorem|def|namespace|section|end|instance|notation|attribute)\b|#"
    if re.search(forbidden, proof):
        return {
            "status": "REJECTED",
            "reason": "Forbidden placeholder, declaration or metaprogram",
            "formal_target_sha256": digest(target),
        }
    executable = shutil.which(config.lean_command)
    bwrap = shutil.which("bwrap")
    if not executable or not bwrap:
        return {
            "status": "UNAVAILABLE",
            "reason": "Lean 4 and bubblewrap are required for isolated checks",
        }
    directory.mkdir(parents=True, exist_ok=True)
    source = (
        f"theorem mathlottery_target : {target} :=\n{proof}\n#print axioms mathlottery_target\n"
    )
    atomic_write(directory / "Candidate.lean", source)
    try:
        prefix = subprocess.run(
            [executable, "--print-prefix"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
        toolchain = Path(prefix).resolve()
        lean = toolchain / "bin" / "lean"
        if not lean.is_file():
            return {"status": "UNAVAILABLE", "reason": "Cannot locate a real Lean toolchain"}
        command = [
            bwrap,
            "--unshare-all",
            "--die-with-parent",
            "--new-session",
            "--clearenv",
            "--setenv",
            "PATH",
            f"{toolchain}/bin:/usr/bin:/bin",
            "--ro-bind",
            str(toolchain),
            str(toolchain),
        ]
        for item in ("/usr", "/lib", "/lib64", "/bin"):
            if Path(item).exists() and not toolchain.is_relative_to(item):
                command += ["--ro-bind", item, item]
        command += [
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--tmpfs",
            "/tmp",
            "--bind",
            str(directory),
            "/work",
            "--chdir",
            "/work",
            str(lean),
            "Candidate.lean",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds,
            env={"PATH": os.defpath, "LANG": "C.UTF-8"},
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"status": "ERROR", "reason": str(error)}
    log = result.stdout + result.stderr
    atomic_write(directory / "lean.log", log)
    names = re.findall(r"depends on axioms:\s*\[([^]]*)\]", result.stdout)
    axioms = {name.strip() for group in names for name in group.split(",") if name.strip()}
    printed = bool(names) or "does not depend on any axioms" in result.stdout
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    passed = result.returncode == 0 and printed and axioms <= allowed
    return {
        "status": "KERNEL_CHECKED" if passed else "REJECTED",
        "stdout": log[: config.max_output_chars],
        "returncode": result.returncode,
        "axioms": sorted(axioms),
        "formal_target": target,
        "formal_target_sha256": digest(target),
        "source_sha256": digest(source),
        "statement_alignment": "NOT_ASSESSED",
        "scope": "Pinned Lean statement compiled; independent lean4checker/comparator not run. "
        "This does not certify the original natural-language claim.",
    }
