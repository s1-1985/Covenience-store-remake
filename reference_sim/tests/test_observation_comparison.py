import unittest

from conveni_sim.observation_comparison import (
    ObservationIdentityMapping,
    ObservationTimelineComparator,
)
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)


class ObservationTimelineComparatorTests(unittest.TestCase):
    def test_reports_signed_time_and_numeric_delta_for_explicit_match(self):
        observed = GameplayObservationTimeline("video")
        observed.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            staff_id="s1",
            numeric_value=8,
        )
        simulated = GameplayObservationTimeline("sim")
        simulated.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 10, 2),
            staff_id="s1",
            numeric_value=7,
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(len(result.matched), 1)
        self.assertEqual(result.matched[0].game_minute_delta, 2)
        self.assertEqual(result.matched[0].numeric_delta, -1)
        self.assertEqual(result.kind_counts[0].delta, 0)
        self.assertFalse(result.exact_event_match)

    def test_explicit_identity_mapping_allows_different_annotation_ids(self):
        observed = GameplayObservationTimeline("video")
        observed.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            customer_id="video-customer-A",
            staff_id="video-clerk",
            fixture_id="video-register",
        )
        simulated = GameplayObservationTimeline("sim")
        simulated.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            customer_id="c17",
            staff_id="s1",
            fixture_id="checkout-1",
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
            identity_mapping=ObservationIdentityMapping(
                customer_ids=(("video-customer-A", "c17"),),
                staff_ids=(("video-clerk", "s1"),),
                fixture_ids=(("video-register", "checkout-1"),),
            ),
        )

        self.assertEqual(len(result.matched), 1)
        self.assertEqual(result.unmatched_observed, ())
        self.assertEqual(result.unmatched_simulated, ())
        self.assertTrue(result.exact_event_match)

    def test_different_ids_are_not_guessed_into_correspondence(self):
        observed = GameplayObservationTimeline("video")
        observed.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            customer_id="observed-a",
        )
        simulated = GameplayObservationTimeline("sim")
        simulated.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            customer_id="sim-a",
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(result.matched, ())
        self.assertEqual(len(result.unmatched_observed), 1)
        self.assertEqual(len(result.unmatched_simulated), 1)
        self.assertEqual(result.kind_counts[0].delta, 0)

    def test_missing_events_and_count_delta_are_reported_without_tolerance(self):
        observed = GameplayObservationTimeline("video")
        observed.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 12, 0),
            customer_id="c1",
            fixture_id="checkout",
        )
        simulated = GameplayObservationTimeline("sim")
        simulated.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 12, 1),
            customer_id="c1",
            fixture_id="checkout",
        )
        simulated.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 12, 5),
            customer_id="c2",
            fixture_id="checkout",
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(len(result.matched), 1)
        self.assertEqual(result.matched[0].game_minute_delta, 1)
        self.assertEqual(result.kind_counts[0].observed_count, 1)
        self.assertEqual(result.kind_counts[0].simulated_count, 2)
        self.assertEqual(result.kind_counts[0].delta, 1)
        self.assertEqual(len(result.unmatched_simulated), 1)

    def test_repeated_same_signature_pairs_by_chronological_occurrence(self):
        observed = GameplayObservationTimeline("video")
        simulated = GameplayObservationTimeline("sim")
        for minute in (0, 10):
            observed.add(
                ObservationKind.CHECKOUT_ANGER,
                GameTimestamp.from_hm(1, 1, 1, 10, minute),
                customer_id="c1",
                fixture_id="checkout",
            )
        for minute in (1, 12):
            simulated.add(
                ObservationKind.CHECKOUT_ANGER,
                GameTimestamp.from_hm(1, 1, 1, 10, minute),
                customer_id="c1",
                fixture_id="checkout",
            )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(
            tuple(item.game_minute_delta for item in result.matched),
            (1, 2),
        )

    def test_coverage_excludes_outside_events_from_missing_event_report(self):
        observed = GameplayObservationTimeline("video")
        observed.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 8, 0),
            customer_id="outside",
        )
        observed.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="inside",
        )
        simulated = GameplayObservationTimeline("sim")
        simulated.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="inside",
        )
        simulated.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 18, 0),
            customer_id="sim-outside",
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=9 * 60,
                end_minute_exclusive=17 * 60,
            ),
        )

        self.assertEqual(len(result.matched), 1)
        self.assertEqual(result.unmatched_observed, ())
        self.assertEqual(result.unmatched_simulated, ())
        self.assertTrue(result.exact_event_match)

    def test_mixed_none_and_string_identity_signatures_are_safe_to_compare(self):
        observed = GameplayObservationTimeline("video")
        simulated = GameplayObservationTimeline("sim")
        observed.add(
            ObservationKind.CLEAN_START,
            GameTimestamp.from_hm(1, 1, 1, 11, 0),
            staff_id="s1",
        )
        observed.add(
            ObservationKind.CLEAN_START,
            GameTimestamp.from_hm(1, 1, 1, 11, 1),
            customer_id="unexpected-but-explicit-id",
            staff_id="s1",
        )
        simulated.add(
            ObservationKind.CLEAN_START,
            GameTimestamp.from_hm(1, 1, 1, 11, 0),
            staff_id="s1",
        )

        result = ObservationTimelineComparator().compare(
            observed,
            simulated,
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(len(result.matched), 1)
        self.assertEqual(len(result.unmatched_observed), 1)

    def test_identity_mapping_must_be_one_to_one(self):
        with self.assertRaises(ValueError):
            ObservationIdentityMapping(
                customer_ids=(("o1", "s1"), ("o2", "s1")),
            )
        with self.assertRaises(ValueError):
            ObservationIdentityMapping(
                staff_ids=(("o1", "s1"), ("o1", "s2")),
            )


if __name__ == "__main__":
    unittest.main()
