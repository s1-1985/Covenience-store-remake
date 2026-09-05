import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.customer_demand import CustomerArrivalIntent, CustomerDemandCoordinator
from conveni_sim.customer_purchase_policy import (
    CustomerPurchaseCoordinator,
    CustomerPurchaseDecision,
    MerchandiseOffer,
)
from conveni_sim.operating_time import OperatingHours, SubdayClock
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class OneArrivalPolicy:
    def __init__(self):
        self.emitted = False

    def arrivals_for(self, context):
        if self.emitted:
            return ()
        self.emitted = True
        return (
            CustomerArrivalIntent(
                "c1",
                entry_point=GridPoint(0, 0),
                exit_point=GridPoint(0, 6),
                merchandise_fixture_ids=("shelf",),
                checkout_fixture_id="checkout",
            ),
        )


class BuyBreadPolicy:
    def choose_purchase(self, context):
        return CustomerPurchaseDecision.buy("bread-slot") if context.offers else CustomerPurchaseDecision.skip()


class StoreStepTests(unittest.TestCase):
    def make_runtime(self):
        grid = StoreGrid(4, 4)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(2, 0),
            footprint_tiles=(1, 1),
            interaction_side=Direction.SOUTH,
        )
        grid.place_fixture(
            instance_id="checkout",
            fixture_id="synthetic_checkout",
            origin_subcell=GridPoint(4, 0),
            footprint_tiles=(1, 1),
            interaction_side=Direction.SOUTH,
        )
        runtime = StoreRuntimeHarness(
            grid,
            initial_cash_yen=1000,
            operating_hours=OperatingHours.twenty_four_hours(),
            subday_clock=SubdayClock(6, 0),
        )
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=5,
            initial_units=2,
        )
        return runtime

    def test_step_composes_clock_demand_traffic_and_purchase_without_checkout(self):
        runtime = self.make_runtime()
        demand = CustomerDemandCoordinator(runtime, OneArrivalPolicy())
        purchases = CustomerPurchaseCoordinator(
            runtime,
            (MerchandiseOffer("bread-slot", 120, PurchaseFlow.CHECKOUT_REQUIRED),),
        )
        orchestrator = StoreStepOrchestrator(
            runtime,
            demand=demand,
            purchases=purchases,
            purchase_policy=BuyBreadPolicy(),
        )

        results = []
        for _ in range(10):
            results.append(orchestrator.step(1))
            if runtime.customers.customer("c1").state is CustomerState.APPROACHING_CHECKOUT:
                break

        self.assertEqual(runtime.subday_clock.minute_of_day, 6 * 60 + len(results))
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 1)
        self.assertEqual(len(runtime.purchases.basket("c1").lines), 1)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.APPROACHING_CHECKOUT)
        self.assertFalse(runtime.purchases.basket("c1").settled)

    def test_closed_store_still_routes_demand_through_admission_gate(self):
        runtime = self.make_runtime()
        runtime.set_temporary_closure(True)
        demand = CustomerDemandCoordinator(runtime, OneArrivalPolicy())
        result = StoreStepOrchestrator(runtime, demand=demand).step(1)

        self.assertIsNotNone(result.demand)
        self.assertFalse(result.demand.admissions[0].admitted)
        with self.assertRaises(KeyError):
            runtime.customers.customer("c1")

    def test_purchase_components_must_be_supplied_as_a_pair(self):
        runtime = self.make_runtime()
        purchases = CustomerPurchaseCoordinator(runtime, ())
        with self.assertRaises(ValueError):
            StoreStepOrchestrator(runtime, purchases=purchases)


if __name__ == "__main__":
    unittest.main()
