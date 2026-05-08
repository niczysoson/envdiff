"""Integration tests: parse real files then compare."""
from pathlib import Path

import pytest

from envdiff.comparator import compare_many, summary_table
from envdiff.parser import parse_env_file


@pytest.fixture()
def src_file(tmp_path: Path) -> Path:
    p = tmp_path / "base.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc\n")
    return p


@pytest.fixture()
def staging_file(tmp_path: Path) -> Path:
    p = tmp_path / "staging.env"
    p.write_text("DB_HOST=staging-db\nDB_PORT=5432\nSECRET_KEY=abc\n")
    return p


@pytest.fixture()
def prod_file(tmp_path: Path) -> Path:
    p = tmp_path / "prod.env"
    p.write_text("DB_HOST=prod-db\nDB_PORT=5432\n")
    return p


def test_integration_no_missing_keys_staging(src_file, staging_file):
    src = parse_env_file(str(src_file))
    targets = {"staging": parse_env_file(str(staging_file))}
    result = compare_many(src, targets, source_file=str(src_file))
    diff = result.results["staging"]
    assert not diff.missing_in_target
    assert not diff.missing_in_source


def test_integration_detects_missing_secret_in_prod(src_file, prod_file):
    src = parse_env_file(str(src_file))
    targets = {"prod": parse_env_file(str(prod_file))}
    result = compare_many(src, targets)
    diff = result.results["prod"]
    assert "SECRET_KEY" in diff.missing_in_target


def test_integration_summary_table_has_correct_counts(src_file, staging_file, prod_file):
    src = parse_env_file(str(src_file))
    targets = {
        "staging": parse_env_file(str(staging_file)),
        "prod": parse_env_file(str(prod_file)),
    }
    result = compare_many(src, targets)
    lines = summary_table(result)
    assert len(lines) == 2


def test_integration_any_differences_reflects_prod(src_file, staging_file, prod_file):
    src = parse_env_file(str(src_file))
    targets = {
        "staging": parse_env_file(str(staging_file)),
        "prod": parse_env_file(str(prod_file)),
    }
    result = compare_many(src, targets)
    assert result.any_differences is True
