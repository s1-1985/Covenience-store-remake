from __future__ import annotations

from dataclasses import dataclass

from .customer import CustomerState
from .observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from .representative_day_runner import RepresentativeDayRunResult
from .staff import StaffTask
from .store_runtime import CustomerAdmissionStatus, StoreRuntimeHarness


@dataclass(frozen=True)
class SimulationObservationExportOptions:
    include_staff_work: bool = True
    include_stamina_snapshots: bool = False
    include_clock_samples: bool = False


class RepresentativeDayObservationExporter:
    """Project a completed reference run onto the video-observation vocabulary.

    The exporter does not create new gameplay events. It re-expresses events
    already present in `StoreStepResult` plus aligned telemetry snapshots. Event
    timestamps therefore have the same game-minute granularity as the caller's
    store-step cadence; no sub-step ordering time or video-time mapping is
    invented.
    """

    def export(
        self,
        run: RepresentativeDayRunResult,
        runtime: StoreRuntimeHarness,
        *,
        source_id: str = "reference-simulation",
        options: SimulationObservationExportOptions = SimulationObservationExportOptions(),
    ) -> GameplayObservationTimeline:
        if len(run.steps) != len(run.step_snapshots):
            raise ValueError("representative-day steps and telemetry snapshots are not aligned")

        timeline = GameplayObservationTimeline(source_id)
        for step, snapshot in zip(run.steps, run.step_snapshots):
            timestamp = GameTimestamp(
                run.year,
                run.month,
                run.day,
                step.clock.current_minute_of_day,
            )

            # These evaluations occur before checkout settlement in StoreStepOrchestrator.
            for evaluation in step.checkout_anger_timing:
                if not evaluation.triggered:
                    continue
                context = evaluation.context
                timeline.add(
                    ObservationKind.CHECKOUT_ANGER,
                    timestamp,
                    customer_id=context.customer_id,
                    staff_id=context.active_staff_id,
                    fixture_id=context.checkout_fixture_id,
                    note="reference runtime checkout anger trigger",
                )

            for evaluation in step.checkout_timing:
                if not evaluation.completed:
                    continue
                context = evaluation.context
                timeline.add(
                    ObservationKind.CHECKOUT_SERVICE_END,
                    timestamp,
                    customer_id=context.customer_id,
                    staff_id=context.staff_id,
                    fixture_id=context.checkout_fixture_id,
                    note="reference runtime checkout completion",
                )

            if options.include_staff_work:
                for evaluation in step.staff_work_timing:
                    if not evaluation.completed:
                        continue
                    context = evaluation.context
                    if context.task is StaffTask.REPLENISH:
                        fixture_id = runtime.inventory.slot(context.target_id).fixture_id
                        kind = ObservationKind.REPLENISH_END
                        note = f"slot:{context.target_id}"
                    elif context.task is StaffTask.CLEAN:
                        fixture_id = None
                        kind = ObservationKind.CLEAN_END
                        note = context.target_id
                    else:
                        continue
                    timeline.add(
                        kind,
                        timestamp,
                        staff_id=context.staff_id,
                        fixture_id=fixture_id,
                        note=note,
                    )

            if step.demand is not None:
                for admission in step.demand.admissions:
                    if admission.status is not CustomerAdmissionStatus.ADMITTED:
                        continue
                    timeline.add(
                        ObservationKind.CUSTOMER_ARRIVAL,
                        timestamp,
                        customer_id=admission.customer_id,
                        note="reference runtime admitted customer",
                    )

            for customer_id, state in step.traffic.state_changes:
                if state is not CustomerState.WAITING_CHECKOUT:
                    continue
                session = runtime.customers.customer(customer_id)
                timeline.add(
                    ObservationKind.CHECKOUT_QUEUE_ENTER,
                    timestamp,
                    customer_id=customer_id,
                    fixture_id=session.checkout_fixture_id,
                    note="reference runtime customer reached checkout",
                )

            if options.include_staff_work:
                for evaluation in step.staff_work_interruptions:
                    if not evaluation.interrupted:
                        continue
                    work = evaluation.context.work
                    if work.task is StaffTask.REPLENISH:
                        fixture_id = runtime.inventory.slot(work.target_id).fixture_id
                        kind = ObservationKind.REPLENISH_INTERRUPT
                        note = f"slot:{work.target_id}"
                    elif work.task is StaffTask.CLEAN:
                        fixture_id = None
                        kind = ObservationKind.CLEAN_INTERRUPT
                        note = work.target_id
                    else:
                        continue
                    timeline.add(
                        kind,
                        timestamp,
                        staff_id=work.staff_id,
                        fixture_id=fixture_id,
                        note=note,
                    )

            if options.include_staff_work and step.staff_tasks is not None:
                for applied in step.staff_tasks.applied:
                    decision = applied.decision
                    if decision.task is StaffTask.REPLENISH and decision.target_id is not None:
                        timeline.add(
                            ObservationKind.REPLENISH_START,
                            timestamp,
                            staff_id=applied.staff_id,
                            fixture_id=runtime.inventory.slot(decision.target_id).fixture_id,
                            note=f"slot:{decision.target_id}",
                        )
                    elif decision.task is StaffTask.CLEAN and decision.target_id is not None:
                        timeline.add(
                            ObservationKind.CLEAN_START,
                            timestamp,
                            staff_id=applied.staff_id,
                            note=decision.target_id,
                        )

            for selection in step.checkout_selections:
                record = selection.service_started
                if record is None:
                    continue
                timeline.add(
                    ObservationKind.CHECKOUT_SERVICE_START,
                    timestamp,
                    customer_id=record.customer_id,
                    staff_id=record.staff_id,
                    fixture_id=record.fixture_id,
                    note="reference runtime checkout service start",
                )

            if options.include_stamina_snapshots:
                for staff in snapshot.staff:
                    if staff.stamina_current is None:
                        continue
                    timeline.add(
                        ObservationKind.STAMINA_SNAPSHOT,
                        timestamp,
                        staff_id=staff.staff_id,
                        numeric_value=staff.stamina_current,
                        note="reference runtime end-of-step stamina",
                    )

            if options.include_clock_samples:
                timeline.add(
                    ObservationKind.GAME_CLOCK_SAMPLE,
                    timestamp,
                    numeric_value=timestamp.minute_of_day,
                    note="reference runtime end-of-step clock",
                )

        return timeline
