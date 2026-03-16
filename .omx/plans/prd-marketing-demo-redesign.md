# PRD — auto-refine Marketing Demo Redesign

Date: 2026-03-16
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
Current GitHub Pages demo proves that the optimization loop works, but it does not sell the product.
The main issues:
- what is being optimized is not obvious enough
- the page leads with mechanism, not user value
- synthetic examples are not clearly framed as proof demos
- users do not see before/after artifact changes or concrete outcomes quickly

## Goal
Redesign the landing/demo page so that it functions as product marketing, not just engineering documentation.

## Target Outcome
A first-time visitor should understand within 10 seconds:
1. what auto-refine optimizes
2. why bounded optimization matters
3. what gets kept vs discarded
4. what changed in a concrete before/after example
5. that the current live examples are deterministic proofs, not fake benchmark claims

## Acceptance Criteria
- Hero copy clearly states the product value proposition.
- Page explicitly answers: "what exactly gets optimized?"
- Each example shows artifact before/after and sample evaluation outcomes.
- Keep/discard reasoning is visually obvious.
- Synthetic proof examples are labeled honestly.
- README links still point to the live demo and remain accurate.

## Non-Goals
- adding real external benchmark integration in this iteration
- backend changes
- collecting live telemetry

## Success Metric
The landing page reads like a product page with evidence, not like an internal dashboard.
