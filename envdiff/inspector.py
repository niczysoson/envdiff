"""Inspector: analyze a single .env file and report key statistics and anomalies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class InspectResult:
    source: str
    total: int
    empty_keys: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)
    numeric_only_values: List[str] = field(default_factory=list)
    boolean_like_values: List[str] = field(default_factory=list)

    @property
    def has_anomalies(self) -> bool:
        return bool(
            self.empty_keys
            or self.duplicate_keys
            or self.long_values
            or self.numeric_only_values
            or self.boolean_like_values
        )


_BOOLEAN_LIKE = {"true", "false", "yes", "no", "1", "0", "on", "off"}
_LONG_VALUE_THRESHOLD = 128


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def inspect_env(env: Dict[str, str], source: str = "<unknown>") -> InspectResult:
    """Inspect a parsed env dict and return an InspectResult with anomaly details."""
    empty: List[str] = []
    long_vals: List[str] = []
    numeric: List[str] = []
    boolean_like: List[str] = []

    for key, value in env.items():
        if value == "":
            empty.append(key)
        elif len(value) > _LONG_VALUE_THRESHOLD:
            long_vals.append(key)
        elif _is_numeric(value):
            numeric.append(key)
        elif value.lower() in _BOOLEAN_LIKE:
            boolean_like.append(key)

    return InspectResult(
        source=source,
        total=len(env),
        empty_keys=sorted(empty),
        duplicate_keys=[],  # duplicates resolved at parse time; tracked separately
        long_values=sorted(long_vals),
        numeric_only_values=sorted(numeric),
        boolean_like_values=sorted(boolean_like),
    )


def format_inspect_report(result: InspectResult, *, color: bool = False) -> str:
    """Render a human-readable inspection report."""
    lines: List[str] = []
    lines.append(f"Inspection report for: {result.source}")
    lines.append(f"  Total keys : {result.total}")

    def _section(title: str, keys: List[str]) -> None:
        if keys:
            lines.append(f"  {title}:")
            for k in keys:
                lines.append(f"    - {k}")

    _section("Empty values", result.empty_keys)
    _section("Long values (>{} chars)".format(_LONG_VALUE_THRESHOLD), result.long_values)
    _section("Numeric-only values", result.numeric_only_values)
    _section("Boolean-like values", result.boolean_like_values)

    if not result.has_anomalies:
        lines.append("  No anomalies detected.")

    return "\n".join(lines)
