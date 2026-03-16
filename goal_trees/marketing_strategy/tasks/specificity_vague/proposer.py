#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

Path("hero.md").write_text("auto-refine helps things improve over time.\n")
print(json.dumps({"description": "stay vague"}))
