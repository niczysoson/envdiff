"""Tests for envdiff.scanner."""

import pytest
from envdiff.scanner import ScanResult, has_issues, scan_env_file, _is_suspicious


# ---------------------------------------------------------------------------
# _is_suspicious
# ---------------------------------------------------------------------------

def test_is_suspicious_changeme():
    assert _is_suspicious("changeme") is True

def test_is_suspicious_case_insensitive():
    assert _is_suspicious("CHANGEME") is True

def test_is_suspicious_contains_todo():
    assert _is_suspicious("TODO_replace_this") is True

def test_is_not_suspicious_normal_value():
    assert _is_suspicious("my-secret-value") is False

def test_is_not_suspicious_empty():
    assert _is_suspicious("") is False


# ---------------------------------------------------------------------------
# scan_env_file
# ---------------------------------------------------------------------------

def test_scan_no_issues():
    lines = ["API_KEY=abc123", "DB_HOST=localhost"]
    result = scan_env_file(lines)
    assert result.duplicates == {}
    assert result.suspicious == []

def test_scan_detects_duplicate():
    lines = ["PORT=8080", "PORT=9090"]
    result = scan_env_file(lines)
    assert "PORT" in result.duplicates
    assert result.duplicates["PORT"] == 2

def test_scan_detects_suspicious_value():
    lines = ["SECRET=changeme"]
    result = scan_env_file(lines)
    assert "SECRET" in result.suspicious

def test_scan_skips_comments():
    lines = ["# PORT=8080", "HOST=localhost"]
    result = scan_env_file(lines)
    assert result.duplicates == {}

def test_scan_skips_blank_lines():
    lines = ["", "   ", "KEY=value"]
    result = scan_env_file(lines)
    assert result.duplicates == {}
    assert result.suspicious == []

def test_scan_skips_lines_without_equals():
    lines = ["NOTANASSIGNMENT"]
    result = scan_env_file(lines)
    assert result.duplicates == {}

def test_scan_stores_source_file():
    result = scan_env_file([], source_file=".env.prod")
    assert result.source_file == ".env.prod"

def test_scan_multiple_duplicates():
    lines = ["A=1", "A=2", "A=3", "B=x", "B=y"]
    result = scan_env_file(lines)
    assert result.duplicates["A"] == 3
    assert result.duplicates["B"] == 2

def test_scan_suspicious_deduped():
    lines = ["KEY=changeme", "KEY=changeme"]
    result = scan_env_file(lines)
    assert result.suspicious.count("KEY") == 1


# ---------------------------------------------------------------------------
# has_issues
# ---------------------------------------------------------------------------

def test_has_issues_false_when_clean():
    result = ScanResult()
    assert has_issues(result) is False

def test_has_issues_true_on_duplicates():
    result = ScanResult(duplicates={"X": 2})
    assert has_issues(result) is True

def test_has_issues_true_on_suspicious():
    result = ScanResult(suspicious=["SECRET"])
    assert has_issues(result) is True
