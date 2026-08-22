# BACKLOG.md — Sprint 1

Six vertical slices, each independently mergeable and each leaving the
generator in a working, testable state. See `ARCHITECTURE.md` for the
domain model each task implements.

## Task 1.1 — Teams and issue seed data
Implement `Team` and `Issue` dataclasses and `build_teams()` /
`build_issues()`. Given a seeded RNG, produce internal + external teams
and a set of issues distributed across them, with all `Issue` fields
populated per the schema (dates internally consistent, `resolved` only
set when `status == Done`).

## Task 1.2 — Blocker link generation with percolation control
Implement `BlockerLink` and `build_blockers()`: the tunable random-graph
process from `ARCHITECTURE.md` §Percolation model (`--blocker-density`,
`--external-bias`, `--resolved-ratio`), with `category` always *derived*
from the teams of the two issues involved, never chosen independently.

## Task 1.3 — CSV export
Write `teams.csv`, `issues.csv`, `blockers.csv` with the exact headers and
field order from `ARCHITECTURE.md`. Referential integrity guaranteed by
construction (issues/teams generated before blockers reference them).

## Task 1.4 — CLI and configuration
`argparse` interface exposing every generation parameter plus `--seed`,
`--output-dir`, `--report-dir`. Sensible defaults so `python
src/generate_blocker_data.py` with no args produces a complete dataset.

## Task 1.5 — Automated test suite
`tests/test_blocker_generator.py` implementing every check listed in
`TESTER.md` §Automated checks: schema, referential integrity, invariants,
determinism, percolation-stats correctness, CLI smoke test.

## Task 1.6 — Validation report generation
Compute percolation statistics (largest-component fraction, component
count, category breakdown) via union-find over the blocker graph and
write them as `docs/validation_report.md` — the artifact BP uses for
narrative validation and PM uses to confirm density sweeps behave as
expected.

## Sprint exit
All six tasks merged to `main`, `pytest tests/` green, `data/*.csv` and
`docs/validation_report.md` regenerated from the merged code, PM manual
spot-check recorded in `session_log.md`.
