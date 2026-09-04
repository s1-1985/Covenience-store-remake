# Convenience Store Remake — Project Memory

Last updated: 2026-09-05 (JST)

This file is the canonical memory checkpoint for the project. If chat context is lost, start by reading this file and the files under `docs/research/`.

## 1. Project goal

- Target: Android smartphone game.
- Development method: GitHub is the source of truth for code, research, decisions, handoff notes, and later generated assets.
- Baseline design target: reproduce the gameplay structure and feel of the first home-console version of **『ザ・コンビニ ～あの町を独占せよ～』**, released for PlayStation / Sega Saturn in 1997, as closely as practical.
- After the baseline is playable, add original systems and modernization step by step.
- Do not reuse original copyrighted game assets, logos, music, text dumps, or sprites. Visual/audio assets for this project should be newly created.
- The previous project `Convenience-store-Frontier` is reference material only. Do not import its architecture blindly.

## 2. Why PS/SS 1997 is the baseline

The original Windows release dates to 1996, but the PlayStation / Sega Saturn release is much easier to research today and is the version most surviving strategy material discusses. The current official Console Archives release also preserves the Japanese PlayStation ROM.

Official source:
- PlayStation Store / Console Archives: https://store.playstation.com/ja-jp/concept/10017477

Community research explicitly states that its data is for the PS/SS version, not the PC version:
- https://wikiwiki.jp/theconveni1/

## 3. Confirmed high-level game loop

The core loop is not just spreadsheet-like management. It combines a city map, store construction, free interior layout, autonomous customer/staff simulation, store-chain expansion, competitor pressure, and city development.

Approximate loop:

1. Inspect town and surrounding population/facilities.
2. Select store location / construct store.
3. Place fixtures, checkout counters, service objects, parking, etc.
4. Choose products and business policies.
5. Hire and allocate staff.
6. Open the store.
7. Customers physically enter, walk to products, queue, buy, and leave.
8. Staff autonomously operate checkout, replenish, clean, recover stamina, etc.
9. Observe congestion, sales, customer complaints, security risk, stock/assortment issues.
10. Improve layout / prices / products / staff / promotion.
11. Open branches, compete with rival stores, acquire rival branches, and influence town development.

Sources:
- https://dengekionline.com/elem/000/000/722/722919/
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://wikiwiki.jp/theconveni1/

## 4. Store view and layout — confirmed details

- The first console title uses a top-down 2D store view.
- Customer and employee pathing is materially affected by fixture placement.
- Congestion can become severe enough to destroy sales.
- At least 1 tile of passage is recommended in normal aisles; checkout fronts need around 2 tiles.
- Multiple routes can allow customers to detour around congestion.
- Some fixtures have a valid interaction side/direction.
- Fixtures can be rotated.
- Popular goods being placed deeper in the store can influence traffic flow.
- Large store layout data includes a 13 x 14 case; the community notes a cursor bug in one orientation.

Confirmed service fixtures:
- Potted plant: service +2, size 1x1, maintenance 120 yen/day.
- Bench: service +3, size 1x1, maintenance 168 yen/day.
- Fountain: service +25, size 2x2, maintenance 2,400 yen/day.

Confirmed parking:
- Ground parking: 2 cars, size 1x2, maintenance 0/day.
- Two-story parking: 4 cars, size 1x2, maintenance 240/day.
- Tower parking: 20 cars, size 2x3, maintenance 4,800/day.

Research source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

Visual evidence (Dengeki PlayStation screenshots):
- https://dengekionline.com/elem/000/000/722/722919/

## 5. Products / fixture selection — confirmed observations

A surviving screenshot shows a modal-style product selection window over the store view with a grid of product-category icons. One captured screen reads `商品を選択して下さい / 調味料類` and displays a daily figure of `¥9,600/日`.

This is important for UI reconstruction: the original presents many management actions as movable/modal windows over the live store view rather than separate full-screen smartphone-style pages.

Visual source:
- https://dengekionline.com/elem/000/000/722/722934/

Known product / merchandise families mentioned in first-title research include at least:
- bentos / prepared food
- bread
- books / magazines
- alcohol
- cigarettes
- medicine
- oden
- steamed buns
- warm drinks
- cold/frozen goods
- seasonings
- event products
- delivery-service application forms

