"""Create one clean, independently versioned benchmark workspace."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

from benchlib import ROOT, TASKS, digest_files, folder_digest, git, read_json, source_files, write_json_new


def prepare(task: str, condition: str, run_id: str, destination: Path, record: Path) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run_id):
        raise ValueError("run-id must contain only letters, numbers, underscores and hyphens (1-80 characters)")
    destination = destination.resolve()
    record = record.resolve()
    if destination.exists():
        raise ValueError(f"Destination already exists; choose a fresh path: {destination}")
    if record.exists():
        raise ValueError(f"Run record already exists: {record}")
    if record.is_relative_to(destination):
        raise ValueError("Keep the run record outside the tested project")
    if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / "local-runs") and not destination.is_relative_to(ROOT / ".scratch"):
        raise ValueError("Inside the experiment folder, use local-runs/ or .scratch/ for workspaces")
    files = source_files(task)
    freeze = read_json(ROOT / "freeze.json")
    fingerprint = digest_files(files)
    prompt_path = ROOT / "tasks" / f"{task}.md"
    prompt_digest = digest_files({"prompt.md": prompt_path.read_bytes()})
    config_digest = folder_digest(ROOT / "configs" / condition)
    if fingerprint != freeze["tasks"][task]["source_sha256"] or prompt_digest != freeze["tasks"][task]["prompt_sha256"]:
        raise ValueError("Task materials changed since freeze.json; version the experiment before running")
    if config_digest != freeze["conditions"][condition]["snapshot_sha256"]:
        raise ValueError("Configuration snapshot changed since freeze.json")

    destination.mkdir(parents=True)
    # Failures leave this newly created workspace for inspection; never remove
    # an existing directory or silently retry over a partial preparation.
    for name, content in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    git(destination, "init", "-q", "-b", "main")
    git(destination, "config", "core.autocrlf", "false")
    git(destination, "add", "--all")
    git(destination, "-c", "user.name=Config AB Fixture", "-c", "user.email=config-ab@example.invalid", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=.git/hooks", "commit", "-q", "-m", "Initial project")
    run = {
        "schema_version": 1,
        "experiment_version": freeze["experiment_version"],
        "run_id": run_id,
        "task": task,
        "condition": condition,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": str(destination),
        "baseline_commit": git(destination, "rev-parse", "HEAD"),
        "source_sha256": fingerprint,
        "prompt_sha256": prompt_digest,
        "config_snapshot_sha256": config_digest,
        "runtime": {
            "configuration_verified": False,
            "visible_roles": None,
            "main_model": None,
            "reasoning_effort": None,
            "speed": None,
            "app_version": None,
            "session_id": None,
        },
        "started_at_utc": None,
        "finished_at_utc": None,
        "stop_reason": None,
        "usage_before": None,
        "usage_after": None,
        "usage_measurement_notes": None,
        "interventions": [],
        "evaluation_file": None,
        "transcript_file": None,
        "notes": "Preparation records the intended condition; it does not load or verify Codex configuration.",
    }
    write_json_new(record, run)
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--condition", choices=("A", "B"), required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--record", type=Path, help="Defaults to local-runs/records/<run-id>.json")
    args = parser.parse_args()
    record = args.record or ROOT / "local-runs" / "records" / f"{args.run_id}.json"
    try:
        run = prepare(args.task, args.condition, args.run_id, args.dest, record)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(2, f"Preparation failed: {error}\n")
    print(f"Project: {run['project']}")
    print(f"Record: {record.resolve()}")
    print(f"Prompt: {ROOT / 'tasks' / (args.task + '.md')}")
    print("Open the project in a fresh Codex session after verifying the intended configuration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
