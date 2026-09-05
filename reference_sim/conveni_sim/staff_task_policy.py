from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Protocol, Sequence

from .staff import StaffCondition, StaffTask, StoreStaffRoster, WORK_TASKS


@dataclass(frozen=True)
class StaffTaskCandidate:
    """Caller-supplied work candidate without an invented priority score."""

    task: StaffTask
    target_id: Optional[str] = None
    reason: str = ""

    def __post_init__(self) -> None:
        if self.task not in WORK_TASKS:
            raise ValueError("staff task candidates must be checkout/replenish/clean work")


@dataclass(frozen=True)
class StaffTaskDecision:
    task: StaffTask
    target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.task not in WORK_TASKS:
            raise ValueError("staff task decisions must be checkout/replenish/clean work")


@dataclass(frozen=True)
class StaffTaskDecisionContext:
    staff_id: str
    current_task: StaffTask
    current_target_id: Optional[str]
    candidates: tuple[StaffTaskCandidate, ...]


class StaffTaskPolicy(Protocol):
    """Replaceable first-title staff task selector.

    Research supports independent staff choices and observable register gaps, but
    does not yet recover the original priority formula. A policy therefore gets
    explicit candidates and may choose one or return no decision.
    """

    def choose_task(
        self,
        context: StaffTaskDecisionContext,
    ) -> Optional[StaffTaskDecision]: ...


@dataclass(frozen=True)
class AppliedStaffTaskDecision:
    staff_id: str
    decision: StaffTaskDecision


@dataclass(frozen=True)
class StaffTaskPolicyApplication:
    applied: tuple[AppliedStaffTaskDecision, ...]
    unavailable_staff_ids: tuple[str, ...]
    no_decision_staff_ids: tuple[str, ...]


class ScriptedStaffTaskPolicy:
    """Deterministic observation/test policy; not an original-game AI claim."""

    def __init__(self, decisions: Mapping[str, StaffTaskDecision]) -> None:
        self._decisions = dict(decisions)

    def choose_task(
        self,
        context: StaffTaskDecisionContext,
    ) -> Optional[StaffTaskDecision]:
        return self._decisions.get(context.staff_id)


class StaffTaskPolicyCoordinator:
    """Ask a policy for each staff member independently and apply valid choices.

    Candidate discovery remains outside this layer. This avoids silently
    deciding when inventory is 'low enough', how urgent a queue is, or how dirt
    competes with checkout work. Multiple staff may choose the same target; the
    first-title evidence does not justify a global optimizer that guarantees
    perfect coverage or deduplicates independent decisions.

    Callers may also lock staff who are inside an externally managed work
    lifecycle (for example an active checkout service). A lock is not an
    original-AI priority claim; it only prevents the generic task selector from
    silently overwriting an in-progress state machine.
    """

    def __init__(self, roster: StoreStaffRoster) -> None:
        self.roster = roster

    @staticmethod
    def _matches_candidate(
        decision: StaffTaskDecision,
        candidates: Sequence[StaffTaskCandidate],
    ) -> bool:
        return any(
            candidate.task is decision.task and candidate.target_id == decision.target_id
            for candidate in candidates
        )

    def apply_policy(
        self,
        policy: StaffTaskPolicy,
        candidates_by_staff: Mapping[str, Sequence[StaffTaskCandidate]],
        *,
        locked_staff_ids: Iterable[str] = (),
    ) -> StaffTaskPolicyApplication:
        applied: list[AppliedStaffTaskDecision] = []
        unavailable: list[str] = []
        no_decision: list[str] = []
        locked = set(locked_staff_ids)

        for state in self.roster.staff:
            candidates = tuple(candidates_by_staff.get(state.id, ()))
            if state.id in locked or state.condition is not StaffCondition.AVAILABLE:
                unavailable.append(state.id)
                continue

            context = StaffTaskDecisionContext(
                staff_id=state.id,
                current_task=state.task,
                current_target_id=state.target_id,
                candidates=candidates,
            )
            decision = policy.choose_task(context)
            if decision is None:
                no_decision.append(state.id)
                continue
            if not self._matches_candidate(decision, candidates):
                raise ValueError(
                    f"policy selected a task that is not a supplied candidate for {state.id}"
                )

            self.roster.assign_task(
                state.id,
                decision.task,
                target_id=decision.target_id,
            )
            applied.append(AppliedStaffTaskDecision(state.id, decision))

        return StaffTaskPolicyApplication(
            applied=tuple(applied),
            unavailable_staff_ids=tuple(unavailable),
            no_decision_staff_ids=tuple(no_decision),
        )
