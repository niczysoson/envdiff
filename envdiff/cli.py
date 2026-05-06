"""CLI entry point for envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.differ import diff_envs, has_differences
from envdiff.parser import parse_env_file
from envdiff.report import format_report
from envdiff.sorter import group_by_prefix, render_sorted, sort_alphabetically


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command")

    diff_cmd = sub.add_parser("diff", help="Diff two .env files")
    diff_cmd.add_argument("source", help="Source .env file")
    diff_cmd.add_argument("target", help="Target .env file")
    diff_cmd.add_argument("--no-color", action="store_true", help="Disable color output")
    diff_cmd.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code when differences are found",
    )

    sort_cmd = sub.add_parser("sort", help="Sort and display a .env file")
    sort_cmd.add_argument("file", help=".env file to sort")
    sort_cmd.add_argument(
        "--group",
        action="store_true",
        help="Group variables by prefix",
    )
    sort_cmd.add_argument(
        "--no-headers",
        action="store_true",
        help="Suppress prefix group headers",
    )
    sort_cmd.add_argument(
        "--delimiter",
        default="_",
        help="Delimiter used to detect prefixes (default: _)",
    )

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "diff":
        source = parse_env_file(Path(args.source))
        target = parse_env_file(Path(args.target))
        result = diff_envs(source, target)
        color = not args.no_color
        print(format_report(result, color=color))
        if args.exit_code and has_differences(result):
            return 1
        return 0

    if args.command == "sort":
        env = parse_env_file(Path(args.file))
        if args.group:
            sort_result = group_by_prefix(env, delimiter=args.delimiter)
            output = render_sorted(sort_result, show_prefix_headers=not args.no_headers)
        else:
            pairs = sort_alphabetically(env)
            output = "\n".join(f"{k}={v}" for k, v in pairs)
        print(output)
        return 0

    parser.print_help()
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
