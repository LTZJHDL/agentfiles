"""Acceptance checks for non-mutating, sequential import previews."""

import sqlite3
from contextlib import closing

from .common import ProjectCase, database_snapshot, record


class PreviewAcceptance(ProjectCase):
    def preview(self, path, code=0, db=None):
        before_files = self.filesystem_snapshot()
        target = db or self.db
        before_database = database_snapshot(target)
        result = self.cli("import", path, "--dry-run", code=code, db=target)
        self.assertIs(result.get("dry_run"), True)
        self.assertEqual(database_snapshot(target), before_database)
        self.assertEqual(self.filesystem_snapshot(), before_files)
        return result

    def assert_matches_import(self, path, code=0):
        preview = self.preview(path, code=code)
        actual = self.cli("import", path, code=code)
        for field in ("inserted", "updated", "unchanged", "invalid", "errors"):
            self.assertEqual(preview[field], actual[field], field)
        return preview

    def test_preview_empty_database_does_not_create_it(self):
        path = self.csv_file([record("station", "1", "2026-01-01", "rain", 4)])
        result = self.preview(path)
        self.assertEqual([result[k] for k in ("inserted", "updated", "unchanged", "invalid")],
                         [1, 0, 0, 0])
        self.assertFalse(self.db.exists())
        self.assert_matches_import(path)

    def test_preview_missing_parent_stays_missing(self):
        target = self.root / "not-created" / "nested" / "ledger.sqlite"
        path = self.csv_file([record("s", "x", "2026-01-01", "a", 1)])
        result = self.preview(path, db=target)
        self.assertEqual(result["inserted"], 1)
        self.assertFalse(target.parent.parent.exists())

    def test_sequential_duplicates_use_tuple_identity_and_normalized_fields(self):
        original = record("a", "b|c", "2026-01-01", "rain", 4)
        changed = record("a", "b|c", "2026-02-01", "sun", -2, "changed")
        self.import_rows([original])
        path = self.csv_file([
            original, changed, changed,
            record("a|b", "c", "2026-01-02", "rain", 9),
            record("other", "b|c", "2026-01-03", "rain", 7),
            record("  气象站  ", " 编号:一 ", "2026-01-04", " 雨 ", 2, " 注释 "),
            record("气象站", "编号:一", "2026-01-04", "雨", 2, "注释"),
            record("s", "bad", "2026-02-30", "rain", 1),
        ])
        result = self.assert_matches_import(path, code=1)
        self.assertEqual([result[k] for k in ("inserted", "updated", "unchanged", "invalid")],
                         [3, 1, 3, 1])
        self.assertEqual([e["row"] for e in result["errors"]], [9])
        self.assertTrue(result["errors"][0]["message"])
        self.assert_records([changed, record("a|b", "c", "2026-01-02", "rain", 9),
                             record("other", "b|c", "2026-01-03", "rain", 7),
                             record("气象站", "编号:一", "2026-01-04", "雨", 2, "注释")])

    def test_preview_preserves_history_and_unchanged_import_adds_no_revision(self):
        old = record("s", "x", "2026-01-01", "rain", 1)
        current = record("s", "x", "2026-02-01", "sun", 2)
        self.import_rows([old, current])
        snapshot = database_snapshot(self.db)
        path = self.csv_file([current, current])
        result = self.assert_matches_import(path)
        self.assertEqual(result["unchanged"], 2)
        self.assertEqual(database_snapshot(self.db), snapshot)

    def test_preview_reads_existing_database_without_acquiring_write_transaction(self):
        self.import_rows([record("s", "x", "2026-01-01", "rain", 1)])
        path = self.csv_file([record("s", "x", "2026-02-01", "rain", 2)])
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                result = self.preview(path)
                self.assertEqual(result["updated"], 1)
            finally:
                connection.rollback()

    def test_invalid_rows_preserve_csv_record_numbers_and_exit_one(self):
        path = self.csv_file([
            record("s", "ok", "2026-01-01", "rain", 2, "two\nlines"),
            record("s", "bad", "2026-1-02", "rain", 2),
            record("s", "bad2", "2026-01-02", "rain", "1.5"),
            ["s", "extra", "2026-01-02", "rain", 2, "", "surplus"],
            record("s", "bad3", "2026-01-02", "rain", 1000000001),
        ])
        result = self.assert_matches_import(path, code=1)
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["invalid"], 4)
        self.assertEqual([e["row"] for e in result["errors"]], [3, 4, 5, 6])
        self.assertTrue(all(e["message"] for e in result["errors"]))

    def test_invalid_only_preview_does_not_create_missing_parent(self):
        target = self.root / "missing" / "ledger.sqlite"
        path = self.csv_file([record("", "x", "2026-01-01", "rain", 2)])
        result = self.preview(path, code=1, db=target)
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["inserted"], 0)

    def test_whole_input_errors_leave_existing_and_absent_databases_untouched(self):
        self.import_rows([record("s", "x", "2026-01-01", "rain", 1)])
        paths = [self.csv_file([], fields=("source", "day")),
                 self.csv_file([], fields=("source", "external_id", "day", "category", "value", "source")),
                 self.root / "unreadable-does-not-exist.csv"]
        for target in (self.db, self.root / "missing" / "ledger.sqlite"):
            for path in paths:
                with self.subTest(target=target, path=path):
                    before = self.filesystem_snapshot()
                    snapshot = database_snapshot(target)
                    result = self.cli("import", path, "--dry-run", code=2, db=target)
                    self.assertTrue(result.stderr.strip())
                    self.assertEqual(database_snapshot(target), snapshot)
                    self.assertEqual(self.filesystem_snapshot(), before)

    def test_help_advertises_preview_and_plain_output_is_available(self):
        help_result = self.cli("import", "--help", json_output=False)
        self.assertIn("--dry-run", help_result.stdout)
        path = self.csv_file([record("s", "x", "2026-01-01", "rain", 1)])
        before = self.filesystem_snapshot()
        result = self.cli("import", path, "--dry-run", json_output=False)
        self.assertTrue(result.stdout.strip())
        self.assertEqual(self.filesystem_snapshot(), before)
        # Human grading assesses whether the prose explains preview and saving.
