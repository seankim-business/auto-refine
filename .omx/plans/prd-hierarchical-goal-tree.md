# PRD — Hierarchical Goal / Hypothesis Tree

Date: 2026-03-16
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
`auto-refine` currently optimizes one bounded task at a time. That is useful, but it does not yet model a larger goal as a hierarchy of hypotheses:
- root goal
- sub-goals (also hypotheses)
- sub-sub-goals
- recursive rejection/acceptance

Without this, the system cannot express a structured search program where each node in the tree is a falsifiable improvement hypothesis.

## Goal
Add a recursive goal-tree layer to `auto-refine` where:
1. a goal can be decomposed into child hypotheses
2. each child hypothesis can itself be optimized or decomposed further
3. hypotheses are automatically accepted/rejected
4. the structure can recurse arbitrarily deep

## MVP Outcome
A user can run a goal-tree config that:
- evaluates a root node
- expands children from a decomposer command or inline config
- recursively visits child nodes
- automatically marks nodes as `accepted` or `rejected`
- records a tree summary with reasons and supporting task/run outputs

## Acceptance Criteria
1. Add recursive goal-tree schema and runtime.
2. Support arbitrary depth via nested nodes or decomposer-generated nodes.
3. Automatic rejection happens when:
   - no kept improvement exists for the node task, or
   - node constraints fail, or
   - decomposer/task execution fails.
4. Tree summary captures node name, hypothesis, depth, verdict, children, and linked task run summary.
5. Add a deterministic example with at least 3 levels: root -> child -> grandchild.
6. Add tests for recursive traversal and auto-rejection.

## Non-Goals
- LLM-based decomposition in this iteration
- multi-parent DAG optimization
- merging child artifacts back into parent artifact automatically
- autonomous git commit/push loops

## Product Framing
This turns auto-refine from a flat bounded optimizer into a **hierarchical hypothesis optimizer**.
Each sub-goal is itself a hypothesis that can be improved, falsified, or decomposed.
