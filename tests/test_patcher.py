"""Unit tests for envdiff.patcher."""
import pytest

from envdiff.patcher import (
    PatchResult,
    has_changes,
    patch_env,
    render_patch_report,
)


@pytest.fixture()
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "false"}


def test_patch_updates_existing_key(base_env):
    result = patch_env(base_env, {"DEBUG": "true"})
    assert result.patched["DEBUG"] == "true"
    assert "DEBUG" in result.applied


def test_patch_adds_missing_key_by_default(base_env):
    result = patch_env(base_env, {"NEW_KEY": "new_val"})
    assert result.patched["NEW_KEY"] == "new_val"
    assert "NEW_KEY" in result.added


def test_patch_no_add_skips_missing_key(base_env):
    result = patch_env(base_env, {"NEW_KEY": "new_val"}, add_missing=False)
    assert "NEW_KEY" not in result.patched
    assert "NEW_KEY" in result.skipped


def test_patch_skip_existing_leaves_key_unchanged(base_env):
    result = patch_env(base_env, {"DEBUG": "true"}, skip_existing=True)
    assert result.patched["DEBUG"] == "false"
    assert "DEBUG" in result.skipped
    assert "DEBUG" not in result.applied


def test_patch_preserves_untouched_keys(base_env):
    result = patch_env(base_env, {"DB_HOST": "remotehost"})
    assert result.patched["DB_PORT"] == "5432"


def test_patch_original_is_not_mutated(base_env):
    original_copy = dict(base_env)
    patch_env(base_env, {"DB_HOST": "changed"})
    assert base_env == original_copy


def test_has_changes_true_when_applied(base_env):
    result = patch_env(base_env, {"DEBUG": "true"})
    assert has_changes(result) is True


def test_has_changes_true_when_added(base_env):
    result = patch_env(base_env, {"EXTRA": "val"})
    assert has_changes(result) is True


def test_has_changes_false_when_only_skipped(base_env):
    result = patch_env(base_env, {"DEBUG": "true"}, skip_existing=True)
    assert has_changes(result) is False


def test_render_report_shows_updated(base_env):
    result = patch_env(base_env, {"DEBUG": "true"})
    report = render_patch_report(result)
    assert "Updated keys" in report
    assert "DEBUG" in report


def test_render_report_shows_added(base_env):
    result = patch_env(base_env, {"BRAND_NEW": "yes"})
    report = render_patch_report(result)
    assert "Added keys" in report
    assert "BRAND_NEW" in report


def test_render_report_shows_skipped(base_env):
    result = patch_env(base_env, {"DEBUG": "true"}, skip_existing=True)
    report = render_patch_report(result)
    assert "Skipped keys" in report


def test_render_report_no_changes_message(base_env):
    result = patch_env(base_env, {}, add_missing=False)
    report = render_patch_report(result)
    assert "No changes applied" in report


def test_render_report_color_contains_ansi(base_env):
    result = patch_env(base_env, {"DEBUG": "true"})
    report = render_patch_report(result, color=True)
    assert "\033[" in report


def test_render_report_no_color_no_ansi(base_env):
    result = patch_env(base_env, {"DEBUG": "true"})
    report = render_patch_report(result, color=False)
    assert "\033[" not in report
