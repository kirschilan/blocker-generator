"""Automated checks for BACKLOG.md Task 1.2 (blocker archetype taxonomy)."""
from blocker_generator.archetypes import (
    ARCHETYPES,
    EXTERNAL_DELAY,
    INTEGRATION_GAP,
    KNOWLEDGE_GAP,
    PEER_SQUAD_OVERLOAD,
    SHARED_COMP_FAILURE,
    TEST_INFRA_ISSUE,
)

EXPECTED_DURATIONS = {
    "SharedCompFailure": (2, 5),
    "ExternalDelay": (10, 20),
    "PeerSquadOverload": (1, 3),
    "TestInfraIssue": (1, 2),
    "IntegrationGap": (2, 4),
    "KnowledgeGap": (1, 2),
}


def test_all_six_archetypes_present():
    assert set(ARCHETYPES.keys()) == set(EXPECTED_DURATIONS.keys())


def test_duration_ranges_match_backlog():
    for type_id, expected in EXPECTED_DURATIONS.items():
        assert ARCHETYPES[type_id].duration_days == expected


def test_shared_comp_failure_duration():
    assert SHARED_COMP_FAILURE.duration_days == (2, 5)


def test_waiting_reason_templates_have_no_hardcoded_squad_names():
    squad_names = {"Auth", "Checkout", "Payments", "Core Banking", "Savings"}
    for archetype in ARCHETYPES.values():
        for name in squad_names:
            assert name not in archetype.waiting_reason_template


def test_templates_support_substitution_where_needed():
    assert EXTERNAL_DELAY.waiting_reason_template.format(external_system="DataPlatform") == (
        "Waiting on DataPlatform team"
    )
    assert PEER_SQUAD_OVERLOAD.waiting_reason_template.format(peer_squad="Checkout") == (
        "Waiting on Checkout capacity"
    )
    assert INTEGRATION_GAP.waiting_reason_template.format(integration="CRM") == (
        "Waiting on CRM API integration / contract clarification"
    )
    # Fixed-text templates (no placeholders) render as-is.
    assert TEST_INFRA_ISSUE.waiting_reason_template == "Waiting on test infrastructure / flaky tests"
    assert KNOWLEDGE_GAP.waiting_reason_template == "Waiting on domain knowledge / legacy code review"
