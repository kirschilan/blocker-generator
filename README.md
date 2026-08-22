# blocker-generator

Generates synthetic Jira-style issue exports and Xray-style blocker-link
exports for a portfolio of internal teams and external vendors/partners,
with inter-team and external blockers, for use by a management dashboard
that detects blockers and potential remedies using percolation-theory
practices.

See `PROJECT.md` for the outcome and constraints, `ARCHITECTURE.md` for the
domain model, `BACKLOG.md` for the current sprint's tasks, and
`TEAM_OPERATING_SYSTEM.md` / `DEFINITION_OF_DONE.md` for how the team
(BP/PM/Code) works.

## Quick start

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
/                 process docs (this README, PROJECT.md, ARCHITECTURE.md,
                  BACKLOG.md, TESTER.md, TEAM_OPERATING_SYSTEM.md,
                  DEFINITION_OF_DONE.md, session_log.md)
src/              generate_blocker_data.py — the generator (stdlib only)
tests/            automated test suite
data/             generated CSVs
docs/             validation reports / analysis docs
```
