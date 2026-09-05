from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

from .store_grid import GridPoint
from .traffic import AgentStatus, DynamicTrafficHarness, TrafficTickResult


class CustomerState(str, Enum):
    ENTERED = "entered"
    APPROACHING_MERCHANDISE = "approaching_merchandise"
    AT_MERCHANDISE = "at_merchandise"
    APPROACHING_CHECKOUT = "approaching_checkout"
    WAITING_CHECKOUT = "waiting_checkout"
    LEAVING = "leaving"
    EJECTING = "ejecting"
    EXITED = "exited"
    EJECTED = "ejected"
    UNREACHABLE = "unreachable"


class PurchaseFlow(str, Enum):
    """A caller-supplied flow classification, not an automatic decision."""

    CHECKOUT_REQUIRED = "checkout_required"
    SELF_SERVICE_CANDIDATE = "self_service_candidate"


@dataclass
class CustomerSession:
    id: str
    state: CustomerState
    exit_point: GridPoint
    checkout_fixture_id: Optional[str]
    planned_merchandise_fixture_ids: tuple[str, ...]
    next_merchandise_index: int = 0
    current_merchandise_fixture_id: Optional[str] = None
    requires_checkout: bool = False
    completed_checkout: bool = False
    interacted_fixture_ids: tuple[str, ...] = ()
    self_service_fixture_ids: tuple[str, ...] = ()
    ejection_reason: Optional[str] = None

    @property
    def remaining_merchandise_fixture_ids(self) -> tuple[str, ...]:
        return self.planned_merchandise_fixture_ids[self.next_merchandise_index :]


@dataclass(frozen=True)
class CustomerTickResult:
    traffic: TrafficTickResult
    state_changes: tuple[tuple[str, CustomerState], ...]


