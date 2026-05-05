"""Core diffing logic for comparing parsed .env files."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Result of comparing two .env files."""

    missing_in_target: List[str] = field(default_factory=list)
    missing_in_source: List[str] = field(default_factory=list)
    mismatched: Dict[str, tuple] = field(default_factory=dict)
    matching: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_target or self.missing_in_source or self.mismatched
        )

    def summary(self) -> str:
        lines = []
        if self.missing_in_target:
            lines.append(f"Missing in target ({len(self.missing_in_target)}): {', '.join(sorted(self.missing_in_target))}")
        if self.missing_in_source:
            lines.append(f"Missing in source ({len(self.missing_in_source)}): {', '.join(sorted(self.missing_in_source))}")
        if self.mismatched:
            lines.append(f"Mismatched ({len(self.mismatched)}): {', '.join(sorted(self.mismatched.keys()))}")
        if not lines:
            return "No differences found."
        return "\n".join(lines)


def diff_envs(
    source: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    ignore_values: bool = False,
) -> DiffResult:
    """Compare two parsed env dicts and return a DiffResult.

    Args:
        source: Parsed env dict treated as the reference.
        target: Parsed env dict to compare against source.
        ignore_values: If True, only check key presence, not values.

    Returns:
        DiffResult describing all differences.
    """
    source_keys: Set[str] = set(source.keys())
    target_keys: Set[str] = set(target.keys())

    result = DiffResult()
    result.missing_in_target = sorted(source_keys - target_keys)
    result.missing_in_source = sorted(target_keys - source_keys)

    common_keys = source_keys & target_keys
    for key in sorted(common_keys):
        src_val = source[key]
        tgt_val = target[key]
        if not ignore_values and src_val != tgt_val:
            result.mismatched[key] = (src_val, tgt_val)
        else:
            result.matching.append(key)

    return result
