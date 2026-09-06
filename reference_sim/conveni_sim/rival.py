from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RivalStoreRole(str, Enum):
    HEADQUARTERS = "headquarters"
    BRANCH = "branch"


class RivalStoreState(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ACQUIRED = "acquired"


class RivalChainState(str, Enum):
    ACTIVE = "active"
    EXTINCT = "extinct"


@dataclass(frozen=True)
class RivalStoreRecord:
    store_id: str
    role: RivalStoreRole
    location_id: str
    state: RivalStoreState
    opened_sequence: int
    closed_sequence: Optional[int] = None
    acquired_by: Optional[str] = None


@dataclass(frozen=True)
class RivalTransitionRecord:
    sequence: int
    store_id: str
    previous_state: Optional[RivalStoreState]
    new_state: RivalStoreState
    source: str
    location_id: str


class RivalChainRuntime:
    """Explicit first-title rival-chain state transition skeleton.

    First-title research confirms headquarters/branch distinction, branch
    acquisition, branch closures and later replacement openings at other
    locations. It does not yet recover the loss threshold, cash model,
    reopening delay, site-selection policy or acquisition-price formula.

    This runtime therefore never decides to close or open a store by itself.
    Callers must provide each observed or policy-produced transition explicitly.
    """

    def __init__(self, rival_id: str) -> None:
        if not rival_id:
            raise ValueError("rival_id must be non-empty")
        self.rival_id = rival_id
        self._stores: dict[str, RivalStoreRecord] = {}
        self._history: list[RivalTransitionRecord] = []
        self._next_sequence = 1

    @property
    def stores(self) -> tuple[RivalStoreRecord, ...]:
        return tuple(self._stores.values())

    @property
    def history(self) -> tuple[RivalTransitionRecord, ...]:
        return tuple(self._history)

    @property
    def active_stores(self) -> tuple[RivalStoreRecord, ...]:
        return tuple(store for store in self._stores.values() if store.state is RivalStoreState.ACTIVE)

    @property
    def state(self) -> RivalChainState:
        return RivalChainState.ACTIVE if self.active_stores else RivalChainState.EXTINCT

    def store(self, store_id: str) -> RivalStoreRecord:
        return self._stores[store_id]

    def _append_transition(
        self,
        *,
        store_id: str,
        previous_state: Optional[RivalStoreState],
        new_state: RivalStoreState,
        source: str,
        location_id: str,
    ) -> int:
        if not source:
            raise ValueError("transition source must be non-empty")
        sequence = self._next_sequence
        self._next_sequence += 1
        self._history.append(
            RivalTransitionRecord(
                sequence=sequence,
                store_id=store_id,
                previous_state=previous_state,
                new_state=new_state,
                source=source,
                location_id=location_id,
            )
        )
        return sequence

    def open_store(
        self,
        store_id: str,
        *,
        role: RivalStoreRole,
        location_id: str,
        source: str,
    ) -> RivalStoreRecord:
        """Record one explicit rival opening without choosing when/where to open."""
        if not store_id:
            raise ValueError("store_id must be non-empty")
        if not location_id:
            raise ValueError("location_id must be non-empty")
        if store_id in self._stores:
            raise ValueError(f"duplicate rival store id: {store_id}")
        if role is RivalStoreRole.HEADQUARTERS and any(
            store.role is RivalStoreRole.HEADQUARTERS
            for store in self._stores.values()
            if store.state is not RivalStoreState.ACQUIRED
        ):
            raise ValueError("rival chain already has a headquarters record")

        sequence = self._append_transition(
            store_id=store_id,
            previous_state=None,
            new_state=RivalStoreState.ACTIVE,
            source=source,
            location_id=location_id,
        )
        record = RivalStoreRecord(
            store_id=store_id,
            role=role,
            location_id=location_id,
            state=RivalStoreState.ACTIVE,
            opened_sequence=sequence,
        )
        self._stores[store_id] = record
        return record

    def close_store(self, store_id: str, *, source: str) -> RivalStoreRecord:
        """Record an externally decided closure; no loss threshold is inferred."""
        current = self._stores[store_id]
        if current.state is not RivalStoreState.ACTIVE:
            raise ValueError("only an active rival store can close")
        sequence = self._append_transition(
            store_id=store_id,
            previous_state=current.state,
            new_state=RivalStoreState.CLOSED,
            source=source,
            location_id=current.location_id,
        )
        updated = RivalStoreRecord(
            store_id=current.store_id,
            role=current.role,
            location_id=current.location_id,
            state=RivalStoreState.CLOSED,
            opened_sequence=current.opened_sequence,
            closed_sequence=sequence,
        )
        self._stores[store_id] = updated
        return updated

    def acquire_branch(
        self,
        store_id: str,
        *,
        acquired_by: str,
        source: str,
    ) -> RivalStoreRecord:
        """Record explicit branch acquisition; headquarters acquisition is rejected."""
        if not acquired_by:
            raise ValueError("acquired_by must be non-empty")
        current = self._stores[store_id]
        if current.role is RivalStoreRole.HEADQUARTERS:
            raise ValueError("first-title evidence does not allow headquarters acquisition")
        if current.state is not RivalStoreState.ACTIVE:
            raise ValueError("only an active rival branch can be acquired")
        sequence = self._append_transition(
            store_id=store_id,
            previous_state=current.state,
            new_state=RivalStoreState.ACQUIRED,
            source=source,
            location_id=current.location_id,
        )
        updated = RivalStoreRecord(
            store_id=current.store_id,
            role=current.role,
            location_id=current.location_id,
            state=RivalStoreState.ACQUIRED,
            opened_sequence=current.opened_sequence,
            closed_sequence=sequence,
            acquired_by=acquired_by,
        )
        self._stores[store_id] = updated
        return updated
