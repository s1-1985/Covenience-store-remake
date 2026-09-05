from __future__ import annotations

from dataclasses import dataclass

from .staff import StaffTask
from .staff_task_policy import StaffTaskCandidate
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class StoreWorkCandidateSnapshot:
    """Objective work opportunities currently visible in the store runtime."""

    checkout: tuple[StaffTaskCandidate, ...]
    replenish: tuple[StaffTaskCandidate, ...]
    clean: tuple[StaffTaskCandidate, ...]

    @property
    def all_candidates(self) -> tuple[StaffTaskCandidate, ...]:
        # Grouping/order is deterministic only; it is not an AI priority rule.
        return self.checkout + self.replenish + self.clean


class StaffWorkCandidateDiscovery:
    """Discover factual work opportunities without choosing who should do them.

    This layer deliberately does not score or prioritize tasks.  It only exposes
    work that is objectively possible from current runtime state:

    - a checkout with at least one waiting customer,
    - an inventory slot that is not full,
    - a currently dirty editable floor cell.

    Every staff member receives the same candidate set.  The existing
    StaffTaskPolicyCoordinator remains responsible for independent per-staff
    choices and for skipping staff who are unavailable or on break.
    """

    CLEAN_TARGET_PREFIX = "floor:"

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime

    @classmethod
    def cleaning_target_id(cls, x: int, y: int) -> str:
        return f"{cls.CLEAN_TARGET_PREFIX}{x}:{y}"

    def discover(self) -> StoreWorkCandidateSnapshot:
        checkout: list[StaffTaskCandidate] = []
        for fixture_id in sorted(self.runtime.checkout_fixture_ids):
            station = self.runtime.checkout(fixture_id)
            waiting = station.refresh_waiting()
            if waiting:
                checkout.append(
                    StaffTaskCandidate(
                        StaffTask.CHECKOUT,
                        target_id=fixture_id,
                        reason=f"{len(waiting)} customer(s) waiting",
                    )
                )

        replenish: list[StaffTaskCandidate] = []
        for slot in sorted(self.runtime.inventory.slots, key=lambda item: item.id):
            if slot.free_capacity <= 0:
                continue
            replenish.append(
                StaffTaskCandidate(
                    StaffTask.REPLENISH,
                    target_id=slot.id,
                    reason=f"{slot.free_capacity} free unit(s)",
                )
            )

        clean: list[StaffTaskCandidate] = []
        for cell in sorted(self.runtime.cleaning.dirty_cells):
            clean.append(
                StaffTaskCandidate(
                    StaffTask.CLEAN,
                    target_id=self.cleaning_target_id(cell.x, cell.y),
                    reason="dirty floor cell",
                )
            )

        return StoreWorkCandidateSnapshot(
            checkout=tuple(checkout),
            replenish=tuple(replenish),
            clean=tuple(clean),
        )

    def candidates_by_staff(self) -> dict[str, tuple[StaffTaskCandidate, ...]]:
        snapshot = self.discover()
        return {
            state.id: snapshot.all_candidates
            for state in self.runtime.staff.staff
        }
