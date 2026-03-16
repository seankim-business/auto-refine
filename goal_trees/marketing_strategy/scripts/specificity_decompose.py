#!/usr/bin/env python3
from __future__ import annotations

import json

payload = {
    "children": [
        {
            "name": "name-bounded-artifacts-explicitly",
            "hypothesis": "Explicitly naming prompts, policies, and configs will improve clarity.",
            "taskConfig": "goal_trees/marketing_strategy/tasks/specificity_explicit/task.json"
        },
        {
            "name": "keep-it-vague",
            "hypothesis": "Vague wording can still be good enough.",
            "taskConfig": "goal_trees/marketing_strategy/tasks/specificity_vague/task.json"
        }
    ]
}

print(json.dumps(payload))
