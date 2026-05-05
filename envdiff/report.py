"""Formatting and colorizing diff reports."""

from envdiff.differ import DiffResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    """Wrap *text* in ANSI escape codes when *use_color* is True."""
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def format_report(
    result: DiffResult,
    source_label: str = "source",
    target_label: str = "target",
    use_color: bool = True,
) -> str:
    """Return a human-readable diff report string."""
    lines: list[str] = []

    header = _colorize(
        f"envdiff: {source_label}  →  {target_label}", _BOLD, use_color
    )
    lines.append(header)
    lines.append(_colorize("-" * 60, _BOLD, use_color))

    if result.missing_in_target:
        lines.append(_colorize("Missing in target:", _RED, use_color))
        for key in sorted(result.missing_in_target):
            lines.append(f"  {_colorize('-', _RED, use_color)} {key}")

    if result.missing_in_source:
        lines.append(_colorize("Extra in target (not in source):", _YELLOW, use_color))
        for key in sorted(result.missing_in_source):
            lines.append(f"  {_colorize('+', _YELLOW, use_color)} {key}")

    if result.mismatched:
        lines.append(_colorize("Mismatched values:", _YELLOW, use_color))
        for key, (src_val, tgt_val) in sorted(result.mismatched.items()):
            lines.append(f"  {_colorize('~', _YELLOW, use_color)} {key}")
            lines.append(
                f"      {_colorize('source:', _BOLD, use_color)} {src_val!r}"
            )
            lines.append(
                f"      {_colorize('target:', _BOLD, use_color)} {tgt_val!r}"
            )

    if not (result.missing_in_target or result.missing_in_source or result.mismatched):
        lines.append(_colorize("No differences found.", _GREEN, use_color))
    else:
        total = (
            len(result.missing_in_target)
            + len(result.missing_in_source)
            + len(result.mismatched)
        )
        summary_line = f"{total} issue(s) found."
        lines.append(_colorize(summary_line, _RED, use_color))

    return "\n".join(lines)
