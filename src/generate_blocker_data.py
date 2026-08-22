#!/usr/bin/env python3
"""Generate synthetic Jira issue and Xray-style blocker-link CSV exports
for a portfolio of internal teams and external vendors/partners.

Domain model and percolation design: see ARCHITECTURE.md.
Implements BACKLOG.md Sprint 1 tasks 1.1-1.6.
"""
from __future__ import annotations

import argparse
import csv
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

ISSUE_TYPES = ["Epic", "Story", "Task", "Bug"]
PRIORITIES = ["Lowest", "Low", "Medium", "High", "Highest"]
STATUSES = ["To Do", "In Progress", "Blocked", "In Review", "Done"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
STORY_POINTS = [1, 2, 3, 5, 8, 13]

INTERNAL_TEAM_NAMES = [
    "Atlas", "Nimbus", "Forge", "Vector", "Halcyon", "Pioneer", "Beacon", "Summit",
]
EXTERNAL_TEAM_NAMES = [
    "Vendor-Cygnus Logistics", "Vendor-Meridian Data", "Vendor-Origin Cloud",
    "Partner-Northwind Systems",
]

SUMMARY_VERBS = [
    "Investigate", "Implement", "Fix", "Refactor", "Document", "Migrate",
    "Optimize", "Design", "Review", "Automate",
]
SUMMARY_NOUNS = [
    "authentication flow", "billing pipeline", "data export job",
    "dashboard widget", "API gateway config", "notification service",
    "onboarding flow", "search index", "deployment pipeline", "reporting module",
]

# Fixed epoch (not wall-clock) so runs are reproducible independent of when
# the generator or its tests happen to execute.
REFERENCE_DATE = date(2026, 6, 1)

CATEGORY_INTRA = "Intra-Team"
CATEGORY_INTER = "Inter-Team"
CATEGORY_EXTERNAL = "External"


@dataclass
class Team:
    team_id: str
    name: str
    type: str  # "Internal" | "External"
    capacity_points: int


@dataclass
class Issue:
    issue_key: str
    team_id: str
    issue_type: str
    status: str
    priority: str
    summary: str
    story_points: int
    created: str
    updated: str
    resolved: str
    sprint: str


@dataclass
class BlockerLink:
    link_id: str
    blocking_issue: str
    blocked_issue: str
    link_type: str
    category: str
    severity: str
    raised_date: str
    resolved_date: str
    is_active: bool


class UnionFind:
    def __init__(self, items):
        self.parent = {item: item for item in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def _numbered_names(base_names: List[str], count: int) -> List[str]:
    names = []
    for i in range(count):
        base = base_names[i % len(base_names)]
        cycle = i // len(base_names)
        names.append(base if cycle == 0 else f"{base} {cycle + 1}")
    return names


def build_teams(rng: random.Random, num_internal: int, num_external: int) -> List[Team]:
    teams: List[Team] = []
    team_id_counter = 1
    for name in _numbered_names(INTERNAL_TEAM_NAMES, num_internal):
        teams.append(Team(f"T{team_id_counter:02d}", name, "Internal", rng.randint(20, 60)))
        team_id_counter += 1
    for name in _numbered_names(EXTERNAL_TEAM_NAMES, num_external):
        teams.append(Team(f"T{team_id_counter:02d}", name, "External", rng.randint(20, 60)))
        team_id_counter += 1
    return teams


def assign_issue_prefixes(teams: List[Team]) -> Dict[str, str]:
    used = set()
    prefixes: Dict[str, str] = {}
    for team in teams:
        words = [w for w in re.split(r"[\s-]+", team.name) if w]
        base = "".join(w[0] for w in words).upper()[:4] if len(words) > 1 else team.name[:3].upper()
        base = base or "TEA"
        candidate = base
        suffix = 1
        while candidate in used:
            suffix += 1
            candidate = f"{base}{suffix}"
        used.add(candidate)
        prefixes[team.team_id] = candidate
    return prefixes


def build_issues(
    rng: random.Random,
    teams: List[Team],
    issues_per_team: int,
    sprint_name: str,
    reference_date: date = REFERENCE_DATE,
) -> List[Issue]:
    prefixes = assign_issue_prefixes(teams)
    issues: List[Issue] = []
    for team in teams:
        prefix = prefixes[team.team_id]
        for n in range(1, issues_per_team + 1):
            age_days = rng.randint(1, 90)
            created_dt = reference_date - timedelta(days=age_days)
            updated_dt = created_dt + timedelta(days=rng.randint(0, age_days))
            status = rng.choice(STATUSES)
            if status == "Done":
                slack = max(0, (reference_date - updated_dt).days)
                resolved_dt = updated_dt + timedelta(days=rng.randint(0, slack))
                resolved = resolved_dt.isoformat()
            else:
                resolved = ""
            issues.append(
                Issue(
                    issue_key=f"{prefix}-{n}",
                    team_id=team.team_id,
                    issue_type=rng.choice(ISSUE_TYPES),
                    status=status,
                    priority=rng.choice(PRIORITIES),
                    summary=f"{rng.choice(SUMMARY_VERBS)} {rng.choice(SUMMARY_NOUNS)}",
                    story_points=rng.choice(STORY_POINTS),
                    created=created_dt.isoformat(),
                    updated=updated_dt.isoformat(),
                    resolved=resolved,
                    sprint=sprint_name,
                )
            )
    return issues


def derive_category(blocking_team: Team, blocked_team: Team) -> str:
    if blocking_team.team_id == blocked_team.team_id:
        return CATEGORY_INTRA
    if blocking_team.type == "External" or blocked_team.type == "External":
        return CATEGORY_EXTERNAL
    return CATEGORY_INTER


def build_blockers(
    rng: random.Random,
    issues: List[Issue],
    teams_by_id: Dict[str, Team],
    blocker_density: float,
    external_bias: float,
    resolved_ratio: float,
    reference_date: date = REFERENCE_DATE,
) -> List[BlockerLink]:
    issues_by_key = {i.issue_key: i for i in issues}
    external_keys = [i.issue_key for i in issues if teams_by_id[i.team_id].type == "External"]

    blockers: List[BlockerLink] = []
    link_counter = 1
    for blocked_issue in issues:
        if rng.random() >= blocker_density:
            continue

        pool: Optional[List[str]] = None
        if external_keys and rng.random() < external_bias:
            candidates = [k for k in external_keys if k != blocked_issue.issue_key]
            if candidates:
                pool = candidates
        if pool is None:
            pool = [i.issue_key for i in issues if i.issue_key != blocked_issue.issue_key]
        if not pool:
            continue

        blocking_issue = issues_by_key[rng.choice(pool)]
        category = derive_category(teams_by_id[blocking_issue.team_id], teams_by_id[blocked_issue.team_id])

        raise_age = rng.randint(0, 60)
        raised_dt = reference_date - timedelta(days=raise_age)
        is_resolved = rng.random() < resolved_ratio
        if is_resolved:
            resolved_dt = min(raised_dt + timedelta(days=rng.randint(1, raise_age + 1)), reference_date)
            resolved_date = resolved_dt.isoformat()
            is_active = False
        else:
            resolved_date = ""
            is_active = True

        blockers.append(
            BlockerLink(
                link_id=f"BLK-{link_counter}",
                blocking_issue=blocking_issue.issue_key,
                blocked_issue=blocked_issue.issue_key,
                link_type="blocks",
                category=category,
                severity=rng.choice(SEVERITIES),
                raised_date=raised_dt.isoformat(),
                resolved_date=resolved_date,
                is_active=is_active,
            )
        )
        link_counter += 1
    return blockers


def compute_percolation_stats(issues: List[Issue], blockers: List[BlockerLink]) -> dict:
    keys = [i.issue_key for i in issues]
    uf = UnionFind(keys)
    for b in blockers:
        uf.union(b.blocking_issue, b.blocked_issue)

    components: Dict[str, List[str]] = {}
    for k in keys:
        components.setdefault(uf.find(k), []).append(k)

    sizes = sorted((len(v) for v in components.values()), reverse=True)
    total = len(keys)
    largest = sizes[0] if sizes else 0

    return {
        "total_issues": total,
        "total_blockers": len(blockers),
        "component_count": len(components),
        "largest_component_size": largest,
        "largest_component_fraction": (largest / total) if total else 0.0,
        "category_counts": dict(Counter(b.category for b in blockers)),
        "component_sizes": sizes,
    }


def write_csv(path: Path, rows: List, fieldnames: List[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_teams_csv(teams: List[Team], path: Path) -> None:
    write_csv(path, teams, ["team_id", "name", "type", "capacity_points"])


def write_issues_csv(issues: List[Issue], path: Path) -> None:
    write_csv(
        path,
        issues,
        ["issue_key", "team_id", "issue_type", "status", "priority", "summary",
         "story_points", "created", "updated", "resolved", "sprint"],
    )


def write_blockers_csv(blockers: List[BlockerLink], path: Path) -> None:
    write_csv(
        path,
        blockers,
        ["link_id", "blocking_issue", "blocked_issue", "link_type", "category",
         "severity", "raised_date", "resolved_date", "is_active"],
    )


def write_validation_report(stats: dict, teams: List[Team], path: Path, params: dict) -> None:
    internal_count = sum(1 for t in teams if t.type == "Internal")
    external_count = sum(1 for t in teams if t.type == "External")

    lines = [
        "# Validation Report",
        "",
        "Generated by `src/generate_blocker_data.py` — regenerate anytime with the "
        "same `--seed` for identical output. See ARCHITECTURE.md for the percolation "
        "model this report summarizes.",
        "",
        "## Dataset size",
        "",
        f"- Teams: {len(teams)} ({internal_count} internal, {external_count} external)",
        f"- Issues: {stats['total_issues']}",
        f"- Blocker links: {stats['total_blockers']}",
        "",
        "## Blocker category breakdown",
        "",
    ]
    for cat in (CATEGORY_INTRA, CATEGORY_INTER, CATEGORY_EXTERNAL):
        lines.append(f"- {cat}: {stats['category_counts'].get(cat, 0)}")
    lines += [
        "",
        "## Percolation statistics",
        "",
        f"- Connected components: {stats['component_count']}",
        f"- Largest component size: {stats['largest_component_size']} issues",
        f"- Largest component fraction (order parameter): {stats['largest_component_fraction']:.3f}",
        f"- Component size distribution (top 5): {stats['component_sizes'][:5]}",
        "",
        "## Generation parameters",
        "",
    ]
    for k, v in params.items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    path.write_text("\n".join(lines))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate synthetic Jira/Xray blocker data.")
    p.add_argument("--num-internal-teams", type=int, default=5)
    p.add_argument("--num-external-teams", type=int, default=3)
    p.add_argument("--issues-per-team", type=int, default=25)
    p.add_argument("--blocker-density", type=float, default=0.35)
    p.add_argument("--external-bias", type=float, default=0.3)
    p.add_argument("--resolved-ratio", type=float, default=0.4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--sprint-name", default="Sprint 1")
    p.add_argument("--output-dir", default="data")
    p.add_argument("--report-dir", default="docs")
    return p


def generate_dataset(args: argparse.Namespace):
    rng = random.Random(args.seed)
    teams = build_teams(rng, args.num_internal_teams, args.num_external_teams)
    issues = build_issues(rng, teams, args.issues_per_team, args.sprint_name)
    teams_by_id = {t.team_id: t for t in teams}
    blockers = build_blockers(
        rng, issues, teams_by_id, args.blocker_density, args.external_bias, args.resolved_ratio
    )
    stats = compute_percolation_stats(issues, blockers)
    return teams, issues, blockers, stats


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    teams, issues, blockers, stats = generate_dataset(args)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    write_teams_csv(teams, output_dir / "teams.csv")
    write_issues_csv(issues, output_dir / "issues.csv")
    write_blockers_csv(blockers, output_dir / "blockers.csv")
    write_validation_report(stats, teams, report_dir / "validation_report.md", vars(args))

    print(f"Generated {len(teams)} teams, {len(issues)} issues, {len(blockers)} blocker links.")
    print(
        f"Largest blocker cluster: {stats['largest_component_size']}/{stats['total_issues']} "
        f"issues ({stats['largest_component_fraction']:.1%})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
