"""Tests for envdiff.template_cli."""

import argparse
from pathlib import Path

import pytest

from envdiff.template_cli import cmd_template_generate, register_template_commands, _parse_keep


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_URL=postgres://localhost/db\nSECRET=hunter2\nDEBUG=false\n")
    return p


def _make_args(**kwargs):
    defaults = {"source": "", "output": None, "keep": None, "placeholder": "<REPLACE_ME>"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_parse_keep_empty():
    assert _parse_keep(None) == []
    assert _parse_keep("") == []


def test_parse_keep_single():
    assert _parse_keep("DEBUG") == ["DEBUG"]


def test_parse_keep_multiple():
    assert _parse_keep("DEBUG,PORT, HOST") == ["DEBUG", "PORT", "HOST"]


def test_cmd_template_generate_missing_file(tmp_path):
    args = _make_args(source=str(tmp_path / "nonexistent.env"))
    assert cmd_template_generate(args) == 1


def test_cmd_template_generate_stdout(env_file, capsys):
    args = _make_args(source=str(env_file))
    rc = cmd_template_generate(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "<REPLACE_ME>" in out
    assert "DB_URL" in out


def test_cmd_template_generate_writes_file(env_file, tmp_path):
    out_file = tmp_path / ".env.example"
    args = _make_args(source=str(env_file), output=str(out_file))
    rc = cmd_template_generate(args)
    assert rc == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "SECRET=<REPLACE_ME>" in content


def test_cmd_template_generate_keep_preserves_value(env_file, capsys):
    args = _make_args(source=str(env_file), keep="DEBUG")
    cmd_template_generate(args)
    out = capsys.readouterr().out
    assert "DEBUG=false" in out
    assert "SECRET=<REPLACE_ME>" in out


def test_cmd_template_generate_custom_placeholder(env_file, capsys):
    args = _make_args(source=str(env_file), placeholder="TODO")
    cmd_template_generate(args)
    out = capsys.readouterr().out
    assert "TODO" in out
    assert "<REPLACE_ME>" not in out


def test_register_template_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_template_commands(subs)
    args = parser.parse_args(["template", ".env"])
    assert args.source == ".env"
    assert args.placeholder == "<REPLACE_ME>"
