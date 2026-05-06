"""Sort and group environment variables by prefix or alphabetically."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SortResult:
    grouped: Dict[str, List[Tuple[str, str]]]
    ungrouped: List[Tuple[str, str]]


def _extract_prefix(key: str, delimiter: str = "_") -> str:
    """Return the prefix of a key (part before the first delimiter)."""
    if delimiter in key:
        return key.split(delimiter, 1)[0]
    return ""


def sort_alphabetically(env: Dict[str, str]) -> List[Tuple[str, str]]:
    """Return env items sorted alphabetically by key."""
    return sorted(env.items(), key=lambda kv: kv[0])


def group_by_prefix(
    env: Dict[str, str],
    delimiter: str = "_",
    min_group_size: int = 2,
) -> SortResult:
    """Group env variables by their key prefix.

    Keys whose prefix group has fewer than *min_group_size* members are placed
    in the ``ungrouped`` bucket instead.
    """
    buckets: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    no_prefix: List[Tuple[str, str]] = []

    for key, value in env.items():
        prefix = _extract_prefix(key, delimiter)
        if prefix:
            buckets[prefix].append((key, value))
        else:
            no_prefix.append((key, value))

    grouped: Dict[str, List[Tuple[str, str]]] = {}
    ungrouped: List[Tuple[str, str]] = list(no_prefix)

    for prefix, items in sorted(buckets.items()):
        if len(items) >= min_group_size:
            grouped[prefix] = sorted(items, key=lambda kv: kv[0])
        else:
            ungrouped.extend(items)

    ungrouped.sort(key=lambda kv: kv[0])
    return SortResult(grouped=grouped, ungrouped=ungrouped)


def render_sorted(
    result: SortResult,
    show_prefix_headers: bool = True,
) -> str:
    """Render a SortResult as a plain-text .env-style block."""
    lines: List[str] = []

    for prefix, items in result.grouped.items():
        if show_prefix_headers:
            lines.append(f"# [{prefix}]")
        for key, value in items:
            lines.append(f"{key}={value}")
        lines.append("")

    if result.ungrouped:
        if show_prefix_headers and result.grouped:
            lines.append("# [other]")
        for key, value in result.ungrouped:
            lines.append(f"{key}={value}")

    return "\n".join(lines)
