"""Small shared helpers for preparing and recording benchmark runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
TASKS = ("feature", "bug")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_new(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def source_files(task: str) -> dict[str, bytes]:
    files = {}
    for folder in (ROOT / "project", ROOT / "tasks" / f"{task}-overlay"):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file() and not any(part in {".git", "__pycache__"} for part in path.relative_to(folder).parts) and path.suffix != ".pyc":
                files[path.relative_to(folder).as_posix()] = path.read_bytes()
    return files


def digest_files(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, content in sorted(files.items()):
        # All benchmark materials are text; Git newline conversion should not
        # turn the same source revision into a different experimental condition.
        content = content.replace(b"\r\n", b"\n")
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def folder_digest(folder: Path) -> str:
    return digest_files({p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()})


def git(project: Path, *args: str, strip: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip() if strip else result.stdout
