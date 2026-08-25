"""Squad domain model.

Implements BACKLOG.md Task 1.1: the Auth-centric 3-squad subgraph carved out
of ARCHITECTURE.md's "Squad Topology" for Sprint 1's minimum viable dataset.

Per Task 1.1's acceptance criteria this slice is deliberately narrower than
the full 8-squad topology in ARCHITECTURE.md: only the two edges Auth ->
Checkout and Auth -> Payments are modeled (the Checkout -> Payments tight
coupling belongs to the full topology, not this slice), and no external
dependency is attached yet ("External dependency: (none for this slice;
deferred)").

Task 2.1 (Milestone 2) extends this with Core Banking and Savings plus the
first external dependency, DataPlatform. `depends_on` keeps meaning
"other Squad ids in this slice" (the existing invariant every Task 1.1 test
relies on); `external_depends_on` is a new, separate field for non-squad
systems rather than overloading `depends_on` with a mixed type. Like Task
1.1, this slice is still narrower than the full topology: Core Banking's
squad-level dependency on Payments (ARCHITECTURE.md's Interdependency
Graph) isn't modeled yet, matching this task's own acceptance criteria
(only Auth -> Core Banking, and DataPlatform -> Core Banking -> Savings).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

AUTH = "SQ-A"
CHECKOUT = "SQ-B"
CORE_BANKING = "SQ-C"
PAYMENTS = "SQ-D"
SAVINGS = "SQ-E"

DATA_PLATFORM = "DataPlatform"


@dataclass
class Squad:
    id: str
    name: str
    domain: str
    depends_on: List[str] = field(default_factory=list)
    external_depends_on: List[str] = field(default_factory=list)
    owns_component: str = ""

    def to_json(self) -> dict:
        return asdict(self)


def build_auth_subgraph() -> List[Squad]:
    """The 3 squads for Sprint 1: Auth (root) + Checkout, Payments (dependents).

    Adjacency (ARCHITECTURE.md "Squad Topology", Auth-centric subgraph):
    Auth -> Checkout, Auth -> Payments. Auth owns the shared Login Service
    component (ARCHITECTURE.md "Shared Components").
    """
    auth = Squad(
        id=AUTH,
        name="Auth",
        domain="secure-login",
        depends_on=[],
        owns_component="Login Service",
    )
    checkout = Squad(
        id=CHECKOUT,
        name="Checkout",
        domain="shopping-cart-payment-flow",
        depends_on=[auth.id],
    )
    payments = Squad(
        id=PAYMENTS,
        name="Payments",
        domain="payment-media-fraud-settlement",
        depends_on=[auth.id],
    )
    return [auth, checkout, payments]


def build_five_squad_subgraph() -> List[Squad]:
    """The 5 squads for Milestone 2 (BACKLOG.md Task 2.1): Task 1.1's
    3 squads plus Core Banking (root of Cluster 2) and Savings (its
    cascade), plus the first external dependency, DataPlatform.

    Adjacency (ARCHITECTURE.md "Squad Topology", narrowed per Task 2.1's
    acceptance criteria): Auth -> Core Banking (squad); DataPlatform ->
    Core Banking (external, 40% of SQ-C's capacity during annual gates,
    ARCHITECTURE.md "External Dependencies") -> Savings (indirect —
    Savings has no direct DataPlatform dependency of its own).
    """
    auth, checkout, payments = build_auth_subgraph()
    core_banking = Squad(
        id=CORE_BANKING,
        name="Core Banking",
        domain="account-balances-ledger-integrity-transaction-history",
        depends_on=[auth.id],
        external_depends_on=[DATA_PLATFORM],
    )
    savings = Squad(
        id=SAVINGS,
        name="Savings",
        domain="savings-goals-rates-account-opening",
        depends_on=[core_banking.id],
    )
    return [auth, checkout, payments, core_banking, savings]


def print_adjacency(squads: List[Squad]) -> None:
    """Verification helper (BACKLOG.md Task 1.1: "Print adjacency; confirm
    Auth blocks the other two")."""
    for squad in squads:
        deps = ", ".join(squad.depends_on) if squad.depends_on else "(none)"
        line = f"{squad.id} ({squad.name}) depends_on: {deps}"
        if squad.external_depends_on:
            line += f"; external: {', '.join(squad.external_depends_on)}"
        print(line)


if __name__ == "__main__":
    print_adjacency(build_auth_subgraph())
