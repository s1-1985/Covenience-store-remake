from __future__ import annotations

import random
from dataclasses import dataclass, field

from .customer_purchase_policy import CustomerPurchaseContext, CustomerPurchaseDecision

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# customer_purchase_policy.py's CustomerPurchasePolicy protocol deliberately
# exposes no purchase-probability, impulse-buy, or price-elasticity formula
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 41 lists
# "ついで買い確率" and "価格による購入/来店反応" as explicitly un-derivable).
# `CustomerPurchaseContext` also carries no link to a specific customer
# archetype's own 集中力(focus)/価格重視度(price sensitivity)/買物重要度
# stats (CUSTOMER_VISIT_SCHEDULE), since demand generation itself does not
# yet assign an admitted customer session to an archetype. This module is
# therefore a population-average, tagged-guess placeholder rather than a
# per-customer model -- a playable starting point to retune (or replace
# outright if better evidence surfaces) after actual play, per the
# project's "build one, play it, adjust what feels wrong" approach agreed
# for this pass.
PRIMARY_PURCHASE_PROBABILITY = 0.9
"""Chance of buying at merchandise_visit_index == 0 (the customer's first,
presumably destination-driven stop). Not 1.0: even a wanted item might be
skipped if the price feels too high relative to REFERENCE_BUDGET_YEN below."""

IMPULSE_BASE_PROBABILITY = 0.35
"""Chance of buying at any later stop (merchandise_visit_index >= 1), i.e.
"ついで買い" (EXPLICIT_BEHAVIOR: the guide confirms impulse buying exists,
but never gives a rate)."""

REFERENCE_BUDGET_YEN = 1_500
"""A single population-average budget used for price-sensitivity scaling,
anchored to CUSTOMER_VISIT_SCHEDULE's own printed budget_yen column: values
there range 500-20,000 but cluster in the hundreds-to-low-thousands, so 1,500
sits inside the common range rather than at either extreme. Per-visit-row
budgets are not used directly because purchase context carries no archetype
link (see module docstring)."""

PRICE_SENSITIVITY_FLOOR = 0.15
"""However expensive an item is relative to REFERENCE_BUDGET_YEN, its
purchase probability is never scaled below this fraction of the base rate --
an unaffordable-looking item is discouraged, not made impossible, since this
is a population average rather than a real budget check."""


@dataclass
class RemakeBalancedPurchasePolicy:
    """Concrete, tagged-guess CustomerPurchasePolicy (see module docstring)."""

    reference_budget_yen: int = REFERENCE_BUDGET_YEN
    primary_purchase_probability: float = PRIMARY_PURCHASE_PROBABILITY
    impulse_base_probability: float = IMPULSE_BASE_PROBABILITY
    price_sensitivity_floor: float = PRICE_SENSITIVITY_FLOOR
    rng: random.Random = field(default_factory=random.Random)

    def choose_purchase(self, context: CustomerPurchaseContext) -> CustomerPurchaseDecision:
        if not context.offers:
            return CustomerPurchaseDecision.skip()

        priced_offers = [offer for offer in context.offers if offer.unit_sale_price_yen is not None]
        offer = min(priced_offers, key=lambda o: o.unit_sale_price_yen) if priced_offers else context.offers[0]

        is_primary = context.merchandise_visit_index == 0
        probability = self.primary_purchase_probability if is_primary else self.impulse_base_probability

        if offer.unit_sale_price_yen is not None:
            price_ratio = offer.unit_sale_price_yen / self.reference_budget_yen
            price_factor = max(self.price_sensitivity_floor, 1.0 - price_ratio)
            probability *= price_factor

        probability = max(0.0, min(1.0, probability))

        if self.rng.random() >= probability:
            return CustomerPurchaseDecision.skip()

        return CustomerPurchaseDecision.buy(offer.slot_id, quantity=1)
