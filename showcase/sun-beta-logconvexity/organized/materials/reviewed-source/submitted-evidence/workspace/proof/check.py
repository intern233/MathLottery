"""Compile the proof using the existing Lean 4.35/mathlib cache, without builds."""

import os
import subprocess
import sys
from pathlib import Path

workspace = Path(__file__).resolve().parent.parent
roots = [workspace, *workspace.parents]
toolchains = next(
    (
        p / ".mathlottery/toolchains"
        for p in roots
        if (p / ".mathlottery/toolchains/mathlib4-v4.35.0").is_dir()
    ),
    None,
)
if toolchains is None:
    sys.exit("Existing Lean 4.35/mathlib cache not found; no download or build attempted.")
mathlib = toolchains / "mathlib4-v4.35.0"
lean = toolchains / "lean-4.35.0-linux/bin/lean"
paths = [workspace / "proof", mathlib / ".lake/build/lib/lean"]
paths.extend(sorted((mathlib / ".lake/packages").glob("*/.lake/build/lib/lean")))
env = os.environ.copy()
env["LEAN_PATH"] = os.pathsep.join(map(str, paths))
files = sys.argv[1:] or ["SunBeta"]
for name in files:
    name = name.removesuffix(".lean")
    log_path = workspace / "research" / f"lean_{name}.log"
    with log_path.open("w") as log_file:
        process = subprocess.Popen(
            [str(lean), "-j1", "-o", f"proof/{name}.olean", f"proof/{name}.lean"],
            cwd=workspace,
            env=env,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            code = process.wait(timeout=900)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            print(f"{name}: exceeded 900 seconds; log retained.", flush=True)
            sys.exit(124)
    log = log_path.read_text()
    print(log or f"{name}: compiled successfully", flush=True)
    if code:
        sys.exit(code)
