from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .clock import MonthBoundary, RepresentativeDayType, SimulationClock
from .economy import DayEndResult
from .operating_time import ClockAdvanceResult, MINUTES_PER_DAY
from .store_step import StoreStepOrchestrator, StoreStepResult
from .store_telemetry import StoreTelemetryRecorder, StoreTelemetrySnapshot


LAST_MINUTE_OF_DAY = MINUTES_PER_DAY - 1


@dataclass(frozen=True)
class RepresentativeDayRunResult:
    year: int
    month: int
    day: int
    day_type: RepresentativeDayType
    start_minute_of_day: int
    step_game_minutes: int
    steps: tuple[StoreStepResult, ...]
    start_snapshot: StoreTelemetrySnapshot
    step_snapshots: tuple[StoreTelemetrySnapshot, ...]
    end_of_day_snapshot: StoreTelemetrySnapshot
    boundary_snapshot: StoreTelemetrySnapshot
    day_end: DayEndResult
    boundary_clock: ClockAdvanceResult
    month_boundary: Optional[MonthBoundary]
    cash_before_yen: int
    cash_after_yen: int
    cash_is_exact_after: bool

    @property
    def simulated_game_minutes(self) -> int:
        return sum(
            step.clock.current_minute_of_day - step.clock.previous_minute_of_day
            for step in self.steps
        )


class RepresentativeDayRunner:
    """Run policy-driven store steps to day end without crossing inside a step.

    `StoreStepOrchestrator.step()` advances the clock before evaluating demand,
    traffic and work policies. Letting an ordinary step cross midnight would
    therefore evaluate next-day policy work before the previous day's ledger is
    closed. This runner deliberately stops normal steps at 23:59, closes the day,
    then advances the runtime clock by one boundary-only minute to 00:00.

    Factual telemetry is captured at the start, after every ordinary step, at
    23:59 before close, and after the 00:00 boundary. The recorder derives no
    formulas and mutates no policy state.

    The caller still supplies the ordinary step cadence. No wall-clock/game-time
    ratio or original policy coefficient is introduced here.
    """

    def __init__(
        self,
        orchestrator: StoreStepOrchestrator,
        calendar: SimulationClock,
        *,
        telemetry: Optional[StoreTelemetryRecorder] = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.runtime = orchestrator.runtime
        self.calendar = calendar
        self.telemetry = telemetry if telemetry is not None else StoreTelemetryRecorder()

    def run(self, *, step_game_minutes: int) -> RepresentativeDayRunResult:
        if step_game_minutes <= 0:
            raise ValueError("step_game_minutes must be > 0")

        start_year = self.calendar.year
        start_month = self.calendar.month
        start_day = self.calendar.day
        start_day_type = self.calendar.representative_day_type
        start_minute = self.runtime.subday_clock.minute_of_day
        start_snapshot = self.telemetry.snapshot(self.runtime)
        cash_before = start_snapshot.known_cash_yen

        steps: list[StoreStepResult] = []
        step_snapshots: list[StoreTelemetrySnapshot] = []
        while self.runtime.subday_clock.minute_of_day < LAST_MINUTE_OF_DAY:
            current = self.runtime.subday_clock.minute_of_day
            remaining = LAST_MINUTE_OF_DAY - current
            delta = min(step_game_minutes, remaining)
            result = self.orchestrator.step(delta)
            if result.clock.days_crossed:
                raise RuntimeError("ordinary representative-day step crossed midnight")
            steps.append(result)
            step_snapshots.append(self.telemetry.snapshot(self.runtime))

        end_of_day_snapshot = self.telemetry.snapshot(self.runtime)
        day_end = self.runtime.close_day()

        boundary = self.runtime.advance_game_minutes(1)
        if boundary.days_crossed != 1 or boundary.current_minute_of_day != 0:
            raise RuntimeError("representative-day boundary did not advance to next midnight")
        month_boundary = self.calendar.advance_day()
        boundary_snapshot = self.telemetry.snapshot(self.runtime)

        return RepresentativeDayRunResult(
            year=start_year,
            month=start_month,
            day=start_day,
            day_type=start_day_type,
            start_minute_of_day=start_minute,
            step_game_minutes=step_game_minutes,
            steps=tuple(steps),
            start_snapshot=start_snapshot,
            step_snapshots=tuple(step_snapshots),
            end_of_day_snapshot=end_of_day_snapshot,
            boundary_snapshot=boundary_snapshot,
            day_end=day_end,
            boundary_clock=boundary,
            month_boundary=month_boundary,
            cash_before_yen=cash_before,
            cash_after_yen=boundary_snapshot.known_cash_yen,
            cash_is_exact_after=boundary_snapshot.cash_is_exact,
        )
