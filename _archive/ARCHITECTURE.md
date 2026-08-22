# ARCHITECTURE.md

Unambiguous domain model for the generator. Code implements exactly this;
if something's missing here, open an issue rather than guessing.

## Entities

### Team
| field | type | notes |
|---|---|---|
| team_id | str | `T01`, `T02`, ... stable, zero-padded |
| name | str | e.g. `Atlas`, `Vendor-Cygnus Logistics` |
| type | enum | `Internal` \| `External` |
| capacity_points | int | synthetic team capacity, 20–60 |

### Issue
| field | type | notes |
|---|---|---|
| issue_key | str | `<TEAMPREFIX>-<n>`, e.g. `ATL-104` |
| team_id | str | FK -> Team.team_id |
| issue_type | enum | `Epic` \| `Story` \| `Task` \| `Bug` |
| status | enum | `To Do` \| `In Progress` \| `Blocked` \| `In Review` \| `Done` |
| priority | enum | `Lowest` \| `Low` \| `Medium` \| `High` \| `Highest` |
| summary | str | short synthetic sentence |
| story_points | int | Fibonacci-ish: 1,2,3,5,8,13 |
| created | date (ISO) | |
| updated | date (ISO) | >= created |
| resolved | date (ISO) or empty | set only if status == Done |
| sprint | str | e.g. `Sprint 1` |

### BlockerLink (Xray-style "blocks" relationship)
| field | type | notes |
|---|---|---|
| link_id | str | `BLK-<n>` |
| blocking_issue | str | FK -> Issue.issue_key (the cause) |
| blocked_issue | str | FK -> Issue.issue_key (the effect) |
| link_type | str | always `blocks` in Sprint 1 |
| category | enum | `Intra-Team` \| `Inter-Team` \| `External` (derived, see below) |
| severity | enum | `Low` \| `Medium` \| `High` \| `Critical` |
| raised_date | date (ISO) | |
| resolved_date | date (ISO) or empty | empty means still active |
| is_active | bool | `resolved_date == ""` |

**Category derivation** (not a free choice — computed from the teams of
the two issues involved):
- `blocking_issue.team == blocked_issue.team` → `Intra-Team`
- both teams `Internal` but different → `Inter-Team`
- either team is `External` → `External`

No issue may block itself. A given ordered `(blocking_issue, blocked_issue)`
pair appears at most once.

## Percolation model

The blocker graph is undirected for analysis purposes: nodes are issues,
edges are blocker links (direction is kept in the CSV for Xray fidelity,
but connectivity analysis treats `blocks` as an edge between two nodes).

Generation is a tunable random-graph process, analogous to bond
percolation:

- `--blocker-density p` (0.0–1.0): for each issue, an edge to a random
  *other* issue is added independently with probability `p`. Expected
  edge count ≈ `p * num_issues`.
- `--external-bias q` (0.0–1.0): when an edge is added, the blocking issue
  is drawn from an external-team issue with probability `q` (if any exist),
  otherwise from any issue — this is what lets the dataset simulate
  vendor-driven blockages without hardcoding which vendor.

As `p` increases, the dataset moves from many small disconnected blocker
clusters toward one giant connected component spanning most issues — the
percolation transition the downstream dashboard is meant to detect. The
generator reports this directly: **largest-component fraction** (order
parameter) and **component count**, computed via union-find over the
blocker graph, written to `docs/validation_report.md`.

## File layout

```
src/generate_blocker_data.py   # generator (stdlib only)
tests/test_blocker_generator.py
data/teams.csv
data/issues.csv
data/blockers.csv
docs/validation_report.md      # regenerated each run
```

## CLI surface (Task 1.4)

```
python src/generate_blocker_data.py \
  --num-internal-teams 5 --num-external-teams 3 \
  --issues-per-team 25 \
  --blocker-density 0.35 --external-bias 0.3 \
  --resolved-ratio 0.4 \
  --seed 42 \
  --output-dir data --report-dir docs
```
All flags have defaults; running with no args produces a complete,
reproducible dataset.
