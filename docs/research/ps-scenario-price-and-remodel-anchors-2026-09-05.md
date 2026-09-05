# PS scenario / pricing / remodel anchors — 2026-09-05

Target: first 1997 PlayStation / Sega Saturn release only. Later-series values are intentionally excluded unless explicitly marked as contamination examples.

## Evidence labels used here

- `DIRECT-PLAY-PS`: detailed first-title PlayStation play record.
- `CONFIRMED-COMMUNITY-PS/SS`: first-title dedicated community source.
- `SS-SPECIFIC`: first-title Sega Saturn evidence; do not silently promote to PS.
- `PROVISIONAL`: useful observation, but not a fixed master value/formula yet.

## 1. Medium-store remodel cost: 12,000,000 yen

A detailed PlayStation intermediate-scenario play record explicitly states that remodeling an existing store to medium size requires **12,000,000 yen**. The same record later repeats that a medium conversion can be done once 12,000,000 yen is available.

Status: `DIRECT-PLAY-PS`

Implementation candidate:

```text
StoreRemodelCost.medium = 12_000_000
source = DIRECT-PLAY-PS
```

This is a remodel-cost anchor, not yet proof that every medium-store orientation/new-build option has the same construction price.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 2. Intermediate scenario victory fires immediately on the 10th store

The same PS play record reaches nine player stores, waits for the rival company to collapse, then opens the tenth store. The victory notification and staff roll occur immediately after the tenth store opens.

This strongly indicates that intermediate victory is evaluated on a **store-count change**, not only at a month boundary or annual evaluation.

Status: `DIRECT-PLAY-PS`

Implementation candidate:

```text
onPlayerStoreOpened():
    if scenario == INTERMEDIATE and activePlayerStoreCount >= 10:
        triggerScenarioVictory()
```

The first-title Wiki independently states that the intermediate goal is ten stores and that player+rival convenience stores cannot exceed ten total.

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 3. Scenario starting rival-store counts: PS observations

Detailed PS records provide additional starting-state anchors:

- Intermediate: the rival begins with **three stores** in the observed run. The player immediately buys two rival branches, leaving the rival main store.
- Advanced: the rival begins with **only its main store** in the observed run.

Status: `DIRECT-PLAY-PS`, but keep these as scenario-map starting-state observations until checked against another PS/SS source or guidebook.

Implementation candidate:

```text
ScenarioStart.intermediate.rivalStoreCount = 3  // provisional PS anchor
ScenarioStart.advanced.rivalStoreCount = 1      // provisional PS anchor
```

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

## 4. Price-control UI accepts at least 5% and 15% discounts on PS

The PS play records explicitly describe changing store price settings to:

- **5% off** in the advanced scenario;
- **15% off** in the intermediate scenario to pressure a rival branch.

Therefore the original price policy is not merely a binary list-price/discount toggle. At minimum, the PS UI supports multiple percentage adjustment values.

Status: `DIRECT-PLAY-PS`

Do not yet infer the exact minimum, maximum or step interval from these two values alone.

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 5. SS pricing exploit gives additional range anchors, but remains SS-specific

A first-title Saturn cheat/strategy source describes changing all products to **20% off** immediately before date change, allowing the day's customer volume to be calculated using the discounted state, then changing the setting to **50% profit** after the daily calculation while retaining the larger customer flow.

This supports two useful SS-specific points:

1. the price-control system can represent at least a 20% discount and a 50% profit setting;
2. customer-flow calculation behaves like a daily snapshot around date change rather than continuously re-evaluating the current price every moment.

Status: `SS-SPECIFIC / PROVISIONAL-FORMULA`

Do not assume PS supports the identical exploit until independently demonstrated.

Source:
- https://menokenkou.work/konbiniura/

## 6. License timing: player can defer some permit purchases until remodel

The intermediate PS play record deliberately chooses a site where tobacco/alcohol/medicine could be applied for, but initially pays only for tobacco because funds are tight. It states that the remaining permit applications can be made when remodeling to medium size.

This reinforces that permit acquisition is available during at least:

- new-store construction; and
- store remodeling.

Status: `DIRECT-PLAY-PS`

It also confirms that eligibility and payment are distinct concepts: a location may be eligible for all three permits while the player chooses to purchase only some of them.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 7. Rival acquisition price is strongly dynamic

PS play observations show acquisition prices changing drastically with time/value:

- first-title Wiki strategy: a rival branch can be around **45,000,000 yen** immediately after game start;
- a long-running intermediate PS game later reports acquisitions around **200,000,000 yen** and **212,000,000 yen**.

Status: `DIRECT-PLAY-PS + CONFIRMED-COMMUNITY-PS/SS`

Conclusion: acquisition cost must not be modeled as a fixed branch price. It likely depends on land/store value and/or business performance. Exact formula remains unresolved.

Sources:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 8. Construction + land dominate late-game new-store cost

The same intermediate PS record estimates that an inexpensive-land, tobacco-only small-store opening can cost roughly **80,000,000 yen** late in the game, and later says even a small-store opening requires over **100,000,000 yen** once cheap land has disappeared.

These are not construction-price masters. They are important evidence that total store-opening cost is composed of large dynamic land costs plus store/permit/setup costs.

Status: `DIRECT-PLAY-PS / PROVISIONAL-ECONOMY`

Therefore do not derive a small-store base construction price from these totals.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## 9. Facility construction is delayed, not instantaneous

The PS beginner play record describes attracting a fire station and then suffering another fire **before the fire station had finished appearing**, explicitly noting that construction takes some time.

Status: `DIRECT-PLAY-PS`

This reinforces the previously recorded town-facility lifecycle:

```text
INDUCED/PLANNED -> construction delay -> ACTIVE
```

Do not make induced facilities take effect immediately.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

## 10. Beginner victory event timing remains month-boundary based

The PS beginner play record reaches population 20,000, then on the following month receives the metropolitan-government arrival message and immediately enters the ending/staff roll.

Status: `DIRECT-PLAY-PS`

Combined with the first-title Wiki statement that the metropolitan government automatically arrives once town population exceeds 20,000, the best current implementation model is:

- monitor the population condition;
- fire the actual government-arrival/victory event at a subsequent month transition.

The exact comparison operator remains unresolved because one source describes 20,000 being reached while the Wiki says "over 20,000".

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 11. Research delta / remaining unknowns

This pass reduces uncertainty in scenario triggers, remodeling cost, price-policy capability, permit timing and rival acquisition economics.

Still unresolved:

- medium-store new-construction price and both orientation dimensions;
- large-store construction/remodel price;
- exact full price-adjustment range and increment;
- exact permit fees and exclusion radii;
- exact rival acquisition-price formula;
- construction delay duration for induced facilities;
- scenario initial layouts/store positions from guidebooks;
- complete product/fixture/staff/building masters.

These remain Priority A guidebook/manual targets.
