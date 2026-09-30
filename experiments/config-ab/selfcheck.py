"""Calibrate the fixtures and acceptance checks; this does not run Codex."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

from benchlib import ROOT, git, read_json
from evaluate import RecordedResult, evaluate
from prepare import prepare


def apply_overlay(project: Path, overlay: Path) -> None:
    for source in overlay.rglob("*"):
        if source.is_file() and "__pycache__" not in source.parts:
            destination = project / source.relative_to(overlay)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)


def check(output: Path) -> dict:
    scratch_root = (ROOT / ".scratch").resolve()
    scratch_root.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="selfcheck-", dir=scratch_root)).resolve()
    # Keep calibration workspaces and reports for inspection; no recursive
    # deletion or reset is needed by this script.
    assert scratch.is_relative_to(scratch_root)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    class SubtestAccounting(unittest.TestCase):
        def runTest(self):
            with self.subTest("assertion"):
                self.fail("an unmet requirement")
            with self.subTest("exception"):
                raise ValueError("a harness error")

    accounting = unittest.TextTestRunner(stream=io.StringIO(), resultclass=RecordedResult).run(SubtestAccounting())
    assert len(accounting.failures) == 1 and len(accounting.errors) == 1
    assert len(accounting.cases) == 1 and accounting.cases[0]["status"] == "error"
    cases = []
    reports = {}
    for name, task, variant, expected in (
        ("feature-start", "feature", None, False),
        ("feature-reference", "feature", "reference", True),
        ("bug-start", "bug", None, False),
        ("bug-reference", "bug", "reference", True),
        ("bug-identity-only", "bug", "identity-only", False),
        ("bug-filter-order-only", "bug", "filter-order-only", False),
    ):
        project = scratch / name
        prepare(task, "A", name, project, scratch / "records" / f"{name}.json")
        if variant == "reference":
            apply_overlay(project, ROOT / "evaluation" / "reference" / task)
        elif variant == "identity-only":
            path = project / "fieldledger" / "store.py"
            path.write_text(path.read_text(encoding="utf-8").replace("GROUP BY external_id", "GROUP BY source, external_id"), encoding="utf-8")
        elif variant == "filter-order-only":
            path = project / "fieldledger" / "reports.py"
            text = path.read_text(encoding="utf-8").replace("store.report_records(db_path, start, end, category)", "store.report_records(db_path)")
            path.write_text(text.replace("return build_report(records)\n", "return build_report(records, start, end, category)\n"), encoding="utf-8")
        before = git(project, "status", "--porcelain")
        report = evaluate(task, project, sys.executable, scratch / "results" / f"{name}.json")
        patch = scratch / "results" / f"{name}.patch"
        if patch.stat().st_size:
            git(project, "apply", "--stat", str(patch))
        reports[name] = report
        assert report["automated_pass"] == expected, f"Unexpected acceptance result: {name}"
        assert report["project_tests"]["returncode"] == 0, f"Existing tests failed: {name}"
        assert not any(case["status"] in {"error", "skipped"} for case in report["acceptance"]["cases"]), f"Harness error or skip: {name}"
        assert git(project, "status", "--porcelain") == before, f"Evaluation modified project files: {name}"
        entry = {"case": name, "expected_automated_pass": expected,
                 "automated_pass": report["automated_pass"],
                 "acceptance_passed": sum(case["status"] == "passed" for case in report["acceptance"]["cases"]),
                 "acceptance_total": report["acceptance"]["tests_run"],
                 "project_tests_returncode": report["project_tests"]["returncode"]}
        cases.append(entry)
        print(f"{name}: {entry['acceptance_passed']}/{entry['acceptance_total']}, project tests passed", flush=True)

    # Partial repairs must pass their targeted check, not fail merely because
    # the calibration mutation broke the CLI or all reports.
    def passed(case_name: str, method: str) -> bool:
        return any(case["test"].endswith("." + method) and case["status"] == "passed"
                   for case in reports[case_name]["acceptance"]["cases"])
    assert passed("bug-identity-only", "test_same_external_id_in_different_sources_remains_two_records")
    assert passed("bug-filter-order-only", "test_latest_revision_is_chosen_before_date_range_filter")

    # Exercise both configuration paths and freeze checks without changing live settings.
    paired = scratch / "paired-B"
    prepare("feature", "B", "paired-B", paired, scratch / "records" / "paired-B.json")
    assert git(paired, "rev-parse", "HEAD^{tree}") == git(scratch / "feature-start", "rev-parse", "HEAD^{tree}")
    paths = {path.relative_to(paired).as_posix() for path in paired.rglob("*") if path.is_file() and ".git" not in path.parts}
    assert not any(path.startswith(("evaluation/", "configs/", "tasks/")) or path.endswith("AGENTS.md") for path in paths)
    try:
        prepare("feature", "B", "paired-B-again", paired, scratch / "records" / "again.json")
    except ValueError:
        pass
    else:
        raise AssertionError("Existing workspace was overwritten")
    assert git(paired, "status", "--porcelain") == ""
    with zipfile.ZipFile(scratch / "results" / "feature-reference.zip") as archive:
        assert "tests/test_dry_run.py" in archive.namelist(), "Untracked candidate source was omitted"

    summary = {
        "experiment_version": read_json(ROOT / "freeze.json")["experiment_version"],
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "purpose": "Fixture and evaluator calibration only; no Codex A/B runs were performed.",
        "cases": cases,
        "checks": {"same_task_A_B_source_trees_match": True, "workspaces_exclude_experiment_materials": True,
                   "existing_workspace_refused": True, "evaluation_preserves_git_status": True,
                   "partial_repairs_rejected_without_harness_errors": True,
                   "subtest_errors_distinguished_from_assertion_failures": True,
                   "untracked_candidate_sources_archived": True,
                   "nonempty_saved_patches_parse_with_git": True},
        "detail_directory": str(scratch.relative_to(ROOT)),
        "limitations": ["Synthetic, small pilot project; no evidence yet about delegation behavior or real task cost.",
                        "Reference implementations are calibration examples, not unique design requirements."]
    }
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "validation.json")
    arguments = parser.parse_args()
    check(arguments.output)
    print(f"Calibration saved: {arguments.output}")
