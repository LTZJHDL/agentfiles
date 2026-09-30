"""Command parsing, output formatting, and exit status mapping."""

import argparse
import json
import sqlite3
import sys

from . import store
from .importer import import_csv
from .model import InputError
from .reports import report_database


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Import and summarize field observations")
    root.add_argument("--db", default="observations.sqlite", help="SQLite database path")
    commands = root.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("import", help="Import observation revisions from CSV")
    ingest.add_argument("csv_path")
    ingest.add_argument("--dry-run", action="store_true",
                        help="Preview without saving; omit --dry-run to import")
    listing = commands.add_parser("list", help="List current observations")
    report = commands.add_parser("report", help="Summarize current observations")
    report.add_argument("--from", dest="start")
    report.add_argument("--to", dest="end")
    report.add_argument("--category")
    for command in (ingest, listing, report):
        command.add_argument("--json", action="store_true", help="Output one JSON value")
    return root


def print_result(command: str, result: dict | list, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    elif command == "import":
        if result.get("dry_run"):
            print("Preview only: no changes saved. Run the same command without --dry-run to import.")
        print(" ".join(f"{key}={result[key]}" for key in
                       ("inserted", "updated", "unchanged", "invalid")))
        for error in result["errors"]:
            print(f"row {error['row']}: {error['message']}", file=sys.stderr)
    elif command == "list":
        for record in result:
            print("\t".join(str(record[key]) for key in
                            ("source", "external_id", "day", "category", "value", "note")))
    else:
        print(f"count={result['count']} total={result['total']}")
        for group in result["groups"]:
            print(f"{group['day']}\t{group['category']}\t"
                  f"count={group['count']}\ttotal={group['total']}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        status = 0
        if args.command == "import":
            summary = import_csv(args.csv_path, args.db, dry_run=args.dry_run)
            result = summary.as_dict()
            if args.dry_run:
                result["dry_run"] = True
            status = 1 if summary.invalid else 0
        elif args.command == "list":
            result = [record.as_dict() for record in store.read_current(args.db)]
        else:
            result = report_database(args.db, args.start, args.end, args.category)
        print_result(args.command, result, args.json)
        return status
    except (InputError, OSError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
