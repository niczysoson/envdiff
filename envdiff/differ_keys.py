"""Key-focused diff: report only on key presence, ignoring values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class KeyDiffResult:
    source_file: str
    target_file: str
    only_in_source: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    in_both: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target)

    @property
    def total_source(self) -> int:
        return len(self.only_in_source) + len(self.in_both)

    @property
    def total_target(self) -> int:
        return len(self.only_in_target) + len(self.in_both)


def diff_keys(
    source: Dict[str, str],
    target: Dict[str, str],
    source_file: str = "source",
    target_file: str = "target",
) -> KeyDiffResult:
    """Compare two env dicts by keys only; values are irrelevant."""
    source_keys: Set[str] = set(source)
    target_keys: Set[str] = set(target)

    return KeyDiffResult(
        source_file=source_file,
        target_file=target_file,
        only_in_source=sorted(source_keys - target_keys),
        only_in_target=sorted(target_keys - source_keys),
        in_both=sorted(source_keys & target_keys),
    )


def format_key_diff_report(result: KeyDiffResult, *, color: bool = False) -> str:
    """Render a human-readable key-diff report."""

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: List[str] = [
        f"Key diff: {result.source_file} vs {result.target_file}",
        f"  Keys in source : {result.total_source}",
        f"  Keys in target : {result.total_target}",
        f"  Shared keys    : {len(result.in_both)}",
    ]

    if result.only_in_source:
        lines.append(_c("\nOnly in source:", "33"))
        for k in result.only_in_source:
            lines.append(f"  - {k}")

    if result.only_in_target:
        lines.append(_c("\nOnly in target:", "36"))
        for k in result.only_in_target:
            lines.append(f"  + {k}")

    if not result.has_differences:
        lines.append(_c("\nKey sets are identical.", "32"))

    return "\n".join(lines)
