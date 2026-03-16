# SDD — Runtime-backed Demo Data

## Design
- Add `auto_refine/demo.py` to build demo data from:
  - static metadata (`docs/demo-config.json`)
  - latest matching run summary for each example
- Builder responsibilities:
  - resolve latest summary by glob
  - parse baseline and kept/discarded records
  - compute `baselineValue`, `bestValue`, `incumbentProgression`
  - extract `baselineArtifact` and `bestArtifact` from record `artifacts`
  - preserve narrative copy from metadata file

## CLI
Add command:

```bash
python3 -m auto_refine build-demo-data docs/demo-config.json --output docs/demo-data.json
```

## Validation
- Unit/integration-style builder test with temp config + temp summary file
- Re-run prompt/routing/self-marketing tasks to create current summaries
- Rebuild `docs/demo-data.json`
- Push and verify GitHub Pages
