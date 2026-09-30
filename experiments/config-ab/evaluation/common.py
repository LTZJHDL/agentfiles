"""Exercise the public CLI without importing the implementation under test."""

import csv
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1] / "project"
PYTHON = sys.executable
FIELDS = ("source", "external_id", "day", "category", "value", "note")


def configure(project: Path, python: str) -> None:
    global PROJECT, PYTHON
    PROJECT, PYTHON = Path(project).resolve(), python


def record(source, external_id, day, category, value, note=""):
    return dict(zip(FIELDS, (source, external_id, day, category, value, note)))


def expected_report(records, start=None, end=None, category=None):
    selected = [r for r in records if
                (start is None or r["day"] >= start) and
                (end is None or r["day"] <= end) and
                (category is None or r["category"] == category)]
    groups = {}
    for row in selected:
        key = row["day"], row["category"]
        group = groups.setdefault(key, {"day": key[0], "category": key[1],
                                        "count": 0, "total": 0})
        group["count"] += 1
        group["total"] += row["value"]
    return {"count": len(selected), "total": sum(r["value"] for r in selected),
            "groups": [groups[key] for key in sorted(groups)]}


def database_snapshot(path):
    if not path.exists():
        return None
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
        schema = connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
        contents = {}
        for kind, name, _, _ in schema:
            if kind == "table":
                quoted = '"' + name.replace('"', '""') + '"'
                contents[name] = sorted(connection.execute("SELECT * FROM " + quoted).fetchall(),
                                        key=repr)
        return schema, contents


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fieldledger-acceptance-")
        self.root = Path(self.temporary.name).resolve()
        self.db = self.root / "ledger.sqlite"
        self.file_counter = 0

    def tearDown(self):
        self.temporary.cleanup()

    def csv_file(self, rows, fields=FIELDS):
        self.file_counter += 1
        path = self.root / ("input-%d.csv" % self.file_counter)
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            for row in rows:
                writer.writerow([row.get(field, "") for field in fields]
                                if isinstance(row, dict) else row)
        return path

    def cli(self, *arguments, code=0, json_output=True, db=None):
        command = [PYTHON, "-m", "fieldledger", "--db", str(db or self.db),
                   *map(str, arguments)]
        if json_output:
            command.append("--json")
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(command, cwd=PROJECT, env=environment,
                                capture_output=True, text=True, encoding="utf-8",
                                timeout=15)
        self.assertEqual(result.returncode, code,
                         f"{command}\nstdout: {result.stdout}\nstderr: {result.stderr}")
        if not json_output or code == 2:
            return result
        try:
            return json.loads(result.stdout)
        except ValueError as error:
            self.fail(f"CLI stdout is not one JSON value: {result.stdout!r}: {error}")

    def import_rows(self, rows):
        return self.cli("import", self.csv_file(rows))

    def assert_records(self, records):
        self.assertEqual(self.cli("list"), sorted(records, key=lambda r: (r["source"], r["external_id"])))

    def filesystem_snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() if path.is_file() else None
                for path in self.root.rglob("*")}

    def assert_report(self, records, start=None, end=None, category=None):
        arguments = ["report"]
        for option, value in (("--from", start), ("--to", end), ("--category", category)):
            if value is not None:
                arguments.extend((option, value))
        actual = self.cli(*arguments)
        self.assertEqual(actual, expected_report(records, start, end, category))
        return actual
