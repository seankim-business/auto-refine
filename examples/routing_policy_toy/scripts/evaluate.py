#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("AUTORESEARCH_TASK_ROOT", Path(__file__).resolve().parent.parent))
POLICY_PATH = TASK_ROOT / "policy.json"
TICKETS_PATH = TASK_ROOT / "data" / "tickets.json"

policy = json.loads(POLICY_PATH.read_text())
tickets = json.loads(TICKETS_PATH.read_text())

LATENCY = {
    "auto_answer": 350,
    "specialist": 1200,
    "manual_review": 2800,
}
COST = {
    "auto_answer": 0.002,
    "specialist": 0.008,
    "manual_review": 0.04,
}


def route(ticket: dict) -> str:
    category = ticket["category"]
    if category in policy["manual_review_categories"]:
        return "manual_review"
    if ticket["sensitive"] and policy["sensitive_manual"]:
        return "manual_review"
    if ticket["urgent"] and category == "payment" and policy["urgent_payment_manual"]:
        return "manual_review"
    if ticket["urgent"] and category in policy["urgent_specialist_categories"]:
        return "specialist"
    if category in policy["specialist_categories"]:
        return "specialist"
    return policy["default_route"]


correct = 0
safety_failures = 0
latency_total = 0
cost_total = 0.0

for ticket in tickets:
    chosen = route(ticket)
    if chosen == ticket["expected_route"]:
        correct += 1
    if ticket["sensitive"] and chosen != "manual_review":
        safety_failures += 1
    latency_total += LATENCY[chosen]
    cost_total += COST[chosen]

result = {
    "quality_score": round(correct / len(tickets), 4),
    "latency_ms": round(latency_total / len(tickets), 2),
    "cost_usd": round(cost_total / len(tickets), 4),
    "safety_failures": safety_failures,
    "num_tickets": len(tickets),
}

print(json.dumps(result))
