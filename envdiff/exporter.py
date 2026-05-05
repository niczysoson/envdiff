"""Export diff or validation results to structured formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Union

from envdiff.differ import DiffResult
from envdiff.validator import ValidationResult


def _diff_to_dict(result: DiffResult) -> dict:
    return {
        "missing_in_target": sorted(result.missing_in_target),
        "missing_in_source": sorted(result.missing_in_source),
        "mismatched": {
            k: {"source": v[0], "target": v[1]}
            for k, v in sorted(result.mismatched.items())
        },
    }


def _validation_to_dict(result: ValidationResult) -> dict:
    return {
        "missing_keys": sorted(result.missing_keys),
        "pattern_violations": {
            k: v for k, v in sorted(result.pattern_violations.items())
        },
    }


def export_json(result: Union[DiffResult, ValidationResult], indent: int = 2) -> str:
    """Serialize a DiffResult or ValidationResult to a JSON string."""
    if isinstance(result, DiffResult):
        data = _diff_to_dict(result)
    elif isinstance(result, ValidationResult):
        data = _validation_to_dict(result)
    else:
        raise TypeError(f"Unsupported result type: {type(result)!r}")
    return json.dumps(data, indent=indent)


def export_csv(result: Union[DiffResult, ValidationResult]) -> str:
    """Serialize a DiffResult or ValidationResult to a CSV string.

    Each row has columns: kind, key, detail
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["kind", "key", "detail"])

    if isinstance(result, DiffResult):
        for key in sorted(result.missing_in_target):
            writer.writerow(["missing_in_target", key, ""])
        for key in sorted(result.missing_in_source):
            writer.writerow(["missing_in_source", key, ""])
        for key, (src, tgt) in sorted(result.mismatched.items()):
            writer.writerow(["mismatched", key, f"source={src!r} target={tgt!r}"])
    elif isinstance(result, ValidationResult):
        for key in sorted(result.missing_keys):
            writer.writerow(["missing_key", key, ""])
        for key, pattern in sorted(result.pattern_violations.items()):
            writer.writerow(["pattern_violation", key, f"pattern={pattern!r}"])
    else:
        raise TypeError(f"Unsupported result type: {type(result)!r}")

    return buf.getvalue()
