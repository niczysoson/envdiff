"""Tests for the timeline diff CLI command."""

from __future__ import annotations

import argparse
import os
import tempfile

import pytest

from envdiff.differ_timeline_cli import cmd_diff_timeline, _format_timeline_report
from envdiff.differ_timeline import TimelineResult, TimelineEntry


def _write_env(tmp_path, name: str, content: str) -> str:
    p = os.path.join(tmp_path, name)
    with open(p, "w") as f:
        f.write(content)
    return p


@pytest.fixture()
def tmp(tmp_path):
    return str(tmp_path)


def _make_args(files, color=False, exit_code=False):
    ns = argparse.Namespace(files=files, color=color, exit_code=exit_code)
    return ns


def test_cmd_returns_zero_no_changes(tmp):
    f1 = _write_env(tmp, "v1.env", "A=1\nB=2\n")
    f2 = _write_env(tmp, "v2.env", "A=1\nB=2\n")
    assert cmd_diff_timeline(_make_args([f1, f2])) == 0


def test_cmd_returns_zero_with_changes_no_exit_code_flag(tmp):
    f1 = _write_env(tmp, "v1.env", "A=1\n")
    f2 = _write_env(tmp, "v2.env", "A=2\n")
    assert cmd_diff_timeline(_make_args([f1, f2], exit_code=False)) == 0


def test_cmd_returns_one_with_changes_and_exit_code_flag(tmp):
    f1 = _write_env(tmp, "v1.env", "A=1\n")
    f2 = _write_env(tmp, "v2.env", "A=2\n")
    assert cmd_diff_timeline(_make_args([f1, f2], exit_code=True)) == 1


def test_format_report_no_changes():
    result = TimelineResult()
    report = _format_timeline_report(result)
    assert "No changes" in report


def test_format_report_shows_added():
    entry = TimelineEntry(from_label="v1", to_label="v2", added={"NEW_KEY": "val"})
    result = TimelineResult(entries=[entry])
    report = _format_timeline_report(result)
    assert "NEW_KEY" in report
    assert "+" in report


def test_format_report_shows_removed():
    entry = TimelineEntry(from_label="v1", to_label="v2", removed={"OLD_KEY": "val"})
    result = TimelineResult(entries=[entry])
    report = _format_timeline_report(result)
    assert "OLD_KEY" in report
    assert "-" in report


def test_format_report_shows_changed():
    entry = TimelineEntry(
        from_label="v1", to_label="v2", changed={"K": ("old", "new")}
    )
    result = TimelineResult(entries=[entry])
    report = _format_timeline_report(result)
    assert "K" in report
    assert "old" in report
    assert "new" in report


def test_format_report_with_color_contains_ansi():
    entry = TimelineEntry(from_label="v1", to_label="v2", added={"X": "1"})
    result = TimelineResult(entries=[entry])
    report = _format_timeline_report(result, color=True)
    assert "\033[" in report
