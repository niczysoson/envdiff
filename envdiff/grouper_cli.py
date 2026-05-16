"""CLI commands for the grouper module."""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List

from envdiff.grouper import format_group_report, group_by_map, group_by_prefix
from envdiff.parser import parse_env_file


def _parse_tag_map(pairs: List[str]) -> Dict[str, str]:
    """Parse ``KEY=group`` strings into a dict."""
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid tag mapping {pair!r}. Expected KEY=group."
            )
        key, group = pair.split("=", 1)
        result[key.strip()] = group.strip()
    return result


def cmd_group(
    args: argparse.Namespace,
    stdout=sys.stdout,
    stderr=sys.stderr,
) -> int:
    """Entry point for the ``envdiff group`` sub-command."""
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        stderr.write(f"Error: file not found: {args.file}\n")
        return 2

    if getattr(args, "tag_map", None):
        try:
            tag_map = _parse_tag_map(args.tag_map)
        except argparse.ArgumentTypeError as exc:
            stderr.write(f"Error: {exc}\n")
            return 2
        result = group_by_map(env, tag_map)
    else:
        delimiter = getattr(args, "delimiter", "_") or "_"
        min_size = getattr(args, "min_group_size", 1) or 1
        result = group_by_prefix(env, delimiter=delimiter, min_group_size=min_size)

    report = format_group_report(result, color=getattr(args, "color", False))
    stdout.write(report + "\n")
    return 0


def register_grouper_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("group", help="Group env variables by prefix or tag map")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--delimiter",
        default="_",
        help="Key delimiter for prefix extraction (default: _)",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        dest="min_group_size",
        help="Minimum keys required to form a named group (default: 1)",
    )
    p.add_argument(
        "--tag",
        nargs="*",
        dest="tag_map",
        metavar="KEY=group",
        help="Explicit key-to-group mappings (overrides prefix mode)",
    )
    p.add_argument("--color", action="store_true", help="Enable ANSI colour output")
    p.set_defaults(func=cmd_group)
