import unittest

from conveni_sim.staff import StaffTask
from conveni_sim.staff_work_candidates import StaffWorkCandidateDiscovery
from conveni_sim.staff_work_completion import (
    CleaningCompletionCommand,
    ReplenishmentCompletionCommand,
    StaffWorkCompletionCoordinator,
)
from conveni_sim.store_grid import GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class StaffWorkCompletionTests(unittest.TestCase):
    def make_runtime(self):
        runtime = StoreRuntimeHarness(StoreGrid(3, 3), initial_cash_yen=1_000)
        runtime.staff.add_staff("s1")
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=5,
            initial_units=2,
            unit_procurement_cost_yen=80,
        )
        return runtime

    def test_explicit_replenishment_completion_mutates_inventory_cash_and_work_count(self):
        runtime = self.make_runtime()
        runtime.staff.assign_task("s1", StaffTask.REPLENISH, target_id="bread-slot")

        result = StaffWorkCompletionCoordinator(runtime).complete_replenishment(
            "s1",
            ReplenishmentCompletionCommand(quantity=2),
        )

        self.assertEqual(result.replenishment.inventory_mutation.units_after, 4)
        self.assertEqual(result.replenishment.procurement_event.amount_yen, 160)
        self.assertEqual(runtime.cash.known_cash_yen, 840)
        self.assertEqual(runtime.staff.staff_member("s1").completed_count(StaffTask.REPLENISH), 1)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.IDLE)

    def test_replenishment_quantity_is_not_inferred_and_cannot_exceed_free_capacity(self):
        runtime = self.make_runtime()
        runtime.staff.assign_task("s1", StaffTask.REPLENISH, target_id="bread-slot")
        with self.assertRaises(ValueError):
            StaffWorkCompletionCoordinator(runtime).complete_replenishment(
                "s1",
                ReplenishmentCompletionCommand(quantity=4),
            )
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 2)

    def test_explicit_cleaning_completion_only_cleans_assigned_dirty_cell(self):
        runtime = self.make_runtime()
        dirty = GridPoint(1, 1)
        other = GridPoint(2, 1)
        runtime.cleaning.mark_dirty((dirty, other))
        target_id = StaffWorkCandidateDiscovery.cleaning_target_id(dirty.x, dirty.y)
        runtime.staff.assign_task("s1", StaffTask.CLEAN, target_id=target_id)

        result = StaffWorkCompletionCoordinator(runtime).complete_cleaning(
            "s1", CleaningCompletionCommand()
        )

        self.assertEqual(result.cleaning.cleaned_cells, (dirty,))
        self.assertNotIn(dirty, runtime.cleaning.dirty_cells)
        self.assertIn(other, runtime.cleaning.dirty_cells)
        self.assertEqual(runtime.staff.staff_member("s1").completed_count(StaffTask.CLEAN), 1)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.IDLE)

    def test_stale_cleaning_target_is_rejected_without_recording_work(self):
        runtime = self.make_runtime()
        cell = GridPoint(1, 1)
        target_id = StaffWorkCandidateDiscovery.cleaning_target_id(cell.x, cell.y)
        runtime.staff.assign_task("s1", StaffTask.CLEAN, target_id=target_id)

        with self.assertRaises(ValueError):
            StaffWorkCompletionCoordinator(runtime).complete_cleaning("s1")
        self.assertEqual(runtime.staff.staff_member("s1").completed_count(StaffTask.CLEAN), 0)

    def test_wrong_assigned_task_is_rejected(self):
        runtime = self.make_runtime()
        runtime.staff.assign_task("s1", StaffTask.CLEAN, target_id="floor:1:1")
        with self.assertRaises(ValueError):
            StaffWorkCompletionCoordinator(runtime).complete_replenishment(
                "s1", ReplenishmentCompletionCommand(quantity=1)
            )


if __name__ == "__main__":
    unittest.main()
