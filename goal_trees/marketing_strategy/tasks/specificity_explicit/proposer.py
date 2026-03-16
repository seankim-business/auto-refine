#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

Path("hero.md").write_text(
    "auto-refine optimizes bounded artifacts like prompts, policies, and configs against a trusted evaluator, with constraints and rollback.\n"
)
print(json.dumps({"description": "explicitly name bounded artifacts"}))
