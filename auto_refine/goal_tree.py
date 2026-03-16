from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .engine import run_from_config


class GoalTreeError(RuntimeError):
    pass


@dataclass(frozen=True)
class GoalNodeSpec:
    name: str
    hypothesis: str
    task_config: Path | None = None
    decomposer_command: list[str] | None = None
    children: list["GoalNodeSpec"] = field(default_factory=list)


@dataclass(frozen=True)
class GoalTreeConfig:
    name: str
    task_root: Path
    output_dir: Path
    max_depth: int
    root: GoalNodeSpec


@dataclass
class GoalNodeResult:
    name: str
    hypothesis: str
    depth: int
    verdict: str
    reason: str
    task_run_dir: str | None = None
    task_baseline_primary: float | None = None
    task_best_primary: float | None = None
    children: list["GoalNodeResult"] = field(default_factory=list)
    error: str | None = None


REQUIRED_GOAL_TREE_FIELDS = {"name", "root"}
REQUIRED_GOAL_NODE_FIELDS = {"name", "hypothesis"}


def _now_slug() -> str:
    return datetime.now().strftime("run-%Y%m%d-%H%M%S")


def _safe_relative(task_root: Path, rel_path: str, must_exist: bool = True) -> Path:
    path = Path(rel_path)
    if path.is_absolute():
        raise GoalTreeError(f"path must be relative: {rel_path}")
    resolved = (task_root / path).resolve()
    root_resolved = task_root.resolve()
    if os.path.commonpath([str(root_resolved), str(resolved)]) != str(root_resolved):
        raise GoalTreeError(f"path escapes task root: {rel_path}")
    if must_exist and not resolved.exists():
        raise GoalTreeError(f"path does not exist: {rel_path}")
    return resolved


def _parse_goal_node(raw: dict[str, Any], task_root: Path) -> GoalNodeSpec:
    missing = REQUIRED_GOAL_NODE_FIELDS - set(raw)
    if missing:
        raise GoalTreeError(f"missing goal node fields: {sorted(missing)}")

    task_config = None
    if raw.get("taskConfig"):
        task_config = _safe_relative(task_root, raw["taskConfig"])

    decomposer_command = None
    if raw.get("decomposerCommand"):
        decomposer_command = list(raw["decomposerCommand"])

    children = [_parse_goal_node(item, task_root) for item in raw.get("children", [])]
    return GoalNodeSpec(
        name=raw["name"],
        hypothesis=raw["hypothesis"],
        task_config=task_config,
        decomposer_command=decomposer_command,
        children=children,
    )


def load_goal_tree_config(config_path: str | Path) -> GoalTreeConfig:
    path = Path(config_path).resolve()
    raw = json.loads(path.read_text())
    missing = REQUIRED_GOAL_TREE_FIELDS - set(raw)
    if missing:
        raise GoalTreeError(f"missing goal tree fields: {sorted(missing)}")

    task_root = (path.parent / raw.get("task_root", ".")).resolve()
    if not task_root.exists():
        raise GoalTreeError(f"task_root does not exist: {task_root}")

    output_dir = (task_root / raw.get("output_dir", "runs/goal-trees")).resolve()
    root_resolved = task_root.resolve()
    if os.path.commonpath([str(root_resolved), str(output_dir)]) != str(root_resolved):
        raise GoalTreeError("output_dir must stay inside task_root")

    max_depth = int(raw.get("max_depth", 16))
    if max_depth < 1:
        raise GoalTreeError("max_depth must be >= 1")

    root = _parse_goal_node(raw["root"], task_root)
    return GoalTreeConfig(
        name=raw["name"],
        task_root=task_root,
        output_dir=output_dir,
        max_depth=max_depth,
        root=root,
    )


def _extract_last_json_line(output: str) -> Any:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise GoalTreeError("no JSON object found in command output")


