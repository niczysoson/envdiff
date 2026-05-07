"""Redactor module: mask sensitive values in env dicts before output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r"(?i)secret",
    r"(?i)password",
    r"(?i)passwd",
    r"(?i)token",
    r"(?i)api_key",
    r"(?i)private_key",
    r"(?i)auth",
    r"(?i)credential",
]

DEFAULT_MASK = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)


def _key_is_sensitive(key: str, patterns: List[str]) -> bool:
    """Return True if *key* matches any of the given regex patterns."""
    return any(re.search(p, key) for p in patterns)


def redact_env(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
    keep_keys: Optional[List[str]] = None,
) -> RedactResult:
    """Return a RedactResult where sensitive values are replaced with *mask*.

    Args:
        env: Parsed env dict to redact.
        extra_patterns: Additional regex patterns to flag as sensitive.
        mask: Replacement string for sensitive values.
        keep_keys: Explicit list of keys that must never be redacted.
    """
    patterns = _DEFAULT_SENSITIVE_PATTERNS + (extra_patterns or [])
    keep = set(keep_keys or [])
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if key not in keep and _key_is_sensitive(key, patterns):
            redacted[key] = mask
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )
