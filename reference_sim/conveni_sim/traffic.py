from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

from .store_grid import GridPoint, StoreGrid


class AgentStatus(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    BLOCKED = "blocked"
    ARRIVED = "arrived"
    UNREACHABLE = "unreachable"


@dataclass(frozen=True)
class CongestionPolicy:
    """Configurable harness policy, not an original-game constant."""

    reroute_after_blocked_ticks: Optional[int] = None

    def __post_init__(self) -> None:
        if self.reroute_after_blocked_ticks is not None and self.reroute_after_blocked_ticks < 1:
            raise ValueError("reroute_after_blocked_ticks must be >= 1 or None")


@dataclass
class TrafficAgent:
    id: str
    position: GridPoint
    status: AgentStatus = AgentStatus.IDLE
    path: tuple[GridPoint, ...] = ()
    target_point: Optional[GridPoint] = None
    target_fixture_id: Optional[str] = None
    blocked_ticks: int = 0
    total_wait_ticks: int = 0
    total_steps: int = 0


@dataclass(frozen=True)
class TrafficTickResult:
    moved: tuple[str, ...]
    blocked: tuple[str, ...]
    arrived: tuple[str, ...]
    unreachable: tuple[str, ...]


class DynamicTrafficHarness:
    """Minimal dynamic-occupancy harness for congestion experiments.

    One harness tick and one subcell step are implementation units only. They
    are intentionally not mapped to an original frame/second or movement speed.
    """

    def __init__(
        self,
        grid: StoreGrid,
        *,
        policy: CongestionPolicy = CongestionPolicy(),
    ) -> None:
        self.grid = grid
        self.policy = policy
        self._agents: dict[str, TrafficAgent] = {}

    @property
    def agents(self) -> tuple[TrafficAgent, ...]:
        return tuple(self._agents.values())

    def agent(self, agent_id: str) -> TrafficAgent:
        return self._agents[agent_id]

    def add_agent(self, agent_id: str, position: GridPoint) -> TrafficAgent:
        if agent_id in self._agents:
            raise ValueError(f"duplicate agent id: {agent_id}")
        if not self.grid.is_walkable(position):
            raise ValueError("agent start position must be walkable")
        if any(agent.position == position for agent in self._agents.values()):
            raise ValueError("agent start position is already occupied")
        agent = TrafficAgent(agent_id, position)
        self._agents[agent_id] = agent
        return agent

    def remove_agent(self, agent_id: str) -> TrafficAgent:
        return self._agents.pop(agent_id)

    def occupied_cells(self, *, except_agent_id: Optional[str] = None) -> frozenset[GridPoint]:
        return frozenset(
            agent.position
            for agent in self._agents.values()
            if agent.id != except_agent_id
        )

    def agent_at(self, point: GridPoint) -> Optional[TrafficAgent]:
        for agent in self._agents.values():
            if agent.position == point:
                return agent
        return None

    def set_point_goal(self, agent_id: str, goal: GridPoint) -> TrafficAgent:
        agent = self._agents[agent_id]
        agent.target_point = goal
        agent.target_fixture_id = None
        self._replan(agent)
        return agent

    def set_fixture_goal(self, agent_id: str, fixture_id: str) -> TrafficAgent:
        agent = self._agents[agent_id]
        agent.target_point = None
        agent.target_fixture_id = fixture_id
        self._replan(agent)
        return agent

    def _target_cells(self, agent: TrafficAgent) -> frozenset[GridPoint]:
        if agent.target_point is not None:
            return frozenset({agent.target_point})
        if agent.target_fixture_id is not None:
            return self.grid.interaction_cells(agent.target_fixture_id)
        return frozenset()

    def _replan(self, agent: TrafficAgent) -> None:
        targets = self._target_cells(agent)
        path = self._shortest_path_avoiding_agents(
            agent.position,
            targets,
            except_agent_id=agent.id,
        )
        agent.blocked_ticks = 0
        if path is None:
            agent.path = ()
            agent.status = AgentStatus.UNREACHABLE
            return
        agent.path = path
        if len(path) == 1:
            agent.status = AgentStatus.ARRIVED
        else:
            agent.status = AgentStatus.MOVING

    def _dynamic_clear_path(
        self,
        start: GridPoint,
        goals: frozenset[GridPoint],
        occupied: frozenset[GridPoint],
    ) -> Optional[tuple[GridPoint, ...]]:
        if not goals:
            return None

        queue = deque([start])
        previous: dict[GridPoint, Optional[GridPoint]] = {start: None}
        reached: Optional[GridPoint] = None

        while queue:
            current = queue.popleft()
            for nxt in self.grid.neighbors(current):
                if nxt in previous or nxt in occupied:
                    continue
                previous[nxt] = current
                if nxt in goals:
                    reached = nxt
                    queue.clear()
                    break
                queue.append(nxt)

        if reached is None:
            return None

        reverse_path = []
        current: Optional[GridPoint] = reached
        while current is not None:
            reverse_path.append(current)
            current = previous[current]
        reverse_path.reverse()
        return tuple(reverse_path)

    def _shortest_path_avoiding_agents(
        self,
        start: GridPoint,
        goals: Iterable[GridPoint],
        *,
        except_agent_id: Optional[str] = None,
    ) -> Optional[tuple[GridPoint, ...]]:
        walkable_goals = frozenset(goal for goal in goals if self.grid.is_walkable(goal))
        if not walkable_goals or not self.grid.is_walkable(start):
            return None
        if start in walkable_goals:
            return (start,)

        occupied = self.occupied_cells(except_agent_id=except_agent_id)
        free_goals = walkable_goals - occupied

        # Prefer a route that is clear of current dynamic occupancy. This lets
        # an agent naturally choose another interaction point or detour when one
        # exists without inventing a timing rule.
        dynamic_path = self._dynamic_clear_path(start, free_goals, occupied)
        if dynamic_path is not None:
            return dynamic_path

        # If the static layout itself is reachable but all routes are currently
        # obstructed by agents, preserve that static path. The next tick then
        # produces BLOCKED/waiting rather than incorrectly classifying a
        # temporary crowd as an impossible layout.
        return self.grid.shortest_path_to_any(start, walkable_goals)

    def tick(self) -> TrafficTickResult:
        moved: list[str] = []
        blocked: list[str] = []
        arrived: list[str] = []
        unreachable: list[str] = []

        moving_agents = [
            agent
            for agent in self._agents.values()
            if agent.status in (AgentStatus.MOVING, AgentStatus.BLOCKED)
        ]

        desired: dict[str, GridPoint] = {}
        for agent in moving_agents:
            if len(agent.path) < 2:
                self._replan(agent)
            if agent.status is AgentStatus.UNREACHABLE:
                unreachable.append(agent.id)
                continue
            if agent.status is AgentStatus.ARRIVED:
                arrived.append(agent.id)
                continue
            desired[agent.id] = agent.path[1]

        start_occupancy = {agent.position: agent.id for agent in self._agents.values()}
        contenders: dict[GridPoint, list[str]] = {}
        for agent_id, point in desired.items():
            contenders.setdefault(point, []).append(agent_id)

        can_move: set[str] = set()
        for agent_id, point in desired.items():
            conflict = len(contenders[point]) > 1
            occupied_by = start_occupancy.get(point)
            occupied = occupied_by is not None and occupied_by != agent_id
            if not conflict and not occupied and self.grid.is_walkable(point):
                can_move.add(agent_id)

        for agent in moving_agents:
            if agent.id not in desired:
                continue
            if agent.id in can_move:
                agent.position = desired[agent.id]
                agent.path = agent.path[1:]
                agent.blocked_ticks = 0
                agent.total_steps += 1
                moved.append(agent.id)
                if len(agent.path) == 1:
                    agent.status = AgentStatus.ARRIVED
                    arrived.append(agent.id)
                else:
                    agent.status = AgentStatus.MOVING
                continue

            agent.status = AgentStatus.BLOCKED
            agent.blocked_ticks += 1
            agent.total_wait_ticks += 1
            blocked.append(agent.id)

        threshold = self.policy.reroute_after_blocked_ticks
        if threshold is not None:
            for agent in moving_agents:
                if agent.status is AgentStatus.BLOCKED and agent.blocked_ticks >= threshold:
                    self._replan(agent)
                    if agent.status is AgentStatus.UNREACHABLE and agent.id not in unreachable:
                        unreachable.append(agent.id)
                    elif agent.status is AgentStatus.ARRIVED and agent.id not in arrived:
                        arrived.append(agent.id)

        return TrafficTickResult(
            moved=tuple(moved),
            blocked=tuple(blocked),
            arrived=tuple(arrived),
            unreachable=tuple(unreachable),
        )
