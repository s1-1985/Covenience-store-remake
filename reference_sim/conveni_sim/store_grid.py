from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Sequence

from .models import FixtureDefinition, StoreVariant


class PlacementError(ValueError):
    pass


class Direction(str, Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

    def rotated(self, quarter_turns_clockwise: int) -> "Direction":
        order = (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)
        return order[(order.index(self) + quarter_turns_clockwise) % 4]


@dataclass(frozen=True, order=True)
class GridPoint:
    x: int
    y: int


@dataclass(frozen=True)
class FixturePlacement:
    instance_id: str
    fixture_id: str
    origin: GridPoint
    width_subcells: int
    height_subcells: int
    interaction_side: Optional[Direction]
    blocks_pedestrian: bool = True

    @property
    def occupied_cells(self) -> frozenset[GridPoint]:
        return frozenset(
            GridPoint(self.origin.x + dx, self.origin.y + dy)
            for dy in range(self.height_subcells)
            for dx in range(self.width_subcells)
        )


class StoreGrid:
    """Engine-independent store grid with configurable sub-tile resolution.

    First-title research says 0.5-tile contact/gaps can materially affect
    interaction and congestion, but does not prove the original engine's
    internal cell size. The reference model therefore uses two subcells per
    tile by default while keeping the scale configurable.
    """

    def __init__(
        self,
        width_tiles: int,
        height_tiles: int,
        *,
        subcells_per_tile: int = 2,
        editable_cells: Optional[Iterable[GridPoint]] = None,
    ) -> None:
        if width_tiles <= 0 or height_tiles <= 0:
            raise ValueError("store dimensions must be positive")
        if subcells_per_tile <= 0:
            raise ValueError("subcells_per_tile must be positive")

        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.subcells_per_tile = subcells_per_tile
        self.width_subcells = width_tiles * subcells_per_tile
        self.height_subcells = height_tiles * subcells_per_tile

        if editable_cells is None:
            self._editable = frozenset(
                GridPoint(x, y)
                for y in range(self.height_subcells)
                for x in range(self.width_subcells)
            )
        else:
            editable = frozenset(editable_cells)
            if any(not self.in_bounds(cell) for cell in editable):
                raise ValueError("editable cell mask contains out-of-bounds cell")
            self._editable = editable

        self._static_blocked: set[GridPoint] = set()
        self._placements: dict[str, FixturePlacement] = {}

    @classmethod
    def from_store_variant(
        cls,
        variant: StoreVariant,
        *,
        subcells_per_tile: int = 2,
    ) -> "StoreGrid":
        if variant.editable_floor is None:
            raise ValueError(f"store variant {variant.id} has unknown editable floor")
        width_tiles, height_tiles = variant.editable_floor.value
        return cls(width_tiles, height_tiles, subcells_per_tile=subcells_per_tile)

    def in_bounds(self, point: GridPoint) -> bool:
        return 0 <= point.x < self.width_subcells and 0 <= point.y < self.height_subcells

    def is_editable(self, point: GridPoint) -> bool:
        return point in self._editable

    @property
    def placements(self) -> tuple[FixturePlacement, ...]:
        return tuple(self._placements.values())

    @property
    def blocked_cells(self) -> frozenset[GridPoint]:
        blocked = set(self._static_blocked)
        for placement in self._placements.values():
            if placement.blocks_pedestrian:
                blocked.update(placement.occupied_cells)
        return frozenset(blocked)

    def set_static_blocked(self, cells: Iterable[GridPoint], *, blocked: bool = True) -> None:
        cells = tuple(cells)
        if any(not self.in_bounds(cell) for cell in cells):
            raise ValueError("static obstacle contains out-of-bounds cell")
        if blocked:
            self._static_blocked.update(cells)
        else:
            self._static_blocked.difference_update(cells)

    def is_walkable(self, point: GridPoint) -> bool:
        return self.in_bounds(point) and point in self._editable and point not in self.blocked_cells

    def place_fixture(
        self,
        *,
        instance_id: str,
        fixture_id: str,
        origin_subcell: GridPoint,
        footprint_tiles: Sequence[int],
        rotation_quarter_turns: int = 0,
        interaction_side: Optional[Direction] = None,
        blocks_pedestrian: bool = True,
    ) -> FixturePlacement:
        if instance_id in self._placements:
            raise PlacementError(f"duplicate fixture instance id: {instance_id}")
        if len(footprint_tiles) != 2:
            raise ValueError("footprint_tiles must contain width and height")
        width_tiles, height_tiles = footprint_tiles
        if width_tiles <= 0 or height_tiles <= 0:
            raise ValueError("fixture footprint must be positive")

        turns = rotation_quarter_turns % 4
        if turns % 2:
            width_tiles, height_tiles = height_tiles, width_tiles

        placement = FixturePlacement(
            instance_id=instance_id,
            fixture_id=fixture_id,
            origin=origin_subcell,
            width_subcells=width_tiles * self.subcells_per_tile,
            height_subcells=height_tiles * self.subcells_per_tile,
            interaction_side=interaction_side.rotated(turns) if interaction_side else None,
            blocks_pedestrian=blocks_pedestrian,
        )

        occupied = placement.occupied_cells
        if any(not self.in_bounds(cell) or not self.is_editable(cell) for cell in occupied):
            raise PlacementError("fixture footprint is outside the editable store area")
        if occupied & self._static_blocked:
            raise PlacementError("fixture footprint overlaps a static obstacle")

        existing_occupied = set()
        for existing in self._placements.values():
            existing_occupied.update(existing.occupied_cells)
        if occupied & existing_occupied:
            raise PlacementError("fixture footprint overlaps an existing fixture")

        self._placements[instance_id] = placement
        return placement

    def place_definition(
        self,
        definition: FixtureDefinition,
        *,
        instance_id: str,
        origin_subcell: GridPoint,
        rotation_quarter_turns: int = 0,
        interaction_side: Optional[Direction] = None,
        blocks_pedestrian: Optional[bool] = None,
    ) -> FixturePlacement:
        if definition.footprint is None:
            raise PlacementError(f"fixture {definition.id} has unknown footprint")

        if blocks_pedestrian is None:
            if definition.blocks_pedestrian is None:
                blocks_pedestrian = True
            else:
                blocks_pedestrian = bool(definition.blocks_pedestrian.value)

        return self.place_fixture(
            instance_id=instance_id,
            fixture_id=definition.id,
            origin_subcell=origin_subcell,
            footprint_tiles=definition.footprint.value,
            rotation_quarter_turns=rotation_quarter_turns,
            interaction_side=interaction_side,
            blocks_pedestrian=blocks_pedestrian,
        )

    def remove_fixture(self, instance_id: str) -> FixturePlacement:
        try:
            return self._placements.pop(instance_id)
        except KeyError as exc:
            raise KeyError(f"unknown fixture instance id: {instance_id}") from exc

    def interaction_cells(self, instance_id: str) -> frozenset[GridPoint]:
        placement = self._placements[instance_id]
        side = placement.interaction_side
        if side is None:
            return frozenset()

        x0 = placement.origin.x
        y0 = placement.origin.y
        x1 = x0 + placement.width_subcells - 1
        y1 = y0 + placement.height_subcells - 1

        if side is Direction.NORTH:
            candidates = (GridPoint(x, y0 - 1) for x in range(x0, x1 + 1))
        elif side is Direction.SOUTH:
            candidates = (GridPoint(x, y1 + 1) for x in range(x0, x1 + 1))
        elif side is Direction.WEST:
            candidates = (GridPoint(x0 - 1, y) for y in range(y0, y1 + 1))
        else:
            candidates = (GridPoint(x1 + 1, y) for y in range(y0, y1 + 1))

        return frozenset(cell for cell in candidates if self.is_walkable(cell))

    def neighbors(self, point: GridPoint) -> tuple[GridPoint, ...]:
        candidates = (
            GridPoint(point.x, point.y - 1),
            GridPoint(point.x + 1, point.y),
            GridPoint(point.x, point.y + 1),
            GridPoint(point.x - 1, point.y),
        )
        return tuple(cell for cell in candidates if self.is_walkable(cell))

    def shortest_path(self, start: GridPoint, goal: GridPoint) -> Optional[tuple[GridPoint, ...]]:
        return self.shortest_path_to_any(start, (goal,))

    def shortest_path_to_any(
        self,
        start: GridPoint,
        goals: Iterable[GridPoint],
    ) -> Optional[tuple[GridPoint, ...]]:
        goals = frozenset(goal for goal in goals if self.is_walkable(goal))
        if not goals or not self.is_walkable(start):
            return None
        if start in goals:
            return (start,)

        queue = deque([start])
        previous: dict[GridPoint, Optional[GridPoint]] = {start: None}
        reached: Optional[GridPoint] = None

        while queue:
            current = queue.popleft()
            for nxt in self.neighbors(current):
                if nxt in previous:
                    continue
                previous[nxt] = current
                if nxt in goals:
                    reached = nxt
                    queue.clear()
                    break
                queue.append(nxt)

        if reached is None:
            return None

        path = []
        current: Optional[GridPoint] = reached
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return tuple(path)

    def shortest_path_to_fixture(
        self,
        start: GridPoint,
        instance_id: str,
    ) -> Optional[tuple[GridPoint, ...]]:
        return self.shortest_path_to_any(start, self.interaction_cells(instance_id))
