"""Integration tests: parse real .env files and run timeline diff end-to-end."""

from __future__ import annotations

import os
import pytest

from envdiff.parser import parse_env_file
from envdiff.snapshotter import create_snapshot
from envdiff.differ_timeline import diff_timeline


@pytest.fixture()
def env_v1(tmp_path):
    p = tmp_path / "v1.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    return str(p)


@pytest.fixture()
def env_v2(tmp_path):
    p = tmp_path / "v2.env"
    p.write_text("DB_HOST=prod.db\nDB_PORT=5432\nSECRET=abc\nNEW_FLAG=true\n")
    return str(p)


@pytest.fixture()
def env_v3(tmp_path):
    p = tmp_path / "v3.env"
    p.write_text("DB_HOST=prod.db\nDB_PORT=5433\nNEW_FLAG=true\n")
    return str(p)


def _load(path):
    return create_snapshot(parse_env_file(path), source_file=path)


def test_integration_no_changes_same_file(env_v1):
    s = _load(env_v1)
    result = diff_timeline([s, s])
    assert not result.any_changes


def test_integration_detects_host_change(env_v1, env_v2):
    result = diff_timeline([_load(env_v1), _load(env_v2)])
    assert "DB_HOST" in result.entries[0].changed


def test_integration_detects_new_flag_added(env_v1, env_v2):
    result = diff_timeline([_load(env_v1), _load(env_v2)])
    assert "NEW_FLAG" in result.entries[0].added


def test_integration_three_steps_entry_count(env_v1, env_v2, env_v3):
    result = diff_timeline([_load(env_v1), _load(env_v2), _load(env_v3)])
    assert len(result.entries) == 2


def test_integration_secret_removed_in_v3(env_v2, env_v3):
    result = diff_timeline([_load(env_v2), _load(env_v3)])
    assert "SECRET" in result.entries[0].removed


def test_integration_total_changes_across_all_steps(env_v1, env_v2, env_v3):
    result = diff_timeline([_load(env_v1), _load(env_v2), _load(env_v3)])
    # step1: DB_HOST changed, NEW_FLAG added => 2
    # step2: SECRET removed, DB_PORT changed => 2
    assert result.total_changes == 4
