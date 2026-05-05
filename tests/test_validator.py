"""Tests for envdiff.validator."""

import pytest

from envdiff.validator import (
    ValidationResult,
    format_validation_report,
    validate_env,
)


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def test_validate_env_all_present_no_patterns():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = validate_env(env, required_keys=["HOST", "PORT"])
    assert result.is_valid
    assert result.missing_required == []


def test_validate_env_missing_required_key():
    env = {"HOST": "localhost"}
    result = validate_env(env, required_keys=["HOST", "PORT"])
    assert not result.is_valid
    assert "PORT" in result.missing_required


def test_validate_env_multiple_missing_keys():
    env = {}
    result = validate_env(env, required_keys=["HOST", "PORT", "SECRET"])
    assert set(result.missing_required) == {"HOST", "PORT", "SECRET"}


def test_validate_env_pattern_match_passes():
    env = {"PORT": "5432"}
    result = validate_env(env, patterns={"PORT": r"\d+"})
    assert result.is_valid
    assert result.pattern_violations == {}


def test_validate_env_pattern_violation():
    env = {"PORT": "not-a-number"}
    result = validate_env(env, patterns={"PORT": r"\d+"})
    assert not result.is_valid
    assert "PORT" in result.pattern_violations
    assert result.pattern_violations["PORT"] == "not-a-number"


def test_validate_env_pattern_key_absent_is_not_a_violation():
    """Pattern checks only apply when the key is present."""
    env = {"HOST": "localhost"}
    result = validate_env(env, patterns={"PORT": r"\d+"})
    assert result.is_valid


def test_validate_env_no_rules_returns_valid():
    env = {"FOO": "bar"}
    result = validate_env(env)
    assert result.is_valid


def test_validate_env_combined_missing_and_violation():
    env = {"PORT": "abc"}
    result = validate_env(
        env,
        required_keys=["HOST", "PORT"],
        patterns={"PORT": r"\d+"},
    )
    assert not result.is_valid
    assert "HOST" in result.missing_required
    assert "PORT" in result.pattern_violations


# ---------------------------------------------------------------------------
# format_validation_report
# ---------------------------------------------------------------------------

def test_format_report_valid_result():
    result = ValidationResult()
    assert format_validation_report(result) == "Validation passed."


def test_format_report_missing_keys_plain():
    result = ValidationResult(missing_required=["SECRET", "HOST"])
    report = format_validation_report(result, color=False)
    assert "Missing required keys:" in report
    assert "- HOST" in report
    assert "- SECRET" in report


def test_format_report_pattern_violations_plain():
    result = ValidationResult(pattern_violations={"PORT": "abc"})
    report = format_validation_report(result, color=False)
    assert "Pattern violations:" in report
    assert "PORT" in report
    assert "'abc'" in report


def test_format_report_color_wraps_headers():
    result = ValidationResult(missing_required=["FOO"])
    report = format_validation_report(result, color=True)
    assert "\033[" in report
