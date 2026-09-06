import unittest

from conveni_sim.staff import StaffCondition, StaffTask
from conveni_sim.staff_rest_timing import (
    StaffRestTimingCoordinator,
    StaffRestTimingStatus,
    StaffRestTransitionDecision,
)
from conveni_sim.staff_work_timing import (
    StaffWorkCompletionDecision,
    StaffWorkTimingCoordinator,
)
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class ThresholdRestPolicy:
    def __init__(self, *, travel_minutes=2, recovery_interval_minutes=1, recovery_amount=2):
        self.travel_minutes = travel_minutes
        self.recovery_interval_minutes = recovery_interval_minutes
        self.recovery_amount = recovery_amount

    def transition(self, context):
        if context.condition is StaffCondition.RETURNING_TO_BREAK_ROOM:
            if context.elapsed_game_minutes >= self.travel_minutes:
                return StaffRestTransitionDecision(arrive_at_break_room=True)
            return None
        if context.elapsed_game_minutes >= self.recovery_interval_minutes:
            return StaffRestTransitionDecision(recovery_amount=self.recovery_amount)
        return None


class CompleteReplenishmentAfterOneMinute:
    def completion(self, context):
        if context.elapsed_game_minutes < 1:
            return None
        return StaffWorkCompletionDecision(
            quantity=1,
            stamina_cost=1,
            break_room_target_id="break-room",
        )


class StaffRestTimingTests(unittest.TestCase):
    def make_runtime(self, *, stamina=3):
        runtime = StoreRuntimeHarness(StoreGrid(3, 3), initial_cash_yen=1_000)
        runtime.staff.add_staff("s1", stamina_max=stamina)
        return runtime

    def test_return_travel_and_recovery_use_explicit_policy_timing(self):
        runtime = self.make_runtime(stamina=3)
        runtime.staff.consume_stamina("s1", 3, break_room_target_id="break-room")
        timing = StaffRestTimingCoordinator(runtime)
        timing.sync_from_roster()
        policy = ThresholdRestPolicy(
            travel_minutes=2,
            recovery_interval_minutes=1,
            recovery_amount=2,
        )

        runtime.advance_game_minutes(1)
        before_arrival = timing.evaluate_all(policy)
        self.assertEqual(before_arrival[0].status, StaffRestTimingStatus.ACTIVE)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RETURNING_TO_BREAK_ROOM)

        runtime.advance_game_minutes(1)
        arrival = timing.evaluate_all(policy)
        self.assertEqual(arrival[0].status, StaffRestTimingStatus.ARRIVED_AT_BREAK_ROOM)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RESTING)
        self.assertEqual(runtime.staff.staff_member("s1").stamina_current, 0)

        runtime.advance_game_minutes(1)
        partial = timing.evaluate_all(policy)
        self.assertEqual(partial[0].status, StaffRestTimingStatus.RECOVERED)
        self.assertEqual(runtime.staff.staff_member("s1").stamina_current, 2)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RESTING)

        runtime.advance_game_minutes(1)
        complete = timing.evaluate_all(policy)
        self.assertEqual(complete[0].status, StaffRestTimingStatus.RECOVERY_COMPLETE)
        self.assertEqual(runtime.staff.staff_member("s1").stamina_current, 3)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.AVAILABLE)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.IDLE)
        self.assertEqual(timing.active_states, ())

    def test_invalid_transition_payload_is_rejected_for_current_condition(self):
        runtime = self.make_runtime(stamina=1)
        runtime.staff.consume_stamina("s1", 1)
        timing = StaffRestTimingCoordinator(runtime)
        timing.sync_from_roster()

        class InvalidRecoveryWhileReturning:
            def transition(self, context):
                return StaffRestTransitionDecision(recovery_amount=1)

        with self.assertRaises(ValueError):
            timing.evaluate_all(InvalidRecoveryWhileReturning())

    def test_store_step_tracks_new_zero_stamina_state_without_same_step_arrival(self):
        runtime = self.make_runtime(stamina=1)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=3,
            initial_units=1,
            unit_procurement_cost_yen=10,
        )
        runtime.staff.assign_task("s1", StaffTask.REPLENISH, target_id="bread-slot")
        work_timing = StaffWorkTimingCoordinator(runtime)
        work_timing.register_assigned("s1")
        rest_timing = StaffRestTimingCoordinator(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_work_timing=work_timing,
            staff_work_completion_policy=CompleteReplenishmentAfterOneMinute(),
            staff_rest_timing=rest_timing,
            staff_rest_transition_policy=ThresholdRestPolicy(
                travel_minutes=1,
                recovery_interval_minutes=1,
                recovery_amount=1,
            ),
        )

        completion_step = orchestrator.step(1)

        self.assertEqual(completion_step.staff_rest_timing, ())
        self.assertTrue(completion_step.staff_work_timing[0].completed)
        state = runtime.staff.staff_member("s1")
        self.assertEqual(state.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(state.stamina_current, 0)
        self.assertEqual(len(rest_timing.active_states), 1)

        arrival_step = orchestrator.step(1)
        self.assertEqual(
            arrival_step.staff_rest_timing[0].status,
            StaffRestTimingStatus.ARRIVED_AT_BREAK_ROOM,
        )
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RESTING)

        recovery_step = orchestrator.step(1)
        self.assertEqual(
            recovery_step.staff_rest_timing[0].status,
            StaffRestTimingStatus.RECOVERY_COMPLETE,
        )
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.AVAILABLE)

    def test_rest_pair_must_be_supplied_together(self):
        runtime = self.make_runtime()
        with self.assertRaises(ValueError):
            StoreStepOrchestrator(
                runtime,
                staff_rest_timing=StaffRestTimingCoordinator(runtime),
            )


if __name__ == "__main__":
    unittest.main()
