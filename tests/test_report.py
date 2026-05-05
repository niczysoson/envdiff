"""Tests for envdiff.report."""

import pytest

from envdiff.differ import DiffResult
from envdiff.report import _colorize, format_report, _RED, _RESET


def _make_result(
    missing_in_target=None,
    missing_in_source=None,
    mismatched=None,
    matching=None,
):
    return DiffResult(
        missing_in_target=missing_in_target or set(),
        missing_in_source=missing_in_source or set(),
        mismatched=mismatched or {},
        matching=matching or set(),
    )


def test_colorize_wraps_with_ansi_when_enabled():
    result = _colorize("hello", _RED, use_color=True)
    assert result.startswith(_RED)
    assert result.endswith(_RESET)
    assert "hello" in result


def test_colorize_returns_plain_text_when_disabled():
    result = _colorize("hello", _RED, use_color=False)
    assert result == "hello"


def test_format_report_no_differences():
    result = _make_result(matching={"KEY"})
    report = format_report(result, use_color=False)
    assert "No differences found." in report


def test_format_report_missing_in_target():
    result = _make_result(missing_in_target={"SECRET_KEY", "DB_URL"})
    report = format_report(result, use_color=False)
    assert "Missing in target:" in report
    assert "SECRET_KEY" in report
    assert "DB_URL" in report


def test_format_report_missing_in_source():
    result = _make_result(missing_in_source={"EXTRA_VAR"})
    report = format_report(result, use_color=False)
    assert "Extra in target" in report
    assert "EXTRA_VAR" in report


def test_format_report_mismatched_values():
    result = _make_result(mismatched={"DEBUG": ("false", "true")})
    report = format_report(result, use_color=False)
    assert "Mismatched values:" in report
    assert "DEBUG" in report
    assert "'false'" in report
    assert "'true'" in report


def test_format_report_shows_issue_count():
    result = _make_result(
        missing_in_target={"A"},
        missing_in_source={"B"},
        mismatched={"C": ("x", "y")},
    )
    report = format_report(result, use_color=False)
    assert "3 issue(s) found." in report


def test_format_report_includes_labels():
    result = _make_result()
    report = format_report(
        result, source_label=".env.example", target_label=".env", use_color=False
    )
    assert ".env.example" in report
    assert ".env" in report


def test_format_report_with_color_enabled_contains_ansi():
    result = _make_result(missing_in_target={"MISSING"})
    report = format_report(result, use_color=True)
    assert "\033[" in report
