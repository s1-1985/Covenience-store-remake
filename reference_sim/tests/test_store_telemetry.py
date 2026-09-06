import unittest

from conveni_sim.clock import SimulationClock
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.operating_time import SubdayClock
from conveni_sim.representative_day_runner import RepresentativeDayRunner
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator
from conveni_sim.store_telemetry import StoreTelemetryRecorder


class StoreTelemetryTests(unittest.TestCase):
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
        runtime = StoreRuntimeHarness(
            grid,
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(10, 0),
        )
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("s1", stamina_max=5)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=3,
            initial_units=2,
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
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, "c1", CustomerState.WAITING_CHECKOUT)

    def test_snapshot_reports_customer_queue_staff_inventory_and_cash_facts(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        recorder = StoreTelemetryRecorder()

        waiting = recorder.snapshot(runtime)

        self.assertEqual(waiting.minute_of_day, 10 * 60)
        self.assertEqual(waiting.total_customer_sessions, 1)
        self.assertEqual(waiting.customer_count(CustomerState.WAITING_CHECKOUT), 1)
        self.assertEqual(waiting.waiting_checkout_customers, 1)
        self.assertEqual(waiting.active_checkout_services, 0)
        self.assertEqual(waiting.inventory[0].units, 1)
        self.assertEqual(waiting.staff[0].stamina_current, 5)
        self.assertEqual(waiting.known_cash_yen, 1_000)
        self.assertTrue(waiting.cash_is_exact)

        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        runtime.begin_checkout_service("checkout", staff_id="s1", customer_id="c1")
        active = recorder.snapshot(runtime)

        self.assertEqual(active.waiting_checkout_customers, 0)
        self.assertEqual(active.active_checkout_services, 1)
        self.assertEqual(active.checkouts[0].active_customer_ids, ("c1",))
        self.assertEqual(active.checkouts[0].active_staff_ids, ("s1",))

    def test_representative_day_result_contains_boundary_aligned_snapshots(self):
        runtime = StoreRuntimeHarness(
            StoreGrid(3, 3),
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(23, 50),
        )
        runner = RepresentativeDayRunner(
            StoreStepOrchestrator(runtime),
            SimulationClock(year=1, month=1, day=1),
        )

        result = runner.run(step_game_minutes=10)

        self.assertEqual(result.start_snapshot.minute_of_day, 23 * 60 + 50)
        self.assertEqual(len(result.step_snapshots), 1)
        self.assertEqual(result.step_snapshots[0].minute_of_day, 23 * 60 + 59)
        self.assertEqual(result.end_of_day_snapshot.minute_of_day, 23 * 60 + 59)
        self.assertEqual(result.boundary_snapshot.minute_of_day, 0)
        self.assertEqual(result.start_snapshot.known_cash_yen, 1_000)
        self.assertEqual(result.boundary_snapshot.known_cash_yen, 1_000)


if __name__ == "__main__":
    unittest.main()
