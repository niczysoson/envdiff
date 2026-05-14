"""Tests for envdiff.aliaser."""
import pytest
from envdiff.aliaser import (
    AliasResult,
    apply_aliases,
    format_alias_report,
    has_changes,
)


@pytest.fixture()
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"}


def test_apply_aliases_renames_key(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_apply_aliases_preserves_original(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.env


def test_apply_aliases_records_applied(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.applied


def test_apply_aliases_unknown_source(base_env):
    result = apply_aliases(base_env, {"MISSING_KEY": "ALIAS"})
    assert "MISSING_KEY" in result.unknown
    assert result.applied == []


def test_apply_aliases_skips_existing_without_overwrite(base_env):
    env = dict(base_env)
    env["DATABASE_HOST"] = "existing"
    result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=False)
    assert "DATABASE_HOST" in result.skipped
    assert result.env["DATABASE_HOST"] == "existing"


def test_apply_aliases_overwrites_when_flag_set(base_env):
    env = dict(base_env)
    env["DATABASE_HOST"] = "old"
    result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=True)
    assert result.env["DATABASE_HOST"] == "localhost"
    assert ("DB_HOST", "DATABASE_HOST") in result.applied


def test_has_changes_true_when_applied(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert has_changes(result) is True


def test_has_changes_false_when_nothing_applied(base_env):
    result = apply_aliases(base_env, {"NOPE": "ALIAS"})
    assert has_changes(result) is False


def test_format_report_applied(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    report = format_alias_report(result)
    assert "DB_HOST" in report
    assert "DATABASE_HOST" in report


def test_format_report_no_changes():
    result = AliasResult(env={}, applied=[], skipped=[], unknown=[])
    report = format_alias_report(result)
    assert "No aliases" in report


def test_format_report_color_contains_ansi(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    report = format_alias_report(result, color=True)
    assert "\033[" in report


def test_format_report_unknown_shown(base_env):
    result = apply_aliases(base_env, {"GHOST": "ALIAS"})
    report = format_alias_report(result)
    assert "GHOST" in report


def test_multiple_aliases_applied(base_env):
    result = apply_aliases(
        base_env,
        {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"},
    )
    assert len(result.applied) == 2
    assert result.env["DATABASE_PORT"] == "5432"
