"""Tests for envdiff.pinner."""
import pytest
from envdiff.pinner import (
    PinResult,
    has_drift,
    pin_env,
    diff_against_pin,
    format_pin_report,
)


@pytest.fixture
def baseline() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


# --- has_drift ---

def test_has_drift_false_when_clean():
    r = PinResult(source_file=".env", pinned={})
    assert not has_drift(r)


def test_has_drift_true_when_drifted():
    r = PinResult(source_file=".env", pinned={}, drifted=["KEY"])
    assert has_drift(r)


def test_has_drift_true_when_added():
    r = PinResult(source_file=".env", pinned={}, added=["NEW_KEY"])
    assert has_drift(r)


def test_has_drift_true_when_removed():
    r = PinResult(source_file=".env", pinned={}, removed=["OLD_KEY"])
    assert has_drift(r)


# --- pin_env ---

def test_pin_env_stores_all_keys(baseline):
    result = pin_env(baseline, source_file=".env.dev")
    assert result.pinned == baseline


def test_pin_env_records_source_file(baseline):
    result = pin_env(baseline, source_file=".env.dev")
    assert result.source_file == ".env.dev"


def test_pin_env_no_drift_fields(baseline):
    result = pin_env(baseline)
    assert result.drifted == []
    assert result.added == []
    assert result.removed == []


# --- diff_against_pin ---

def test_diff_no_drift_when_identical(baseline):
    result = diff_against_pin(baseline, baseline)
    assert not has_drift(result)


def test_diff_detects_drifted_value(baseline):
    current = {**baseline, "DB_HOST": "prod-db"}
    result = diff_against_pin(current, baseline)
    assert "DB_HOST" in result.drifted


def test_diff_detects_added_key(baseline):
    current = {**baseline, "NEW_VAR": "hello"}
    result = diff_against_pin(current, baseline)
    assert "NEW_VAR" in result.added


def test_diff_detects_removed_key(baseline):
    current = {k: v for k, v in baseline.items() if k != "SECRET"}
    result = diff_against_pin(current, baseline)
    assert "SECRET" in result.removed


def test_diff_ignore_keys_skipped(baseline):
    current = {**baseline, "DB_HOST": "other-host"}
    result = diff_against_pin(current, baseline, ignore_keys=["DB_HOST"])
    assert "DB_HOST" not in result.drifted


def test_diff_stores_baseline_as_pinned(baseline):
    result = diff_against_pin(baseline, baseline)
    assert result.pinned == baseline


# --- format_pin_report ---

def test_format_report_no_drift(baseline):
    result = pin_env(baseline, source_file=".env")
    report = format_pin_report(result)
    assert "No drift" in report


def test_format_report_shows_drifted_key(baseline):
    current = {**baseline, "DB_HOST": "prod-db"}
    result = diff_against_pin(current, baseline, source_file=".env")
    report = format_pin_report(result)
    assert "DB_HOST" in report
    assert "Drifted" in report


def test_format_report_shows_added_key(baseline):
    current = {**baseline, "EXTRA": "val"}
    result = diff_against_pin(current, baseline)
    report = format_pin_report(result)
    assert "EXTRA" in report
    assert "Added" in report


def test_format_report_shows_removed_key(baseline):
    current = {k: v for k, v in baseline.items() if k != "SECRET"}
    result = diff_against_pin(current, baseline)
    report = format_pin_report(result)
    assert "SECRET" in report
    assert "Removed" in report


def test_format_report_color_contains_ansi(baseline):
    current = {**baseline, "DB_HOST": "changed"}
    result = diff_against_pin(current, baseline)
    report = format_pin_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi(baseline):
    current = {**baseline, "DB_HOST": "changed"}
    result = diff_against_pin(current, baseline)
    report = format_pin_report(result, color=False)
    assert "\033[" not in report
