"""Unit tests for envdiff.comparator."""
import pytest

from envdiff.comparator import CompareResult, compare_many, summary_table
from envdiff.differ import DiffResult


@pytest.fixture()
def source() -> dict:
    return {"A": "1", "B": "2", "C": "3"}


@pytest.fixture()
def targets(source) -> dict:
    return {
        "staging": {"A": "1", "B": "2", "C": "3"},
        "production": {"A": "1", "C": "99"},
        "review": {"A": "1", "B": "2", "C": "3", "D": "4"},
    }


def test_compare_many_returns_compare_result(source, targets):
    result = compare_many(source, targets, source_file=".env")
    assert isinstance(result, CompareResult)


def test_compare_many_has_entry_per_target(source, targets):
    result = compare_many(source, targets)
    assert set(result.target_files) == {"staging", "production", "review"}


def test_compare_many_no_diff_for_identical(source, targets):
    result = compare_many(source, targets)
    diff: DiffResult = result.results["staging"]
    assert not diff.missing_in_target
    assert not diff.missing_in_source
    assert not diff.mismatched


def test_compare_many_detects_missing_in_target(source, targets):
    result = compare_many(source, targets)
    diff = result.results["production"]
    assert "B" in diff.missing_in_target


def test_compare_many_detects_mismatch(source, targets):
    result = compare_many(source, targets)
    diff = result.results["production"]
    assert "C" in diff.mismatched


def test_compare_many_detects_extra_key(source, targets):
    result = compare_many(source, targets)
    diff = result.results["review"]
    assert "D" in diff.missing_in_source


def test_any_differences_true_when_diffs_exist(source, targets):
    result = compare_many(source, targets)
    assert result.any_differences is True


def test_any_differences_false_when_all_match(source):
    result = compare_many(source, {"same": source.copy()})
    assert result.any_differences is False


def test_summary_table_returns_one_line_per_target(source, targets):
    result = compare_many(source, targets)
    lines = summary_table(result)
    assert len(lines) == len(targets)


def test_summary_table_line_format(source, targets):
    result = compare_many(source, targets)
    lines = summary_table(result)
    for line in lines:
        assert "missing" in line
        assert "extra" in line
        assert "mismatched" in line


def test_compare_many_empty_targets(source):
    result = compare_many(source, {})
    assert result.target_files == []
    assert result.any_differences is False


def test_source_file_stored(source, targets):
    result = compare_many(source, targets, source_file="my.env")
    assert result.source_file == "my.env"
