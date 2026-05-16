"""Integration tests for the aliaser feature (parser → aliaser → report)."""
import pytest
from envdiff.parser import parse_env_file
from envdiff.aliaser import apply_aliases, format_alias_report, has_changes


@pytest.fixture()
def env_file(tmp_path):
    content = (
        "DB_HOST=db.internal\n"
        "DB_PORT=5432\n"
        'DB_PASS=\"s3cr3t\"\n'
        "APP_DEBUG=true\n"
    )
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_integration_alias_applied_end_to_end(env_file):
    env = parse_env_file(str(env_file))
    result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert result.env["DATABASE_HOST"] == "db.internal"


def test_integration_report_contains_mapping(env_file):
    env = parse_env_file(str(env_file))
    result = apply_aliases(env, {"DB_PORT": "DATABASE_PORT"})
    report = format_alias_report(result)
    assert "DB_PORT" in report
    assert "DATABASE_PORT" in report


def test_integration_unknown_key_reported(env_file):
    env = parse_env_file(str(env_file))
    result = apply_aliases(env, {"NONEXISTENT": "ALIAS"})
    assert "NONEXISTENT" in result.unknown
    assert not has_changes(result)


def test_integration_original_key_retained(env_file):
    env = parse_env_file(str(env_file))
    result = apply_aliases(env, {"APP_DEBUG": "DEBUG"})
    assert "APP_DEBUG" in result.env
    assert "DEBUG" in result.env


def test_integration_no_aliases_leaves_env_unchanged(env_file):
    env = parse_env_file(str(env_file))
    result = apply_aliases(env, {})
    assert result.env == env
    assert not has_changes(result)


def test_integration_multiple_aliases_applied(env_file):
    """All aliases in a batch mapping should be applied in a single call."""
    env = parse_env_file(str(env_file))
    aliases = {
        "DB_HOST": "DATABASE_HOST",
        "DB_PORT": "DATABASE_PORT",
        "DB_PASS": "DATABASE_PASSWORD",
    }
    result = apply_aliases(env, aliases)
    for new_key in ("DATABASE_HOST", "DATABASE_PORT", "DATABASE_PASSWORD"):
        assert new_key in result.env
    assert has_changes(result)
    assert not result.unknown
