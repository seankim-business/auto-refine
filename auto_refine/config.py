from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Constraint, Objective, TaskConfig


class ConfigError(ValueError):
    pass


REQUIRED_FIELDS = {
    "name",
    "mutable_paths",
    "baseline_command",
    "proposer_command",
    "trial_command",
    "objective",
}


def _ensure_safe_relative_path(task_root: Path, rel_path: str) -> Path:
    path = Path(rel_path)
    if path.is_absolute():
        raise ConfigError(f"mutable path must be relative: {rel_path}")
    resolved = (task_root / path).resolve()
    root_resolved = task_root.resolve()
    if os.path.commonpath([str(root_resolved), str(resolved)]) != str(root_resolved):
        raise ConfigError(f"mutable path escapes task root: {rel_path}")
    if not resolved.exists():
        raise ConfigError(f"mutable path does not exist: {rel_path}")
    return resolved


def load_task_config(config_path: str | Path) -> TaskConfig:
    path = Path(config_path).resolve()
    raw = json.loads(path.read_text())
    missing = REQUIRED_FIELDS - set(raw)
    if missing:
        raise ConfigError(f"missing required fields: {sorted(missing)}")

    task_root_value = raw.get("task_root", ".")
    task_root = (path.parent / task_root_value).resolve()
    if not task_root.exists():
        raise ConfigError(f"task_root does not exist: {task_root}")

    mutable_paths = [_ensure_safe_relative_path(task_root, p) for p in raw["mutable_paths"]]

    objective_raw = raw["objective"]
    constraints = [Constraint(**item) for item in objective_raw.get("constraints", [])]
    objective = Objective(
        primary_metric=objective_raw["primary_metric"],
        direction=objective_raw["direction"],
        constraints=constraints,
    )
    if objective.direction not in {"maximize", "minimize"}:
        raise ConfigError("objective.direction must be 'maximize' or 'minimize'")

    iterations = int(raw.get("iterations", 1))
    if iterations < 1:
        raise ConfigError("iterations must be >= 1")

    output_dir = (task_root / raw.get("output_dir", "runs/auto-refine")).resolve()
    root_resolved = task_root.resolve()
    if os.path.commonpath([str(root_resolved), str(output_dir)]) != str(root_resolved):
        raise ConfigError("output_dir must stay inside task_root")

    return TaskConfig(
        name=raw["name"],
        task_root=task_root,
        mutable_paths=mutable_paths,
        baseline_command=list(raw["baseline_command"]),
        proposer_command=list(raw["proposer_command"]),
        trial_command=list(raw["trial_command"]),
        objective=objective,
        iterations=iterations,
        output_dir=output_dir,
    )
