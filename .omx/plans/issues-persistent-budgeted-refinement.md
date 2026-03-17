# Issue Breakdown — Persistent / Budgeted Refinement

## WS1 — Engine state
- [ ] add `state.json` persistence
- [ ] store incumbent snapshot in run dir
- [ ] load existing ledger records for resume

## WS2 — Runtime
- [ ] add latest-run lookup for a task
- [ ] add resume execution path with total trial budget
- [ ] keep one-shot run path working

## WS3 — CLI / docs
- [ ] add `resume --task ... --budget ...`
- [ ] document persistent refinement in README

## WS4 — Verification
- [ ] add integration test for resume
- [ ] run resume flow on repo-owned self-task
- [ ] keep full test suite green
