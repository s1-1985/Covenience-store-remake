import unittest

from conveni_sim.observation_day_adapter import (
    ObservationDayCoverage,
    ObservationDayMetricAdapter,
)
from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)


class CheckoutPressureDayAdapterTests(unittest.TestCase):
    def make_timeline(self):
        timeline = GameplayObservationTimeline("pressure-adapter")
        for customer_id, base_minute, wait, service in (
            ("c1", 10 * 60, 3, 5),
            ("c2", 12 * 60, 7, 4),
        ):
            timeline.add(
                ObservationKind.CHECKOUT_QUEUE_ENTER,
                GameTimestamp(1, 1, 1, base_minute),
                customer_id=customer_id,
                fixture_id="register",
            )
            timeline.add(
                ObservationKind.CHECKOUT_SERVICE_START,
                GameTimestamp(1, 1, 1, base_minute + wait),
                customer_id=customer_id,
                staff_id="s1",
                fixture_id="register",
            )
            timeline.add(
                ObservationKind.CHECKOUT_SERVICE_END,
                GameTimestamp(1, 1, 1, base_minute + wait + service),
                customer_id=customer_id,
                staff_id="s1",
                fixture_id="register",
            )
        return timeline

    def test_full_day_promotes_only_explicit_duration_maxima(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(reduction.window_max_pre_service_wait_game_minutes, 7)
        self.assertEqual(reduction.window_max_checkout_service_game_minutes, 5)
        self.assertEqual(reduction.window_max_total_checkout_game_minutes, 11)
        self.assertEqual(reduction.comparison_targets.max_pre_service_wait_game_minutes, 7)
        self.assertEqual(reduction.comparison_targets.max_checkout_service_game_minutes, 5)
        self.assertEqual(reduction.comparison_targets.max_total_checkout_game_minutes, 11)

    def test_partial_window_keeps_duration_facts_out_of_full_day_targets(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=11 * 60,
                end_minute_exclusive=13 * 60,
            ),
        )

        self.assertEqual(reduction.window_max_pre_service_wait_game_minutes, 7)
        self.assertEqual(reduction.window_max_checkout_service_game_minutes, 4)
        self.assertEqual(reduction.window_max_total_checkout_game_minutes, 11)
        self.assertIsNone(reduction.comparison_targets.max_pre_service_wait_game_minutes)
        self.assertIsNone(reduction.comparison_targets.max_checkout_service_game_minutes)
        self.assertIsNone(reduction.comparison_targets.max_total_checkout_game_minutes)

    def test_pair_crossing_coverage_boundary_is_not_completed_from_hidden_event(self):
        timeline = GameplayObservationTimeline("boundary-pair")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 9, 59),
            customer_id="c1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 3),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )

        reduction = ObservationDayMetricAdapter().reduce(
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=10 * 60,
                end_minute_exclusive=11 * 60,
            ),
        )

        self.assertIsNone(reduction.window_max_pre_service_wait_game_minutes)
        self.assertEqual(reduction.window_max_checkout_service_game_minutes, 4)
        self.assertIsNone(reduction.window_max_total_checkout_game_minutes)


if __name__ == "__main__":
    unittest.main()
