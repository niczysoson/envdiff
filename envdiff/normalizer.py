"""Normalize .env values for consistent comparison (trim whitespace, unify booleans, etc.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)


def _normalize_bool(value: str) -> str:
    """Unify boolean-like strings to 'true' or 'false'."""
    lower = value.lower()
    if lower in _BOOL_TRUE:
        return "true"
    if lower in _BOOL_FALSE:
        return "false"
    return value


def _normalize_value(value: str) -> str:
    """Apply all normalization rules to a single value."""
    value = value.strip()
    value = _normalize_bool(value)
    return value


def normalize_env(env: Dict[str, str]) -> NormalizeResult:
    """Return a NormalizeResult with normalized values and a log of what changed."""
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, original_value in env.items():
        new_value = _normalize_value(original_value)
        normalized[key] = new_value
        if new_value != original_value:
            changes.append((key, original_value, new_value))

    return NormalizeResult(original=dict(env), normalized=normalized, changes=changes)


def format_normalize_report(result: NormalizeResult, *, color: bool = False) -> str:
    """Render a human-readable report of normalization changes."""
    if not result.has_changes:
        return "No normalization changes."

    lines: List[str] = [f"Normalized {len(result.changes)} value(s):\n"]
    for key, before, after in result.changes:
        entry = f"  {key}: {before!r} -> {after!r}"
        if color:
            entry = f"\033[33m{entry}\033[0m"
        lines.append(entry)
    return "\n".join(lines)
