"""Tests for envdiff.parser module."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file, _strip_inline_comment, _unquote


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

def test_strip_inline_comment_removes_comment():
    assert _strip_inline_comment("my_value # this is a comment") == "my_value"


def test_strip_inline_comment_no_comment():
    assert _strip_inline_comment("my_value") == "my_value"


def test_unquote_double_quotes():
    assert _unquote('"hello world"') == "hello world"


def test_unquote_single_quotes():
    assert _unquote("'hello world'") == "hello world"


def test_unquote_no_quotes():
    assert _unquote("hello") == "hello"


# ---------------------------------------------------------------------------
# Integration tests using temporary .env files
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path):
    """Factory fixture that writes content to a temp .env file."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p
    return _write


def test_parse_simple_key_value(env_file):
    path = env_file("""
        APP_ENV=production
        DEBUG=false
    """)
    result = parse_env_file(path)
    assert result == {"APP_ENV": "production", "DEBUG": "false"}


def test_parse_skips_comments_and_blank_lines(env_file):
    path = env_file("""
        # This is a comment

        KEY=value
    """)
    result = parse_env_file(path)
    assert result == {"KEY": "value"}


def test_parse_quoted_values(env_file):
    path = env_file("""
        GREETING="hello world"
        SALUTATION='hi there'
    """)
    result = parse_env_file(path)
    assert result["GREETING"] == "hello world"
    assert result["SALUTATION"] == "hi there"


def test_parse_inline_comment_stripped(env_file):
    path = env_file("""
        PORT=8080 # default port
    """)
    result = parse_env_file(path)
    assert result["PORT"] == "8080"


def test_parse_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_parse_empty_value(env_file):
    path = env_file("EMPTY_VAR=\n")
    result = parse_env_file(path)
    assert result["EMPTY_VAR"] == ""


def test_parse_export_prefix_stripped(env_file):
    """Lines starting with 'export ' should have the prefix stripped."""
    path = env_file("""
        export APP_ENV=staging
        export SECRET_KEY="abc123"
    """)
    result = parse_env_file(path)
    assert result == {"APP_ENV": "staging", "SECRET_KEY": "abc123"}
