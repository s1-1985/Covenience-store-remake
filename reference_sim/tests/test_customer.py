import unittest

from conveni_sim.customer import CustomerLifecycleHarness, CustomerState, PurchaseFlow
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.traffic import DynamicTrafficHarness


class CustomerLifecycleTests(unittest.TestCase):
    def make_store(self):
        grid = StoreGrid(6, 4)
        grid.place_fixture(
            instance_id="shelf-1",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        grid.place_fixture(
            instance_id="shelf-2",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 5),
            footprint_tiles=(1, 1),
            interaction_side=Direction.WEST,
        )
        grid.place_fixture(
            instance_id="checkout-1",
            fixture_id="synthetic_checkout",
            origin_subcell=GridPoint(8, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        traffic = DynamicTrafficHarness(grid)
        return grid, CustomerLifecycleHarness(traffic)

    def advance_until(self, lifecycle, customer_id, expected, limit=50):
        for _ in range(limit):
            if lifecycle.customer(customer_id).state is expected:
                return lifecycle.customer(customer_id)
            lifecycle.tick()
        self.fail(f"customer {customer_id} did not reach {expected}")

    def test_normal_purchase_requires_explicit_checkout_completion_then_exit(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1",),
            checkout_fixture_id="checkout-1",
        )

        self.advance_until(lifecycle, "c1", CustomerState.AT_MERCHANDISE)
        lifecycle.record_merchandise_interaction("c1", flow=PurchaseFlow.CHECKOUT_REQUIRED)
        self.assertEqual(customer.state, CustomerState.APPROACHING_CHECKOUT)

        self.advance_until(lifecycle, "c1", CustomerState.WAITING_CHECKOUT)
        lifecycle.tick()
        self.assertEqual(customer.state, CustomerState.WAITING_CHECKOUT)

        lifecycle.complete_checkout("c1")
        self.assertEqual(customer.state, CustomerState.LEAVING)
        self.advance_until(lifecycle, "c1", CustomerState.EXITED)
        self.assertTrue(customer.completed_checkout)

    def test_self_service_candidate_can_leave_without_checkout(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1",),
        )

        self.advance_until(lifecycle, "c1", CustomerState.AT_MERCHANDISE)
        lifecycle.record_merchandise_interaction(
            "c1", flow=PurchaseFlow.SELF_SERVICE_CANDIDATE
        )

        self.assertFalse(customer.requires_checkout)
        self.assertEqual(customer.self_service_fixture_ids, ("shelf-1",))
        self.assertEqual(customer.state, CustomerState.LEAVING)
        self.advance_until(lifecycle, "c1", CustomerState.EXITED)

    def test_mixed_plan_can_self_service_then_continue_to_normal_purchase(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1", "shelf-2"),
            checkout_fixture_id="checkout-1",
        )

        self.advance_until(lifecycle, "c1", CustomerState.AT_MERCHANDISE)
        lifecycle.record_merchandise_interaction(
            "c1", flow=PurchaseFlow.SELF_SERVICE_CANDIDATE
        )
        self.assertEqual(customer.current_merchandise_fixture_id, "shelf-2")

        self.advance_until(lifecycle, "c1", CustomerState.AT_MERCHANDISE)
        lifecycle.record_merchandise_interaction("c1", flow=PurchaseFlow.CHECKOUT_REQUIRED)
        self.assertEqual(customer.state, CustomerState.APPROACHING_CHECKOUT)
        self.assertEqual(customer.interacted_fixture_ids, ("shelf-1", "shelf-2"))

    def test_purchase_order_is_supplied_by_caller_not_chosen_by_lifecycle(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-2", "shelf-1"),
        )
        self.assertEqual(customer.current_merchandise_fixture_id, "shelf-2")
        self.assertEqual(customer.remaining_merchandise_fixture_ids, ("shelf-2", "shelf-1"))

    def test_no_merchandise_plan_routes_directly_to_exit(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
        )
        self.assertEqual(customer.state, CustomerState.LEAVING)
        self.advance_until(lifecycle, "c1", CustomerState.EXITED)

    def test_force_eject_routes_selected_customer_to_exit(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1",),
        )
        lifecycle.force_eject("c1", reason="manual_player_action")
        self.assertEqual(customer.state, CustomerState.EJECTING)
        self.advance_until(lifecycle, "c1", CustomerState.EJECTED)
        self.assertEqual(customer.ejection_reason, "manual_player_action")

    def test_blocked_fixture_interaction_face_is_unreachable(self):
        grid, lifecycle = self.make_store()
        grid.set_static_blocked((GridPoint(4, 1), GridPoint(5, 1)))
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1",),
        )
        self.assertEqual(customer.state, CustomerState.UNREACHABLE)

    def test_checkout_required_interaction_without_checkout_is_rejected_without_mutation(self):
        _, lifecycle = self.make_store()
        customer = lifecycle.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 1),
            merchandise_fixture_ids=("shelf-1",),
        )
        self.advance_until(lifecycle, "c1", CustomerState.AT_MERCHANDISE)

        with self.assertRaises(ValueError):
            lifecycle.record_merchandise_interaction("c1", flow=PurchaseFlow.CHECKOUT_REQUIRED)

        self.assertFalse(customer.requires_checkout)
        self.assertEqual(customer.interacted_fixture_ids, ())
        self.assertEqual(customer.state, CustomerState.AT_MERCHANDISE)


if __name__ == "__main__":
    unittest.main()
