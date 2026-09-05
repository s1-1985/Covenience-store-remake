import unittest

from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)


class ObservationTimelineTests(unittest.TestCase):
    def test_representative_calendar_minutes_cross_day_and_month(self):
        a = GameTimestamp.from_hm(1, 1, 4, 23, 58)
        b = GameTimestamp.from_hm(1, 2, 1, 0, 2)
        self.assertEqual(a.minutes_until(b), 4)

    def test_customer_arrival_intervals_use_game_time_not_video_ratio(self):
        timeline = GameplayObservationTimeline("video-a")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 6, 3, 13, 16),
            video_seconds=120.0,
            customer_id="c1",
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 6, 3, 13, 24),
            video_seconds=121.7,
            customer_id="c2",
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 6, 3, 13, 40),
            video_seconds=124.2,
            customer_id="c3",
        )

        intervals = timeline.customer_arrival_intervals()
        self.assertEqual([m.game_minutes for m in intervals], [8, 16])
        self.assertAlmostEqual(intervals[0].video_seconds, 1.7)
        self.assertAlmostEqual(intervals[1].video_seconds, 2.5)

    def test_checkout_service_duration_pairs_same_customer_staff_and_fixture(self):
        timeline = GameplayObservationTimeline("video-a")
        start = GameTimestamp.from_hm(1, 6, 3, 14, 0)
        end = GameTimestamp.from_hm(1, 6, 3, 14, 12)
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            start,
            video_seconds=200.0,
            customer_id="c7",
            staff_id="s1",
            fixture_id="register-a",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            end,
            video_seconds=201.5,
            customer_id="c7",
            staff_id="s1",
            fixture_id="register-a",
        )

        measurement = timeline.checkout_service_durations()[0]
        self.assertEqual(measurement.game_minutes, 12)
        self.assertEqual(measurement.video_seconds, 1.5)

    def test_checkout_end_without_start_is_rejected(self):
        timeline = GameplayObservationTimeline("video-a")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id="s1",
            fixture_id="r1",
        )
        with self.assertRaises(ValueError):
            timeline.checkout_service_durations()

    def test_stamina_delta_is_only_difference_between_explicit_snapshots(self):
        timeline = GameplayObservationTimeline("video-b")
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(2, 3, 2, 9, 0),
            staff_id="nagasawa",
            numeric_value=85,
        )
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(2, 3, 2, 10, 0),
            staff_id="nagasawa",
            numeric_value=79,
        )

        delta = timeline.stamina_deltas("nagasawa")[0]
        self.assertEqual(delta.stamina_delta, -6)
        self.assertEqual(delta.game_minutes, 60)

    def test_count_arrivals_uses_half_open_window(self):
        timeline = GameplayObservationTimeline("video-a")
        for minute in (0, 15, 59, 60):
            timeline.add(
                ObservationKind.CUSTOMER_ARRIVAL,
                GameTimestamp(1, 1, 1, 9 * 60 + minute),
                customer_id=f"c{minute}",
            )
        count = timeline.count_arrivals(
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
        )
        self.assertEqual(count, 3)

    def test_game_time_cannot_go_backwards(self):
        timeline = GameplayObservationTimeline("video-a")
        timeline.add(ObservationKind.GAME_CLOCK_SAMPLE, GameTimestamp.from_hm(1, 1, 1, 12, 0))
        with self.assertRaises(ValueError):
            timeline.add(ObservationKind.GAME_CLOCK_SAMPLE, GameTimestamp.from_hm(1, 1, 1, 11, 59))


if __name__ == "__main__":
    unittest.main()
