"""aliaser_cli.py — CLI commands for the aliaser module."""
from __future__ import annotations

import argparse
from typing import Dict

from envdiff.parser import parse_env_file
from envdiff.aliaser import apply_aliases, format_alias_report


def _parse_aliases(pairs: list[str]) -> Dict[str, str]:
    """Parse a list of 'ORIGINAL=ALIAS' strings into a dict."""
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid alias mapping {pair!r}; expected ORIGINAL=ALIAS"
            )
        src, _, dst = pair.partition("=")
        result[src.strip()] = dst.strip()
    return result


def cmd_alias(args: argparse.Namespace) -> int:
    env = parse_env_file(args.file)
    try:
        aliases = _parse_aliases(args.map or [])
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}")
        return 2

    result = apply_aliases(env, aliases, overwrite=args.overwrite)
    print(format_alias_report(result, color=args.color))
    return 0


def register_aliaser_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("alias", help="Apply key aliases to an env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--map",
        metavar="ORIGINAL=ALIAS",
        nargs="+",
        help="One or more ORIGINAL=ALIAS mappings",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite alias key if it already exists in the env",
    )
    p.add_argument("--color", action="store_true", default=False, help="Colorize output")
    p.set_defaults(func=cmd_alias)
