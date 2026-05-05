"""Merge multiple .env files into a unified template with all known keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MergeResult:
    """Result of merging multiple env file dicts."""

    keys: Dict[str, Optional[str]] = field(default_factory=dict)
    """Merged key -> value mapping. Value is None when key has no consistent value."""

    sources: Dict[str, List[str]] = field(default_factory=dict)
    """Mapping of key -> list of source names where the key appeared."""

    conflicts: Dict[str, List[str]] = field(default_factory=dict)
    """Keys whose values differ across sources: key -> list of distinct values."""

    @property
    def all_keys(self) -> Set[str]:
        return set(self.keys.keys())

    @property
    def conflict_keys(self) -> Set[str]:
        return set(self.conflicts.keys())


def merge_envs(
    envs: Dict[str, Dict[str, str]],
    prefer: Optional[str] = None,
) -> MergeResult:
    """Merge multiple env dicts into a single MergeResult.

    Args:
        envs: Mapping of source_name -> parsed env dict.
        prefer: Optional source name whose values take precedence on conflict.

    Returns:
        A MergeResult containing merged keys, source tracking, and conflicts.
    """
    result = MergeResult()

    # Collect all keys and their values per source
    all_keys: Set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())

    for key in sorted(all_keys):
        values_seen: Dict[str, str] = {}
        for source_name, env in envs.items():
            if key in env:
                values_seen[source_name] = env[key]

        result.sources[key] = list(values_seen.keys())

        distinct_values = list(dict.fromkeys(values_seen.values()))

        if len(distinct_values) > 1:
            result.conflicts[key] = distinct_values
            if prefer and prefer in values_seen:
                result.keys[key] = values_seen[prefer]
            else:
                # Use the value from the first source that has it
                first_source = next(iter(envs))
                result.keys[key] = values_seen.get(first_source, distinct_values[0])
        elif len(distinct_values) == 1:
            result.keys[key] = distinct_values[0]
        else:
            result.keys[key] = None

    return result


def render_merged(result: MergeResult) -> str:
    """Render a MergeResult back into .env file content."""
    lines: List[str] = []
    for key in sorted(result.all_keys):
        value = result.keys.get(key, "")
        if value is None:
            value = ""
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""
