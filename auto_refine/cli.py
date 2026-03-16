from __future__ import annotations

import argparse

from .engine import run_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="auto_refine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run a generic bounded optimization task")
    run_parser.add_argument("config", help="path to task.json")
    run_parser.add_argument("--iterations", type=int, default=None, help="override iteration count")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_dir = run_from_config(args.config, iteration_override=args.iterations)
        print(f"[complete] run_dir={run_dir}")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
