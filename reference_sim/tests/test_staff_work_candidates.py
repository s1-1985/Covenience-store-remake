import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffTask
from conveni_sim.staff_work_candidates import StaffWorkCandidateDiscovery
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class StaffWorkCandidateDiscoveryTests(unittest.TestCase):
    def make_runtime(self):
        grid = StoreGrid(5, 5)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        grid.place_fixture(
            instance_id="checkout",
            fixture_id="synthetic_checkout",
            origin_subcell=GridPoint(6, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000)
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("s1")
        runtime.staff.add_staff("s2")
        runtime.inventory.add_slot(
            "low-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=4,
        )
        runtime.inventory.add_slot(
            "full-slot",
            fixture_id="shelf",
            product_id="rice-ball",
            capacity_units=5,
            initial_units=5,
        )
        return runtime

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def add_waiting_customer(self, runtime):
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(runtime, "c1", CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            "c1",
            "low-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, "c1", CustomerState.WAITING_CHECKOUT)

    def test_discovers_checkout_only_when_customer_is_actually_waiting(self):
        runtime = self.make_runtime()
        discovery = StaffWorkCandidateDiscovery(runtime)

        before = discovery.discover()
        self.assertEqual(before.checkout, ())

        self.add_waiting_customer(runtime)
        after = discovery.discover()
        self.assertEqual(len(after.checkout), 1)
        self.assertEqual(after.checkout[0].task, StaffTask.CHECKOUT)
        self.assertEqual(after.checkout[0].target_id, "checkout")
        self.assertIn("1 customer", after.checkout[0].reason)

    def test_discovers_nonfull_inventory_but_not_full_slot(self):
        runtime = self.make_runtime()

        snapshot = StaffWorkCandidateDiscovery(runtime).discover()

        self.assertEqual([candidate.target_id for candidate in snapshot.replenish], ["low-slot"])
        self.assertEqual(snapshot.replenish[0].task, StaffTask.REPLENISH)
        self.assertIn("6 free", snapshot.replenish[0].reason)

    def test_discovers_each_current_dirty_floor_cell_without_spawning_dirt(self):
        runtime = self.make_runtime()
        runtime.cleaning.mark_dirty((GridPoint(1, 1), GridPoint(2, 1)))

        snapshot = StaffWorkCandidateDiscovery(runtime).discover()

        self.assertEqual(
            [candidate.target_id for candidate in snapshot.clean],
            ["floor:1:1", "floor:2:1"],
        )
        self.assertTrue(all(candidate.task is StaffTask.CLEAN for candidate in snapshot.clean))

    def test_each_staff_gets_same_unprioritized_objective_candidate_set(self):
        runtime = self.make_runtime()
        runtime.cleaning.mark_dirty((GridPoint(1, 1),))
        self.add_waiting_customer(runtime)
        discovery = StaffWorkCandidateDiscovery(runtime)

        by_staff = discovery.candidates_by_staff()

        self.assertEqual(set(by_staff), {"s1", "s2"})
        self.assertEqual(by_staff["s1"], by_staff["s2"])
        tasks = [candidate.task for candidate in by_staff["s1"]]
        self.assertIn(StaffTask.CHECKOUT, tasks)
        self.assertIn(StaffTask.REPLENISH, tasks)
        self.assertIn(StaffTask.CLEAN, tasks)

    def test_discovery_does_not_assign_any_staff_task(self):
        runtime = self.make_runtime()
        runtime.cleaning.mark_dirty((GridPoint(1, 1),))

        StaffWorkCandidateDiscovery(runtime).discover()

        self.assertTrue(all(state.task is StaffTask.IDLE for state in runtime.staff.staff))


if __name__ == "__main__":
    unittest.main()
