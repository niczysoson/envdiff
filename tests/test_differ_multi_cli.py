"""Tests for envdiff.differ_multi_cli."""
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envdiff.differ_multi_cli import cmd_diff_multi, register_diff_multi_commands


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.source"
    f.write_text("A=1\nB=2\nC=3\n")
    return f


@pytest.fixture
def target_full(tmp_path: Path) -> Path:
    f = tmp_path / ".env.staging"
    f.write_text("A=1\nB=2\nC=3\n")
    return f


@pytest.fixture
def target_missing(tmp_path: Path) -> Path:
    f = tmp_path / ".env.prod"
    f.write_text("A=1\nB=2\n")
    return f


def _make_args(source, targets, no_color=True, exit_code=False):
    ns = argparse.Namespace(
        source=str(source),
        targets=[str(t) for t in targets],
        no_color=no_color,
        exit_code=exit_code,
    )
    return ns


def test_cmd_returns_zero_when_no_diffs(source_file, target_full):
    args = _make_args(source_file, [target_full])
    assert cmd_diff_multi(args) == 0


def test_cmd_returns_zero_without_exit_code_flag(source_file, target_missing):
    args = _make_args(source_file, [target_missing], exit_code=False)
    assert cmd_diff_multi(args) == 0


def test_cmd_returns_one_with_exit_code_flag_and_diffs(source_file, target_missing):
    args = _make_args(source_file, [target_missing], exit_code=True)
    assert cmd_diff_multi(args) == 1


def test_cmd_returns_two_when_source_missing(tmp_path, target_full):
    args = _make_args(tmp_path / "nonexistent.env", [target_full])
    assert cmd_diff_multi(args) == 2


def test_cmd_skips_missing_target_file(source_file, tmp_path, capsys):
    args = _make_args(source_file, [tmp_path / "ghost.env"])
    result = cmd_diff_multi(args)
    assert result == 2
    captured = capsys.readouterr()
    assert "warning" in captured.err


def test_cmd_prints_report(source_file, target_full, capsys):
    args = _make_args(source_file, [target_full])
    cmd_diff_multi(args)
    captured = capsys.readouterr()
    assert "Source" in captured.out


def test_register_diff_multi_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_diff_multi_commands(subparsers)
    parsed = parser.parse_args(["diff-multi", "src.env", "tgt.env"])
    assert parsed.source == "src.env"
    assert parsed.targets == ["tgt.env"]
