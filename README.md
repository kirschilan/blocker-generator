# blocker-generator

Synthetic Jira + Xray data for 3 squads (Auth, Checkout, Payments), 12
sprints, and 1 injected blocker cluster (an Auth service outage that
cascades to its dependent squads). This is Sprint 1 of a larger finance-
domain dataset generator — see `specification/PROJECT.md` for the full
scope and `specification/BACKLOG.md` for what's built vs. deferred to
Sprint 2/3.

## The hypothesis

The generator exists to test a **percolation-theory** approach to blocker
detection: model an org's work as a graph where blockers are edges between
issues, and look for the point where local blockages merge into one large
connected cluster of stuck work. Sprint 1 proves this at the smallest
possible scale — one blocker cluster, three squads — showing that the
Auth service outage visibly halts Auth's own work and then cascades to
Checkout and Payments with a measurable 1-day lag, both in when their
blockers start and when they clear. Sprint 3 scales this to the full
8-squad, 3-cluster topology where blocker density is meant to cross the
percolation threshold and visibly stall flow dataset-wide.

## Quick start

```
pip install pytest
pytest tests/ -v
```

The committed CSVs in `data/` were generated with `--seed 42` and are
ready to use as-is:

```python
import csv

with open("data/v1_auth_cluster_high_density.csv") as f:
    rows = list(csv.DictReader(f))

waiting = [r for r in rows if r["Status"] == "Waiting"]
# All 9 Waiting rows fall in a 4-day window (Jul 15-18, 2026) -- the
# visible Auth-cluster cascade. Import into Tableau/Excel and filter
# Status = Waiting, or group by Assignee + Created, to see it directly.
```

See `docs/VALIDATION_REPORT_Sprint_1.md` for the full dataset summary
(row counts, cascade timing, density, test coverage) and how to read it
in a viz tool.

## Repo layout

```
specification/          locked spec docs (source of truth for the domain
                         model): PROJECT, BACKLOG, ARCHITECTURE, TESTER,
                         ETHICS_AGREEMENT
src/blocker_generator/   the generator (squads, archetypes, cluster
                         injection, feature + test-log generation)
tests/                   automated test suite (pytest)
data/                    committed example CSVs (reproducible via seed)
docs/                    validation reports
_archive/                an earlier, generic (non-finance-domain)
                         version of the generator, kept for reference
```

## Limitations (Sprint 1)

- Synthetic data — waiting reasons are templates, not real tickets.
- Only 1 of the eventual 3 blocker clusters is injected (Auth only).
- Only 3 of the eventual 8 squads are modeled.
- Global blocker density (~1-2%) won't by itself show a percolation-
  threshold "flow stall" — that's Sprint 3's full topology. Sprint 1
  proves the cluster's cascade timing and local density are correct.

Ready for PM spot-check and Business Partner narrative validation per
`specification/TESTER.md`.
