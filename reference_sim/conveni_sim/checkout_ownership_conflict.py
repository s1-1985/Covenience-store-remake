from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from .staff import StaffCondition, StaffTask, StoreStaffRoster
from .store_runtime import StoreRuntimeHarness


class CheckoutConflictLoserDisposition(str, Enum):
    KEEP_CHECKOUT = "keep_checkout"
    RELEASE_TO_IDLE = "release_to_idle"
    RETURN_TO_BREAK_ROOM = "return_to_break_room"


@dataclass(frozen=True)
class CheckoutConflictLoserDecision:
    staff_id: str
    disposition: CheckoutConflictLoserDisposition
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.staff_id:
            raise ValueError("checkout conflict loser decision requires staff_id")
        if (
            self.disposition is not CheckoutConflictLoserDisposition.RETURN_TO_BREAK_ROOM
            and self.break_room_target_id is not None
        ):
            raise ValueError(
                "break_room_target_id is only valid for RETURN_TO_BREAK_ROOM"
            )


@dataclass(frozen=True)
class CheckoutOwnershipConflictContext:
    checkout_fixture_id: str
    contender_staff_ids: tuple[str, ...]
    active_staff_ids: tuple[str, ...]
    waiting_customer_ids: tuple[str, ...]
    simultaneous_staff_capacity: int
    free_service_slots: int


@dataclass(frozen=True)
class CheckoutOwnershipConflictDecision:
    owner_staff_ids: tuple[str, ...]
    loser_decisions: tuple[CheckoutConflictLoserDecision, ...]

    def __post_init__(self) -> None:
        if len(set(self.owner_staff_ids)) != len(self.owner_staff_ids):
            raise ValueError("owner_staff_ids must be unique")
        loser_ids = tuple(item.staff_id for item in self.loser_decisions)
        if len(set(loser_ids)) != len(loser_ids):
            raise ValueError("checkout conflict loser staff ids must be unique")
        if set(self.owner_staff_ids) & set(loser_ids):
            raise ValueError("checkout conflict staff cannot be both owner and loser")


class CheckoutOwnershipConflictPolicy(Protocol):
    """Resolve an explicitly detected checkout ownership conflict.

    First-title evidence supports multiple staff reacting to the same checkout
    demand and only one ultimately serving in some cases. It does not recover
    the original winner rule or loser transition. Returning None therefore keeps
    the conflict unresolved instead of inventing a winner.
    """

    def resolve(
        self,
        context: CheckoutOwnershipConflictContext,
    ) -> Optional[CheckoutOwnershipConflictDecision]: ...


class CheckoutOwnershipConflictStatus(str, Enum):
    NO_CONFLICT = "no_conflict"
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class CheckoutOwnershipConflictEvaluation:
    context: CheckoutOwnershipConflictContext
    status: CheckoutOwnershipConflictStatus
    decision: Optional[CheckoutOwnershipConflictDecision] = None

    @property
    def conflicting(self) -> bool:
        return self.status is not CheckoutOwnershipConflictStatus.NO_CONFLICT


class CheckoutOwnershipConflictCoordinator:
    """Detect and optionally resolve competing checkout assignments.

    A conflict exists only when more AVAILABLE staff are assigned to one
    checkout without active service than there are currently free service slots.
    The coordinator does not choose a winner itself. A supplied policy may name
    owners and must account for every contender as either an owner or loser.

    Losers can remain assigned, return to idle, or explicitly begin a break-room
    return. None of those outcomes is treated as the original default.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime

    def _context(self, checkout_fixture_id: str) -> CheckoutOwnershipConflictContext:
        checkout = self.runtime.checkout(checkout_fixture_id)
        checkout.refresh_waiting()
        active_staff_ids = tuple(record.staff_id for record in checkout.active_services)
        active_staff_set = set(active_staff_ids)
        contender_staff_ids = tuple(
            staff.id
            for staff in self.runtime.staff.staff
            if staff.condition is StaffCondition.AVAILABLE
            and staff.task is StaffTask.CHECKOUT
            and staff.target_id == checkout_fixture_id
            and staff.id not in active_staff_set
        )
        free_service_slots = max(
            0,
            checkout.simultaneous_staff_capacity - len(active_staff_ids),
        )
        return CheckoutOwnershipConflictContext(
            checkout_fixture_id=checkout_fixture_id,
            contender_staff_ids=contender_staff_ids,
            active_staff_ids=active_staff_ids,
            waiting_customer_ids=checkout.waiting_customer_ids,
            simultaneous_staff_capacity=checkout.simultaneous_staff_capacity,
            free_service_slots=free_service_slots,
        )

    def evaluate_checkout(
        self,
        checkout_fixture_id: str,
        policy: CheckoutOwnershipConflictPolicy,
    ) -> CheckoutOwnershipConflictEvaluation:
        context = self._context(checkout_fixture_id)
        if len(context.contender_staff_ids) <= context.free_service_slots:
            return CheckoutOwnershipConflictEvaluation(
                context=context,
                status=CheckoutOwnershipConflictStatus.NO_CONFLICT,
            )

        decision = policy.resolve(context)
        if decision is None:
            return CheckoutOwnershipConflictEvaluation(
                context=context,
                status=CheckoutOwnershipConflictStatus.UNRESOLVED,
            )

        contenders = set(context.contender_staff_ids)
        owners = set(decision.owner_staff_ids)
        losers = {item.staff_id for item in decision.loser_decisions}
        if not owners <= contenders or not losers <= contenders:
            raise ValueError("checkout conflict decision references a non-contender")
        if owners | losers != contenders:
            raise ValueError("checkout conflict decision must account for every contender")
        if len(decision.owner_staff_ids) > context.free_service_slots:
            raise ValueError("checkout conflict decision exceeds free service slots")

        for loser in decision.loser_decisions:
            if loser.disposition is CheckoutConflictLoserDisposition.KEEP_CHECKOUT:
                continue
            if loser.disposition is CheckoutConflictLoserDisposition.RELEASE_TO_IDLE:
                self.runtime.staff.release_to_idle(loser.staff_id)
                continue
            self.runtime.staff.begin_break_room_return(
                loser.staff_id,
                break_room_target_id=loser.break_room_target_id,
            )

        return CheckoutOwnershipConflictEvaluation(
            context=context,
            status=CheckoutOwnershipConflictStatus.RESOLVED,
            decision=decision,
        )

    def evaluate_all(
        self,
        policy: CheckoutOwnershipConflictPolicy,
    ) -> tuple[CheckoutOwnershipConflictEvaluation, ...]:
        return tuple(
            self.evaluate_checkout(fixture_id, policy)
            for fixture_id in self.runtime.checkout_fixture_ids
        )
