"""CSV writers for the Jira-format issue export (Task 1.4) and the
Xray-like test execution log export (Task 1.5)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from blocker_generator.features import ALL_COLUMNS, IssueRow, row_to_csv_dict
from blocker_generator.xray_logs import TEST_LOG_COLUMNS, TestLogRow, log_row_to_csv_dict


def write_jira_csv(rows: List[IssueRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ALL_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row_to_csv_dict(row))


def write_test_logs_csv(rows: List[TestLogRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEST_LOG_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(log_row_to_csv_dict(row))
