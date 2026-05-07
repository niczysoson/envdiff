"""CLI commands for the redactor feature."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.parser import parse_env_file
from envdiff.redactor import DEFAULT_MASK, redact_env


def _parse_extra_patterns(raw: str) -> List[str]:
    """Split a comma-separated string of patterns into a list."""
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def cmd_redact(args: argparse.Namespace) -> int:
    """Print the env file with sensitive values masked."""
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    extra = _parse_extra_patterns(args.patterns or "")
    keep = [k.strip() for k in (args.keep or "").split(",") if k.strip()]
    mask = args.mask or DEFAULT_MASK

    result = redact_env(env, extra_patterns=extra, mask=mask, keep_keys=keep or None)

    for key, value in result.redacted.items():
        print(f"{key}={value}")

    if args.summary:
        print(f"\n# Redacted {len(result.redacted_keys)} key(s): {', '.join(result.redacted_keys)}",
              file=sys.stderr)
    return 0


def register_redactor_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the 'redact' subcommand to *subparsers*."""
    p = subparsers.add_parser("redact", help="Mask sensitive values in an env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--patterns",
        default="",
        help="Comma-separated extra regex patterns to treat as sensitive",
    )
    p.add_argument(
        "--keep",
        default="",
        help="Comma-separated keys that must never be redacted",
    )
    p.add_argument(
        "--mask",
        default=DEFAULT_MASK,
        help="Replacement string for sensitive values",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of redacted keys to stderr",
    )
    p.set_defaults(func=cmd_redact)
