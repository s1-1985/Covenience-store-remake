import unittest

from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)


class CheckoutPressureObservationTests(unittest.TestCase):
    def test_explicit_queue_start_end_measure_wait_service_and_total(self):
        timeline = GameplayObservationTimeline("checkout-pressure")
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
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 8),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )

        waits = timeline.checkout_queue_wait_durations()
        services = timeline.checkout_service_durations()
        totals = timeline.checkout_total_durations()

        self.assertEqual(len(waits), 1)
        self.assertEqual(waits[0].game_minutes, 3)
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].game_minutes, 5)
        self.assertEqual(len(totals), 1)
        self.assertEqual(totals[0].game_minutes, 8)

    def test_missing_queue_enter_does_not_invent_wait_or_total(self):
        timeline = GameplayObservationTimeline("service-only")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 11, 0),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 11, 4),
            customer_id="c1",
            staff_id="s1",
            fixture_id="register",
        )

        self.assertEqual(timeline.checkout_queue_wait_durations(), ())
        self.assertEqual(timeline.checkout_total_durations(), ())
        self.assertEqual(timeline.checkout_service_durations()[0].game_minutes, 4)


if __name__ == "__main__":
    unittest.main()
