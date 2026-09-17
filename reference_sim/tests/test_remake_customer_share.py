import unittest

from conveni_sim.customer_share import CustomerShareInputs
from conveni_sim.remake_customer_share import compute_customer_share_percent


class RemakeCustomerShareTests(unittest.TestCase):
    def test_none_when_nothing_is_known(self):
        self.assertIsNone(compute_customer_share_percent(CustomerShareInputs()))

    def test_all_100_inputs_score_100(self):
        inputs = CustomerShareInputs(
            popularity=100,
            service=100,
            cleaning=100,
            security=100,
            assortment_product_ids=tuple(f"p{i}" for i in range(30)),
            opening_minutes_per_day=1440,
        )
        self.assertEqual(compute_customer_share_percent(inputs), 100)

    def test_all_zero_inputs_score_0(self):
        inputs = CustomerShareInputs(
            popularity=0,
            service=0,
            cleaning=0,
            security=0,
            assortment_product_ids=(),
            opening_minutes_per_day=0,
        )
        self.assertEqual(compute_customer_share_percent(inputs), 0)

    def test_unknown_factors_are_excluded_not_treated_as_zero(self):
        low_confidence = compute_customer_share_percent(CustomerShareInputs(popularity=80))
        # Only the known factor (popularity) is averaged; it should score
        # near 80, not be dragged toward 0 by the four unknown factors.
        self.assertEqual(low_confidence, 80)

    def test_more_rivals_reduces_score(self):
        base = CustomerShareInputs(popularity=80, service=80)
        with_rivals = CustomerShareInputs(popularity=80, service=80, competing_store_ids=("r1", "r2", "r3"))

        self.assertLess(
            compute_customer_share_percent(with_rivals),
            compute_customer_share_percent(base),
        )

    def test_bad_weather_reduces_score(self):
        base = CustomerShareInputs(popularity=80, service=80)
        rainy = CustomerShareInputs(popularity=80, service=80, weather="大雨")

        self.assertLess(compute_customer_share_percent(rainy), compute_customer_share_percent(base))

    def test_result_stays_within_0_and_100(self):
        inputs = CustomerShareInputs(popularity=100, service=100, competing_store_ids=("r1",) * 20)
        result = compute_customer_share_percent(inputs)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)


if __name__ == "__main__":
    unittest.main()
