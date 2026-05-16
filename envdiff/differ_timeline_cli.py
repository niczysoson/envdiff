"""CLI commands for the timeline diff feature."""

from __future__ import annotations

import argparse
from typing import List

from envdiff.parser import parse_env_file
from envdiff.snapshotter import create_snapshot
from envdiff.differ_timeline import diff_timeline, TimelineResult
from envdiff.report import _colorize


def _format_timeline_report(result: TimelineResult, *, color: bool = False) -> str:
    if not result.any_changes:
        return _colorize("No changes across timeline.", "green", color)

    lines: List[str] = []
    for entry in result.entries:
        header = f"[{entry.from_label}] -> [{entry.to_label}]"
        lines.append(_colorize(header, "cyan", color))
        for k, v in sorted(entry.added.items()):
            lines.append(_colorize(f"  + {k}={v}", "green", color))
        for k, v in sorted(entry.removed.items()):
            lines.append(_colorize(f"  - {k}={v}", "red", color))
        for k, (old, new) in sorted(entry.changed.items()):
            lines.append(_colorize(f"  ~ {k}: {old!r} -> {new!r}", "yellow", color))
        if not entry.has_changes:
            lines.append("  (no changes)")
    return "\n".join(lines)


def cmd_diff_timeline(args: argparse.Namespace) -> int:
    snapshots = []
    for path in args.files:
        env = parse_env_file(path)
        snapshots.append(create_snapshot(env, source_file=path))

    result = diff_timeline(snapshots)
    print(_format_timeline_report(result, color=args.color))
    if args.exit_code and result.any_changes:
        return 1
    return 0


def register_timeline_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "timeline",
        help="Diff a sequence of .env files to track changes over time",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Ordered list of .env files to compare (oldest first)",
    )
    p.add_argument("--color", action="store_true", default=False)
    p.add_argument("--exit-code", action="store_true", default=False)
    p.set_defaults(func=cmd_diff_timeline)
