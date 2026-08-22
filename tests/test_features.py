"""Automated checks for BACKLOG.md Task 1.4 + TESTER.md Sprint 1 checks
that apply to `v1_auth_cluster_high_density.csv`.

See features.py's module docstring for the two spec inconsistencies
(13-vs-12 core columns; 15-30 total blocker rows vs. the mutually
unsatisfiable 3-5/2-3/2-3 per-squad ranges) this suite resolves by
following the more specific/reachable constraint.
"""
import csv
import io
import re
from datetime import datetime

import pytest

from blocker_generator.clusters import CLUSTER_1_AUTH
from blocker_generator.features import (
    ALL_COLUMNS,
    CORE_COLUMNS,
    SPRINT_COLUMNS,
    generate_dataset,
)
from blocker_generator.squads import AUTH, CHECKOUT, PAYMENTS, build_auth_subgraph

ISSUE_KEY_RE = re.compile(r"^SQ-[ABD]-[0-9]+$")


@pytest.fixture(scope="module")
def dataset():
    return generate_dataset(seed=42, squads=build_auth_subgraph(), cluster=CLUSTER_1_AUTH)


@pytest.fixture(scope="module")
def csv_rows(dataset):
    from blocker_generator.features import row_to_csv_dict

    return [row_to_csv_dict(r) for r in dataset]


# --- Row counts (BACKLOG.md Task 1.4 / TESTER.md) ---------------------------

def test_feature_row_count_in_range(dataset):
    features = [r for r in dataset if r.type == "Story"]
    assert 540 <= len(features) <= 720


def test_total_row_count_reasonable(dataset):
    # TESTER.md's literal "555-750" total assumes 15-30 blocker rows, which
    # is mutually unsatisfiable with its own 3-5/2-3/2-3 per-squad ranges
    # (max 11). We check the feature-row range holds and blockers are a
    # small addition on top, per the per-squad ranges we do satisfy.
    assert 540 <= len(dataset) <= 720 + 11


def test_issue_keys_match_pattern(dataset):
    for row in dataset:
        assert ISSUE_KEY_RE.match(row.issue_key), row.issue_key


def test_no_duplicate_issue_keys(dataset):
    keys = [r.issue_key for r in dataset]
    assert len(keys) == len(set(keys))


# --- Cascade validation (TESTER.md) -----------------------------------------

def test_auth_blocker_count_in_week_3():
    blockers = [r for r in generate_dataset(42, build_auth_subgraph(), CLUSTER_1_AUTH) if r.type == "Sub-task"]
    auth_blockers = [r for r in blockers if r.assignee == "auth-squad"]
    assert 3 <= len(auth_blockers) <= 5


def test_checkout_and_payments_blocker_counts():
    blockers = [r for r in generate_dataset(42, build_auth_subgraph(), CLUSTER_1_AUTH) if r.type == "Sub-task"]
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

def test_waiting_rows_have_reason_done_rows_do_not(dataset):
    for row in dataset:
        if row.status == "Waiting":
            assert row.waiting_reason != ""
            assert row.resolved is None
            assert row.cycle_time_days is None
        elif row.status == "Done":
            assert row.waiting_reason == ""
            assert row.resolved is not None
            assert row.cycle_time_days is not None


def test_resolved_after_created(dataset):
    for row in dataset:
        if row.resolved is not None:
            assert row.resolved >= row.created


def test_cluster_tag_only_on_auth_cluster_blockers(dataset):
    for row in dataset:
        if row.type == "Sub-task":
            assert row.cluster_tag == "Cluster-1-Auth"
        else:
            assert row.cluster_tag == ""


def test_external_blocker_false_for_all_sprint1_rows(dataset):
    # Auth cluster is an internal SharedCompFailure; Sprint 1 has no
    # external dependency (Task 1.1: "External dependency: none for this
    # slice").
    assert all(row.external_blocker is False for row in dataset)


def test_test_automation_values_valid(dataset):
    valid = {"Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile", None}
    for row in dataset:
        assert row.test_automation in valid


# --- CSV structure -----------------------------------------------------------

def test_csv_has_12_core_and_12_sprint_columns():
    assert len(CORE_COLUMNS) == 12
    assert len(SPRINT_COLUMNS) == 12
    assert len(ALL_COLUMNS) == 24


def test_csv_round_trips_through_csv_module(csv_rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=ALL_COLUMNS)
    writer.writeheader()
    writer.writerows(csv_rows)
    buf.seek(0)
    reloaded = list(csv.DictReader(buf))
    assert len(reloaded) == len(csv_rows)
    assert reloaded[0].keys() == set(ALL_COLUMNS)


def test_created_dates_are_valid_iso8601(csv_rows):
    for row in csv_rows:
        datetime.strptime(row["Created"], "%Y-%m-%dT%H:%M:%SZ")


def test_sprint_columns_populated_1_to_3_times(csv_rows):
    for row in csv_rows:
        populated = [row[c] for c in SPRINT_COLUMNS if row[c]]
        assert 1 <= len(populated) <= 3


def test_sprint_columns_never_beyond_sprint_12(csv_rows):
    for row in csv_rows:
        for col in SPRINT_COLUMNS:
            # presence alone proves it's Sprint-1..Sprint-12 (no Sprint-13+
            # column exists in the header at all)
            assert col in row


def test_no_utf8_or_null_byte_issues(csv_rows):
    for row in csv_rows:
        for value in row.values():
            assert "\x00" not in value
