"""Snapshot store: list and manage persisted snapshots on disk."""

from __future__ import annotations

import glob
import os
from typing import List

from envdiff.snapshotter import Snapshot, load_snapshot, save_snapshot


DEFAULT_STORE_DIR = ".envdiff_snapshots"


class SnapshotStore:
    """Manages a directory of saved env snapshots."""

    def __init__(self, store_dir: str = DEFAULT_STORE_DIR) -> None:
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)

    def _path_for(self, label: str) -> str:
        safe = label.replace(os.sep, "_").replace(" ", "_")
        return os.path.join(self.store_dir, f"{safe}.json")

    def save(self, snapshot: Snapshot) -> str:
        """Persist snapshot; returns the file path used."""
        path = self._path_for(snapshot.label)
        save_snapshot(snapshot, path)
        return path

    def load(self, label: str) -> Snapshot:
        """Load a snapshot by label."""
        path = self._path_for(label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Snapshot '{label}' not found at {path}")
        return load_snapshot(path)

    def list_labels(self) -> List[str]:
        """Return sorted list of stored snapshot labels."""
        pattern = os.path.join(self.store_dir, "*.json")
        paths = glob.glob(pattern)
        labels = [
            os.path.splitext(os.path.basename(p))[0] for p in sorted(paths)
        ]
        return labels

    def delete(self, label: str) -> bool:
        """Delete a snapshot by label. Returns True if deleted, False if not found."""
        path = self._path_for(label)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def exists(self, label: str) -> bool:
        """Check whether a snapshot with the given label exists."""
        return os.path.exists(self._path_for(label))
