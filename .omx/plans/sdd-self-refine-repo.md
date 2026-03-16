# SDD — auto-refine Self-Refine Repo Evolution

## 1. Artifact snapshot capture

### Design
- Extend `TrialRecord` with `artifacts: dict[str, str]`
- Capture text snapshots for mutable paths at baseline and after proposer mutations
- Use repo-relative paths where possible
- Skip binary/decode failures rather than crashing

### Reason
This makes the engine outputs more legible and supports demo/report tooling without re-reading files from the task workspace later.

## 2. Self-hosting task

### Artifact
- `marketing/hero.md`

### Task config
- `self_tasks/marketing_copy/task.json`
- `task_root` points to repo root
- `mutable_paths` includes only `marketing/hero.md`

### Proposer
Candidate variants by attempt number:
1. concise, strong, concrete marketing copy -> should keep
2. overhyped AGI-style copy -> should discard on hype constraint
3. vague generic copy -> should discard on lower quality
4. verbose overlong copy -> should discard on latency/cost/length proxy

### Evaluator
Compute deterministic metrics from hero copy text:
- `quality_score` based on presence of key ideas: bounded artifact, evaluator, constraints, rollback, examples
- `latency_ms` as a text-length proxy
- `cost_usd` as a text-length proxy
- `safety_failures` / `hype_flags` based on banned hype patterns

Objective:
- maximize `quality_score`
- constraints:
  - `latency_ms <= 2200`
  - `cost_usd <= 0.02`
  - `hype_flags == 0`

## 3. Testing
- integration test copies repo task assets to temp dir
- run 4 iterations
- assert at least one keep and one discard
- assert final artifact equals kept incumbent
- assert summary contains artifact snapshots
