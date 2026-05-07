"""Annotate .env files with comments describing each key's status."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.differ import DiffResult
from envdiff.validator import ValidationResult


@dataclass
class AnnotatedLine:
    key: str
    value: Optional[str]
    annotation: str
    is_comment: bool = False


@dataclass
class AnnotationResult:
    lines: List[AnnotatedLine] = field(default_factory=list)

    def as_text(self, include_values: bool = True) -> str:
        output: List[str] = []
        for line in self.lines:
            if line.is_comment:
                output.append(f"# {line.annotation}")
            else:
                value_part = f"={line.value}" if include_values and line.value is not None else "="
                output.append(f"{line.key}{value_part}  # {line.annotation}")
        return "\n".join(output)


def annotate_from_diff(env: Dict[str, str], diff: DiffResult) -> AnnotationResult:
    """Annotate env keys using a DiffResult for context."""
    result = AnnotationResult()
    all_keys = sorted(
        set(env.keys()) | set(diff.missing_in_target) | set(diff.missing_in_source)
    )
    for key in all_keys:
        if key in diff.missing_in_target:
            annotation = "MISSING in target"
        elif key in diff.missing_in_source:
            annotation = "MISSING in source"
        elif key in diff.mismatched:
            annotation = "VALUE MISMATCH"
        else:
            annotation = "ok"
        result.lines.append(
            AnnotatedLine(key=key, value=env.get(key), annotation=annotation)
        )
    return result


def annotate_from_validation(
    env: Dict[str, str], validation: ValidationResult
) -> AnnotationResult:
    """Annotate env keys using a ValidationResult for context."""
    result = AnnotationResult()
    for key in sorted(env.keys()):
        violations = [
            v.message for v in validation.violations if v.key == key
        ]
        annotation = "; ".join(violations) if violations else "ok"
        result.lines.append(
            AnnotatedLine(key=key, value=env[key], annotation=annotation)
        )
    missing = [v for v in validation.violations if v.key not in env]
    for v in missing:
        result.lines.append(
            AnnotatedLine(key=v.key, value=None, annotation=v.message)
        )
    return result
