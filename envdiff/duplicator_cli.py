"""CLI commands for the duplicator module."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.parser import parse_env_file
from envdiff.duplicator import find_duplicates, format_duplicate_report


def cmd_duplicates(args: argparse.Namespace) -> int:
    """Scan a .env file for keys that share the same value."""
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = find_duplicates(env)
    report = format_duplicate_report(result, color=args.color)
    print(report)

    if args.exit_code and result.has_duplicates:
        return 1
    return 0


def register_duplicator_commands(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    """Attach the 'duplicates' sub-command to an existing argument parser."""
    p = subparsers.add_parser(
        "duplicates",
        help="Find keys that share the same value in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file to inspect.")
    p.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Enable ANSI colour output.",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when duplicates are found.",
    )
    p.set_defaults(func=cmd_duplicates)
