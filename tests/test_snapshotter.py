"""Tests for envdiff.snapshotter."""

import json
import os
import pytest

from envdiff.snapshotter import (
    Snapshot,
    SnapshotDiff,
    create_snapshot,
    diff_snapshots,
    format_snapshot_diff,
    load_snapshot,
    save_snapshot,
)


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"}


def test_create_snapshot_stores_env():
    snap = create_snapshot(ENV_A, label="test")
    assert snap.env == ENV_A
    assert snap.label == "test"
    assert snap.timestamp  # non-empty


def test_create_snapshot_records_source_file():
    snap = create_snapshot(ENV_A, label="ci", source_file=".env.ci")
    assert snap.source_file == ".env.ci"


def test_save_and_load_snapshot_roundtrip(tmp_path):
    snap = create_snapshot(ENV_A, label="roundtrip", source_file=".env")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded.label == snap.label
    assert loaded.env == snap.env
    assert loaded.source_file == snap.source_file
    assert loaded.timestamp == snap.timestamp


def test_save_snapshot_creates_valid_json(tmp_path):
    snap = create_snapshot({"KEY": "val"}, label="x")
    path = str(tmp_path / "out.json")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert data["env"] == {"KEY": "val"}


def test_diff_snapshots_detects_added():
    old = create_snapshot(ENV_A, label="old")
    new = create_snapshot(ENV_B, label="new")
    result = diff_snapshots(old, new)
    assert "LOG_LEVEL" in result.added
    assert result.added["LOG_LEVEL"] == "info"


def test_diff_snapshots_detects_removed():
    old = create_snapshot(ENV_A, label="old")
    new = create_snapshot(ENV_B, label="new")
    result = diff_snapshots(old, new)
    assert "DEBUG" in result.removed


def test_diff_snapshots_detects_changed():
    old = create_snapshot(ENV_A, label="old")
    new = create_snapshot(ENV_B, label="new")
    result = diff_snapshots(old, new)
    assert "HOST" in result.changed
    assert result.changed["HOST"] == ("localhost", "prod.example.com")


def test_diff_snapshots_no_change_for_matching_key():
    old = create_snapshot(ENV_A, label="old")
    new = create_snapshot(ENV_B, label="new")
    result = diff_snapshots(old, new)
    assert "PORT" not in result.changed
    assert "PORT" not in result.added
    assert "PORT" not in result.removed


def test_has_changes_true():
    diff = SnapshotDiff(added={"X": "1"})
    assert diff.has_changes() is True


def test_has_changes_false():
    diff = SnapshotDiff()
    assert diff.has_changes() is False


def test_format_snapshot_diff_no_changes():
    diff = SnapshotDiff()
    output = format_snapshot_diff(diff)
    assert "No changes" in output


def test_format_snapshot_diff_shows_added():
    diff = SnapshotDiff(added={"NEW_KEY": "value"})
    output = format_snapshot_diff(diff)
    assert "+ NEW_KEY=value" in output


def test_format_snapshot_diff_shows_removed():
    diff = SnapshotDiff(removed={"OLD_KEY": "gone"})
    output = format_snapshot_diff(diff)
    assert "- OLD_KEY=gone" in output


def test_format_snapshot_diff_shows_changed():
    diff = SnapshotDiff(changed={"HOST": ("old", "new")})
    output = format_snapshot_diff(diff)
    assert "~ HOST" in output
    assert "old" in output
    assert "new" in output


def test_format_snapshot_diff_color_wraps_added():
    diff = SnapshotDiff(added={"K": "v"})
    output = format_snapshot_diff(diff, color=True)
    assert "\033[32m" in output
