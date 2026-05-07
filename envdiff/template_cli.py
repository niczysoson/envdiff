"""CLI commands for the template generation feature."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.parser import parse_env_file
from envdiff.templater import build_template, render_template


def _parse_keep(raw: Optional[str]) -> List[str]:
    """Split comma-separated keep-keys string into a list."""
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


def cmd_template_generate(args: argparse.Namespace) -> int:
    """Generate a .env.example from a source .env file."""
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: source file '{source_path}' not found.", file=sys.stderr)
        return 1

    env = parse_env_file(str(source_path))
    keep_keys = _parse_keep(getattr(args, "keep", None))
    placeholder = getattr(args, "placeholder", "<REPLACE_ME>")

    result = build_template(env, keep_keys=keep_keys, placeholder=placeholder)
    output = render_template(result)

    output_path = getattr(args, "output", None)
    if output_path:
        Path(output_path).write_text(output)
        print(f"Template written to {output_path}")
    else:
        print(output, end="")

    return 0


def register_template_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register template subcommands onto an existing subparser group."""
    p = subparsers.add_parser(
        "template",
        help="Generate a .env.example template from a .env file",
    )
    p.add_argument("source", help="Path to source .env file")
    p.add_argument("-o", "--output", help="Write output to this file instead of stdout")
    p.add_argument(
        "--keep",
        help="Comma-separated list of keys whose values should NOT be redacted",
    )
    p.add_argument(
        "--placeholder",
        default="<REPLACE_ME>",
        help="Placeholder string for redacted values (default: <REPLACE_ME>)",
    )
    p.set_defaults(func=cmd_template_generate)
