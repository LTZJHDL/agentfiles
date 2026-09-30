"""Plan normalized rows once, then optionally save their revisions."""

from dataclasses import dataclass, field
from pathlib import Path

from . import store
from .csv_input import ParsedInput, RowError, read_csv
from .model import Record


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


def _plan_import(parsed: ParsedInput, existing: list[Record]) -> tuple[ImportSummary, list[Record]]:
    summary = ImportSummary(errors=parsed.errors)
    current = {record.key: record for record in existing}
    revisions = []
    for record in parsed.records:
        previous = current.get(record.key)
        if previous == record:
            summary.unchanged += 1
            continue
        if previous is None:
            summary.inserted += 1
        else:
            summary.updated += 1
        revisions.append(record)
        current[record.key] = record
    return summary, revisions


def import_csv(csv_path: str | Path, db_path: str | Path, *, dry_run: bool = False) -> ImportSummary:
    parsed = read_csv(csv_path)
    if dry_run:
        summary, _ = _plan_import(parsed, store.read_current(db_path))
        return summary
    with store.connect(db_path) as connection:
        summary, revisions = _plan_import(parsed, store.current_records(connection))
        for record in revisions:
            store.append_revision(connection, record)
    return summary
