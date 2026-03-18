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
        "description": "expand bug/enhancement keywords and add auth-sensitive manual review guard",
        "policy": {
            "bug_keywords": ["bug", "fails", "error", "corrupt", "failure", "duplicate", "rate limit", "returns"],
            "enhancement_keywords": ["should", "support", "add", "json", "auto-select", "emoji", "prompting"],
            "manual_review_keywords": ["auth", "authentication", "token", "trusted host", "enterprise"],
            "default_route": "enhancement"
        }
    },
    2: {
        "description": "over-escalate many issues to manual review",
        "policy": {
            "bug_keywords": ["bug", "fails", "error", "corrupt", "failure", "duplicate", "rate limit", "returns"],
            "enhancement_keywords": ["should", "support", "add", "json", "auto-select", "emoji", "prompting"],
            "manual_review_keywords": ["gh", "repo", "pr", "issue", "auth", "token", "host"],
            "default_route": "manual_review"
        }
    },
    3: {
        "description": "bug-heavy simplification",
        "policy": {
            "bug_keywords": ["gh", "repo", "issue", "fails", "returns", "status"],
            "enhancement_keywords": [],
            "manual_review_keywords": [],
            "default_route": "bug"
        }
    },
    4: {
        "description": "strong classification but no manual review guard",
        "policy": {
            "bug_keywords": ["bug", "fails", "error", "corrupt", "failure", "duplicate", "rate limit", "returns"],
            "enhancement_keywords": ["should", "support", "add", "json", "auto-select", "emoji", "prompting", "authentication", "token"],
            "manual_review_keywords": [],
            "default_route": "enhancement"
        }
    }
}

variant = VARIANTS.get(ATTEMPT)
if variant is None:
    print(json.dumps({"description": f"no-op variant for attempt {ATTEMPT}"}))
    raise SystemExit(0)

POLICY_PATH.write_text(json.dumps(variant["policy"], ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"description": variant["description"]}))
