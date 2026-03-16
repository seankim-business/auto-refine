#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ["AUTORESEARCH_TASK_ROOT"])
ATTEMPT = int(os.environ.get("AUTORESEARCH_ATTEMPT", "0"))
POLICY_PATH = TASK_ROOT / "policy.json"

VARIANTS = {
    1: {
        "description": "tighten routing for refund/security/payment while preserving cost bounds",
        "policy": {
            "manual_review_categories": ["fraud", "security"],
            "specialist_categories": ["technical"],
            "urgent_specialist_categories": ["refund"],
            "sensitive_manual": False,
            "urgent_payment_manual": True,
            "default_route": "auto_answer"
        }
    },
    2: {
        "description": "over-escalate many categories to manual review",
        "policy": {
            "manual_review_categories": ["fraud", "security", "payment", "refund", "technical"],
            "specialist_categories": [],
            "urgent_specialist_categories": [],
            "sensitive_manual": True,
            "urgent_payment_manual": True,
            "default_route": "auto_answer"
        }
    },
    3: {
        "description": "oversimplify to mostly auto routing",
        "policy": {
            "manual_review_categories": ["fraud"],
            "specialist_categories": [],
            "urgent_specialist_categories": [],
            "sensitive_manual": False,
            "urgent_payment_manual": False,
            "default_route": "auto_answer"
        }
    },
    4: {
        "description": "unsafe routing that skips secure review",
        "policy": {
            "manual_review_categories": [],
            "specialist_categories": ["technical", "refund"],
            "urgent_specialist_categories": ["payment"],
            "sensitive_manual": False,
            "urgent_payment_manual": False,
            "default_route": "auto_answer"
        }
    }
}

variant = VARIANTS.get(ATTEMPT)
if variant is None:
    print(json.dumps({"description": f"no-op variant for attempt {ATTEMPT}"}))
    raise SystemExit(0)

POLICY_PATH.write_text(json.dumps(variant["policy"], ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"description": variant["description"]}))
