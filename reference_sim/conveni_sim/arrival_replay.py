from __future__ import annotations

from dataclasses import dataclass

from .arrival_schedule import ExplicitArrivalSchedule, ScheduledCustomerArrival
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class ArrivalReplayResult:
    arrivals: tuple[ScheduledCustomerArrival, ...]
    spawned_customer_ids: tuple[str, ...]


class ObservedArrivalReplayer:
    """Feeds observed/manual arrivals into StoreRuntimeHarness at game time.

    This layer deliberately contains no spawn probability, customer-share
    formula, weather multiplier, or time-of-day demand curve.
    """

    def __init__(self, runtime: StoreRuntimeHarness, schedule: ExplicitArrivalSchedule) -> None:
        self.runtime = runtime
        self.schedule = schedule

    def emit_due(self) -> ArrivalReplayResult:
        arrivals = self.schedule.pop_due(self.runtime.subday_clock)
        spawned: list[str] = []
        for arrival in arrivals:
            self.runtime.add_customer(
                arrival.customer_id,
                entry_point=arrival.entry_point,
                exit_point=arrival.exit_point,
                merchandise_fixture_ids=arrival.merchandise_fixture_ids,
                checkout_fixture_id=arrival.checkout_fixture_id,
            )
            spawned.append(arrival.customer_id)
        return ArrivalReplayResult(arrivals=arrivals, spawned_customer_ids=tuple(spawned))
