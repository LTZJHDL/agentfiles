"""Group a filtered current snapshot of observations."""

from collections.abc import Iterable
from pathlib import Path

from . import store
from .model import InputError, Record, validate_day


def validate_range(start: str | None, end: str | None) -> None:
    if start is not None:
        validate_day(start)
    if end is not None:
        validate_day(end)
    if start is not None and end is not None and start > end:
        raise InputError("start day must not be after end day")


def build_report(
    records: Iterable[Record], start: str | None = None,
    end: str | None = None, category: str | None = None,
) -> dict:
    validate_range(start, end)
    groups = {}
    count = 0
    total = 0
    for record in records:
        if start is not None and record.day < start:
            continue
        if end is not None and record.day > end:
            continue
        if category is not None and record.category != category:
            continue
        key = record.day, record.category
        group = groups.setdefault(key, {
            "day": record.day, "category": record.category, "count": 0, "total": 0,
        })
        group["count"] += 1
        group["total"] += record.value
        count += 1
        total += record.value
    return {"count": count, "total": total,
            "groups": [groups[key] for key in sorted(groups)]}


def report_database(
    db_path: str | Path, start: str | None = None,
    end: str | None = None, category: str | None = None,
) -> dict:
    validate_range(start, end)
    records = store.report_records(db_path, start, end, category)
    return build_report(records)
