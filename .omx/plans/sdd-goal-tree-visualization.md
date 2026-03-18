# SDD — Goal Tree Visualization

## Data model
Extend demo-config with a `goalTrees` array.
Each entry contains:
- `id`
- `summaryGlob`
- `title`
- `problem`
- `whyItMatters`

Builder output includes merged runtime fields:
- `root`
- `generatedFrom`
- acceptance/rejection counts (computed)

## Rendering
Add a dedicated section after examples.
Render the root node and recurse through children.
For each node show:
- name
- hypothesis
- verdict badge
- reason
- depth
- task baseline / best if present

Use nested cards with left border / indentation for tree depth.

## Verification
- add demo builder test with fake `goal-tree-summary.json`
- rebuild live `docs/demo-data.json`
- inspect local page render
