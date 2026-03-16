# SDD — auto-refine Marketing Demo Redesign

## Design Principles
1. Lead with outcome, not mechanism.
2. Show the optimization target explicitly.
3. Use before/after artifact views to make changes legible.
4. Show evaluation examples so metrics feel grounded.
5. Be honest that current examples are deterministic proof datasets.

## Page Structure
1. Hero
   - product value proposition
   - one-line explanation of bounded optimization
   - CTA to GitHub repo + section jump to proof examples
2. What gets optimized
   - cards for artifact / evaluator / objective / constraints / rollback
3. Why this is different
   - keep/discard/rollback rules with real reasons
4. Proof examples
   - prompt artifact
   - routing policy artifact
   - each includes:
     - before artifact
     - best kept artifact
     - sample case comparisons
     - trial decision list
5. Footer honesty note
   - deterministic proof examples today
   - real benchmark-backed demos next

## Data Changes
Extend `docs/demo-data.json` with:
- beforeArtifact
- bestArtifact
- caseStudies[]
- concise problem statement per example

## Verification
- browser snapshot on local served page
- push to `main`
- verify live GitHub Pages page renders updated sections
