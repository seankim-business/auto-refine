from __future__ import annotations

from .models import Objective


OPS = {
    "<": lambda left, right: left < right,
    "<=": lambda left, right: left <= right,
    ">": lambda left, right: left > right,
    ">=": lambda left, right: left >= right,
    "==": lambda left, right: left == right,
}


class DecisionError(ValueError):
    pass


def evaluate_constraints(metrics: dict, objective: Objective) -> list[str]:
    failures: list[str] = []
    for constraint in objective.constraints:
        if constraint.metric not in metrics:
            failures.append(f"missing metric: {constraint.metric}")
            continue
        if constraint.op not in OPS:
            failures.append(f"unsupported operator: {constraint.op}")
            continue
        value = float(metrics[constraint.metric])
        if not OPS[constraint.op](value, float(constraint.value)):
            failures.append(
                f"{constraint.metric} {constraint.op} {constraint.value} failed (got {value})"
            )
    return failures


def primary_value(metrics: dict, objective: Objective) -> float:
    if objective.primary_metric not in metrics:
        raise DecisionError(f"missing primary metric: {objective.primary_metric}")
    return float(metrics[objective.primary_metric])


def is_improvement(candidate_metrics: dict, incumbent_metrics: dict, objective: Objective) -> bool:
    candidate = primary_value(candidate_metrics, objective)
    incumbent = primary_value(incumbent_metrics, objective)
    if objective.direction == "maximize":
        return candidate > incumbent
    if objective.direction == "minimize":
        return candidate < incumbent
    raise DecisionError(f"unsupported direction: {objective.direction}")
