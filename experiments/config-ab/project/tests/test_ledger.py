import csv
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from fieldledger.csv_input import read_csv
from fieldledger.importer import import_csv
from fieldledger.model import InputError
from fieldledger import store
from fieldledger.reports import report_database


HEADER = ["source", "external_id", "day", "category", "value", "note"]


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "ledger.sqlite"
        self.csv = self.root / "input.csv"

    def write_rows(self, rows, header=HEADER):
        with self.csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        return self.csv

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "fieldledger", "--db", str(self.db), *args],
            capture_output=True, text=True, encoding="utf-8",
            cwd=Path(__file__).resolve().parents[1],
        )

    def test_insert_update_and_unchanged_preserve_history(self):
        self.write_rows([["north", "one", "2026-01-10", "rain", "10", "first"]])
        self.assertEqual(import_csv(self.csv, self.db).inserted, 1)
        self.assertEqual(import_csv(self.csv, self.db).unchanged, 1)
        self.write_rows([["north", "one", "2026-01-10", "rain", "14", "revised"]])
        self.assertEqual(import_csv(self.csv, self.db).updated, 1)
        current = store.read_current(self.db)
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].value, 14)
        self.assertEqual(current[0].note, "revised")
        with store.connect(self.db) as connection:
            self.assertEqual([r.value for r in store.history_records(connection)], [10, 14])
            self.assertEqual(connection.execute(
                "SELECT revision_id FROM revisions ORDER BY revision_id"
            ).fetchall(), [(1,), (2,)])

    def test_repeated_identity_in_one_file_uses_evolving_state(self):
        self.write_rows([
            ["north", "one", "2026-01-10", "rain", "10", ""],
            ["north", "one", "2026-01-10", "rain", "14", ""],
            ["north", "one", "2026-01-10", "rain", "14", ""],
        ])
        self.assertEqual(import_csv(self.csv, self.db).as_dict(), {
            "inserted": 1, "updated": 1, "unchanged": 1, "invalid": 0, "errors": [],
        })
        self.assertEqual(store.read_current(self.db)[0].value, 14)

    def test_normalization_bom_optional_note_and_extra_column(self):
        self.csv.write_text(
            "\ufeffsource,external_id,day,category,value,ignored\n"
            " 北方 , station:一 , 2026-01-10 , rain , +0010 ,extra\n",
            encoding="utf-8",
        )
        summary = import_csv(self.csv, self.db)
        self.assertEqual(summary.inserted, 1)
        self.assertEqual(store.read_current(self.db)[0].as_dict(), {
            "source": "北方", "external_id": "station:一", "day": "2026-01-10",
            "category": "rain", "value": 10, "note": "",
        })

    def test_invalid_rows_are_diagnosed_and_valid_rows_commit(self):
        self.write_rows([
            ["north", "valid", "2026-01-10", "rain", "-2", ""],
            ["", "missing", "2026-01-10", "rain", "1", ""],
            ["north", "bad-day", "2026-02-30", "rain", "1", ""],
            ["north", "bad-value", "2026-01-10", "rain", "1.5", ""],
            ["north", "overflow", "2026-01-10", "rain", "1000000001", ""],
            ["north", "extra", "2026-01-10", "rain", "1", "", "extra"],
            ["north", "short"],
        ])
        result = self.cli("import", str(self.csv), "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["inserted"], 1)
        self.assertEqual(summary["invalid"], 6)
        self.assertEqual([error["row"] for error in summary["errors"]], list(range(3, 9)))
        self.assertTrue(all(error["message"] for error in summary["errors"]))
        self.assertEqual(len(store.read_current(self.db)), 1)

    def test_diagnostic_row_number_counts_records_not_physical_lines(self):
        self.write_rows([
            ["north", "one", "2026-01-10", "rain", "1", "two\nlines"],
            ["north", "two", "not-a-date", "rain", "1", ""],
        ])
        parsed = read_csv(self.csv)
        self.assertEqual(parsed.errors[0].row, 3)
        self.assertEqual(parsed.records[0].note, "two\nlines")

    def test_whole_input_errors_do_not_create_database(self):
        inputs = [
            "source,external_id\nnorth,one\n",
            "source,external_id,day,category,value,value\n",
            "source,external_id,day,category,value,\n",
        ]
        for content in inputs:
            with self.subTest(content=content):
                self.csv.write_text(content, encoding="utf-8")
                result = self.cli("import", str(self.csv), "--json")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.strip())
                self.assertFalse(self.db.exists())
        result = self.cli("import", str(self.root / "missing.csv"), "--json")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.db.exists())

    def test_whole_input_error_preserves_existing_database_bytes(self):
        self.write_rows([["north", "one", "2026-01-10", "rain", "10", ""]])
        import_csv(self.csv, self.db)
        before = self.db.read_bytes()
        self.csv.write_bytes(b"source,external_id,day,category,value\n\xff")
        with self.assertRaises(InputError):
            import_csv(self.csv, self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_valid_rows_roll_back_together_on_database_failure(self):
        with store.connect(self.db) as connection:
            connection.execute("""
                CREATE TRIGGER reject_stop BEFORE INSERT ON revisions
                WHEN NEW.external_id = 'stop'
                BEGIN SELECT RAISE(ABORT, 'rejected for test'); END
            """)
        self.write_rows([
            ["north", "first", "2026-01-10", "rain", "1", ""],
            ["north", "stop", "2026-01-10", "rain", "2", ""],
        ])
        with self.assertRaises(sqlite3.IntegrityError):
            import_csv(self.csv, self.db)
        self.assertEqual(store.read_current(self.db), [])

    def test_list_json_sorted_and_has_exact_fields(self):
        self.write_rows([
            ["west", "z", "2026-01-11", "snow", "3", ""],
            ["north", "b", "2026-01-10", "rain", "2", ""],
            ["north", "a", "2026-01-10", "rain", "1", ""],
        ])
        import_csv(self.csv, self.db)
        result = self.cli("list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertEqual([(r["source"], r["external_id"]) for r in records],
                         [("north", "a"), ("north", "b"), ("west", "z")])
        self.assertTrue(all(set(record) == set(HEADER) for record in records))

    def test_reports_group_and_filter_with_inclusive_bounds(self):
        self.write_rows([
            ["north", "one", "2026-01-01", "rain", "10", ""],
            ["north", "two", "2026-01-31", "rain", "7", ""],
            ["north", "three", "2026-01-31", "rain", "-2", ""],
            ["north", "four", "2026-01-15", "snow", "5", ""],
            ["north", "five", "2026-02-01", "rain", "20", ""],
        ])
        import_csv(self.csv, self.db)
        result = self.cli("report", "--from", "2026-01-01", "--to", "2026-01-31",
                          "--category", "rain", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "count": 3, "total": 15, "groups": [
                {"day": "2026-01-01", "category": "rain", "count": 1, "total": 10},
                {"day": "2026-01-31", "category": "rain", "count": 2, "total": 5},
            ],
        })
        self.assertEqual(report_database(self.db, start="2026-02-01")["total"], 20)
        self.assertEqual(report_database(self.db, end="2026-01-01")["count"], 1)
        self.assertEqual(report_database(self.db, category="RAIN")["count"], 0)

    def test_report_uses_corrected_value_once(self):
        self.write_rows([["north", "one", "2026-01-10", "rain", "10", ""]])
        import_csv(self.csv, self.db)
        self.write_rows([["north", "one", "2026-01-10", "rain", "14", ""]])
        import_csv(self.csv, self.db)
        self.assertEqual(report_database(self.db)["count"], 1)
        self.assertEqual(report_database(self.db)["total"], 14)

    def test_missing_database_queries_are_empty_and_do_not_create_file(self):
        listing = self.cli("list", "--json")
        report = self.cli("report", "--json")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertEqual(json.loads(listing.stdout), [])
        self.assertEqual(json.loads(report.stdout), {"count": 0, "total": 0, "groups": []})
        self.assertFalse(self.db.exists())

    def test_invalid_filter_returns_exit_two(self):
        for args in [
            ["--from", "2026-1-01"], ["--to", "2026-02-30"],
            ["--from", "2026-02-01", "--to", "2026-01-01"],
        ]:
            with self.subTest(args=args):
                result = self.cli("report", *args, "--json")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.strip())
        self.assertFalse(self.db.exists())

    def test_human_output_contains_summary_and_row_diagnostic(self):
        self.write_rows([
            ["north", "one", "2026-01-10", "rain", "10", ""],
            ["north", "bad", "2026-01-10", "rain", "oops", ""],
        ])
        result = self.cli("import", str(self.csv))
        self.assertEqual(result.returncode, 1)
        self.assertIn("inserted=1", result.stdout)
        self.assertIn("invalid=1", result.stdout)
        self.assertIn("row 3:", result.stderr)
        self.assertIn("north\tone", self.cli("list").stdout)
        self.assertIn("count=1 total=10", self.cli("report").stdout)


if __name__ == "__main__":
    unittest.main()
