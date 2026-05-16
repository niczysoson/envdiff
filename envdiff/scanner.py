"""Scanner: detect duplicate keys and suspicious patterns in .env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScanResult:
    duplicates: Dict[str, int] = field(default_factory=dict)  # key -> count
    suspicious: List[str] = field(default_factory=list)       # keys with suspicious values
    source_file: str = ""


_SUSPICIOUS_PATTERNS = (
    "changeme",
    "todo",
    "fixme",
    "example",
    "test",
    "dummy",
    "fake",
    "replace",
)


def has_issues(result: ScanResult) -> bool:
    """Return True if the scan found any duplicates or suspicious values."""
    return bool(result.duplicates) or bool(result.suspicious)


def _is_suspicious(value: str) -> bool:
    """Return True if the value looks like a placeholder or reminder."""
    lower = value.strip().lower()
    return any(pat in lower for pat in _SUSPICIOUS_PATTERNS)


def format_report(result: ScanResult) -> str:
    """Return a human-readable summary of a ScanResult.

    Example output::

        File: .env
        Duplicates: FOO (2x), BAR (3x)
        Suspicious values: SECRET, TOKEN
    """
    lines: List[str] = []
    header = f"File: {result.source_file}" if result.source_file else "File: <unknown>"
    lines.append(header)

    if result.duplicates:
        dup_parts = ", ".join(f"{k} ({v}x)" for k, v in result.duplicates.items())
        lines.append(f"Duplicates: {dup_parts}")
    else:
        lines.append("Duplicates: none")

    if result.suspicious:
        lines.append(f"Suspicious values: {', '.join(result.suspicious)}")
    else:
        lines.append("Suspicious values: none")

    return "\n".join(lines)


def scan_env_file(lines: List[str], source_file: str = "") -> ScanResult:
    """Scan raw lines from a .env file for duplicate keys and suspicious values."""
    key_counts: Dict[str, int] = {}
    suspicious: List[str] = []

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        key_counts[key] = key_counts.get(key, 0) + 1
        if _is_suspicious(value):
            suspicious.append(key)

    duplicates = {k: v for k, v in key_counts.items() if v > 1}
    return ScanResult(
        duplicates=duplicates,
        suspicious=list(dict.fromkeys(suspicious)),  # preserve order, deduplicate
        source_file=source_file,
    )
