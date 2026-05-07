"""Integration tests: parse a real .env file and profile it end-to-end."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.parser import parse_env_file
from envdiff.profiler import profile_env
from envdiff.profiler_cli import format_profile_report


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    content = (
        "# Database\n"
        "DATABASE_URL=postgres://user:pass@localhost/mydb\n"
        "DB_PORT=5432\n"
        "DB_POOL_SIZE=10\n"
        "\n"
        "# Auth\n"
        "SECRET_KEY=changeme\n"
        "JWT_EXPIRY=3600\n"
        "ENABLE_AUTH=true\n"
        "\n"
        "# Empty and long\n"
        "UNSET_VAR=\n"
        f"LONG_TOKEN={'a' * 120}\n"
    )
    p = tmp_path / "integration.env"
    p.write_text(content)
    return p


def test_integration_total_keys(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env, source_file=str(env_file))
    assert result.total_keys == 8


def test_integration_empty_detected(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env)
    assert "UNSET_VAR" in result.empty_keys


def test_integration_placeholder_detected(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env)
    assert "SECRET_KEY" in result.placeholder_keys


def test_integration_numeric_keys(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env)
    for key in ("DB_PORT", "DB_POOL_SIZE", "JWT_EXPIRY"):
        assert key in result.numeric_value_keys


def test_integration_boolean_keys(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env)
    assert "ENABLE_AUTH" in result.boolean_value_keys


def test_integration_long_value_keys(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env)
    assert "LONG_TOKEN" in result.long_value_keys


def test_integration_report_renders(env_file):
    env = parse_env_file(env_file)
    result = profile_env(env, source_file=str(env_file))
    report = format_profile_report(result, color=False)
    assert "Total keys" in report
    assert "8" in report
    assert "Complexity score" in report
