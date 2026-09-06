import unittest

from conveni_sim.staff import StaffTask
from conveni_sim.staff_task_policy import StaffTaskDecision
from conveni_sim.staff_work_timing import (
    StaffWorkCompletionDecision,
    StaffWorkTimingCoordinator,
    StaffWorkTimingStatus,
)
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class ChooseReplenishPolicy:
    def choose_task(self, context):
        for candidate in context.candidates:
            if candidate.task is StaffTask.REPLENISH:
                return StaffTaskDecision(candidate.task, target_id=candidate.target_id)
        return None


class ReplenishAfterTwoMinutes:
    def completion(self, context):
        if context.elapsed_game_minutes < 2:
            return None
        return StaffWorkCompletionDecision(quantity=context.inventory_free_capacity)


class CompleteCleaningNow:
    def completion(self, context):
        return StaffWorkCompletionDecision()


class StaffWorkTimingTests(unittest.TestCase):
    def make_runtime(self, *, staff_count=1):
        grid = StoreGrid(5, 5)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000)
        for index in range(staff_count):
            runtime.staff.add_staff(f"s{index + 1}")
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=4,
            unit_procurement_cost_yen=10,
        )
        return runtime

    def test_store_steps_complete_replenishment_after_policy_elapsed_time(self):
        runtime = self.make_runtime()
        timing = StaffWorkTimingCoordinator(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseReplenishPolicy(),
            staff_work_timing=timing,
            staff_work_completion_policy=ReplenishAfterTwoMinutes(),
        )

        assigned = orchestrator.step(0)

        self.assertEqual(assigned.staff_work_timing, ())
        self.assertEqual(len(timing.active_states), 1)
        self.assertEqual(timing.active_states[0].target_id, "bread-slot")
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.REPLENISH)

        working = orchestrator.step(1)

        self.assertEqual(len(working.staff_work_timing), 1)
        self.assertEqual(working.staff_work_timing[0].status, StaffWorkTimingStatus.ACTIVE)
        self.assertEqual(working.staff_work_timing[0].context.elapsed_game_minutes, 1)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 4)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.REPLENISH)

        completed = orchestrator.step(1)

        self.assertEqual(len(completed.staff_work_timing), 1)
        self.assertTrue(completed.staff_work_timing[0].completed)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 10)
        self.assertEqual(runtime.cash.known_cash_yen, 940)
        self.assertEqual(runtime.staff.staff_member("s1").completed_count(StaffTask.REPLENISH), 1)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.IDLE)
        self.assertEqual(len(runtime.staff.growth_opportunities), 1)
        self.assertEqual(timing.active_states, ())

    def test_duplicate_cleaning_target_releases_second_staff_without_false_work_event(self):
        runtime = self.make_runtime(staff_count=2)
        cell = GridPoint(1, 1)
        runtime.cleaning.mark_dirty((cell,))
        target_id = "floor:1:1"
        runtime.staff.assign_task("s1", StaffTask.CLEAN, target_id=target_id)
        runtime.staff.assign_task("s2", StaffTask.CLEAN, target_id=target_id)
        timing = StaffWorkTimingCoordinator(runtime)
        timing.register_assigned("s1")
        timing.register_assigned("s2")

        results = timing.evaluate_all(CompleteCleaningNow())

        self.assertEqual(results[0].status, StaffWorkTimingStatus.COMPLETED)
        self.assertEqual(results[1].status, StaffWorkTimingStatus.TARGET_UNAVAILABLE)
        self.assertNotIn(cell, runtime.cleaning.dirty_cells)
        self.assertEqual(runtime.staff.staff_member("s1").completed_count(StaffTask.CLEAN), 1)
        self.assertEqual(runtime.staff.staff_member("s2").completed_count(StaffTask.CLEAN), 0)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.IDLE)
        self.assertEqual(runtime.staff.staff_member("s2").task, StaffTask.IDLE)
        self.assertEqual(timing.active_states, ())

    def test_staff_work_timing_inputs_must_be_supplied_as_a_pair(self):
        runtime = self.make_runtime()
        timing = StaffWorkTimingCoordinator(runtime)

        with self.assertRaises(ValueError):
            StoreStepOrchestrator(runtime, staff_work_timing=timing)
        with self.assertRaises(ValueError):
            StoreStepOrchestrator(
                runtime,
                staff_work_completion_policy=ReplenishAfterTwoMinutes(),
            )


if __name__ == "__main__":
    unittest.main()
