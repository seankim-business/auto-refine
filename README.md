# auto-refine

**Benchmark-driven autonomous optimization for bounded systems.**

`auto-refine` takes a small, explicit search space:
- a bounded mutable artifact
- a trusted evaluator
- a primary metric
- hard constraints
- a rollback path

Then it runs the loop:

1. establish baseline
2. propose bounded mutation
3. evaluate candidate
4. keep or discard
5. restore incumbent if discarded
6. write ledger + report

This repo is the non-ML extraction of the `autoresearch` pattern into a reusable core.

## What it proves

The same loop can optimize different artifact types without changing the engine:

- **prompt artifact** → `examples/prompt_eval_toy/`
- **workflow policy artifact** → `examples/routing_policy_toy/`
- **public GitHub issue triage benchmark** → `examples/github_issue_triage_public/`
- **repo-owned marketing artifact** → `self_tasks/marketing_copy/`
- **hierarchical goal / hypothesis tree** → `goal_trees/marketing_strategy/`

These examples are:
- deterministic
- local-only at runtime
- constraint-aware
- rollback-safe

The new issue-triage example is benchmark-backed by public issue excerpts from `cli/cli`, stored locally with source URLs for reproducibility.

## Live demo

- GitHub Pages demo: `https://seankim-business.github.io/auto-refine/`

The demo now shows, explicitly:
- what artifact is being optimized
- the before/after artifact that wins
- sample case-level behavior changes
- which candidates get discarded and why
- recursive goal trees with accepted / rejected hypotheses

Current live examples are deterministic proof demos, labeled honestly as such. The published page data is generated from actual `summary.json` and `goal-tree-summary.json` run outputs plus a thin narrative metadata layer.

## Quick start

```bash
python3 -m auto_refine run examples/prompt_eval_toy/task.json --iterations 4
python3 -m auto_refine run examples/routing_policy_toy/task.json --iterations 4
python3 -m auto_refine run examples/github_issue_triage_public/task.json --iterations 4
python3 -m auto_refine run self_tasks/marketing_copy/task.json --iterations 4
python3 -m auto_refine run-goal-tree goal_trees/marketing_strategy/tree.json
python3 -m auto_refine resume --task self_tasks/marketing_copy/task.json --budget 8
```

## Self-refine this repo

The repo now includes a bounded self-hosting task:

- mutable artifact: `marketing/hero.md`
- evaluator: `self_tasks/marketing_copy/scripts/evaluate.py`
- proposer: `self_tasks/marketing_copy/scripts/proposer.py`

This is intentionally narrow: it lets `auto-refine` improve a repo-owned marketing artifact without turning into an unrestricted self-editing system.

When you run it, the winning incumbent is written back to `marketing/hero.md`, and the baseline/trial artifact texts are preserved in `summary.json` for inspection.

## Persistent / budgeted refinement

`auto-refine` can now resume the latest run for a task up to a total trial budget.

```bash
python3 -m auto_refine resume --task self_tasks/marketing_copy/task.json --budget 8
```

This makes long-running self-hosted refinement a first-class capability:
- latest run is resumed instead of starting from scratch
- `state.json` tracks attempts completed and incumbent metrics
- `incumbent/` stores the current accepted artifact snapshot
- one-shot task runs are resume-compatible

## Hierarchical goal trees

`auto-refine` can also model a larger goal as a recursive tree of hypotheses:

- root goal
- sub-goals (also hypotheses)
- sub-sub-goals
- automatic acceptance / rejection at each node

Use:

```bash
python3 -m auto_refine run-goal-tree goal_trees/marketing_strategy/tree.json
```

The included `goal_trees/marketing_strategy/` example demonstrates:
- recursive decomposition via decomposer commands
- arbitrary depth through nested child nodes
- automatic rejection when a node task produces no kept candidate
- accepted parent nodes when an accepted descendant hypothesis exists

## Core ideas

`auto-refine` is deliberately narrow.
It is **not** a free-form self-editing agent.
It is a **bounded optimizer** for systems where you can define:

- **mutable_paths** — what can change
- **baseline_command** — how to score the current incumbent
- **proposer_command** — how to generate the next candidate
- **trial_command** — how to score the candidate
- **objective** — primary metric + constraints

## Task contract

A task is defined in JSON:

```json
{
  "name": "prompt-eval-toy",
  "task_root": ".",
  "mutable_paths": ["prompts/system.md"],
  "baseline_command": ["python3", "scripts/evaluate.py"],
  "proposer_command": ["python3", "scripts/proposer.py"],
  "trial_command": ["python3", "scripts/evaluate.py"],
  "objective": {
    "primary_metric": "quality_score",
    "direction": "maximize",
    "constraints": [
      {"metric": "latency_ms", "op": "<=", "value": 2000},
      {"metric": "cost_usd", "op": "<=", "value": 0.02},
      {"metric": "safety_failures", "op": "==", "value": 0}
    ]
  },
  "iterations": 4,
  "output_dir": "runs/auto-refine"
}
```

## Current scope

Included in this repo:
- generic loop engine
- constrained keep/discard decision policy
- file snapshot rollback
- artifact text snapshots in `summary.json`
- persistent `resume --task ... --budget ...` refinement mode
- recursive goal / hypothesis tree runtime
- ledger + Markdown report generation
- deterministic proof examples
- unit + integration tests

Not included yet:
- unrestricted repo-wide mutation
- browser automation adapters
- stochastic LLM judges
- distributed workers
- Git-native branching/worktree rollback

## Why this exists

The useful part of `autoresearch` is not “ML training” specifically.
The useful part is the **closed-loop improvement pattern**.

`auto-refine` makes that pattern reusable.

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Rebuild demo data from actual run summaries:

```bash
python3 -m auto_refine build-demo-data docs/demo-config.json --output docs/demo-data.json
```

## License

MIT
