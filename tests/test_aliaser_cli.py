"""Tests for envdiff.aliaser_cli."""
import argparse
import pytest
from unittest.mock import patch

from envdiff.aliaser_cli import _parse_aliases, cmd_alias, register_aliaser_commands


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return str(p)


def _make_args(env_file, mappings=None, overwrite=False, color=False):
    ns = argparse.Namespace(
        file=env_file,
        map=mappings,
        overwrite=overwrite,
        color=color,
    )
    return ns


def test_parse_aliases_valid():
    result = _parse_aliases(["DB_HOST=DATABASE_HOST"])
    assert result == {"DB_HOST": "DATABASE_HOST"}


def test_parse_aliases_empty_list():
    assert _parse_aliases([]) == {}


def test_parse_aliases_multiple():
    result = _parse_aliases(["A=B", "C=D"])
    assert result == {"A": "B", "C": "D"}


def test_parse_aliases_invalid_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_aliases(["NO_EQUALS_SIGN"])


def test_cmd_alias_returns_zero(env_file):
    args = _make_args(env_file, mappings=["DB_HOST=DATABASE_HOST"])
    assert cmd_alias(args) == 0


def test_cmd_alias_no_map_returns_zero(env_file, capsys):
    args = _make_args(env_file, mappings=None)
    rc = cmd_alias(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_bad_map_returns_two(env_file):
    args = _make_args(env_file, mappings=["BADFORMAT"])
    assert cmd_alias(args) == 2


def test_register_aliaser_commands_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_aliaser_commands(sub)
    parsed = parser.parse_args(["alias", "/dev/null"])
    assert hasattr(parsed, "func")
