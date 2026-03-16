# SDD — Hierarchical Goal / Hypothesis Tree

## Core idea
A goal-tree node is a falsifiable hypothesis with optional:
- bounded task config
- decomposer command
- inline children

Each node can:
1. run its own bounded task
2. produce a verdict (`accepted` / `rejected`)
3. expand into child hypotheses
4. recurse into children if allowed

## Node schema
Suggested fields:
- `name`
- `hypothesis`
- `taskConfig` (optional; path to flat task config)
- `decomposerCommand` (optional; outputs child nodes JSON)
- `children` (optional; inline child nodes)
- `maxDepth` (optional)

## Verdict rules
- `accepted` if node task produces at least one kept candidate
- `rejected` if node task produces no kept candidate
- `rejected` if task or decomposer fails
- `rejected` if child generation returns nothing and node has no accepted task result

## Recursion
Traversal is depth-first in MVP.
Each child node is the same schema, so depth is arbitrary.

## Outputs
Per goal-tree run:
- `goal-tree-summary.json`
- `goal-tree-report.md`

Each node result should include:
- name
- hypothesis
- depth
- verdict
- reason
- taskRunDir (if task executed)
- childCount
- children[]

## Example design
Create deterministic example under `goal_trees/marketing_strategy/`:
- root goal: make product positioning stronger
- child A: improve specificity
- grandchild A1: name bounded artifacts explicitly -> accepted
- grandchild A2: vague wording -> rejected
- child B: improve excitement via hype -> rejected

This gives both recursion and automatic hypothesis rejection.
