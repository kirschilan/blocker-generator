"""CSV writers for the Jira-format issue export (Task 1.4) and the
Xray-like test execution log export (Task 1.5)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from blocker_generator.features import IssueRow, build_header, max_sprint_span, row_to_csv_row
from blocker_generator.xray_logs import TEST_LOG_COLUMNS, TestLogRow, log_row_to_csv_dict


def write_jira_csv(rows: List[IssueRow], path: Path) -> None:
    """Positional writer, not DictWriter: a real Jira export's repeated
    'Sprint' header (Issue #7) means duplicate column names, which a
    dict-keyed row can't represent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sprint_slots = max_sprint_span(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(build_header(sprint_slots))
        for row in rows:
            writer.writerow(row_to_csv_row(row, sprint_slots))


def write_test_logs_csv(rows: List[TestLogRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TEST_LOG_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(log_row_to_csv_dict(row))
