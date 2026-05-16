"""Tests for envdiff.grouper."""
from __future__ import annotations

import pytest

from envdiff.grouper import (
    GroupResult,
    _extract_prefix,
    format_group_report,
    group_by_map,
    group_by_prefix,
)


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_delimiter():
    assert _extract_prefix("SIMPLE") is None


def test_extract_prefix_custom_delimiter():
    assert _extract_prefix("AWS.REGION", delimiter=".") == "AWS"


def test_extract_prefix_trailing_delimiter_only():
    # "DB_" has an empty rest part — treated as no prefix
    assert _extract_prefix("DB_") is None


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_group_by_prefix_creates_groups(sample_env):
    result = group_by_prefix(sample_env)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_group_by_prefix_keys_sorted(sample_env):
    result = group_by_prefix(sample_env)
    assert result.groups["DB"] == ["DB_HOST", "DB_PORT"]


def test_group_by_prefix_ungrouped_contains_no_delimiter_keys(sample_env):
    result = group_by_prefix(sample_env)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_group_by_prefix_min_group_size_filters_small_groups():
    env = {"DB_HOST": "h", "DB_PORT": "p", "AWS_KEY": "k", "PORT": "80"}
    result = group_by_prefix(env, min_group_size=2)
    assert "DB" in result.groups
    assert "AWS" not in result.groups
    assert "AWS_KEY" in result.ungrouped


def test_group_by_prefix_empty_env():
    result = group_by_prefix({})
    assert result.groups == {}
    assert result.ungrouped == []


# ---------------------------------------------------------------------------
# group_by_map
# ---------------------------------------------------------------------------

def test_group_by_map_assigns_correct_group():
    env = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}
    tag_map = {"HOST": "database", "PORT": "database"}
    result = group_by_map(env, tag_map)
    assert result.groups["database"] == ["HOST", "PORT"]
    assert "SECRET" in result.ungrouped


def test_group_by_map_empty_tag_map():
    env = {"A": "1", "B": "2"}
    result = group_by_map(env, {})
    assert result.groups == {}
    assert sorted(result.ungrouped) == ["A", "B"]


# ---------------------------------------------------------------------------
# format_group_report
# ---------------------------------------------------------------------------

def test_format_report_contains_group_headers():
    result = GroupResult(groups={"DB": ["DB_HOST", "DB_PORT"]}, ungrouped=[])
    report = format_group_report(result)
    assert "[DB]" in report
    assert "DB_HOST" in report


def test_format_report_ungrouped_section():
    result = GroupResult(groups={}, ungrouped=["PORT"])
    report = format_group_report(result)
    assert "[ungrouped]" in report
    assert "PORT" in report


def test_format_report_color_adds_ansi():
    result = GroupResult(groups={"DB": ["DB_HOST"]}, ungrouped=[])
    report = format_group_report(result, color=True)
    assert "\033[" in report


def test_format_report_no_color_no_ansi():
    result = GroupResult(groups={"DB": ["DB_HOST"]}, ungrouped=[])
    report = format_group_report(result, color=False)
    assert "\033[" not in report
