# Research checkpoint — 2026-09-05

This checkpoint records the current completion policy and the immediate continuation plan for the 1997 PS/SS baseline.

## Completion policy

The target is no longer ROM-exact reconstruction. Phase 1 is considered research-complete when every implementation-required specification/master field is populated using, in priority order:

1. 1997 PS/SS strategy guides
2. first-title PS/SS Wiki
3. original PS/SS manual/screens/gameplay
4. detailed first-title play records
5. corroborated inference
6. `remake_balanced_default` for values that remain unrecoverable after reasonable research

Gameplay-affecting values remain high priority. Low-value spelling differences such as staff-name kanji must not block progress.

## Latest Wiki extraction

The first-title Wiki is sufficiently detailed to act as a provisional implementation source, not merely a loose secondary reference.

Recovered examples include:

### Promotion
| Promotion | Cost | Popularity | Trigger |
|---|---:|---:|---|
| Direct mail | 100,000 | +12 | day 2 10:00 |
| Newspaper | 500,000 | +20 | day 2 07:00 |
| Airship | 1,000,000 | +30 | day 3 15:00 |
| Radio | 3,000,000 | +50 | day 1 17:00 |
| TV | 5,000,000 | +100 | day 1 19:00 |

Popularity cap is 100. Cumulative visitor milestones at multiples of 10,000 can trigger the idol one-day-owner event.

### Service fixtures
| Fixture | Service | Size | Maintenance/day |
|---|---:|---:|---:|
| Potted plant | +2 | 1x1 | 120 |
| Bench | +3 | 1x1 | 168 |
| Fountain | +25 | 2x2 | 2,400 |

### Parking
| Parking | Capacity | Size | Maintenance/day |
|---|---:|---:|---:|
| Ground lines | 2 | 1x2 | 0 |
| Two-story | 4 | 1x2 | 240 |
| Tower | 20 | 2x3 | 4,800 |

### Store/layout anchors
- PS small-store variant A construction price: 6,000,000 yen (visual evidence).
- PS small-store variant A editable floor: 8x13 (visual reconstruction).
- Large-store case: 13x14 (first-title Wiki).
- Fixtures have interaction direction/orientation.
- 0.5-tile contact can be sufficient for product interaction, but practical aisles should normally be at least one tile wide.
- Checkout fronts need roughly two tiles to avoid severe congestion.

### Staff
- 35 candidates total.
- Maximum 3 assigned staff per store.
- Hiring stats and runtime/operational skills are separate concepts.
- Hiring: salary, stamina, academic background, agility, sociability.
- Operational: education, register, replenishment, security, cleaning, service.
- Education relates to register/security ceilings.
- Agility relates to replenishment ceiling and rest recovery behavior.
- Sociability relates to cleaning/service ceilings.
- Manager education affects subordinate growth.
- Hiring salary is daily salary at a 24-hour baseline; shorter hours reduce effective salary, exact formula still unresolved.

### Time/economy behavior
- Real-time simulation: days 1-4 each month.
- Day 5 onward is skipped/aggregated to month end.
- Customer share is recalculated at date change and can be recalculated on weather changes.
- Closing across midnight can produce effectively zero share for the next day.
- During closed hours many operating costs including labor are not charged, while staff can still clean/replenish; replenishment purchases still cost money.

### Scenarios/town
- Beginner initial assets: 200,000,000 yen; metropolitan-government objective, with population >20,000 reported as automatic trigger.
- Intermediate initial assets: 150,000,000 yen; objective 10 stores.
- Advanced initial assets: 150,000,000 yen; objective owner rating 5 stars.
- Player+rival store count cap: 10.
- Station reported to appear above town population 5,000.
- Station population/display value: 2,240.
- Advanced evaluation is currently modeled as `AnnualEvaluation`, likely January-based.

## Product-category anchors

Ambient: bentos, bread, retort foods, snacks, instant foods, daily necessities, stationery, appliances, magazines, underwear, medicine, seasonings.

Refrigerated: drinks, alcohol, bentos, medicine, meat, fish, vegetables.

Frozen: ice cream, frozen foods.

Dedicated/service grouping observed in PS play records includes cold/hot drinks, alcohol, tobacco, event goods, oden, steamed buns, warm drinks, ATM, copier, checkout, break room, fountain, plant/tree, parking and seating.

`ProductCategory` and `FixtureType` must remain separate with compatibility mappings.

## Remaining high-priority gaps

1. All six store variants: construction/remodel price and editable-floor dimensions.
2. Complete fixture master: purchase price, maintenance, footprint, capacity, orientation/interaction side, service/security effects.
3. Complete product master: category, retail/procurement values, capacity/compatibility and demand-related values.
4. Complete numeric table for all 35 staff.
5. Tobacco/alcohol/medicine permit fees and competition-distance rule.
6. Complete town-building master: shopping population, induction cost, effects, appearance conditions.
7. Customer-share formula or tuned first-title-compatible approximation.
8. Month-end aggregation and operating-cost formulas.
9. Event probabilities/conditions.
10. Remaining PS/SS differences.

## Guidebook targets

Priority A:
- ISBN 9784575160499 — 必勝攻略法; PS/SS; advertises complete data and all maps.
- ISBN 9784895637862 — Game Fan Books 41; PS/SS.
- ISBN 9784796611992 — 攻略の帝王; Chapter 4 is コンビニ経営資料集; physical listings identify PS/SS.
- ISBN 9784889914344 — レイアウトデザインセレクション74; includes data list; multiple physical listings identify SS/PS.
- ISBN 9784063292862 — 店舗拡大ガイドブック; PS/SS.

Priority B:
- ISBN 9784916090812 — 完全研究; all-platform cross-check.

## Immediate continuation rule

When the user says to continue, do not stop at acknowledgement. In the same turn:

1. search the complete first-title Wiki/page links for remaining numeric tables and conditions;
2. search current used-book/listing images for interior strategy-guide pages;
3. convert recovered facts toward implementation-ready master structures (`FixtureDefinition`, `ProductDefinition`, `StaffDefinition`, `TownBuildingDefinition`, etc.);
4. after reasonable search, fill genuinely unrecoverable fields with explicitly tagged `remake_balanced_default` values rather than stalling;
5. commit research/data changes through a fresh branch, PR, diff review and squash merge.

## Contamination warning

Do not silently import data from The Conveni 2/3/200X/DS/SP. Known sequel values such as 5x8/7x10/9x12 store dimensions, a 4-day x8 monthly formula, police/fire numeric bonuses, or later-title permit fees are not original-title facts. If later-title values are ever deliberately used as balancing inspiration, record them only as remake defaults.

## Key sources

- https://wikiwiki.jp/theconveni1/
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://minkara.carview.co.jp/userid/2518797/blog/40357970/
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://psinstructionmanual.com/theconveni/
