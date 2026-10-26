"""Check exported bytes only; never execute supplied research or build scripts."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / "handoff/files.json").read_text(encoding="utf-8"))
failures = []
for entry in manifest["files"]:
    relative = Path(entry["path"])
    target = root / relative
    if relative.is_absolute() or ".." in relative.parts or any(
        path.is_symlink() for path in [target, *target.parents] if path != root.parent
    ) or not target.is_file():
        failures.append(str(relative))
        continue
    if target.stat().st_size != entry["size"] or hashlib.sha256(target.read_bytes()).hexdigest() != entry["sha256"]:
        failures.append(str(relative))
if failures:
    raise SystemExit("File integrity check failed: " + ", ".join(failures))
print("All listed file hashes match. This does not verify mathematics or certify novelty.")
