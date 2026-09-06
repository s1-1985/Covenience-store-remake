import unittest

from conveni_sim.observation_day_adapter import (
    ObservationDayCoverage,
    ObservationDayMetricAdapter,
    ObservationDayMetricMapping,
)
from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)


class ObservationDayAdapterTests(unittest.TestCase):
    def make_timeline(self):
        timeline = GameplayObservationTimeline("V03-test")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 9, 0),
            customer_id="c1",
        )
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 9, 10),
            staff_id="s1",
            numeric_value=10,
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 12, 0),
            customer_id="c2",
        )
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 13, 0),
            staff_id="s1",
            numeric_value=8,
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 14, 0),
            customer_id="c1",
            staff_id="s1",
            fixture_id="checkout",
        )
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 18, 0),
            staff_id="s1",
            numeric_value=9,
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 2, 9, 0),
            customer_id="next-day",
        )
        return timeline

    def test_full_day_maps_only_semantics_explicitly_asserted_by_researcher(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationDayMetricMapping(
                customer_arrival_means_admitted=True,
                checkout_service_end_means_completed_sale=True,
            ),
        )

        self.assertEqual(reduction.window_arrival_count, 2)
        self.assertEqual(reduction.window_checkout_service_end_count, 1)
        self.assertEqual(reduction.window_staff_minimums[0].minimum_stamina, 8)
        self.assertEqual(reduction.comparison_targets.admitted_arrivals, 2)
        self.assertEqual(reduction.comparison_targets.completed_checkout_sales, 1)
        self.assertEqual(reduction.comparison_targets.staff_minimums[0].minimum_stamina, 8)
        self.assertIsNone(reduction.comparison_targets.attempted_arrivals)
        self.assertIsNone(reduction.comparison_targets.known_checkout_revenue_yen)

    def test_full_day_does_not_assume_arrival_or_checkout_event_semantics(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 1),
        )

        self.assertEqual(reduction.window_arrival_count, 2)
        self.assertEqual(reduction.window_checkout_service_end_count, 1)
        self.assertIsNone(reduction.comparison_targets.admitted_arrivals)
        self.assertIsNone(reduction.comparison_targets.completed_checkout_sales)
        self.assertEqual(reduction.comparison_targets.staff_minimums[0].minimum_stamina, 8)

    def test_partial_window_is_summarized_but_not_promoted_to_full_day_targets(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=8 * 60,
                end_minute_exclusive=12 * 60,
            ),
            mapping=ObservationDayMetricMapping(
                customer_arrival_means_admitted=True,
                checkout_service_end_means_completed_sale=True,
            ),
        )

        self.assertEqual(reduction.window_arrival_count, 1)
        self.assertEqual(reduction.window_checkout_service_end_count, 0)
        self.assertEqual(reduction.window_staff_minimums[0].minimum_stamina, 10)
        self.assertIsNone(reduction.comparison_targets.admitted_arrivals)
        self.assertIsNone(reduction.comparison_targets.completed_checkout_sales)
        self.assertEqual(reduction.comparison_targets.staff_minimums, ())

    def test_events_from_other_representative_days_are_excluded(self):
        reduction = ObservationDayMetricAdapter().reduce(
            self.make_timeline(),
            ObservationDayCoverage(1, 1, 2),
            mapping=ObservationDayMetricMapping(customer_arrival_means_admitted=True),
        )

        self.assertEqual(reduction.window_arrival_count, 1)
        self.assertEqual(reduction.comparison_targets.admitted_arrivals, 1)

    def test_non_integral_stamina_snapshot_is_rejected_instead_of_rounded(self):
        timeline = GameplayObservationTimeline("bad-stamina")
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            staff_id="s1",
            numeric_value=8.5,
        )

        with self.assertRaises(ValueError):
            ObservationDayMetricAdapter().reduce(
                timeline,
                ObservationDayCoverage(1, 1, 1),
            )


if __name__ == "__main__":
    unittest.main()
