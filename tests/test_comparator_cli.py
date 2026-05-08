"""Tests for envdiff.comparator_cli."""
import argparse
from pathlib import Path

import pytest

from envdiff.comparator_cli import cmd_compare, register_comparator_commands


@pytest.fixture()
def env_source(tmp_path: Path) -> Path:
    f = tmp_path / "source.env"
    f.write_text("A=1\nB=2\nC=3\n")
    return f


@pytest.fixture()
def env_same(tmp_path: Path) -> Path:
    f = tmp_path / "same.env"
    f.write_text("A=1\nB=2\nC=3\n")
    return f


@pytest.fixture()
def env_diff(tmp_path: Path) -> Path:
    f = tmp_path / "diff.env"
    f.write_text("A=1\nC=99\n")
    return f


def _args(**kwargs) -> argparse.Namespace:
    defaults = dict(source="", targets=[], summary=False, no_color=True, exit_code=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_compare_returns_zero_no_diffs(env_source, env_same):
    args = _args(source=str(env_source), targets=[str(env_same)], exit_code=True)
    assert cmd_compare(args) == 0


def test_cmd_compare_returns_one_with_exit_code_and_diffs(env_source, env_diff):
    args = _args(source=str(env_source), targets=[str(env_diff)], exit_code=True)
    assert cmd_compare(args) == 1


def test_cmd_compare_returns_zero_without_exit_code_flag(env_source, env_diff):
    args = _args(source=str(env_source), targets=[str(env_diff)], exit_code=False)
    assert cmd_compare(args) == 0


def test_cmd_compare_missing_source(tmp_path, env_same):
    args = _args(source=str(tmp_path / "nope.env"), targets=[str(env_same)])
    assert cmd_compare(args) == 2


def test_cmd_compare_all_targets_missing(env_source, tmp_path):
    args = _args(source=str(env_source), targets=[str(tmp_path / "ghost.env")])
    assert cmd_compare(args) == 2


def test_cmd_compare_summary_mode(env_source, env_same, env_diff, capsys):
    args = _args(
        source=str(env_source),
        targets=[str(env_same), str(env_diff)],
        summary=True,
    )
    cmd_compare(args)
    out = capsys.readouterr().out
    assert "missing" in out


def test_register_comparator_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_comparator_commands(subparsers)
    parsed = parser.parse_args(["compare", "src.env", "tgt.env"])
    assert parsed.source == "src.env"
    assert parsed.targets == ["tgt.env"]
