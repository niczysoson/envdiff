"""Parser for .env files.

Handles reading and parsing of .env files into key-value dictionaries,
supporting comments, blank lines, quoted values, and inline comments.
"""

import re
from pathlib import Path
from typing import Dict


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)


def _strip_inline_comment(value: str) -> str:
    """Remove inline comments from an unquoted value."""
    idx = value.find(" #")
    if idx != -1:
        return value[:idx].strip()
    return value.strip()


def _unquote(value: str) -> str:
    """Strip surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        A dictionary mapping variable names to their string values.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    env_vars: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")

            # Skip blank lines and full-line comments
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                continue

            key = match.group("key")
            raw_value = match.group("value").strip()

            if raw_value and raw_value[0] in ('"', "'"):
                value = _unquote(raw_value)
            else:
                value = _strip_inline_comment(raw_value)

            env_vars[key] = value

    return env_vars
