"""Patch an .env file by applying a set of key-value overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchResult:
    original: Dict[str, str]
    patched: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)


def has_changes(result: PatchResult) -> bool:
    """Return True if any patches were applied or keys were added."""
    return bool(result.applied or result.added)


def patch_env(
    env: Dict[str, str],
    overrides: Dict[str, str],
    *,
    add_missing: bool = True,
    skip_existing: bool = False,
) -> PatchResult:
    """Apply *overrides* to *env* and return a PatchResult.

    Parameters
    ----------
    env:          The source environment mapping.
    overrides:    Key/value pairs to apply.
    add_missing:  When True, keys absent from *env* are added.
    skip_existing: When True, existing keys are not overwritten.
    """
    patched = dict(env)
    applied: List[str] = []
    skipped: List[str] = []
    added: List[str] = []

    for key, value in overrides.items():
        if key in patched:
            if skip_existing:
                skipped.append(key)
            else:
                patched[key] = value
                applied.append(key)
        else:
            if add_missing:
                patched[key] = value
                added.append(key)
            else:
                skipped.append(key)

    return PatchResult(
        original=dict(env),
        patched=patched,
        applied=applied,
        skipped=skipped,
        added=added,
    )


def render_patch_report(result: PatchResult, *, color: bool = False) -> str:
    """Return a human-readable summary of a PatchResult."""
    lines: List[str] = []

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    if result.applied:
        lines.append(_c("Updated keys:", "33"))
        for k in sorted(result.applied):
            lines.append(f"  ~ {k}")

    if result.added:
        lines.append(_c("Added keys:", "32"))
        for k in sorted(result.added):
            lines.append(f"  + {k}")

    if result.skipped:
        lines.append(_c("Skipped keys:", "90"))
        for k in sorted(result.skipped):
            lines.append(f"  - {k}")

    if not lines:
        lines.append("No changes applied.")

    return "\n".join(lines)
