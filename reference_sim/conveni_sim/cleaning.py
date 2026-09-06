from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .staff import StaffTask, StoreStaffRoster
from .store_grid import GridPoint, StoreGrid


@dataclass(frozen=True)
class DirtGenerationPolicy:
    """Optional platform/observation policy; default makes no suppression claim."""

    suppress_at_cleaning_value_or_above: Optional[int] = None

    def __post_init__(self) -> None:
        if (
            self.suppress_at_cleaning_value_or_above is not None
            and self.suppress_at_cleaning_value_or_above < 0
        ):
            raise ValueError("cleaning suppression threshold must be >= 0 or None")


@dataclass(frozen=True)
class InteriorEditDirtResetPolicy:
    """Explicit compatibility opt-in for the observed closed-store reset quirk."""

    clear_floor_dirt_when_closed: bool = False


@dataclass(frozen=True)
class CleaningActionResult:
    staff_id: Optional[str]
    requested_cells: tuple[GridPoint, ...]
    cleaned_cells: tuple[GridPoint, ...]
    dirty_cells_remaining: int


@dataclass(frozen=True)
class InteriorEditDirtResetResult:
    is_closed_for_business: bool
    policy_enabled: bool
    cleared_cells: tuple[GridPoint, ...]
    dirty_cells_remaining: int

    @property
    def reset_applied(self) -> bool:
        return self.policy_enabled and self.is_closed_for_business


class StoreCleaningRuntime:
    """Explicit dirt/cleaning event ledger without a guessed dirt spawn rate."""

    def __init__(
        self,
        grid: StoreGrid,
        *,
        dirt_policy: DirtGenerationPolicy = DirtGenerationPolicy(),
        interior_edit_policy: InteriorEditDirtResetPolicy = InteriorEditDirtResetPolicy(),
    ) -> None:
        self.grid = grid
        self.dirt_policy = dirt_policy
        self.interior_edit_policy = interior_edit_policy
        self._dirty: set[GridPoint] = set()
        self._history: list[CleaningActionResult] = []
        self._interior_edit_history: list[InteriorEditDirtResetResult] = []

    @property
    def dirty_cells(self) -> frozenset[GridPoint]:
        return frozenset(self._dirty)

    @property
    def history(self) -> tuple[CleaningActionResult, ...]:
        return tuple(self._history)

    @property
    def interior_edit_history(self) -> tuple[InteriorEditDirtResetResult, ...]:
        return tuple(self._interior_edit_history)

    def mark_dirty(
        self,
        cells: Iterable[GridPoint],
        *,
        store_cleaning_value: Optional[int] = None,
    ) -> tuple[GridPoint, ...]:
        cells = tuple(cells)
        if any(not self.grid.in_bounds(cell) for cell in cells):
            raise ValueError("dirt cell is outside store grid")
        if any(not self.grid.is_editable(cell) for cell in cells):
            raise ValueError("dirt cell is outside editable store area")

        threshold = self.dirt_policy.suppress_at_cleaning_value_or_above
        if threshold is not None:
            if store_cleaning_value is None:
                raise ValueError("configured dirt suppression requires store_cleaning_value")
            if store_cleaning_value >= threshold:
                return ()

        added: list[GridPoint] = []
        for cell in cells:
            if cell not in self._dirty:
                self._dirty.add(cell)
                added.append(cell)
        return tuple(added)

    def enter_interior_edit(
        self,
        *,
        is_closed_for_business: bool,
    ) -> InteriorEditDirtResetResult:
        """Record interior-edit entry without inferring cleanliness-value side effects.

        The first-title observation is kept behind an explicit compatibility policy
        because exact platform coverage and the internal trigger timing remain
        unresolved. Applying the reset clears only floor-dirt cells; it does not
        record staff cleaning work or mutate any external cleanliness parameter.
        """

        enabled = self.interior_edit_policy.clear_floor_dirt_when_closed
        cleared: tuple[GridPoint, ...] = ()
        if enabled and is_closed_for_business:
            cleared = tuple(sorted(self._dirty))
            self._dirty.clear()

        result = InteriorEditDirtResetResult(
            is_closed_for_business=is_closed_for_business,
            policy_enabled=enabled,
            cleared_cells=cleared,
            dirty_cells_remaining=len(self._dirty),
        )
        self._interior_edit_history.append(result)
        return result

    def clean(
        self,
        cells: Iterable[GridPoint],
        *,
        staff_roster: Optional[StoreStaffRoster] = None,
        staff_id: Optional[str] = None,
        stamina_cost: Optional[int] = None,
        break_room_target_id: Optional[str] = None,
    ) -> CleaningActionResult:
        if (staff_roster is None) != (staff_id is None):
            raise ValueError("staff_roster and staff_id must be supplied together")

        requested = tuple(cells)
        if any(not self.grid.in_bounds(cell) for cell in requested):
            raise ValueError("cleaning cell is outside store grid")

        cleaned = tuple(cell for cell in requested if cell in self._dirty)
        self._dirty.difference_update(cleaned)

        if staff_roster is not None and staff_id is not None and cleaned:
            # One explicit `clean()` invocation represents one completed floor-
            # cleaning work action. We do not assume one skill event per cell.
            staff_roster.record_completed_work(
                staff_id,
                StaffTask.CLEAN,
                stamina_cost=stamina_cost,
                break_room_target_id=break_room_target_id,
            )

        result = CleaningActionResult(
            staff_id=staff_id,
            requested_cells=requested,
            cleaned_cells=cleaned,
            dirty_cells_remaining=len(self._dirty),
        )
        self._history.append(result)
        return result
