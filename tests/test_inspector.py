"""Tests for envdiff.inspector."""
from __future__ import annotations

import pytest
from envdiff.inspector import (
    InspectResult,
    inspect_env,
    format_inspect_report,
    _is_numeric,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_env(**kwargs: str) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# _is_numeric
# ---------------------------------------------------------------------------

def test_is_numeric_integer():
    assert _is_numeric("42") is True


def test_is_numeric_float():
    assert _is_numeric("3.14") is True


def test_is_numeric_string():
    assert _is_numeric("hello") is False


def test_is_numeric_empty():
    assert _is_numeric("") is False


# ---------------------------------------------------------------------------
# inspect_env
# ---------------------------------------------------------------------------

def test_inspect_total_keys():
    env = _make_env(A="1", B="2", C="3")
    result = inspect_env(env, source="test.env")
    assert result.total == 3


def test_inspect_empty_keys_detected():
    env = _make_env(EMPTY_KEY="", NORMAL="value")
    result = inspect_env(env)
    assert "EMPTY_KEY" in result.empty_keys
    assert "NORMAL" not in result.empty_keys


def test_inspect_numeric_only_values():
    env = _make_env(PORT="8080", NAME="myapp")
    result = inspect_env(env)
    assert "PORT" in result.numeric_only_values
    assert "NAME" not in result.numeric_only_values


def test_inspect_boolean_like_values():
    env = _make_env(DEBUG="true", ENABLED="yes", NAME="myapp")
    result = inspect_env(env)
    assert "DEBUG" in result.boolean_like_values
    assert "ENABLED" in result.boolean_like_values
    assert "NAME" not in result.boolean_like_values


def test_inspect_long_value_detected():
    env = _make_env(SECRET="x" * 200, SHORT="abc")
    result = inspect_env(env)
    assert "SECRET" in result.long_values
    assert "SHORT" not in result.long_values


def test_inspect_no_anomalies():
    env = _make_env(APP_NAME="myapp", APP_ENV="production")
    result = inspect_env(env)
    assert result.has_anomalies is False


def test_inspect_has_anomalies_when_empty_key():
    env = _make_env(MISSING="")
    result = inspect_env(env)
    assert result.has_anomalies is True


def test_inspect_source_stored():
    result = inspect_env({}, source="my.env")
    assert result.source == "my.env"


# ---------------------------------------------------------------------------
# format_inspect_report
# ---------------------------------------------------------------------------

def test_format_report_contains_source():
    result = inspect_env({"A": "val"}, source="prod.env")
    report = format_inspect_report(result)
    assert "prod.env" in report


def test_format_report_no_anomalies_message():
    result = inspect_env({"A": "val"})
    report = format_inspect_report(result)
    assert "No anomalies" in report


def test_format_report_lists_empty_keys():
    result = inspect_env({"EMPTY": ""})
    report = format_inspect_report(result)
    assert "EMPTY" in report
    assert "Empty values" in report


def test_format_report_total_keys():
    result = inspect_env({"A": "1", "B": "2"})
    report = format_inspect_report(result)
    assert "2" in report
