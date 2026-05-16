"""freezer.py — freeze an env snapshot to a canonical, sorted, redacted export."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.redactor import _key_is_sensitive

_REDACTED = "***"


@dataclass
class FreezeResult:
    source: str
    keys: List[str] = field(default_factory=list)
    frozen: Dict[str, str] = field(default_factory=dict)
    redacted_keys: List[str] = field(default_factory=list)


def freeze_env(
    env: Dict[str, str],
    source: str = "<unknown>",
    redact: bool = True,
    extra_patterns: Optional[List[str]] = None,
    sort: bool = True,
) -> FreezeResult:
    """Return a FreezeResult with an optionally redacted, optionally sorted snapshot."""
    keys = sorted(env.keys()) if sort else list(env.keys())
    frozen: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key in keys:
        value = env[key]
        if redact and _key_is_sensitive(key, extra_patterns or []):
            frozen[key] = _REDACTED
            redacted_keys.append(key)
        else:
            frozen[key] = value

    return FreezeResult(
        source=source,
        keys=keys,
        frozen=frozen,
        redacted_keys=redacted_keys,
    )


def format_freeze_report(result: FreezeResult, color: bool = False) -> str:
    """Render a human-readable freeze report."""

    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    lines: List[str] = [
        _c(f"Frozen: {result.source}", "1"),
        f"  Total keys   : {len(result.keys)}",
        f"  Redacted keys: {len(result.redacted_keys)}",
    ]

    if result.redacted_keys:
        lines.append(_c("  Redacted:", "33"))
        for k in result.redacted_keys:
            lines.append(f"    - {k}")

    lines.append("")
    lines.append(_c("  Values:", "36"))
    for key in result.keys:
        val = result.frozen[key]
        lines.append(f"    {key}={val}")

    return "\n".join(lines)
