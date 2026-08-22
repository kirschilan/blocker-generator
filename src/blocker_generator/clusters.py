"""Blocker cluster injection.

Implements BACKLOG.md Task 1.3: inject Cluster 1 (Auth Service Outage,
ARCHITECTURE.md "Cluster Topology") onto the calendar.

Modeling choice, made explicit here because ARCHITECTURE.md's own Cluster 1
narrative is internally inconsistent (it states "duration 3 days" and
"Weeks 3-5" as the cluster's window, but its day-by-day timeline says the
root resolves "Week 4, Day 3" -- nine days after onset, not three -- which
contradicts both the stated duration and BACKLOG.md Task 1.3's own
verification text: "Auth on days 1-3 (week 3), Checkout/Payments on days
2-4 (1-day lag)"). This implementation follows the self-consistent,
BACKLOG.md-matching reading:

- Root (Auth) blocker: active on onset_day, onset_day+1, ..., for
  `duration_days` days (days 1-3 of week 3).
- Cascade (Checkout, Payments) blockers: created `cascade_lag_days` after
  the root (day 2), active for the same duration, so they clear
  `propagation_lag_days` after the root clears (active days 2-4).

Flagged in session_log.md / a GitHub Issue for whoever reconciles the
"Week 4" narrative wording in ARCHITECTURE.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List

from blocker_generator.archetypes import SHARED_COMP_FAILURE
from blocker_generator.squads import AUTH, CHECKOUT, PAYMENTS
from blocker_generator.sprints import week_day_to_date


@dataclass(frozen=True)
class BlockerCluster:
    cluster_id: str
    archetype_id: str
    root_squad: str
    cascade_squads: List[str]
    onset_week: int
    onset_day: int
    duration_days: int
    cascade_lag_days: int
    propagation_lag_days: int
    root_waiting_reason: str
    cascade_waiting_reason: str


@dataclass(frozen=True)
class BlockerDay:
    squad_id: str
    date: date
    cluster_id: str
    waiting_reason: str
    is_root: bool


CLUSTER_1_AUTH = BlockerCluster(
    cluster_id="Cluster-1-Auth",
    archetype_id=SHARED_COMP_FAILURE.type_id,
    root_squad=AUTH,
    cascade_squads=[CHECKOUT, PAYMENTS],
    onset_week=3,
    onset_day=1,
    duration_days=3,
    cascade_lag_days=1,
    propagation_lag_days=1,
    root_waiting_reason="Session cache corruption in Auth service; fix in progress",
    cascade_waiting_reason="Waiting on Login service (SQ-A)",
)


def inject_cluster(cluster: BlockerCluster) -> List[BlockerDay]:
    """Expand a BlockerCluster into one BlockerDay per squad per active day."""
    root_start = week_day_to_date(cluster.onset_week, cluster.onset_day)
    entries: List[BlockerDay] = [
        BlockerDay(cluster.root_squad, root_start + timedelta(days=offset), cluster.cluster_id, cluster.root_waiting_reason, True)
        for offset in range(cluster.duration_days)
    ]

    cascade_start = root_start + timedelta(days=cluster.cascade_lag_days)
    # Cascade blockers clear propagation_lag_days after the root clears, so
    # they're active for (duration + propagation_lag - cascade_lag) days.
    cascade_duration = cluster.duration_days + cluster.propagation_lag_days - cluster.cascade_lag_days
    for squad in cluster.cascade_squads:
        entries.extend(
            BlockerDay(squad, cascade_start + timedelta(days=offset), cluster.cluster_id, cluster.cascade_waiting_reason, False)
            for offset in range(cascade_duration)
        )
    return entries


def print_cluster_impact(entries: List[BlockerDay]) -> None:
    """Verification helper (BACKLOG.md Task 1.3: "Print cluster impact ...
    for each day")."""
    by_day = {}
    for entry in entries:
        by_day.setdefault(entry.date, []).append(entry.squad_id)
    for day in sorted(by_day):
        counts = ", ".join(f"{squad} blocker x1" for squad in by_day[day])
        print(f"{day.isoformat()}: {counts}")


if __name__ == "__main__":
    print_cluster_impact(inject_cluster(CLUSTER_1_AUTH))
