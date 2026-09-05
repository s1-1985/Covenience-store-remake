"""既知バグの再現テスト(Claude Code が発見、ChatGPT が修正する対象)。

対象コミット: 554d78d (2026-09-06)

ここにあるテストは「こうあるべき」という期待を書いたもので、現在は失敗する。
修正されると XPASS になるので、`pytest -q` の出力で直ったことが機械的に分かる。
修正後は `@unittest.expectedFailure` を外して通常のテストに戻すこと。

各項目の背景は docs/handoff/chatgpt-review-notes.md を参照。
"""

import unittest
import urllib.parse

from conveni_sim.baseline_data import SCENARIOS, PROMOTIONS
from conveni_sim.checkout_service_timing import CheckoutServiceTimingCoordinator
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.promotion import (
    PromotionMoment,
    PromotionScheduler,
    StorePopularityRuntime,
)
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import CheckoutSaleResult, StoreRuntimeHarness


class StaffAssignmentKnownIssueTests(unittest.TestCase):
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
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000_000)
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )
        return runtime

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def send_customer_to_checkout(self, runtime, customer_id):
        runtime.add_customer(
            customer_id,
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(runtime, customer_id, CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            customer_id,
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, customer_id, CustomerState.WAITING_CHECKOUT)

    @unittest.expectedFailure
    def test_begin_service_must_not_silently_steal_a_replenishing_staff(self):
        """メモ項目2: begin_service が REPLENISH 中のstaffを黙ってCHECKOUTに上書きする。

        begin_service は「別のcheckoutに割当て済みか」だけを見ており、
        REPLENISH/CLEAN 中かどうかを見ていない。
        """
        runtime = self.make_runtime()
        runtime.staff.add_staff("s1")
        runtime.staff.assign_task("s1", StaffTask.REPLENISH, target_id="bread-slot")
        self.send_customer_to_checkout(runtime, "c1")

        with self.assertRaises(ValueError):
            runtime.begin_checkout_service("checkout", staff_id="s1", customer_id="c1")

    @unittest.expectedFailure
    def test_checkout_timing_completion_returns_the_declared_sale_type(self):
        """メモ項目4: CheckoutServiceTimingEvaluation.sale の型注釈と実際の値が違う。

        注釈は Optional[CheckoutSaleResult] だが、実際に入るのは
        CheckoutSaleCompletion。注釈を信じて .service_started を読むと
        AttributeError になる。
        """
        runtime = self.make_runtime()
        runtime.staff.add_staff("s1")
        self.send_customer_to_checkout(runtime, "c1")
        started = runtime.begin_checkout_service(
            "checkout", staff_id="s1", customer_id="c1"
        )
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(started)
        runtime.advance_game_minutes(5)

        class FixedDuration:
            def required_game_minutes(self, context):
                return 1

        evaluation = timing.evaluate_staff("s1", FixedDuration())
        self.assertTrue(evaluation.completed)
        self.assertIsInstance(evaluation.sale, CheckoutSaleResult)


class PromotionKnownIssueTests(unittest.TestCase):
    def make_fired_promotion(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        scheduler.schedule(
            "direct_mail",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        due = scheduler.pop_due(PromotionMoment(1, 1, 2, 10))
        return scheduler, due[0]

    @unittest.expectedFailure
    def test_promotion_cannot_be_applied_twice(self):
        """メモ項目5: 同じ発火済みプロモーションを何度でも適用でき、人気度が多重加算される。

        StaffRoster.resolve_growth_opportunity や
        StorePopularityRuntime.resolve_decay_opportunity には
        「already resolved」ガードがあるのに、apply_promotion には無い。
        """
        scheduler, record = self.make_fired_promotion()
        popularity = StorePopularityRuntime()
        popularity.add_store("store-1", popularity=10)

        popularity.apply_promotion(record, scheduler, target_store_ids=["store-1"])
        with self.assertRaises(ValueError):
            popularity.apply_promotion(record, scheduler, target_store_ids=["store-1"])

    @unittest.expectedFailure
    def test_promotion_with_unknown_store_does_not_partially_apply(self):
        """メモ項目6: 未登録店舗IDでKeyErrorになると、それ以前の店舗だけ人気度が上がって戻らない。"""
        scheduler, record = self.make_fired_promotion()
        popularity = StorePopularityRuntime()
        popularity.add_store("store-1", popularity=10)

        with self.assertRaises(KeyError):
            popularity.apply_promotion(
                record, scheduler, target_store_ids=["store-1", "ghost-store"]
            )
        self.assertEqual(popularity.popularity("store-1"), 10)


class RemovedFixtureKnownIssueTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_a_fixture_removed_from_the_grid_cannot_still_sell_goods(self):
        """メモ項目10: グリッドから撤去された什器から商品を購入でき、売上まで計上される。

        `StoreGrid.remove_fixture` は在庫スロットや進行中の顧客セッションと
        連動していないため、撤去済みの什器に顧客が「到着」し、そこから購入できる。
        """
        grid = StoreGrid(5, 5)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="f1",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000_000)
        runtime.inventory.add_slot(
            "slot-a",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
        )
        runtime.customers.tick()
        runtime.grid.remove_fixture("shelf")
        for _ in range(60):
            if runtime.customers.customer("c1").state is CustomerState.AT_MERCHANDISE:
                break
            runtime.customers.tick()

        self.assertEqual(runtime.grid.placements, ())
        with self.assertRaises(ValueError):
            runtime.customer_pick_and_continue(
                "c1",
                "slot-a",
                quantity=1,
                unit_sale_price_yen=120,
                flow=PurchaseFlow.SELF_SERVICE_CANDIDATE,
            )


class StoreStepKnownIssueTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_a_failing_purchase_phase_does_not_leave_the_clock_advanced(self):
        """メモ項目11: step() が購入評価の例外で中断し、時計だけ進んだ状態になる。

        `advance_game_minutes` が最初に走るため、後段で例外が出ても時間は戻らない。
        呼び出し側が同じstepをリトライすると時間が二重に進む。
        """
        from conveni_sim.customer_purchase_policy import (
            CustomerPurchaseCoordinator,
            CustomerPurchaseDecision,
            MerchandiseOffer,
        )
        from conveni_sim.operating_time import OperatingHours
        from conveni_sim.store_step import StoreStepOrchestrator

        grid = StoreGrid(6, 6)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="f1",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(
            grid,
            initial_cash_yen=1_000_000,
            operating_hours=OperatingHours.twenty_four_hours(),
        )
        runtime.inventory.add_slot(
            "slot-a",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )

        class AlwaysBuy:
            def choose_purchase(self, context):
                return CustomerPurchaseDecision.buy("slot-a", 1)

        # CHECKOUT_REQUIRED offer, but the customer was routed with no checkout.
        coordinator = CustomerPurchaseCoordinator(
            runtime, [MerchandiseOffer("slot-a", 100, PurchaseFlow.CHECKOUT_REQUIRED)]
        )
        orchestrator = StoreStepOrchestrator(
            runtime, purchases=coordinator, purchase_policy=AlwaysBuy()
        )
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 10),
            merchandise_fixture_ids=("shelf",),
        )
        for _ in range(40):
            if runtime.customers.customer("c1").state is CustomerState.AT_MERCHANDISE:
                break
            runtime.customers.tick()

        before = runtime.subday_clock.absolute_minutes
        with self.assertRaises(ValueError):
            orchestrator.step(1)
        self.assertEqual(runtime.subday_clock.absolute_minutes, before)


class BaselineDataKnownIssueTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_scenario_source_urls_are_not_typo_corrupted(self):
        """メモ項目8: シナリオのソースURLに壊れたWikiページ名が混ざっている。

        `ゲームモード攻略` を指すべき箇所が3つ、`ゲームード攻略`(「モ」欠落)になっている。
        """
        broken = []
        for scenario in SCENARIOS:
            for label, value in (
                ("initial_cash_yen", scenario.initial_cash_yen),
                ("objective", scenario.objective),
            ):
                decoded = urllib.parse.unquote(value.source)
                if "ゲームード" in decoded:
                    broken.append(f"{scenario.id}.{label}: {decoded}")
        self.assertEqual(broken, [], f"corrupted wiki page names: {broken}")


if __name__ == "__main__":
    unittest.main()
