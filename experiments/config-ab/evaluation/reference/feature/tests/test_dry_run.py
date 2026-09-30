"""Preview parity and absence of database writes through public entry points."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fieldledger import cli, store
from fieldledger.importer import import_csv
from fieldledger.model import InputError


class DryRunTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.csv = self.root / "input.csv"
        self.db = self.root / "observations.sqlite"

    def write_rows(self, rows):
        self.csv.write_text("source,external_id,day,category,value,note\n" + rows,
                            encoding="utf-8")

    def test_existing_database_parity_and_revision_history(self):
        self.write_rows("a,1,2026-01-01,rain,5,\n")
        import_csv(self.csv, self.db)
        before = self.db.read_bytes()
        self.write_rows("a,1,2026-01-01,rain,5,\n"
                        "a,1,2026-01-02,snow,7,\n"
                        "b,1,2026-01-01,rain,3,\n"
                        "b,1,2026-01-01,rain,3,\n"
                        "a,1,2026-01-01,rain,5,\n"
                        "a,1,not-a-date,rain,5,\n")
        with patch.object(store, "connect", side_effect=AssertionError("writable open")), \
                patch.object(store, "append_revision", side_effect=AssertionError("write")):
            preview = import_csv(self.csv, self.db, dry_run=True)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual((preview.inserted, preview.updated, preview.unchanged, preview.invalid),
                         (1, 2, 2, 1))
        self.assertEqual(preview.errors[0].row, 7)
        self.assertEqual(preview.as_dict(), import_csv(self.csv, self.db).as_dict())
        with store.connect(self.db) as connection:
            self.assertEqual(len(store.history_records(connection)), 4)

    def test_missing_parent_stays_missing(self):
        db = self.root / "missing" / "db.sqlite"
        self.write_rows("a,1,2026-01-01,rain,5,\n")
        self.assertEqual(import_csv(self.csv, db, dry_run=True).inserted, 1)
        self.assertFalse(db.parent.exists())
        self.csv.write_text("wrong,header\n", encoding="utf-8")
        with self.assertRaises(InputError):
            import_csv(self.csv, db, dry_run=True)
        self.assertFalse(db.parent.exists())

    def test_cli_json_and_human_preview(self):
        self.write_rows("a,1,2026-01-01,rain,5,\n")
        argv = ["--db", str(self.db), "import", str(self.csv), "--dry-run"]
        output = io.StringIO()
        with redirect_stdout(output):
            status = cli.main(argv + ["--json"])
        self.assertEqual(status, 0)
        self.assertIs(json.loads(output.getvalue())["dry_run"], True)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli.main(argv), 0)
        self.assertIn("no changes saved", output.getvalue())
        self.assertIn("without --dry-run", output.getvalue())
        self.assertFalse(self.db.exists())


if __name__ == "__main__":
    unittest.main()
