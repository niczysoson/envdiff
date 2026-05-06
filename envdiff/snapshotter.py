"""Snapshot module: save and compare .env state across time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Snapshot:
    label: str
    timestamp: str
    env: Dict[str, str]
    source_file: Optional[str] = None


@dataclass
class SnapshotDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def create_snapshot(
    env: Dict[str, str],
    label: str,
    source_file: Optional[str] = None,
) -> Snapshot:
    """Create a snapshot of the given env dict."""
    timestamp = datetime.now(timezone.utc).isoformat()
    return Snapshot(label=label, timestamp=timestamp, env=env, source_file=source_file)


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    data = {
        "label": snapshot.label,
        "timestamp": snapshot.timestamp,
        "source_file": snapshot.source_file,
        "env": snapshot.env,
    }
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot(
        label=data["label"],
        timestamp=data["timestamp"],
        env=data["env"],
        source_file=data.get("source_file"),
    )


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return what changed."""
    old_env, new_env = old.env, new.env
    added = {k: v for k, v in new_env.items() if k not in old_env}
    removed = {k: v for k, v in old_env.items() if k not in new_env}
    changed = {
        k: (old_env[k], new_env[k])
        for k in old_env
        if k in new_env and old_env[k] != new_env[k]
    }
    return SnapshotDiff(added=added, removed=removed, changed=changed)


def format_snapshot_diff(diff: SnapshotDiff, color: bool = False) -> str:
    """Render a SnapshotDiff as a human-readable string."""
    if not diff.has_changes():
        return "No changes detected between snapshots."

    lines: List[str] = []
    for k, v in sorted(diff.added.items()):
        line = f"+ {k}={v}"
        lines.append(f"\033[32m{line}\033[0m" if color else line)
    for k, v in sorted(diff.removed.items()):
        line = f"- {k}={v}"
        lines.append(f"\033[31m{line}\033[0m" if color else line)
    for k, (old_v, new_v) in sorted(diff.changed.items()):
        line = f"~ {k}: {old_v!r} -> {new_v!r}"
        lines.append(f"\033[33m{line}\033[0m" if color else line)
    return "\n".join(lines)
