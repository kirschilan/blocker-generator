"""Automated checks for BACKLOG.md Task 1.3 (Auth cluster injection)."""
from datetime import timedelta

from blocker_generator.clusters import CLUSTER_1_AUTH, inject_cluster
from blocker_generator.squads import AUTH, CHECKOUT, PAYMENTS
from blocker_generator.sprints import week_day_to_date


def test_auth_has_three_blockers_in_week_3():
    entries = inject_cluster(CLUSTER_1_AUTH)
    auth_entries = [e for e in entries if e.squad_id == AUTH]
    assert len(auth_entries) == 3
    week3_start = week_day_to_date(3, 1)
    week3_end = week_day_to_date(3, 7)
    assert all(week3_start <= e.date <= week3_end for e in auth_entries)


def test_auth_active_days_1_through_3():
    entries = inject_cluster(CLUSTER_1_AUTH)
    auth_dates = sorted(e.date for e in entries if e.squad_id == AUTH)
    day1 = week_day_to_date(3, 1)
    assert auth_dates == [day1, day1 + timedelta(days=1), day1 + timedelta(days=2)]


def test_cascade_squads_active_days_2_through_4_with_one_day_lag():
    entries = inject_cluster(CLUSTER_1_AUTH)
    day1 = week_day_to_date(3, 1)
    expected_dates = {day1 + timedelta(days=off) for off in (1, 2, 3)}
    for squad in (CHECKOUT, PAYMENTS):
        squad_dates = {e.date for e in entries if e.squad_id == squad}
        assert squad_dates == expected_dates
        assert 2 <= len(squad_dates) <= 3


def test_cascade_blockers_created_one_day_after_root():
    entries = inject_cluster(CLUSTER_1_AUTH)
    root_min_date = min(e.date for e in entries if e.is_root)
    for squad in (CHECKOUT, PAYMENTS):
        cascade_min_date = min(e.date for e in entries if e.squad_id == squad)
        assert (cascade_min_date - root_min_date).days == 1


def test_resolution_order_root_clears_before_cascade():
    entries = inject_cluster(CLUSTER_1_AUTH)
    root_max_date = max(e.date for e in entries if e.is_root)
    for squad in (CHECKOUT, PAYMENTS):
        cascade_max_date = max(e.date for e in entries if e.squad_id == squad)
        assert cascade_max_date > root_max_date
        assert (cascade_max_date - root_max_date).days == 1  # propagation lag


def test_waiting_reasons_reference_correct_cause():
    entries = inject_cluster(CLUSTER_1_AUTH)
    for entry in entries:
        if entry.is_root:
            assert "Auth" in entry.waiting_reason or "session cache" in entry.waiting_reason.lower()
        else:
            assert "Login service" in entry.waiting_reason or "SQ-A" in entry.waiting_reason


def test_all_entries_tagged_with_cluster_id():
    entries = inject_cluster(CLUSTER_1_AUTH)
    assert all(e.cluster_id == "Cluster-1-Auth" for e in entries)


def test_no_blockers_outside_weeks_3_to_5():
    entries = inject_cluster(CLUSTER_1_AUTH)
    week3_start = week_day_to_date(3, 1)
    week5_end = week_day_to_date(5, 7)
    assert all(week3_start <= e.date <= week5_end for e in entries)
