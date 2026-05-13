"""CLI sub-commands for the patcher module."""
from __future__ import annotations

import argparse
from typing import List

from envdiff.parser import parse_env_file
from envdiff.patcher import has_changes, patch_env, render_patch_report


def _parse_overrides(pairs: List[str]) -> dict:
    """Parse KEY=VALUE strings into a dict, raising on bad format."""
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Override must be in KEY=VALUE format, got: {pair!r}"
            )
        key, _, value = pair.partition("=")
        key = key.strip()
        if not key:
            raise argparse.ArgumentTypeError(f"Empty key in override: {pair!r}")
        result[key] = value
    return result


def cmd_patch(args: argparse.Namespace) -> int:
    """Apply key-value overrides to an .env file and print the result."""
    try:
        overrides = _parse_overrides(args.set or [])
    except argparse.ArgumentTypeError as exc:
        print(f"Error: {exc}")
        return 2

    env = parse_env_file(args.file)
    result = patch_env(
        env,
        overrides,
        add_missing=not args.no_add,
        skip_existing=args.skip_existing,
    )

    print(render_patch_report(result, color=args.color))

    if args.output:
        lines = [f"{k}={v}" for k, v in sorted(result.patched.items())]
        with open(args.output, "w") as fh:
            fh.write("\n".join(lines) + "\n")

    if args.exit_code and has_changes(result):
        return 1
    return 0


def register_patcher_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser("patch", help="Apply key-value overrides to an .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        nargs="+",
        help="One or more KEY=VALUE overrides to apply",
    )
    p.add_argument(
        "--no-add",
        action="store_true",
        help="Do not add keys that are missing from the source file",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip keys that already exist in the source file",
    )
    p.add_argument("--output", metavar="FILE", help="Write patched env to this file")
    p.add_argument("--color", action="store_true", help="Enable coloured output")
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when changes were applied",
    )
    p.set_defaults(func=cmd_patch)
