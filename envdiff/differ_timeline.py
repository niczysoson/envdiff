"""Timeline diff: compare a sequence of snapshots to track env drift over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.snapshotter import Snapshot


@dataclass
class TimelineEntry:
    """Diff between two consecutive snapshots."""

    from_label: str
    to_label: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


@dataclass
class TimelineResult:
    entries: List[TimelineEntry] = field(default_factory=list)

    @property
    def any_changes(self) -> bool:
        return any(e.has_changes for e in self.entries)

    @property
    def total_changes(self) -> int:
        return sum(
            len(e.added) + len(e.removed) + len(e.changed)
            for e in self.entries
        )


def _diff_two(snap_a: Snapshot, snap_b: Snapshot) -> Tuple[
    Dict[str, str], Dict[str, str], Dict[str, Tuple[str, str]]
]:
    keys_a = set(snap_a.env.keys())
    keys_b = set(snap_b.env.keys())

    added = {k: snap_b.env[k] for k in keys_b - keys_a}
    removed = {k: snap_a.env[k] for k in keys_a - keys_b}
    changed = {
        k: (snap_a.env[k], snap_b.env[k])
        for k in keys_a & keys_b
        if snap_a.env[k] != snap_b.env[k]
    }
    return added, removed, changed


def diff_timeline(snapshots: List[Snapshot]) -> TimelineResult:
    """Produce a timeline of diffs across an ordered list of snapshots."""
    if len(snapshots) < 2:
        return TimelineResult()

    entries: List[TimelineEntry] = []
    for i in range(len(snapshots) - 1):
        a, b = snapshots[i], snapshots[i + 1]
        added, removed, changed = _diff_two(a, b)
        entries.append(
            TimelineEntry(
                from_label=a.source_file,
                to_label=b.source_file,
                added=added,
                removed=removed,
                changed=changed,
            )
        )
    return TimelineResult(entries=entries)
