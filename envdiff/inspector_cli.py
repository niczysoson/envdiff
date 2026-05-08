"""CLI commands for the inspector module."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.inspector import inspect_env, format_inspect_report


def cmd_inspect(args: argparse.Namespace) -> int:
    """Run inspection on one or more .env files."""
    exit_code = 0
    for raw_path in args.files:
        path = Path(raw_path)
        if not path.exists():
            print(f"[error] File not found: {path}", file=sys.stderr)
            exit_code = 2
            continue

        env = parse_env_file(path)
        result = inspect_env(env, source=str(path))
        report = format_inspect_report(result, color=args.color)
        print(report)

        if result.has_anomalies and args.exit_code:
            exit_code = 1

    return exit_code


def register_inspector_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "inspect",
        help="Inspect one or more .env files for anomalies and statistics.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to .env file(s) to inspect.",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Enable ANSI colour output.",
    )
    parser.add_argument(
        "--exit-code",
        dest="exit_code",
        action="store_true",
        default=False,
        help="Exit with code 1 if anomalies are found.",
    )
    parser.set_defaults(func=cmd_inspect)
