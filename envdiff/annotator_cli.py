"""CLI commands for the annotator feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.annotator import annotate_from_diff, annotate_from_validation
from envdiff.differ import diff_envs
from envdiff.parser import parse_env_file
from envdiff.validator import validate_env


def _parse_rules(rules_arg: Optional[str]) -> dict:
    if not rules_arg:
        return {}
    rules: dict = {"required": [], "patterns": {}}
    for token in rules_arg.split(","):
        token = token.strip()
        if "=" in token:
            k, pat = token.split("=", 1)
            rules["patterns"][k.strip()] = pat.strip()
        else:
            rules["required"].append(token)
    return rules


def cmd_annotate_diff(args: argparse.Namespace) -> int:
    try:
        source = parse_env_file(args.source)
        target = parse_env_file(args.target)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    diff = diff_envs(source, target)
    result = annotate_from_diff(source, diff)
    print(result.as_text(include_values=not args.redact))
    return 0


def cmd_annotate_validate(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.source)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    rules = _parse_rules(getattr(args, "rules", None))
    required: List[str] = rules.get("required", [])
    patterns: dict = rules.get("patterns", {})
    validation = validate_env(env, required_keys=required, patterns=patterns)
    result = annotate_from_validation(env, validation)
    print(result.as_text(include_values=not args.redact))
    return 0


def register_annotator_commands(subparsers: argparse._SubParsersAction) -> None:
    diff_p = subparsers.add_parser(
        "annotate-diff", help="Annotate a .env file with diff status vs another file"
    )
    diff_p.add_argument("source", help="Source .env file")
    diff_p.add_argument("target", help="Target .env file to diff against")
    diff_p.add_argument("--redact", action="store_true", help="Hide values in output")
    diff_p.set_defaults(func=cmd_annotate_diff)

    val_p = subparsers.add_parser(
        "annotate-validate", help="Annotate a .env file with validation status"
    )
    val_p.add_argument("source", help="Source .env file")
    val_p.add_argument(
        "--rules",
        default=None,
        help="Comma-separated required keys or KEY=PATTERN pairs",
    )
    val_p.add_argument("--redact", action="store_true", help="Hide values in output")
    val_p.set_defaults(func=cmd_annotate_validate)
