"""Tests for envdiff.profiler_cli."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envdiff.profiler import ProfileResult
from envdiff.profiler_cli import cmd_profile, format_profile_report, register_profiler_commands


def _make_result(**kwargs) -> ProfileResult:
    defaults = dict(
        source_file="test.env",
        total_keys=3,
        empty_keys=[],
        placeholder_keys=["SECRET"],
        numeric_value_keys=["PORT"],
        boolean_value_keys=["DEBUG"],
        long_value_keys=[],
        key_lengths={"SECRET": 6, "PORT": 4, "DEBUG": 5},
    )
    defaults.update(kwargs)
    return ProfileResult(**defaults)


def test_format_report_contains_total_keys():
    result = _make_result()
    report = format_profile_report(result, color=False)
    assert "Total keys" in report
    assert "3" in report


def test_format_report_lists_placeholder_keys():
    result = _make_result()
    report = format_profile_report(result, color=False)
    assert "SECRET" in report


def test_format_report_no_color_no_ansi():
    result = _make_result()
    report = format_profile_report(result, color=False)
    assert "\033[" not in report


def test_format_report_color_contains_ansi():
    result = _make_result()
    report = format_profile_report(result, color=True)
    assert "\033[" in report


def test_format_report_shows_complexity():
    result = _make_result()
    report = format_profile_report(result, color=False)
    assert "Complexity score" in report


def test_cmd_profile_missing_file(tmp_path, capsys):
    args = argparse.Namespace(file=str(tmp_path / "missing.env"), no_color=True)
    code = cmd_profile(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_cmd_profile_valid_file(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=9000\nDEBUG=false\n")
    args = argparse.Namespace(file=str(env_file), no_color=True)
    code = cmd_profile(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "Total keys" in captured.out


def test_register_profiler_commands_adds_profile():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_profiler_commands(subparsers)
    args = parser.parse_args(["profile", "some.env"])
    assert args.file == "some.env"
    assert callable(args.func)
