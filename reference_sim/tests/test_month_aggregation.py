import unittest

from conveni_sim.month_aggregation import MONTH_MULTIPLIER, aggregate_representative_days_to_month


class MonthAggregationTests(unittest.TestCase):
    def test_multiplies_by_8(self):
        self.assertEqual(MONTH_MULTIPLIER, 8)
        self.assertEqual(aggregate_representative_days_to_month(100_000), 800_000)

    def test_handles_negative_net_result(self):
        self.assertEqual(aggregate_representative_days_to_month(-50_000), -400_000)

    def test_zero_stays_zero(self):
        self.assertEqual(aggregate_representative_days_to_month(0), 0)


if __name__ == "__main__":
    unittest.main()
