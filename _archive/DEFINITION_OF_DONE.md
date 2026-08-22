# DEFINITION_OF_DONE.md

## Decision rights

| Decision | Owner |
|---|---|
| What ships this sprint (`BACKLOG.md`) | PM |
| Domain model / file schemas (`ARCHITECTURE.md`) | PM (Code may propose changes via Issue) |
| Whether the dataset's narrative is usable for a demo | BP |
| Implementation approach, test coverage | Code |
| Whether automated tests are sufficient | Code, checked by PM's manual spot-check |

## Scope-change rule

If implementing a task reveals that `ARCHITECTURE.md` or `BACKLOG.md` is
wrong, ambiguous, or insufficient: **stop, open a GitHub Issue describing
the gap, do not silently improvise the domain model.** PM updates the
artifact; Code resumes once it's updated. Small clarifications (a default
value, a naming detail) that don't change behavior or the schema may be
made inline with a note in the PR description — anything that changes a
CSV column, an entity relationship, or a CLI flag's meaning requires the
artifact update first.

## Definition of Done — per task

A `BACKLOG.md` task is done when:

1. A PR exists, titled/linked to the task number, referencing the
   relevant `ARCHITECTURE.md` section in its commit message(s).
2. Automated tests for the task's behavior exist under `tests/` and pass
   (`TESTER.md` §Automated checks).
3. The PR is merged to `main`.

## Definition of Done — Sprint

The sprint is done when:

- All tasks 1.1–1.6 are merged to `main`.
- The full automated test suite passes on `main`.
- PM has run the manual spot-checks in `TESTER.md` against the CSVs in
  `data/` and signed off (recorded in `session_log.md`).
- `docs/validation_report.md` is current and BP has what they need to do
  narrative validation.
- No open "blocked" GitHub Issues against Sprint 1 tasks.
