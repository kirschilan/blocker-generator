"""Automated checks for BACKLOG.md Task 1.1 (squad domain model) and
Task 2.1 (5-squad + DataPlatform extension)."""
import json

from blocker_generator.squads import (
    AUTH,
    CHECKOUT,
    CORE_BANKING,
    DATA_PLATFORM,
    PAYMENTS,
    SAVINGS,
    Squad,
    build_auth_subgraph,
    build_five_squad_subgraph,
)


def test_three_squads_instantiated():
    squads = build_auth_subgraph()
    assert len(squads) == 3
    assert {s.id for s in squads} == {AUTH, CHECKOUT, PAYMENTS}


def test_auth_has_no_dependencies():
    squads = {s.id: s for s in build_auth_subgraph()}
    assert squads[AUTH].depends_on == []


def test_checkout_and_payments_depend_on_auth():
    squads = {s.id: s for s in build_auth_subgraph()}
    assert squads[CHECKOUT].depends_on == [AUTH]
    assert squads[PAYMENTS].depends_on == [AUTH]


def test_auth_owns_login_service():
    squads = {s.id: s for s in build_auth_subgraph()}
    assert squads[AUTH].owns_component == "Login Service"
    assert squads[CHECKOUT].owns_component == ""
    assert squads[PAYMENTS].owns_component == ""


def test_no_external_dependency_in_this_slice():
    # Task 1.1 acceptance criteria: "External dependency: (none for this
    # slice; deferred)" — the Squad model has no field for it yet, and
    # depends_on only ever references other Squad ids in this slice.
    squads = build_auth_subgraph()
    all_ids = {s.id for s in squads}
    for squad in squads:
        assert set(squad.depends_on) <= all_ids


def test_squad_names_and_ids_match_architecture_md():
    squads = {s.id: s for s in build_auth_subgraph()}
    assert squads[AUTH].name == "Auth"
    assert squads[CHECKOUT].name == "Checkout"
    assert squads[PAYMENTS].name == "Payments"


def test_datastructure_is_json_serializable():
    squads = build_auth_subgraph()
    serialized = json.dumps([s.to_json() for s in squads])
    reloaded = json.loads(serialized)
    assert len(reloaded) == 3
    assert reloaded[0]["id"] == AUTH
    assert reloaded[1]["depends_on"] == [AUTH]


def test_auth_blocks_the_other_two():
    # "confirm Auth blocks the other two" (BACKLOG.md Task 1.1 verification)
    squads = build_auth_subgraph()
    auth = next(s for s in squads if s.id == AUTH)
    dependents = [s for s in squads if auth.id in s.depends_on]
    assert {s.id for s in dependents} == {CHECKOUT, PAYMENTS}


# --- BACKLOG.md Task 2.1: 5-squad + DataPlatform extension ---


def test_five_squads_instantiated():
    squads = build_five_squad_subgraph()
    assert len(squads) == 5
    assert {s.id for s in squads} == {AUTH, CHECKOUT, PAYMENTS, CORE_BANKING, SAVINGS}


def test_task_1_1_squads_unchanged_by_extension():
    # "Extend Task 1.1 datastructure (no breaking changes)"
    original = {s.id: s for s in build_auth_subgraph()}
    extended = {s.id: s for s in build_five_squad_subgraph()}
    for squad_id in (AUTH, CHECKOUT, PAYMENTS):
        assert extended[squad_id] == original[squad_id]


def test_core_banking_depends_on_auth_and_data_platform():
    squads = {s.id: s for s in build_five_squad_subgraph()}
    assert squads[CORE_BANKING].depends_on == [AUTH]
    assert squads[CORE_BANKING].external_depends_on == [DATA_PLATFORM]


def test_savings_depends_on_core_banking_indirectly():
    # "Adjacency: DataPlatform -> Core Banking -> Savings (indirect)" --
    # Savings has no *direct* external dependency of its own.
    squads = {s.id: s for s in build_five_squad_subgraph()}
    assert squads[SAVINGS].depends_on == [CORE_BANKING]
    assert squads[SAVINGS].external_depends_on == []


def test_only_core_banking_has_external_dependency():
    squads = build_five_squad_subgraph()
    with_external = [s.id for s in squads if s.external_depends_on]
    assert with_external == [CORE_BANKING]


def test_five_squad_datastructure_is_json_serializable():
    squads = build_five_squad_subgraph()
    serialized = json.dumps([s.to_json() for s in squads])
    reloaded = json.loads(serialized)
    assert len(reloaded) == 5
    core_banking = next(s for s in reloaded if s["id"] == CORE_BANKING)
    assert core_banking["depends_on"] == [AUTH]
    assert core_banking["external_depends_on"] == [DATA_PLATFORM]
