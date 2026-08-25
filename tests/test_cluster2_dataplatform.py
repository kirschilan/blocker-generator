"""Automated checks for BACKLOG.md Task 2.2 (inject DataPlatform cluster
alongside Auth, on the 5-squad model from Task 2.1).

Tests the *resulting CSV file* (round-tripped through write_jira_csv and
read back with csv.reader), not just the in-memory dataset -- per PO's
explicit ask (2026-08-25) after Task 2.1 shipped with no data artifact:
"test the resulting CSV files meet the criteria."

Scope note: this generates a real, CSV-verified dataset combining the
5-squad model (Task 2.1) with both clusters (Task 2.2's own acceptance
criteria: "DataPlatform cluster ... affects Core Banking (root) + Savings
(cascade)", "Inject alongside Auth cluster", "No overlap"). It does NOT
attempt Task 2.3's full acceptance criteria (tuned 25-35% combined
density, the official `v2_two_clusters_high_density.csv` row-count
range, the optimized/mocked variant, test logs, or the validation
report) -- those remain Task 2.3-2.6's scope, not pulled into today's
Iteration.
"""
import csv

import pytest

from blocker_generator.clusters import CLUSTER_1_AUTH, CLUSTER_2_DATAPLATFORM
from blocker_generator.csv_io import write_jira_csv
from blocker_generator.features import CORE_COLUMNS, generate_dataset, max_label_span
from blocker_generator.squads import build_five_squad_subgraph
from blocker_generator.sprints import week_for_date


@pytest.fixture(scope="module")
def dataset():
    return generate_dataset(
        seed=42,
        squads=build_five_squad_subgraph(),
        clusters=[CLUSTER_1_AUTH, CLUSTER_2_DATAPLATFORM],
    )


@pytest.fixture(scope="module")
def csv_table(dataset, tmp_path_factory):
    path = tmp_path_factory.mktemp("csv") / "task_2.2.csv"
    write_jira_csv(dataset, path)
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


@pytest.fixture(scope="module")
def csv_rows_with_labels(csv_table, dataset):
    """Core fields + all Labels slots, as dicts with a combined 'labels'
    list -- Labels is a repeated column (PBI 2.0c), so it can't be a
    single dict key."""
    header, data_rows = csv_table
    core_len = len(CORE_COLUMNS)
    label_slots = max_label_span(dataset)
    out = []
    for row in data_rows:
        core = dict(zip(CORE_COLUMNS, row[:core_len]))
        core["labels"] = [v for v in row[core_len:core_len + label_slots] if v]
        out.append(core)
    return out


# --- Task 2.2 acceptance criteria, verified against the written CSV --------


def test_both_cluster_labels_present_in_csv(csv_rows_with_labels):
    all_labels = {label for row in csv_rows_with_labels for label in row["labels"]}
    assert "Cluster-1-Auth" in all_labels
    assert "Cluster-2-DataPlatform" in all_labels


def test_dataplatform_root_is_core_banking_in_week_6(csv_rows_with_labels):
    root_rows = [
        r for r in csv_rows_with_labels
        if "Cluster-2-DataPlatform" in r["labels"] and r["Assignee"] == "core-banking-squad"
    ]
    assert 3 <= len(root_rows) <= 6, "expect ~4-5 Core Banking blockers (ARCHITECTURE.md Cluster 2)"
    for row in root_rows:
        created = _parse_iso(row["Created"])
        assert week_for_date(created.date()) == 6, row


def test_dataplatform_cascade_is_savings_only(csv_rows_with_labels):
    cascade_rows = [
        r for r in csv_rows_with_labels
        if "Cluster-2-DataPlatform" in r["labels"] and r["Assignee"] != "core-banking-squad"
    ]
    assert cascade_rows
    assert {r["Assignee"] for r in cascade_rows} == {"savings-squad"}
    for row in cascade_rows:
        assert "Core Banking" in row["Custom field (Waiting Reason)"]


def test_dataplatform_cascade_lags_root_by_one_day(csv_rows_with_labels):
    root_dates = sorted(
        _parse_iso(r["Created"]) for r in csv_rows_with_labels
        if "Cluster-2-DataPlatform" in r["labels"] and r["Assignee"] == "core-banking-squad"
    )
    cascade_dates = sorted(
        _parse_iso(r["Created"]) for r in csv_rows_with_labels
        if "Cluster-2-DataPlatform" in r["labels"] and r["Assignee"] == "savings-squad"
    )
    assert cascade_dates[0].date() == root_dates[0].date() + __import__("datetime").timedelta(days=1)


def test_no_overlap_between_auth_and_dataplatform_windows(csv_rows_with_labels):
    """BACKLOG.md Task 2.2: "No overlap (Auth weeks 3-5, DataPlatform weeks 6-10)"."""
    auth_weeks = {
        week_for_date(_parse_iso(r["Created"]).date())
        for r in csv_rows_with_labels if "Cluster-1-Auth" in r["labels"]
    }
    dataplatform_weeks = {
        week_for_date(_parse_iso(r["Created"]).date())
        for r in csv_rows_with_labels if "Cluster-2-DataPlatform" in r["labels"]
    }
    assert auth_weeks, dataplatform_weeks
    assert auth_weeks.isdisjoint(dataplatform_weeks), (auth_weeks, dataplatform_weeks)


def test_auth_cluster_unchanged_by_dataplatform_addition(csv_rows_with_labels):
    """Task 2.2: "Inject alongside Auth cluster" -- Auth's own blocker
    counts (BACKLOG.md Task 1.4 acceptance) shouldn't shift just because
    a second cluster was added to the same dataset."""
    auth_blockers = [r for r in csv_rows_with_labels if "Cluster-1-Auth" in r["labels"]]
    auth_root = [r for r in auth_blockers if r["Assignee"] == "auth-squad"]
    assert 3 <= len(auth_root) <= 5


def test_no_duplicate_issue_keys_across_both_clusters(csv_rows_with_labels):
    keys = [r["Issue Key"] for r in csv_rows_with_labels]
    assert len(keys) == len(set(keys))


def test_dataplatform_rows_do_not_mention_auth_in_csv(csv_rows_with_labels):
    # Regression: this exact bug (Cluster 1's "Auth service" summary text
    # hardcoded and reused for Cluster 2) was caught by eyeballing this
    # CSV's actual rows, not by any prior test -- see test_clusters.py's
    # matching regression test for the in-memory-level check.
    dataplatform_rows = [r for r in csv_rows_with_labels if "Cluster-2-DataPlatform" in r["labels"]]
    assert dataplatform_rows
    for row in dataplatform_rows:
        assert "Auth" not in row["Summary"], row
        assert "Auth" not in row["Custom field (Waiting Reason)"], row


def test_no_conflicts_same_squad_same_day(dataset):
    """BACKLOG.md Task 2.2's own test line: "no conflicts" -- no squad has
    two blocker rows active from different clusters on the same day."""
    blockers = [r for r in dataset if r.type == "Sub-task"]
    seen = set()
    for row in blockers:
        key = (row.assignee, row.created.date())
        assert key not in seen, f"conflict: {row.assignee} has 2 blockers on {row.created.date()}"
        seen.add(key)


def _parse_iso(value: str):
    from datetime import datetime

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
