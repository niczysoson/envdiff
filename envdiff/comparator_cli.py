"""CLI commands for the multi-file comparator."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.comparator import compare_many, summary_table
from envdiff.parser import parse_env_file
from envdiff.report import format_report


def cmd_compare(args: argparse.Namespace) -> int:
    """Entry point for the ``compare`` sub-command."""
    try:
        source = parse_env_file(args.source)
    except FileNotFoundError:
        print(f"error: source file not found: {args.source}", file=sys.stderr)
        return 2

    targets: dict = {}
    for path in args.targets:
        try:
            targets[path] = parse_env_file(path)
        except FileNotFoundError:
            print(f"warning: target file not found, skipping: {path}", file=sys.stderr)

    if not targets:
        print("error: no valid target files provided", file=sys.stderr)
        return 2

    compare = compare_many(source, targets, source_file=args.source)

    if args.summary:
        for line in summary_table(compare):
            print(line)
    else:
        for label, diff in compare.results.items():
            print(f"--- {args.source}")
            print(f"+++ {label}")
            color = not args.no_color
            print(format_report(diff, color=color))

    if args.exit_code and compare.any_differences:
        return 1
    return 0


def register_comparator_commands(subparsers) -> None:  # type: ignore[type-arg]
    p: argparse.ArgumentParser = subparsers.add_parser(
        "compare",
        help="Diff one source .env against multiple target files.",
    )
    p.add_argument("source", help="Source .env file")
    p.add_argument("targets", nargs="+", help="One or more target .env files")
    p.add_argument("--summary", action="store_true", help="Print one-line summary per target")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colours")
    p.add_argument("--exit-code", action="store_true", help="Exit 1 when differences found")
    p.set_defaults(func=cmd_compare)
