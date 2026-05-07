"""Tests for envdiff.annotator."""
from __future__ import annotations

import pytest

from envdiff.annotator import (
    AnnotatedLine,
    AnnotationResult,
    annotate_from_diff,
    annotate_from_validation,
)
from envdiff.differ import DiffResult
from envdiff.validator import ValidationResult, Violation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def source_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


@pytest.fixture()
def diff_all_ok():
    return DiffResult(missing_in_target=[], missing_in_source=[], mismatched={})


@pytest.fixture()
def diff_with_issues():
    return DiffResult(
        missing_in_target=["DEBUG"],
        missing_in_source=["SECRET"],
        mismatched={"PORT": ("5432", "3306")},
    )


# ---------------------------------------------------------------------------
# AnnotationResult.as_text
# ---------------------------------------------------------------------------

def test_as_text_includes_key_and_annotation():
    result = AnnotationResult(lines=[AnnotatedLine(key="FOO", value="bar", annotation="ok")])
    assert "FOO=bar  # ok" in result.as_text()


def test_as_text_redacts_values_when_disabled():
    result = AnnotationResult(lines=[AnnotatedLine(key="FOO", value="secret", annotation="ok")])
    text = result.as_text(include_values=False)
    assert "secret" not in text
    assert "FOO=" in text


def test_as_text_none_value_renders_empty():
    result = AnnotationResult(lines=[AnnotatedLine(key="MISSING", value=None, annotation="MISSING in target")])
    assert "MISSING=  #" in result.as_text()


# ---------------------------------------------------------------------------
# annotate_from_diff
# ---------------------------------------------------------------------------

def test_annotate_diff_ok_keys_marked_ok(source_env, diff_all_ok):
    result = annotate_from_diff(source_env, diff_all_ok)
    annotations = {line.key: line.annotation for line in result.lines}
    assert annotations["HOST"] == "ok"
    assert annotations["PORT"] == "ok"


def test_annotate_diff_missing_in_target(source_env, diff_with_issues):
    result = annotate_from_diff(source_env, diff_with_issues)
    annotations = {line.key: line.annotation for line in result.lines}
    assert annotations["DEBUG"] == "MISSING in target"


def test_annotate_diff_missing_in_source(source_env, diff_with_issues):
    result = annotate_from_diff(source_env, diff_with_issues)
    annotations = {line.key: line.annotation for line in result.lines}
    assert annotations["SECRET"] == "MISSING in source"


def test_annotate_diff_mismatch(source_env, diff_with_issues):
    result = annotate_from_diff(source_env, diff_with_issues)
    annotations = {line.key: line.annotation for line in result.lines}
    assert annotations["PORT"] == "VALUE MISMATCH"


def test_annotate_diff_keys_are_sorted(source_env, diff_with_issues):
    result = annotate_from_diff(source_env, diff_with_issues)
    keys = [line.key for line in result.lines]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# annotate_from_validation
# ---------------------------------------------------------------------------

def test_annotate_validation_ok_when_no_violations(source_env):
    validation = ValidationResult(violations=[])
    result = annotate_from_validation(source_env, validation)
    for line in result.lines:
        assert line.annotation == "ok"


def test_annotate_validation_shows_violation_message(source_env):
    violation = Violation(key="PORT", message="does not match pattern")
    validation = ValidationResult(violations=[violation])
    result = annotate_from_validation(source_env, validation)
    annotations = {line.key: line.annotation for line in result.lines}
    assert "does not match pattern" in annotations["PORT"]


def test_annotate_validation_missing_key_appended():
    env = {"HOST": "localhost"}
    violation = Violation(key="SECRET_KEY", message="required key missing")
    validation = ValidationResult(violations=[violation])
    result = annotate_from_validation(env, validation)
    keys = [line.key for line in result.lines]
    assert "SECRET_KEY" in keys
