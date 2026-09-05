import unittest

from conveni_sim.measurement_profiles import (
    checkout_timing_profiles,
    make_arrival_window_sample,
    summarize_numeric,
)
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind


class MeasurementProfileTests(unittest.TestCase):
    def test_numeric_summary_keeps_count_range_mean_and_median(self):
        summary = summarize_numeric((4.0, 8.0, 12.0, 20.0))
        self.assertEqual(summary.sample_count, 4)
        self.assertEqual(summary.minimum, 4.0)
        self.assertEqual(summary.mean, 11.0)
        self.assertEqual(summary.median, 10.0)
        self.assertEqual(summary.maximum, 20.0)

    def test_checkout_profiles_group_by_staff_and_fixture(self):
        timeline = GameplayObservationTimeline("video")
        pairs = (
            ("c1", 10, 14, 100.0, 100.5),
            ("c2", 20, 28, 110.0, 111.0),
        )
        for customer_id, start_minute, end_minute, video_start, video_end in pairs:
            timeline.add(
                ObservationKind.CHECKOUT_SERVICE_START,
                GameTimestamp(1, 1, 1, start_minute),
                video_seconds=video_start,
                customer_id=customer_id,
                staff_id="staff-a",
                fixture_id="register-a",
            )
            timeline.add(
                ObservationKind.CHECKOUT_SERVICE_END,
                GameTimestamp(1, 1, 1, end_minute),
                video_seconds=video_end,
                customer_id=customer_id,
                staff_id="staff-a",
                fixture_id="register-a",
            )

        profile = checkout_timing_profiles(timeline)[0]
        self.assertEqual(profile.staff_id, "staff-a")
        self.assertEqual(profile.fixture_id, "register-a")
        self.assertEqual(profile.game_minutes.sample_count, 2)
        self.assertEqual(profile.game_minutes.minimum, 4.0)
        self.assertEqual(profile.game_minutes.maximum, 8.0)
        self.assertAlmostEqual(profile.video_seconds.mean, 0.75)

    def test_checkout_profile_does_not_require_video_seconds(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id="s1",
            fixture_id="r1",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 5),
            customer_id="c1",
            staff_id="s1",
            fixture_id="r1",
        )
        profile = checkout_timing_profiles(timeline)[0]
        self.assertIsNone(profile.video_seconds)
        self.assertEqual(profile.game_minutes.mean, 5.0)

    def test_arrival_window_rate_is_derived_only_from_explicit_count_and_duration(self):
        timeline = GameplayObservationTimeline("video")
        for minute in (0, 10, 20, 40):
            timeline.add(
                ObservationKind.CUSTOMER_ARRIVAL,
                GameTimestamp.from_hm(1, 1, 1, 9, minute),
                customer_id=f"c{minute}",
            )
        sample = make_arrival_window_sample(
            timeline,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            share_percent=42,
            popularity=55,
            weather="sunny",
            store_open=True,
        )
        self.assertEqual(sample.arrival_count, 4)
        self.assertEqual(sample.arrivals_per_game_hour, 4.0)
        self.assertEqual(sample.share_percent, 42)
        self.assertEqual(sample.popularity, 55)
        self.assertEqual(sample.weather, "sunny")

    def test_arrival_window_rejects_invalid_context_range(self):
        timeline = GameplayObservationTimeline("video")
        with self.assertRaises(ValueError):
            make_arrival_window_sample(
                timeline,
                GameTimestamp.from_hm(1, 1, 1, 9, 0),
                GameTimestamp.from_hm(1, 1, 1, 10, 0),
                share_percent=101,
            )


if __name__ == "__main__":
    unittest.main()
