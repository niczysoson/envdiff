"""CLI commands for the key-renamer feature."""
from __future__ import annotations

import argparse
import sys
from typing import Dict

from envdiff.parser import parse_env_file
from envdiff.renamer import format_rename_report, rename_keys


def _parse_mapping(raw: list[str]) -> Dict[str, str]:
    """Parse a list of 'OLD=NEW' strings into a dict."""
    mapping: Dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid rename spec {item!r}: expected OLD=NEW"
            )
        old, new = item.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


def cmd_rename(
    args: argparse.Namespace,
    out=sys.stdout,
    err=sys.stderr,
) -> int:
    """Entry point for the 'rename' sub-command."""
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        err.write(f"File not found: {args.file}\n")
        return 2

    try:
        mapping = _parse_mapping(args.rename or [])
    except argparse.ArgumentTypeError as exc:
        err.write(f"{exc}\n")
        return 2

    if not mapping:
        err.write("No rename specs provided. Use --rename OLD=NEW.\n")
        return 2

    result = rename_keys(env, mapping, overwrite=args.overwrite)
    report = format_rename_report(result, color=args.color)
    out.write(report + "\n")

    if args.in_place:
        with open(args.file, "w") as fh:
            for key, value in result.renamed.items():
                fh.write(f"{key}={value}\n")

    return 1 if result.skipped else 0


def register_renamer_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("rename", help="Rename keys in an .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--rename",
        metavar="OLD=NEW",
        nargs="+",
        help="One or more OLD=NEW rename specs",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing key if new name already present",
    )
    p.add_argument(
        "--in-place",
        action="store_true",
        dest="in_place",
        help="Write renamed env back to the source file",
    )
    p.add_argument("--color", action="store_true", help="Colorize output")
    p.set_defaults(func=cmd_rename)
