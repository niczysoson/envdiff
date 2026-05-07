"""CLI commands for the env profiler."""
from __future__ import annotations

import argparse
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.profiler import ProfileResult, profile_env


def _format_list(label: str, items: list, color: bool) -> str:
    if not items:
        return ""
    joined = ", ".join(items)
    line = f"  {label}: {joined}"
    if color:
        line = f"\033[33m{line}\033[0m"
    return line


def format_profile_report(result: ProfileResult, color: bool = True) -> str:
    lines = []
    header = f"Profile: {result.source_file or '(unknown)'}"
    lines.append(f"\033[1m{header}\033[0m" if color else header)
    lines.append(f"  Total keys      : {result.total_keys}")
    lines.append(f"  Empty values    : {result.empty_count}")
    lines.append(f"  Placeholders    : {result.placeholder_count}")
    lines.append(f"  Numeric values  : {len(result.numeric_value_keys)}")
    lines.append(f"  Boolean values  : {len(result.boolean_value_keys)}")
    lines.append(f"  Long values     : {len(result.long_value_keys)}")
    lines.append(f"  Complexity score: {result.complexity_score}")

    for label, items in [
        ("Empty keys", result.empty_keys),
        ("Placeholder keys", result.placeholder_keys),
        ("Long-value keys", result.long_value_keys),
    ]:
        entry = _format_list(label, items, color)
        if entry:
            lines.append(entry)

    return "\n".join(lines)


def cmd_profile(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 1
    env = parse_env_file(path)
    result = profile_env(env, source_file=str(path))
    color = not getattr(args, "no_color", False)
    print(format_profile_report(result, color=color))
    return 0


def register_profiler_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("profile", help="Profile a .env file and show statistics")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--no-color", action="store_true", help="Disable coloured output")
    p.set_defaults(func=cmd_profile)
