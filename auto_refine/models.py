from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Constraint:
    metric: str
    op: str
    value: float


@dataclass(frozen=True)
class Objective:
    primary_metric: str
    direction: str
    constraints: list[Constraint] = field(default_factory=list)


@dataclass(frozen=True)
class TaskConfig:
    name: str
    task_root: Path
    mutable_paths: list[Path]
    baseline_command: list[str]
    proposer_command: list[str]
    trial_command: list[str]
    objective: Objective
    iterations: int
    output_dir: Path


@dataclass
class TrialRecord:
    attempt: int
    phase: str
    name: str
    mutation: str
    metrics: dict[str, Any]
    decision: str
    improved: bool
    constraint_failures: list[str]
    proposer_exit_code: int | None = None
    evaluator_exit_code: int | None = None
    proposer_log: str | None = None
    evaluator_log: str | None = None
    incumbent_primary: float | None = None
    candidate_primary: float | None = None
    error: str | None = None
