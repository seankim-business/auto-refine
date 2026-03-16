#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("AUTORESEARCH_TASK_ROOT", Path(__file__).resolve().parent.parent))
PROMPT_PATH = TASK_ROOT / "prompts" / "system.md"
text = PROMPT_PATH.read_text().strip()
lower = text.lower()

quality = 0.10
if "clarifying question" in lower or "clarify" in lower:
    quality += 0.25
if "clear steps" in lower or "give clear steps" in lower:
    quality += 0.25
if "concise" in lower:
    quality += 0.20
if "safety" in lower or "safe" in lower:
    quality += 0.20
if "constraints" in lower:
    quality += 0.10
if len(text) > 220:
    quality -= 0.05

latency_ms = 700 + len(text) * 6
cost_usd = round(len(text) / 10000, 4)
safety_failures = 1 if "ignore safety" in lower else 0

result = {
    "quality_score": round(max(0.0, min(1.0, quality)), 4),
    "latency_ms": latency_ms,
    "cost_usd": cost_usd,
    "safety_failures": safety_failures,
    "prompt_chars": len(text),
}

print(json.dumps(result))
