from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .staff import StaffTask, StoreStaffRoster


class InventoryError(ValueError):
    pass


class OutOfStockError(InventoryError):
    pass


class CapacityExceededError(InventoryError):
    pass


@dataclass(frozen=True)
class InventoryMutation:
    slot_id: str
    fixture_id: str
    product_id: str
    quantity_delta: int
    units_after: int
    procurement_cost_yen: Optional[int] = None


@dataclass
class FixtureInventorySlot:
    """One explicit product stock slot attached to a fixture instance.

    Capacity and procurement cost must be supplied by the caller/source. This
    runtime intentionally has no guessed capacity, pack size, reorder point or
    replenishment amount.
    """

    id: str
    fixture_id: str
    product_id: str
    capacity_units: int
    units: int = 0
    unit_procurement_cost_yen: Optional[int] = None

    def __post_init__(self) -> None:
        if self.capacity_units < 0:
            raise ValueError("capacity_units must be >= 0")
        if self.units < 0 or self.units > self.capacity_units:
            raise ValueError("initial units must be within 0..capacity")
        if self.unit_procurement_cost_yen is not None and self.unit_procurement_cost_yen < 0:
            raise ValueError("unit procurement cost must be >= 0 or None")

    @property
    def free_capacity(self) -> int:
        return self.capacity_units - self.units

    @property
    def empty(self) -> bool:
        return self.units == 0

    @property
    def full(self) -> bool:
        return self.units == self.capacity_units

    def take(self, quantity: int = 1) -> InventoryMutation:
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        if quantity > self.units:
            raise OutOfStockError(
                f"slot {self.id!r} has {self.units} units, cannot take {quantity}"
            )
        self.units -= quantity
        return InventoryMutation(
            slot_id=self.id,
            fixture_id=self.fixture_id,
            product_id=self.product_id,
            quantity_delta=-quantity,
            units_after=self.units,
        )

    def replenish(self, quantity: int) -> InventoryMutation:
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        if quantity > self.free_capacity:
            raise CapacityExceededError(
                f"slot {self.id!r} has free capacity {self.free_capacity}, cannot add {quantity}"
            )
        self.units += quantity
        cost = (
            quantity * self.unit_procurement_cost_yen
            if self.unit_procurement_cost_yen is not None
            else None
        )
        return InventoryMutation(
            slot_id=self.id,
            fixture_id=self.fixture_id,
            product_id=self.product_id,
            quantity_delta=quantity,
            units_after=self.units,
            procurement_cost_yen=cost,
        )


class StoreInventoryRuntime:
    """Explicit store stock ledger; no automatic ordering policy is assumed."""

    def __init__(self) -> None:
        self._slots: dict[str, FixtureInventorySlot] = {}
        self._history: list[InventoryMutation] = []

    @property
    def slots(self) -> tuple[FixtureInventorySlot, ...]:
        return tuple(self._slots.values())

    @property
    def history(self) -> tuple[InventoryMutation, ...]:
        return tuple(self._history)

    def slot(self, slot_id: str) -> FixtureInventorySlot:
        return self._slots[slot_id]

    def add_slot(
        self,
        slot_id: str,
        *,
        fixture_id: str,
        product_id: str,
        capacity_units: int,
        initial_units: int = 0,
        unit_procurement_cost_yen: Optional[int] = None,
    ) -> FixtureInventorySlot:
        if slot_id in self._slots:
            raise ValueError(f"duplicate inventory slot id: {slot_id}")
        slot = FixtureInventorySlot(
            id=slot_id,
            fixture_id=fixture_id,
            product_id=product_id,
            capacity_units=capacity_units,
            units=initial_units,
            unit_procurement_cost_yen=unit_procurement_cost_yen,
        )
        self._slots[slot_id] = slot
        return slot

    def take_for_customer(self, slot_id: str, quantity: int = 1) -> InventoryMutation:
        mutation = self._slots[slot_id].take(quantity)
        self._history.append(mutation)
        return mutation

    def replenish(
        self,
        slot_id: str,
        quantity: int,
        *,
        staff_roster: Optional[StoreStaffRoster] = None,
        staff_id: Optional[str] = None,
        stamina_cost: Optional[int] = None,
        break_room_target_id: Optional[str] = None,
    ) -> InventoryMutation:
        if (staff_roster is None) != (staff_id is None):
            raise ValueError("staff_roster and staff_id must be supplied together")

        mutation = self._slots[slot_id].replenish(quantity)
        self._history.append(mutation)

        if staff_roster is not None and staff_id is not None:
            staff_roster.record_completed_work(
                staff_id,
                StaffTask.REPLENISH,
                stamina_cost=stamina_cost,
                break_room_target_id=break_room_target_id,
            )
        return mutation

    @property
    def known_procurement_total_yen(self) -> int:
        """Sum only replenishments whose procurement cost is known."""
        return sum(
            mutation.procurement_cost_yen
            for mutation in self._history
            if mutation.procurement_cost_yen is not None
        )

    @property
    def has_unknown_procurement_costs(self) -> bool:
        return any(
            mutation.quantity_delta > 0 and mutation.procurement_cost_yen is None
            for mutation in self._history
        )
