# PRD — auto-refine Self-Refine Repo Evolution

Date: 2026-03-16
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
The repo proves bounded optimization on toy examples, but it does not yet demonstrate that `auto-refine` can be used on artifacts that belong to the repo itself.

## Goal
Add a self-hosting path where `auto-refine` optimizes a repo-owned marketing artifact, and improve the engine so run summaries include the mutable artifact snapshot for baseline and trial candidates.

## Target Outcome
1. The engine records artifact snapshots in run summaries.
2. The repo contains a self-hosting task config that targets a repo-owned artifact.
3. Running the task once updates the repo-owned artifact to the kept incumbent.
4. Tests cover the self-hosting task.

## Scope
- add artifact snapshot capture to the engine
- add repo-owned artifact `marketing/hero.md`
- add self-hosting task under `self_tasks/marketing_copy/`
- add deterministic proposer/evaluator for the marketing artifact
- run the task once and keep the winning incumbent
- document the self-hosting path in README

## Non-Goals
- live LLM evaluator
- self-refining arbitrary repo files
- automatic commit loop
- GitHub Actions orchestration

## Acceptance Criteria
- `summary.json` includes mutable artifact text snapshots for baseline/trials.
- A new self-hosting task runs via `python3 -m auto_refine run self_tasks/marketing_copy/task.json`.
- The task yields at least one keep and one discard outcome.
- Integration test passes for the self-hosting task.
- README documents the self-refine task.
