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


class CheckoutAngerObservationTests(unittest.TestCase):
    def test_explicit_anger_measures_queue_and_service_elapsed_without_threshold_formula(self):
        timeline = GameplayObservationTimeline("anger-timing")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
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
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 8),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )

        queue_to_anger = timeline.checkout_queue_to_first_anger_durations()
        service_to_anger = timeline.checkout_service_to_first_anger_durations()

        self.assertEqual(len(queue_to_anger), 1)
        self.assertEqual(queue_to_anger[0].game_minutes, 7)
        self.assertEqual(len(service_to_anger), 1)
        self.assertEqual(service_to_anger[0].game_minutes, 4)

    def test_pre_service_anger_does_not_invent_a_serving_staff_measurement(self):
        timeline = GameplayObservationTimeline("pre-service-anger")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 11, 0),
            customer_id="c1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 11, 4),
            customer_id="c1",
            fixture_id="register",
        )

        self.assertEqual(
            timeline.checkout_queue_to_first_anger_durations()[0].game_minutes,
            4,
        )
        self.assertEqual(timeline.checkout_service_to_first_anger_durations(), ())

    def test_full_day_promotes_anger_count_but_partial_clip_does_not(self):
        timeline = GameplayObservationTimeline("anger-count")
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 12, 0),
            customer_id="c2",
            fixture_id="register",
        )

        full = ObservationDayMetricAdapter().reduce(
            timeline,
            ObservationDayCoverage(1, 1, 1),
        )
        partial = ObservationDayMetricAdapter().reduce(
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=9 * 60,
                end_minute_exclusive=11 * 60,
            ),
        )

        self.assertEqual(full.window_checkout_anger_count, 2)
        self.assertEqual(full.comparison_targets.checkout_anger_events, 2)
        self.assertEqual(partial.window_checkout_anger_count, 1)
        self.assertIsNone(partial.comparison_targets.checkout_anger_events)


if __name__ == "__main__":
    unittest.main()
