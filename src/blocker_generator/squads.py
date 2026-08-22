"""Squad domain model.

Implements BACKLOG.md Task 1.1: the Auth-centric 3-squad subgraph carved out
of ARCHITECTURE.md's "Squad Topology" for Sprint 1's minimum viable dataset.

Per Task 1.1's acceptance criteria this slice is deliberately narrower than
the full 8-squad topology in ARCHITECTURE.md: only the two edges Auth ->
Checkout and Auth -> Payments are modeled (the Checkout -> Payments tight
coupling belongs to the full topology, not this slice), and no external
dependency is attached yet ("External dependency: (none for this slice;
deferred)").
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

AUTH = "SQ-A"
CHECKOUT = "SQ-B"
PAYMENTS = "SQ-D"


@dataclass
class Squad:
    id: str
    name: str
    domain: str
    depends_on: List[str] = field(default_factory=list)
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


def print_adjacency(squads: List[Squad]) -> None:
    """Verification helper (BACKLOG.md Task 1.1: "Print adjacency; confirm
    Auth blocks the other two")."""
    for squad in squads:
        deps = ", ".join(squad.depends_on) if squad.depends_on else "(none)"
        print(f"{squad.id} ({squad.name}) depends_on: {deps}")


if __name__ == "__main__":
    print_adjacency(build_auth_subgraph())
