#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ["AUTORESEARCH_TASK_ROOT"])
ATTEMPT = int(os.environ.get("AUTORESEARCH_ATTEMPT", "0"))
ARTIFACT = TASK_ROOT / "marketing" / "hero.md"

VARIANTS = {
    1: {
        "description": "concrete bounded-optimization positioning",
        "content": (
            "auto-refine optimizes bounded artifacts like prompts, policies, and configs against a trusted evaluator. "
            "It keeps candidates that improve the target metric without breaking latency, cost, or safety constraints, "
            "and rolls back bad candidates automatically.\n"
        ),
    },
    2: {
        "description": "overhyped AGI-style positioning",
        "content": (
            "auto-refine is an AGI optimization engine that can automatically improve anything and everything in your stack. "
            "It is universal, magical, and unstoppable.\n"
        ),
    },
    3: {
        "description": "too vague to sell the product",
        "content": (
            "auto-refine runs experiments on files and tries to make them better over time.\n"
        ),
    },
    4: {
        "description": "too verbose even though conceptually strong",
        "content": (
            "auto-refine optimizes bounded artifacts like prompts, policies, configs, and workflow rules against a trusted evaluator, "
            "and it keeps only the candidates that improve the chosen metric without breaking latency, cost, or safety constraints. "
            "It also records the ledger, explains keep and discard decisions, preserves rollback safety, and helps teams understand exactly what changed and why. "
            "This makes it useful for benchmark-driven iteration across multiple artifact classes while still keeping the search space explicit and governed by constraints.\n"
        ),
    },
}

variant = VARIANTS.get(ATTEMPT)
if variant is None:
    print(json.dumps({"description": f"no-op variant for attempt {ATTEMPT}"}))
    raise SystemExit(0)

ARTIFACT.write_text(variant["content"])
print(json.dumps({"description": variant["description"]}))
