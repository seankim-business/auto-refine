# Review — Public GitHub Issue Triage Benchmark

Date: 2026-03-19
Mode: manual DEV/QA/PM/OPS review

## DEV
- Keep the benchmark local and deterministic.
- Public issue excerpts + source URLs are enough for credibility without live API dependence.

## QA
- Test should reset baseline policy before running.
- Need at least one kept candidate and one discard due to safety/over-escalation.

## PM
- This is a much better credibility demo than the current toy-only lineup.
- Must be framed as semi-real/public benchmark-backed, not a production classifier.

## OPS
- No network calls during example runs.
- Store all outputs under `examples/.../runs` as before.

## Verdict
PASS
