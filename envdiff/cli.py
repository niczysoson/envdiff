"""Command-line interface for envdiff."""

import sys
import argparse
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs, has_differences
from envdiff.report import format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff .env files across environments and flag missing or mismatched variables.",
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="Path to the source .env file (e.g. .env.example).",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target .env file (e.g. .env).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    target_path = Path(args.target)

    for path in (source_path, target_path):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    source_env = parse_env_file(source_path)
    target_env = parse_env_file(target_path)

    result = diff_envs(source_env, target_env)
    report = format_report(
        result,
        source_label=str(source_path),
        target_label=str(target_path),
        use_color=not args.no_color,
    )
    print(report)

    if args.exit_code and has_differences(result):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
