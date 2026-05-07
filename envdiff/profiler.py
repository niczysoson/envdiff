"""Profile .env files: count keys, detect empty values, estimate complexity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    source_file: str
    total_keys: int
    empty_keys: List[str]
    placeholder_keys: List[str]
    numeric_value_keys: List[str]
    boolean_value_keys: List[str]
    long_value_keys: List[str]  # values > 100 chars
    key_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    @property
    def placeholder_count(self) -> int:
        return len(self.placeholder_keys)

    @property
    def complexity_score(self) -> int:
        """Rough complexity: penalise empties/placeholders, reward diversity."""
        return (
            self.total_keys
            - self.empty_count
            - self.placeholder_count
            + len(self.numeric_value_keys)
            + len(self.boolean_value_keys)
        )


_PLACEHOLDERS = {"changeme", "todo", "fixme", "your_value", "xxx", "<value>", "<secret>"}
_BOOLEANS = {"true", "false", "yes", "no", "1", "0", "on", "off"}


def _is_placeholder(value: str) -> bool:
    return value.lower() in _PLACEHOLDERS or value.startswith("<") and value.endswith(">")


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def profile_env(env: Dict[str, str], source_file: str = "") -> ProfileResult:
    """Analyse *env* dict and return a :class:`ProfileResult`."""
    empty: List[str] = []
    placeholders: List[str] = []
    numeric: List[str] = []
    boolean: List[str] = []
    long_vals: List[str] = []
    lengths: Dict[str, int] = {}

    for key, value in env.items():
        lengths[key] = len(key)
        if value == "":
            empty.append(key)
        elif _is_placeholder(value):
            placeholders.append(key)
        if _is_numeric(value):
            numeric.append(key)
        if value.lower() in _BOOLEANS:
            boolean.append(key)
        if len(value) > 100:
            long_vals.append(key)

    return ProfileResult(
        source_file=source_file,
        total_keys=len(env),
        empty_keys=sorted(empty),
        placeholder_keys=sorted(placeholders),
        numeric_value_keys=sorted(numeric),
        boolean_value_keys=sorted(boolean),
        long_value_keys=sorted(long_vals),
        key_lengths=lengths,
    )
