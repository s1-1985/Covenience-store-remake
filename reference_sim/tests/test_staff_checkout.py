import unittest

from conveni_sim.checkout import CheckoutCapacityError, CheckoutStationRuntime
from conveni_sim.customer import CustomerLifecycleHarness, CustomerState, PurchaseFlow
from conveni_sim.staff import FIRST_TITLE_MAX_STAFF_PER_STORE, StaffTask, StoreStaffRoster
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.traffic import DynamicTrafficHarness


class StaffAndCheckoutTests(unittest.TestCase):
    def make_customer_system(self):
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
        traffic = DynamicTrafficHarness(grid)
        return CustomerLifecycleHarness(traffic)

    def advance_until(self, customers, customer_id, state, *, limit=100):
        for _ in range(limit):
            if customers.customer(customer_id).state is state:
                return
            customers.tick()
        self.fail(f"customer {customer_id} did not reach state {state}")

    def add_waiting_customer(self, customers, customer_id, entry_point, exit_point):
        customers.add_customer(
            customer_id,
            entry_point=entry_point,
            exit_point=exit_point,
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(customers, customer_id, CustomerState.AT_MERCHANDISE)
        customers.record_merchandise_interaction(
            customer_id,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(customers, customer_id, CustomerState.WAITING_CHECKOUT)

    def test_first_title_roster_capacity_defaults_to_three(self):
        roster = StoreStaffRoster()
        self.assertEqual(roster.max_staff, FIRST_TITLE_MAX_STAFF_PER_STORE)
        roster.add_staff("s1")
        roster.add_staff("s2")
        roster.add_staff("s3")
        with self.assertRaises(ValueError):
            roster.add_staff("s4")

    def test_manager_identity_is_explicit_without_growth_formula(self):
        roster = StoreStaffRoster()
        roster.add_staff("manager", manager=True)
        roster.add_staff("worker")
        self.assertEqual(roster.manager_staff_id, "manager")
        roster.set_manager("worker")
        self.assertEqual(roster.manager_staff_id, "worker")

    def test_staff_tasks_do_not_auto_switch_without_caller_decision(self):
        roster = StoreStaffRoster()
        state = roster.add_staff("s1")
        roster.assign_task("s1", StaffTask.REPLENISH, target_id="shelf")
        self.assertEqual(state.task, StaffTask.REPLENISH)
        self.assertEqual(state.target_id, "shelf")
        self.assertEqual(state.task_switch_count, 1)

    def test_waiting_arrival_order_is_recorded_but_service_need_not_be_fifo(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        self.add_waiting_customer(customers, "c2", GridPoint(0, 2), GridPoint(1, 8))

        roster = StoreStaffRoster()
        roster.add_staff("s1")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=1
        )
        self.assertEqual(checkout.refresh_waiting(), ("c1", "c2"))

        checkout.begin_service("s1", "c2")
        self.assertEqual(checkout.customer_being_served_by("s1"), "c2")
        self.assertEqual(checkout.waiting_customer_ids, ("c1",))

    def test_single_staff_capacity_rejects_second_simultaneous_cashier(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        self.add_waiting_customer(customers, "c2", GridPoint(0, 2), GridPoint(1, 8))
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        roster.add_staff("s2")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=1
        )

        checkout.begin_service("s1", "c1")
        with self.assertRaises(CheckoutCapacityError):
            checkout.begin_service("s2", "c2")

    def test_two_staff_capacity_can_represent_two_person_checkout_variant(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        self.add_waiting_customer(customers, "c2", GridPoint(0, 2), GridPoint(1, 8))
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        roster.add_staff("s2")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=2
        )

        checkout.begin_service("s1", "c1")
        checkout.begin_service("s2", "c2")
        self.assertEqual(len(checkout.active_services), 2)
        self.assertEqual(roster.staff_member("s1").task, StaffTask.CHECKOUT)
        self.assertEqual(roster.staff_member("s2").task, StaffTask.CHECKOUT)

    def test_checkout_has_no_invented_automatic_service_duration(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=1
        )
        checkout.begin_service("s1", "c1")

        for _ in range(10):
            customers.tick()

        self.assertEqual(customers.customer("c1").state, CustomerState.WAITING_CHECKOUT)
        self.assertEqual(checkout.customer_being_served_by("s1"), "c1")
        self.assertFalse(customers.customer("c1").completed_checkout)

    def test_finishing_service_completes_checkout_and_releases_staff(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=1
        )
        checkout.begin_service("s1", "c1")

        record = checkout.finish_service("s1")

        self.assertEqual(record.customer_id, "c1")
        self.assertEqual(customers.customer("c1").state, CustomerState.LEAVING)
        self.assertTrue(customers.customer("c1").completed_checkout)
        self.assertEqual(roster.staff_member("s1").task, StaffTask.IDLE)
        self.assertEqual(checkout.service_history[-1].customer_id, "c1")

    def test_ejected_waiter_is_removed_without_guessing_penalty(self):
        customers = self.make_customer_system()
        self.add_waiting_customer(customers, "c1", GridPoint(0, 0), GridPoint(0, 8))
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        checkout = CheckoutStationRuntime(
            "checkout", customers, roster, simultaneous_staff_capacity=1
        )
        self.assertEqual(checkout.refresh_waiting(), ("c1",))
        customers.force_eject("c1", reason="manual")
        self.assertEqual(checkout.refresh_waiting(), ())


if __name__ == "__main__":
    unittest.main()
