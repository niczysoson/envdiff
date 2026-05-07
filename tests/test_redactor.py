"""Tests for envdiff.redactor."""

from __future__ import annotations

import pytest

from envdiff.redactor import (
    DEFAULT_MASK,
    RedactResult,
    _key_is_sensitive,
    redact_env,
)


# ---------------------------------------------------------------------------
# _key_is_sensitive
# ---------------------------------------------------------------------------

def test_key_is_sensitive_password():
    assert _key_is_sensitive("DB_PASSWORD", [r"(?i)password"]) is True


def test_key_is_sensitive_case_insensitive():
    assert _key_is_sensitive("db_secret", [r"(?i)secret"]) is True


def test_key_is_not_sensitive():
    assert _key_is_sensitive("DB_HOST", [r"(?i)secret", r"(?i)password"]) is False


def test_key_is_sensitive_custom_pattern():
    assert _key_is_sensitive("INTERNAL_CERT", [r"(?i)cert"]) is True


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

_SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PASSWORD": "s3cr3t",
    "API_TOKEN": "tok_abc123",
    "APP_NAME": "envdiff",
    "SECRET_KEY": "supersecret",
}


def test_redact_env_returns_redact_result():
    result = redact_env(_SAMPLE)
    assert isinstance(result, RedactResult)


def test_redact_env_masks_sensitive_keys():
    result = redact_env(_SAMPLE)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert result.redacted["API_TOKEN"] == DEFAULT_MASK
    assert result.redacted["SECRET_KEY"] == DEFAULT_MASK


def test_redact_env_preserves_safe_keys():
    result = redact_env(_SAMPLE)
    assert result.redacted["DB_HOST"] == "localhost"
    assert result.redacted["APP_NAME"] == "envdiff"


def test_redact_env_original_is_unchanged():
    result = redact_env(_SAMPLE)
    assert result.original == _SAMPLE


def test_redact_env_redacted_keys_sorted():
    result = redact_env(_SAMPLE)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_redact_env_custom_mask():
    result = redact_env(_SAMPLE, mask="[hidden]")
    assert result.redacted["DB_PASSWORD"] == "[hidden]"


def test_redact_env_keep_keys_skips_redaction():
    result = redact_env(_SAMPLE, keep_keys=["DB_PASSWORD"])
    assert result.redacted["DB_PASSWORD"] == "s3cr3t"
    assert "DB_PASSWORD" not in result.redacted_keys


def test_redact_env_extra_patterns():
    env = {"DB_HOST": "localhost", "INTERNAL_CERT": "cert_data"}
    result = redact_env(env, extra_patterns=[r"(?i)cert"])
    assert result.redacted["INTERNAL_CERT"] == DEFAULT_MASK
    assert result.redacted["DB_HOST"] == "localhost"


def test_redact_env_empty_dict():
    result = redact_env({})
    assert result.redacted == {}
    assert result.redacted_keys == []
