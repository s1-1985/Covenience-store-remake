from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .customer import CustomerState
from .representative_day_runner import RepresentativeDayRunResult
from .store_runtime import CustomerAdmissionStatus


@dataclass(frozen=True)
class StaffDayMetrics:
    staff_id: str
    minimum_stamina: Optional[int]
    ending_stamina: Optional[int]


@dataclass(frozen=True)
class InventoryDayMetrics:
    slot_id: str
    ending_units: int
    capacity_units: int


@dataclass(frozen=True)
class RepresentativeDayMetrics:
    attempted_arrivals: int
    admitted_arrivals: int
    store_closed_rejections: int
    open_state_unknown_rejections: int
    completed_checkout_sales: int
    checkout_anger_events: int
    known_checkout_revenue_yen: int
    checkout_revenue_is_exact: bool
    peak_waiting_checkout_customers: int
    peak_active_checkout_services: int
    total_customer_sessions: int
    exited_customers: int
    ejected_customers: int
    unreachable_customers: int
    known_cash_delta_yen: int
    cash_is_exact_after: bool
    day_known_credits_yen: int
    day_known_debits_yen: int
    staff: tuple[StaffDayMetrics, ...]
    inventory: tuple[InventoryDayMetrics, ...]


@dataclass(frozen=True)
class ObservedStaffMinimum:
    staff_id: str
    minimum_stamina: int


@dataclass(frozen=True)
class ObservedInventoryEnding:
    slot_id: str
    ending_units: int


@dataclass(frozen=True)
class ObservedRepresentativeDayMetrics:
    """Optional observation-side targets; None means not observed."""

    attempted_arrivals: Optional[int] = None
    admitted_arrivals: Optional[int] = None
    completed_checkout_sales: Optional[int] = None
    checkout_anger_events: Optional[int] = None
    known_checkout_revenue_yen: Optional[int] = None
    peak_waiting_checkout_customers: Optional[int] = None
    peak_active_checkout_services: Optional[int] = None
    total_customer_sessions: Optional[int] = None
    exited_customers: Optional[int] = None
    known_cash_delta_yen: Optional[int] = None
    staff_minimums: tuple[ObservedStaffMinimum, ...] = ()
    inventory_endings: tuple[ObservedInventoryEnding, ...] = ()


@dataclass(frozen=True)
class RepresentativeDayMetricDelta:
    metric: str
    simulated_value: Optional[int]
    observed_value: int
    delta: Optional[int]


@dataclass(frozen=True)
class RepresentativeDayComparison:
    metrics: RepresentativeDayMetrics
    observed: ObservedRepresentativeDayMetrics
    deltas: tuple[RepresentativeDayMetricDelta, ...]


