"""Tests for envdiff.duplicator."""
from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from envdiff.duplicator import (
    DuplicateResult,
    find_duplicates,
    format_duplicate_report,
)
from envdiff.duplicator_cli import cmd_duplicates


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

def test_no_duplicates_when_all_values_unique():
    env = {"A": "alpha", "B": "beta", "C": "gamma"}
    result = find_duplicates(env)
    assert not result.has_duplicates
    assert result.duplicates == {}


def test_detects_single_duplicate_pair():
    env = {"A": "same", "B": "same", "C": "different"}
    result = find_duplicates(env)
    assert result.has_duplicates
    assert set(result.duplicates["same"]) == {"A", "B"}


def test_detects_multiple_duplicate_groups():
    env = {"A": "x", "B": "x", "C": "y", "D": "y"}
    result = find_duplicates(env)
    assert len(result.duplicates) == 2


def test_empty_value_can_be_duplicate():
    env = {"A": "", "B": "", "C": "real"}
    result = find_duplicates(env)
    assert "" in result.duplicates


def test_single_key_env_has_no_duplicates():
    result = find_duplicates({"ONLY": "value"})
    assert not result.has_duplicates


def test_empty_env_has_no_duplicates():
    result = find_duplicates({})
    assert not result.has_duplicates


# ---------------------------------------------------------------------------
# format_duplicate_report
# ---------------------------------------------------------------------------

def test_format_report_no_duplicates():
    result = DuplicateResult()
    assert format_duplicate_report(result) == "No duplicate values found."


def test_format_report_lists_shared_keys():
    env = {"KEY_A": "shared", "KEY_B": "shared"}
    result = find_duplicates(env)
    report = format_duplicate_report(result)
    assert "KEY_A" in report
    assert "KEY_B" in report


def test_format_report_color_contains_ansi():
    env = {"X": "dup", "Y": "dup"}
    result = find_duplicates(env)
    report = format_duplicate_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi():
    env = {"X": "dup", "Y": "dup"}
    result = find_duplicates(env)
    report = format_duplicate_report(result, color=False)
    assert "\033[" not in report


# ---------------------------------------------------------------------------
# cmd_duplicates (CLI)
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"file": "dummy.env", "color": False, "exit_code": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_returns_zero_when_no_duplicates(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=one\nB=two\n")
    args = _make_args(file=str(env_file), exit_code=True)
    assert cmd_duplicates(args) == 0


def test_cmd_returns_one_with_exit_code_flag(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=same\nB=same\n")
    args = _make_args(file=str(env_file), exit_code=True)
    assert cmd_duplicates(args) == 1


def test_cmd_returns_zero_without_exit_code_flag(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=same\nB=same\n")
    args = _make_args(file=str(env_file), exit_code=False)
    assert cmd_duplicates(args) == 0


def test_cmd_returns_two_for_missing_file():
    args = _make_args(file="nonexistent.env")
    assert cmd_duplicates(args) == 2
