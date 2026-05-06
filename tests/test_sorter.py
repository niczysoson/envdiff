"""Tests for envdiff.sorter."""

import pytest

from envdiff.sorter import (
    SortResult,
    _extract_prefix,
    group_by_prefix,
    render_sorted,
    sort_alphabetically,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "AKID",
        "AWS_SECRET": "secret",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_delimiter():
    assert _extract_prefix("DEBUG") == ""


def test_extract_prefix_custom_delimiter():
    assert _extract_prefix("DB.HOST", delimiter=".") == "DB"


def test_sort_alphabetically_orders_keys(sample_env):
    result = sort_alphabetically(sample_env)
    keys = [k for k, _ in result]
    assert keys == sorted(keys)


def test_sort_alphabetically_returns_all_items(sample_env):
    result = sort_alphabetically(sample_env)
    assert len(result) == len(sample_env)


def test_group_by_prefix_creates_groups(sample_env):
    result = group_by_prefix(sample_env)
    assert "DB" in result.grouped
    assert "AWS" in result.grouped


def test_group_by_prefix_ungrouped_contains_solo_keys(sample_env):
    result = group_by_prefix(sample_env)
    ungrouped_keys = [k for k, _ in result.ungrouped]
    assert "DEBUG" in ungrouped_keys
    assert "PORT" in ungrouped_keys


def test_group_by_prefix_min_group_size_respected():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "SOLO_KEY": "val"}
    result = group_by_prefix(env, min_group_size=2)
    assert "DB" in result.grouped
    ungrouped_keys = [k for k, _ in result.ungrouped]
    assert "SOLO_KEY" in ungrouped_keys


def test_group_by_prefix_items_sorted_within_group(sample_env):
    result = group_by_prefix(sample_env)
    db_keys = [k for k, _ in result.grouped["DB"]]
    assert db_keys == sorted(db_keys)


def test_render_sorted_includes_prefix_headers(sample_env):
    result = group_by_prefix(sample_env)
    output = render_sorted(result, show_prefix_headers=True)
    assert "# [DB]" in output
    assert "# [AWS]" in output


def test_render_sorted_no_headers(sample_env):
    result = group_by_prefix(sample_env)
    output = render_sorted(result, show_prefix_headers=False)
    assert "# [DB]" not in output


def test_render_sorted_contains_all_key_value_pairs(sample_env):
    result = group_by_prefix(sample_env)
    output = render_sorted(result)
    for key, value in sample_env.items():
        assert f"{key}={value}" in output


def test_render_sorted_empty_env():
    result = group_by_prefix({})
    output = render_sorted(result)
    assert output.strip() == ""
