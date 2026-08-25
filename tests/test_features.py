"""Automated checks for BACKLOG.md Task 1.4 + TESTER.md Sprint 1 checks
that apply to `v1_auth_cluster_high_density.csv`.

See features.py's module docstring for the reconciled spec (PM ruling,
GitHub Issue #2, 2026-08-22): 12 core columns, 7-11 blocker rows,
week-3-scoped 20-30% density.
"""
import csv
import io
import re
from datetime import datetime

import pytest

from blocker_generator.clusters import CLUSTER_1_AUTH
from blocker_generator.csv_io import write_jira_csv
from blocker_generator.features import (
    CORE_COLUMNS,
    generate_dataset,
    max_label_span,
    max_sprint_span,
)
from blocker_generator.squads import AUTH, CHECKOUT, PAYMENTS, build_auth_subgraph

ISSUE_KEY_RE = re.compile(r"^SQ-[ABD]-[0-9]+$")
SPRINT_NAME_RE = re.compile(r"^Sprint-([1-9]|1[0-2])$")


@pytest.fixture(scope="module")
def dataset():
    return generate_dataset(seed=42, squads=build_auth_subgraph(), clusters=[CLUSTER_1_AUTH])


@pytest.fixture(scope="module")
def csv_table(dataset, tmp_path_factory):
    """Writes the real CSV and reads it back positionally (csv.reader, not
    DictReader) -- a real Jira export repeats the 'Sprint' header once per
    occupied slot (Issue #7), which a dict-keyed row can't represent."""
    path = tmp_path_factory.mktemp("csv") / "out.csv"
    write_jira_csv(dataset, path)
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


@pytest.fixture(scope="module")
def csv_rows(csv_table):
    """Core (non-Sprint) fields only, as dicts -- safe since CORE_COLUMNS
    has no duplicates."""
    header, data_rows = csv_table
    core_len = len(CORE_COLUMNS)
    return [dict(zip(CORE_COLUMNS, row[:core_len])) for row in data_rows]


@pytest.fixture(scope="module")
def label_slot_values(csv_table, dataset):
    header, data_rows = csv_table
    core_len = len(CORE_COLUMNS)
    label_slots = max_label_span(dataset)
    return [row[core_len:core_len + label_slots] for row in data_rows]


@pytest.fixture(scope="module")
def sprint_slot_values(csv_table, dataset):
    header, data_rows = csv_table
    core_len = len(CORE_COLUMNS)
    label_slots = max_label_span(dataset)
    return [row[core_len + label_slots:] for row in data_rows]


# --- Row counts (BACKLOG.md Task 1.4 / TESTER.md) ---------------------------

def test_feature_row_count_in_range(dataset):
    features = [r for r in dataset if r.type == "Story"]
    assert 540 <= len(features) <= 720


def test_total_row_count_in_reconciled_range(dataset):
    # TESTER.md (updated 2026-08-22): 547-731 total (540-720 features +
    # 7-11 blockers).
    blockers = [r for r in dataset if r.type == "Sub-task"]
    assert 7 <= len(blockers) <= 11
    assert 547 <= len(dataset) <= 731


def test_window_scoped_blocker_density_week_3(dataset):
    # TESTER.md (updated 2026-08-22): density scoped to week 3 specifically
    # (where all Cluster-1-Auth activity concentrates), not the full
    # "weeks 3-5" span, which dilutes density to ~11%.
    from blocker_generator.sprints import week_for_date

    in_week3 = [r for r in dataset if week_for_date(r.created.date()) == 3]
    features_w3 = [r for r in in_week3 if r.type == "Story"]
    blockers_w3 = [r for r in in_week3 if r.type == "Sub-task"]
    assert features_w3
    density = len(blockers_w3) / len(features_w3) * 100
    assert 20 <= density <= 30, f"week-3 density {density:.1f}% not in 20-30%"


def test_global_blocker_density_is_small(dataset):
    # ~1-2% globally is expected and correct for a single-cluster MVP;
    # full percolation density is Sprint 3's scope.
    features = [r for r in dataset if r.type == "Story"]
    blockers = [r for r in dataset if r.type == "Sub-task"]
    density = len(blockers) / len(features) * 100
    assert density < 5


def test_issue_keys_match_pattern(dataset):
    for row in dataset:
        assert ISSUE_KEY_RE.match(row.issue_key), row.issue_key


def test_no_duplicate_issue_keys(dataset):
    keys = [r.issue_key for r in dataset]
    assert len(keys) == len(set(keys))


# --- Cascade validation (TESTER.md) -----------------------------------------

def test_auth_blocker_count_in_week_3():
    blockers = [r for r in generate_dataset(42, build_auth_subgraph(), [CLUSTER_1_AUTH]) if r.type == "Sub-task"]
    auth_blockers = [r for r in blockers if r.assignee == "auth-squad"]
    assert 3 <= len(auth_blockers) <= 5


def test_checkout_and_payments_blocker_counts():
    blockers = [r for r in generate_dataset(42, build_auth_subgraph(), [CLUSTER_1_AUTH]) if r.type == "Sub-task"]
    for assignee in ("checkout-squad", "payments-squad"):
        count = len([r for r in blockers if r.assignee == assignee])
        assert 2 <= count <= 3


def test_all_blockers_reference_login_or_auth(dataset):
    blockers = [r for r in dataset if r.type == "Sub-task"]
    assert blockers
    for row in blockers:
        assert "Login service" in row.waiting_reason or "Auth" in row.waiting_reason


