"""Multi-file comparator: diff one source env against multiple targets at once."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import DiffResult, diff_envs


@dataclass
class CompareResult:
    source_file: str
    results: Dict[str, DiffResult] = field(default_factory=dict)

    @property
    def target_files(self) -> List[str]:
        return list(self.results.keys())

    @property
    def any_differences(self) -> bool:
        return any(r.missing_in_target or r.missing_in_source or r.mismatched
                   for r in self.results.values())


def compare_many(
    source: Dict[str, str],
    targets: Dict[str, Dict[str, str]],
    source_file: str = "<source>",
) -> CompareResult:
    """Diff *source* against every env in *targets*.

    Args:
        source: Parsed key/value mapping for the source env.
        targets: Mapping of label -> parsed key/value mapping for each target.
        source_file: Display name for the source file.

    Returns:
        A :class:`CompareResult` collecting one :class:`DiffResult` per target.
    """
    result = CompareResult(source_file=source_file)
    for label, target_env in targets.items():
        result.results[label] = diff_envs(source, target_env)
    return result


def summary_table(compare: CompareResult) -> List[str]:
    """Return a list of human-readable summary lines, one per target."""
    lines: List[str] = []
    for label, diff in compare.results.items():
        missing = len(diff.missing_in_target)
        extra = len(diff.missing_in_source)
        mismatch = len(diff.mismatched)
        lines.append(
            f"{label}: -{missing} missing, +{extra} extra, ~{mismatch} mismatched"
        )
    return lines
