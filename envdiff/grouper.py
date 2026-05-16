"""Group environment variables by a shared prefix or custom tag map."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)


def _extract_prefix(key: str, delimiter: str = "_") -> Optional[str]:
    """Return the portion of *key* before the first *delimiter*, or None."""
    if delimiter in key:
        prefix, rest = key.split(delimiter, 1)
        if prefix and rest:
            return prefix
    return None


def group_by_prefix(
    env: Dict[str, str],
    delimiter: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group keys by their prefix (text before *delimiter*).

    Keys whose prefix group has fewer than *min_group_size* members are
    placed in ``ungrouped``.
    """
    buckets: Dict[str, List[str]] = {}
    for key in env:
        prefix = _extract_prefix(key, delimiter)
        if prefix:
            buckets.setdefault(prefix, []).append(key)
        else:
            buckets.setdefault(None, []).append(key)  # type: ignore[arg-type]

    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = list(buckets.pop(None, []))

    for prefix, keys in buckets.items():
        if len(keys) >= min_group_size:
            groups[prefix] = sorted(keys)
        else:
            ungrouped.extend(keys)

    return GroupResult(groups=groups, ungrouped=sorted(ungrouped))


def group_by_map(
    env: Dict[str, str],
    tag_map: Dict[str, str],
) -> GroupResult:
    """Group keys according to an explicit *tag_map* of ``{key: group_name}``.

    Keys absent from *tag_map* are placed in ``ungrouped``.
    """
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in env:
        tag = tag_map.get(key)
        if tag:
            groups.setdefault(tag, []).append(key)
        else:
            ungrouped.append(key)

    return GroupResult(
        groups={g: sorted(keys) for g, keys in groups.items()},
        ungrouped=sorted(ungrouped),
    )


def format_group_report(result: GroupResult, *, color: bool = False) -> str:
    """Return a human-readable report of grouped keys."""
    lines: List[str] = []

    def _h(text: str) -> str:
        return f"\033[1m{text}\033[0m" if color else text

    for group, keys in sorted(result.groups.items()):
        lines.append(_h(f"[{group}]"))
        for k in keys:
            lines.append(f"  {k}")

    if result.ungrouped:
        lines.append(_h("[ungrouped]"))
        for k in result.ungrouped:
            lines.append(f"  {k}")

    return "\n".join(lines)