Some categories require sales licenses, with regional restrictions noted by play records. Exact full product list and prices are NOT yet reconstructed.

Sources:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 6. Staff system — confirmed details

- Total staff candidates: 35.
- Hiring-screen stats and transfer/assignment-screen operational stats are distinct.
- Hiring-side parameters include salary, stamina, education/academic background, agility, sociability.
- Operational parameters include register, replenishment, security, cleaning, customer service.
- Education is related to register/security ceilings and store-manager education affects staff growth.
- Agility relates to replenishment ceiling and appears to affect stamina recovery probability.
- Sociability relates to customer service and cleaning ceilings.
- Staff improve over time.
- Low register skill can make checkout extremely slow and cause customer anger.
- The game includes intentionally odd staff candidates, including an alien-like character, reinforcing the slightly comedic tone.

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 7. Customer / demand system — confirmed details

The game visibly simulates individual customers rather than only converting demand into aggregate sales.

Observed / reported customer groups include office workers, students, housewives/mothers, elderly people, child-accompanied customers, etc. Groups of visually identical customers can arrive together.

The community research suggests destination-product demand plus incidental/add-on purchasing. Large wagons may have higher `attention` and possibly affect incidental purchase probability; this remains a hypothesis and must not yet be treated as an exact formula.

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

## 8. Customer monopoly / store attraction — confirmed factors

The first-title community refers to a key metric `顧客独占率` (customer monopoly/share).

Confirmed or strongly supported factors:
- service
- surrounding building population
- assortment breadth
- merchandise price
- business hours
- weather
- nearby rival stores

Service can be raised through staff service ability and fixtures such as plants, benches and fountains.

Important timing behavior:
- Customer monopoly is normally recalculated around the date change and affects that day's customer traffic.
- Weather changes can also trigger recalculation during a day.
- Setting temporary closure at the wrong time can make customer monopoly effectively calculate as 0 and kill traffic for the day.

Source:
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/FAQ

## 9. Time progression — confirmed unusual rule

- Real-time simulation runs only through the first four days of a month.
- From day 5 to month-end, time is skipped/aggregated rapidly.
- The original PS title does not offer speed control; contemporary retrospective coverage specifically notes that once the store is stable, the player often waits and watches.

Sources:
- https://wikiwiki.jp/theconveni1/FAQ
- https://dengekionline.com/elem/000/000/722/722919/

Implementation note:
- For the first faithful prototype, preserve the economic/simulation meaning of this rule.
- Android usability may later add speed controls, but do not change the underlying rules until baseline behavior has been validated.

## 10. Hours / costs — confirmed behavior

- Business hours are configurable, including 24-hour operation and shorter opening windows.
- When closed, many operating costs including labor are not charged according to community testing, while employees can still appear to clean/replenish.
- Therefore 24-hour operation is not always economically optimal.

Source:
- https://wikiwiki.jp/theconveni1/FAQ

## 11. Promotion — confirmed values

Community data currently records:

| Promotion | Cost | Popularity gain |
|---|---:|---:|
| Direct mail | 100,000 yen | +12 |
| Newspaper ad | 500,000 yen | +20 |
| Airship | 1,000,000 yen | +30 |
| Radio | 3,000,000 yen | +50 |
| TV | 5,000,000 yen | +100 |

Also reported: every additional cumulative 10,000 visitors can trigger an idol one-day-owner event, temporarily raising popularity to 100.

Source:
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D

## 12. Security / incidents — confirmed behavior

- Security below 100 can allow serious incidents such as fire.
- Even 99 is unsafe according to repeated community testing.
- Customer anger and store expansion can reduce security.
- Police box / fire-station attraction is a practical way to maintain security.
- Other reported incidents/events include shoplifting, robbery, complaints, magazine coverage, idol one-day-owner, weather events, and bankruptcy.

Sources:
- https://wikiwiki.jp/theconveni1/FAQ
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 13. Rival stores / chain expansion / town growth

- Rival convenience stores actively compete for customers.
- Rival stores can be acquired.
- New branches should often be prioritized because land values rise as the town develops.
- Community tests report that land worth roughly 20 million early can later exceed 100 million.
- The town can develop new infrastructure/facilities; one documented case reports a station appearing after town population exceeds 5,000 near an existing rail line.
- Facilities such as universities and police can be attracted intentionally, making city development part of the strategy.

