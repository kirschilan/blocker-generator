"""Automated checks per TESTER.md §Automated checks.

Covers: schema, referential integrity, invariants, determinism,
percolation-stats correctness, and a CLI smoke test.
"""
import csv
import random
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from src.generate_blocker_data import (
    CATEGORY_EXTERNAL,
    CATEGORY_INTER,
    CATEGORY_INTRA,
    Issue,
    Team,
    UnionFind,
    build_arg_parser,
    build_blockers,
    build_issues,
    build_teams,
    compute_percolation_stats,
    derive_category,
    generate_dataset,
    write_blockers_csv,
    write_issues_csv,
    write_teams_csv,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "src" / "generate_blocker_data.py"


def make_dataset(**overrides):
    args = build_arg_parser().parse_args([])
    for key, value in overrides.items():
        setattr(args, key, value)
    return generate_dataset(args)


# --- Schema -----------------------------------------------------------------

def test_teams_have_valid_type():
    teams, *_ = make_dataset()
    assert teams, "expected at least one team"
    for team in teams:
        assert team.type in ("Internal", "External")
        assert isinstance(team.capacity_points, int)
        assert 20 <= team.capacity_points <= 60


def test_issues_have_valid_enums_and_dates():
    _, issues, _, _ = make_dataset()
    assert issues
    for issue in issues:
        assert issue.issue_type in ("Epic", "Story", "Task", "Bug")
        assert issue.status in ("To Do", "In Progress", "Blocked", "In Review", "Done")
        assert issue.priority in ("Lowest", "Low", "Medium", "High", "Highest")
        created = date.fromisoformat(issue.created)
        updated = date.fromisoformat(issue.updated)
        assert created <= updated
        if issue.status == "Done":
            assert issue.resolved != ""
            resolved = date.fromisoformat(issue.resolved)
            assert updated <= resolved
        else:
            assert issue.resolved == ""


def test_blocker_links_have_valid_schema():
    _, _, blockers, _ = make_dataset(blocker_density=0.8)
    assert blockers
    for link in blockers:
        assert link.link_type == "blocks"
        assert link.category in (CATEGORY_INTRA, CATEGORY_INTER, CATEGORY_EXTERNAL)
        assert link.severity in ("Low", "Medium", "High", "Critical")
        raised = date.fromisoformat(link.raised_date)
        if link.is_active:
            assert link.resolved_date == ""
        else:
            resolved = date.fromisoformat(link.resolved_date)
            assert raised <= resolved


def test_csv_headers_match_schema(tmp_path):
    teams, issues, blockers, _ = make_dataset()

    teams_path = tmp_path / "teams.csv"
    issues_path = tmp_path / "issues.csv"
    blockers_path = tmp_path / "blockers.csv"
    write_teams_csv(teams, teams_path)
    write_issues_csv(issues, issues_path)
    write_blockers_csv(blockers, blockers_path)

    with teams_path.open() as f:
        assert next(csv.reader(f)) == ["team_id", "name", "type", "capacity_points"]
    with issues_path.open() as f:
        assert next(csv.reader(f)) == [
            "issue_key", "team_id", "issue_type", "status", "priority", "summary",
            "story_points", "created", "updated", "resolved", "sprint",
        ]
    with blockers_path.open() as f:
        assert next(csv.reader(f)) == [
            "link_id", "blocking_issue", "blocked_issue", "link_type", "category",
            "severity", "raised_date", "resolved_date", "is_active",
        ]


# --- Referential integrity ---------------------------------------------------

def test_every_issue_references_existing_team():
    teams, issues, _, _ = make_dataset()
    team_ids = {t.team_id for t in teams}
    for issue in issues:
        assert issue.team_id in team_ids


def test_every_blocker_references_existing_issues():
    _, issues, blockers, _ = make_dataset(blocker_density=0.8)
    issue_keys = {i.issue_key for i in issues}
    assert blockers
    for link in blockers:
        assert link.blocking_issue in issue_keys
        assert link.blocked_issue in issue_keys


# --- Invariants ---------------------------------------------------------------

def test_no_self_blocking():
    _, _, blockers, _ = make_dataset(blocker_density=1.0)
    for link in blockers:
        assert link.blocking_issue != link.blocked_issue


def test_no_duplicate_ordered_pairs():
    _, _, blockers, _ = make_dataset(blocker_density=1.0)
    pairs = [(b.blocking_issue, b.blocked_issue) for b in blockers]
    assert len(pairs) == len(set(pairs))


def test_category_is_correctly_derived_not_arbitrary():
    teams, issues, blockers, _ = make_dataset(blocker_density=1.0, external_bias=0.5)
    teams_by_id = {t.team_id: t for t in teams}
    issues_by_key = {i.issue_key: i for i in issues}
    assert blockers
    for link in blockers:
        blocking_team = teams_by_id[issues_by_key[link.blocking_issue].team_id]
        blocked_team = teams_by_id[issues_by_key[link.blocked_issue].team_id]
        assert link.category == derive_category(blocking_team, blocked_team)


def test_derive_category_rules_directly():
    internal_a = Team("T01", "Atlas", "Internal", 30)
    internal_b = Team("T02", "Nimbus", "Internal", 30)
    external = Team("T03", "Vendor-X", "External", 30)

    assert derive_category(internal_a, internal_a) == CATEGORY_INTRA
    assert derive_category(internal_a, internal_b) == CATEGORY_INTER
    assert derive_category(internal_a, external) == CATEGORY_EXTERNAL
    assert derive_category(external, internal_b) == CATEGORY_EXTERNAL


# --- Determinism ----------------------------------------------------------

def test_same_seed_produces_identical_datasets():
    a = make_dataset(seed=7)
    b = make_dataset(seed=7)
    assert a[0] == b[0]  # teams
    assert a[1] == b[1]  # issues
    assert a[2] == b[2]  # blockers


def test_different_seed_produces_different_dataset():
    a = make_dataset(seed=1)
    b = make_dataset(seed=2)
    assert a[1] != b[1] or a[2] != b[2]


def test_same_seed_produces_byte_identical_csvs(tmp_path):
    def run(out_dir):
        teams, issues, blockers, _ = make_dataset(seed=99)
        write_teams_csv(teams, out_dir / "teams.csv")
        write_issues_csv(issues, out_dir / "issues.csv")
        write_blockers_csv(blockers, out_dir / "blockers.csv")

    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    run(dir_a)
    run(dir_b)

    for name in ("teams.csv", "issues.csv", "blockers.csv"):
        assert (dir_a / name).read_bytes() == (dir_b / name).read_bytes()


# --- Percolation stats ------------------------------------------------------

def test_union_find_basic_components():
    uf = UnionFind(["a", "b", "c", "d"])
    uf.union("a", "b")
    uf.union("b", "c")
    roots = {uf.find(x) for x in ["a", "b", "c", "d"]}
    assert len({uf.find("a"), uf.find("b"), uf.find("c")}) == 1
    assert uf.find("d") != uf.find("a")
    assert len(roots) == 2


def test_percolation_stats_on_hand_built_graph():
    from src.generate_blocker_data import BlockerLink

    issues = [
        Issue("A-1", "T01", "Task", "To Do", "Medium", "s", 1, "2026-01-01", "2026-01-01", "", "Sprint 1"),
        Issue("A-2", "T01", "Task", "To Do", "Medium", "s", 1, "2026-01-01", "2026-01-01", "", "Sprint 1"),
        Issue("A-3", "T01", "Task", "To Do", "Medium", "s", 1, "2026-01-01", "2026-01-01", "", "Sprint 1"),
        Issue("A-4", "T01", "Task", "To Do", "Medium", "s", 1, "2026-01-01", "2026-01-01", "", "Sprint 1"),
    ]
    # A-1 <-> A-2 connected; A-3, A-4 isolated singletons.
    blockers = [
        BlockerLink("BLK-1", "A-1", "A-2", "blocks", CATEGORY_INTRA, "Low", "2026-01-01", "", True),
    ]
    stats = compute_percolation_stats(issues, blockers)
    assert stats["total_issues"] == 4
    assert stats["total_blockers"] == 1
    assert stats["component_count"] == 3
    assert stats["largest_component_size"] == 2
    assert stats["largest_component_fraction"] == pytest.approx(0.5)
    assert stats["component_sizes"] == [2, 1, 1]


def test_zero_blocker_density_yields_no_blockers_and_singleton_components():
    _, issues, blockers, stats = make_dataset(blocker_density=0.0)
    assert blockers == []
    assert stats["total_blockers"] == 0
    assert stats["component_count"] == len(issues)
    assert stats["largest_component_size"] == 1


def test_higher_density_does_not_decrease_largest_component_fraction():
    rng_seed = 123
    _, _, _, low_stats = make_dataset(seed=rng_seed, blocker_density=0.1)
    _, _, _, high_stats = make_dataset(seed=rng_seed, blocker_density=0.9)
    assert high_stats["largest_component_fraction"] >= low_stats["largest_component_fraction"]


# --- Direct builder tests (Task 1.1 / 1.2) ----------------------------------

def test_build_teams_ids_unique_and_sized():
    rng = random.Random(1)
    teams = build_teams(rng, num_internal=5, num_external=3)
    assert len(teams) == 8
    assert len({t.team_id for t in teams}) == 8
    assert sum(1 for t in teams if t.type == "Internal") == 5
    assert sum(1 for t in teams if t.type == "External") == 3


def test_build_issues_count_and_unique_keys():
    rng = random.Random(1)
    teams = build_teams(rng, num_internal=3, num_external=1)
    issues = build_issues(rng, teams, issues_per_team=10, sprint_name="Sprint 1")
    assert len(issues) == 40
    assert len({i.issue_key for i in issues}) == 40


def test_build_teams_beyond_name_list_length_still_unique():
    rng = random.Random(1)
    teams = build_teams(rng, num_internal=12, num_external=6)
    assert len(teams) == 18
    assert len({t.name for t in teams}) == 18
    assert len({t.team_id for t in teams}) == 18


# --- CLI smoke test ----------------------------------------------------------

def test_cli_generates_expected_files_and_row_counts(tmp_path):
    out_dir = tmp_path / "data"
    report_dir = tmp_path / "docs"
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--num-internal-teams", "2",
            "--num-external-teams", "1",
            "--issues-per-team", "5",
            "--seed", "5",
            "--output-dir", str(out_dir),
            "--report-dir", str(report_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0

    teams_csv = out_dir / "teams.csv"
    issues_csv = out_dir / "issues.csv"
    blockers_csv = out_dir / "blockers.csv"
    report_md = report_dir / "validation_report.md"

    for path in (teams_csv, issues_csv, blockers_csv, report_md):
        assert path.exists() and path.stat().st_size > 0

    with teams_csv.open() as f:
        assert len(list(csv.DictReader(f))) == 3  # 2 internal + 1 external
    with issues_csv.open() as f:
        assert len(list(csv.DictReader(f))) == 15  # 3 teams * 5 issues

    assert "Percolation statistics" in report_md.read_text()
