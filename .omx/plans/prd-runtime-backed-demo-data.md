# PRD — Runtime-backed Demo Data

Date: 2026-03-16
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
The current demo page is more honest than before, but its data is still hand-authored. That weakens credibility because the demo is not visibly generated from actual `auto-refine` run outputs.

## Goal
Make the demo page consume data generated from real `summary.json` run artifacts rather than manually maintained result objects.

## Acceptance Criteria
1. Add a code path that builds `docs/demo-data.json` from actual run summaries.
2. Keep narrative metadata separate from runtime metrics/artifacts.
3. Add a CLI command or script for rebuilding the demo data.
4. Add at least one test for the demo-data builder.
5. Regenerate the live demo from actual run outputs for prompt, routing, and self-refine marketing tasks.
