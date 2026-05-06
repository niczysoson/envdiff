"""CLI sub-commands for snapshot management (save, load, diff, list)."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.parser import parse_env_file
from envdiff.snapshot_store import SnapshotStore
from envdiff.snapshotter import (
    create_snapshot,
    diff_snapshots,
    format_snapshot_diff,
)


def _get_store(args: argparse.Namespace) -> SnapshotStore:
    store_dir = getattr(args, "store_dir", ".envdiff_snapshots")
    return SnapshotStore(store_dir=store_dir)


def cmd_snapshot_save(args: argparse.Namespace) -> int:
    env = parse_env_file(args.file)
    snap = create_snapshot(env, label=args.label, source_file=args.file)
    store = _get_store(args)
    path = store.save(snap)
    print(f"Snapshot '{args.label}' saved to {path}")
    return 0


def cmd_snapshot_list(args: argparse.Namespace) -> int:
    store = _get_store(args)
    labels = store.list_labels()
    if not labels:
        print("No snapshots stored.")
    else:
        for label in labels:
            print(label)
    return 0


def cmd_snapshot_diff(args: argparse.Namespace) -> int:
    store = _get_store(args)
    try:
        old = store.load(args.old)
        new = store.load(args.new)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    diff = diff_snapshots(old, new)
    color = not getattr(args, "no_color", False)
    print(format_snapshot_diff(diff, color=color))
    return 1 if (diff.has_changes() and getattr(args, "exit_code", False)) else 0


def cmd_snapshot_delete(args: argparse.Namespace) -> int:
    store = _get_store(args)
    removed = store.delete(args.label)
    if removed:
        print(f"Snapshot '{args.label}' deleted.")
        return 0
    print(f"Snapshot '{args.label}' not found.", file=sys.stderr)
    return 1


def build_snapshot_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach snapshot sub-commands to an existing subparser group."""
    snap = subparsers.add_parser("snapshot", help="Manage env snapshots")
    snap_sub = snap.add_subparsers(dest="snap_cmd", required=True)

    save_p = snap_sub.add_parser("save", help="Save a snapshot")
    save_p.add_argument("file", help="Path to .env file")
    save_p.add_argument("label", help="Label for the snapshot")
    save_p.add_argument("--store-dir", default=".envdiff_snapshots")
    save_p.set_defaults(func=cmd_snapshot_save)

    list_p = snap_sub.add_parser("list", help="List stored snapshots")
    list_p.add_argument("--store-dir", default=".envdiff_snapshots")
    list_p.set_defaults(func=cmd_snapshot_list)

    diff_p = snap_sub.add_parser("diff", help="Diff two snapshots")
    diff_p.add_argument("old", help="Label of the older snapshot")
    diff_p.add_argument("new", help="Label of the newer snapshot")
    diff_p.add_argument("--store-dir", default=".envdiff_snapshots")
    diff_p.add_argument("--no-color", action="store_true")
    diff_p.add_argument("--exit-code", action="store_true")
    diff_p.set_defaults(func=cmd_snapshot_diff)

    del_p = snap_sub.add_parser("delete", help="Delete a snapshot")
    del_p.add_argument("label", help="Label to delete")
    del_p.add_argument("--store-dir", default=".envdiff_snapshots")
    del_p.set_defaults(func=cmd_snapshot_delete)
