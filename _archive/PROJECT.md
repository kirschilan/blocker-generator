# PROJECT.md

## What we're building

`blocker-generator` produces synthetic Jira-style issue exports and
Xray-style blocker-link exports for a *portfolio* of teams — some internal,
some external vendors/partners. The output feeds a downstream management
dashboard that detects organizational blockers and suggests remedies using
**percolation theory**: it models blocking dependencies as a graph and looks
for the point at which local blockages merge into one large connected
cluster of stuck work (a percolating cluster), plus the specific links
whose removal would most shrink that cluster.

We are not building the dashboard. We are building its test fixture: a
realistic, tunable, reproducible dataset generator.

## Outcome

A teammate (PM, BP, or a dashboard engineer) can run one command and get:

1. `teams.csv` — the roster of internal teams and external vendors/partners
2. `issues.csv` — a Jira-style issue export across those teams
3. `blockers.csv` — an Xray-style "blocks" link export between issues,
   tagged by category (intra-team / inter-team / external)
4. A validation report (`docs/validation_report.md`) summarizing the
   dataset's shape — team/category breakdown and percolation statistics
   (largest connected cluster of blocked work, as a fraction of all
   issues) — so a non-technical reader can sanity-check the story the data
   tells before it's used in a demo or a dashboard test.

## Constraints

- **No real data.** Everything is synthetic; no PII, no real company or
  vendor names.
- **Deterministic.** The same `--seed` always produces byte-identical CSVs,
  so tests and demos are reproducible.
- **Configurable scale.** Number of teams, issues per team, and blocker
  density must be CLI parameters — the dashboard team needs to test both
  small (sparse) and large (percolating) scenarios.
- **Plain CSV, standard library only.** Output must import cleanly into
  spreadsheet tools and the dashboard's importer without extra tooling.
  The generator itself has no third-party runtime dependencies.
- **Referential integrity.** Every blocker link must reference issue keys
  that actually exist in `issues.csv`; every issue must reference a team
  that exists in `teams.csv`.

## Out of scope (Sprint 1)

- The dashboard itself (blocker detection, remedy suggestion UI).
- Live Jira/Xray API integration — file-based export only.
- Multi-sprint issue history / burndown simulation.