Sources:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://dengekionline.com/elem/000/000/722/722919/

## 14. Scenario structure — provisional reconstruction

Current community sources indicate at least three standard difficulty/scenario goals:
- beginner: grow population / attract metropolitan government (reported target around 20,000 population)
- intermediate: reach 10 company stores
- advanced: reach 5-star owner evaluation

A hidden additional map/mode is also reported after clearing the standard modes.

This section is PROVISIONAL and must be verified against manual/gameplay before implementation.

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 15. Research-quality rules

Use evidence labels going forward:

- **CONFIRMED-OFFICIAL**: current official product page / publisher / manual.
- **CONFIRMED-VISUAL**: readable directly from original-game screenshot/video/manual page.
- **CONFIRMED-COMMUNITY**: multiple reproducible community observations or detailed data table.
- **PROVISIONAL**: plausible but not independently verified.
- **HYPOTHESIS**: inferred behavior/formula that must not be hard-coded yet.

Do not silently promote a community guess into a game rule.

## 16. Primary research sources collected so far

Official/current:
- https://store.playstation.com/ja-jp/concept/10017477

Manual archive (PS1 manual images; needs page-by-page extraction):
- https://psinstructionmanual.com/theconveni/

First-title community research:
- https://wikiwiki.jp/theconveni1/
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

Retrospective / visual evidence:
- https://dengekionline.com/elem/000/000/722/722919/
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

Secondary historical tips:
- https://wazap.com/game/12333/cheats/

## 17. Next research tasks — DO NOT START CODING BEFORE THESE ARE SUFFICIENTLY MAPPED

Priority A — original manual/UI reconstruction
- Extract manual page by page.
- Reconstruct controller mapping and every top-level command/menu.
- Reconstruct screen hierarchy and modal windows.
- Identify all status bars / date / weather / money / store information shown during live simulation.

Priority A — authoritative data inventory
- Complete product/category list.
- Complete fixture/equipment list with footprint, orientation, cost, maintenance, capacity and service/security effects.
- Store size types and exact tile dimensions.
- Complete staff roster and initial/ceiling stats.
- Customer archetypes and origin buildings.
- Full facility/building list and population/demand effects.
- Sales-license rules for alcohol / cigarettes / medicine.

Priority A — simulation behavior
- Customer spawn/destination selection.
- Customer pathfinding and congestion rules.
- Primary-purchase vs incidental-purchase behavior.
- Checkout queue behavior and abandonment/anger conditions.
- Staff task selection / priority / stamina / rest behavior.
- Shelf replenishment and inventory flow.

Priority B — economy/formulas
- Purchase cost / retail price / markup UI.
- Daily operating cost model.
- Monthly day-1-to-4 aggregation formula.
- Customer monopoly formula or practical approximation.
- Popularity decay and advertisement timing.
- Land-price evolution.
- Rival AI expansion and pricing.

Priority B — progression/events
- Exact scenario start conditions and victory/failure conditions.
- Town population growth rules.
- Facility attraction costs/probabilities/effect radius.
- Station/city-hall/metropolitan-government appearance conditions.
- Fire/robbery/shoplifting/complaint/media/idol events.

## 18. Architecture principle for later implementation

Before original features are added, build a testable "baseline compatibility layer":

- `sim/` — deterministic economic/customer/staff model
- `world/` — town map, buildings, population, rivals
- `store/` — tile grid, fixtures, pathing, inventory, queues
- `ui/` — PS/SS-inspired information architecture adapted to touch
- `data/` — research-derived tables, separated from code
- `docs/research/` — factual evidence and uncertainties
- `docs/decisions/` — deliberate deviations from the original

Any deliberate modernization (speed controls, touch controls, autosave, accessibility) should be recorded as a decision rather than silently changing baseline behavior.

## 19. Immediate next step

Continue research. Do not begin full production implementation yet. The first implementation milestone should only start after the original command hierarchy, fixture/product data model, store tile rules, customer loop, staff loop, and scenario objectives are sufficiently documented to avoid another architecture-first false start.
