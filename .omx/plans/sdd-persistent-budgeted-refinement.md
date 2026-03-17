# SDD — Persistent / Budgeted Refinement

## Core design
Add persistence directly to the flat task engine.

### Run directory additions
- `ledger.jsonl` — existing per-record append log
- `summary.json` — existing report summary
- `report.md` — existing Markdown report
- `state.json` — persisted task state
- `incumbent/` — persisted file snapshot of current incumbent artifact(s)

## Resume semantics
Command:

```bash
python3 -m auto_refine resume --task <task.json> --budget <N>
```

Semantics:
- Find latest run directory for that task under task output dir.
- If none exists, create a new run.
- If run exists, load `state.json`, `ledger.jsonl`, and `incumbent/`.
- Continue attempts from `attempts_completed + 1` until total attempts == `budget`.
- Do not rerun baseline when resuming an initialized run.

## State fields
Suggested minimal fields:
- `task`
- `attempts_completed`
- `kept_trials`
- `incumbent_metrics`
- `baseline_metrics`

## Test plan
- first `resume --budget 2` creates a new run and executes two attempts
- second `resume --budget 4` reuses same run and extends to four attempts total
- final artifact should reflect the kept incumbent
- `state.json` should show `attempts_completed == 4`