def _run_command(command: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_path.write_text(proc.stdout)
    return proc.returncode, proc.stdout


def _task_verdict_from_summary(summary_path: Path) -> tuple[bool, float | None, float | None]:
    summary = json.loads(summary_path.read_text())
    primary = summary["primary_metric"]
    baseline = next((r for r in summary["records"] if r.get("phase") == "baseline"), None)
    kept = [r for r in summary["records"] if r.get("decision") == "keep"]
    baseline_value = None
    if baseline and primary in baseline.get("metrics", {}):
        baseline_value = float(baseline["metrics"][primary])
    best_value = None
    if kept:
        best_value = max(float(r["metrics"][primary]) for r in kept)
    return bool(kept), baseline_value, best_value


class GoalTreeRunner:
    def __init__(self, config: GoalTreeConfig, run_dir: Path):
        self.config = config
        self.run_dir = run_dir
        self.log_dir = run_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_config(cls, config_path: str | Path) -> "GoalTreeRunner":
        config = load_goal_tree_config(config_path)
        run_dir = config.output_dir / _now_slug()
        run_dir.mkdir(parents=True, exist_ok=True)
        return cls(config=config, run_dir=run_dir)

    def _base_env(self, depth: int, node_name: str) -> dict[str, str]:
        env = os.environ.copy()
        env["AUTO_REFINE_GOAL_TREE_ROOT"] = str(self.config.task_root)
        env["AUTO_REFINE_GOAL_TREE_RUN_DIR"] = str(self.run_dir)
        env["AUTO_REFINE_GOAL_DEPTH"] = str(depth)
        env["AUTO_REFINE_GOAL_NAME"] = node_name
        return env

    def _children_from_decomposer(self, node: GoalNodeSpec, depth: int) -> list[GoalNodeSpec]:
        if not node.decomposer_command:
            return []
        log_path = self.log_dir / f"depth-{depth}-{node.name}-decomposer.log"
        exit_code, output = _run_command(node.decomposer_command, self.config.task_root, self._base_env(depth, node.name), log_path)
        if exit_code != 0:
            raise GoalTreeError(f"decomposer failed for {node.name}; see {log_path}")
        payload = _extract_last_json_line(output)
        if isinstance(payload, dict):
            raw_children = payload.get("children", [])
        elif isinstance(payload, list):
            raw_children = payload
        else:
            raise GoalTreeError(f"invalid decomposer output for {node.name}")
        return [_parse_goal_node(item, self.config.task_root) for item in raw_children]

    def _run_node(self, node: GoalNodeSpec, depth: int) -> GoalNodeResult:
        if depth > self.config.max_depth:
            return GoalNodeResult(
                name=node.name,
                hypothesis=node.hypothesis,
                depth=depth,
                verdict="rejected",
                reason=f"max_depth {self.config.max_depth} exceeded",
                error="max depth exceeded",
            )

        task_accepted = False
        task_run_dir = None
        baseline_primary = None
        best_primary = None
        reasons: list[str] = []

        if node.task_config:
            try:
                task_run_path = run_from_config(node.task_config)
                task_run_dir = str(task_run_path)
                summary_path = Path(task_run_path) / "summary.json"
                task_accepted, baseline_primary, best_primary = _task_verdict_from_summary(summary_path)
                if task_accepted:
                    reasons.append("node task produced at least one kept candidate")
                else:
                    reasons.append("node task produced no kept candidates")
            except Exception as exc:  # noqa: BLE001
                return GoalNodeResult(
                    name=node.name,
                    hypothesis=node.hypothesis,
                    depth=depth,
                    verdict="rejected",
                    reason="node task failed",
                    task_run_dir=task_run_dir,
                    error=str(exc),
                )

        child_results: list[GoalNodeResult] = []
        try:
            dynamic_children = self._children_from_decomposer(node, depth)
        except Exception as exc:  # noqa: BLE001
            if task_accepted:
                return GoalNodeResult(
                    name=node.name,
                    hypothesis=node.hypothesis,
                    depth=depth,
                    verdict="accepted",
                    reason="; ".join(reasons + [f"decomposer failed after accepted task: {exc}"]),
                    task_run_dir=task_run_dir,
                    task_baseline_primary=baseline_primary,
                    task_best_primary=best_primary,
                    error=str(exc),
                )
            return GoalNodeResult(
                name=node.name,
                hypothesis=node.hypothesis,
                depth=depth,
                verdict="rejected",
                reason="decomposer failed",
                task_run_dir=task_run_dir,
                task_baseline_primary=baseline_primary,
                task_best_primary=best_primary,
                error=str(exc),
            )

        all_children = list(node.children) + dynamic_children
        for child in all_children:
            child_results.append(self._run_node(child, depth + 1))

        accepted_children = [child for child in child_results if child.verdict == "accepted"]
        if accepted_children:
            reasons.append(f"{len(accepted_children)} child hypothesis/hypotheses accepted")

        accepted = task_accepted or bool(accepted_children)
        if accepted:
            verdict = "accepted"
            if not reasons:
                reasons.append("accepted descendant exists")
        else:
            verdict = "rejected"
            if not reasons:
                reasons.append("no accepted child hypotheses and no accepted node task")

        return GoalNodeResult(
            name=node.name,
            hypothesis=node.hypothesis,
            depth=depth,
            verdict=verdict,
            reason="; ".join(reasons),
            task_run_dir=task_run_dir,
            task_baseline_primary=baseline_primary,
            task_best_primary=best_primary,
            children=child_results,
        )

    def _report_lines(self, node: GoalNodeResult, indent: int = 0) -> list[str]:
        prefix = "  " * indent
        lines = [
            f"{prefix}- **{node.name}** — `{node.verdict}`",
            f"{prefix}  - hypothesis: {node.hypothesis}",
            f"{prefix}  - reason: {node.reason}",
        ]
        if node.task_run_dir:
            lines.append(f"{prefix}  - task_run_dir: `{node.task_run_dir}`")
        if node.task_baseline_primary is not None:
            lines.append(f"{prefix}  - task_baseline_primary: `{node.task_baseline_primary}`")
        if node.task_best_primary is not None:
            lines.append(f"{prefix}  - task_best_primary: `{node.task_best_primary}`")
        if node.error:
            lines.append(f"{prefix}  - error: `{node.error}`")
        for child in node.children:
            lines.extend(self._report_lines(child, indent + 1))
        return lines

    def run(self) -> Path:
        result = self._run_node(self.config.root, depth=0)
        summary = {
            "name": self.config.name,
            "task_root": str(self.config.task_root),
            "root": asdict(result),
        }
        (self.run_dir / "goal-tree-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
        report_lines = [
            "# auto-refine Goal Tree Report",
            "",
            f"Tree: `{self.config.name}`",
            f"Run dir: `{self.run_dir}`",
            "",
            "## Root",
            "",
            *self._report_lines(result),
            "",
        ]
        (self.run_dir / "goal-tree-report.md").write_text("\n".join(report_lines))
        return self.run_dir


def run_goal_tree(config_path: str | Path) -> Path:
    runner = GoalTreeRunner.from_config(config_path)
    return runner.run()
