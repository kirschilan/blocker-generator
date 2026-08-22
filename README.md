# blocker-generator

Generates synthetic Jira-style issue exports and Xray-style blocker-link
exports for a portfolio of internal teams and external vendors/partners,
with inter-team and external blockers, for use by a management dashboard
that detects blockers and potential remedies using percolation-theory
practices.

See `specification/PROJECT.md` for the outcome and constraints,
`specification/ARCHITECTURE.md` for the domain model, `specification/BACKLOG.md`
for the current sprint's tasks, and `TEAM_OPERATING_SYSTEM.md` /
`DEFINITION_OF_DONE.md` for how the team (BP/PM/Code) works. `specification/` is
the locked single source of truth (see Issue #5 for the in-progress Sprint 1
rebuild against it).

## Quick start

**Note:** `src/generate_blocker_data.py` currently implements the older generic
portfolio model, not yet the finance-specific Sprint 1 scenario locked in
`specification/`. See Issue #5 for the in-progress rebuild.

```
python3 src/generate_blocker_data.py
```

Runs with defaults and writes:

- `data/teams.csv`
- `data/issues.csv`
- `data/blockers.csv`
- `docs/validation_report.md`

Run `python3 src/generate_blocker_data.py --help` for every tunable
parameter (team counts, issues per team, blocker density, external bias,
seed, output locations).

## Tests

```
pip install pytest
pytest tests/ -v
```

## Repo layout

```
/                 governance docs (this README, TEAM_OPERATING_SYSTEM.md,
                  DEFINITION_OF_DONE.md, session_log.md)
specification/    locked source of truth (PROJECT.md, ARCHITECTURE.md,
                  BACKLOG.md, TESTER.md)
_archive/         superseded generic docs (reference only)
src/              generate_blocker_data.py — the generator (stdlib only)
tests/            automated test suite
data/             generated CSVs
docs/             validation reports / analysis docs
```
