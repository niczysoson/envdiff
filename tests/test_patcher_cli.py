"""Unit tests for envdiff.patcher_cli."""
import argparse
from pathlib import Path

import pytest

from envdiff.patcher_cli import _parse_overrides, cmd_patch


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDEBUG=false\n")
    return f


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "file": None,
        "set": None,
        "no_add": False,
        "skip_existing": False,
        "output": None,
        "color": False,
        "exit_code": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# --- _parse_overrides ---

def test_parse_overrides_valid():
    result = _parse_overrides(["KEY=value", "OTHER=123"])
    assert result == {"KEY": "value", "OTHER": "123"}


def test_parse_overrides_empty_list():
    assert _parse_overrides([]) == {}


def test_parse_overrides_value_with_equals():
    result = _parse_overrides(["URL=http://example.com/path?a=1"])
    assert result["URL"] == "http://example.com/path?a=1"


def test_parse_overrides_no_equals_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_overrides(["BADVALUE"])


def test_parse_overrides_empty_key_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_overrides(["=value"])


# --- cmd_patch ---

def test_cmd_patch_returns_zero_no_changes(env_file):
    args = _make_args(file=str(env_file), set=["DB_HOST=localhost"])
    assert cmd_patch(args) == 0


def test_cmd_patch_returns_zero_with_changes_no_flag(env_file):
    args = _make_args(file=str(env_file), set=["DEBUG=true"])
    assert cmd_patch(args) == 0


def test_cmd_patch_returns_one_with_exit_code_flag(env_file):
    args = _make_args(file=str(env_file), set=["DEBUG=true"], exit_code=True)
    assert cmd_patch(args) == 1


def test_cmd_patch_writes_output_file(env_file, tmp_path):
    out = tmp_path / "patched.env"
    args = _make_args(file=str(env_file), set=["DEBUG=true"], output=str(out))
    cmd_patch(args)
    content = out.read_text()
    assert "DEBUG=true" in content
    assert "DB_HOST=localhost" in content


def test_cmd_patch_bad_override_returns_two(env_file):
    args = _make_args(file=str(env_file), set=["NOEQUALSSIGN"])
    assert cmd_patch(args) == 2
