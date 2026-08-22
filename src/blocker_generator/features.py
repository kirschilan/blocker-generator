"""Feature + blocker generation for the Sprint 1 Jira CSV.

Implements BACKLOG.md Task 1.4 against Tasks 1.1-1.3's squads, archetypes,
and cluster injection. Produces the row set for
`v1_auth_cluster_high_density.csv`.

Column-count note: TESTER.md's Sprint 1 "Row Counts & Data Volume" section
says "13 core columns + 12 Sprint columns (total 25)", but the mandatory
core-column list it (and ARCHITECTURE.md's "Core Columns" table) names
explicitly has 12 entries (Issue Key, Summary, Type, Status, Assignee,
Created, Resolved, Waiting Reason, Cycle Time (days), Test Automation,
External Blocker, Cluster Tag). This implementation uses the 12 explicitly
named columns (24 total with Sprint-1..12) rather than inventing an
unnamed 13th column; flagged in session_log.md / GitHub Issue.

Blocker-row-count note: TESTER.md also states "Total blocker rows: 15-30"
while separately requiring "Auth blocker count: 3-5 in week 3", "Checkout
blockers: 2-3", "Payments blockers: 2-3" -- which sums to at most 11, never
15-30. These two constraints are mutually unsatisfiable as written. This
implementation follows the specific per-squad ranges (they're also what
Task 1.3's cluster injection already produces and is tested against) over
the unreachable aggregate total; flagged in the same issue.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from blocker_generator.clusters import BlockerCluster, inject_cluster
from blocker_generator.squads import AUTH, CHECKOUT, PAYMENTS, Squad
from blocker_generator.sprints import SPRINT_COUNT, sprint_for_date, sprint_start_date

FEATURES_PER_SQUAD_PER_SPRINT_RANGE = (15, 20)

ISSUE_KEY_PREFIX = {AUTH: "SQ-A", CHECKOUT: "SQ-B", PAYMENTS: "SQ-D"}
ASSIGNEE = {AUTH: "auth-squad", CHECKOUT: "checkout-squad", PAYMENTS: "payments-squad"}

SQUAD_KEYWORDS = {
    AUTH: ["session handling", "token refresh", "MFA enrollment", "credential rotation",
           "login rate limiting", "password reset flow"],
    CHECKOUT: ["cart persistence", "checkout widget", "discount code", "order summary",
               "guest checkout", "cart abandonment email"],
    PAYMENTS: ["card tokenization", "wallet linking", "fraud rule tuning",
               "settlement batch", "refund workflow", "payment retry logic"],
}
SQUAD_VERBS = ["Add", "Fix", "Improve", "Refactor", "Investigate", "Harden", "Optimize", "Document"]

# BACKLOG.md Task 1.5 automation-coverage defaults: Selenium 50%, Postman
# 10%, Perfecto Mobile 10%, Swagger 5%, remainder Manual.
TEST_AUTOMATION_POOL = (
    ["Selenium"] * 50 + ["Manual"] * 25 + ["Postman"] * 10 + ["Perfecto Mobile"] * 10 + ["Swagger"] * 5
)

CORE_COLUMNS = [
    "Issue Key", "Summary", "Type", "Status", "Assignee", "Created", "Resolved",
    "Waiting Reason", "Cycle Time (days)", "Test Automation", "External Blocker", "Cluster Tag",
]
SPRINT_COLUMNS = [f"Sprint-{i}" for i in range(1, SPRINT_COUNT + 1)]
ALL_COLUMNS = CORE_COLUMNS + SPRINT_COLUMNS


@dataclass
class IssueRow:
    issue_key: str
    summary: str
    type: str
    status: str
    assignee: str
    created: datetime
    resolved: Optional[datetime]
    waiting_reason: str
    cycle_time_days: Optional[float]
    test_automation: Optional[str]
    external_blocker: bool
    cluster_tag: str


def _random_time_of_day(rng: random.Random) -> time:
    return time(hour=rng.randint(8, 17), minute=rng.choice([0, 15, 30, 45]))


def _random_cycle_time_days(rng: random.Random) -> float:
    # Mostly a short 2-10 day cycle; occasionally longer, so a few features
    # naturally span 3 sprints (TESTER.md: "some span 2-3" sprint columns).
    if rng.random() < 0.08:
        return round(rng.uniform(11, 20), 2)
    return round(rng.uniform(2, 10), 2)


def generate_features(rng: random.Random, squads: List[Squad]) -> tuple[List[IssueRow], Dict[str, int]]:
    """Task 1.4: 15-20 Story rows per squad per sprint, Status=Done."""
    counters: Dict[str, int] = {s.id: 0 for s in squads}
    rows: List[IssueRow] = []
    for sprint in range(1, SPRINT_COUNT + 1):
        sprint_start = sprint_start_date(sprint)
        for squad in squads:
            count = rng.randint(*FEATURES_PER_SQUAD_PER_SPRINT_RANGE)
            for _ in range(count):
                counters[squad.id] += 1
                key = f"{ISSUE_KEY_PREFIX[squad.id]}-{counters[squad.id]}"
                created_date = sprint_start + timedelta(days=rng.randint(0, 13))
                created = datetime.combine(created_date, _random_time_of_day(rng))
                cycle_time = _random_cycle_time_days(rng)
                resolved = created + timedelta(days=cycle_time)
                summary = f"{rng.choice(SQUAD_VERBS)} {rng.choice(SQUAD_KEYWORDS[squad.id])}"
                rows.append(
                    IssueRow(
                        issue_key=key,
                        summary=summary,
                        type="Story",
                        status="Done",
                        assignee=ASSIGNEE[squad.id],
                        created=created,
                        resolved=resolved,
                        waiting_reason="",
                        cycle_time_days=cycle_time,
                        test_automation=rng.choice(TEST_AUTOMATION_POOL),
                        external_blocker=False,
                        cluster_tag="",
                    )
                )
    return rows, counters


def generate_cluster_blockers(
    rng: random.Random, cluster: BlockerCluster, counters: Dict[str, int]
) -> List[IssueRow]:
    """Task 1.4: inject the cluster's blocker rows (Type=Sub-task, Status=Waiting).

    Each BlockerDay from Task 1.3's injection becomes its own issue: still
    Waiting at generation time (this is a point-in-time synthetic export,
    not a live system), so Resolved / Cycle Time stay null, and the
    root-vs-cascade day-by-day Created timestamps are what makes the
    cascade timing visible (ARCHITECTURE.md's "Cascade Logic").
    """
    rows: List[IssueRow] = []
    for entry in inject_cluster(cluster):
        counters[entry.squad_id] += 1
        key = f"{ISSUE_KEY_PREFIX[entry.squad_id]}-{counters[entry.squad_id]}"
        created = datetime.combine(entry.date, _random_time_of_day(rng))
        summary = (
            "Session cache corruption in Auth service"
            if entry.is_root
            else "Feature blocked pending Auth service fix"
        )
        rows.append(
            IssueRow(
                issue_key=key,
                summary=summary,
                type="Sub-task",
                status="Waiting",
                assignee=ASSIGNEE[entry.squad_id],
                created=created,
                resolved=None,
                waiting_reason=entry.waiting_reason,
                cycle_time_days=None,
                test_automation=None,
                external_blocker=False,
                cluster_tag=entry.cluster_id,
            )
        )
    return rows


def spanned_sprints(created: datetime, resolved: Optional[datetime]) -> List[int]:
    start_sprint = max(1, sprint_for_date(created.date()))
    end_sprint = start_sprint if resolved is None else sprint_for_date(resolved.date())
    end_sprint = min(max(end_sprint, start_sprint), SPRINT_COUNT)
    return list(range(start_sprint, end_sprint + 1))


def row_to_csv_dict(row: IssueRow) -> Dict[str, str]:
    d = {
        "Issue Key": row.issue_key,
        "Summary": row.summary,
        "Type": row.type,
        "Status": row.status,
        "Assignee": row.assignee,
        "Created": row.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Resolved": row.resolved.strftime("%Y-%m-%dT%H:%M:%SZ") if row.resolved else "",
        "Waiting Reason": row.waiting_reason,
        "Cycle Time (days)": f"{row.cycle_time_days:.2f}" if row.cycle_time_days is not None else "",
        "Test Automation": row.test_automation or "",
        "External Blocker": "true" if row.external_blocker else "false",
        "Cluster Tag": row.cluster_tag,
    }
    spans = spanned_sprints(row.created, row.resolved)
    for i in range(1, SPRINT_COUNT + 1):
        col = f"Sprint-{i}"
        if i not in spans:
            d[col] = ""
        elif i == spans[0]:
            d[col] = row.created.date().isoformat()
        else:
            d[col] = sprint_start_date(i).isoformat()
    return d


def generate_dataset(seed: int, squads: List[Squad], cluster: BlockerCluster) -> List[IssueRow]:
    rng = random.Random(seed)
    features, counters = generate_features(rng, squads)
    blockers = generate_cluster_blockers(rng, cluster, counters)
    return features + blockers
