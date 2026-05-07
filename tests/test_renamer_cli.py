"""Tests for envdiff.renamer_cli."""
import argparse
import io
import textwrap
from pathlib import Path

import pytest

from envdiff.renamer_cli import _parse_mapping, cmd_rename


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent("""\
        OLD_HOST=localhost
        OLD_PORT=5432
        SECRET=abc123
    """))
    return p


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "file": "",
        "rename": [],
        "overwrite": False,
        "in_place": False,
        "color": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_parse_mapping_valid():
    result = _parse_mapping(["OLD=NEW", "FOO=BAR"])
    assert result == {"OLD": "NEW", "FOO": "BAR"}


def test_parse_mapping_empty():
    assert _parse_mapping([]) == {}


def test_parse_mapping_invalid_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_mapping(["INVALID_SPEC"])


def test_cmd_rename_returns_zero_on_success(env_file):
    args = _make_args(file=str(env_file), rename=["OLD_HOST=NEW_HOST"])
    out = io.StringIO()
    code = cmd_rename(args, out=out)
    assert code == 0
    assert "OLD_HOST -> NEW_HOST" in out.getvalue()


def test_cmd_rename_returns_one_when_skipped(env_file):
    args = _make_args(file=str(env_file), rename=["MISSING=NEW"])
    out = io.StringIO()
    code = cmd_rename(args, out=out)
    assert code == 1


def test_cmd_rename_file_not_found():
    args = _make_args(file="/no/such/.env", rename=["A=B"])
    err = io.StringIO()
    code = cmd_rename(args, out=io.StringIO(), err=err)
    assert code == 2
    assert "not found" in err.getvalue()


def test_cmd_rename_no_specs_returns_two(env_file):
    args = _make_args(file=str(env_file), rename=[])
    err = io.StringIO()
    code = cmd_rename(args, out=io.StringIO(), err=err)
    assert code == 2


def test_cmd_rename_in_place_writes_file(env_file):
    args = _make_args(
        file=str(env_file), rename=["OLD_HOST=NEW_HOST"], in_place=True
    )
    cmd_rename(args, out=io.StringIO())
    content = env_file.read_text()
    assert "NEW_HOST=localhost" in content
    assert "OLD_HOST" not in content
