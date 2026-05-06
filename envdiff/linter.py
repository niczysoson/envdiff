"""Lint .env files for common style and correctness issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Patterns that indicate a suspicious or problematic value
_PLACEHOLDER_PATTERNS = ("changeme", "todo", "fixme", "placeholder", "xxx", "your_", "<", ">")


@dataclass
class LintResult:
    blank_values: List[str] = field(default_factory=list)
    placeholder_values: Dict[str, str] = field(default_factory=dict)
    duplicate_keys: List[str] = field(default_factory=list)
    invalid_key_names: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(
            self.blank_values
            or self.placeholder_values
            or self.duplicate_keys
            or self.invalid_key_names
        )


def _is_valid_key(key: str) -> bool:
    """Keys must start with a letter or underscore and contain only alphanumerics/underscores."""
    if not key:
        return False
    if not (key[0].isalpha() or key[0] == "_"):
        return False
    return all(c.isalnum() or c == "_" for c in key)


def _is_placeholder(value: str) -> bool:
    lower = value.lower()
    return any(p in lower for p in _PLACEHOLDER_PATTERNS)


def lint_env(env: Dict[str, str], raw_lines: List[str] | None = None) -> LintResult:
    """Lint a parsed env dict and return a LintResult."""
    result = LintResult()

    # Detect duplicate keys from raw lines if provided
    if raw_lines is not None:
        seen_keys: Dict[str, int] = {}
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                seen_keys[key] = seen_keys.get(key, 0) + 1
        result.duplicate_keys = [k for k, count in seen_keys.items() if count > 1]

    for key, value in env.items():
        if not _is_valid_key(key):
            result.invalid_key_names.append(key)
        if value == "":
            result.blank_values.append(key)
        elif _is_placeholder(value):
            result.placeholder_values[key] = value

    return result


def format_lint_report(result: LintResult, color: bool = True) -> str:
    """Format a LintResult into a human-readable string."""
    if not result.has_issues:
        prefix = "\033[32m" if color else ""
        suffix = "\033[0m" if color else ""
        return f"{prefix}No lint issues found.{suffix}\n"

    warn = ("\033[33m" if color else "", "\033[0m" if color else "")
    lines = []

    if result.invalid_key_names:
        lines.append(f"{warn[0]}Invalid key names:{warn[1]}")
        for k in sorted(result.invalid_key_names):
            lines.append(f"  - {k}")

    if result.duplicate_keys:
        lines.append(f"{warn[0]}Duplicate keys:{warn[1]}")
        for k in sorted(result.duplicate_keys):
            lines.append(f"  - {k}")

    if result.blank_values:
        lines.append(f"{warn[0]}Blank values:{warn[1]}")
        for k in sorted(result.blank_values):
            lines.append(f"  - {k}")

    if result.placeholder_values:
        lines.append(f"{warn[0]}Placeholder values:{warn[1]}")
        for k, v in sorted(result.placeholder_values.items()):
            lines.append(f"  - {k}={v}")

    return "\n".join(lines) + "\n"
