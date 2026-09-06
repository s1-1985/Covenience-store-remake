import unittest

from conveni_sim.baseline_data import PROMOTIONS
from conveni_sim.economy import FinancialEventKind, StoreCashLedger
from conveni_sim.promotion import (
    PromotionMoment,
    PromotionScheduler,
    StorePopularityRuntime,
    apply_confirmed_triggered_promotion,
)


class PromotionSchedulerTests(unittest.TestCase):
    def make_scheduler(self):
        return PromotionScheduler(PROMOTIONS)

    def test_known_trigger_time_is_taken_from_baseline_definition(self):
        scheduler = self.make_scheduler()
        scheduled = scheduler.schedule(
            "radio",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        self.assertEqual(scheduled.trigger_at, PromotionMoment(1, 1, 1, 17))

    def test_promotion_is_not_immediate(self):
        scheduler = self.make_scheduler()
        scheduler.schedule(
            "direct_mail",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        self.assertEqual(scheduler.pop_due(PromotionMoment(1, 1, 2, 9)), ())
        due = scheduler.pop_due(PromotionMoment(1, 1, 2, 10))
        self.assertEqual(tuple(item.promotion_id for item in due), ("direct_mail",))

    def test_each_method_can_be_scheduled_once_per_month(self):
        scheduler = self.make_scheduler()
        scheduler.schedule(
            "tv",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        with self.assertRaises(ValueError):
            scheduler.schedule(
                "tv",
                target_year=1,
                target_month=1,
                scheduled_at=PromotionMoment(1, 1, 1, 1),
            )

    def test_different_methods_can_be_scheduled_in_same_month(self):
        scheduler = self.make_scheduler()
        scheduler.schedule(
            "radio",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        scheduler.schedule(
            "tv",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        self.assertEqual(len(scheduler.scheduled), 2)

    def test_late_same_month_scheduling_is_left_unresolved(self):
        scheduler = self.make_scheduler()
        with self.assertRaises(ValueError):
            scheduler.schedule(
                "radio",
                target_year=1,
                target_month=1,
                scheduled_at=PromotionMoment(1, 1, 1, 18),
            )

    def test_cross_month_advance_booking_is_left_unresolved(self):
        scheduler = self.make_scheduler()
        with self.assertRaises(ValueError):
            scheduler.schedule(
                "newspaper",
                target_year=1,
                target_month=2,
                scheduled_at=PromotionMoment(1, 1, 4, 20),
            )


class StorePopularityRuntimeTests(unittest.TestCase):
    def test_video_confirmed_direct_mail_event_charges_and_affects_all_stores(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=42)
        popularity.add_store("branch", popularity=37)
        ledger = StoreCashLedger(7_430_572)
        scheduler.schedule(
            "direct_mail",
            target_year=1,
            target_month=9,
            scheduled_at=PromotionMoment(1, 9, 2, 9),
        )
        due = scheduler.pop_due(PromotionMoment(1, 9, 2, 10))[0]

        result = apply_confirmed_triggered_promotion(
            due,
            scheduler,
            popularity,
            ledger,
            target_store_ids=("main", "branch"),
        )

        self.assertEqual(popularity.popularity("main"), 54)
        self.assertEqual(popularity.popularity("branch"), 49)
        self.assertEqual(ledger.known_cash_yen, 7_330_572)
        self.assertEqual(result.payment_event.kind, FinancialEventKind.PROMOTION)
        self.assertEqual(result.payment_event.amount_yen, 100_000)

    def test_composed_payment_refuses_methods_with_unknown_timing(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=20)
        ledger = StoreCashLedger(10_000_000)
        scheduler.schedule(
            "newspaper",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        due = scheduler.pop_due(PromotionMoment(1, 1, 2, 7))[0]

        with self.assertRaises(ValueError):
            apply_confirmed_triggered_promotion(
                due,
                scheduler,
                popularity,
                ledger,
                target_store_ids=("main",),
            )

        self.assertEqual(popularity.popularity("main"), 20)
        self.assertEqual(ledger.events, ())

    def test_composed_direct_mail_validates_all_stores_before_charging(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=42)
        ledger = StoreCashLedger(7_430_572)
        scheduler.schedule(
            "direct_mail",
            target_year=1,
            target_month=9,
            scheduled_at=PromotionMoment(1, 9, 2, 9),
        )
        due = scheduler.pop_due(PromotionMoment(1, 9, 2, 10))[0]

        with self.assertRaises(KeyError):
            apply_confirmed_triggered_promotion(
                due,
                scheduler,
                popularity,
                ledger,
                target_store_ids=("main", "unknown-branch"),
            )

        self.assertEqual(popularity.popularity("main"), 42)
        self.assertEqual(ledger.known_cash_yen, 7_430_572)
        self.assertEqual(ledger.events, ())
        self.assertFalse(due.applied)

    def test_promotion_applies_to_supplied_current_store_set(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=20)
        popularity.add_store("branch", popularity=95)
        scheduled = scheduler.schedule(
            "newspaper",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        due = scheduler.pop_due(PromotionMoment(1, 1, 2, 7))[0]

        result = popularity.apply_promotion(
            due,
            scheduler,
            target_store_ids=("main", "branch"),
        )

        self.assertEqual(popularity.popularity("main"), 40)
        self.assertEqual(popularity.popularity("branch"), 100)
        by_store = {change.store_id: change for change in result.changes}
        self.assertEqual(by_store["main"].applied_gain, 20)
        self.assertEqual(by_store["branch"].applied_gain, 5)

    def test_popularity_gain_cannot_exceed_100(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=20)
        scheduler.schedule(
            "tv",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        due = scheduler.pop_due(PromotionMoment(1, 1, 1, 19))[0]
        popularity.apply_promotion(due, scheduler, target_store_ids=("main",))
        self.assertEqual(popularity.popularity("main"), 100)

    def test_unfired_promotion_cannot_be_applied(self):
        scheduler = PromotionScheduler(PROMOTIONS)
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=20)
        scheduled = scheduler.schedule(
            "airship",
            target_year=1,
            target_month=1,
            scheduled_at=PromotionMoment(1, 1, 1, 0),
        )
        with self.assertRaises(ValueError):
            popularity.apply_promotion(scheduled, scheduler, target_store_ids=("main",))


if __name__ == "__main__":
    unittest.main()
