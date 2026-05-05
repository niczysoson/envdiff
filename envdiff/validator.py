"""Validation utilities for envdiff: check required keys and value patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationResult:
    """Holds the outcome of validating an env mapping against a schema."""

    missing_required: List[str] = field(default_factory=list)
    pattern_violations: Dict[str, str] = field(default_factory=dict)  # key -> value

    @property
    def is_valid(self) -> bool:
        return not self.missing_required and not self.pattern_violations


def validate_env(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    patterns: Optional[Dict[str, str]] = None,
) -> ValidationResult:
    """Validate *env* against optional required-key and regex-pattern rules.

    Args:
        env: Parsed environment mapping (key -> value).
        required_keys: Keys that must be present in *env*.
        patterns: Mapping of key -> regex pattern.  If the key exists in *env*
                  its value must fully match the given pattern.

    Returns:
        A :class:`ValidationResult` describing any violations found.
    """
    result = ValidationResult()

    if required_keys:
        for key in required_keys:
            if key not in env:
                result.missing_required.append(key)

    if patterns:
        for key, pattern in patterns.items():
            if key in env:
                value = env[key]
                if not re.fullmatch(pattern, value):
                    result.pattern_violations[key] = value

    return result


def format_validation_report(result: ValidationResult, *, color: bool = True) -> str:
    """Return a human-readable string describing *result*."""
    if result.is_valid:
        return "Validation passed."

    lines: List[str] = []

    if result.missing_required:
        header = "Missing required keys:"
        if color:
            header = f"\033[1;31m{header}\033[0m"
        lines.append(header)
        for key in sorted(result.missing_required):
            lines.append(f"  - {key}")

    if result.pattern_violations:
        header = "Pattern violations:"
        if color:
            header = f"\033[1;33m{header}\033[0m"
        lines.append(header)
        for key in sorted(result.pattern_violations):
            value = result.pattern_violations[key]
            lines.append(f"  - {key}={value!r}")

    return "\n".join(lines)
