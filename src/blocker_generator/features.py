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

BACKLOG.md PBI 2.0b/c/d (2026-08-23, BP's ruling on each): none of
`Cluster Tag`, `Cycle Time (days)`, or `External Blocker` are real Jira
fields.
- `Cluster Tag` -> Jira's native `Labels` field, which -- like `Sprint`
  (Issue #7) -- exports as one repeated column per occupied multi-value
  slot, not one comma-joined cell (confirmed: Atlassian JRACLOUD-85433 /
  JRASERVER-63747).
- `Cycle Time (days)` isn't exported by Jira at all (a real dashboard
  computes it from `Created`/`Resolved`) -- dropped from the CSV; kept as
  an internal field since `xray_logs.py` and the validation report still
  use it.
- `External Blocker` isn't a field Jira has either; the signal it carried
  is inherent to which blocker archetype produced the `Waiting Reason`
  text (an internal vs. external template), not a separate flag -- so
  it's removed rather than relabeled.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from blocker_generator.clusters import BlockerCluster, inject_cluster
from blocker_generator.squads import AUTH, CHECKOUT, CORE_BANKING, PAYMENTS, SAVINGS, Squad
from blocker_generator.sprints import SPRINT_COUNT, sprint_for_date, sprint_start_date

FEATURES_PER_SQUAD_PER_SPRINT_RANGE = (15, 20)

ISSUE_KEY_PREFIX = {
    AUTH: "SQ-A", CHECKOUT: "SQ-B", PAYMENTS: "SQ-D",
    CORE_BANKING: "SQ-C", SAVINGS: "SQ-E",  # BACKLOG.md Task 2.1/2.2
}
ASSIGNEE = {
    AUTH: "auth-squad", CHECKOUT: "checkout-squad", PAYMENTS: "payments-squad",
    CORE_BANKING: "core-banking-squad", SAVINGS: "savings-squad",  # Task 2.1/2.2
}

SQUAD_KEYWORDS = {
    AUTH: ["session handling", "token refresh", "MFA enrollment", "credential rotation",
           "login rate limiting", "password reset flow"],
    CHECKOUT: ["cart persistence", "checkout widget", "discount code", "order summary",
               "guest checkout", "cart abandonment email"],
    PAYMENTS: ["card tokenization", "wallet linking", "fraud rule tuning",
               "settlement batch", "refund workflow", "payment retry logic"],
    CORE_BANKING: ["account balance reconciliation", "ledger integrity check",
                   "transaction history pagination", "interest accrual calculation",
                   "statement generation", "double-entry validation"],
    SAVINGS: ["savings goal tracking", "interest rate tiering", "account opening flow",
              "auto-save rule", "goal progress notification", "savings withdrawal limit"],
}
SQUAD_VERBS = ["Add", "Fix", "Improve", "Refactor", "Investigate", "Harden", "Optimize", "Document"]

# BACKLOG.md Task 1.5 automation-coverage defaults: Selenium 50%, Postman
# 10%, Perfecto Mobile 10%, Swagger 5%, remainder Manual.
TEST_AUTOMATION_POOL = (
    ["Selenium"] * 50 + ["Manual"] * 25 + ["Postman"] * 10 + ["Perfecto Mobile"] * 10 + ["Swagger"] * 5
)

CORE_COLUMNS = [
    "Issue Key", "Summary", "Type", "Status", "Assignee", "Created", "Resolved",
    "Custom field (Waiting Reason)", "Custom field (Test Automation)",
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
    cycle_time_days: Optional[float]  # internal use only (xray_logs, validation report) -- not exported, PBI 2.0d
    test_automation: Optional[str]
    labels: List[str]  # exported as repeated "Labels" columns, PBI 2.0c


def _random_time_of_day(rng: random.Random) -> time:
    return time(hour=rng.randint(8, 17), minute=rng.choice([0, 15, 30, 45]))


def _random_cycle_time_days(rng: random.Random) -> float:
    # Mostly a short 2-10 day cycle; occasionally longer, so a few features
    # naturally span 3 sprints (TESTER.md: "some span 2-3" sprint columns).
    if rng.random() < 0.08:
        return round(rng.uniform(11, 20), 2)
    return round(rng.uniform(2, 10), 2)


# PBI 2.1 (2026-08-24): BP's observation -- every row was Status=Done,
# giving a dashboard nothing "currently open" to point at. A fixed
# fraction of ordinary feature work stays In Progress (no Resolved date),
# matching a realistic WIP snapshot rather than a fully-drained backlog.
# Aging itself is NOT computed here -- BP's ruling: the dashboard
# calculates it as NOW()-Created at report time, so we just need to leave
# some issues genuinely unresolved.
IN_PROGRESS_PROBABILITY = 0.08


def generate_features(rng: random.Random, squads: List[Squad]) -> tuple[List[IssueRow], Dict[str, int]]:
    """Task 1.4: 15-20 Story rows per squad per sprint. Most are Done;
    ~8% stay In Progress (PBI 2.1) as aging/at-risk candidates."""
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
                # Independent per-issue RNG, not the shared `rng` stream: an
                # issue's in-progress/done split shouldn't perturb every
                # later issue's created-date draw (and with it, week-level
                # distributions this seed's tests depend on).
                still_open = random.Random(f"{key}:in-progress").random() < IN_PROGRESS_PROBABILITY
                if still_open:
                    status, resolved, cycle_time = "In Progress", None, None
                else:
                    status = "Done"
                summary = f"{rng.choice(SQUAD_VERBS)} {rng.choice(SQUAD_KEYWORDS[squad.id])}"
                rows.append(
                    IssueRow(
                        issue_key=key,
                        summary=summary,
                        type="Story",
                        status=status,
                        assignee=ASSIGNEE[squad.id],
                        created=created,
                        resolved=resolved,
                        waiting_reason="",
                        cycle_time_days=cycle_time,
                        test_automation=rng.choice(TEST_AUTOMATION_POOL),
                        labels=[],
                    )
                )
    return rows, counters


def generate_cluster_blockers(
    rng: random.Random, cluster: BlockerCluster, counters: Dict[str, int]
) -> List[IssueRow]:
    """Task 1.4: inject the cluster's blocker rows (Type=Sub-task).

    Root (Auth) blocker days all resolve to Done, matching BACKLOG.md's
    "Auth blocker resolves day 3" exactly. Per PM's 2026-08-23 ruling,
    `Waiting Reason` persists after resolution instead of being cleared --
    Status carries current state, Waiting Reason carries the historical
    cluster signal needed for retrospective detection (PROJECT.md P1).

    PBI 2.1 (2026-08-24, BP's observation): each cascade squad's *last*
    day stays genuinely open (Status=Waiting, no Resolved) rather than
    also resolving -- BACKLOG.md's own "downstream blockers clear day 4"
    is a propagation *lag* relative to the root resolving on day 3; the
    report is implicitly taken at that moment, so the cascade's final
    clearing hasn't happened yet. Earlier cascade days still resolve
    normally (the historical, already-cleared portion of the incident).
    """
    entries = inject_cluster(cluster)
    last_index_per_squad: Dict[str, int] = {}
    for i, entry in enumerate(entries):
        last_index_per_squad[entry.squad_id] = i

    rows: List[IssueRow] = []
    for i, entry in enumerate(entries):
        counters[entry.squad_id] += 1
        key = f"{ISSUE_KEY_PREFIX[entry.squad_id]}-{counters[entry.squad_id]}"
        created = datetime.combine(entry.date, _random_time_of_day(rng))
        still_open = not entry.is_root and i == last_index_per_squad[entry.squad_id]
        if still_open:
            status, resolved, cycle_time = "Waiting", None, None
        else:
            resolved = created + timedelta(days=1)
            status, cycle_time = "Done", (resolved - created).total_seconds() / 86400
        rows.append(
            IssueRow(
                issue_key=key,
                summary=entry.summary,
                type="Sub-task",
                status=status,
                assignee=ASSIGNEE[entry.squad_id],
                created=created,
                resolved=resolved,
                waiting_reason=entry.waiting_reason,
                cycle_time_days=cycle_time,
                test_automation=None,
                labels=[entry.cluster_id],
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


def max_label_span(rows: List["IssueRow"]) -> int:
    """Widest number of labels any single issue in this dataset carries --
    sizes the repeated 'Labels' header (PBI 2.0c), same convention as
    Sprint (Issue #7): Jira exports one column per occupied label slot,
    not a comma-joined cell."""
    return max((len(r.labels) for r in rows), default=0)


def build_header(label_slots: int, sprint_slots: int) -> List[str]:
    """Real Jira CSV export repeats a multi-value field's literal name
    once per occupied slot -- 'Sprint','Sprint',... (Issue #7) and
    'Labels','Labels',... (PBI 2.0c) -- not a single joined cell."""
    return CORE_COLUMNS + ["Labels"] * label_slots + ["Sprint"] * sprint_slots


def row_to_csv_row(row: IssueRow, label_slots: int, sprint_slots: int) -> List[str]:
    core = [
        row.issue_key,
        row.summary,
        row.type,
        row.status,
        row.assignee,
        row.created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        row.resolved.strftime("%Y-%m-%dT%H:%M:%SZ") if row.resolved else "",
        row.waiting_reason,
        row.test_automation or "",
    ]
    label_values = list(row.labels) + [""] * (label_slots - len(row.labels))
    spans = spanned_sprints(row.created, row.resolved)
    sprint_values = [sprint_name(s) for s in spans]
    sprint_values += [""] * (sprint_slots - len(sprint_values))
    return core + label_values + sprint_values


def generate_dataset(seed: int, squads: List[Squad], clusters: List[BlockerCluster]) -> List[IssueRow]:
    """BACKLOG.md Task 2.2: accepts 2+ clusters (previously a single
    cluster) so Milestone 2's dataset can inject Auth + DataPlatform
    together. Clusters share one counters dict so issue-key numbering
    stays sequential per squad across clusters -- no key collisions
    regardless of how many clusters touch the same squad."""
    rng = random.Random(seed)
    features, counters = generate_features(rng, squads)
    blockers: List[IssueRow] = []
    for cluster in clusters:
        blockers.extend(generate_cluster_blockers(rng, cluster, counters))
    return features + blockers
