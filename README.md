# blocker-generator

Synthetic Jira + Xray-style data for 3 squads (Auth, Checkout, Payments),
12 sprints, with 1 injected blocker cluster — for a management dashboard
that detects blocker clusters and potential remedies using
percolation-theory practices.

See `specification/PROJECT.md` for the outcome and constraints,
`specification/ARCHITECTURE.md` for the domain model,
`specification/BACKLOG.md` for the current Iteration's tasks, and
`TEAM_OPERATING_SYSTEM.md` / `DEFINITION_OF_DONE.md` / `CLAUDE.md` for how
the team (BP/PM/Code) works.

**Hypothesis:** percolation theory — a shared-component failure (Auth) halts
not just its own squad but cascades to dependent squads, visible as a
blocker-density spike that crosses a percolation threshold within its own
time window.

**Limitations:** synthetic, not historically accurate; only the Auth
cluster (1 of the 3 clusters in the full domain model); only 3 of 8 squads;
no external dependencies yet (deferred, see `specification/BACKLOG.md` Task
1.1).

## Quick start

```
PYTHONPATH=src python3 -m blocker_generator
```

Runs with defaults (seed 42) and writes:

- `data/v1_auth_cluster_high_density.csv` (Jira format)
- `data/v1_auth_cluster_test_logs.csv` (Xray format)
- `docs/VALIDATION_REPORT_Iteration_1.md`

Run `PYTHONPATH=src python3 -m blocker_generator --help` for tunable
parameters (seed, output/report directories). Same seed always produces
byte-identical CSVs (regression-safe).

## Tests

```
pip install pytest
pytest tests/ -v
```

## Repo layout

```
/                        process docs (this README, CLAUDE.md,
                         TEAM_OPERATING_SYSTEM.md, DEFINITION_OF_DONE.md,
                         session_log.md)
specification/           PROJECT.md, ARCHITECTURE.md, BACKLOG.md, TESTER.md —
                         single source of truth for outcomes, domain model,
                         current Iteration's tasks, and verification
src/blocker_generator/   the generator package (stdlib only):
                         squads, archetypes, clusters, features, xray_logs,
                         csv_io, __main__ (CLI)
tests/                   automated test suite
data/                    generated CSVs (committed; regenerable via the CLI)
docs/                    validation reports
```
