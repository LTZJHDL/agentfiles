"""Regression checks deriving statistics from independently specified current rows."""

from .common import ProjectCase, database_snapshot, record


class ReportAcceptance(ProjectCase):
    def seed_corrections(self):
        initial = [
            record("north", "shared", "2026-01-01", "rain", 10),
            record("south", "shared", "2026-01-31", "rain", 7),
            record("north", "enter", "2025-12-31", "snow", 3),
            record("north", "leave", "2026-01-15", "rain", 4),
            record("north", "steady", "2026-01-01", "rain", 4),
        ]
        current = [
            record("north", "shared", "2026-02-01", "sun", 20),
            record("south", "shared", "2026-01-15", "snow", 8),
            record("north", "enter", "2026-01-31", "rain", 12),
            record("north", "leave", "2025-12-31", "rain", 9),
            initial[-1],
        ]
        self.import_rows(initial)
        self.import_rows(current[:-1])
        return current

    def test_same_external_id_in_different_sources_remains_two_records(self):
        rows = [record("north", "same", "2026-01-01", "rain", 10),
                record("south", "same", "2026-01-01", "rain", 7)]
        self.import_rows(rows)
        self.assert_records(rows)
        result = self.assert_report(rows)
        self.assertEqual((result["count"], result["total"]), (2, 17))

    def test_latest_revision_is_chosen_before_date_range_filter(self):
        current = self.seed_corrections()
        self.assert_records(current)
        result = self.assert_report(current, "2026-01-01", "2026-01-31")
        self.assertEqual((result["count"], result["total"]), (3, 24))

    def test_latest_revision_is_chosen_before_category_filter(self):
        current = self.seed_corrections()
        for category in ("rain", "snow", "sun", "Rain", "missing"):
            with self.subTest(category=category):
                self.assert_report(current, category=category)
                self.assert_report(current, "2026-01-01", "2026-01-31", category)

    def test_date_endpoints_are_inclusive_and_one_sided_ranges_work(self):
        current = self.seed_corrections()
        for start, end in [("2026-01-01", "2026-01-01"),
                           ("2026-01-31", "2026-01-31"),
                           (None, "2026-01-01"), ("2026-01-31", None),
                           ("2026-03-01", None), (None, "2025-01-01")]:
            with self.subTest(start=start, end=end):
                self.assert_report(current, start, end)

    def test_unbounded_report_matches_list_and_does_not_change_history(self):
        current = self.seed_corrections()
        before = database_snapshot(self.db)
        self.assert_records(current)
        result = self.assert_report(current)
        self.assertEqual((result["count"], result["total"]), (5, 53))
        self.assert_report(current, "2026-01-01", "2026-01-31", "rain")
        self.assertEqual(database_snapshot(self.db), before)

    def test_repeated_revisions_follow_import_order_not_observation_day(self):
        old = record("s", "repeated", "2026-06-01", "rain", 99)
        middle = record("s", "repeated", "2026-03-01", "sun", 8)
        latest = record("s", "repeated", "2026-01-01", "snow", -3, "last")
        other = record("other", "repeated", "2026-01-01", "snow", 5)
        summary = self.import_rows([old, middle, middle, other, latest, latest])
        self.assertEqual([summary[k] for k in ("inserted", "updated", "unchanged", "invalid")],
                         [2, 2, 2, 0])
        self.assert_records([latest, other])
        self.assert_report([latest, other])
        self.assert_report([latest, other], "2026-01-01", "2026-01-01", "snow")
        self.assert_report([latest, other], "2026-03-01", "2026-06-01")

    def test_unicode_and_delimiter_identities_are_not_concatenated(self):
        rows = [record("a|b", "c", "2026-01-01", "雨", 2),
                record("a", "b|c", "2026-01-01", "雨", 3),
                record("站:一", "二", "2026-01-01", "雨", 5),
                record("站", "一:二", "2026-01-01", "雨", 7),
                record("A", "b|c", "2026-01-01", "雨", 11)]
        self.import_rows(rows)
        self.assert_records(rows)
        result = self.assert_report(rows, category="雨")
        self.assertEqual((result["count"], result["total"]), (5, 28))

    def test_empty_and_invalid_ranges_preserve_database(self):
        self.assertEqual(self.cli("report"), {"count": 0, "total": 0, "groups": []})
        self.assertFalse(self.db.exists())
        current = self.seed_corrections()
        before = database_snapshot(self.db)
        self.assert_report(current, "2027-01-01", "2027-12-31")
        for arguments in (("--from", "2026-02-30"), ("--to", "2026-1-01"),
                          ("--from", "2026-02-01", "--to", "2026-01-01")):
            with self.subTest(arguments=arguments):
                result = self.cli("report", *arguments, code=2)
                self.assertTrue(result.stderr.strip())
        self.assertEqual(database_snapshot(self.db), before)
