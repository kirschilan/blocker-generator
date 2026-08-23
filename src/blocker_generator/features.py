"""Feature + blocker generation for the Sprint 1 Jira CSV.

Implements BACKLOG.md Task 1.4 against Tasks 1.1-1.3's squads, archetypes,
and cluster injection. Produces the row set for
`v1_auth_cluster_high_density.csv`.

Resolved per PM's 2026-08-22 ruling (GitHub Issue #2; see BACKLOG.md /
TESTER.md's "updated 2026-08-22" sections for the reconciled criteria):
- Blocker rows: 7-11 total (Auth 3, Checkout 2-3, Payments 2-3) -- the
  small, cluster-accurate count Task 1.3 already produces.
- Blocker density is window-scoped to week 3 (where Task 1.3's cluster
  injection actually concentrates all activity), not the full "weeks 3-5"
  span or the global 12-sprint dataset: 20-30% within week 3, ~1-2%
  globally. Full percolation-threshold density is Sprint 3's job.

GitHub Issue #7 (2026-08-23): the Sprint column model is corrected here to
match real Jira CSV export behavior for a multi-value field -- the header
repeats the literal column name "Sprint" once per occupied slot (not
distinct "Sprint-1".."Sprint-12" names), and each cell holds the sprint's
*name* (e.g. "Sprint-3"), not a date. Slot count is sized to the actual
dataset's widest-spanning issue (see `max_sprint_span`), not a fixed 12.
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
    """Task 1.4: inject the cluster's blocker rows (Type=Sub-task).

    This dataset is a retrospective export of a completed 12-sprint quarter,
    so every blocker day has, by generation time, already run its course:
    Status resolves to "Done" and Resolved is populated a day after Created
    (day-granularity blocker), matching BACKLOG.md's "Auth blocker resolves
    day 3; downstream blockers clear day 4 (visible in Created/Resolved
    timestamps)". Per PM's 2026-08-23 ruling, `Waiting Reason` persists after
    resolution instead of being cleared -- Status carries current state,
    Waiting Reason carries the historical cluster signal needed for
    retrospective detection (PROJECT.md P1).
    """
    rows: List[IssueRow] = []
    for entry in inject_cluster(cluster):
        counters[entry.squad_id] += 1
        key = f"{ISSUE_KEY_PREFIX[entry.squad_id]}-{counters[entry.squad_id]}"
        created = datetime.combine(entry.date, _random_time_of_day(rng))
        resolved = created + timedelta(days=1)
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
                status="Done",
                assignee=ASSIGNEE[entry.squad_id],
                created=created,
                resolved=resolved,
                waiting_reason=entry.waiting_reason,
                cycle_time_days=(resolved - created).total_seconds() / 86400,
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


def sprint_name(sprint_number: int) -> str:
    """The value a real Jira export would show for a Sprint field -- the
    sprint's name, not a date. Our domain numbers sprints 1..12, so the
    name is just that number (Issue #7)."""
    return f"Sprint-{sprint_number}"


def max_sprint_span(rows: List["IssueRow"]) -> int:
    """Widest number of sprints any single issue in this dataset spans --
    sizes the repeated 'Sprint' header (Issue #7); not a fixed 12."""
    return max((len(spanned_sprints(r.created, r.resolved)) for r in rows), default=1)


def build_header(sprint_slots: int) -> List[str]:
    """Real Jira CSV export repeats the literal field name once per
    occupied multi-value slot -- 'Sprint','Sprint',... not 'Sprint-1',
    'Sprint-2' (Issue #7)."""
    return CORE_COLUMNS + ["Sprint"] * sprint_slots


def row_to_csv_row(row: IssueRow, sprint_slots: int) -> List[str]:
    core = [
        row.issue_key,
        row.summary,
        row.type,
        row.status,
        row.assignee,
        row.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        row.resolved.strftime("%Y-%m-%dT%H:%M:%SZ") if row.resolved else "",
        row.waiting_reason,
        f"{row.cycle_time_days:.2f}" if row.cycle_time_days is not None else "",
        row.test_automation or "",
        "true" if row.external_blocker else "false",
        row.cluster_tag,
    ]
    spans = spanned_sprints(row.created, row.resolved)
    sprint_values = [sprint_name(s) for s in spans]
    sprint_values += [""] * (sprint_slots - len(sprint_values))
    return core + sprint_values


def generate_dataset(seed: int, squads: List[Squad], cluster: BlockerCluster) -> List[IssueRow]:
    rng = random.Random(seed)
    features, counters = generate_features(rng, squads)
    blockers = generate_cluster_blockers(rng, cluster, counters)
    return features + blockers
