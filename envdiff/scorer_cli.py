"""CLI command for the env scorer."""
from __future__ import annotations

import argparse

from envdiff.parser import parse_env_file
from envdiff.scorer import format_score_report, score_env


def cmd_score(args: argparse.Namespace) -> int:
    """Run the scorer command and print the report."""
    env = parse_env_file(args.file)
    result = score_env(env, source=args.file)
    print(format_score_report(result, color=not args.no_color))
    if args.fail_below is not None and result.score < args.fail_below:
        return 1
    return 0


def register_scorer_commands(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    """Attach the 'score' subcommand to the given subparsers."""
    parser = subparsers.add_parser(
        "score",
        help="Score an env file for overall health (0-100).",
    )
    parser.add_argument("file", help="Path to the .env file to score.")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output.",
    )
    parser.add_argument(
        "--fail-below",
        type=int,
        default=None,
        metavar="N",
        help="Exit with code 1 if score is below N.",
    )
    parser.set_defaults(func=cmd_score)
