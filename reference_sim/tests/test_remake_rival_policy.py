import unittest

from conveni_sim.remake_rival_policy import (
    RemakeBalancedRivalPolicy,
    RivalDecision,
    RivalPolicyInputs,
)
from conveni_sim.remake_town_spatial import trade_area_overlap_ratio


def make_inputs(**overrides):
    defaults = dict(
        cash_yen=10_000_000,
        monthly_profit_yen=100_000,
        own_popularity=50,
        rival_popularity=50,
        own_service_value=50.0,
        rival_service_value=50.0,
        trade_area_overlap_ratio=1.0,
    )
    defaults.update(overrides)
    return RivalPolicyInputs(**defaults)


class RivalPolicyInputsValidationTests(unittest.TestCase):
    def test_own_popularity_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            make_inputs(own_popularity=101)
        with self.assertRaises(ValueError):
            make_inputs(own_popularity=-1)

    def test_rival_popularity_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            make_inputs(rival_popularity=101)
        with self.assertRaises(ValueError):
            make_inputs(rival_popularity=-1)

    def test_trade_area_overlap_ratio_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            make_inputs(trade_area_overlap_ratio=1.1)
        with self.assertRaises(ValueError):
            make_inputs(trade_area_overlap_ratio=-0.1)

    def test_boundary_values_accepted(self):
        make_inputs(own_popularity=0, rival_popularity=100, trade_area_overlap_ratio=0.0)
        make_inputs(own_popularity=100, rival_popularity=0, trade_area_overlap_ratio=1.0)


class RemakeBalancedRivalPolicyDecisionTests(unittest.TestCase):
    def setUp(self):
        self.policy = RemakeBalancedRivalPolicy()

    def test_losing_money_under_heavy_pressure_retreats(self):
        inputs = make_inputs(
            monthly_profit_yen=-50_000,
            own_popularity=10,
            rival_popularity=90,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=1.0,
        )
        self.assertEqual(self.policy.decide(inputs), RivalDecision.RETREAT)

    def test_losing_money_with_no_overlap_never_retreats_on_pressure_alone(self):
        # trade_area_overlap_ratio=0.0 neutralizes competitive pressure
        # regardless of the popularity/service gap.
        inputs = make_inputs(
            monthly_profit_yen=-50_000,
            own_popularity=10,
            rival_popularity=90,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=0.0,
        )
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)

    def test_profitable_with_cash_and_low_pressure_expands(self):
        inputs = make_inputs(
            monthly_profit_yen=500_000,
            cash_yen=25_000_000,
            own_popularity=90,
            rival_popularity=10,
            own_service_value=90.0,
            rival_service_value=10.0,
            trade_area_overlap_ratio=1.0,
        )
        self.assertEqual(self.policy.decide(inputs), RivalDecision.EXPAND)

    def test_profitable_but_insufficient_cash_holds_instead_of_expanding(self):
        inputs = make_inputs(
            monthly_profit_yen=500_000,
            cash_yen=1_000_000,
            own_popularity=90,
            rival_popularity=10,
            own_service_value=90.0,
            rival_service_value=10.0,
            trade_area_overlap_ratio=1.0,
        )
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)

    def test_profitable_with_cash_but_under_pressure_holds_instead_of_expanding(self):
        inputs = make_inputs(
            monthly_profit_yen=500_000,
            cash_yen=25_000_000,
            own_popularity=90,
            rival_popularity=10,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=1.0,
        )
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)

    def test_break_even_profit_holds(self):
        inputs = make_inputs(monthly_profit_yen=0)
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)

    def test_equal_footing_holds(self):
        inputs = make_inputs()
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)


class SpatialTradeAreaOverlapIntegrationTests(unittest.TestCase):
    """Task #58: `RivalPolicyInputs.trade_area_overlap_ratio` was always a
    caller-supplied abstract float -- decision 0095 explicitly declined to
    build the spatial layer that would compute it from real store
    positions, since no rival entity/position existed yet. remake_town_
    spatial.py now provides that computation; these tests are the first
    actual caller wiring a real (position, radius) pair into this policy,
    closing the gap decision 0095 left open rather than leaving this
    module's spatial input permanently unreachable."""

    def setUp(self) -> None:
        self.policy = RemakeBalancedRivalPolicy()

    def test_far_apart_stores_have_no_competitive_pressure_regardless_of_the_gap(self):
        ratio = trade_area_overlap_ratio((0, 0), 20, (1000, 0), 20)
        inputs = make_inputs(
            own_popularity=10,
            rival_popularity=90,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=ratio,
        )
        # A losing-badly store with a losing-money branch still does not
        # retreat if the two stores are too far apart to actually compete.
        inputs_losing = make_inputs(
            monthly_profit_yen=-1,
            own_popularity=10,
            rival_popularity=90,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=ratio,
        )
        self.assertEqual(ratio, 0.0)
        self.assertEqual(self.policy.decide(inputs), RivalDecision.HOLD)
        self.assertEqual(self.policy.decide(inputs_losing), RivalDecision.HOLD)

    def test_fully_overlapping_stores_let_a_losing_branch_retreat(self):
        ratio = trade_area_overlap_ratio((0, 0), 20, (0, 0), 20)
        inputs = make_inputs(
            monthly_profit_yen=-1,
            own_popularity=10,
            rival_popularity=90,
            own_service_value=10.0,
            rival_service_value=90.0,
            trade_area_overlap_ratio=ratio,
        )
        self.assertEqual(ratio, 1.0)
        self.assertEqual(self.policy.decide(inputs), RivalDecision.RETREAT)


if __name__ == "__main__":
    unittest.main()
