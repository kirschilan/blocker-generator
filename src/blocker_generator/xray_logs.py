"""Xray-like test execution log generation.

Implements BACKLOG.md Task 1.5 against Task 1.4's feature CSV and
TESTER.md's Sprint 1 "Test Execution Log Format" / "Automation Coverage
Distribution" / "Flaky Test Correlation" checks.

Only Story (feature) rows get test logs -- Sub-task (blocker) rows from
Task 1.4 represent a squad waiting on something else, not a testable
feature, so they're excluded here.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from blocker_generator.features import IssueRow
from blocker_generator.sprints import sprint_for_date, week_for_date

TEST_TYPES = ["Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile"]

# BACKLOG.md Task 1.5 / TESTER.md "Automation Coverage Distribution":
# Manual always; Selenium ~50%, Postman ~10%, Perfecto Mobile ~10%,
# Swagger ~5%. Nudged a few points above the literal figures so the
# resulting row count actually lands in TESTER.md's stated 1,200-1,500
# range ("roughly 2-3 test types per feature x 3 squads x 12 sprints") --
# the literal percentages alone average ~1.75 types/feature, landing at
# ~1,130 rows, short of the stated floor. See session_log.md.
PRESENCE_PROB = {
    "Manual": 1.0,
    "Selenium": 0.55,
    "Postman": 0.15,
    "Perfecto Mobile": 0.15,
    "Swagger": 0.10,
}

# TESTER.md "Flaky Test Correlation": 15-20% of tests flaky in the Auth
# cluster's weeks 3-5, concentrated in Selenium + Perfecto Mobile
# ("automation-heavy"); elsewhere, flakiness is low background noise.
FLAKY_CHANCE_IN_WINDOW_AUTOMATION_HEAVY = 0.45
FLAKY_CHANCE_BASELINE = 0.03
FLAKY_FAIL_RATIO_RANGE = (0.20, 0.30)


@dataclass
class TestLogRow:
    issue_key: str
    sprint: int
    test_type: str
    test_count: int
    pass_count: int
    fail_count: int
    flaky: bool
    automation_coverage_pct: float
    executed_date: datetime


def _generate_type_counts(
    rng: random.Random, present_types: List[str], in_cluster_window: bool
) -> Dict[str, Tuple[int, int, int, bool]]:
    """type -> (test_count, pass_count, fail_count, flaky)."""
    counts: Dict[str, Tuple[int, int, int, bool]] = {}
    for test_type in present_types:
        # Automated suites tend to run more cases than a manual pass, which
        # is what pulls per-feature automation coverage into TESTER.md's
        # 40-60% average band.
        total = rng.randint(3, 6) if test_type == "Manual" else rng.randint(5, 12)
        automation_heavy = test_type in ("Selenium", "Perfecto Mobile")
        flaky_chance = (
            FLAKY_CHANCE_IN_WINDOW_AUTOMATION_HEAVY
            if in_cluster_window and automation_heavy
            else FLAKY_CHANCE_BASELINE
        )
        is_flaky = rng.random() < flaky_chance
        if is_flaky:
            fail_ratio = rng.uniform(*FLAKY_FAIL_RATIO_RANGE)
            fail_count = min(max(1, round(total * fail_ratio)), max(1, total - 1))
        else:
            fail_count = 0
        pass_count = total - fail_count
        flaky = fail_count > 0 and 0.20 <= (fail_count / total) <= 0.30
        counts[test_type] = (total, pass_count, fail_count, flaky)
    return counts


def generate_test_logs(rng: random.Random, features: List[IssueRow]) -> List[TestLogRow]:
    rows: List[TestLogRow] = []
    for feature in features:
        if feature.type != "Story":
            continue

        sprint = sprint_for_date(feature.created.date())
        in_cluster_window = 3 <= week_for_date(feature.created.date()) <= 5

        present_types = [t for t in TEST_TYPES if t == "Manual" or rng.random() < PRESENCE_PROB[t]]
        type_counts = _generate_type_counts(rng, present_types, in_cluster_window)

        automated_total = sum(c[0] for t, c in type_counts.items() if t != "Manual")
        grand_total = sum(c[0] for c in type_counts.values())
        automation_pct = round((automated_total / grand_total) * 100, 2) if grand_total else 0.0

        span_days = max(1, int(feature.cycle_time_days or 3))
        executed_date = feature.created + timedelta(days=rng.randint(0, span_days))

        for test_type, (total, pass_count, fail_count, flaky) in type_counts.items():
            rows.append(
                TestLogRow(
                    issue_key=feature.issue_key,
                    sprint=sprint,
                    test_type=test_type,
                    test_count=total,
                    pass_count=pass_count,
                    fail_count=fail_count,
                    flaky=flaky,
                    automation_coverage_pct=automation_pct,
                    executed_date=executed_date,
                )
            )
    return rows


TEST_LOG_COLUMNS = [
    "Issue Key", "Sprint", "Test Type", "Test Count", "Pass Count", "Fail Count",
    "Flaky", "Automation Coverage %", "Executed Date",
]


def log_row_to_csv_dict(row: TestLogRow) -> Dict[str, str]:
    return {
        "Issue Key": row.issue_key,
        "Sprint": str(row.sprint),
        "Test Type": row.test_type,
        "Test Count": str(row.test_count),
        "Pass Count": str(row.pass_count),
        "Fail Count": str(row.fail_count),
        "Flaky": "true" if row.flaky else "false",
        "Automation Coverage %": f"{row.automation_coverage_pct:.2f}",
        "Executed Date": row.executed_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
