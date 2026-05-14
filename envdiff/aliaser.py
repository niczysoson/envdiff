"""aliaser.py — map environment variable keys to canonical aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class AliasResult:
    env: Dict[str, str]
    applied: List[Tuple[str, str]]   # (original_key, alias_key)
    skipped: List[str]               # alias targets that already existed
    unknown: List[str]               # alias sources not found in env


def has_changes(result: AliasResult) -> bool:
    return bool(result.applied)


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    overwrite: bool = False,
) -> AliasResult:
    """Return a new env dict with alias keys added (or replaced).

    Args:
        env:       Original key→value mapping.
        aliases:   Mapping of original_key → alias_key.
        overwrite: If True, overwrite alias_key even when it already exists.
    """
    out = dict(env)
    applied: List[Tuple[str, str]] = []
    skipped: List[str] = []
    unknown: List[str] = []

    for src, dst in aliases.items():
        if src not in env:
            unknown.append(src)
            continue
        if dst in out and not overwrite:
            skipped.append(dst)
            continue
        out[dst] = env[src]
        applied.append((src, dst))

    return AliasResult(env=out, applied=applied, skipped=skipped, unknown=unknown)


def format_alias_report(result: AliasResult, *, color: bool = False) -> str:
    """Render a human-readable alias report."""
    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: List[str] = []
    if result.applied:
        lines.append(_c("Aliases applied:", "1"))
        for src, dst in result.applied:
            lines.append(f"  {src} -> {dst}")
    if result.skipped:
        lines.append(_c("Skipped (already exist):", "33"))
        for key in result.skipped:
            lines.append(f"  {key}")
    if result.unknown:
        lines.append(_c("Unknown source keys:", "31"))
        for key in result.unknown:
            lines.append(f"  {key}")
    if not lines:
        lines.append("No aliases to apply.")
    return "\n".join(lines)
