"""Automated checks for BACKLOG.md Task 1.5 + TESTER.md Sprint 1 checks
that apply to `v1_auth_cluster_test_logs.csv`.
"""
import random
from datetime import datetime

import pytest

from blocker_generator.clusters import CLUSTER_1_AUTH
from blocker_generator.features import generate_dataset
from blocker_generator.squads import build_auth_subgraph
from blocker_generator.sprints import week_for_date
from blocker_generator.xray_logs import (
    TEST_TYPES,
    generate_test_logs,
    log_row_to_csv_dict,
)

VALID_TEST_TYPES = {"Manual", "Selenium", "Postman", "Swagger", "Perfecto Mobile"}


@pytest.fixture(scope="module")
def features():
    rows = generate_dataset(seed=42, squads=build_auth_subgraph(), cluster=CLUSTER_1_AUTH)
    return [r for r in rows if r.type == "Story"]


@pytest.fixture(scope="module")
def logs(features):
    return generate_test_logs(random.Random(4242), features)


# --- Format / row counts -----------------------------------------------------

def test_row_count_in_range(logs):
    assert 1200 <= len(logs) <= 1500


def test_no_duplicate_issue_sprint_type_tuples(logs):
    tuples = [(r.issue_key, r.sprint, r.test_type) for r in logs]
    assert len(tuples) == len(set(tuples))


def test_all_issue_keys_reference_real_features(logs, features):
    feature_keys = {f.issue_key for f in features}
    assert all(r.issue_key in feature_keys for r in logs)


def test_every_feature_has_at_least_one_log_row(logs, features):
    logged_keys = {r.issue_key for r in logs}
    assert logged_keys == {f.issue_key for f in features}


def test_every_feature_has_a_manual_row(logs, features):
    manual_keys = {r.issue_key for r in logs if r.test_type == "Manual"}
    assert manual_keys == {f.issue_key for f in features}


# --- Data integrity -----------------------------------------------------------

def test_sprint_values_in_range(logs):
    assert all(1 <= r.sprint <= 12 for r in logs)


def test_test_type_values_valid(logs):
    assert all(r.test_type in VALID_TEST_TYPES for r in logs)


def test_test_count_covers_pass_and_fail(logs):
    for r in logs:
        assert r.test_count >= r.pass_count + r.fail_count


def test_flaky_iff_fail_ratio_20_to_30_pct(logs):
    for r in logs:
        ratio = r.fail_count / r.test_count if r.test_count else 0
        expected_flaky = r.fail_count > 0 and 0.20 <= ratio <= 0.30
        assert r.flaky == expected_flaky


def test_automation_coverage_in_0_100(logs):
    assert all(0 <= r.automation_coverage_pct <= 100 for r in logs)


def test_no_feature_at_100_percent_automation(logs):
    by_feature = {r.issue_key: r.automation_coverage_pct for r in logs}
    assert all(pct < 100 for pct in by_feature.values())


def test_executed_dates_valid_iso8601(logs):
    for r in logs:
        csv_row = log_row_to_csv_dict(r)
        datetime.strptime(csv_row["Executed Date"], "%Y-%m-%dT%H:%M:%SZ")


# --- Automation coverage distribution (TESTER.md) ----------------------------

def test_average_automation_coverage_40_to_60_pct(logs):
    by_feature = {}
    for r in logs:
        by_feature[r.issue_key] = r.automation_coverage_pct
    avg = sum(by_feature.values()) / len(by_feature)
    assert 40 <= avg <= 60


def test_all_features_have_manual(logs, features):
    manual_keys = {r.issue_key for r in logs if r.test_type == "Manual"}
    assert len(manual_keys) == len(features)


def test_test_type_presence_distribution_reasonable(logs, features):
    n = len(features)
    presence = {t: len({r.issue_key for r in logs if r.test_type == t}) / n for t in TEST_TYPES}
    assert presence["Manual"] == 1.0
    assert 0.35 <= presence["Selenium"] <= 0.70
    assert 0.05 <= presence["Postman"] <= 0.25
    assert 0.05 <= presence["Perfecto Mobile"] <= 0.25
    assert 0.02 <= presence["Swagger"] <= 0.20


# --- Flaky test correlation (TESTER.md) --------------------------------------

def test_flaky_rate_elevated_in_cluster_window(logs, features):
    features_by_key = {f.issue_key: f for f in features}

    def in_window(row):
        return 3 <= week_for_date(features_by_key[row.issue_key].created.date()) <= 5

    in_window_logs = [r for r in logs if in_window(r)]
    out_window_logs = [r for r in logs if not in_window(r)]

    in_rate = sum(1 for r in in_window_logs if r.flaky) / len(in_window_logs)
    out_rate = sum(1 for r in out_window_logs if r.flaky) / len(out_window_logs)

    assert 0.15 <= in_rate <= 0.20, f"in-window flaky rate {in_rate:.2%} not in 15-20%"
    assert out_rate < in_rate


def test_flaky_tests_concentrated_in_selenium_and_perfecto(logs, features):
    features_by_key = {f.issue_key: f for f in features}
    in_window_flaky = [
        r for r in logs
        if r.flaky and 3 <= week_for_date(features_by_key[r.issue_key].created.date()) <= 5
    ]
    assert in_window_flaky
    automation_heavy = sum(1 for r in in_window_flaky if r.test_type in ("Selenium", "Perfecto Mobile"))
    assert automation_heavy / len(in_window_flaky) >= 0.7
