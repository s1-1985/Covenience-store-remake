import unittest

from conveni_sim.customer_share import (
    CustomerShareInputs,
    CustomerShareRuntime,
    ShareRecalculationReason,
)
from conveni_sim.operating_time import SubdayClock
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class CustomerShareRuntimeTests(unittest.TestCase):
    def test_share_starts_unknown_and_formula_is_not_automatic(self):
        runtime = CustomerShareRuntime(
            CustomerShareInputs(popularity=80, cleaning=90, service=100, weather="sunny")
        )
        self.assertIsNone(runtime.current_share_percent)
        self.assertFalse(runtime.recalculation_pending)

    def test_date_change_marks_recalculation_without_inventing_result(self):
        runtime = CustomerShareRuntime()
        runtime.on_date_change()
        self.assertTrue(runtime.recalculation_pending)
        self.assertEqual(runtime.pending_reasons, (ShareRecalculationReason.DATE_CHANGE,))
        self.assertIsNone(runtime.current_share_percent)

    def test_known_weather_change_marks_recalculation(self):
        runtime = CustomerShareRuntime()
        runtime.observe_weather("sunny")
        self.assertFalse(runtime.recalculation_pending)
        runtime.observe_weather("snow")
        self.assertEqual(runtime.pending_reasons, (ShareRecalculationReason.WEATHER_CHANGE,))

    def test_same_weather_does_not_create_false_refresh(self):
        runtime = CustomerShareRuntime(CustomerShareInputs(weather="rain"))
        runtime.observe_weather("rain")
        self.assertFalse(runtime.recalculation_pending)

    def test_apply_share_records_context_and_clears_pending_reasons(self):
        runtime = CustomerShareRuntime(CustomerShareInputs(popularity=55, weather="cloudy"))
        runtime.on_date_change()
        snapshot = runtime.apply_share(42, source="observed UI")
        self.assertEqual(snapshot.share_percent, 42)
        self.assertEqual(snapshot.inputs.popularity, 55)
        self.assertEqual(snapshot.reasons, (ShareRecalculationReason.DATE_CHANGE,))
        self.assertEqual(runtime.current_share_percent, 42)
        self.assertFalse(runtime.recalculation_pending)

    def test_multiple_crossed_days_are_not_collapsed(self):
        runtime = CustomerShareRuntime()
        runtime.on_date_change(days_crossed=2)
        self.assertEqual(
            runtime.pending_reasons,
            (
                ShareRecalculationReason.DATE_CHANGE,
                ShareRecalculationReason.DATE_CHANGE,
            ),
        )

    def test_input_validation_preserves_unknown_not_zero_semantics(self):
        inputs = CustomerShareInputs()
        self.assertIsNone(inputs.popularity)
        self.assertIsNone(inputs.nearby_population)
        with self.assertRaises(ValueError):
            CustomerShareInputs(popularity=101)
        with self.assertRaises(ValueError):
            CustomerShareInputs(opening_minutes_per_day=1441)


class CustomerShareStoreCompositionTests(unittest.TestCase):
    def test_midnight_crossing_requests_share_recalculation(self):
        store = StoreRuntimeHarness(
            StoreGrid(2, 2),
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(23, 59),
        )
        store.advance_game_minutes(1)
        self.assertEqual(
            store.customer_share.pending_reasons,
            (ShareRecalculationReason.DATE_CHANGE,),
        )

    def test_intra_day_time_advance_does_not_request_share_recalculation(self):
        store = StoreRuntimeHarness(
            StoreGrid(2, 2),
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(12, 0),
        )
        store.advance_game_minutes(30)
        self.assertFalse(store.customer_share.recalculation_pending)

    def test_store_weather_change_requests_share_recalculation(self):
        store = StoreRuntimeHarness(StoreGrid(2, 2), initial_cash_yen=1_000)
        store.observe_weather("clear")
        self.assertFalse(store.customer_share.recalculation_pending)
        store.observe_weather("snow")
        self.assertEqual(
            store.customer_share.pending_reasons,
            (ShareRecalculationReason.WEATHER_CHANGE,),
        )


if __name__ == "__main__":
    unittest.main()
