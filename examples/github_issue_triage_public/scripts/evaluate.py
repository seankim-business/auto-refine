#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("AUTORESEARCH_TASK_ROOT", Path(__file__).resolve().parent.parent))
POLICY_PATH = TASK_ROOT / "policy.json"
ISSUES_PATH = TASK_ROOT / "data" / "issues.json"

policy = json.loads(POLICY_PATH.read_text())
issues = json.loads(ISSUES_PATH.read_text())

COST = {
    "bug": 0.003,
    "enhancement": 0.002,
    "manual_review": 0.012,
}


def score_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


def predict(issue: dict) -> str:
    text = f"{issue['title']}\n{issue['body']}".lower()
    if score_hits(text, policy["manual_review_keywords"]) > 0:
        return "manual_review"
    bug_score = score_hits(text, policy["bug_keywords"])
    enhancement_score = score_hits(text, policy["enhancement_keywords"])
    if bug_score > enhancement_score:
        return "bug"
    if enhancement_score > bug_score:
        return "enhancement"
    return policy["default_route"]


correct = 0
manual_reviews = 0
safety_failures = 0
cost_total = 0.0

for issue in issues:
    route = predict(issue)
    if route == issue["expected_route"]:
        correct += 1
    if route == "manual_review":
        manual_reviews += 1
    if issue["sensitive"] and route != "manual_review":
        safety_failures += 1
    cost_total += COST[route]

result = {
    "quality_score": round(correct / len(issues), 4),
    "manual_review_rate": round(manual_reviews / len(issues), 4),
    "cost_usd": round(cost_total / len(issues), 4),
    "safety_failures": safety_failures,
    "num_issues": len(issues),
}

print(json.dumps(result))
