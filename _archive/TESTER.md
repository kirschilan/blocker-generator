# TESTER.md

Shared agreement on what "verified" means, split by who does it.

## Automated checks (Code, `tests/test_blocker_generator.py`, run via `pytest`)

- **Schema**: every `Team` / `Issue` / `BlockerLink` field matches the
  types and enums in `ARCHITECTURE.md`; CSV headers match exactly.
- **Referential integrity**: every `Issue.team_id` exists in `teams.csv`;
  every `BlockerLink.blocking_issue` / `blocked_issue` exists in
  `issues.csv`.
- **Invariants**: no issue blocks itself; no duplicate
  `(blocking_issue, blocked_issue)` pairs; `category` is always correctly
  derived from the two teams involved (not just randomly assigned).
- **Determinism**: two runs with the same `--seed` produce byte-identical
  CSVs; a different seed produces a different dataset.
- **Percolation stats**: the largest-connected-component calculation is
  correct against a hand-built small graph, and `--blocker-density 0`
  yields zero blocker links / a largest-component fraction of one issue.
- **CLI smoke test**: running the script end-to-end into a temp directory
  produces all three CSVs, non-empty, with the row counts implied by the
  arguments.

Run with: `pytest tests/ -v`. This must pass before any PR merges.

## Manual spot-checks (PM, on merged `main` output in `data/`)

- Open `teams.csv` — team names/types look sane, external vendors are
  clearly distinguishable from internal teams.
- Open `issues.csv` — spot-check 5–10 rows for internally consistent
  dates (`created <= updated`, `resolved` only set when `status == Done`).
- Open `blockers.csv` — pick a few `External` and `Inter-Team` rows and
  manually confirm the category against the teams of the two issues in
  `issues.csv`.
- Re-run the generator with a couple of different `--blocker-density`
  values and confirm `docs/validation_report.md`'s largest-component
  fraction moves in the expected direction (up as density goes up).
- Record sign-off (pass/issues found) in `session_log.md`.

## Narrative validation (BP, on `docs/validation_report.md` + CSVs)

- Does the mix of internal vs. external blockers look like something a
  real engineering org would recognize?
- Is there a clear "story" in the largest cluster (e.g., one vendor
  showing up as a recurring blocker source) that a dashboard demo could
  tell?
- Flag anything that reads as implausible (e.g., every team blocked by
  every other team equally, with no discernible pattern) as a GitHub
  Issue against `BACKLOG.md` generation parameters, not as a code bug.
