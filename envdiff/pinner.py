"""Pin current env variable values as a baseline for drift detection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinResult:
    source_file: str
    pinned: Dict[str, str] = field(default_factory=dict)
    drifted: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)


def has_drift(result: PinResult) -> bool:
    """Return True if any drift was detected against the pinned baseline."""
    return bool(result.drifted or result.added or result.removed)


def pin_env(env: Dict[str, str], source_file: str = "") -> PinResult:
    """Create a fresh pin from the given env dict."""
    return PinResult(
        source_file=source_file,
        pinned=dict(env),
    )


def diff_against_pin(
    current: Dict[str, str],
    baseline: Dict[str, str],
    source_file: str = "",
    ignore_keys: Optional[List[str]] = None,
) -> PinResult:
    """Compare *current* env against a previously pinned *baseline*.

    Returns a PinResult describing keys that drifted (value changed),
    were added (present in current but not baseline), or removed (present
    in baseline but missing from current).
    """
    ignore = set(ignore_keys or [])
    current_keys = set(current) - ignore
    baseline_keys = set(baseline) - ignore

    drifted: List[str] = [
        k for k in current_keys & baseline_keys if current[k] != baseline[k]
    ]
    added: List[str] = sorted(current_keys - baseline_keys)
    removed: List[str] = sorted(baseline_keys - current_keys)

    return PinResult(
        source_file=source_file,
        pinned=dict(baseline),
        drifted=sorted(drifted),
        added=added,
        removed=removed,
    )


def format_pin_report(result: PinResult, color: bool = False) -> str:
    """Render a human-readable drift report."""

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: List[str] = [f"Pin report: {result.source_file or '(unknown)'}"]

    if not has_drift(result):
        lines.append(_c("  No drift detected.", "32"))
        return "\n".join(lines)

    if result.drifted:
        lines.append(_c("  Drifted keys:", "33"))
        for k in result.drifted:
            lines.append(f"    - {k}")

    if result.added:
        lines.append(_c("  Added keys (not in baseline):", "34"))
        for k in result.added:
            lines.append(f"    + {k}")

    if result.removed:
        lines.append(_c("  Removed keys (missing from current):", "31"))
        for k in result.removed:
            lines.append(f"    x {k}")

    return "\n".join(lines)
