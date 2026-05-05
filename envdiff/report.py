"""Formatting and rendering of diff results for CLI output."""

from typing import Optional
from envdiff.differ import DiffResult


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_report(
    result: DiffResult,
    source_label: str = "source",
    target_label: str = "target",
    use_color: bool = True,
    show_values: bool = False,
) -> str:
    """Format a DiffResult into a human-readable report string.

    Args:
        result: The diff result to render.
        source_label: Display name for the source env file.
        target_label: Display name for the target env file.
        use_color: Whether to emit ANSI color codes.
        show_values: Whether to display actual values in mismatches.

    Returns:
        Formatted report as a string.
    """
    lines = []

    header = f"Comparing {source_label} → {target_label}"
    lines.append(_colorize(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    if result.missing_in_target:
        label = _colorize(f"Missing in {target_label}:", ANSI_RED, use_color)
        lines.append(label)
        for key in result.missing_in_target:
            lines.append(f"  - {key}")

    if result.missing_in_source:
        label = _colorize(f"Extra in {target_label} (not in {source_label}):", ANSI_YELLOW, use_color)
        lines.append(label)
        for key in result.missing_in_source:
            lines.append(f"  + {key}")

    if result.mismatched:
        label = _colorize("Mismatched values:", ANSI_YELLOW, use_color)
        lines.append(label)
        for key, (src_val, tgt_val) in sorted(result.mismatched.items()):
            if show_values:
                lines.append(f"  ~ {key}: {src_val!r} → {tgt_val!r}")
            else:
                lines.append(f"  ~ {key}")

    if not result.has_differences:
        lines.append(_colorize("No differences found.", ANSI_GREEN, use_color))
    else:
        total = (
            len(result.missing_in_target)
            + len(result.missing_in_source)
            + len(result.mismatched)
        )
        summary = _colorize(f"\n{total} issue(s) found.", ANSI_RED, use_color)
        lines.append(summary)

    return "\n".join(lines)
