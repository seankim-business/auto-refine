# PRD — Goal Tree Visualization

Date: 2026-03-19
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
The repo now has a recursive goal / hypothesis tree runtime, but the live demo page does not visualize it. That means one of the most differentiating features of auto-refine is invisible to visitors.

## Goal
Add runtime-backed goal-tree visualization to the GitHub Pages demo so visitors can see:
- recursive decomposition
- accepted vs rejected hypotheses
- node reasons
- task-linked evidence

## Acceptance Criteria
1. Extend demo-data generation to include goal-tree runtime summaries.
2. Add a goal-tree section to the live demo page.
3. Visualization shows nested structure, verdict, reason, and any task metrics/run paths available.
4. Add a test covering demo-data builder support for goal trees.
5. Rebuild demo-data and verify the live page renders the section.
