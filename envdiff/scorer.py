"""Score an env file for overall health based on multiple signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.linter import lint_env
from envdiff.profiler import profile_env
from envdiff.scanner import scan_env_file


@dataclass
class ScoreResult:
    source: str
    total_keys: int
    score: int  # 0-100
    penalties: List[str] = field(default_factory=list)
    breakdown: Dict[str, int] = field(default_factory=dict)


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def score_env(env: Dict[str, str], source: str = "<env>") -> ScoreResult:
    """Compute a health score (0-100) for the given env mapping."""
    penalties: List[str] = []
    breakdown: Dict[str, int] = {}
    deductions = 0

    lint = lint_env(env)
    lint_issues = len(lint.invalid_keys) + len(lint.placeholder_keys)
    lint_deduction = min(30, lint_issues * 5)
    breakdown["lint"] = lint_deduction
    if lint_deduction:
        penalties.append(
            f"{lint_issues} lint issue(s) (-{lint_deduction})"
        )
    deductions += lint_deduction

    profile = profile_env(env)
    empty_deduction = min(20, profile.empty_count * 4)
    breakdown["empty_values"] = empty_deduction
    if empty_deduction:
        penalties.append(
            f"{profile.empty_count} empty value(s) (-{empty_deduction})"
        )
    deductions += empty_deduction

    scan = scan_env_file(env, source)
    suspicious_deduction = min(30, len(scan.suspicious) * 6)
    dup_deduction = min(10, len(scan.duplicates) * 5)
    breakdown["suspicious"] = suspicious_deduction
    breakdown["duplicates"] = dup_deduction
    if suspicious_deduction:
        penalties.append(
            f"{len(scan.suspicious)} suspicious value(s) (-{suspicious_deduction})"
        )
    if dup_deduction:
        penalties.append(
            f"{len(scan.duplicates)} duplicate key(s) (-{dup_deduction})"
        )
    deductions += suspicious_deduction + dup_deduction

    score = _clamp(100 - deductions)
    return ScoreResult(
        source=source,
        total_keys=len(env),
        score=score,
        penalties=penalties,
        breakdown=breakdown,
    )


def format_score_report(result: ScoreResult, *, color: bool = True) -> str:
    """Render a human-readable score report."""
    def _c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    grade_color = "32" if result.score >= 80 else ("33" if result.score >= 50 else "31")
    lines = [
        f"Health score for {_c(result.source, '1')}: "
        f"{_c(str(result.score) + '/100', grade_color)} "
        f"({result.total_keys} keys)",
    ]
    if result.penalties:
        lines.append("Penalties:")
        for p in result.penalties:
            lines.append(f"  - {_c(p, '33')}")
    else:
        lines.append(_c("  No issues detected.", "32"))
    return "\n".join(lines)
