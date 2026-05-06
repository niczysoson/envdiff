"""Tests for envdiff.linter."""

import pytest
from envdiff.linter import (
    LintResult,
    _is_valid_key,
    _is_placeholder,
    lint_env,
    format_lint_report,
)


# ---------------------------------------------------------------------------
# _is_valid_key
# ---------------------------------------------------------------------------

def test_valid_key_simple():
    assert _is_valid_key("DATABASE_URL") is True


def test_valid_key_leading_underscore():
    assert _is_valid_key("_PRIVATE") is True


def test_invalid_key_starts_with_digit():
    assert _is_valid_key("1BAD") is False


def test_invalid_key_with_hyphen():
    assert _is_valid_key("MY-KEY") is False


def test_invalid_key_empty():
    assert _is_valid_key("") is False


# ---------------------------------------------------------------------------
# _is_placeholder
# ---------------------------------------------------------------------------

def test_placeholder_changeme():
    assert _is_placeholder("changeme") is True


def test_placeholder_angle_brackets():
    assert _is_placeholder("<your_secret>") is True


def test_placeholder_normal_value():
    assert _is_placeholder("postgres://localhost/db") is False


# ---------------------------------------------------------------------------
# lint_env
# ---------------------------------------------------------------------------

def test_lint_env_clean():
    env = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "false"}
    result = lint_env(env)
    assert not result.has_issues


def test_lint_env_blank_value():
    env = {"SECRET_KEY": ""}
    result = lint_env(env)
    assert "SECRET_KEY" in result.blank_values


def test_lint_env_placeholder_value():
    env = {"API_KEY": "changeme"}
    result = lint_env(env)
    assert "API_KEY" in result.placeholder_values


def test_lint_env_invalid_key():
    env = {"1BADKEY": "value"}
    result = lint_env(env)
    assert "1BADKEY" in result.invalid_key_names


def test_lint_env_duplicate_keys_from_raw_lines():
    env = {"PORT": "8080"}
    raw_lines = ["PORT=3000\n", "PORT=8080\n"]
    result = lint_env(env, raw_lines=raw_lines)
    assert "PORT" in result.duplicate_keys


def test_lint_env_no_duplicates_when_unique():
    env = {"HOST": "localhost", "PORT": "8080"}
    raw_lines = ["HOST=localhost\n", "PORT=8080\n"]
    result = lint_env(env, raw_lines=raw_lines)
    assert result.duplicate_keys == []


def test_lint_env_has_issues_true():
    env = {"SECRET": ""}
    result = lint_env(env)
    assert result.has_issues is True


# ---------------------------------------------------------------------------
# format_lint_report
# ---------------------------------------------------------------------------

def test_format_lint_report_no_issues():
    result = LintResult()
    report = format_lint_report(result, color=False)
    assert "No lint issues found" in report


def test_format_lint_report_blank_values():
    result = LintResult(blank_values=["SECRET_KEY"])
    report = format_lint_report(result, color=False)
    assert "Blank values" in report
    assert "SECRET_KEY" in report


def test_format_lint_report_placeholder():
    result = LintResult(placeholder_values={"API_KEY": "changeme"})
    report = format_lint_report(result, color=False)
    assert "Placeholder values" in report
    assert "API_KEY=changeme" in report


def test_format_lint_report_with_color():
    result = LintResult(blank_values=["FOO"])
    report = format_lint_report(result, color=True)
    assert "\033[" in report