def test_no_blockers_outside_weeks_3_to_5(dataset):
    from blocker_generator.sprints import week_for_date

    blockers = [r for r in dataset if r.type == "Sub-task"]
    for row in blockers:
        week = week_for_date(row.created.date())
        assert 3 <= week <= 5


# --- Data integrity (TESTER.md) ---------------------------------------------

def test_blocker_rows_keep_reason_regardless_of_status(dataset):
    """PM ruling 2026-08-23: Waiting Reason persists on blocker rows (Type =
    Sub-task) whether Done or still Waiting (PBI 2.1's cascade-tail rows),
    so the cluster signal is retrospectively detectable either way; feature
    rows (Type = Story) never have one."""
    for row in dataset:
        if row.type == "Sub-task":
            assert row.waiting_reason != ""
            assert row.status in ("Done", "Waiting")
            if row.status == "Done":
                assert row.resolved is not None
                assert row.cycle_time_days is not None
            else:
                assert row.resolved is None
                assert row.cycle_time_days is None
        elif row.type == "Story":
            assert row.waiting_reason == ""
            assert row.status in ("Done", "In Progress")
            if row.status == "Done":
                assert row.resolved is not None
                assert row.cycle_time_days is not None
            else:
                assert row.resolved is None
                assert row.cycle_time_days is None


def test_cluster_cascade_tail_stays_open(dataset):
    """PBI 2.1 (2026-08-24): the last day of each cascade squad's blocker
    (Checkout, Payments) stays genuinely open -- BACKLOG.md's "downstream
    blockers clear day 4" is a lag relative to the root resolving day 3;
    the report is implicitly taken at that moment, so the final clearing
    hasn't happened yet. The root (Auth) itself always fully resolves."""
    blockers = [r for r in dataset if r.type == "Sub-task"]
    by_squad: dict = {}
    for r in blockers:
        by_squad.setdefault(r.assignee, []).append(r)
    for assignee, rows in by_squad.items():
        rows.sort(key=lambda r: r.created)
        if assignee == "auth-squad":
            assert all(r.status == "Done" for r in rows)
        else:
            assert all(r.status == "Done" for r in rows[:-1])
            assert rows[-1].status == "Waiting"


def test_resolved_after_created(dataset):
    for row in dataset:
        if row.resolved is not None:
            assert row.resolved >= row.created


def test_labels_only_on_auth_cluster_blockers(dataset):
    """PBI 2.0c (2026-08-23): Cluster Tag -> Jira's native Labels field."""
    for row in dataset:
        if row.type == "Sub-task":
            assert row.labels == ["Cluster-1-Auth"]
        else:
            assert row.labels == []


def test_test_automation_values_valid(dataset):
    valid = {"Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile", None}
    for row in dataset:
        assert row.test_automation in valid


# --- CSV structure -----------------------------------------------------------
# Issue #7 (2026-08-23): real Jira CSV export repeats the literal "Sprint"
# header once per occupied multi-value slot, sized to the widest-spanning
# issue in the dataset -- not a fixed "Sprint-1".."Sprint-12".

def test_csv_header_has_core_repeated_labels_and_repeated_sprint_columns(csv_table, dataset):
    header, _ = csv_table
    core_len = len(CORE_COLUMNS)
    assert header[:core_len] == CORE_COLUMNS
    label_slots = max_label_span(dataset)
    sprint_slots = max_sprint_span(dataset)
    assert header[core_len:core_len + label_slots] == ["Labels"] * label_slots
    assert header[core_len + label_slots:] == ["Sprint"] * sprint_slots
    assert len(header) == core_len + label_slots + sprint_slots


def test_non_native_fields_labeled_as_custom_fields(csv_table):
    """PBI 2.0a (2026-08-23): real Jira CSV export labels every custom
    field column as "Custom field (<Name>)" -- Waiting Reason and Test
    Automation aren't native Jira fields, so they get that treatment.
    Native fields (Issue Key, Summary, Type, Status, Assignee, Created,
    Resolved, Sprint) keep plain names."""
    header, _ = csv_table
    assert "Custom field (Waiting Reason)" in header
    assert "Custom field (Test Automation)" in header
    assert "Waiting Reason" not in header
    assert "Test Automation" not in header
    for native in ("Issue Key", "Summary", "Type", "Status", "Assignee", "Created", "Resolved"):
        assert native in header


def test_csv_round_trips_through_csv_module(csv_table, dataset):
    header, data_rows = csv_table
    assert len(data_rows) == len(dataset)
    assert all(len(row) == len(header) for row in data_rows)


def test_created_dates_are_valid_iso8601(csv_rows):
    for row in csv_rows:
        datetime.strptime(row["Created"], "%Y-%m-%dT%H:%M:%SZ")


def test_sprint_slots_populated_1_to_3_times(sprint_slot_values):
    for slots in sprint_slot_values:
        populated = [v for v in slots if v]
        assert 1 <= len(populated) <= 3


def test_sprint_slot_values_are_sprint_names_not_dates(sprint_slot_values):
    for slots in sprint_slot_values:
        for v in slots:
            if v:
                assert SPRINT_NAME_RE.match(v), f"{v!r} is not a 'Sprint-N' name"


def test_no_utf8_or_null_byte_issues(csv_rows, sprint_slot_values):
    for row in csv_rows:
        for value in row.values():
            assert "\x00" not in value
    for slots in sprint_slot_values:
        for v in slots:
            assert "\x00" not in v
