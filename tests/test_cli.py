"""Tests for the CLI entry point."""

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import run


@pytest.fixture()
def source_env(tmp_path: Path) -> Path:
    p = tmp_path / ".env.example"
    p.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DEBUG=false
            SECRET_KEY=changeme
            """
        )
    )
    return p


@pytest.fixture()
def target_env_full(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DEBUG=true
            SECRET_KEY=supersecret
            """
        )
    )
    return p


@pytest.fixture()
def target_env_missing(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            """
        )
    )
    return p


def test_run_returns_zero_when_no_exit_code_flag(source_env, target_env_full):
    result = run([str(source_env), str(target_env_full)])
    assert result == 0


def test_run_returns_zero_even_with_diffs_without_flag(source_env, target_env_missing):
    result = run([str(source_env), str(target_env_missing)])
    assert result == 0


def test_run_returns_one_with_exit_code_flag_and_diffs(source_env, target_env_missing):
    result = run([str(source_env), str(target_env_missing), "--exit-code"])
    assert result == 1


def test_run_returns_zero_with_exit_code_flag_no_diffs(tmp_path):
    content = "APP_NAME=myapp\nDEBUG=false\n"
    src = tmp_path / "a.env"
    tgt = tmp_path / "b.env"
    src.write_text(content)
    tgt.write_text(content)
    result = run([str(src), str(tgt), "--exit-code"])
    assert result == 0


def test_run_returns_two_for_missing_source(tmp_path):
    missing = tmp_path / "nonexistent.env"
    existing = tmp_path / "real.env"
    existing.write_text("KEY=val\n")
    result = run([str(missing), str(existing)])
    assert result == 2


def test_run_returns_two_for_missing_target(tmp_path):
    existing = tmp_path / "real.env"
    existing.write_text("KEY=val\n")
    missing = tmp_path / "nonexistent.env"
    result = run([str(existing), str(missing)])
    assert result == 2


def test_run_no_color_flag_does_not_crash(source_env, target_env_full):
    result = run([str(source_env), str(target_env_full), "--no-color"])
    assert result == 0


def test_run_returns_two_for_both_missing(tmp_path):
    """Both source and target missing should still return exit code 2."""
    missing_src = tmp_path / "nonexistent_src.env"
    missing_tgt = tmp_path / "nonexistent_tgt.env"
    result = run([str(missing_src), str(missing_tgt)])
    assert result == 2
