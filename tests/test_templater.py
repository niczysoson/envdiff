"""Tests for envdiff.templater."""

import pytest
from envdiff.templater import (
    TemplateResult,
    _redact_value,
    build_template,
    render_template,
)


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://user:pass@localhost/db",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_redact_value_returns_placeholder():
    assert _redact_value("real_value") == "<REPLACE_ME>"


def test_redact_value_custom_placeholder():
    assert _redact_value("real_value", "TODO") == "TODO"


def test_build_template_redacts_all_by_default(sample_env):
    result = build_template(sample_env)
    for key in sample_env:
        assert result.redacted[key] == "<REPLACE_ME>"


def test_build_template_keys_are_sorted(sample_env):
    result = build_template(sample_env)
    assert result.keys == sorted(sample_env.keys())


def test_build_template_keep_keys_preserves_value(sample_env):
    result = build_template(sample_env, keep_keys=["DEBUG", "PORT"])
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted["PORT"] == "8080"
    assert result.redacted["SECRET_KEY"] == "<REPLACE_ME>"


def test_build_template_custom_placeholder(sample_env):
    result = build_template(sample_env, placeholder="CHANGEME")
    assert result.redacted["DATABASE_URL"] == "CHANGEME"


def test_build_template_comments_only_for_known_keys(sample_env):
    comments = {"SECRET_KEY": "JWT signing secret", "UNKNOWN_KEY": "ignored"}
    result = build_template(sample_env, comments=comments)
    assert "SECRET_KEY" in result.comments
    assert "UNKNOWN_KEY" not in result.comments


def test_build_template_empty_env():
    result = build_template({})
    assert result.keys == []
    assert result.redacted == {}


def test_render_template_produces_key_equals_placeholder(sample_env):
    result = build_template(sample_env)
    output = render_template(result)
    for key in sample_env:
        assert f"{key}=<REPLACE_ME>" in output


def test_render_template_includes_comments():
    env = {"API_KEY": "abc123"}
    result = build_template(env, comments={"API_KEY": "Your API key"})
    output = render_template(result)
    assert "# Your API key" in output
    assert output.index("# Your API key") < output.index("API_KEY=")


def test_render_template_ends_with_newline(sample_env):
    result = build_template(sample_env)
    output = render_template(result)
    assert output.endswith("\n")


def test_render_template_empty_result():
    result = TemplateResult()
    assert render_template(result) == ""
