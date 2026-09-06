import unittest

from conveni_sim.visitor_milestone import (
    ChainVisitorMilestoneRuntime,
    VisitorMilestoneMoment,
)


class ChainVisitorMilestoneRuntimeTests(unittest.TestCase):
    def test_exact_10000_visitors_schedules_free_next_day_midnight_event(self):
        runtime = ChainVisitorMilestoneRuntime()

        event = runtime.observe_total_visitors(
            10_000,
            notified_at=VisitorMilestoneMoment(37, 14),
        )

        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.threshold_visitors, 10_000)
        self.assertEqual(event.popularity_gain, 100)
        self.assertEqual(event.cost_yen, 0)
        self.assertEqual(event.trigger_at, VisitorMilestoneMoment(38, 0))
        self.assertTrue(event.applies_to_current_player_stores)
        self.assertEqual(runtime.next_threshold, 20_000)

    def test_event_does_not_fire_before_next_day_midnight(self):
        runtime = ChainVisitorMilestoneRuntime()
        runtime.observe_total_visitors(
            10_000,
            notified_at=VisitorMilestoneMoment(5, 23),
        )

        self.assertEqual(runtime.pop_due(VisitorMilestoneMoment(5, 23)), ())
        due = runtime.pop_due(VisitorMilestoneMoment(6, 0))
        self.assertEqual(len(due), 1)
        self.assertEqual(runtime.pop_due(VisitorMilestoneMoment(6, 1)), ())

    def test_non_threshold_total_does_not_schedule_event(self):
        runtime = ChainVisitorMilestoneRuntime()

        event = runtime.observe_total_visitors(
            9_999,
            notified_at=VisitorMilestoneMoment(8, 12),
        )

        self.assertIsNone(event)
        self.assertEqual(runtime.events, ())
        self.assertEqual(runtime.next_threshold, 10_000)

    def test_threshold_crossing_without_exact_observation_is_left_unresolved(self):
        runtime = ChainVisitorMilestoneRuntime()
        runtime.observe_total_visitors(
            9_900,
            notified_at=VisitorMilestoneMoment(8, 12),
        )

        with self.assertRaises(ValueError):
            runtime.observe_total_visitors(
                10_050,
                notified_at=VisitorMilestoneMoment(8, 13),
            )

        self.assertEqual(runtime.events, ())
        self.assertEqual(runtime.next_threshold, 10_000)

    def test_targets_are_not_snapshotted_when_event_is_reserved(self):
        runtime = ChainVisitorMilestoneRuntime()

        event = runtime.observe_total_visitors(
            10_000,
            notified_at=VisitorMilestoneMoment(12, 18),
        )

        assert event is not None
        self.assertFalse(hasattr(event, "store_ids"))
        self.assertTrue(event.applies_to_current_player_stores)

    def test_cumulative_total_cannot_decrease(self):
        runtime = ChainVisitorMilestoneRuntime()
        runtime.observe_total_visitors(
            5_000,
            notified_at=VisitorMilestoneMoment(2, 10),
        )

        with self.assertRaises(ValueError):
            runtime.observe_total_visitors(
                4_999,
                notified_at=VisitorMilestoneMoment(2, 11),
            )


if __name__ == "__main__":
    unittest.main()
