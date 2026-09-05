# Customer demand, menu hierarchy, and cleaning evidence — 2026-09-05

Scope: first-title PlayStation / Sega Saturn only. This note records newly isolated implementation-relevant evidence and explicitly separates strong observations from hypotheses.

## Evidence labels

- `CONFIRMED-COMMUNITY-PS/SS`: first-title-specific Wiki statement with concrete mechanics/data.
- `DIRECT-PLAY-PS`: detailed PlayStation play record describing an observed action/state.
- `DIRECT-PLAY-SS`: detailed Sega Saturn play record describing an observed action/state.
- `PROVISIONAL-COMMUNITY`: first-title source presents the behavior as likely but not proven.
- `HYPOTHESIS`: plausible interpretation only; do not hard-code without validation.

## 1. Customer demand is not a simple "every product can be a destination" model

The first-title PS/SS Wiki's interior-analysis page records several category-specific observations:

- Oden, steamed buns, warm drinks, frozen foods, and seasonings appear to have no customers who come to the store specifically intending to buy them.
- Bentos and delivery-service application forms appear not to be purchased incidentally / as add-on purchases.
- The Wiki phrases both observations as questions, so these are not formula-level confirmations.

Evidence level: `PROVISIONAL-COMMUNITY`.

Implementation consequence:

Do not model all merchandise with one undifferentiated demand weight. The data model should support at least two independent demand channels:

```text
ProductDemandProfile
- destination_purchase_weight
- incidental_purchase_weight
```

For the categories above, leave exact weights unresolved. Use research flags rather than assigning zero until direct gameplay or guidebook data confirms it.

Suggested provisional flags:

```text
oden.destination_purchase = possibly_none
steamed_bun.destination_purchase = possibly_none
warm_drink.destination_purchase = possibly_none
frozen_food.destination_purchase = possibly_none
seasoning.destination_purchase = possibly_none
bento.incidental_purchase = possibly_none
delivery_form.incidental_purchase = possibly_none
```

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

## 2. Fixture "attention" exists as a distinct concept

The same first-title Wiki records that a 2x2 large wagon has slightly higher `注目度` than a one-tile-width wagon. It further suggests that attention likely affects the probability of add-on purchases.

Evidence split:

- Relative attention difference between large and narrow wagon: `CONFIRMED-COMMUNITY-PS/SS`.
- Attention -> incidental-purchase probability formula: `HYPOTHESIS`.

Implementation consequence:

`FixtureDefinition` should reserve an attention/merchandising field independent from capacity, service, security, and footprint.

```text
FixtureDefinition
- attention_modifier
```

Do not yet assume a linear formula or exact numeric values.

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

## 3. Confirmed menu-hierarchy anchors

### Promotion

The first-title Wiki explicitly states:

```text
販促 -> 宣伝
```

This is stronger than merely knowing that promotion exists and should be represented in the command hierarchy.

Evidence level: `CONFIRMED-COMMUNITY-PS/SS`.

Source:
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D

### Research / overall evaluation

The first-title Wiki explicitly identifies the owner/overall rating used by the advanced scenario as the `総合評価` shown under:

```text
調査 -> 全店収支グラフ
```

Evidence level: `CONFIRMED-COMMUNITY-PS/SS`.

This means `全店収支グラフ` is not merely a finance chart; it also exposes the scenario-relevant overall/owner evaluation.

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

### Other research subcommands already supported by SS play record

A detailed SS play record reports that `調査` can show:

- per-store sales results
- best-selling / wanted-product questionnaire information
- income/expense graphs
- rival-store investigation

Rival-store investigation costs 500,000 yen in that SS record and exposes basic information such as hours and earnings, not the rival store's internal layout.

Evidence level: `DIRECT-PLAY-SS`.

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

The exact ordering and labels of all `調査` children remain unresolved.

## 4. Cleaning-100 behavior: source conflict must stay explicit

A detailed SS play record states that when store cleaning reaches 100, the floor stops becoming dirty.

Evidence level: `DIRECT-PLAY-SS`.

However, the first-title Wiki currently contains wording equivalent to "if store cleaning is 100 or less, dirt appears". Because 100 is the known parameter cap, that wording is internally inconsistent with the rest of the page and likely contains a comparison-sign/editorial error.

Therefore:

- retain `cleaning == 100 prevents floor dirt` as a strong SS observation;
- do **not** promote it to platform-common confirmed behavior until PS evidence or guidebook data is found;
- do not derive a dirt-generation formula from the Wiki sentence as written.

Sources:
- SS direct play record: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- first-title Wiki staff page: https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 5. Bankruptcy timing remains unresolved across evidence

The SS data memo states that if funds are negative at the end of a day, bankruptcy/game over occurs at that point.

Evidence level: `DIRECT-PLAY-SS`.

The same author's narrative episode describes bankruptcy being noticed at the month-end settlement, while PS research has also emphasized the special day-5-to-month-end aggregation. These statements are not sufficient to distinguish whether:

1. solvency is checked after every simulated day,
2. solvency is checked at the monthly aggregated settlement,
3. both checks exist depending on whether the current period is day 1-4 or the skipped remainder.

Implementation status: unresolved. Do not use an instantaneous `cash < 0 => game over` check during arbitrary intra-day transactions.

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 6. PS economic and license anchors re-confirmed

A detailed PS play record confirms the following first-title behavior:

- remodeling to a medium store costs 12,000,000 yen;
- new-store land can be eligible for tobacco/alcohol/medicine before the player actually pays for/acquires those licenses;
- the player can open a small store with only tobacco licensed, then apply for the remaining licenses when remodeling later;
- an inexpensive land + small store + tobacco-only license package was roughly 80,000,000 yen in a developed mid-game town, showing that land inflation dominates total new-store cost later in the scenario;
- rival stores that close can re-open elsewhere quickly, so the 10-store world cap is dynamically contested;
- rival-store investigation costs 500,000 yen in this PS record as well.

Evidence level: `DIRECT-PLAY-PS`.

This last point upgrades the 500,000-yen rival-investigation cost from SS-only observation to PS+SS corroboration.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 7. Research deltas produced by this pass

Newly stronger / implementation-ready:

- `販促 -> 宣伝` menu path.
- `調査 -> 全店収支グラフ` menu path and the location of overall/owner evaluation.
- Rival-store investigation cost = 500,000 yen is now corroborated on both PS and SS records.
- Fixture model requires an independent attention/merchandising field.
- Customer demand model must allow destination purchase and incidental purchase to vary independently by product/category.

Still unresolved:

- exact demand weights / probabilities for the suspected no-destination and no-incidental categories;
- exact attention values and formula;
- exact ordering/full list of `調査` menu children;
- PS confirmation of cleaning-100 dirt suppression;
- exact bankruptcy checkpoint relative to day-end versus month-end aggregation.

## 8. Implementation guidance

These findings are sufficient to shape interfaces/data models but not to freeze formulas. Safe near-term implementation contracts are:

```text
ProductDemandProfile(destinationWeight, incidentalWeight)
FixtureDefinition(..., attentionModifier)
ResearchMenuNode(id, label, children)
SolvencyPolicy(checkpoints)
```

Avoid hard-coding category demand to zero or the dirt/bankruptcy formulas until the unresolved platform/common evidence is closed.
