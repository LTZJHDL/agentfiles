"""Apply normalized rows in file order against the evolving current state."""

from dataclasses import dataclass, field
from pathlib import Path

from . import store
from .csv_input import RowError, read_csv


@dataclass
class ImportSummary:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    errors: list[RowError] = field(default_factory=list)

    @property
    def invalid(self) -> int:
        return len(self.errors)

    def as_dict(self) -> dict:
        return {
            "inserted": self.inserted,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "invalid": self.invalid,
            "errors": [error.as_dict() for error in self.errors],
        }


def import_csv(csv_path: str | Path, db_path: str | Path) -> ImportSummary:
    parsed = read_csv(csv_path)
    summary = ImportSummary(errors=parsed.errors)
    with store.connect(db_path) as connection:
        current = {record.key: record for record in store.current_records(connection)}
        for record in parsed.records:
            previous = current.get(record.key)
            if previous == record:
                summary.unchanged += 1
                continue
            store.append_revision(connection, record)
            if previous is None:
                summary.inserted += 1
            else:
                summary.updated += 1
            current[record.key] = record
    return summary
