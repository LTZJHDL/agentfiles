"""Read the complete input before opening a writable database."""

import csv
from dataclasses import dataclass
from pathlib import Path

from .model import InputError, Record, parse_record


REQUIRED_COLUMNS = {"source", "external_id", "day", "category", "value"}


@dataclass(frozen=True)
class RowError:
    row: int
    message: str

    def as_dict(self) -> dict:
        return {"row": self.row, "message": self.message}


@dataclass
class ParsedInput:
    records: list[Record]
    errors: list[RowError]


def read_csv(path: str | Path) -> ParsedInput:
    records = []
    errors = []
    try:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, [])
            if len(header) != len(set(header)):
                raise InputError("duplicate CSV column names")
            if any(not column for column in header):
                raise InputError("CSV columns must have names")
            missing = REQUIRED_COLUMNS - set(header)
            if missing:
                raise InputError("missing CSV columns: " + ", ".join(sorted(missing)))
            for row_number, cells in enumerate(reader, start=2):
                if len(cells) > len(header):
                    errors.append(RowError(row_number, "more fields than CSV header"))
                    continue
                fields = dict(zip(header, cells))
                try:
                    records.append(parse_record(fields))
                except InputError as exc:
                    errors.append(RowError(row_number, str(exc)))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise InputError(f"cannot read CSV {str(path)!r}: {exc}") from exc
    return ParsedInput(records, errors)
