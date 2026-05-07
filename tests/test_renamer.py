"""Unit tests for envdiff.renamer."""
import pytest
from envdiff.renamer import RenameResult, rename_keys, format_rename_report


@pytest.fixture()
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
    }


def test_rename_single_key(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.renamed
    assert "DB_HOST" not in result.renamed
    assert result.renamed["DATABASE_HOST"] == "localhost"


def test_rename_preserves_other_keys(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_PORT" in result.renamed
    assert "APP_SECRET" in result.renamed


def test_rename_missing_key_goes_to_skipped(base_env):
    result = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.renamed


def test_rename_conflict_skipped_without_overwrite(base_env):
    # DB_PORT already exists; renaming DB_HOST -> DB_PORT should be skipped
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"})
    assert "DB_HOST" in result.skipped
    assert result.renamed["DB_PORT"] == "5432"  # original value preserved


def test_rename_conflict_allowed_with_overwrite(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"}, overwrite=True)
    assert ("DB_HOST", "DB_PORT") in result.applied
    assert result.renamed["DB_PORT"] == "localhost"


def test_rename_multiple_keys(base_env):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(base_env, mapping)
    assert "DATABASE_HOST" in result.renamed
    assert "DATABASE_PORT" in result.renamed
    assert len(result.applied) == 2


def test_applied_contains_old_new_tuple(base_env):
    result = rename_keys(base_env, {"APP_SECRET": "APP_KEY"})
    assert ("APP_SECRET", "APP_KEY") in result.applied


def test_format_report_shows_renamed():
    result = RenameResult(
        renamed={"NEW": "val"},
        applied=[("OLD", "NEW")],
        skipped=[],
    )
    report = format_rename_report(result)
    assert "OLD -> NEW" in report


def test_format_report_shows_skipped():
    result = RenameResult(
        renamed={},
        applied=[],
        skipped=["GHOST"],
    )
    report = format_rename_report(result)
    assert "GHOST" in report


def test_format_report_no_renames_message():
    result = RenameResult(renamed={}, applied=[], skipped=[])
    report = format_rename_report(result)
    assert "No keys renamed" in report


def test_format_report_color_wraps_ansi():
    result = RenameResult(
        renamed={"B": "v"},
        applied=[("A", "B")],
        skipped=[],
    )
    report = format_rename_report(result, color=True)
    assert "\033[" in report
