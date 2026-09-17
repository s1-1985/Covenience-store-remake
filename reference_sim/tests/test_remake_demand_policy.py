import random
import unittest

from conveni_sim.customer_demand import CustomerDemandContext
from conveni_sim.customer_share import CustomerShareInputs
from conveni_sim.remake_demand_policy import RemakeBalancedDemandPolicy
from conveni_sim.store_grid import GridPoint


def make_context(**share_kwargs) -> CustomerDemandContext:
    return CustomerDemandContext(
        absolute_minute=0,
        minute_of_day=600,
        elapsed_days=0,
        store_open=True,
        customer_share_percent=share_kwargs.pop("customer_share_percent", 50),
        share_inputs=CustomerShareInputs(**share_kwargs),
    )


class RemakeDemandPolicyRateTests(unittest.TestCase):
    def make_policy(self, **kwargs):
        return RemakeBalancedDemandPolicy(
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 0),
            **kwargs,
        )

    def test_none_when_population_or_share_unknown(self):
        policy = self.make_policy()
        self.assertIsNone(policy.expected_arrivals_per_minute(make_context(customer_share_percent=None)))
        self.assertIsNone(
            policy.expected_arrivals_per_minute(
                CustomerDemandContext(
                    absolute_minute=0,
                    minute_of_day=0,
                    elapsed_days=0,
                    store_open=True,
                    customer_share_percent=50,
                    share_inputs=CustomerShareInputs(nearby_population=None),
                )
            )
        )

    def test_higher_share_and_population_increase_rate(self):
        policy = self.make_policy()
        low = policy.expected_arrivals_per_minute(
            make_context(customer_share_percent=10, nearby_population=1000)
        )
        high = policy.expected_arrivals_per_minute(
            make_context(customer_share_percent=90, nearby_population=1000)
        )
        self.assertLess(low, high)

    def test_bad_weather_reduces_rate(self):
        policy = self.make_policy()
        clear = policy.expected_arrivals_per_minute(
            make_context(nearby_population=1000, weather="快晴")
        )
        rainy = policy.expected_arrivals_per_minute(
            make_context(nearby_population=1000, weather="大雨")
        )
        self.assertLess(rainy, clear)

    def test_falls_back_to_default_opening_minutes_when_unknown(self):
        policy = self.make_policy()
        rate = policy.expected_arrivals_per_minute(
            make_context(nearby_population=1000, opening_minutes_per_day=None)
        )
        self.assertIsNotNone(rate)
        self.assertGreater(rate, 0)


class RemakeDemandPolicyArrivalsTests(unittest.TestCase):
    def test_closed_store_never_admits(self):
        policy = RemakeBalancedDemandPolicy(
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(1, 1),
            rng=random.Random(0),
        )
        context = CustomerDemandContext(
            absolute_minute=0,
            minute_of_day=0,
            elapsed_days=0,
            store_open=False,
            customer_share_percent=90,
            share_inputs=CustomerShareInputs(nearby_population=100_000),
        )
        self.assertEqual(policy.arrivals_for(context), ())

    def test_zero_rate_produces_no_arrivals(self):
        policy = RemakeBalancedDemandPolicy(
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(1, 1),
            rng=random.Random(0),
        )
        context = make_context(nearby_population=0)
        self.assertEqual(policy.arrivals_for(context), ())

    def test_certain_arrival_produces_one_customer_with_configured_layout(self):
        policy = RemakeBalancedDemandPolicy(
            entry_point=GridPoint(2, 3),
            exit_point=GridPoint(4, 5),
            merchandise_fixture_ids=("shelf-1",),
            checkout_fixture_id="checkout",
            daily_visit_rate_per_population=1_000_000,  # force rate >= 1
            rng=random.Random(0),
        )
        context = make_context(nearby_population=1000, customer_share_percent=100)

        arrivals = policy.arrivals_for(context)

        self.assertEqual(len(arrivals), 1)
        intent = arrivals[0]
        self.assertEqual(intent.entry_point, GridPoint(2, 3))
        self.assertEqual(intent.exit_point, GridPoint(4, 5))
        self.assertEqual(intent.merchandise_fixture_ids, ("shelf-1",))
        self.assertEqual(intent.checkout_fixture_id, "checkout")

    def test_sequential_arrivals_get_distinct_customer_ids(self):
        policy = RemakeBalancedDemandPolicy(
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(1, 1),
            daily_visit_rate_per_population=1_000_000,
            rng=random.Random(0),
        )
        context = make_context(nearby_population=1000, customer_share_percent=100)

        first = policy.arrivals_for(context)[0]
        second = policy.arrivals_for(context)[0]

        self.assertNotEqual(first.customer_id, second.customer_id)


if __name__ == "__main__":
    unittest.main()
