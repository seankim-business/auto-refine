#!/usr/bin/env python3
from __future__ import annotations

import json

payload = {
    "children": [
        {
            "name": "improve-specificity",
            "hypothesis": "Naming exactly what gets optimized will improve positioning clarity.",
            "decomposerCommand": [
                "python3",
                "goal_trees/marketing_strategy/scripts/specificity_decompose.py"
            ]
        },
        {
            "name": "increase-excitement-with-hype",
            "hypothesis": "More hype will make the product feel more compelling.",
            "taskConfig": "goal_trees/marketing_strategy/tasks/hype_branch/task.json"
        }
    ]
}

print(json.dumps(payload))
