"""Rename keys across an env dict with optional dry-run support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameResult:
    renamed: Dict[str, str] = field(default_factory=dict)   # new_key -> value
    skipped: List[str] = field(default_factory=list)         # old keys not found
    applied: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *mapping*.

    Args:
        env:       Source environment dict.
        mapping:   Dict of {old_key: new_key}.
        overwrite: If False (default) and *new_key* already exists in *env*,
                   the rename is skipped and the old key is added to *skipped*.

    Returns:
        RenameResult with the updated env, list of applied renames, and
        list of old keys that were not found in *env*.
    """
    result_env: Dict[str, str] = dict(env)
    applied: List[Tuple[str, str]] = []
    skipped: List[str] = []

    for old_key, new_key in mapping.items():
        if old_key not in result_env:
            skipped.append(old_key)
            continue
        if new_key in result_env and not overwrite:
            skipped.append(old_key)
            continue
        value = result_env.pop(old_key)
        result_env[new_key] = value
        applied.append((old_key, new_key))

    return RenameResult(renamed=result_env, skipped=skipped, applied=applied)


def format_rename_report(result: RenameResult, *, color: bool = False) -> str:
    """Produce a human-readable report of a RenameResult."""
    lines: List[str] = []

    if result.applied:
        lines.append("Renamed keys:")
        for old, new in result.applied:
            entry = f"  {old} -> {new}"
            if color:
                entry = f"\033[32m{entry}\033[0m"
            lines.append(entry)
    else:
        lines.append("No keys renamed.")

    if result.skipped:
        lines.append("Skipped keys (not found or conflict):")
        for key in result.skipped:
            entry = f"  {key}"
            if color:
                entry = f"\033[33m{entry}\033[0m"
            lines.append(entry)

    return "\n".join(lines)
