"""Unit tests for envdiff.differ_timeline."""

from __future__ import annotations

import pytest

from envdiff.snapshotter import create_snapshot
from envdiff.differ_timeline import (
    TimelineEntry,
    TimelineResult,
    diff_timeline,
)


def _snap(env: dict, label: str):
    return create_snapshot(env, source_file=label)


def test_diff_timeline_empty_returns_no_entries():
    result = diff_timeline([])
    assert result.entries == []


def test_diff_timeline_single_snapshot_returns_no_entries():
    result = diff_timeline([_snap({"A": "1"}, "s1")])
    assert result.entries == []


def test_diff_timeline_no_changes_when_identical():
    s1 = _snap({"A": "1", "B": "2"}, "v1")
    s2 = _snap({"A": "1", "B": "2"}, "v2")
    result = diff_timeline([s1, s2])
    assert len(result.entries) == 1
    assert not result.entries[0].has_changes


def test_diff_timeline_detects_added_key():
    s1 = _snap({"A": "1"}, "v1")
    s2 = _snap({"A": "1", "B": "2"}, "v2")
    result = diff_timeline([s1, s2])
    assert result.entries[0].added == {"B": "2"}


def test_diff_timeline_detects_removed_key():
    s1 = _snap({"A": "1", "B": "2"}, "v1")
    s2 = _snap({"A": "1"}, "v2")
    result = diff_timeline([s1, s2])
    assert result.entries[0].removed == {"B": "2"}


def test_diff_timeline_detects_changed_value():
    s1 = _snap({"A": "old"}, "v1")
    s2 = _snap({"A": "new"}, "v2")
    result = diff_timeline([s1, s2])
    assert result.entries[0].changed == {"A": ("old", "new")}


def test_diff_timeline_multiple_steps():
    s1 = _snap({"A": "1"}, "v1")
    s2 = _snap({"A": "2"}, "v2")
    s3 = _snap({"A": "2", "B": "3"}, "v3")
    result = diff_timeline([s1, s2, s3])
    assert len(result.entries) == 2
    assert result.entries[0].changed == {"A": ("1", "2")}
    assert result.entries[1].added == {"B": "3"}


def test_any_changes_false_when_all_identical():
    s1 = _snap({"X": "1"}, "v1")
    s2 = _snap({"X": "1"}, "v2")
    result = diff_timeline([s1, s2])
    assert not result.any_changes


def test_any_changes_true_when_drift_exists():
    s1 = _snap({"X": "1"}, "v1")
    s2 = _snap({"X": "2"}, "v2")
    result = diff_timeline([s1, s2])
    assert result.any_changes


def test_total_changes_counts_all():
    s1 = _snap({"A": "1", "B": "2"}, "v1")
    s2 = _snap({"A": "9", "C": "3"}, "v2")
    result = diff_timeline([s1, s2])
    # A changed, B removed, C added => 3
    assert result.total_changes == 3


def test_entry_labels_are_set_correctly():
    s1 = _snap({}, "alpha.env")
    s2 = _snap({}, "beta.env")
    result = diff_timeline([s1, s2])
    assert result.entries[0].from_label == "alpha.env"
    assert result.entries[0].to_label == "beta.env"
