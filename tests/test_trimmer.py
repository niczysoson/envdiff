"""Tests for envdiff.trimmer."""
import pytest
from envdiff.trimmer import (
    TrimResult,
    has_removals,
    trim_env,
    format_trim_report,
)


@pytest.fixture()
def base_env():
    return {"APP_NAME": "myapp", "DEBUG": "true", "SECRET_KEY": "abc123", "PORT": "8080"}


@pytest.fixture()
def reference():
    return {"APP_NAME": "ref", "PORT": "9090"}


# --- has_removals ---

def test_has_removals_true_when_keys_removed(base_env, reference):
    result = trim_env(base_env, reference)
    assert has_removals(result) is True


def test_has_removals_false_when_nothing_removed(reference):
    result = trim_env({"APP_NAME": "x", "PORT": "1"}, reference)
    assert has_removals(result) is False


# --- trim_env ---

def test_trim_removes_keys_not_in_reference(base_env, reference):
    result = trim_env(base_env, reference)
    assert set(result.trimmed.keys()) == {"APP_NAME", "PORT"}


def test_trim_removed_keys_sorted(base_env, reference):
    result = trim_env(base_env, reference)
    assert result.removed_keys == ["DEBUG", "SECRET_KEY"]


def test_trim_original_is_unchanged(base_env, reference):
    result = trim_env(base_env, reference)
    assert result.original == base_env


def test_trim_values_preserved(base_env, reference):
    result = trim_env(base_env, reference)
    assert result.trimmed["APP_NAME"] == "myapp"
    assert result.trimmed["PORT"] == "8080"


def test_trim_empty_env_returns_empty(reference):
    result = trim_env({}, reference)
    assert result.trimmed == {}
    assert result.removed_keys == []


def test_trim_empty_reference_removes_all(base_env):
    result = trim_env(base_env, {})
    assert result.trimmed == {}
    assert len(result.removed_keys) == len(base_env)


def test_trim_keep_extra_retains_all_keys(base_env, reference):
    result = trim_env(base_env, reference, keep_extra=True)
    assert result.trimmed == base_env
    assert result.removed_keys == []


# --- format_trim_report ---

def test_format_report_no_removals():
    result = TrimResult(original={}, trimmed={}, removed_keys=[])
    report = format_trim_report(result)
    assert "No stale keys found" in report


def test_format_report_lists_removed_keys():
    result = TrimResult(
        original={"A": "1", "B": "2"},
        trimmed={"A": "1"},
        removed_keys=["B"],
    )
    report = format_trim_report(result)
    assert "B" in report
    assert "1" in report or "Removed" in report


def test_format_report_shows_count():
    result = TrimResult(
        original={"X": "1", "Y": "2", "Z": "3"},
        trimmed={},
        removed_keys=["X", "Y", "Z"],
    )
    report = format_trim_report(result)
    assert "3" in report


def test_format_report_color_contains_ansi():
    result = TrimResult(
        original={"OLD": "v"},
        trimmed={},
        removed_keys=["OLD"],
    )
    report = format_trim_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi():
    result = TrimResult(
        original={"OLD": "v"},
        trimmed={},
        removed_keys=["OLD"],
    )
    report = format_trim_report(result, color=False)
    assert "\033[" not in report
