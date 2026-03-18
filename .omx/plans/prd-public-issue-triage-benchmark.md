# PRD — Public GitHub Issue Triage Benchmark

Date: 2026-03-19
Repo: `/Users/sean/.openclaw/workspace/projects/auto-refine`

## Problem
`auto-refine` currently demonstrates only deterministic local proof tasks. The runtime is real, but the benchmark artifacts and datasets are obviously toy-like, which weakens product credibility.

## Goal
Add a semi-real benchmark-backed example based on public GitHub issues so the repo can show a more credible bounded optimization task.

## Chosen benchmark
A local issue-triage routing task built from public issues in `cli/cli`:
- artifact: `policy.json`
- dataset: selected public issues with title/body excerpts and expected routes
- evaluator: deterministic local scoring on accuracy, manual review rate, and safety failures
- proposer: bounded policy variants

## Acceptance Criteria
1. Add new example under `examples/github_issue_triage_public/`.
2. Dataset contains real public issue excerpts and source URLs.
3. Example produces one keep and multiple discard outcomes.
4. Add integration test.
5. Surface the example in README and GitHub Pages demo.
6. Rebuild runtime-backed `docs/demo-data.json` from actual run summaries.

## Non-Goals
- live GitHub API evaluation during task runs
- LLM-based issue classification
- production-grade classifier accuracy

## Success Metric
A visitor can see that auto-refine can optimize against a recognizably real public benchmark, not only synthetic toy inputs.
