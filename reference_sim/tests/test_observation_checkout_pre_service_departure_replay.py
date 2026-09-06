import unittest

from conveni_sim.checkout_pre_service_departure import (
    CheckoutPreServiceDepartureCoordinator,
    CheckoutPreServiceDepartureStatus,
)
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.observation_checkout_pre_service_departure_replay import (
    ObservationCheckoutPreServiceDepartureReplayAdapter,
    ObservationCheckoutPreServiceDepartureReplayMapping,
)
from conveni_sim.observation_comparison import ObservationIdentityMapping
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import SubdayClock
from conveni_sim.staff import StaffCondition, StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class ObservationCheckoutPreServiceDepartureReplayTests(unittest.TestCase):
    def make_timeline(self):
        timeline = GameplayObservationTimeline("source")
        timeline.add(
            ObservationKind.CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM,
            GameTimestamp.from_hm(1, 1, 1, 10, 5),
            staff_id="observed-staff",
            fixture_id="observed-checkout",
        )
        return timeline

    def make_runtime(self, *, minute_of_day=10 * 60):
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
            subday_clock=SubdayClock(minute_of_day // 60, minute_of_day % 60),
        )
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("s1", stamina_max=5)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=5,
            initial_units=2,
        )
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        return runtime

    def add_waiting_customer(self, runtime):
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        for _ in range(100):
            if runtime.customers.customer("c1").state is CustomerState.AT_MERCHANDISE:
                break
            runtime.customers.tick()
        else:
            self.fail("customer did not reach merchandise")
        runtime.customer_pick_and_continue(
            "c1",
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        for _ in range(100):
            if runtime.customers.customer("c1").state is CustomerState.WAITING_CHECKOUT:
                return
            runtime.customers.tick()
        self.fail("customer did not reach checkout")

    def test_adapter_requires_explicit_causal_interpretation(self):
        with self.assertRaises(ValueError):
            ObservationCheckoutPreServiceDepartureReplayAdapter().build_plan(
                self.make_timeline(),
                ObservationDayCoverage(1, 1, 1),
            )

    def test_adapter_uses_only_explicit_identity_mapping(self):
        plan = ObservationCheckoutPreServiceDepartureReplayAdapter().build_plan(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutPreServiceDepartureReplayMapping(
                checkout_staff_return_means_pre_service_departure=True
            ),
            identity_mapping=ObservationIdentityMapping(
                staff_ids=(("observed-staff", "s1"),),
                fixture_ids=(("observed-checkout", "checkout"),),
            ),
        )

        self.assertEqual(len(plan.rules), 1)
        rule = plan.rules[0]
        self.assertEqual(rule.staff_id, "s1")
        self.assertEqual(rule.checkout_fixture_id, "checkout")
        self.assertEqual(rule.return_minute_of_day, 10 * 60 + 5)
        self.assertEqual(rule.occurrence_index, 0)

    def test_policy_holds_service_until_observed_return_then_departs(self):
        adapter = ObservationCheckoutPreServiceDepartureReplayAdapter()
        plan = adapter.build_plan(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutPreServiceDepartureReplayMapping(
                checkout_staff_return_means_pre_service_departure=True
            ),
            identity_mapping=ObservationIdentityMapping(
                staff_ids=(("observed-staff", "s1"),),
                fixture_ids=(("observed-checkout", "checkout"),),
            ),
        )
        policy = adapter.build_policy(plan, break_room_target_id="break-room")
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        coordinator = CheckoutPreServiceDepartureCoordinator(runtime)

        before = coordinator.evaluate_staff("s1", policy)
        self.assertEqual(before.status, CheckoutPreServiceDepartureStatus.UNRESOLVED)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.CHECKOUT)

        runtime.advance_game_minutes(5)
        at_observation = coordinator.evaluate_staff("s1", policy)
        self.assertEqual(at_observation.status, CheckoutPreServiceDepartureStatus.DEPARTED)
        staff = runtime.staff.staff_member("s1")
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(staff.task, StaffTask.RETURN_TO_BREAK_ROOM)
        self.assertEqual(staff.target_id, "break-room")
        self.assertEqual(staff.stamina_current, 5)

    def test_observed_return_does_not_create_checkout_demand(self):
        adapter = ObservationCheckoutPreServiceDepartureReplayAdapter()
        plan = adapter.build_plan(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutPreServiceDepartureReplayMapping(
                checkout_staff_return_means_pre_service_departure=True
            ),
            identity_mapping=ObservationIdentityMapping(
                staff_ids=(("observed-staff", "s1"),),
                fixture_ids=(("observed-checkout", "checkout"),),
            ),
        )
        policy = adapter.build_policy(plan)
        runtime = self.make_runtime(minute_of_day=10 * 60 + 10)
        evaluation = CheckoutPreServiceDepartureCoordinator(runtime).evaluate_staff(
            "s1",
            policy,
        )

        self.assertEqual(evaluation.status, CheckoutPreServiceDepartureStatus.NOT_APPLICABLE)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.CHECKOUT)


if __name__ == "__main__":
    unittest.main()
