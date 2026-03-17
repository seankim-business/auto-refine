from __future__ import annotations

import argparse

from .demo import build_demo_data
from .engine import resume_from_config, run_from_config
from .goal_tree import run_goal_tree


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="auto_refine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run a generic bounded optimization task")
    run_parser.add_argument("config", help="path to task.json")
    run_parser.add_argument("--iterations", type=int, default=None, help="override iteration count")

    resume_parser = subparsers.add_parser("resume", help="resume the latest run for a task up to a total trial budget")
    resume_parser.add_argument("--task", required=True, help="path to task.json")
    resume_parser.add_argument("--budget", required=True, type=int, help="total trial budget to reach across resumed execution")

    demo_parser = subparsers.add_parser("build-demo-data", help="build demo-data.json from runtime summaries")
    demo_parser.add_argument("config", help="path to demo-config.json")
    demo_parser.add_argument("--output", required=True, help="path to write generated demo-data.json")

    tree_parser = subparsers.add_parser("run-goal-tree", help="run a recursive goal/hypothesis tree")
    tree_parser.add_argument("config", help="path to goal-tree json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        run_dir = run_from_config(args.config, iteration_override=args.iterations)
        print(f"[complete] run_dir={run_dir}")
        return 0
    if args.command == "resume":
        run_dir = resume_from_config(args.task, budget=args.budget)
        print(f"[complete] resumed_run_dir={run_dir}")
        return 0
    if args.command == "build-demo-data":
        build_demo_data(args.config, output_path=args.output)
        print(f"[complete] demo_data={args.output}")
        return 0
    if args.command == "run-goal-tree":
        run_dir = run_goal_tree(args.config)
        print(f"[complete] goal_tree_run_dir={run_dir}")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2
