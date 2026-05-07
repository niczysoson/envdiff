"""Tests for envdiff.scanner_cli."""

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envdiff.scanner import ScanResult
from envdiff.scanner_cli import format_scan_report, cmd_scan, register_scanner_commands


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(**kwargs) -> ScanResult:
    defaults = dict(duplicates={}, suspicious=[], source_file=".env")
    defaults.update(kwargs)
    return ScanResult(**defaults)


def _make_args(file: str, color: bool = False, exit_code: bool = False) -> argparse.Namespace:
    return argparse.Namespace(file=file, color=color, exit_code=exit_code)


# ---------------------------------------------------------------------------
# format_scan_report
# ---------------------------------------------------------------------------

def test_format_report_no_issues():
    result = _make_result()
    report = format_scan_report(result)
    assert "No duplicate keys found" in report
    assert "No suspicious values found" in report

def test_format_report_shows_duplicate():
    result = _make_result(duplicates={"PORT": 2})
    report = format_scan_report(result)
    assert "PORT" in report
    assert "2x" in report

def test_format_report_shows_suspicious():
    result = _make_result(suspicious=["SECRET"])
    report = format_scan_report(result)
    assert "SECRET" in report

def test_format_report_no_color_no_ansi():
    result = _make_result(duplicates={"X": 2})
    report = format_scan_report(result, color=False)
    assert "\033[" not in report

def test_format_report_color_contains_ansi():
    result = _make_result(duplicates={"X": 2})
    report = format_scan_report(result, color=True)
    assert "\033[" in report


# ---------------------------------------------------------------------------
# cmd_scan
# ---------------------------------------------------------------------------

def test_cmd_scan_missing_file(tmp_path):
    args = _make_args(str(tmp_path / "nonexistent.env"))
    assert cmd_scan(args) == 2

def test_cmd_scan_returns_zero_on_clean(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    args = _make_args(str(env_file), exit_code=True)
    assert cmd_scan(args) == 0

def test_cmd_scan_returns_one_on_issues_with_flag(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nPORT=9090\n")
    args = _make_args(str(env_file), exit_code=True)
    assert cmd_scan(args) == 1

def test_cmd_scan_returns_zero_on_issues_without_flag(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nPORT=9090\n")
    args = _make_args(str(env_file), exit_code=False)
    assert cmd_scan(args) == 0


# ---------------------------------------------------------------------------
# register_scanner_commands
# ---------------------------------------------------------------------------

def test_register_scanner_commands_adds_scan():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_scanner_commands(subparsers)
    args = parser.parse_args(["scan", "some.env"])
    assert args.file == "some.env"
