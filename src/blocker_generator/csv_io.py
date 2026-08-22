"""CSV writer for the Jira-format issue export (Task 1.4)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from blocker_generator.features import ALL_COLUMNS, IssueRow, row_to_csv_dict


def write_jira_csv(rows: List[IssueRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ALL_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row_to_csv_dict(row))
