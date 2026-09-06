from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class VisitorMilestoneMoment:
    """Absolute game-day position for evidence-backed visitor milestone events.

    ``day_index`` is intentionally calendar-agnostic. The first-title evidence
    establishes a next-day 00:00 trigger, while the exact interaction with the
    representative-day/month-skip boundary is still unresolved.
    """

    day_index: int
    hour: int

    def __post_init__(self) -> None:
        if self.day_index < 1:
            raise ValueError("day_index must be >= 1")
        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be 0..23")


@dataclass
class ScheduledIdolOwnerEvent:
    threshold_visitors: int
    observed_total_visitors: int
    notified_at: VisitorMilestoneMoment
    trigger_at: VisitorMilestoneMoment
    popularity_gain: int = 100
    cost_yen: int = 0
    fired: bool = False

    @property
    def applies_to_current_player_stores(self) -> bool:
        """Targets are intentionally resolved at fire time, not reservation time."""
        return True


class ChainVisitorMilestoneRuntime:
    """Evidence-safe scheduler for the first-title idol one-day-owner event.

    First-title PS/SS research supports a free popularity +100 event every
    10,000 cumulative visitors across the player chain, firing at 00:00 on the
    day after the milestone notification. Research has not yet established
    whether merely crossing a threshold without observing the exact multiple
    must fire, nor how multiple thresholds crossed in one interval are queued.
    This runtime therefore schedules only explicitly observed exact multiples
    and refuses to invent catch-up events.
    """

    THRESHOLD_STEP = 10_000
    POPULARITY_GAIN = 100

    def __init__(self) -> None:
        self._events: list[ScheduledIdolOwnerEvent] = []
        self._last_observed_total = 0
        self._next_threshold = self.THRESHOLD_STEP

    @property
    def events(self) -> tuple[ScheduledIdolOwnerEvent, ...]:
        return tuple(self._events)

    @property
    def last_observed_total(self) -> int:
        return self._last_observed_total

    @property
    def next_threshold(self) -> int:
        return self._next_threshold

    def observe_total_visitors(
        self,
        total_visitors: int,
        *,
        notified_at: VisitorMilestoneMoment,
    ) -> ScheduledIdolOwnerEvent | None:
        if total_visitors < 0:
            raise ValueError("total_visitors must be >= 0")
        if total_visitors < self._last_observed_total:
            raise ValueError("chain cumulative visitors cannot decrease")

        if total_visitors > self._next_threshold:
            raise ValueError(
                "visitor threshold was crossed without an exact observed milestone; "
                "catch-up behavior is unresolved"
            )

        self._last_observed_total = total_visitors
        if total_visitors != self._next_threshold:
            return None

        event = ScheduledIdolOwnerEvent(
            threshold_visitors=self._next_threshold,
            observed_total_visitors=total_visitors,
            notified_at=notified_at,
            trigger_at=VisitorMilestoneMoment(notified_at.day_index + 1, 0),
            popularity_gain=self.POPULARITY_GAIN,
            cost_yen=0,
        )
        self._events.append(event)
        self._next_threshold += self.THRESHOLD_STEP
        return event

    def pop_due(self, now: VisitorMilestoneMoment) -> tuple[ScheduledIdolOwnerEvent, ...]:
        due: list[ScheduledIdolOwnerEvent] = []
        for event in self._events:
            if event.fired:
                continue
            if event.trigger_at <= now:
                event.fired = True
                due.append(event)
        return tuple(due)
