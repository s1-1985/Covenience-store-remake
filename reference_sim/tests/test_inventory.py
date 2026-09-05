import unittest

from conveni_sim.inventory import (
    CapacityExceededError,
    OutOfStockError,
    StoreInventoryRuntime,
)
from conveni_sim.staff import StaffCondition, StaffTask, StoreStaffRoster


class InventoryRuntimeTests(unittest.TestCase):
    def test_customer_take_decrements_explicit_stock(self):
        inventory = StoreInventoryRuntime()
        slot = inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            initial_units=3,
        )

        mutation = inventory.take_for_customer("slot-1")

        self.assertEqual(slot.units, 2)
        self.assertEqual(mutation.quantity_delta, -1)
        self.assertEqual(mutation.units_after, 2)

    def test_out_of_stock_is_explicit(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )
        with self.assertRaises(OutOfStockError):
            inventory.take_for_customer("slot-1")

    def test_replenishment_does_not_silently_overfill(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=5,
            initial_units=4,
        )
        with self.assertRaises(CapacityExceededError):
            inventory.replenish("slot-1", 2)

    def test_known_procurement_cost_is_recorded_per_replenishment(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            unit_procurement_cost_yen=80,
        )

        mutation = inventory.replenish("slot-1", 4)

        self.assertEqual(mutation.procurement_cost_yen, 320)
        self.assertEqual(inventory.known_procurement_total_yen, 320)
        self.assertFalse(inventory.has_unknown_procurement_costs)

    def test_unknown_procurement_cost_stays_unknown_not_zero(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )

        mutation = inventory.replenish("slot-1", 4)

        self.assertIsNone(mutation.procurement_cost_yen)
        self.assertEqual(inventory.known_procurement_total_yen, 0)
        self.assertTrue(inventory.has_unknown_procurement_costs)

    def test_staff_replenishment_records_one_completed_work_event(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1")

        inventory.replenish(
            "slot-1",
            6,
            staff_roster=roster,
            staff_id="s1",
        )

        self.assertEqual(staff.completed_count(StaffTask.REPLENISH), 1)
        self.assertIsNone(staff.stamina_current)

    def test_staff_replenishment_can_use_explicit_stamina_cost(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=2)
        roster.assign_task("s1", StaffTask.REPLENISH, target_id="slot-1")

        inventory.replenish(
            "slot-1",
            6,
            staff_roster=roster,
            staff_id="s1",
            stamina_cost=2,
            break_room_target_id="break-room",
        )

        self.assertEqual(staff.completed_count(StaffTask.REPLENISH), 1)
        self.assertEqual(staff.stamina_current, 0)
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)

    def test_staff_pair_arguments_must_be_supplied_together(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )
        with self.assertRaises(ValueError):
            inventory.replenish("slot-1", 1, staff_id="s1")

    def test_history_preserves_sale_and_replenishment_order(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            initial_units=2,
            unit_procurement_cost_yen=80,
        )
        inventory.take_for_customer("slot-1")
        inventory.replenish("slot-1", 3)

        self.assertEqual([m.quantity_delta for m in inventory.history], [-1, 3])


if __name__ == "__main__":
    unittest.main()
