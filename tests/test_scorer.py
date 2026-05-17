"""Tests for envdiff.scorer."""
from __future__ import annotations

import pytest

from envdiff.scorer import ScoreResult, format_score_report, score_env


@pytest.fixture
def clean_env() -> dict:
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "s3cur3-rand0m-string",
        "DEBUG": "false",
    }


@pytest.fixture
def dirty_env() -> dict:
    return {
        "DATABASE_URL": "",
        "1INVALID": "bad-key",
        "PASSWORD": "changeme",
        "SECRET": "TODO",
        "DUPE_A": "same",
        "DUPE_B": "same",
        "API_KEY": "CHANGE_ME",
    }


def test_score_env_returns_score_result(clean_env):
    result = score_env(clean_env, source=".env.test")
    assert isinstance(result, ScoreResult)


def test_score_clean_env_is_high(clean_env):
    result = score_env(clean_env)
    assert result.score >= 80


def test_score_clean_env_has_no_penalties(clean_env):
    result = score_env(clean_env)
    assert result.penalties == []


def test_score_dirty_env_is_lower(dirty_env):
    result = score_env(dirty_env)
    assert result.score < 80


def test_score_dirty_env_has_penalties(dirty_env):
    result = score_env(dirty_env)
    assert len(result.penalties) > 0


def test_score_records_total_keys(clean_env):
    result = score_env(clean_env)
    assert result.total_keys == len(clean_env)


def test_score_records_source(clean_env):
    result = score_env(clean_env, source="staging.env")
    assert result.source == "staging.env"


def test_score_never_below_zero(dirty_env):
    # Add many bad keys to push score toward floor
    env = {f"1BAD_{i}": "changeme" for i in range(20)}
    result = score_env(env)
    assert result.score >= 0


def test_score_never_above_100(clean_env):
    result = score_env(clean_env)
    assert result.score <= 100


def test_breakdown_keys_present(dirty_env):
    result = score_env(dirty_env)
    assert "lint" in result.breakdown
    assert "empty_values" in result.breakdown
    assert "suspicious" in result.breakdown
    assert "duplicates" in result.breakdown


def test_format_report_contains_score(clean_env):
    result = score_env(clean_env, source=".env")
    report = format_score_report(result, color=False)
    assert "/100" in report
    assert ".env" in report


def test_format_report_no_color_no_ansi(clean_env):
    result = score_env(clean_env)
    report = format_score_report(result, color=False)
    assert "\033[" not in report


def test_format_report_color_contains_ansi(clean_env):
    result = score_env(clean_env)
    report = format_score_report(result, color=True)
    assert "\033[" in report


def test_format_report_lists_penalties(dirty_env):
    result = score_env(dirty_env)
    report = format_score_report(result, color=False)
    assert "Penalties:" in report


def test_format_report_no_issues_message_for_clean(clean_env):
    result = score_env(clean_env)
    report = format_score_report(result, color=False)
    assert "No issues detected" in report
