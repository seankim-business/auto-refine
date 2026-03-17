# PRD — Persistent / Budgeted Refinement

Date: 2026-03-17
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
`auto-refine` currently runs isolated one-shot optimization batches. A user can run a task for N iterations, but the system does not natively resume from previous task state or continue until a total refinement budget is exhausted.

That makes long-running self-hosted refinement feel externally orchestrated rather than first-class inside the product.

## Goal
Add a native persistent refinement mode that can resume the latest task run and continue optimizing until a total trial budget is reached.

## Outcome
A user can run:

```bash
python3 -m auto_refine resume --task self_tasks/marketing_copy/task.json --budget 100
```

and `auto-refine` will:
- find the latest run for the task (or start a new one)
- restore the last incumbent snapshot
- continue from the next attempt number
- write updated ledger/report/state files
- stop when the total trial budget is reached

## Acceptance Criteria
1. Add native `resume` CLI command.
2. Persist run state in `state.json`.
3. Persist incumbent snapshot under the run directory.
4. One-shot runs are also resume-compatible.
5. Add tests covering fresh resume start + continued resume.
6. Apply the feature to a repo-owned self-task and verify green tests.

## Non-Goals
- cross-task orchestration
- parallel scheduling
- time-based cancellation
- automatic commits/pushes from the engine itself
