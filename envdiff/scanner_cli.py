"""CLI commands for the scanner feature."""

from __future__ import annotations

import argparse
from pathlib import Path

from envdiff.scanner import ScanResult, has_issues, scan_env_file
from envdiff.report import _colorize


def format_scan_report(result: ScanResult, color: bool = False) -> str:
    lines: list[str] = []
    header = f"Scan report for: {result.source_file or '(unknown)'}"
    lines.append(_colorize(header, "\033[1m", color))

    if result.duplicates:
        lines.append(_colorize("  Duplicate keys:", "\033[33m", color))
        for key, count in result.duplicates.items():
            lines.append(f"    {key}  ({count}x)")
    else:
        lines.append("  No duplicate keys found.")

    if result.suspicious:
        lines.append(_colorize("  Suspicious values:", "\033[31m", color))
        for key in result.suspicious:
            lines.append(f"    {key}")
    else:
        lines.append("  No suspicious values found.")

    return "\n".join(lines)


def cmd_scan(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 2

    lines = path.read_text(encoding="utf-8").splitlines()
    result = scan_env_file(lines, source_file=str(path))
    report = format_scan_report(result, color=getattr(args, "color", False))
    print(report)

    if has_issues(result) and getattr(args, "exit_code", False):
        return 1
    return 0


def register_scanner_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("scan", help="Scan a .env file for duplicates and suspicious values")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--color", action="store_true", help="Enable colored output")
    p.add_argument("--exit-code", action="store_true", dest="exit_code",
                   help="Exit with code 1 if issues are found")
    p.set_defaults(func=cmd_scan)
