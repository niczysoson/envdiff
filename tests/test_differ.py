"""Tests for envdiff.differ module."""

import pytest
from envdiff.differ import diff_envs, DiffResult


SOURCE = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "DATABASE_URL": "postgres://localhost/dev",
    "SECRET_KEY": "abc123",
}

TARGET = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DATABASE_URL": "postgres://prod-host/prod",
    "API_KEY": "xyz789",
}


def test_missing_in_target():
    result = diff_envs(SOURCE, TARGET)
    assert "SECRET_KEY" in result.missing_in_target
    assert len(result.missing_in_target) == 1


def test_missing_in_source():
    result = diff_envs(SOURCE, TARGET)
    assert "API_KEY" in result.missing_in_source
    assert len(result.missing_in_source) == 1


def test_mismatched_values():
    result = diff_envs(SOURCE, TARGET)
    assert "DEBUG" in result.mismatched
    assert result.mismatched["DEBUG"] == ("true", "false")
    assert "DATABASE_URL" in result.mismatched


def test_matching_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "APP_NAME" in result.matching


def test_has_differences_true():
    result = diff_envs(SOURCE, TARGET)
    assert result.has_differences is True


def test_has_differences_false():
    env = {"KEY": "value"}
    result = diff_envs(env, env)
    assert result.has_differences is False


def test_ignore_values_skips_mismatch():
    result = diff_envs(SOURCE, TARGET, ignore_values=True)
    assert "DEBUG" not in result.mismatched
    assert "DATABASE_URL" not in result.mismatched


def test_ignore_values_still_catches_missing():
    result = diff_envs(SOURCE, TARGET, ignore_values=True)
    assert "SECRET_KEY" in result.missing_in_target
    assert "API_KEY" in result.missing_in_source


def test_identical_envs():
    result = diff_envs(SOURCE, SOURCE)
    assert not result.missing_in_target
    assert not result.missing_in_source
    assert not result.mismatched
    assert set(result.matching) == set(SOURCE.keys())


def test_empty_source_and_target():
    result = diff_envs({}, {})
    assert not result.has_differences


def test_summary_no_differences():
    result = diff_envs({"K": "v"}, {"K": "v"})
    assert result.summary() == "No differences found."


def test_summary_with_differences():
    result = diff_envs(SOURCE, TARGET)
    summary = result.summary()
    assert "Missing in target" in summary
    assert "Missing in source" in summary
    assert "Mismatched" in summary


def test_none_values_treated_as_different():
    result = diff_envs({"KEY": None}, {"KEY": "value"})
    assert "KEY" in result.mismatched
    assert result.mismatched["KEY"] == (None, "value")
