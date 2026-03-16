#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

text = Path("hero.md").read_text().strip()
lower = text.lower()

quality = 0.05
if "prompt" in lower or "prompts" in lower:
    quality += 0.15
if "policy" in lower or "policies" in lower:
    quality += 0.15
if "config" in lower or "configs" in lower:
    quality += 0.1
if "trusted evaluator" in lower:
    quality += 0.2
if "constraint" in lower or "constraints" in lower:
    quality += 0.15
if "rollback" in lower or "rolls back" in lower:
    quality += 0.15
if "bounded" in lower:
    quality += 0.1
if len(text) < 80:
    quality -= 0.08
if len(text) > 320:
    quality -= 0.04

hype_patterns = ["agi", "magical", "unstoppable", "anything and everything", "universal"]
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
