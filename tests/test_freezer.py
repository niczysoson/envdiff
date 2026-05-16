"""Tests for envdiff.freezer."""
import pytest

from envdiff.freezer import FreezeResult, freeze_env, format_freeze_report


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_freeze_returns_freeze_result(sample_env):
    result = freeze_env(sample_env, source=".env.test")
    assert isinstance(result, FreezeResult)


def test_freeze_source_recorded(sample_env):
    result = freeze_env(sample_env, source=".env.prod")
    assert result.source == ".env.prod"


def test_freeze_keys_are_sorted(sample_env):
    result = freeze_env(sample_env, sort=True)
    assert result.keys == sorted(sample_env.keys())


def test_freeze_keys_unsorted_preserves_insertion_order():
    env = {"Z": "1", "A": "2", "M": "3"}
    result = freeze_env(env, sort=False)
    assert result.keys == ["Z", "A", "M"]


def test_freeze_redacts_sensitive_keys(sample_env):
    result = freeze_env(sample_env, redact=True)
    assert result.frozen["DB_PASSWORD"] == "***"
    assert result.frozen["API_KEY"] == "***"


def test_freeze_non_sensitive_keys_unchanged(sample_env):
    result = freeze_env(sample_env, redact=True)
    assert result.frozen["APP_NAME"] == "myapp"
    assert result.frozen["DEBUG"] == "true"
    assert result.frozen["PORT"] == "8080"


def test_freeze_redacted_keys_list(sample_env):
    result = freeze_env(sample_env, redact=True)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_freeze_no_redact_leaves_all_values(sample_env):
    result = freeze_env(sample_env, redact=False)
    assert result.frozen["DB_PASSWORD"] == "s3cr3t"
    assert result.redacted_keys == []


def test_freeze_extra_patterns_redact_custom_key():
    env = {"MY_TOKEN": "xyz", "APP_NAME": "app"}
    result = freeze_env(env, redact=True, extra_patterns=["token"])
    assert result.frozen["MY_TOKEN"] == "***"
    assert "MY_TOKEN" in result.redacted_keys


def test_format_freeze_report_contains_source(sample_env):
    result = freeze_env(sample_env, source=".env")
    report = format_freeze_report(result)
    assert ".env" in report


def test_format_freeze_report_contains_total_keys(sample_env):
    result = freeze_env(sample_env)
    report = format_freeze_report(result)
    assert str(len(sample_env)) in report


def test_format_freeze_report_lists_redacted_key(sample_env):
    result = freeze_env(sample_env, redact=True)
    report = format_freeze_report(result)
    assert "DB_PASSWORD" in report


def test_format_freeze_report_shows_values(sample_env):
    result = freeze_env(sample_env, redact=False)
    report = format_freeze_report(result)
    assert "APP_NAME=myapp" in report


def test_format_freeze_report_color_contains_ansi(sample_env):
    result = freeze_env(sample_env)
    report = format_freeze_report(result, color=True)
    assert "\033[" in report


def test_format_freeze_report_no_color_no_ansi(sample_env):
    result = freeze_env(sample_env)
    report = format_freeze_report(result, color=False)
    assert "\033[" not in report