def derive_representative_day_metrics(
    run: RepresentativeDayRunResult,
) -> RepresentativeDayMetrics:
    """Reduce one run into factual counters/extrema without fitting game rules."""

    attempted_arrivals = 0
    admitted_arrivals = 0
    store_closed_rejections = 0
    open_state_unknown_rejections = 0
    completed_checkout_sales = 0
    checkout_anger_events = 0
    known_checkout_revenue_yen = 0
    checkout_revenue_is_exact = True

    for step in run.steps:
        if step.demand is not None:
            attempted_arrivals += len(step.demand.intents)
            for admission in step.demand.admissions:
                if admission.status is CustomerAdmissionStatus.ADMITTED:
                    admitted_arrivals += 1
                elif admission.status is CustomerAdmissionStatus.STORE_CLOSED:
                    store_closed_rejections += 1
                elif admission.status is CustomerAdmissionStatus.OPEN_STATE_UNKNOWN:
                    open_state_unknown_rejections += 1

        checkout_anger_events += sum(
            1 for evaluation in step.checkout_anger_timing if evaluation.triggered
        )

        for checkout in step.checkout_timing:
            if not checkout.completed or checkout.sale is None:
                continue
            completed_checkout_sales += 1
            settlement = checkout.sale.settlement
            known_checkout_revenue_yen += settlement.known_revenue_yen
            if settlement.exact_total_yen is None:
                checkout_revenue_is_exact = False

    snapshots = (
        run.start_snapshot,
        *run.step_snapshots,
        run.end_of_day_snapshot,
        run.boundary_snapshot,
    )
    peak_waiting = max(snapshot.waiting_checkout_customers for snapshot in snapshots)
    peak_active = max(snapshot.active_checkout_services for snapshot in snapshots)
    total_sessions = max(snapshot.total_customer_sessions for snapshot in snapshots)

    end = run.end_of_day_snapshot
    exited = end.customer_count(CustomerState.EXITED)
    ejected = end.customer_count(CustomerState.EJECTED)
    unreachable = end.customer_count(CustomerState.UNREACHABLE)

    staff_ids = tuple(staff.staff_id for staff in run.boundary_snapshot.staff)
    staff_metrics: list[StaffDayMetrics] = []
    for staff_id in staff_ids:
        values: list[int] = []
        ending: Optional[int] = None
        for snapshot in snapshots:
            staff = next(item for item in snapshot.staff if item.staff_id == staff_id)
            if staff.stamina_current is not None:
                values.append(staff.stamina_current)
            if snapshot is run.boundary_snapshot:
                ending = staff.stamina_current
        staff_metrics.append(
            StaffDayMetrics(
                staff_id=staff_id,
                minimum_stamina=min(values) if values else None,
                ending_stamina=ending,
            )
        )

    inventory_metrics = tuple(
        InventoryDayMetrics(
            slot_id=item.slot_id,
            ending_units=item.units,
            capacity_units=item.capacity_units,
        )
        for item in run.end_of_day_snapshot.inventory
    )

    return RepresentativeDayMetrics(
        attempted_arrivals=attempted_arrivals,
        admitted_arrivals=admitted_arrivals,
        store_closed_rejections=store_closed_rejections,
        open_state_unknown_rejections=open_state_unknown_rejections,
        completed_checkout_sales=completed_checkout_sales,
        checkout_anger_events=checkout_anger_events,
        known_checkout_revenue_yen=known_checkout_revenue_yen,
        checkout_revenue_is_exact=checkout_revenue_is_exact,
        peak_waiting_checkout_customers=peak_waiting,
        peak_active_checkout_services=peak_active,
        total_customer_sessions=total_sessions,
        exited_customers=exited,
        ejected_customers=ejected,
        unreachable_customers=unreachable,
        known_cash_delta_yen=run.cash_after_yen - run.cash_before_yen,
        cash_is_exact_after=run.cash_is_exact_after,
        day_known_credits_yen=run.day_end.summary.known_credits_yen,
        day_known_debits_yen=run.day_end.summary.known_debits_yen,
        staff=tuple(staff_metrics),
        inventory=inventory_metrics,
    )


def compare_representative_day_metrics(
    metrics: RepresentativeDayMetrics,
    observed: ObservedRepresentativeDayMetrics,
) -> RepresentativeDayComparison:
    """Subtract only explicitly supplied observation targets from simulation."""

    deltas: list[RepresentativeDayMetricDelta] = []

    scalar_fields = (
        "attempted_arrivals",
        "admitted_arrivals",
        "completed_checkout_sales",
        "checkout_anger_events",
        "known_checkout_revenue_yen",
        "peak_waiting_checkout_customers",
        "peak_active_checkout_services",
        "total_customer_sessions",
        "exited_customers",
        "known_cash_delta_yen",
    )
    for field in scalar_fields:
        observed_value = getattr(observed, field)
        if observed_value is None:
            continue
        simulated_value = getattr(metrics, field)
        deltas.append(
            RepresentativeDayMetricDelta(
                metric=field,
                simulated_value=simulated_value,
                observed_value=observed_value,
                delta=simulated_value - observed_value,
            )
        )

    staff_by_id = {item.staff_id: item for item in metrics.staff}
    for target in observed.staff_minimums:
        simulated = staff_by_id.get(target.staff_id)
        simulated_value = simulated.minimum_stamina if simulated is not None else None
        deltas.append(
            RepresentativeDayMetricDelta(
                metric=f"staff:{target.staff_id}:minimum_stamina",
                simulated_value=simulated_value,
                observed_value=target.minimum_stamina,
                delta=(
                    simulated_value - target.minimum_stamina
                    if simulated_value is not None
                    else None
                ),
            )
        )

    inventory_by_id = {item.slot_id: item for item in metrics.inventory}
    for target in observed.inventory_endings:
        simulated = inventory_by_id.get(target.slot_id)
        simulated_value = simulated.ending_units if simulated is not None else None
        deltas.append(
            RepresentativeDayMetricDelta(
                metric=f"inventory:{target.slot_id}:ending_units",
                simulated_value=simulated_value,
                observed_value=target.ending_units,
                delta=(
                    simulated_value - target.ending_units
                    if simulated_value is not None
                    else None
                ),
            )
        )

    return RepresentativeDayComparison(metrics, observed, tuple(deltas))
