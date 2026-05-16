"""Tests for envdiff.differ_keys."""
import pytest
from envdiff.differ_keys import KeyDiffResult, diff_keys, format_key_diff_report


@pytest.fixture
def source() -> dict:
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://"}


@pytest.fixture
def target_full(source) -> dict:
    return dict(source)


@pytest.fixture
def target_missing() -> dict:
    return {"APP_HOST": "prod.example.com", "EXTRA_KEY": "extra"}


# --- diff_keys ---

def test_diff_keys_returns_key_diff_result(source, target_full):
    result = diff_keys(source, target_full)
    assert isinstance(result, KeyDiffResult)


def test_diff_keys_identical_sets_no_differences(source, target_full):
    result = diff_keys(source, target_full)
    assert not result.has_differences


def test_diff_keys_identical_in_both_sorted(source, target_full):
    result = diff_keys(source, target_full)
    assert result.in_both == sorted(source.keys())


def test_diff_keys_detects_only_in_source(source, target_missing):
    result = diff_keys(source, target_missing)
    assert "APP_PORT" in result.only_in_source
    assert "DB_URL" in result.only_in_source


def test_diff_keys_detects_only_in_target(source, target_missing):
    result = diff_keys(source, target_missing)
    assert "EXTRA_KEY" in result.only_in_target


def test_diff_keys_shared_key_not_in_only_lists(source, target_missing):
    result = diff_keys(source, target_missing)
    assert "APP_HOST" in result.in_both
    assert "APP_HOST" not in result.only_in_source
    assert "APP_HOST" not in result.only_in_target


def test_diff_keys_has_differences_true_when_mismatch(source, target_missing):
    result = diff_keys(source, target_missing)
    assert result.has_differences


def test_diff_keys_total_source_count(source, target_missing):
    result = diff_keys(source, target_missing)
    assert result.total_source == len(source)


def test_diff_keys_total_target_count(source, target_missing):
    result = diff_keys(source, target_missing)
    assert result.total_target == len(target_missing)


def test_diff_keys_records_file_names(source, target_full):
    result = diff_keys(source, target_full, source_file=".env.dev", target_file=".env.prod")
    assert result.source_file == ".env.dev"
    assert result.target_file == ".env.prod"


def test_diff_keys_empty_source():
    result = diff_keys({}, {"A": "1"})
    assert result.only_in_target == ["A"]
    assert result.only_in_source == []


def test_diff_keys_empty_target():
    result = diff_keys({"A": "1"}, {})
    assert result.only_in_source == ["A"]
    assert result.only_in_target == []


def test_diff_keys_both_empty():
    result = diff_keys({}, {})
    assert not result.has_differences


# --- format_key_diff_report ---

def test_format_report_contains_file_names(source, target_missing):
    result = diff_keys(source, target_missing, source_file="a.env", target_file="b.env")
    report = format_key_diff_report(result)
    assert "a.env" in report
    assert "b.env" in report


def test_format_report_lists_only_in_source(source, target_missing):
    result = diff_keys(source, target_missing)
    report = format_key_diff_report(result)
    assert "APP_PORT" in report
    assert "DB_URL" in report


def test_format_report_lists_only_in_target(source, target_missing):
    result = diff_keys(source, target_missing)
    report = format_key_diff_report(result)
    assert "EXTRA_KEY" in report


def test_format_report_identical_shows_message(source, target_full):
    result = diff_keys(source, target_full)
    report = format_key_diff_report(result)
    assert "identical" in report.lower()


def test_format_report_color_contains_ansi(source, target_missing):
    result = diff_keys(source, target_missing)
    report = format_key_diff_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi(source, target_missing):
    result = diff_keys(source, target_missing)
    report = format_key_diff_report(result, color=False)
    assert "\033[" not in report
