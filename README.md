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

Both examples are:
- deterministic
- local-only
- constraint-aware
- rollback-safe

## Quick start

```bash
python3 -m auto_refine run examples/prompt_eval_toy/task.json --iterations 4
python3 -m auto_refine run examples/routing_policy_toy/task.json --iterations 4
```

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

## License

MIT
