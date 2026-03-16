# Issue Breakdown — Hierarchical Goal / Hypothesis Tree

## WS1 — Schema / models
- [ ] add goal-tree config loader
- [ ] add recursive GoalNode / GoalResult models
- [ ] support inline children and decomposer-generated children

## WS2 — Runtime
- [ ] add recursive traversal engine
- [ ] connect node task execution to existing flat `run_from_config`
- [ ] derive accepted/rejected verdict automatically
- [ ] capture failure reasons and linked run dirs

## WS3 — CLI / reports
- [ ] add `run-goal-tree` CLI command
- [ ] write `goal-tree-summary.json`
- [ ] write simple Markdown tree report

## WS4 — Example
- [ ] add deterministic recursive example with 3 levels
- [ ] include both accepted and rejected hypotheses

## WS5 — Verification
- [ ] add recursive integration test
- [ ] run end-to-end example
