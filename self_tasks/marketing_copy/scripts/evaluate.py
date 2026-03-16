#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("AUTORESEARCH_TASK_ROOT", Path(__file__).resolve().parents[2]))
ARTIFACT = TASK_ROOT / "marketing" / "hero.md"
text = ARTIFACT.read_text().strip()
lower = text.lower()

quality = 0.05
checks = [
    "bounded artifact" in lower or "bounded artifacts" in lower or "bounded systems" in lower,
    "trusted evaluator" in lower,
    "constraint" in lower or "constraints" in lower,
    "rollback" in lower or "rolls back" in lower,
    "prompt" in lower or "prompts" in lower,
    "policy" in lower or "policies" in lower,
    "latency" in lower,
    "cost" in lower,
    "safety" in lower,
]
quality += sum(0.1 for ok in checks if ok)
if "anything and everything" in lower or "universal" in lower:
    quality += 0.03
if len(text) < 90:
    quality -= 0.08
if len(text) > 320:
    quality -= 0.04

hype_patterns = [
    "agi",
    "magical",
    "unstoppable",
    "anything and everything",
    "universal",
]
hype_flags = sum(1 for token in hype_patterns if token in lower)
latency_ms = 700 + len(text) * 4
cost_usd = round(len(text) / 14000, 4)

result = {
    "quality_score": round(max(0.0, min(1.0, quality)), 4),
    "latency_ms": latency_ms,
    "cost_usd": cost_usd,
    "hype_flags": hype_flags,
    "artifact_chars": len(text),
}

print(json.dumps(result))
