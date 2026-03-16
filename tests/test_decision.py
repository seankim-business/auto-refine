from __future__ import annotations

import unittest

from auto_refine.decision import evaluate_constraints, is_improvement
from auto_refine.models import Constraint, Objective


class DecisionTests(unittest.TestCase):
    def test_constraint_failures_detected(self) -> None:
        objective = Objective(
            primary_metric="quality_score",
            direction="maximize",
            constraints=[
                Constraint(metric="latency_ms", op="<=", value=2000),
                Constraint(metric="safety_failures", op="==", value=0),
            ],
        )
        failures = evaluate_constraints(
            {"quality_score": 0.8, "latency_ms": 2500, "safety_failures": 1},
            objective,
        )
        self.assertEqual(len(failures), 2)

    def test_improvement_maximize(self) -> None:
        objective = Objective(primary_metric="quality_score", direction="maximize")
        self.assertTrue(
            is_improvement(
                {"quality_score": 0.9},
                {"quality_score": 0.8},
                objective,
            )
        )
        self.assertFalse(
            is_improvement(
                {"quality_score": 0.8},
                {"quality_score": 0.8},
                objective,
            )
        )

    def test_improvement_minimize(self) -> None:
        objective = Objective(primary_metric="latency_ms", direction="minimize")
        self.assertTrue(
            is_improvement(
                {"latency_ms": 1000},
                {"latency_ms": 1200},
                objective,
            )
        )
        self.assertFalse(
            is_improvement(
                {"latency_ms": 1300},
                {"latency_ms": 1200},
                objective,
            )
        )


if __name__ == "__main__":
    unittest.main()
