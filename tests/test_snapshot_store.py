"""Tests for envdiff.snapshot_store."""

import pytest

from envdiff.snapshot_store import SnapshotStore
from envdiff.snapshotter import create_snapshot


@pytest.fixture
def store(tmp_path):
    return SnapshotStore(store_dir=str(tmp_path / "snaps"))


@pytest.fixture
def snap_dev():
    return create_snapshot({"HOST": "localhost", "PORT": "8000"}, label="dev")


@pytest.fixture
def snap_prod():
    return create_snapshot({"HOST": "prod.example.com", "PORT": "443"}, label="prod")


def test_save_and_exists(store, snap_dev):
    store.save(snap_dev)
    assert store.exists("dev") is True


def test_load_returns_correct_env(store, snap_dev):
    store.save(snap_dev)
    loaded = store.load("dev")
    assert loaded.env == snap_dev.env
    assert loaded.label == "dev"


def test_load_missing_raises(store):
    with pytest.raises(FileNotFoundError, match="Snapshot 'ghost'"):
        store.load("ghost")


def test_list_labels_empty(store):
    assert store.list_labels() == []


def test_list_labels_multiple(store, snap_dev, snap_prod):
    store.save(snap_dev)
    store.save(snap_prod)
    labels = store.list_labels()
    assert "dev" in labels
    assert "prod" in labels


def test_list_labels_sorted(store, snap_dev, snap_prod):
    store.save(snap_prod)
    store.save(snap_dev)
    labels = store.list_labels()
    assert labels == sorted(labels)


def test_delete_existing(store, snap_dev):
    store.save(snap_dev)
    result = store.delete("dev")
    assert result is True
    assert store.exists("dev") is False


def test_delete_nonexistent(store):
    result = store.delete("ghost")
    assert result is False


def test_exists_false_before_save(store):
    assert store.exists("nothing") is False


def test_overwrite_snapshot(store, snap_dev):
    store.save(snap_dev)
    updated = create_snapshot({"HOST": "newhost"}, label="dev")
    store.save(updated)
    loaded = store.load("dev")
    assert loaded.env["HOST"] == "newhost"
