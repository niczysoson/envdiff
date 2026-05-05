"""Tests for envdiff.exporter — JSON and CSV export helpers."""

import csv
import io
import json

import pytest

from envdiff.differ import DiffResult
from envdiff.exporter import export_csv, export_json
from envdiff.validator import ValidationResult


@pytest.fixture()
def diff_result():
    return DiffResult(
        missing_in_target={"MISSING_KEY"},
        missing_in_source={"EXTRA_KEY"},
        mismatched={"HOST": ("localhost", "prod.example.com")},
    )


@pytest.fixture()
def validation_result():
    return ValidationResult(
        missing_keys={"SECRET_KEY"},
        pattern_violations={"PORT": r"^\d+$"},
    )


# --- JSON export ---

def test_export_json_diff_structure(diff_result):
    raw = export_json(diff_result)
    data = json.loads(raw)
    assert "missing_in_target" in data
    assert "missing_in_source" in data
    assert "mismatched" in data


def test_export_json_diff_values(diff_result):
    data = json.loads(export_json(diff_result))
    assert "MISSING_KEY" in data["missing_in_target"]
    assert "EXTRA_KEY" in data["missing_in_source"]
    assert data["mismatched"]["HOST"] == {"source": "localhost", "target": "prod.example.com"}


def test_export_json_validation_structure(validation_result):
    data = json.loads(export_json(validation_result))
    assert "missing_keys" in data
    assert "pattern_violations" in data


def test_export_json_validation_values(validation_result):
    data = json.loads(export_json(validation_result))
    assert "SECRET_KEY" in data["missing_keys"]
    assert data["pattern_violations"]["PORT"] == r"^\d+$"


def test_export_json_raises_on_unknown_type():
    with pytest.raises(TypeError):
        export_json(object())  # type: ignore[arg-type]


# --- CSV export ---

def _parse_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def test_export_csv_diff_headers(diff_result):
    rows = _parse_csv(export_csv(diff_result))
    assert rows[0].keys() == {"kind", "key", "detail"}


def test_export_csv_diff_rows(diff_result):
    rows = _parse_csv(export_csv(diff_result))
    kinds = {r["kind"] for r in rows}
    assert "missing_in_target" in kinds
    assert "missing_in_source" in kinds
    assert "mismatched" in kinds


def test_export_csv_validation_rows(validation_result):
    rows = _parse_csv(export_csv(validation_result))
    kinds = {r["kind"] for r in rows}
    assert "missing_key" in kinds
    assert "pattern_violation" in kinds


def test_export_csv_raises_on_unknown_type():
    with pytest.raises(TypeError):
        export_csv(object())  # type: ignore[arg-type]
