import csv
from pathlib import Path
import tempfile
import unittest

from fieldledger import store
from fieldledger.importer import import_csv
from fieldledger.reports import report_database


class ReportRegressionTests(unittest.TestCase):
    def test_shared_ids_and_corrections_preserve_current_view_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "records.sqlite"
            source = root / "data.csv"
            rows = [
                ["north", "shared", "2026-01-10", "rain", 10],
                ["south", "shared", "2026-01-11", "rain", 7],
                ["north", "moving", "2026-01-12", "snow", 5],
                ["east", "fixed", "2026-01-31", "rain", 3],
            ]
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["source", "external_id", "day", "category", "value"])
                writer.writerows(rows)
            import_csv(source, database)
            self.assertEqual(report_database(database)["count"], 4)
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["source", "external_id", "day", "category", "value"])
                writer.writerows([
                    ["north", "moving", "2026-02-02", "sun", 5],
                    ["north", "shared", "2026-01-10", "rain", 14],
                ])
            import_csv(source, database)
            before = database.read_bytes()
            january = report_database(database, "2026-01-01", "2026-01-31")
            self.assertEqual((january["count"], january["total"]), (3, 24))
            self.assertEqual(report_database(database, category="snow")["count"], 0)
            self.assertEqual(report_database(database)["total"], 29)
            self.assertEqual(database.read_bytes(), before)
            self.assertEqual(len(store.read_current(database)), 4)


if __name__ == "__main__":
    unittest.main()
