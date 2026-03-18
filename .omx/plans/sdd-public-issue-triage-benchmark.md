# SDD — Public GitHub Issue Triage Benchmark

## Task shape
- artifact: `policy.json`
- dataset: `data/issues.json`
- task: `examples/github_issue_triage_public/task.json`

## Routes
Three route outputs:
- `bug`
- `enhancement`
- `manual_review`

## Dataset
Use public issue excerpts from `cli/cli` with expected routes.
Most examples map to `bug` or `enhancement`; a security/auth-sensitive issue is routed to `manual_review`.

## Evaluator metrics
- `quality_score`: routing accuracy
- `manual_review_rate`: fraction sent to manual review
- `safety_failures`: sensitive issues not sent to manual review
- `cost_usd`: small route-cost proxy

Objective:
- maximize `quality_score`
- constraints:
  - `manual_review_rate <= 0.4`
  - `cost_usd <= 0.02`
  - `safety_failures == 0`

## Candidate behavior
- baseline: weak keyword policy -> lower accuracy / safety miss
- attempt 1: better keyword policy + auth/manual review guard -> keep
- attempt 2: over-escalate to manual review -> discard on manual_review_rate/cost
- attempt 3: bug-heavy oversimplification -> discard on accuracy/safety
- attempt 4: no manual review guard -> discard on safety
