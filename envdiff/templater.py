"""Generate .env.example template files from existing env data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateResult:
    keys: List[str] = field(default_factory=list)
    redacted: Dict[str, str] = field(default_factory=dict)
    comments: Dict[str, str] = field(default_factory=dict)


_PLACEHOLDER = "<REPLACE_ME>"


def _redact_value(value: str, placeholder: str = _PLACEHOLDER) -> str:
    """Replace a real value with a placeholder string."""
    return placeholder


def build_template(
    env: Dict[str, str],
    keep_keys: Optional[List[str]] = None,
    placeholder: str = _PLACEHOLDER,
    comments: Optional[Dict[str, str]] = None,
) -> TemplateResult:
    """Build a template from an env dict, redacting all values.

    Args:
        env: Source environment variables.
        keep_keys: Keys whose values should be preserved as-is.
        placeholder: String to use for redacted values.
        comments: Optional per-key comments to include in output.
    """
    keep = set(keep_keys or [])
    result = TemplateResult()
    result.keys = sorted(env.keys())
    for key in result.keys:
        if key in keep:
            result.redacted[key] = env[key]
        else:
            result.redacted[key] = _redact_value(env[key], placeholder)
    if comments:
        result.comments = {k: v for k, v in comments.items() if k in env}
    return result


def render_template(result: TemplateResult) -> str:
    """Render a TemplateResult as .env.example file content."""
    lines: List[str] = []
    for key in result.keys:
        if key in result.comments:
            lines.append(f"# {result.comments[key]}")
        value = result.redacted.get(key, _PLACEHOLDER)
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def merge_templates(base: TemplateResult, override: TemplateResult) -> TemplateResult:
    """Merge two TemplateResults, with override taking precedence.

    Keys present in either result are included. Values and comments from
    ``override`` take precedence over those in ``base`` when both define
    the same key.

    Args:
        base: The base template result.
        override: The template result whose values win on conflict.

    Returns:
        A new TemplateResult combining both inputs.
    """
    merged = TemplateResult()
    all_keys = dict.fromkeys(base.keys)
    all_keys.update(dict.fromkeys(override.keys))
    merged.keys = sorted(all_keys)
    merged.redacted = {**base.redacted, **override.redacted}
    merged.comments = {**base.comments, **override.comments}
    return merged
