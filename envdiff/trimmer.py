"""Trimmer: remove unused or stale keys from an env file given a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)


def has_removals(result: TrimResult) -> bool:
    """Return True when at least one key was removed."""
    return bool(result.removed_keys)


def trim_env(
    env: Dict[str, str],
    reference: Dict[str, str],
    *,
    keep_extra: bool = False,
) -> TrimResult:
    """Remove keys from *env* that are absent from *reference*.

    Parameters
    ----------
    env:
        The environment mapping to trim.
    reference:
        The authoritative set of keys (values are ignored).
    keep_extra:
        When True, keys not in *reference* are kept; the result will then
        have an empty ``removed_keys`` list.
    """
    if keep_extra:
        return TrimResult(original=dict(env), trimmed=dict(env), removed_keys=[])

    ref_keys = set(reference.keys())
    trimmed = {k: v for k, v in env.items() if k in ref_keys}
    removed = sorted(k for k in env if k not in ref_keys)
    return TrimResult(original=dict(env), trimmed=trimmed, removed_keys=removed)


def format_trim_report(result: TrimResult, *, color: bool = False) -> str:
    """Return a human-readable trim report."""

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: List[str] = []
    if not has_removals(result):
        lines.append(_c("No stale keys found.", "32"))
        return "\n".join(lines)

    lines.append(_c(f"Removed {len(result.removed_keys)} stale key(s):", "33"))
    for key in result.removed_keys:
        lines.append(f"  {_c('-', '31')} {key}")
    return "\n".join(lines)
