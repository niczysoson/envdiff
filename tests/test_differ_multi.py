"""Tests for envdiff.differ_multi."""
import pytest
from envdiff.differ_multi import (
    MultiDiffResult,
    MultiDiffEntry,
    diff_one_to_many,
    format_multi_diff_report,
)
from envdiff.differ import DiffResult


SOURCE = {"A": "1", "B": "2", "C": "3"}
TARGET_FULL = {"A": "1", "B": "2", "C": "3"}
TARGET_MISSING = {"A": "1", "B": "2"}
TARGET_MISMATCH = {"A": "1", "B": "99", "C": "3"}
TARGET_EXTRA = {"A": "1", "B": "2", "C": "3", "D": "4"}


def test_diff_one_to_many_returns_multi_diff_result():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_FULL)])
    assert isinstance(result, MultiDiffResult)


def test_diff_one_to_many_entry_count_matches_targets():
    targets = [("staging", TARGET_FULL), ("prod", TARGET_MISSING)]
    result = diff_one_to_many(SOURCE, targets)
    assert len(result.entries) == 2


def test_diff_one_to_many_no_differences_when_identical():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_FULL)])
    assert not result.any_differences()


def test_diff_one_to_many_detects_missing_in_target():
    result = diff_one_to_many(SOURCE, [("prod", TARGET_MISSING)])
    assert result.any_differences()
    assert "C" in result.entries[0].result.missing_in_target


def test_diff_one_to_many_detects_mismatch():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_MISMATCH)])
    assert "B" in result.entries[0].result.mismatched


def test_diff_one_to_many_detects_missing_in_source():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_EXTRA)])
    assert "D" in result.entries[0].result.missing_in_source


def test_labels_with_differences_returns_correct_labels():
    targets = [("staging", TARGET_FULL), ("prod", TARGET_MISSING)]
    result = diff_one_to_many(SOURCE, targets)
    assert result.labels_with_differences() == ["prod"]


def test_labels_with_differences_empty_when_all_ok():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_FULL)])
    assert result.labels_with_differences() == []


def test_format_report_shows_all_ok_when_no_diffs():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_FULL)], source_file=".env")
    report = format_multi_diff_report(result)
    assert "All targets match source." in report


def test_format_report_shows_missing_in_target():
    result = diff_one_to_many(SOURCE, [("prod", TARGET_MISSING)], source_file=".env")
    report = format_multi_diff_report(result)
    assert "MISSING IN TARGET" in report
    assert "C" in report


def test_format_report_shows_mismatch():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_MISMATCH)], source_file=".env")
    report = format_multi_diff_report(result)
    assert "MISMATCH" in report
    assert "B" in report


def test_format_report_includes_source_file():
    result = diff_one_to_many(SOURCE, [("staging", TARGET_FULL)], source_file="my.env")
    report = format_multi_diff_report(result)
    assert "my.env" in report


def test_format_report_ok_label_when_target_matches():
    targets = [("staging", TARGET_FULL), ("prod", TARGET_MISSING)]
    result = diff_one_to_many(SOURCE, targets, source_file=".env")
    report = format_multi_diff_report(result)
    assert "OK" in report
