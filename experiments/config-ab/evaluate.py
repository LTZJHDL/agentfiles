"""Evaluate a finished workspace without changing its source or accepting its self-report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import io
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import zipfile

from benchlib import ROOT, TASKS, digest_files, git, read_json, write_json_new


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []
        self.started = {}

    def startTest(self, test):
        self.started[test.id()] = time.monotonic()
        super().startTest(test)

    def add_record(self, test, status, detail=None):
        self.cases.append({"test": test.id(), "status": status, "seconds": round(time.monotonic() - self.started.get(test.id(), time.monotonic()), 3), "detail": detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.add_record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.add_record(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.add_record(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.add_record(test, "skipped", reason)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "failed" if issubclass(err[0], test.failureException) else "error"
            existing = next((case for case in self.cases if case["test"] == test.id()), None)
            detail = f"{subtest}:\n{self._exc_info_to_string(err, test)}"
            if existing:
                existing["detail"] += "\n" + detail
                if status == "error":
                    existing["status"] = "error"
            else:
                self.add_record(test, status, detail)


def evaluate(task: str, project: Path, python: str, output: Path) -> dict:
    project = project.resolve()
    output = output.resolve()
    if output.suffix != ".json":
        raise ValueError("Evaluation output must end in .json")
    if not (project / "fieldledger").is_dir():
        raise ValueError(f"Not a Field Ledger project: {project}")
    if output.is_relative_to(project):
        raise ValueError("Save evaluation output outside the tested project")
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    for suffix in (".patch", ".zip"):
        if output.with_suffix(suffix).exists():
            raise ValueError(f"Artifact already exists: {output.with_suffix(suffix)}")

    freeze = read_json(ROOT / "freeze.json")
    evaluator_files = [ROOT / name for name in freeze["evaluator_files"]]
    evaluator_digest = digest_files({path.relative_to(ROOT).as_posix(): path.read_bytes() for path in evaluator_files})
    if evaluator_digest != freeze["evaluator_sha256"]:
        raise ValueError("Evaluator changed since freeze.json; version and recalibrate before comparing runs")

    from evaluation import common
    common.configure(project, python)
    started = time.monotonic()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName(f"evaluation.test_{task}")
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        existing = subprocess.run([python, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=project, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        existing_checks = {"returncode": existing.returncode, "stdout": existing.stdout, "stderr": existing.stderr, "timeout": False}
    except subprocess.TimeoutExpired as error:
        existing_checks = {"returncode": None, "stdout": str(error.stdout or ""), "stderr": str(error.stderr or ""), "timeout": True}

    names = set(git(project, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")) - {""}
    files = {name: (project / name).read_bytes() for name in names if (project / name).is_file()}
    report = {
        "schema_version": 1,
        "experiment_version": freeze["experiment_version"],
        "evaluator_sha256": evaluator_digest,
        "task": task,
        "project": str(project),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_seconds": round(time.monotonic() - started, 3),
        "head_commit": git(project, "rev-parse", "HEAD"),
        "git_status": git(project, "status", "--short"),
        "evaluated_source_sha256": digest_files(files),
        "source_archive": output.with_suffix(".zip").name,
        "acceptance": {"passed": result.wasSuccessful() and not result.skipped and result.testsRun > 0, "tests_run": result.testsRun, "cases": result.cases, "log": stream.getvalue()},
        "project_tests": existing_checks,
        "automated_pass": result.wasSuccessful() and not result.skipped and result.testsRun > 0 and existing_checks["returncode"] == 0,
        "human_review": "Pending: documentation, design, explanation and user experience are not graded by these checks.",
    }
    # Every prepared project has one root commit. Include committed changes as
    # well as working-tree edits; untracked files remain identified in status.
    roots = git(project, "rev-list", "--max-parents=0", "HEAD").splitlines()
    patch = git(project, "diff", "--binary", roots[0], "--", strip=False)
    write_json_new(output, report)
    with output.with_suffix(".patch").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(patch)
    with zipfile.ZipFile(output.with_suffix(".zip"), "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable, help="Python used for the tested project")
    args = parser.parse_args()
    try:
        report = evaluate(args.task, args.project, args.python, args.output)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Evaluation failed: {error}\n")
    print(f"Acceptance: {sum(case['status'] == 'passed' for case in report['acceptance']['cases'])}/{report['acceptance']['tests_run']}")
    print(f"Project tests exit code: {report['project_tests']['returncode']}")
    print(f"Report: {args.output.resolve()}")
    print("Human review is still required; this is not an overall quality score.")
    return 0 if report["automated_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
