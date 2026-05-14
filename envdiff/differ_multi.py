"""Multi-file diff: compare one source env against multiple targets at once."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.differ import DiffResult, diff_envs


@dataclass
class MultiDiffEntry:
    label: str
    result: DiffResult


@dataclass
class MultiDiffResult:
    source_file: str
    entries: List[MultiDiffEntry] = field(default_factory=list)

    def any_differences(self) -> bool:
        return any(e.result.missing_in_target or e.result.missing_in_source or e.result.mismatched
                   for e in self.entries)

    def labels_with_differences(self) -> List[str]:
        return [
            e.label for e in self.entries
            if e.result.missing_in_target or e.result.missing_in_source or e.result.mismatched
        ]


def diff_one_to_many(
    source: Dict[str, str],
    targets: List[Tuple[str, Dict[str, str]]],
    source_file: str = "<source>",
) -> MultiDiffResult:
    """Diff *source* against each (label, env) pair in *targets*."""
    result = MultiDiffResult(source_file=source_file)
    for label, target_env in targets:
        dr = diff_envs(source, target_env)
        result.entries.append(MultiDiffEntry(label=label, result=dr))
    return result


def format_multi_diff_report(mdr: MultiDiffResult, color: bool = False) -> str:
    """Return a human-readable summary of a MultiDiffResult."""
    lines: List[str] = []
    lines.append(f"Source: {mdr.source_file}")
    lines.append(f"Targets checked: {len(mdr.entries)}")
    if not mdr.any_differences():
        lines.append("All targets match source.")
        return "\n".join(lines)

    for entry in mdr.entries:
        r = entry.result
        if not (r.missing_in_target or r.missing_in_source or r.mismatched):
            lines.append(f"  [{entry.label}] OK")
            continue
        lines.append(f"  [{entry.label}]")
        for k in sorted(r.missing_in_target):
            lines.append(f"    MISSING IN TARGET : {k}")
        for k in sorted(r.missing_in_source):
            lines.append(f"    MISSING IN SOURCE : {k}")
        for k, (sv, tv) in sorted(r.mismatched.items()):
            lines.append(f"    MISMATCH          : {k} ({sv!r} vs {tv!r})")
    return "\n".join(lines)
