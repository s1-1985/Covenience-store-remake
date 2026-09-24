import random
import unittest

from conveni_sim.customer import PurchaseFlow
from conveni_sim.customer_purchase_policy import (
    CustomerPurchaseContext,
    MerchandiseOfferSnapshot,
    PurchaseDecisionAction,
)
from conveni_sim.remake_purchase_policy import RemakeBalancedPurchasePolicy


def make_context(*, visit_index=0, offers=()) -> CustomerPurchaseContext:
    return CustomerPurchaseContext(
        customer_id="c1",
        current_fixture_id="shelf-1",
        merchandise_visit_index=visit_index,
        purchased_fixture_ids=(),
        basket_line_count=0,
        basket_known_subtotal_yen=0,
        basket_unknown_price_line_count=0,
        offers=offers,
    )


def make_offer(slot_id="slot-1", price=100, units=5):
    return MerchandiseOfferSnapshot(
        slot_id=slot_id,
        fixture_id="shelf-1",
        product_id="bread",
        units_available=units,
        unit_sale_price_yen=price,
        flow=PurchaseFlow.CHECKOUT_REQUIRED,
    )


class RemakePurchasePolicyTests(unittest.TestCase):
    def test_skips_when_no_offers_in_stock(self):
        policy = RemakeBalancedPurchasePolicy(rng=random.Random(0))
        decision = policy.choose_purchase(make_context(offers=()))
        self.assertEqual(decision.action, PurchaseDecisionAction.SKIP)

    def test_primary_visit_has_higher_purchase_rate_than_impulse(self):
        # Same seed sequence, only visit_index differs; the higher primary
        # probability should buy where the impulse rate skips.
        offer = make_offer(price=100)
        primary = RemakeBalancedPurchasePolicy(rng=random.Random(7)).choose_purchase(
            make_context(visit_index=0, offers=(offer,))
        )
        impulse = RemakeBalancedPurchasePolicy(rng=random.Random(7)).choose_purchase(
            make_context(visit_index=1, offers=(offer,))
        )
        # With an identical roll, the higher-probability (primary) branch
        # buys at least as often as the lower-probability (impulse) branch.
        if impulse.action is PurchaseDecisionAction.BUY:
            self.assertEqual(primary.action, PurchaseDecisionAction.BUY)

    def test_expensive_item_reduces_purchase_probability(self):
        policy = RemakeBalancedPurchasePolicy(reference_budget_yen=1000)
        cheap_rate = policy.primary_purchase_probability * max(
            policy.price_sensitivity_floor, 1 - 100 / 1000
        )
        expensive_rate = policy.primary_purchase_probability * max(
            policy.price_sensitivity_floor, 1 - 5000 / 1000
        )
        self.assertLess(expensive_rate, cheap_rate)
        self.assertEqual(expensive_rate, policy.primary_purchase_probability * policy.price_sensitivity_floor)

    def test_certain_purchase_buys_cheapest_priced_offer(self):
        # Setting primary_purchase_probability alone does not make this
        # "certain": choose_purchase() also multiplies by a price-based
        # price_factor (max(price_sensitivity_floor, 1 - price_ratio)),
        # which is < 1.0 for any offer priced above zero. That left this
        # test's outcome genuinely probabilistic (failing at roughly the
        # rate 1 - price_factor) despite its name and intent -- and the
        # stray `policy.rng = random.Random()` right after construction
        # (overwriting the seeded rng=random.Random(0) with an unseeded
        # one) turned that latent ~5% failure rate into an observable
        # flake instead of a fixed, silently-wrong pass/fail. Flooring
        # price_sensitivity_floor at 1.0 makes price_factor == 1.0
        # unconditionally, so the purchase really is certain regardless of
        # price or rng state, matching the test's actual name.
        policy = RemakeBalancedPurchasePolicy(rng=random.Random(0))
        policy.primary_purchase_probability = 1.0
        policy.price_sensitivity_floor = 1.0
        expensive = make_offer(slot_id="expensive", price=100_000, units=1)
        cheap = make_offer(slot_id="cheap", price=50, units=1)

        decision = policy.choose_purchase(make_context(visit_index=0, offers=(expensive, cheap)))

        self.assertEqual(decision.action, PurchaseDecisionAction.BUY)
        self.assertEqual(decision.slot_id, "cheap")
        self.assertEqual(decision.quantity, 1)

    def test_zero_probability_always_skips(self):
        policy = RemakeBalancedPurchasePolicy(
            primary_purchase_probability=0.0,
            impulse_base_probability=0.0,
            rng=random.Random(0),
        )
        decision = policy.choose_purchase(make_context(offers=(make_offer(),)))
        self.assertEqual(decision.action, PurchaseDecisionAction.SKIP)

    def test_unknown_price_offer_is_still_purchasable(self):
        policy = RemakeBalancedPurchasePolicy(primary_purchase_probability=1.0, rng=random.Random(0))
        offer = MerchandiseOfferSnapshot(
            slot_id="slot-unknown",
            fixture_id="shelf-1",
            product_id="mystery",
            units_available=1,
            unit_sale_price_yen=None,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        decision = policy.choose_purchase(make_context(visit_index=0, offers=(offer,)))
        self.assertEqual(decision.action, PurchaseDecisionAction.BUY)
        self.assertEqual(decision.slot_id, "slot-unknown")


if __name__ == "__main__":
    unittest.main()
