"""Tests for envdiff.merger module."""

import pytest

from envdiff.merger import MergeResult, merge_envs, render_merged


@pytest.fixture
def env_alpha():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"}


@pytest.fixture
def env_beta():
    return {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET_KEY": "abc123"}


@pytest.fixture
def env_gamma():
    return {"DB_HOST": "staging.db", "LOG_LEVEL": "info"}


def test_merge_collects_all_keys(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta})
    assert "DB_HOST" in result.all_keys
    assert "DB_PORT" in result.all_keys
    assert "DEBUG" in result.all_keys
    assert "SECRET_KEY" in result.all_keys


def test_merge_no_conflict_when_values_match(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta})
    assert "DB_PORT" not in result.conflict_keys
    assert result.keys["DB_PORT"] == "5432"


def test_merge_detects_conflict_on_differing_values(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta})
    assert "DB_HOST" in result.conflict_keys
    assert "localhost" in result.conflicts["DB_HOST"]
    assert "prod.db" in result.conflicts["DB_HOST"]


def test_merge_prefer_overrides_conflict(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta}, prefer="beta")
    assert result.keys["DB_HOST"] == "prod.db"


def test_merge_prefer_falls_back_when_not_present(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta}, prefer="unknown")
    # Should still resolve without error, using first source value
    assert result.keys["DB_HOST"] in ("localhost", "prod.db")


def test_merge_tracks_sources(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta})
    assert "alpha" in result.sources["DEBUG"]
    assert "beta" not in result.sources["DEBUG"]
    assert "beta" in result.sources["SECRET_KEY"]


def test_merge_three_sources(env_alpha, env_beta, env_gamma):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta, "gamma": env_gamma})
    assert "LOG_LEVEL" in result.all_keys
    assert "DB_HOST" in result.conflict_keys
    assert len(result.conflicts["DB_HOST"]) >= 2


def test_merge_empty_envs():
    result = merge_envs({})
    assert result.all_keys == set()
    assert result.conflicts == {}


def test_merge_single_source(env_alpha):
    result = merge_envs({"alpha": env_alpha})
    assert result.conflict_keys == set()
    assert result.keys["DEBUG"] == "true"


def test_render_merged_produces_valid_lines(env_alpha, env_beta):
    result = merge_envs({"alpha": env_alpha, "beta": env_beta})
    output = render_merged(result)
    lines = [l for l in output.strip().splitlines() if l]
    keys_in_output = [line.split("=", 1)[0] for line in lines]
    assert "DB_HOST" in keys_in_output
    assert "SECRET_KEY" in keys_in_output


def test_render_merged_empty_result():
    result = MergeResult()
    assert render_merged(result) == ""


def test_render_merged_sorted_keys():
    envs = {"src": {"ZEBRA": "1", "ALPHA": "2", "MIDDLE": "3"}}
    result = merge_envs(envs)
    output = render_merged(result)
    keys = [line.split("=")[0] for line in output.strip().splitlines()]
    assert keys == sorted(keys)