class CustomerLifecycleHarness:
    """Minimal observable customer-flow state machine.

    This class deliberately does not choose products, decide whether an add-on
    purchase happens, calculate patience, form a checkout queue, or decide a
    checkout duration. Those behaviors remain external/unknown.
    """

    def __init__(self, traffic: DynamicTrafficHarness) -> None:
        self.traffic = traffic
        self._customers: dict[str, CustomerSession] = {}

    @property
    def customers(self) -> tuple[CustomerSession, ...]:
        return tuple(self._customers.values())

    def customer(self, customer_id: str) -> CustomerSession:
        return self._customers[customer_id]

    def add_customer(
        self,
        customer_id: str,
        *,
        entry_point: GridPoint,
        exit_point: GridPoint,
        merchandise_fixture_ids: Sequence[str] = (),
        checkout_fixture_id: Optional[str] = None,
    ) -> CustomerSession:
        if customer_id in self._customers:
            raise ValueError(f"duplicate customer id: {customer_id}")
        if not self.traffic.grid.is_walkable(exit_point):
            raise ValueError("exit point must be walkable")

        self.traffic.add_agent(customer_id, entry_point)
        session = CustomerSession(
            id=customer_id,
            state=CustomerState.ENTERED,
            exit_point=exit_point,
            checkout_fixture_id=checkout_fixture_id,
            planned_merchandise_fixture_ids=tuple(merchandise_fixture_ids),
        )
        self._customers[customer_id] = session
        self._route_to_next_step(session)
        return session

    def _route_to_next_step(self, session: CustomerSession) -> None:
        if session.next_merchandise_index < len(session.planned_merchandise_fixture_ids):
            fixture_id = session.planned_merchandise_fixture_ids[session.next_merchandise_index]
            session.current_merchandise_fixture_id = fixture_id
            session.state = CustomerState.APPROACHING_MERCHANDISE
            self.traffic.set_fixture_goal(session.id, fixture_id)
            self._sync_unreachable(session)
            return

        session.current_merchandise_fixture_id = None
        if session.requires_checkout and not session.completed_checkout:
            if session.checkout_fixture_id is None:
                raise ValueError(
                    f"customer {session.id} requires checkout but no checkout fixture was supplied"
                )
            session.state = CustomerState.APPROACHING_CHECKOUT
            self.traffic.set_fixture_goal(session.id, session.checkout_fixture_id)
            self._sync_unreachable(session)
            return

        session.state = CustomerState.LEAVING
        self.traffic.set_point_goal(session.id, session.exit_point)
        self._sync_unreachable(session)

    def _sync_unreachable(self, session: CustomerSession) -> None:
        if self.traffic.agent(session.id).status is AgentStatus.UNREACHABLE:
            session.state = CustomerState.UNREACHABLE

    def record_merchandise_interaction(
        self,
        customer_id: str,
        *,
        flow: PurchaseFlow,
    ) -> CustomerSession:
        session = self._customers[customer_id]
        if session.state is not CustomerState.AT_MERCHANDISE:
            raise ValueError("customer is not at merchandise")
        fixture_id = session.current_merchandise_fixture_id
        if fixture_id is None:
            raise RuntimeError("AT_MERCHANDISE without current fixture")
        if flow is PurchaseFlow.CHECKOUT_REQUIRED and session.checkout_fixture_id is None:
            raise ValueError("checkout-required interaction needs a checkout fixture")

        session.interacted_fixture_ids = session.interacted_fixture_ids + (fixture_id,)
        if flow is PurchaseFlow.CHECKOUT_REQUIRED:
            session.requires_checkout = True
        elif flow is PurchaseFlow.SELF_SERVICE_CANDIDATE:
            session.self_service_fixture_ids = session.self_service_fixture_ids + (fixture_id,)
        else:
            raise ValueError(f"unsupported purchase flow: {flow}")

        session.next_merchandise_index += 1
        self._route_to_next_step(session)
        return session

    def leave_merchandise_without_purchase(self, customer_id: str) -> CustomerSession:
        """Advance from the current merchandise stop without inventing a purchase.

        A future purchase policy may explicitly decide that a customer buys
        nothing at a visited fixture.  This transition records no purchase and
        no interacted fixture; it only advances the already caller-supplied
        route.  The original probability of such a decision remains external.
        """
        session = self._customers[customer_id]
        if session.state is not CustomerState.AT_MERCHANDISE:
            raise ValueError("customer is not at merchandise")
        if session.current_merchandise_fixture_id is None:
            raise RuntimeError("AT_MERCHANDISE without current fixture")
        session.next_merchandise_index += 1
        self._route_to_next_step(session)
        return session

    def complete_checkout(self, customer_id: str) -> CustomerSession:
        session = self._customers[customer_id]
        if session.state is not CustomerState.WAITING_CHECKOUT:
            raise ValueError("customer is not waiting at checkout")
        session.completed_checkout = True
        self._route_to_next_step(session)
        return session

    def force_eject(self, customer_id: str, *, reason: Optional[str] = None) -> CustomerSession:
        session = self._customers[customer_id]
        if session.state in (CustomerState.EXITED, CustomerState.EJECTED):
            raise ValueError("customer has already left")
        session.ejection_reason = reason
        session.state = CustomerState.EJECTING
        session.current_merchandise_fixture_id = None
        self.traffic.set_point_goal(session.id, session.exit_point)
        self._sync_unreachable(session)
        return session

    def tick(self) -> CustomerTickResult:
        traffic_result = self.traffic.tick()
        state_changes: list[tuple[str, CustomerState]] = []

        for session in self._customers.values():
            agent = self.traffic.agent(session.id)
            previous_state = session.state

            if agent.status is AgentStatus.UNREACHABLE and session.state not in (
                CustomerState.EXITED,
                CustomerState.EJECTED,
            ):
                session.state = CustomerState.UNREACHABLE
            elif agent.status is AgentStatus.ARRIVED:
                if session.state is CustomerState.APPROACHING_MERCHANDISE:
                    session.state = CustomerState.AT_MERCHANDISE
                elif session.state is CustomerState.APPROACHING_CHECKOUT:
                    session.state = CustomerState.WAITING_CHECKOUT
                elif session.state is CustomerState.LEAVING:
                    session.state = CustomerState.EXITED
                elif session.state is CustomerState.EJECTING:
                    session.state = CustomerState.EJECTED

            if session.state is not previous_state:
                state_changes.append((session.id, session.state))

        return CustomerTickResult(traffic_result, tuple(state_changes))
