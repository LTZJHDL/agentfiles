"""Normalized record values and validation shared by input boundaries."""

from dataclasses import asdict, dataclass
from datetime import date
import re


class InputError(ValueError):
    """An expected input failure suitable for a command-line diagnostic."""


def validate_day(value: str) -> str:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InputError(f"invalid day: {value!r}; expected YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"invalid calendar day: {value!r}") from exc
    return value


@dataclass(frozen=True)
class Record:
    source: str
    external_id: str
    day: str
    category: str
    value: int
    note: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return self.source, self.external_id

    def as_dict(self) -> dict:
        return asdict(self)


def parse_record(fields: dict[str, str]) -> Record:
    normalized = {key: value.strip() for key, value in fields.items()}
    for name in ("source", "external_id", "day", "category", "value"):
        if not normalized.get(name):
            raise InputError(f"missing required value: {name}")
    day = validate_day(normalized["day"])
    raw_value = normalized["value"]
    if not re.fullmatch(r"[+-]?[0-9]+", raw_value):
        raise InputError(f"invalid integer value: {raw_value!r}")
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise InputError("integer value is too long") from exc
    if not -1_000_000_000 <= value <= 1_000_000_000:
        raise InputError("value must be between -1000000000 and 1000000000")
    return Record(
        normalized["source"], normalized["external_id"], day,
        normalized["category"], value, normalized.get("note", ""),
    )
