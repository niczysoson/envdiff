"""CLI commands for multi-target diffing."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envdiff.parser import parse_env_file
from envdiff.differ_multi import diff_one_to_many, format_multi_diff_report


def cmd_diff_multi(args: argparse.Namespace) -> int:
    """Compare one source .env file against multiple target .env files."""
    try:
        source_env = parse_env_file(args.source)
    except FileNotFoundError:
        print(f"error: source file not found: {args.source}", file=sys.stderr)
        return 2

    targets = []
    for path_str in args.targets:
        p = Path(path_str)
        try:
            env = parse_env_file(path_str)
        except FileNotFoundError:
            print(f"warning: target file not found, skipping: {path_str}", file=sys.stderr)
            continue
        targets.append((p.name, env))

    if not targets:
        print("error: no valid target files provided.", file=sys.stderr)
        return 2

    result = diff_one_to_many(source_env, targets, source_file=args.source)
    report = format_multi_diff_report(result, color=not args.no_color)
    print(report)

    if args.exit_code and result.any_differences():
        return 1
    return 0


def register_diff_multi_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "diff-multi",
        help="Diff one source .env against multiple target files.",
    )
    p.add_argument("source", help="Path to the source .env file.")
    p.add_argument("targets", nargs="+", help="One or more target .env files.")
    p.add_argument("--no-color", action="store_true", default=False)
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any differences are found.",
    )
    p.set_defaults(func=cmd_diff_multi)
