"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import (
    NormalizeResult,
    _normalize_bool,
    _normalize_value,
    normalize_env,
    format_normalize_report,
)


# ---------------------------------------------------------------------------
# _normalize_bool
# ---------------------------------------------------------------------------


def test_normalize_bool_true_variants():
    for v in ("true", "True", "TRUE", "yes", "Yes", "1", "on", "ON"):
        assert _normalize_bool(v) == "true", f"Expected 'true' for {v!r}"


def test_normalize_bool_false_variants():
    for v in ("false", "False", "FALSE", "no", "No", "0", "off", "OFF"):
        assert _normalize_bool(v) == "false", f"Expected 'false' for {v!r}"


def test_normalize_bool_passthrough():
    assert _normalize_bool("hello") == "hello"
    assert _normalize_bool("") == ""
    assert _normalize_bool("maybe") == "maybe"


# ---------------------------------------------------------------------------
# _normalize_value
# ---------------------------------------------------------------------------


def test_normalize_value_strips_whitespace():
    assert _normalize_value("  hello  ") == "hello"


def test_normalize_value_strips_and_normalizes_bool():
    assert _normalize_value("  YES  ") == "true"


def test_normalize_value_plain_string_unchanged():
    assert _normalize_value("postgres") == "postgres"


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_env():
    return {
        "DEBUG": "True",
        "RETRIES": "3",
        "HOST": "  localhost  ",
        "ENABLED": "yes",
        "NAME": "myapp",
    }


def test_normalize_env_returns_normalize_result(sample_env):
    result = normalize_env(sample_env)
    assert isinstance(result, NormalizeResult)


def test_normalize_env_has_changes(sample_env):
    result = normalize_env(sample_env)
    assert result.has_changes


def test_normalize_env_bool_normalized(sample_env):
    result = normalize_env(sample_env)
    assert result.normalized["DEBUG"] == "true"
    assert result.normalized["ENABLED"] == "true"


def test_normalize_env_whitespace_stripped(sample_env):
    result = normalize_env(sample_env)
    assert result.normalized["HOST"] == "localhost"


def test_normalize_env_unchanged_keys_preserved(sample_env):
    result = normalize_env(sample_env)
    assert result.normalized["RETRIES"] == "3"
    assert result.normalized["NAME"] == "myapp"


def test_normalize_env_original_untouched(sample_env):
    result = normalize_env(sample_env)
    assert result.original["DEBUG"] == "True"
    assert result.original["HOST"] == "  localhost  "


def test_normalize_env_no_changes_when_already_clean():
    env = {"KEY": "value", "OTHER": "false"}
    result = normalize_env(env)
    assert not result.has_changes


def test_normalize_env_changes_list_entries(sample_env):
    result = normalize_env(sample_env)
    changed_keys = {c[0] for c in result.changes}
    assert "DEBUG" in changed_keys
    assert "HOST" in changed_keys
    assert "NAME" not in changed_keys


# ---------------------------------------------------------------------------
# format_normalize_report
# ---------------------------------------------------------------------------


def test_format_report_no_changes():
    env = {"A": "value"}
    result = normalize_env(env)
    report = format_normalize_report(result)
    assert report == "No normalization changes."


def test_format_report_lists_changed_keys(sample_env):
    result = normalize_env(sample_env)
    report = format_normalize_report(result)
    assert "DEBUG" in report
    assert "HOST" in report


def test_format_report_color_contains_ansi(sample_env):
    result = normalize_env(sample_env)
    report = format_normalize_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi(sample_env):
    result = normalize_env(sample_env)
    report = format_normalize_report(result, color=False)
    assert "\033[" not in report
