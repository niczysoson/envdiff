"""Tests for envdiff.profiler."""
from __future__ import annotations

import pytest

from envdiff.profiler import ProfileResult, _is_numeric, _is_placeholder, profile_env


@pytest.fixture()
def sample_env():
    return {
        "DATABASE_URL": "postgres://user:pass@localhost/db",
        "DEBUG": "true",
        "PORT": "8080",
        "SECRET_KEY": "changeme",
        "EMPTY_VAR": "",
        "LONG_VAR": "x" * 150,
        "API_KEY": "abc123",
    }


def test_profile_total_keys(sample_env):
    result = profile_env(sample_env, source_file=".env")
    assert result.total_keys == 7


def test_profile_empty_keys(sample_env):
    result = profile_env(sample_env)
    assert "EMPTY_VAR" in result.empty_keys
    assert result.empty_count == 1


def test_profile_placeholder_keys(sample_env):
    result = profile_env(sample_env)
    assert "SECRET_KEY" in result.placeholder_keys
    assert result.placeholder_count == 1


def test_profile_numeric_keys(sample_env):
    result = profile_env(sample_env)
    assert "PORT" in result.numeric_value_keys


def test_profile_boolean_keys(sample_env):
    result = profile_env(sample_env)
    assert "DEBUG" in result.boolean_value_keys


def test_profile_long_value_keys(sample_env):
    result = profile_env(sample_env)
    assert "LONG_VAR" in result.long_value_keys


def test_profile_source_file_stored():
    result = profile_env({}, source_file="prod.env")
    assert result.source_file == "prod.env"


def test_profile_empty_env():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.complexity_score == 0


def test_complexity_score_decreases_for_placeholders():
    env = {"A": "real_value", "B": "changeme"}
    result = profile_env(env)
    # total=2, placeholders=1 -> score = 2 - 0 - 1 = 1
    assert result.complexity_score == 1


def test_is_placeholder_angle_brackets():
    assert _is_placeholder("<secret>") is True
    assert _is_placeholder("<value>") is True


def test_is_placeholder_known_word():
    assert _is_placeholder("CHANGEME") is True
    assert _is_placeholder("todo") is True


def test_is_not_placeholder_real_value():
    assert _is_placeholder("my-real-password-123") is False


def test_is_numeric_integer():
    assert _is_numeric("42") is True


def test_is_numeric_float():
    assert _is_numeric("3.14") is True


def test_is_not_numeric_word():
    assert _is_numeric("hello") is False


def test_key_lengths_recorded(sample_env):
    result = profile_env(sample_env)
    assert result.key_lengths["PORT"] == len("PORT")
