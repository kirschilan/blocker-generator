"""Blocker archetype taxonomy.

Implements BACKLOG.md Task 1.2 against ARCHITECTURE.md's "Blocker
Archetypes" table. Code once, reused across every sprint/cluster.

Note: ARCHITECTURE.md's archetype table states ExternalDelay as "5-20
days" while BACKLOG.md's Task 1.2 acceptance criteria states "10-20
days" for the same archetype. This implementation follows the literal
Task 1.2 acceptance criteria (10-20); it doesn't affect Sprint 1's
output since Cluster 1 (the only cluster Sprint 1 injects) uses
SharedCompFailure, not ExternalDelay. Flagged in session_log.md for
whoever builds the Sprint 2 DataPlatform cluster.

affected_squads is deliberately not a field here (contrast with
ARCHITECTURE.md's internal-notes pseudocode): a taxonomy entry is
reusable across squads by construction ("No hardcoded squad names in
templates"); which squads are affected belongs to a BlockerCluster
(Task 1.3), not the archetype.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class BlockerArchetype:
    type_id: str
    duration_days: Tuple[int, int]
    waiting_reason_template: str


SHARED_COMP_FAILURE = BlockerArchetype(
    type_id="SharedCompFailure",
    duration_days=(2, 5),
    waiting_reason_template="Waiting on {component} service",
)
EXTERNAL_DELAY = BlockerArchetype(
    type_id="ExternalDelay",
    duration_days=(10, 20),
    waiting_reason_template="Waiting on {external_system} team",
)
PEER_SQUAD_OVERLOAD = BlockerArchetype(
    type_id="PeerSquadOverload",
    duration_days=(1, 3),
    waiting_reason_template="Waiting on {peer_squad} capacity",
)
TEST_INFRA_ISSUE = BlockerArchetype(
    type_id="TestInfraIssue",
    duration_days=(1, 2),
    waiting_reason_template="Waiting on test infrastructure / flaky tests",
)
INTEGRATION_GAP = BlockerArchetype(
    type_id="IntegrationGap",
    duration_days=(2, 4),
    waiting_reason_template="Waiting on {integration} API integration / contract clarification",
)
KNOWLEDGE_GAP = BlockerArchetype(
    type_id="KnowledgeGap",
    duration_days=(1, 2),
    waiting_reason_template="Waiting on domain knowledge / legacy code review",
)

ARCHETYPES: Dict[str, BlockerArchetype] = {
    a.type_id: a
    for a in (
        SHARED_COMP_FAILURE,
        EXTERNAL_DELAY,
        PEER_SQUAD_OVERLOAD,
        TEST_INFRA_ISSUE,
        INTEGRATION_GAP,
        KNOWLEDGE_GAP,
    )
}
