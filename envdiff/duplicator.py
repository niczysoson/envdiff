"""Detect and report duplicate values across keys in a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    """Result of a duplicate-value scan."""

    # Maps each value to the list of keys that share it
    value_to_keys: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def duplicates(self) -> Dict[str, List[str]]:
        """Return only values that appear more than once."""
        return {v: keys for v, keys in self.value_to_keys.items() if len(keys) > 1}

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)


def find_duplicates(env: Dict[str, str]) -> DuplicateResult:
    """Group keys by their value and return a DuplicateResult."""
    value_to_keys: Dict[str, List[str]] = {}
    for key, value in env.items():
        value_to_keys.setdefault(value, []).append(key)
    return DuplicateResult(value_to_keys=value_to_keys)


def format_duplicate_report(result: DuplicateResult, *, color: bool = False) -> str:
    """Render a human-readable report of duplicate values."""
    if not result.has_duplicates:
        return "No duplicate values found."

    lines: List[str] = []
    for value, keys in sorted(result.duplicates.items()):
        display_value = repr(value) if value else "(empty)"
        header = f"Value {display_value} shared by:"
        if color:
            header = f"\033[33m{header}\033[0m"
        lines.append(header)
        for key in sorted(keys):
            lines.append(f"  - {key}")
    return "\n".join(lines)
