# Convenience Store Remake — Project Memory

Last updated: 2026-09-24 (JST)

This file is the canonical memory checkpoint for the project. If chat context is lost, start by reading this file and the files under `docs/research/`.

## 1. Project goal

- Target: Android smartphone game.
- Development method: GitHub is the source of truth for code, research, decisions, handoff notes, and later generated assets.
- Baseline design target: reproduce the gameplay structure and feel of the first home-console version of **『ザ・コンビニ ～あの町を独占せよ～』**, released for PlayStation / Sega Saturn in 1997, as closely as practical.
- After the baseline is playable, add original systems and modernization step by step.
- Distribution scope (owner decision, 2026-09-21): this project is for the owner's personal use only and will not be publicly distributed or shared with unspecified third parties. Given that, original-title assets/data may be referenced directly (including via disc-image analysis) when preparing this project's own visual/audio assets, superseding this section's earlier blanket "do not reuse, always create new" instruction. A separate, later original convenience-store-management game the owner plans to build using know-how from this project will not reuse any assets or data derived from the original title.
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

Confirmed service fixtures (values below match `reference_sim/conveni_sim/baseline_data.py`'s
current CONFIRMED_OFFICIAL strategy-guide figures; a 2026-09-17 session resolved a wiki-vs-guide
conflict in favor of the guide for bench/fountain's service_bonus and bench's maintenance -- this
section previously still showed the superseded wiki-derived numbers, corrected here):
- Potted plant: service +2, size 1x1, maintenance 120 yen/day.
- Bench: service +4, size 1x1, maintenance 160 yen/day.
- Fountain: service +30, size 2x2, maintenance 2,400 yen/day.

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

The community research suggests destination-product demand plus incidental/add-on purchasing. Large wagons may have higher `attention` and possibly affect incidental purchase probability; the `attention`-weighting angle specifically remains a HYPOTHESIS and must not yet be treated as an exact formula.

**Incidental-purchase count upgraded to CONFIRMED-OFFICIAL (2026-09-19)**: directly re-read from
「クイックリファレンス」book p.9: "顧客は購入希望の品を求めて来店する。希望の品を購入した後、
時間が許せばそのほかの商品も購入する。それぞれの顧客に3品程度の「ついでに欲しい品」があるので、
それらを揃えておくことも大切だ。" Each customer wants roughly 3 additional in-stock products beyond
their primary destination purchase, bought afterward if time allows. This is now wired into `game/`
(task #55, decision 0124, lifting decision 0004's "incidental/add-on purchase probability" boundary
with the user's explicit go-ahead) as a uniform-random draw from currently-stocked products, not a
weighted-by-category or `attention`-weighted draw -- the guide's own per-category bar chart is
single-playthrough example data, not a confirmed general weighting table, so that part of the
HYPOTHESIS above remains open.

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

Values below match `reference_sim/conveni_sim/baseline_data.py`'s current `PROMOTIONS`
(CONFIRMED_OFFICIAL for airship/radio/tv's popularity_gain, directly re-verified 2026-09-19
against 「新人店長実習マニュアル」book page 120's own "広告データ" table; CONFIRMED_COMMUNITY
wiki source for the rest). This table previously still showed superseded wiki-derived
airship/radio/tv popularity figures (+30/+50/+100) after an earlier session had already
corrected the code; corrected here to match.

| Promotion | Cost | Popularity gain |
|---|---:|---:|
| Direct mail | 100,000 yen | +12 |
| Newspaper ad | 500,000 yen | +20 |
| Airship | 1,000,000 yen | +40 |
| Radio | 3,000,000 yen | +60 |
| TV | 5,000,000 yen | +90 |

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

**When implementing (not just researching) and no CONFIRMED value covers a needed number or mechanic**,
work down this priority order rather than jumping straight to invention:

1. Recovered evidence (the CONFIRMED-* levels above).
2. **Analogy-based inference from another already-CONFIRMED, related data point** on the same entity or
   source row -- e.g. deriving an unstated per-category order size from that same category's own
   CONFIRMED_OFFICIAL shelf `max_capacity`, rather than picking an unrelated round number. Prefer this
   over (3) whenever a real anchor point exists anywhere in the already-recovered data.
3. This project's own invented `REMAKE_BALANCED_DEFAULT` placeholder, only when neither (1) nor (2) is
   available (including when a qualitative research note explicitly says no formula should be invented
   from it).

A session was corrected on exactly this ordering in task #39: `product_catalog`'s `initial_stock_units`
was set to a flat `10` for every ported category, even though each category's own CONFIRMED_OFFICIAL
`max_capacity` was sitting in the same source row unused. Task #42 fixed it to derive the number from
`max_capacity` instead. See `CLAUDE.md` (project root) for the standing version of this rule and
`docs/decisions/0111-*.md` for the fix. Every bucket-3 invention still needs the full `REMAKE_BALANCED_
DEFAULT` tagging discipline from section 19's task #38 correction: code comment + JSON `evidence_note` +
test assertion, all three, not just a decision doc.

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

## 17. Research gaps to close alongside implementation

The executable reference core is already under active development. Continue filling the
following evidence gaps in parallel with deterministic, unknown-safe implementation. Do not
block reference-layer work merely because the complete original data tables or formulas are
still missing; keep unknown values explicit and do not invent coefficients. Full Android client
production remains later than the compatibility core.

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

## 19. Current implementation checkpoint and next milestone

The executable compatibility model under `reference_sim/conveni_sim/` is now established. It
contains evidence-aware baseline data, store grid/pathing and dynamic occupancy, explicit
customer/staff/checkout lifecycles, stamina/rest, inventory/replenishment, cleaning, purchases,
cash/day-end bookkeeping, representative-day and sub-day clocks, opening hours, observation
replay/statistics, customer-share recalculation gates, fixed-time promotion events, temporary
closure behavior, and an effective-opening-state customer admission gate.

The autonomous representative-day milestone has been reached. The Python implementation now acts
primarily as a compatibility oracle: unresolved original policies remain explicit and observation
replay can compare representative runs against recorded evidence.

The production client now exists under `game/` as a Godot 4 vertical slice. Its first executable
loop covers entry, pathfinding, product pickup, stock depletion, staffed checkout, cash settlement,
and exit, using newly drawn primitives and explicitly provisional JSON inputs. Completed visits can
be repeated explicitly while preserving stock and cash, including a no-sale sellout path. This is a
manual prototype admission boundary rather than an invented demand formula. Godot-native headless
validation protects the loop in CI.

The vertical-slice runtime now composes separate engine-native state objects for store layout,
inventory, economy, one customer, and one staff member. This is an architecture boundary only:
the orchestrator still runs the same explicitly provisional visit, and the split does not promote
prototype pathing, demand, purchase, staff, timing, or economy behavior into recovered first-title
rules.

Customer and staff state now live in explicit rosters. Every manual visit retains a distinct
terminal customer record, while the prototype still allows only one active customer and explicitly
selects its checkout staff. These limits avoid inventing original concurrent-arrival, collision,
queue, or staff-dispatch behavior while creating a stable boundary for later evidence replay.

The client also has a touch/mouse prototype for transactional fixture relocation between visits.
It preserves bounds, occupancy, staff cells, and the current required route, but its interaction
flow and validation policy are explicitly PROVISIONAL rather than a claim about the original
construction menu, closure requirements, costs, or time behavior.

Selected fixtures can also be rotated transactionally, and full Reset restores the immutable
configured layout along with actors, inventory, and cash. Rotation exists in original evidence,
but the prototype's clockwise control, pivot, interaction-cell transform, edit gate, and lack of
cost remain PROVISIONAL.

The client inventory is now a product-ID catalog with per-product fixture binding, stock, and price,
and customers retain basket lines across an explicit ordered multi-product visit plan. The included
two-product plan exercises shelf-to-shelf-to-checkout traversal and sellout reconciliation without
inventing original demand, product choice, incidental purchase, substitution, or quantity rules;
the plan and all values remain PROVISIONAL.

Successful prototype checkouts now retain immutable cause-neutral sale records linking customer,
prototype time, basket lines, and total, allowing cash/sellout reconciliation without reconstructing
mutable actor state. Record IDs, timestamp granularity, and storage shape are PROVISIONAL telemetry,
not a recovered original receipt or accounting format.

Godot CI invokes the smoke harness directly via `--script`. Its preload graph therefore avoids
cross-script custom `class_name` annotations that require an editor-generated global class cache;
the CI job also performs a clean headless editor import before the smoke command so project metadata
and resources are validated in the same way as a first project open. This is a CI/runtime loading
constraint, not a gameplay or compatibility rule.

The production slice now records a cause-neutral runtime event timeline and exports a versioned
provisional observation snapshot containing events, sales, and inventory. This creates a future
comparison seam for video/emulator observations without claiming the original used these event names,
sequence IDs, timestamps, storage format, or inferred causes.

An explicit customer-admission seam can now preserve a caller-provided unique ID and ordered known-
product plan for future observation replay. It validates only supplied facts and route feasibility;
it does not choose arrival time, demand, products, quantities, or concurrent behavior.

An explicit between-visit restock seam can add caller-supplied units for a known product/staff pair,
deduct a caller-supplied total procurement cost, and record matching expense/event facts. It does not
invent capacity, reorder timing, quantity, supplier pricing, delivery, or staff-task selection.

The vertical slice now gains customers on its own. `scripts/domain/demand_policy.gd` ports
`reference_sim/conveni_sim/remake_demand_policy.py`'s REMAKE_BALANCED_DEFAULT arrival-rate formula
(population x share% x a per-population daily visit rate, spread across opening minutes, reduced
under bad weather) so `VerticalSliceSimulation.tick_idle_for_demand()` can admit the next customer
via a per-minute probability roll once the store is empty, instead of requiring the manual
`start_next_customer()` boundary every time. The manual boundary still exists as an override. This
does not add concurrency: the existing single-active-customer constraint (original concurrent-
arrival and collision rules remain unrecovered) is unchanged, and `nearby_population`/
`customer_share_percent` are still supplied directly in `data/vertical_slice.json` because no town/
trade-area spatial simulation exists in this client yet (see decision 0088).

The second, non-checkout staff member is no longer permanent furniture. `staff_state.gd` gains a
`to_restock`/`restocking` task cycle, and `VerticalSliceSimulation._assign_idle_restock_tasks()`
dispatches the first idle non-checkout staff member to the first sold-out product each tick (a
simple greedy match, not a skill- or priority-based dispatcher), restocking it back to its own
configured `initial_stock_units` and deducting `quantity x restock_unit_cost_yen` from cash through
the existing expense/event-log plumbing. This PROVISIONAL prototype rule -- the guide only confirms
that register-assignment AI exists and is imperfect, never its dispatch logic -- is disabled by
default (`restock_task_enabled: false`) because this vertical slice's base scenario deliberately
demonstrates a shelf staying empty after sellout; enabling it there would silently invalidate that
existing, tested behavior. A dedicated headless-smoke configuration exercises it instead (see
decision 0089). Layout edits are now also blocked while any restock task is active.

`minute_of_day` no longer just wraps silently forever: `VerticalSliceSimulation` now counts each
midnight crossing as a day (`day_count`) and, every `REPRESENTATIVE_DAYS_PER_MONTH` (4) days,
settles a month by taking the net cash change across those 4 days and multiplying it by
`MONTH_MULTIPLIER` (8), applying the difference as a lump-sum `month_end_settlement` record. Unlike
the demand/restock features above, this multiplier is `CONFIRMED_OFFICIAL` -- the guide states
"1月=4日間×8" directly, matching `reference_sim/conveni_sim/month_aggregation.py`'s own citation --
this client only ports the already-confirmed formula, it does not invent how each representative
day's own result is computed (see decision 0090).

Every month-end settlement now also evaluates two CONFIRMED (not guessed) terminal rules:
bankruptcy when cash is negative at a day/month boundary
(`reference_sim/conveni_sim/month_boundary.py`'s `MonthBoundaryBankruptcyPolicy`; cash exactly at
zero stays explicitly unresolved, matching that policy's own unresolved `bankrupt_when_zero`), and
a 100-year time limit without meeting the scenario's clear condition
(`reference_sim/conveni_sim/store_events.scenario_time_limit_exceeded`). This client has no
scenario/clear-condition system yet, so `clear_condition_met` defaults to `false`. Once
`is_game_over` is set, every mutating method (`step`, `tick_idle_for_demand`,
`start_next_customer`, `apply_explicit_restock`, layout edits) becomes a no-op (see decision 0091).

Task #25 (什器購入・商品仕入れ・許可・広告) bundles four independent systems. The first,
fixture purchase, is implemented: `try_purchase_fixture()` adds a new fixture from a
`fixture_catalog` config section (potted plant/bench/fountain, prices ported from
`reference_sim/conveni_sim/baseline_data.py`'s `FIXTURES`, CONFIRMED_OFFICIAL) with the same
atomic route/walkability safety check as fixture relocation (decision 0092). The second, permits
and product procurement, is also implemented: `try_purchase_permit()`/`has_permit()` (tobacco
¥7,000,000 / alcohol ¥3,000,000 / medicine ¥10,000,000, CONFIRMED_OFFICIAL from `PERMITS`) and
`try_procure_product()` (adds a new product SKU from `product_catalog` to an unoccupied fixture;
currently just `tobacco`, CONFIRMED_OFFICIAL pricing from the guide's category table). Both
permit-gated fixtures and permit-gated products refuse purchase without the permit held first.
Each permit's confirmed exclusion-distance-from-other-stores rule is deliberately left
unenforced (would need an actual rival-store map, which task #26 deliberately did not build);
fixture-to-category compatibility is also not checked (decision 0093).

Task #25's fourth and final system, advertising, is also implemented, completing the task.
`reference_sim/conveni_sim/promotion.py` already had a complete evidence-safe design for this
(`PromotionScheduler`/`StorePopularityRuntime`/`apply_confirmed_triggered_promotion`), so Godot
ports it faithfully: `trigger_day`/`trigger_hour` are an absolute representative-day-of-month
(1-4)/hour (not "days after purchase"), cost is debited only when the event fires (not at
purchase), popularity is capped at 100, and each promotion method can only be used once per
month. `try_purchase_promotion()` schedules from a `promotions` catalog (direct mail/newspaper/
airship/radio/tv, CONFIRMED pricing/timing from `PROMOTIONS`); `_fire_due_promotions()` runs
every tick before day-boundary handling (so a trigger on a month's last tick still resolves
against the correct day) and applies cost/popularity once due. The guide-confirmed daily
popularity decay for low-rated stores is not modeled, since `reference_sim` itself leaves the
decay amount unresolved (decision 0094).

Task #26 (町・ライバル店・地価) deliberately scoped down from "spatial model" to three
non-spatial pieces, since neither `reference_sim` nor this project's research has an actual town
map, facility-placement, or population-growth simulation to port (section 13/17 gap). `TownState`
(`town_state.gd`) mirrors `reference_sim/conveni_sim/town.py` exactly: just tracked
`population`/`store_count_including_rivals`. The one piece with a real gameplay effect is rival
dilution: `demand.rival_store_count = max(0, town.store_count_including_rivals - 1)`, and
`DemandPolicy.expected_arrivals_per_minute()` scales down by
`min(MAX_RIVAL_DILUTION, RIVAL_DILUTION_PER_COMPETITOR * rival_store_count)` -- reusing
`remake_customer_share.py`'s confirmed constants (0.08/competitor, capped at 0.6) but applied to
the whole expected-visitor estimate rather than that module's 0-100 customer-share score, since
this client has no service/cleaning/security/assortment stats yet. Defaults to zero rivals (a
no-op). `land_value_policy.gd` ports `remake_land_value.py`'s land-price formula
(REMAKE_BALANCED_DEFAULT) verbatim as an informational `snapshot()` field only -- no
purchase/sale mechanic consumes it. Deliberately not implemented: the spatial map itself, rival
store placement/distance-based trade-area overlap, and the rival AI decision function
(`remake_rival_policy.py`), since no rival-store entity exists in Godot yet for it to act on
(decision 0095).

Task #27 (店舗評価をゲームループへ反映) ports `reference_sim/conveni_sim/store_rating.py`/
`store_value.py` -- direct CONFIRMED_OFFICIAL transcriptions of the guide's own ★-rank table and
service/security/cleaning value formulas (書籍頁74-75), not this project's guesses. `store_rating.gd`/
`store_value.gd` mirror them verbatim: a 0-100 internal value maps to 0-5 stars at fixed
breakpoints, and each representative month, >=3 of (price change/service/security/cleaning/sales)
meeting the current rank's upgrade thresholds grants +5 while each of the 5 falling below the
downgrade thresholds costs -1. `VerticalSliceSimulation._evaluate_store_rating()` runs from
`_settle_month_end()`, feeding it staff `service_skill` average plus purchased amenity fixtures'
`service_bonus` (service value), staff `security_skill`/`cleaning_skill` totals times the store's
`size_tier` multiplier (security/cleaning value), the representative month's sales revenue x8
(section 9's 4x8 rule), and `price_change_pct=0` (no price-setting mechanic exists yet). Staff
`service_skill`/`security_skill`/`cleaning_skill` are new static REMAKE_BALANCED_DEFAULT config
fields on `StaffState` -- the guide's skill-growth model (work-event counting, manager-education
bonus) has not been ported to Godot at all yet, so these never change on their own; `size_tier`
("small") is likewise a REMAKE_BALANCED_DEFAULT house-rule mapping, since `STORE_SIZE_VALUE_MULTIPLIER`'s
three tiers are keyed by a *different*, already-flagged-as-conflicting guide dimension notation
(10x10/12x12/14x14) than the store's actual `editable_floor` grid dimensions (see task #31 below).
Deliberately not implemented: the police-box/fire-station security-facility bonus (no such
fixtures or spatial search exist) and the guide's per-event rating deltas (angry customer/
shoplifting/donation), since their trigger events aren't wired into this client either
(decision 0096).

Task #28 (セーブ/ロードをGodotに実装) is a pure engine feature -- no `reference_sim` counterpart,
so decision 0097 records design choices rather than evidence tags. `VerticalSliceSimulation.
save_state()`/`load_state()` round-trip time/day/month, game-over/clear state, popularity/rating,
permits, promotions, the full store layout, inventory, economy, and event log. Deliberately not
saved/restored: the active customer's/staff's mid-visit/mid-task walk state, since both are
transient and a fresh `reset()` already produces a sensible state on load -- `load_state()` in fact
resets every subsystem to its config-derived starting point first, applies the saved fields,
restores the layout, and only then admits a fresh default customer (admitting one before the layout
is restored would leave its cached route stale). `load_state()` rejects an incompatible save
(different scenario_id/config_schema_version/save_schema_version) by returning `false` without
mutating anything, the same convention as this client's `try_*` methods; a structurally corrupted
save instead asserts, matching `_require_config()`. `save_game_service.gd`'s `SaveGameService` is
the only I/O-touching piece (JSON under `user://saves/`), kept separate from the I/O-free
`scripts/domain/` classes. Implementing this surfaced and fixed two existing latent bugs:
`StoreLayout.restore_fixture_snapshot()` wasn't normalizing float-typed coordinates from a JSON
round-trip, and naively rebuilding `EconomyState`'s settled-customer guard from saved sale records
would have permanently blocked a freshly re-admitted customer of the same recycled id from ever
completing a sale.

Task #29 (基本メニューUIをGodotに実装) adds a title screen: `scenes/main_menu.tscn`/
`scripts/main_menu.gd` is now `project.godot`'s `run/main_scene`, with New Game / Continue / Quit.
`Continue` is disabled until `SaveGameService.save_exists()` is true. Since Godot cannot pass
parameters across `change_scene_to_file()`, a minimal autoload (`game_launch_state.gd`, registered
as `GameLaunchState`) carries a single `continue_from_save` flag from the menu to the gameplay
scene; `main.gd._ready()` reads and immediately clears it, loading the save only when it was set
(never on a direct launch of `main.tscn`). New Game deliberately does not delete an existing save.
The gameplay screen also gained Save/Load/Quit-to-Menu buttons calling the same `SaveGameService`
task #28 built. Since `godot --script`'s `instantiate()` never enters the tree on its own,
`@onready var`/`_ready()` never actually run during the existing CI "instantiate-then-free" scene
check, so this task's new NodePaths are checked explicitly via `get_node_or_null()` in
`headless_smoke.gd` instead (decision 0098).

Task #30 (複数店舗(チェーン展開)管理), the last task on this session's self-generated Godot-porting
roadmap (#21-#30), ports `reference_sim/conveni_sim/visitor_milestone.py`'s
`ChainVisitorMilestoneRuntime` verbatim -- CONFIRMED first-title evidence for a free +100 popularity
event every 10,000 cumulative visitors across the player's store chain. `chain_visitor_milestone.gd`
is fed this single store's completed-visit count today (the whole "chain" for now), so it already
generalizes correctly once a second playable store exists. `try_expand_chain()` models opening a new
branch as an abstract economic action (no second store is actually simulated), reusing task #26's
land-value infrastructure for its cost; success increments a new `player_store_count`, which
`PLAYER_STORE_COUNT_SCENARIO_TARGET = 10` wires into `clear_condition_met` for the first time
(previously always false, decision 0091) -- tagged PROVISIONAL, one rung weaker than
REMAKE_BALANCED_DEFAULT, since its own community source (section 14 above) is itself flagged
unverified. `store_events.gd` ports the guide's CONFIRMED_OFFICIAL magazine/contest eligibility gate
and prize formula as informational `snapshot()` fields only, never rolling the event's own
unconfirmed "may or may not be picked" draw. Deliberately not implemented: actually playing a second
store simultaneously (a much larger architecture redesign, out of scope exactly as the town/rival
spatial model was in task #26), a dedicated victory screen, the contest's actual draw/payout, and
rival chain open/acquire/close transitions (no rival-store entity exists in Godot yet). Chain state
now round-trips through save/load (`SAVE_SCHEMA_VERSION` bumped 1 -> 2) (decision 0099).

Task #31 (店舗グリッド寸法・動線を既存研究(攻略本準拠)に合わせる) fixes a fidelity gap the user
directly flagged: the vertical slice's `7x6`-tile store grid and diagonal-corner entry/exit were
never cross-checked against any research and are not plausible for the first title. `store.
width_tiles`/`height_tiles` now port `STORE_VARIANTS['small_top'].editable_floor = (5, 8)` tiles from
`reference_sim/conveni_sim/baseline_data.py`, a CONFIRMED_OFFICIAL strategy-guide transcription a
prior session had already resolved into `reference_sim` but never carried into this file (see
`docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md` sections 3 and 9). Entry and exit now
sit on the same wall instead of opposite corners, per the passage-width/circular-flow guidance in
`docs/research/store-dimensions-and-fixture-costs-2026-09-05.md` section 5 and
`docs/research/strategy-guide-full-decode-2026-09-16.md` section 20.3; the new fixture/staff layout
was verified reachable with a BFS mirroring `store_layout.gd`'s own check before being written, and
every hardcoded coordinate in `headless_smoke.gd` that assumed the old grid was updated to match.
`store_view.gd`'s `SUBCELL_PIXELS` dropped 42.0 -> 36.0 so the taller new grid still fits the window
(decision 0100).

Task #32 (スタッフ実名候補データ(35名)をGodotへ移植) replaces another identical-placeholder gap:
`staff.members`' staff-1/staff-2 both carried the exact same flat `service_skill=20/security_skill=
15/cleaning_skill=15`, tied to no real candidate. `reference_sim/conveni_sim/baseline_data.py`'s
`STAFF_CANDIDATES` already held a CONFIRMED_OFFICIAL 35-person roster from the strategy guide's
individual candidate cards (book pages 127-133,
`docs/research/strategy-guide-full-decode-2026-09-16.md` section "店員データ"). A new
`staff_candidates` array in `vertical_slice.json` ports all 35 verbatim (generated directly from
`reference_sim` via script to avoid transcription drift) as a reference-only hiring-pool catalog --
no hiring UI exists yet to actually pick from it. `staff-1`/`staff-2` are now bound to two specific
real candidates (`manda_machiko`, highest `register_skill`; `sugawara_fumio`, highest
`replenishment_skill`) instead of the shared placeholder; `register_skill`/`replenishment_skill` ride
along as unconsumed data (task #33 wires `register_skill` into checkout timing). This changed the
store-rating headless-smoke test's expected service/security/cleaning values (20.0/45.0/45.0 ->
17.0/57.0/51.0), updated accordingly (decision 0101).

Task #33 (レジ能力(register_skill)をチェック時間に反映) makes that ported register_skill data
actually do something: `checkout_ticks` used to apply as one flat duration no matter which staff
member ran the register. The research note confirms only a qualitative effect and explicitly warns
against inventing a numeric formula, and reference_sim's own `checkout_service_timing.py` likewise
only defines an abstract duration-policy Protocol with no concrete formula. A new
`scripts/domain/checkout_timing.gd` (`CheckoutTiming`) implements this client's own tagged
REMAKE_BALANCED_DEFAULT inverse-proportion scaling: `checkout_ticks` is reinterpreted as the
duration at `REFERENCE_REGISTER_SKILL` (13 -- the median register_skill across the 35 ported
candidates, not arbitrary) and scales inversely with the actual serving staff member's
register_skill, floored at 1 tick. `StaffState` gained a `register_skill` field; the checkout-start
transition now calls `_checkout_timing.required_ticks(checkout_staff.register_skill,
_checkout_ticks)`. This changed the headless smoke test's step count (515 -> 500), since staff-1
(manda_machiko, register_skill=20) now checks out faster than the old flat 3-tick constant
(decision 0102).

Task #34 (駐車場什器の追加), the last item on the user-approved priority list, adds
`parking_ground`/`parking_two_story`/`parking_tower` to `fixture_catalog`, ported verbatim from
reference_sim's `FIXTURES` (footprint/capacity/`blocks_pedestrian` CONFIRMED_COMMUNITY from the
first-title wiki, purchase price CONFIRMED_OFFICIAL). `store_layout.gd` needed no new mechanic:
every fixture already blocks its full footprint regardless of `kind`, so the confirmed
"parking blocks pedestrians" fact already held; `blocks_pedestrian`/`parking_capacity` are carried
as informational catalog fields only. `store_view.gd` gained a render branch so parking fixtures
don't render mislabeled as a shelf. The guide's `outdoor` placement fact is not enforced -- this
client has no outdoor/exterior space model yet (same boundary as task #26's deferred town/rival
spatial model) -- so purchasing one places it on the interior grid like any other fixture; this gap
is documented rather than worked around (decision 0103). This closes the priority list the user
approved after the store-grid audit: store grid -> named staff roster -> register-skill checkout
timing -> parking fixtures.

Task #35 (STORE STATUSパネルのUI表示ギャップ解消) closes a gap flagged before the priority-list audit
even started: `vertical_slice_simulation.gd`'s `snapshot()` already computed `star_rating`/
`popularity`/`town_population`/`land_value_yen` (tasks #26/#27), but `main.tscn`'s STORE STATUS panel
had no labels for any of them -- backend-only data invisible on screen, the concrete case behind the
original "is this playable at all?" question. `main.gd`/`main.tscn` gained two label pairs (star
rating + popularity, town population/rival count/land value) that only read existing `snapshot()`
fields; no simulation logic changed. `town_store_count_including_rivals` is the *total* store count
including the player's own, not a rival-only count (confirmed by `headless_smoke.gd`'s own
assertion), so the displayed rival count subtracts `player_store_count` rather than showing the raw
field under a misleading label (decision 0104). Of the other three items surfaced alongside this one
in the prior handoff, the user approved proceeding and the first (simultaneous customers/queue
ordering) became task #36 below; sample-layout loading and fixture-attention differentiation remain
out of scope -- no task number assigned.

Task #36 (同時複数顧客・チェックアウト待ち行列) ports a capability `reference_sim`'s
`CheckoutStationRuntime` already had (multiple waiting customers, explicit non-forced-FIFO service
selection) into `game/`, which previously hard-capped the store at exactly one active customer via
`CustomerRoster.can_admit()`. Rather than loosening that existing single-customer gate in place (an
existing `headless_smoke.gd`/reference_sim-contract test locks in that the fully-automatic passive
demand flow, `demand_admit_if_due()`, stays single-customer -- there is no guide/wiki evidence for
how many shoppers the original title allows in a store at once, so this project is not inventing an
answer there), a second, additive gate `can_admit_concurrent()` was introduced
(`_active_non_done_count() < max_concurrent_customers`, a REMAKE_BALANCED_DEFAULT cap of 3 read from
`vertical_slice.json`). Both the observed/explicit admission path (`start_explicit_customer`) and the
manual "Admit next customer" button (`start_next_customer`) now use it, so a player can actually reach
concurrent customers through ordinary play, not only through a scripted/observation path. The single
checkout fixture/staff still serializes service through a new `_checkout_queue` FIFO and
`_dispatch_checkout_queue()`, dispatched once per tick after every customer's own phase transition
runs; the customer-facing phase gained a `waiting_checkout` step between `to_checkout` and `checkout`.
Because more than one customer can now be active, the eight layout-edit-safety checks
(`try_purchase_fixture` and its seven siblings) that used to reuse `can_admit()` as a "no visit in
progress" proxy needed their own predicate, `all_settled()`: with concurrency, `can_admit()` alone
only reflects the single most-recently-admitted customer and could wrongly read as safe to edit while
an earlier-admitted customer is still mid-visit. `store_view.gd` and the HUD's Customer line were
updated to draw/list every active customer instead of only one; `snapshot()` kept its existing
singular `customer_id`/`customer_phase`/`customer_basket_*` fields untouched for backward
compatibility and added a new `active_customers` array alongside them. `vertical_slice.json`'s
`schema_version` moved 12 -> 13 for the new required `customer.max_concurrent_customers` field
(decision 0105). Not attempted: queue-cell geometry (the research note this task cites explicitly
says exact queue coordinates are unconfirmed) and register-orientation-dependent queue direction --
waiting customers stay logically queued at the checkout interaction cell, offset only cosmetically in
the renderer.

Task #37 (サンプルレイアウト読み込み機能) closes the second item of that same backlog. First-title
evidence confirms a built-in sample-layout loading path exists and that loading one is not trivially
reversible, but not what any sample actually contains -- an asymmetry this task's implementation keeps
explicit: the *mechanism* (`try_load_sample_layout`) is a CONFIRMED requirement, while the two sample
layouts themselves (`default_layout`, `with_bench`, in `vertical_slice.json`'s new `sample_layouts`
section) are this project's own REMAKE_BALANCED_DEFAULT placeholders, tagged as such in their own
`evidence_note` rather than presented as recovered data. Loading a sample reuses any fixture id already
in the current layout for free (a rearrangement, not a resale) and only charges catalog price for ids
the sample introduces that the layout doesn't already have -- sidestepping the research note's other
unresolved question (exact resale ratio) entirely rather than inventing an answer to it. No undo/sell
mechanic exists, matching the note's own instruction to treat `load sample`, `sell/remove fixture`, and
`restore previous layout` as separate, still-open questions; internally, `restore_fixture_snapshot` is
used only for atomic rollback of a *rejected* load, never as a player-facing "undo". Loading a sample
that would strand currently-procured inventory on a fixture the sample omits is rejected rather than
this client inventing an auto-clear-inventory rule, and a sample missing the fixed `checkout_fixture_id`
is rejected before `_refresh_interactions()` would otherwise assert on a missing fixture. `vertical_
slice.json`'s `schema_version` moved 13 -> 14 for the new required `sample_layouts` section. A dedicated
`SampleLayoutOption`/`LoadSampleLayoutButton` pair in `main.tscn` makes this reachable through ordinary
play, same as task #36's concurrency work (decision 0106).

Of the three items in the "3.2節" backlog the 2026-09-18 handoff first deferred, two are now done
(tasks #36 and #37); the third, fixture-attention differentiation, conflicts with decision 0004's
explicit "deliberately absent: incidental/add-on purchase probability" boundary (attention could only
plausibly affect an add-on-purchase probability that doesn't exist in this client at all yet) and
remains unstarted pending an explicit user decision to lift that boundary, the same way task #33 got
one for register-skill checkout timing.

Task #38 (経済アクションをUIに接続) responded to the user directly asking, after tasks #35-37 had
already landed, how far this client actually is from "playable as a game." Investigating turned up
that `vertical_slice_simulation.gd` already implemented six substantial player-facing economy actions
(`try_purchase_fixture`, `try_purchase_permit`, `try_procure_product`, `try_purchase_promotion`,
`try_expand_chain`, `apply_explicit_restock`) that `main.gd` never called at all -- only
`headless_smoke.gd` ever reached them. A player could not buy a fixture, get a permit, stock a
product, run a promotion, restock a shelf, or expand the chain through any UI control, which is most
of what "running a convenience store" actually consists of. This task wires all six into the HUD:
one OptionButton+Button pair per catalog-driven action (fixture/permit/product/promotion), plus a
restock button and a chain-expansion button. Buying a new fixture reuses store_view's existing
tap-to-target flow (the same `fixture_relocation_requested` signal relocate already uses) via a
`"__new:" + catalog_id` sentinel on the pending selection, rather than a second input mode; since the
catalog has no interaction-point data for a newly bought fixture, `_find_open_interaction_cell()`
derives one from the existing convention (every current fixture's interaction cell sits exactly one
subcell outside its own footprint) rather than requiring a second tap, giving up rather than guessing
if none of the four cardinal candidates are open. The STORE STATUS panel outgrew its fixed-height
`Panel` once this task's controls joined tasks #35-37's, so `UI/Panel/Margin/VBox` moved under a new
`UI/Panel/Margin/Scroll` (`ScrollContainer`), with `main.gd`'s `@onready` paths and
`headless_smoke.gd`'s structural node-path check updated to match. This task also added
`headless_smoke.gd`'s first scenario that actually enters the scene tree (`add_child`) to exercise
`main.gd` itself, since every earlier scenario in that file drove `vertical_slice_simulation.gd`
directly and this is the first time UI-layer logic (option-list population, the sentinel-based
placement flow, the interaction-cell heuristic) needed its own coverage beyond a manual Xvfb screenshot
(decision 0107).

**Correction (2026-09-19)**: the user pushed back hard after task #38 -- "don't forget this is a
recreation of the original The Conveni; don't drift toward some incomprehensible original game." An
audit turned up that task #38's two own inventions in `main.gd` (the interaction-cell placement
heuristic and the restock button's batch-size/cost default) were documented as non-original in decision
0107 and the PR description, but were missing the in-code `REMAKE_BALANCED_DEFAULT` tag that
`vertical_slice_simulation.gd` and every `domain/` file have followed since task #33 -- a real gap in
that discipline, not a false alarm. Both call sites now carry that tag in a code comment, and
`test_economy_actions_are_reachable_from_the_ui_not_only_headless_smoke` asserts the tag text is
present, so this class of gap is now caught mechanically rather than relying on remembering to add it.
No behavior changed.

**Task #39 (2026-09-19)**: after the correction above merged (PR #209), the user asked to prioritize
wiring/porting already-confirmed logic over inventing new content. An audit of `vertical_slice_simulation.gd`/
`domain/*.gd` for confirmed-but-unwired logic (mirroring how task #38 found six unwired economy actions)
turned up that `game/data/vertical_slice.json`'s `product_catalog` still held only the one "tobacco" entry
from task #32, while `reference_sim/conveni_sim/baseline_data.py`'s `PRODUCT_CATEGORY_PRICING` has 27
CONFIRMED_OFFICIAL product categories transcribed from the strategy guide's DATA LIST table (book page 85).
Since `try_procure_product`/`apply_explicit_restock` and `main.gd`'s `product_catalog_option` are already
fully generic over `catalog_id`, this required no new mechanic: 25 of the 27 categories were ported as
data (`sale_price_yen`/`restock_unit_cost_yen` computed the same way as the existing tobacco entry;
`alcohol`/`medicine` carry `required_permit_id` matching this file's existing permits). `cash` (現金) was
excluded -- it is the guide's zero-margin instrument row tied to a cash-dispenser fixture (an ATM-like
mechanic), not an ordinary restockable product, and no such fixture exists in this client. `initial_stock_units`
stays a REMAKE_BALANCED_DEFAULT of 10 per entry, matching tobacco's precedent, and is now tagged as such
directly in each entry's `evidence_note` (not just in the decision doc), per the tagging discipline the
correction above established. See decision 0108. `reference_sim` full suite 655 passed/1 xfailed (one
unrelated unseeded-RNG flake in `test_remake_purchase_policy.py` confirmed to pass on rerun/isolation);
`headless_smoke.gd` unchanged at 734 steps (its tobacco-selection test already looked the catalog id up
dynamically rather than assuming index 0).

**Task #40 (2026-09-19)**: continuing the same "wire confirmed logic before inventing" priority after
task #39 merged (PR #210), `vertical_slice.json`'s own `staff.skill_evidence_note` still said
`replenishment_skill` was ported data but consumed by no GDScript logic (task #33 had only wired its
sibling `register_skill` into checkout timing). Two qualitative research notes support a real effect --
"early low-skill staff clean slowly because they are also occupied with replenishment"
(`ss-early-store-operations-and-acquisition-2026-09-06.md` section 4, DIRECT-PLAY-SS) and "agility bounds
replenishment" (`checkout-staff-dispatch-evidence-2026-09-05.md` section 6) -- with no numeric formula in
either, the same evidence shape task #33 used for register_skill. New `game/scripts/domain/restock_timing.gd`
(`RestockTiming`) reuses `CheckoutTiming`'s exact inverse-proportion shape, wired into
`_step_restock_tasks()`'s `"to_restock"` transition in place of the flat `_restock_ticks` constant.
`REFERENCE_REPLENISHMENT_SKILL := 13` is the median `replenishment_skill` across the same 35
CONFIRMED_OFFICIAL candidates task #32 ported (coincidentally equal to register_skill's median). Tagged
REMAKE_BALANCED_DEFAULT in the code comment, the new `simulation.restock_ticks_evidence_note`, and a new
contract test mirroring task #33's, per the tagging discipline the task #38 correction established. See
decision 0109. Automatic restock dispatch stays disabled by default (task #36's existing carve-out), so
`headless_smoke.gd`'s main scenario is unaffected (734 steps, unchanged); only the dedicated
`restock_task_enabled=true` test block exercises this wiring, and it already waited on staff state rather
than an exact tick count, so it needed no change. `reference_sim` full suite 656 passed/1 xfailed, no
flake this run.

**Task #41 (2026-09-19)**: continuing the same priority after task #40 merged (PR #211), `game/data/
vertical_slice.json`'s `fixture_catalog` still held only the 8 fixtures ported in tasks #32/#34, while
`reference_sim/conveni_sim/baseline_data.py`'s `FIXTURES` has 45 CONFIRMED_OFFICIAL entries from the
strategy guide's DATA LIST fixture table. `try_purchase_fixture`/`main.gd`'s `fixture_catalog_option` are
already fully generic over `catalog_id`, and `store_view.gd` already falls back to a default blue "SHELF"
render for any `kind` other than `"checkout"`/`"amenity"`/`"parking"` (confirmed correct behavior since
task #34's parking fixtures), so 27 more fixtures were ported as `kind: "shelf"` data with zero code
changes -- ambient/refrigerated/frozen shelves and wagons at every size, the hot-drink/oden/steamed-bun
cases, event fixtures, and the large tobacco/cold-drink/hot-cold-drink vending machines.
`capacity`/`compatible_product_categories` stay unconsumed, matching task #39's identical choice to leave
the product side's `compatible_fixtures_text` unconsumed. 10 fixtures were deliberately excluded as
mechanics this client doesn't implement: `register_1`-`register_4` (multi-checkout routing isn't
simulated -- a single fixed `checkout_fixture_id`/`_checkout_queue` exists), `copier_a`/`copier_b`
(no copier service), `indoor_dispenser` (an ATM-like cash mechanic, same reasoning as excluding the
`cash` product category in task #39), `break_room_1`/`break_room_2` (no staff rest mechanic), and
`vending_machine` (its reference_sim entry itself has no confirmed footprint/price/maintenance data at
all -- an incomplete placeholder, nothing to port). See decision 0110. `headless_smoke.gd` unchanged at
734 steps (no code touched); `reference_sim` full suite 657 passed/1 xfailed.

**Task #42 (2026-09-19, correction)**: after task #41 merged (PR #212), the user pushed back again --
paraphrased, "this project reconstructs the original even where the guide doesn't fully resolve
something, by analogy from other data; it must not add arbitrary original elements, and recent work felt
like it was doing that." No `CLAUDE.md` existed in this repo at all (confirmed by search), so this
principle had never been written down anywhere a session would see it automatically. A self-audit of
tasks #39-#41 found one real instance: task #39 set every one of the 26 `product_catalog` entries'
`initial_stock_units` to a flat `10`, even though each category's own CONFIRMED_OFFICIAL `max_capacity`
(from the same `PRODUCT_CATEGORY_PRICING` source row) was sitting right there unused -- a real anchor
point ignored in favor of an untethered guess. Tasks #40/#41 were re-checked and found clean on this
same standard (task #40 reused an already-accepted formula *shape*, not a fresh flat guess; task #41 was
a pure CONFIRMED_OFFICIAL data port with no invented numbers). Fixed by re-deriving all 26
`initial_stock_units` values from each category's own `max_capacity` instead (tobacco included, for
internal consistency: 10 -> 40). This surfaced a second, unrelated latent problem while testing: two
`headless_smoke.gd` assertions had hard-coded tobacco's old `10 * 175` procurement cost and `10` stock
count as literal numbers instead of reading them from `config["product_catalog"]`, so they broke the
instant the underlying data changed -- fixed to look the values up dynamically instead of repeating them.
Wrote `CLAUDE.md` (project root, previously absent) to make this priority order (confirmed evidence >
analogy from other confirmed data > this project's own tagged invention, in that order) a standing,
automatically-loaded rule rather than something that only lived in one session's memory; also formalized
it in this file's section 15. See decision 0111. `reference_sim` full suite 657 passed/1 xfailed (no
data-count change, only field-level correction); `headless_smoke.gd` unchanged at 734 steps once both
hard-coded assertions were fixed.

**Task #43 (2026-09-19)**: after task #42 merged (PR #213), the user said "続けて" and a fresh audit ran
for remaining confirmed-but-unwired logic under CLAUDE.md's new priority order. The audit found `vertical_
slice.json`'s own `staff.skill_evidence_note` still claiming `service_skill`/`security_skill`/`cleaning_
skill` were "present as data but unconsumed by any GDScript logic" -- false since task #27, which already
wired all three into `VerticalSliceSimulation._evaluate_store_rating()` -> `store_value.gd`'s `compute_
service_value`/`compute_security_value`/`compute_cleaning_value` -> the monthly star rating, with existing
`headless_smoke.gd` coverage. `demand_policy.gd`'s header comment carried the same stale premise ("this
Godot port has no service/cleaning/security/assortment gameplay stats yet"). Fixed both (and a matching
test-file comment) to state what's actually true: the three stats exist and feed the monthly rating, but
nothing threads them into `demand_policy.gd`'s customer-arrival formula, and assortment breadth still has
no stat at all -- so the comment's actual point (no 0-100 share score exists here for `rival_store_count`
to dilute) stays correct. Pure evidence-accuracy fix, no logic or test-assertion change. See decision 0112.
`reference_sim` full suite 657 passed/1 xfailed, `headless_smoke.gd` unchanged at 734 steps.

The same audit also surfaced two candidates left for the user to prioritize rather than assumed as
"next": (a) porting `FIXTURES`' CONFIRMED_OFFICIAL `capacity`/`compatible_product_categories` into
`fixture_catalog` and enforcing them in `try_procure_product` -- deliberately left unconsumed three times
already (decision 0093, and again in tasks #39/#41's own evidence_notes), so possibly an intentional
low-priority choice rather than an oversight; and (b) wiring `remake_customer_share.py`'s already-tagged
weighted 0-100 share formula into `demand_policy.gd` now that task #27's service/security/cleaning stats
exist to feed it -- a real integration (medium scope), not a one-line hookup.

**Task #44 (2026-09-19)**: the user chose to proceed with the customer-share integration. New
`game/scripts/domain/customer_share.gd` (`CustomerShare`) ports `remake_customer_share.py`'s
`compute_customer_share_percent()` field-for-field (all six weights, `ASSORTMENT_SATURATION_PRODUCT_
COUNT=20`), wired into `VerticalSliceSimulation._evaluate_store_rating()` right after `service_value`/
`security_value`/`cleaning_value` are computed each month: it now also feeds them, plus `popularity`
(previously completely unused outside `snapshot()`/save-load -- itself a confirmed-but-unwired stat this
audit turned up) `inventory.products.size()` (assortment proxy), and `demand.opening_minutes_per_day`,
into the ported formula, and overwrites `demand.customer_share_percent` with the result -- which was
previously a static config placeholder that never changed. Deliberately not ported: the Python source's
`weather`/`competing_store_ids` dilution and its "unknown factor" renormalization branch, since
`demand_policy.gd` already applies weather/rival dilution downstream to the whole visitor estimate (double-
applying it in the share score too would double-count, not add fidelity) and every one of the six factors
is always known by the time this client calls it (no reachable "unknown" case to renormalize around).
`service_value`/`cleaning_value`/`security_value` are clamped to [0, 100] before feeding in -- reusing the
same ceiling `store_rating.gd`'s own CONFIRMED_OFFICIAL upgrade/downgrade thresholds already treat those
three values as (e.g. `min_service: 100` for 5-star), not inventing a new one. See decision 0113.
`headless_smoke.gd` gained 3 direct unit tests for the ported function plus an assertion on the existing
monthly-rating scenario (hand-computed expected share of 25 from that scenario's known service=17.0/
cleaning=51.0/security=57.0/2 products/960 minutes); unchanged at 734 steps otherwise (the main long
scenario never reaches month-end). `reference_sim` full suite 658 passed/1 xfailed.

**Task #45 (2026-09-19)**: the user chose the other task #43 candidate -- wiring fixture `capacity`/
`compatible_product_categories`. All 29 shelf-kind `fixture_catalog` entries gained both CONFIRMED_
OFFICIAL fields (ported from `FIXTURES`, matching `product_catalog`'s catalog_id vocabulary exactly since
task #39 already ported product categories as catalog entries). `try_procure_product()` now rejects a
procurement whose `catalog_id` isn't in the target fixture's `compatible_product_categories` (skipped
entirely for a fixture with no `fixture_catalog` origin at all, e.g. the prototype scenario's shelf-1/
shelf-2 from before the catalog system existed -- no confirmed data to check, so no invented rule for
them either), and clamps the procured quantity to `min(product_catalog's own initial_stock_units,
the fixture's own capacity)`. That clamp matters because task #42 set `initial_stock_units` from each
category's *general* `max_capacity` (e.g. bread=120), which can exceed the *specific* fixture actually
purchased (e.g. `small_ambient_shelf`'s capacity=40) -- resolved by taking the smaller of two already-
confirmed numbers, not inventing a third. Since the clamped quantity is stored as the product's own
`initial_stock_units`, every later restock path (`apply_explicit_restock`, automatic `_complete_restock`)
respects the cap with no further changes, since both already restock toward that same field. See decision
0114. Fixed two headless_smoke.gd tests that broke under the new rules: the tobacco-procurement cost/
stock assertions now read the fixture's own capacity dynamically too (40 -> 20, since `small_tobacco_
vending`'s capacity is 20), and the economy-UI end-to-end scenario swapped its second fixture purchase
from `small_ambient_shelf` to `small_tobacco_vending` so procuring tobacco onto it stays compatible.
Added a new scenario exercising both the rejection (tobacco onto small_ambient_shelf) and acceptance
(bread onto the same fixture) paths. `headless_smoke.gd` unchanged at 734 steps; `reference_sim` full
suite 659 passed/1 xfailed.

**Task #46 (2026-09-19)**: the user stated a standing development-order directive -- build out the system
side completely first, and only at the end generate images/audio and wire them to the system -- and, in
that spirit, chose to wire fixture `maintenance_yen_per_day` into daily cashflow next. Every one of the 35
`fixture_catalog` entries carries a CONFIRMED_OFFICIAL `maintenance_yen_per_day`, but nothing ever
deducted it. New `VerticalSliceSimulation._apply_daily_fixture_maintenance()`, called from `_handle_day_
boundary()`, sums it across every currently-owned fixture that actually has a `fixture_catalog` origin
(skipping `shelf-1`/`shelf-2`/`checkout-1`, which predate the catalog system and have no confirmed figure
to charge -- same precedent task #45 set for the compatibility check) and deducts the total once per
simulated day via `economy.record_explicit_expense("fixture_maintenance", ...)`, recording no event at
all on a zero-maintenance day rather than a redundant zero-yen entry. Because this happens inside the
4-simulated-day window `_settle_month_end()` already reads via `economy.cash_yen`'s own delta, it needed
no separate x8 scaling logic of its own. Removed the now-false "not consumed" claim from all 35
`fixture_catalog` `evidence_note`s (the same kind of staleness task #43 corrected for service/security/
cleaning_skill). Investigating this also turned up that `salary_yen_per_day_24h` (on the 35-candidate
hiring pool, not on the active `staff.members` entries themselves) is similarly unconsumed -- deliberately
left out of this task's scope (the user asked specifically about fixture maintenance) and noted as a
separate future candidate. See decision 0115. `headless_smoke.gd` gained a dedicated scenario (buy a
bench, cross one day boundary, confirm the exact deduction and event) plus a no-op-day check; 764 steps
(up from 734, the new scenario's own ticks). `reference_sim` full suite 660 passed/1 xfailed.

**Task #47 (2026-09-19)**: continuing directly from task #46's own leftover candidate, `salary_yen_per_day_
24h` (CONFIRMED_OFFICIAL on the 35-candidate hiring pool) is now duplicated onto `staff.members`' two
active entries too (7680/7920 for staff-1/staff-2), the same copy-from-bound-candidate pattern task #32
already established for the five skill fields. New `VerticalSliceSimulation._apply_daily_staff_wages()`,
mirroring `_apply_daily_fixture_maintenance()`'s exact shape, sums it across every active staff member and
deducts the total once per simulated day via `economy.record_explicit_expense("staff_wages", ...)`. Charged
in full rather than prorated by hours worked, since this client has no shift/hours-worked tracking for
staff at all to prorate against. Fixing this also forced two existing `headless_smoke.gd` tests to update:
the month-end settlement test's expected cash now accounts for the wages charged across the 4 day
boundaries crossed, and its `expected_cash_after_month_end` formula was rebuilt from `_settle_month_end()`'s
own arithmetic (`cash_at_month_start + month_result_yen`) rather than reusing a pre-day-boundary cash
snapshot that, only before day-boundary expenses existed, happened to equal the pre-settlement figure; the
promotion-firing test now tracks how many day boundaries were actually crossed while waiting for the
promotion to trigger and adds that many days' wages to its expected deduction. Also corrected
`staff_candidates_evidence_note`, which had gone stale in the same way task #43 caught for
`staff.skill_evidence_note` (it still claimed register_skill/replenishment_skill were future-only and
listed salary among unconsumed fields, both now false). See decision 0116. `headless_smoke.gd` unchanged
at 764 steps (reused task #46's own scenario rather than adding a new one); `reference_sim` full suite 661
passed/1 xfailed.

**Task #48 (2026-09-19)**: the user was offered a choice between wiring staff skill growth (work-event
counting against each candidate's own CONFIRMED_OFFICIAL `*_skill_growth_ceiling`, already flagged as the
next candidate in task #47's own out-of-scope note) and a checkout-anger penalty (blocked on an unconfirmed
trigger threshold/floor reference_sim itself leaves for callers to invent), and chose skill growth. New
`game/scripts/domain/staff_growth.gd` ports `reference_sim/conveni_sim/staff_growth_resolution.py` +
`remake_staff_growth.py` into `apply_checkout_growth()` (register_skill+service_skill) and
`apply_replenish_growth()` (replenishment_skill+cleaning_skill+security_skill), each +1 per completed work
task, clamped to that skill's own growth ceiling. Of these five (task, skill) pairs, only
replenish->replenishment_skill's +1 is CONFIRMED_COMMUNITY; the other four reuse +1 as a
REMAKE_BALANCED_DEFAULT guess, matching reference_sim's own equivalent default. Wired into
`VerticalSliceSimulation` at the two real work-task completion points (checkout phase completion,
`_complete_restock()`), applied regardless of whether the task produced a sale/restocked quantity (the
guide's growth model is about performing the work, not its economic result); deliberately NOT wired into
`apply_explicit_restock()` (the instant UI restock action models no staff work time at all). Not ported:
the manager-education growth bonus (no "who is the manager" designation exists among `staff.members` in
this vertical slice) and clean-task growth (no standalone cleaning task/mechanic exists in this client at
all, unaffected since task #41). `staff.members`' two active entries gained the five `*_skill_growth_ceiling`
fields (CONFIRMED_OFFICIAL, duplicated from their bound `staff_candidates` entry, same pattern as tasks
#32/#47), and `StaffState.reset()` now restores skills to their config-derived starting value (previously a
no-op since skills were static) so `VerticalSliceSimulation.load_state()`'s existing "clears every subsystem
back to its config-derived starting point" comment stays true; skill growth itself is explicitly not part of
the save/load format yet (noted in `save_state()`'s own comment), so a save/load round trip currently reverts
accumulated growth. Fixing this broke the month-end rating scenario's hardcoded `service_value`/
`customer_share_percent` expectations (the scenario's own single checkout grows staff-1's service_skill
17->18 before the rating fires); rewritten to compute both dynamically from the simulation's actual
post-growth state instead of hand-derived literals. See decision 0117. `headless_smoke.gd` gained direct
`StaffGrowth` unit coverage (mirroring CheckoutTiming/RestockTiming's own unit tests) plus growth assertions
added to task #40's existing automatic-restock scenario; 764 steps (no new independent scenario, assertions
only). `reference_sim` full suite 662 passed/1 xfailed.

**Task #49 (2026-09-19)**: the user was offered a choice between the checkout-anger penalty (initially
floated in task #45's investigation and passed over there for lacking a confirmed trigger) and a larger-scope
staff hiring/firing UI, and chose the penalty after a reassessment found it structurally identical to task
#33's own precedent: the -2 effect itself is CONFIRMED_COMMUNITY, only the *shape* of the trigger threshold
needs this project's own REMAKE_BALANCED_DEFAULT invention -- exactly the same situation `checkout_timing.gd`
already resolved for the checkout-duration formula. New `game/scripts/domain/checkout_anger.gd` ports
`reference_sim/conveni_sim/checkout_anger_penalty.py` + `checkout_anger_timing.py`: `SKILL_DELTA := -2`
(CONFIRMED_COMMUNITY, register/replenishment/security/cleaning/service, education/stamina unaffected),
`MINIMUM_SKILL_VALUE := 0` (reuses this codebase's existing non-negative floor rather than inventing a new
one), and `TRIGGER_MULTIPLIER := 2.0` (REMAKE_BALANCED_DEFAULT) applied to `CheckoutTiming`'s own already-
confirmed reference duration -- so the trigger threshold is anchored to already-confirmed data (CLAUDE.md
priority 2, analogy) rather than an unrelated new absolute number (priority 3). Wired into
`VerticalSliceSimulation`'s checkout-service tick: once per checkout, once elapsed service ticks exceed
`trigger_ticks(checkout_ticks)`, applies the penalty to the currently serving staff member and records a
`checkout_anger_triggered` event. `CustomerState` gained `checkout_assigned_ticks`/`checkout_anger_triggered`
to track this per visit. Because both staff-1/staff-2's register_skill already exceed the reference skill
(13), this mechanic never fires under the default roster (and skill growth from task #48 only widens that
margin further, so there is no interaction risk with the existing scenarios) -- it only activates for a
below-reference hire, matching the guide's own causal story. See decision 0118. `headless_smoke.gd` gained
direct `CheckoutAnger` unit coverage plus a new dedicated scenario (a deliberately slow checkout staff
member, with that staff member's own register/service growth ceilings overridden to isolate this test from
task #48's growth so the two mechanics' expected values don't have to be hand-composed); 831 steps (up from
764, the new scenario's own long low-skill checkout). `reference_sim` full suite 663 passed/1 xfailed.

**Task #50 (2026-09-19)**: the user provided 4 PDF scans of two previously-unseen strategy guide
books (「ザ・コンビニ 新人店長実習マニュアル」, ~143 pages, and 「クイックリファレンス」, ~95
pages -- see section 21 below). Four parallel research agents transcribed every page
(`docs/research/strategy-guide-shopkeeper-manual-part{1,2}-2026-09-19.md`, `docs/research/
quick-reference-guide-part{1,2}-2026-09-19.md`). The 新人店長実習マニュアル turned out to be
the exact same physical source already cited in `baseline_data.py` as `本1.pdf`/`本2.pdf` (an
independent re-verification, not new territory); the クイックリファレンス's DATA 4 建物 table
likewise turned out already ported as `TOWN_BUILDINGS`. But its 時間 section (p.2) surfaced a
concrete formula that closes an explicit gap decision 0116 had left open: 什器維持費/スタッフ給与
は共に「24時間営業基準の日額」であり、実際には設定営業時間に応じて按分される
(CONFIRMED_OFFICIAL, "維持費...営業時間に応じて"/"人件費...時給×営業時間", independently stated
twice for wages). `VerticalSliceSimulation._scale_yen_to_configured_business_hours()`
(REMAKE_BALANCED_DEFAULT floor-rounding only; the proportional relationship itself is confirmed)
now scales both `_apply_daily_fixture_maintenance()`/`_apply_daily_staff_wages()` by
`demand.opening_minutes_per_day` before summing, replacing the flat-charge simplification tasks
#46/#47 had adopted for lack of this formula. No new staff-shift tracking was needed: the guide's
formula scales by the *store's* configured hours, not by each staff member's individually-worked
hours. See decision 0119. `headless_smoke.gd` unchanged at 831 steps (only expense amounts
changed, not scenario length); `reference_sim` full suite 663 passed/1 xfailed (2 existing
contract tests updated, no new test functions added). Several other findings from this research
pass -- some contradicting already-CONFIRMED values, some closing other open gaps -- were
deliberately left untouched pending further triage; see section 21 for the full catalogue.

**Task #51 (2026-09-19)**: continuing directly from task #50, two items flagged as CONTRADICTS in
section 21.4 were re-verified against the original PDF scans (still accessible this session) rather
than left open indefinitely. Directly re-reading 「新人店長実習マニュアル」book pp.34-35 confirmed,
in the guide's own prose ("お客さんに怒られると店員全員の能力が下がってしまう"), that an angry
customer's -2 skill penalty is store-wide (every active staff member), not scoped to whichever staff
member happened to be serving -- CONFIRMED_OFFICIAL, superseding task #49's original single-staff-
member scoping (a REMAKE_BALANCED_DEFAULT simplification made without this evidence). `Vertical
SliceSimulation`'s checkout-anger handling now loops `_checkout_anger.apply_penalty()` across
`staff.all_staff()` instead of only `staff.checkout_staff()`. Separately, re-reading book p.118
directly confirmed bench maintenance is 160 yen/day (matching existing code exactly), resolving the
"168 yen/day" secondary data point section 21.4 had flagged from the other book's indirect
hourly-rate derivation -- no code change needed there, just confirmation. Also fixed a stale
`PROJECT_MEMORY.md` section 11 (still showing wiki-derived airship/radio/tv popularity-gain figures
+30/+50/+100; `baseline_data.py` already had the guide-correct +40/+60/+90, independently re-
confirmed against book p.120's own "広告データ" table this task). See decision 0120.
`headless_smoke.gd` unchanged at 831 steps (existing scenario extended with new assertions, no new
scenario); `reference_sim` full suite 663 passed/1 xfailed.

**Task #52 (2026-09-19)**: the same book page 35 that task #51 re-read also confirmed a second,
previously-uncoded mechanic (CONFIRMED_OFFICIAL): "怒りやすいお客さんは、おじさんやおじいさんに
多い。もしレジ前の混雑にこの人が混じっていたら、カーソルをこの人に合わせて決定ボタン。怒り出す
まえに"つまみだす"を選んで、お店の外に出してしまうといいぞ。" -- an explicit player action to
eject a customer from the checkout queue/service before they can get angry, forfeiting their
purchase. `VerticalSliceSimulation.try_eject_customer(customer_id)` transitions a customer in
`waiting_checkout`/`checkout` phase to the existing `"leaving"` phase (reusing the no-sale-sellout
pattern rather than inventing a new one), freeing the checkout staff/dequeuing as needed. Whether an
ejected customer's already-picked-up basket returns to shelf stock is unconfirmed by any source;
this project's own REMAKE_BALANCED_DEFAULT choice is that it does not (no other "undo a pick-up"
mechanic exists in this client to reuse). Following task #38's own established discipline that
economy/gameplay actions must be reachable from the UI, not only headless_smoke.gd, this task also
added `EjectCustomerOption`/`EjectCustomerButton` to the STORE STATUS panel, refreshed every tick
(unlike the other catalog-driven option lists, the set of ejectable customers changes on its own as
customers walk through the store, not only after an explicit player action). See decision 0121.
`headless_smoke.gd` grew from 831 to 897 steps (two new scenarios: a direct backend exercise and a
real-UI exercise reusing task #38's `economy_ui_scene`); `reference_sim` full suite 664 passed/1
xfailed (one new test function).

**Task #53 (2026-09-19)**: a direct re-read of the quick reference guide (book pp.5-6) confirmed
CONFIRMED_OFFICIAL that a price-setting/margin mechanic exists in the original game -- a global
"all items X% off list price" slider (plus a per-item override this task deliberately does not
port) defaulting to a 40% profit margin ("通常は全て40%に設定されており、これが定価と考えられ
る"). `store_rating.gd`'s `price_change_pct` input has been hardcoded to 0 since task #27, with an
explicit comment that no price-setting mechanic existed yet to feed it. `VerticalSliceSimulation.
try_set_price_policy(new_price_change_pct)` now sets a persistent `price_change_pct` state (0 =
baseline, rejected below -100 as this project's own REMAKE_BALANCED_DEFAULT sanity floor), consumed
both at the moment a customer picks up a product (`_apply_price_policy()` scales the product's own
confirmed `sale_price_yen`, floored) and by the monthly rating evaluation (finally passing the real
value instead of a hardcoded 0). Deliberately NOT wired: the confirmed section-8 fact that price is
one factor in customer monopoly/footfall -- no source states a price-to-demand formula, so
`demand_policy.gd`'s arrival rate stays unaffected, matching this project's standing "don't invent
an unconfirmed formula" discipline. `price_change_pct` round-trips through save/load like every
other durable state field (`SAVE_SCHEMA_VERSION` bumped 2->3). Following task #38's UI-reachability
precedent, a `PriceChangeSpinBox`/`SetPricePolicyButton` pair was added to the STORE STATUS panel.
See decision 0122. `headless_smoke.gd` grew from 897 to 957 steps; `reference_sim` full suite 665
passed/1 xfailed (one new test function, plus a stale task-#27 assertion corrected to match the new
wiring).

**Task #54 (2026-09-19)**: re-verified two more section-21.4 items directly against the original
PDF scans. (1) The security-facility (交番/消防署) bonus "conflict" between the two books turned
out not to be a conflict at all: the 実習マニュアル's flat "+40/+30 within a 7-area radius" is
exactly the fully-contained case of the クイックリファレンス's more granular "per-area-cell x rate,
capped at footprint_area x rate" formula (2x2 police x 10/cell = 40; 2x3 fire x 5/cell = 30, both
matching exactly) -- reconciled and documented in section 21.3, though still blocked on this
client's complete lack of a town-facility-placement/spatial-distance model (decision 0095), not on
the formula itself. (2) 小宮千明's `security_skill_growth_ceiling` was re-read directly from book
p.127 as 44, not the 41 currently in both `baseline_data.py` and `vertical_slice.json` (an
adjacent-cell transcription slip, most likely picking up a neighboring column's value) -- fixed in
both files. See decision 0123. No test suite changes (no existing test covered this specific
candidate's specific field); `reference_sim` 665 passed/1 xfailed, `headless_smoke.gd` unchanged at
957 steps.

**Task #55 (2026-09-19)**: decision 0004 (2026-09-05) deliberately left "incidental/add-on purchase
probability" absent, explicitly pending "guide/video evidence... strong enough," and task #43's
audit kept this boundary standing as "pending an explicit user decision." Section 7's HYPOTHESIS
note was upgraded to CONFIRMED-OFFICIAL this session (see section 7): each customer wants ~3
additional in-stock products beyond their primary plan, bought after it. Asked the user directly
whether to lift the boundary now that this evidence exists; they said yes. `VerticalSliceSimulation.
_start_default_customer()` now appends up to `INCIDENTAL_WANT_PRODUCT_COUNT` (3) extra product ids,
drawn via a uniform-random pick from currently-stocked products (reusing the shared demand RNG, not
a new stream), to a demand-driven customer's plan -- no new phase or mechanic needed, since the
existing multi-product plan/pickup machinery already supported an arbitrary-length ordered list.
Deliberately scoped to demand-driven admission only: `start_explicit_customer()` (the observation-
replay path) is untouched and still replays exactly the caller-supplied plan, so existing
determinism there is preserved. `CustomerRoster.admit_default()`'s signature changed to take the
caller's (possibly-extended) plan instead of always reusing its own static default list internally.
See decision 0124. `headless_smoke.gd` grew from 957 to 1009 steps (one new scenario, made RNG-
seed-independent by stocking exactly one extra product so the incidental draw is deterministic);
`reference_sim` full suite 666 passed/1 xfailed (one new test function).

**Task #56 (2026-09-20)**: the `staff_candidates` pool (task #32, 35 named CONFIRMED_OFFICIAL
candidates) has existed since early in this project, but `staff.members`' two roster slots
(staff-1/staff-2) were always statically bound at config load time to one fixed candidate each, with
no way for a player to actually draw from the other 33. Section 21.3 tracked this as an unwired
CONFIRMED_OFFICIAL mechanic. A direct re-read of the quick reference book p.6 confirmed
CONFIRMED_OFFICIAL that a hiring pool with a normal 2-employee cap exists ("店員は2人まで雇用でき
る"), and separately named a 店長 (manager) role and a "スーパー社員" (super employee, 3-headcount)
mechanic that no source states a formula or trigger condition for. `VerticalSliceSimulation.
try_hire_candidate(staff_id, candidate_id)` now lets a player replace whoever occupies an existing
roster slot with a different candidate from the pool; scoped as a fixed-2-slot swap only (no 3rd
manager slot, no スーパー社員), both tagged REMAKE_BALANCED_DEFAULT and explicitly out of scope in
the decision doc, since neither has a stated formula to implement from. Rejects an unknown staff_id/
candidate_id and a candidate already employed in the other slot; discards the outgoing occupant's
accumulated skill growth (task #48). `staff_roster` was added to `snapshot()`/`save_state()`/
`load_state()` so a hire survives a save/load round trip (`SAVE_SCHEMA_VERSION` 3->4); `load_state()`
reapplies it via `StaffState.hire()` directly rather than the guarded `_apply_hire()`, since applying
the cross-slot collision check one slot at a time immediately after `staff.reset()` could spuriously
reject a legitimate two-slot swap reload. Wired into the actual HUD (`StaffSlotOption`/
`HireCandidateOption`/`HireCandidateButton` in `main.tscn`/`main.gd`), not only
`headless_smoke.gd`/`VerticalSliceSimulation`, per the task #38 UI-reachability discipline. See
decision 0125. `headless_smoke.gd` grew from 1009 to 1046 steps (direct try_hire_candidate scenario,
UI-reachability scenario, and a save/load round-trip check); `reference_sim` full suite 668 passed/1
xfailed (one new test function; also fixed a stale `SAVE_SCHEMA_VERSION := 3` hardcoded assertion in
the price-policy test that this task's version bump to 4 would otherwise have broken).

**Task #57 (2026-09-20)**: section 21.3's "Facility/scenario data" item flagged a full 建物面積
breakdown (総面積/建物全体/床面積/店外スペース) for all 6 store variants (店舗1-6) as CONFIRMED_
OFFICIAL, cross-checked value-for-value against the already-ported `本2.pdf` source in the newly
transcribed `docs/research/strategy-guide-shopkeeper-manual-part2-2026-09-19.md` section 4.1, but
never actually ported as fields on `StoreVariant` -- only `editable_floor` (店舗内, the in-store
placement grid) and `construction_price_yen` were. Unlike most of section 21.3's remaining items,
this one is not blocked on a missing subsystem (no town/map spatial model, no rival-store entity):
it is pure reference data with an established "hold it even though nothing consumes it yet" landing
spot (the same pattern `land_value_yen`, decision 0095, and fixture `service_bonus`/
`maintenance_yen_per_day` already established), so it was ported directly. Added `total_area_tiles`/
`whole_building_area_tiles`/`floor_area_tiles`/`exterior_space_tiles` (each `Optional[EvidenceValue]`)
to `reference_sim/conveni_sim/models.py`'s `StoreVariant` and populated all 6 `STORE_VARIANTS`
entries in `baseline_data.py`. Confirmed these are genuinely distinct from `editable_floor` (not a
derivable width*height duplicate) with a dedicated test assertion. `reference_sim`-only change: `game/`
has no multi-store-variant selection mechanism at all (it hardcodes the `small_top` prototype size
per decision 0100), so there is nowhere yet for this data to be consumed or even displayed on the
Godot side, and no Godot files were touched. See decision 0126. `headless_smoke.gd` unchanged at 1046
steps (re-run to confirm no regression); `reference_sim` full suite 668 passed/1 xfailed (one new test
function).

**Task #58 (2026-09-20)**: decision 0095 (task #26) had declined to build any town/map spatial
simulation, reasoning that `reference_sim` itself had no spatial model and inventing one would fill
"the area with the thinnest evidence" without an anchor. The user re-shared the source PDFs (this
time split into 4 files instead of 2) and explicitly asked to begin the spatial model now. A direct
re-read of the strategy guide's own distance diagram (book pages 6-7) re-confirmed data that was
already CONFIRMED_OFFICIAL but sitting unconsumed in the codebase: four concentric radii from a
store -- 5 tiles (new-store construction minimum spacing), 7/11/15 tiles (tobacco/alcohol/medicine
permit mutual-exclusion) -- already ported as `PermitDefinition.exclusion_distance_tiles` but with
every `game/data/vertical_slice.json` permit entry's own evidence_note stating "not enforced here:
no town/rival spatial model exists in this client yet (see task #26)". Also re-confirmed the guide's
"来店手段/エリア半径" table (book page 31, `TRADE_AREA_RADIUS_TILES`, already CONFIRMED_OFFICIAL)
and noticed `remake_rival_policy.RivalPolicyInputs.trade_area_overlap_ratio` had always been an
abstract caller-supplied float with no caller able to actually compute it. Rather than reopening
decision 0095's declined full town/map simulation (map size, facility placement, population growth --
still no evidence for any of these), this task added a narrower `reference_sim/conveni_sim/
remake_town_spatial.py`: pure functions operating on caller-supplied `Position` (x, y) tuples --
`chebyshev_distance_tiles()`, `can_construct_store_at()`/`can_acquire_permit_at()` (both directly
enforcing the four CONFIRMED_OFFICIAL radii above, `STORE_CONSTRUCTION_MIN_DISTANCE_TILES=5` newly
promoted from a code comment to an actual named constant), and `trade_area_overlap_ratio()` (a
REMAKE_BALANCED_DEFAULT circle-circle geometric overlap computation over the CONFIRMED_OFFICIAL
trade-area radii). Added integration tests in `test_remake_rival_policy.py` actually driving
`RemakeBalancedRivalPolicy.decide()` from a computed overlap ratio -- the first real caller for that
input, closing the "no caller exists, would just be dead code" concern decision 0095 raised for the
rival policy module specifically. `reference_sim`-only, same as task #57: no rival-store entity (with
a tracked position and known permit holdings) exists in `game/` yet to wire `can_acquire_permit_at()`
into `try_purchase_permit()`, and the town-map-scale, rival-spawn-algorithm, and per-rival-permit-
ownership questions remain genuinely unanswered by any source -- all left as open gaps, not invented.
Security-facility coverage's police-box/fire-station bonus (section 21.3's other spatial item) needs
a different computation (footprint-rectangle-vs-radius area overlap, not point-to-point distance) and
was not attempted here. See decision 0127. `headless_smoke.gd` unchanged at 1046 steps (re-run, no
regression); `reference_sim` full suite 696 passed/1 xfailed (28 new test functions: 26 in the new
spatial-module test file, 2 rival-policy integration tests).

**Task #59 (2026-09-20)**: decision 0127 (task #58) had explicitly deferred wiring
`remake_town_spatial.py`'s permit-exclusion rule into `game/`, since no rival-store entity (a
tracked position and known permit holdings) existed in this client yet. This task added exactly
that: `game/scripts/domain/town_spatial.gd` (a Godot port of only the piece of `remake_town_
spatial.py` with an actual caller here -- `can_acquire_permit_at()`/`chebyshev_distance_tiles()`;
`trade_area_overlap_ratio()` still has no Godot caller, so it stays unported) and two new
`VerticalSliceSimulation` fields, `_player_store_position` (a REMAKE_BALANCED_DEFAULT coordinate
origin -- this client still has no real town/map spatial simulation, decision 0095, so this is only
a reference point for distance math) and `_rival_stores` (a static, config-supplied roster of
position + held-permits; defaults to empty/no-op, same convention as `demand.rival_store_count`'s
own default). `try_purchase_permit()` now calls a new `_can_acquire_permit()` helper that rejects a
purchase if a configured rival within that permit's CONFIRMED_OFFICIAL exclusion radius (7/11/15
tiles for tobacco/alcohol/medicine, book pages 6-7) already holds it -- the rule stated on book page
9 that was ported as data back in task #26 but explicitly marked "not enforced here" ever since.
`exclusion_distance_tiles` is now an actual numeric field on each `vertical_slice.json` permit entry
(previously only mentioned in prose inside its evidence_note). `STORE_CONSTRUCTION_MIN_DISTANCE_
TILES` (5 tiles, same diagram) is ported in `town_spatial.gd` but still unenforced anywhere in
Godot: `try_expand_chain()` has no store-placement mechanic to attach a construction-distance check
to. See decision 0128. `headless_smoke.gd` grew from 1046 to 1106 steps (two new scenarios: a
near-rival-blocks/far-rival-doesn't-block case, and an exact-radius-boundary case); `reference_sim`
full suite 697 passed/1 xfailed (one new test function).

**Task #60 (2026-09-20)**: a standing self-correction. Section 21.3's land-purchase-cost item had
been described (including in this session's own earlier status summary to the user) as blocked on
missing evidence, alongside similar framing suggesting some systems might permanently stay
unimplemented for lack of confirmed data. The user directly corrected this: CLAUDE.md's own 3-tier
priority order (recovered evidence -> analogy from confirmed related data -> this project's own
tagged REMAKE_BALANCED_DEFAULT placeholder, "the last resort, not the default") means nothing is
meant to stay permanently blocked on missing evidence -- tier 3 always exists precisely so every gap
gets filled, tagged appropriately. `land_value_policy.gd`'s entire growth-factor structure and
`remake_rival_policy.py`'s entire decision policy are existing examples of exactly this: full
REMAKE_BALANCED_DEFAULT structures built over confirmed factors, not held back pending more
evidence. Applying that same standing methodology (not a new one) to the land-purchase-cost item:
the guide's own 建てる場所や店の規模を決める page (実習マニュアル book page 7) states 必要金額=
土地代(エリア地価×エリア数)for a vacant lot, or +建物評価額の50%(CONFIRMED_OFFICIAL rate) for
an occupied one. Added `RemakeBalancedLandValuePolicy.land_purchase_cost_yen()` to `remake_land_
value.py`: it reinterprets the existing `current_land_price_yen()` as a per-area rate (analogy-based
-- the same already-established uniform-town-wide-price simplification from decision 0095, applied
per-area instead of per-whole-plot, not a new one) multiplied by an `area_count` meant to be sourced
from a store variant's own CONFIRMED_OFFICIAL `total_area_tiles` (task #57) -- on the inference
(analogy-based, not confirmed) that this project's "エリア" and "tile" units are the same, since the
police-box/fire-station security bonus formula and this store-size table both describe footprints in
"エリア" units matching known tile footprints elsewhere. `reference_sim`-only for now: `game/` has no
multi-store-placement mechanic (`try_expand_chain()` is a purely abstract number, not a site-purchase
action) to actually call this from yet, same boundary as tasks #57/#58. See decision 0129.
`headless_smoke.gd` unchanged at 1106 steps (re-run, no regression); `reference_sim` full suite 705
passed/1 xfailed (8 new test functions).

**Task #61 (2026-09-20)**: continuing the same corrected methodology from task #60. `store_value.
SecurityFacilityCoverage`'s own docstring explicitly left "the spatial search itself (counting how
many area tiles of a facility fall in that range)... out of scope" -- it only turns an already-
counted tile count into the CONFIRMED_OFFICIAL bonus (police box +10/tile up to +40, fire station
+5/tile up to +30, both within a 16-tile "店舗周囲16×16エリア" range). All the inputs that spatial
search needs were already CONFIRMED_OFFICIAL and sitting in `baseline_data.TOWN_FACILITIES`: police_
box's (2, 2) footprint and fire_station's (2, 3) footprint. Added `remake_town_spatial.facility_area_
tiles_within_range(store_position, facility_position, facility_footprint, range_tiles)`, reusing
task #58's `chebyshev_distance_tiles()` to count how many of a facility's footprint tiles fall within
range of the store -- its output is exactly what `SecurityFacilityCoverage`'s `police_box_area_
tiles`/`fire_station_area_tiles` fields expect. Added an integration test that actually feeds this
function's output into `SecurityFacilityCoverage` and checks the confirmed bonus formula fires
correctly -- the first real caller of those fields computed from positions rather than a caller-
supplied constant. The "16x16エリア範囲内" region's exact shape/anchor is still not stated by any
source; this reuses `store_value.py`'s own pre-existing implicit reading of it as a Chebyshev-
distance threshold (not a new interpretation introduced here), flagged the same way task #58 already
flags its own distance-metric choice. `reference_sim`-only: this client still has no security-
facility placement mechanic (`TownState` remains non-spatial, decision 0095) to call this from in
`game/`. See decision 0130. `headless_smoke.gd` unchanged at 1106 steps (re-run, no regression);
`reference_sim` full suite 713 passed/1 xfailed (8 new test functions).

Task #62 (シナリオ初期ライバル構成 + 自社/ライバル合計店舗上限) picks up the handoff-7-flagged
"rival spawn timing/location" candidate, but scopes it to what `docs/research/scenario-initial-
rival-topology-2026-09-06.md` (an existing but previously unimplemented research doc) actually
confirms: PS long-play records state the intermediate scenario starts with 1 headquarters + 2
rival branches ("ライバル店は最初3店舗ありました") while the advanced scenario starts with just a
headquarters and grows branches over its first 2 years -- two genuinely different topologies, not
a single shared default. `ScenarioDefinition` (models.py) gained three new `Optional[EvidenceValue]`
fields (`initial_rival_store_roles`, `initial_rival_branch_exists`, `rival_can_open_branches_
after_start`), left `None` wherever unconfirmed (beginner's exact rival count stays UNKNOWN, only
"at least one branch exists" is confirmed). A new `scenario_initial_rival_topology.
seed_rival_chain_for_scenario()` turns the confirmed role list into a populated `rival.
RivalChainRuntime`, using an opaque placeholder `location_id` string (not a spatial claim --
`rival.py`'s `location_id` was already an opaque key, not a position) since exact coordinates are
UNKNOWN. Separately, two independent CONFIRMED_COMMUNITY sources (the first-title wiki and a PS
long-play record) agree on a hard "player + rival combined <= 10 stores" map-wide construction cap,
distinct from the intermediate scenario's own "reach 10 player stores" clear condition that happens
to share the same number; added as `town.TOTAL_STORE_CAP_INCLUDING_RIVALS` plus a non-mutating
`TownState.has_capacity_for_new_store()` check. `reference_sim`-only, as usual for this class of
work: no `game/` scenario-selection or multi-rival-placement mechanic exists yet to wire this into
(same decision-0095/0128 boundary), and the rival policy's EXPAND/HOLD/RETREAT decisions
(`remake_rival_policy.py`) are still not integrated with this new seeding/cap machinery -- that
integration loop is left for a future task. See decision 0131. `reference_sim` full suite 722
passed/1 xfailed (9 new test functions); `game/` untouched.

**Task #63 (2026-09-24)**: the user re-shared the same 4 PDF strategy-guide scans already fully
transcribed in task #50 (2026-09-19) and asked to continue system-side work. Rather than
re-transcribing from scratch, this session re-opened the two pages already flagged as CONTRADICTS
in section 21.4 at 400dpi (`pdftoppm -r 400` + targeted `convert -crop`), well above the original
scan resolution, and read them directly. Two items resolved with high confidence: (1) the quick
reference guide's 天候のパーセンテージ設定 table (book page 3) actually has 5 columns 快晴/晴れ/
曇り/雨・雪/荒天 (荒天 glossed as "大雨・雷雨・台風・大雪") -- different from both the existing
code comment's claimed columns and the task #50 transcription's own moderate-confidence reading;
all 12 monthly rows now sum exactly to 100 (task #50's reading had 3 rows that didn't). (2) the
same page's 年間カレンダー table gives an exact weekday/holiday flag per (month, representative
day 1-4), confirming `clock.py`'s existing "day==4 is the only holiday" simplification -- whose own
comment invited replacement "if the guidebook contradicts it" -- is wrong for January/May/August/
December, each of which carries one extra 休日. Also directly re-confirmed the business-hours
preset③ text ("AM11:00~AM2:00 (16時間営業)") is exactly what the source prints (an internal
15h-vs-16h-label inconsistency in the original book itself, not a scan misread as task #50 had
guessed). New `baseline_data.ANNUAL_CALENDAR`/`MONTHLY_WEATHER_PERCENTAGES`/
`BUSINESS_HOURS_PRESETS` (all CONFIRMED_OFFICIAL) hold this data; `clock.py`'s
`representative_day_type` now looks up `ANNUAL_CALENDAR` instead of the old day==4 rule, and
`remake_customer_share.BAD_WEATHER_VALUES` is corrected/extended to match the real column
vocabulary. `reference_sim`-only, matching the established "add confirmed data even before a
consumer exists" pattern for the weather/hours tables: `game/` has no weekday/holiday, weather-
roll, or business-hours-preset-selection mechanic to wire these into yet. See decision 0132.
`reference_sim` full suite grew from 725 to 726 passed/1 xfailed (two existing tests -- the day==4
clock assumption and the 14-month calendar-invariant fuzz test -- rewritten to compute their
expected values from `ANNUAL_CALENDAR` itself rather than a hardcoded simplification; four new
test functions for the three new tables).

**Task #64 (2026-09-24)**: continuing the same session, the task #50 research catalogue (section
21.3) flagged a 都庁(metropolitan government building) auto-build population threshold as a
candidate to upgrade from PROVISIONAL/CONFIRMED_COMMUNITY to CONFIRMED_OFFICIAL: the strategy
guide's own body text (quick reference book, マップ攻略 section, pages 80-83) states directly
"20000人の人口を集めれば、役所用地に都庁が建設される" for the beginner scenario's clear
condition. `baseline_data.SCENARIOS`'s `beginner.objective` field previously cited only a wiki
source at CONFIRMED_COMMUNITY with no numeric threshold anywhere in code; its evidence level is
now CONFIRMED_OFFICIAL, citing the guide's own text, and new `store_events.
METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD` (20,000) plus `metropolitan_government_is_induced()`
give the actual number for the first time. Investigating the same research section's other
candidate (contest-prize eligibility gated on cleanliness value) found only qualitative advice
("keep cleanliness maxed") with no stated number or probability, so it was left alone rather than
inventing a threshold -- consistent with `store_events.py`'s existing decision (0099) not to model
the contest's own "may or may not be picked" draw at all. `reference_sim`-only: `game/` has no
scenario-selection mechanic to attach a beginner-specific clear condition to (same boundary as
task #62/decision 0131). See decision 0133. `reference_sim` full suite grew from 726 to 730
passed/1 xfailed (4 new test functions).

**Task #65 (2026-09-24)**: after tasks #63/#64, a background agent was asked to transcribe all 115
pages of the same 4 re-shared PDFs in full (independent of the already-existing task #50 research
docs, as a fresh cross-check). It reported that PDF4 (`d9b60a50-downloadfile3.PDF`) pages 10-24 are
not more of the already-known 2-book set at all, but a **previously-unseen third companion book**
("攻略&データブック", オールテクニックガイド + データリスト). Two of its findings were directly
re-verified at 400dpi and implemented:

1. **Angry-customer store-rating penalty, wired for the first time.** Print page 75's rank table
   footer states "お客に怒られる=1/6の確率で-1、万引き=-1、寄付イベント=+5" -- re-verification
   found this exactly CONFIRMS constants `store_rating.py`/`store_rating.gd` already carried
   (`ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY=(1,6)`, `_POINTS=-1`, `SHOPLIFTING_DOWNGRADE_POINTS=-1`,
   `DONATION_UPGRADE_POINTS=5`), but decision 0096 (task #27) had left all three unwired because "no
   trigger events exist in this client." That premise is now stale for the angry-customer case
   specifically: task #49 (2026-09-19) wired a real `checkout_anger_triggered` event that fires on
   every slow checkout. `vertical_slice_simulation.gd`'s existing anger-trigger block now also rolls
   this 1/6 chance (reusing the shared `_demand_rng`, matching task #55's "one shared random stream"
   convention) and applies the confirmed -1 to `internal_rating_value` when it hits, recording
   `rating_penalty_applied`/`internal_rating_value` on the event. Shoplifting/donation stay unwired
   (no such mechanics exist in `game/` at all yet) -- decision 0096's reasoning still holds for those
   two. See decision 0134.
2. **New-branch land cost's exact area multiplier.** Print page 79 states directly "新規出店時の
   土地代 = 地価（4エリア分）+建物評価額／2" -- a fixed 4-area count for opening a new branch,
   independent of store size, distinct from decision 0129's `total_area_tiles`-based analogy (which
   remains this project's best guess for some other, not-yet-built land-purchase context). Investigating
   this surfaced a real, concrete gap: `chain_expansion_cost_yen()` (task #30's abstract chain-
   expansion cost) had never actually called `land_purchase_cost_yen()` at all -- it charged the bare
   per-area land price with an implicit ×1. New `NEW_BRANCH_LAND_AREA_COUNT=4` (both
   `remake_land_value.py` and `vertical_slice_simulation.gd`) now makes `chain_expansion_cost_yen()`
   charge exactly ×4 the per-area rate; the formula's other "+建物評価額／2" term is not applied,
   since `try_expand_chain()` still has no specific plot/existing-building to appraise (decision 0099's
   abstraction is otherwise unchanged). See decision 0135. Both fixes are corrections to code already
   believed complete, not new-territory guesses -- this is exactly the kind of gap CLAUDE.md's evidence
   discipline exists to catch (a stale "unwired" premise, and an inference quietly overridden by a more
   specific confirmed number). `reference_sim` full suite grew from 730 to 731 passed/1 xfailed (one
   new test function; task #64's own additions already covered in that count). `headless_smoke.gd`
   step count unchanged (assertions added to two existing scenarios, no new scenario). The remaining
   findings from this background pass (item-level 季節 tags for cold/hot drinks & おでん/中華まん,
   aisle-width exact rule, per-building hourly customer-frequency matrices, exact security-value/
   cleaning-value formulas with store-size multipliers, the secret 極上 map's 5-rival starting
   handicap, and more) are catalogued in the agent's full 115-page transcript, now committed at
   `docs/research/strategy-guide-third-companion-book-full-extraction-2026-09-24.md` (its own header
   notes which parts this session independently re-verified at higher resolution vs. which remain
   first-pass only), for a future session to triage -- not all implemented in this pass.

**Task #66 (2026-09-24)**: the user chose "passage-width/passing constraint" from the section
21.3-style candidate list this session's research surfaced. A 400dpi re-verification of the quick
reference guide's 店舗 section (book page 5) directly confirms "1マス通路...客や店員が2人並んで
通れる幅。すれ違えるので混雑しにくい" / "1/2マス通路...客や店員1人が通れる幅。すれ違うこと
ができず、混雑しやすい" -- upgrading `store_grid.py`'s existing `subcells_per_tile=2` default
(previously flagged as an unconfirmed 0.5-tile granularity guess) to CONFIRMED_OFFICIAL, and
revealing that the passing/congestion RULE itself had never been wired anywhere: customer/staff
movement had zero collision checking, so multiple actors could freely overlap the same subcell.
New `VerticalSliceSimulation._subcell_is_free_for()`/`_try_move_along_route()` enforce exclusive
subcell occupancy (no two actors share a subcell) across all 4 existing movement call sites
(customer to_shelf/to_checkout/leaving, staff to_restock) -- this reproduces both guide rules as an
emergent property (a 2-subcell corridor always has a free parallel cell, a 1-subcell corridor does
not) without needing an explicit direction-aware corridor-width calculation the guide doesn't
specify. A blocked actor waits in place and retries next tick (REMAKE_BALANCED_DEFAULT choice; the
guide separately confirms multi-route detours are possible but not whether a blocked individual
actor reroutes or waits). The checkout interaction cell is explicitly exempted, since task #36's
queued-customer design already deliberately converges multiple customers' logical position there
(cosmetic-only offset in the renderer) -- without this exemption the FIFO queue itself would break
(a second customer could never finish "arriving" to be enqueued). `reference_sim`-only doc update
(no logic change there; no real-time collision runtime exists there to wire this into).
`game/scripts/headless_smoke.gd`'s existing task #36 concurrent-customer scenario (two customers
with an identical plan, admitted in the same tick so they start stacked on the entry subcell) was
extended to verify the new invariant holds every tick and that the trailing customer is actually
forced to wait at least once (proving the scenario isn't vacuously passing). See decision 0136.

**Task #67 (2026-09-24)**: the user chose "asset wiring" as the next direction after this session's
system-side fixes (tasks #63-#66), matching task #46's own standing development order ("build out
the system side completely first, then generate images/audio and wire them"). This is the project's
**first asset-integration work** -- `game/` previously had zero image assets; `store_view.gd`'s
`_draw()` drew only colored rectangles. Scoped to fixtures only (of the several asset categories
sitting in `assets/raw/`, per the 2026-09-24 handoff): `assets/raw/conveni_fixtures_remake_v3/`'s
manifest turned out to have exactly one sprite per `fixture_catalog` catalog_id (all 35, zero
mismatch either direction), the cleanest of the un-wired packages. Sprites were copied into
`game/assets/fixtures/` (Godot can only load `res://`-relative paths, not the project-external
`assets/raw/`), and `store_view.gd`'s `_draw_fixtures()` now draws the matching texture via
`draw_texture_rect()` when one exists, falling back to the pre-existing colored-rect+label rendering
otherwise (nothing regresses for a fixture with no sprite). `checkout-1`/`shelf-1`/`shelf-2` predate
the catalog system entirely (task #39/#41) and carry no `catalog_id` at all; a new
`FALLBACK_VISUAL_CATALOG_ID_BY_KIND` gives them a same-footprint stand-in sprite
(`register_1`/`medium_ambient_shelf`) for display only -- explicitly not a claim that these specific
scenario fixtures ARE those catalog items. These sprites are this project's own newly-generated art
(REMAKE_BALANCED_DEFAULT visual tier, per PROJECT_MEMORY section 1's 2026-09-21 personal-use policy),
not a recovered original asset. `headless_smoke.gd`'s existing task #38 UI scenario (the only one that
actually instantiates `main.tscn` into the scene tree) now also verifies every one of the 35
catalog sprites, plus the `register_1` fallback, actually loads as a real `Texture2D` under a fresh
CI editor import -- not just that the files exist on disk. See decision 0137. `reference_sim`
untouched (this task is `game/`-only); could not run `headless_smoke.gd` locally (no Godot binary in
this sandbox) so this was validated via the CI feedback loop established in tasks #63-#66. Explicitly
out of scope: product overlays, staff sprites, customer sprites, the town map, and the 5 menu-UI
asset packages -- each a separate future task; fixture rotation does not yet change which sprite
variant is drawn (no orientation-specific sprites exist in the source manifest).

**Task #68 (2026-09-24)**: after task #67 merged (PR #244, both CI checks green), the user chose
"product overlays" as the second asset-wiring pass. `assets/raw/conveni_products_remake_v3/`
(same brief as the task #67 fixture package) ships 25 product-category sprites x 3 stock states
(high/medium/low, 75 PNGs total, `<catalog_id>_<state>.png`) copied into `game/assets/products/`.
Investigating how to pick the right sprite surfaced a real gap: `InventoryState` never recorded
which `product_catalog` category a procured product actually was -- `try_procure_product()` looked
up `catalog_id` to price the purchase and then discarded it, so even a catalog-procured product
had no data-level link back to its category. New `InventoryState.catalog_id` threads that
already-known value through instead of inventing one. The two task #38 pre-catalog-system
prototype products (`prototype-bread`/`prototype-drink`, whose prices don't match their
same-named `product_catalog` entries) still get no `catalog_id` in the data itself -- same
judgment as task #67's checkout-1/shelf-1/shelf-2 -- and instead resolve through a new
`store_view.gd` display-only fallback (`FALLBACK_PRODUCT_CATALOG_ID_BY_PRODUCT_ID`). Since each
sprite already depicts its own unit count as artwork (no per-unit scaling needed in code), the
only invented value is which stock-ratio cutoff switches the displayed sprite between the three
states; 0.66/0.33 are tagged REMAKE_BALANCED_DEFAULT, and `_draw_product_overlay()` repeats the
sprite once per footprint tile per the source README's own instruction ("2x1や3x1はタイルごとに
繰り返す"). `product_catalog`'s one sprite-less category (`copy_paper`, per the source package's
own README) is asserted to stay sprite-less rather than silently drifting. This task also closed a
tagging-discipline gap task #67 itself had left open: CLAUDE.md requires the REMAKE_BALANCED_DEFAULT
string in a code comment, a `vertical_slice.json` evidence_note, AND a test assertion checking the
tag text is actually present -- task #67 shipped only the code comment. Both task #67's and task
#68's tags now have all three, via two new tests in
`reference_sim/tests/test_game_vertical_slice_contract.py` and new `evidence_note` fields on the two
prototype product entries in `vertical_slice.json`. `reference_sim` full suite grew from 731 to 733
passed/1 xfailed (task #68's own two new contract tests). See decision 0138. Explicitly out of
scope (same boundary as task #67): staff sprites, customer sprites, the town map, the 5 menu-UI
packages, and orientation-aware overlay sprites on fixture rotation.

**Task #69 (2026-09-24)**: after task #68 merged (PR #245, both CI checks green), the user chose
"staff sprites" as the third asset-wiring pass. `assets/raw/staff_v2/staff/` ships 35 anonymous
walking figures (`staff_001`-`staff_035`, 4 directions x 2 walk-cycle phases each, 280 PNGs,
160x160px, feet-anchored at (80,154)), copied into `game/assets/staff/`. Unlike task #68,
`StaffState.candidate_id` already existed (task #56) and needed no new threading -- only
`store_view.gd`'s display side was new. The real gap here was different: the sprite package itself
never links any of its 35 anonymous figures to any of the 35 *named* `staff_candidates` -- no name
is printed on a sprite, and `reference_faces/` (which separately restores each candidate's actual
portrait from the same guide pages, 127-133) ships no sprite-to-portrait correspondence, even
though `STAFF_CANDIDATES`'s own comment cites that identical page range. That page-range overlap
makes a same-order correspondence plausible but unverified, so it is not treated as confirmed:
`_staff_sprite_id_for_candidate()` instead assigns sprites purely by each candidate's list position
in `staff_candidates` (index 0 -> `staff_001`, ...), tagged REMAKE_BALANCED_DEFAULT as a
display-only convention, not an identity claim -- the same judgment class as tasks #67/#68's
fallback mappings. Two more choices needed the same tag: using the static "A" walk-cycle frame
always (no idle-specific sprite ships, and no delta-time animation convention exists anywhere else
in this tick-driven renderer to switch to "B"), and deriving on-screen facing direction from each
staff member's own last-observed movement delta (no confirmed rule exists for this either). Both
tasks #67's and #68's established tagging-discipline fix pattern (code comment + test assertion,
this task's feature adds no new `vertical_slice.json` field so there is no per-entry evidence_note
site) was followed via one new contract test. `reference_sim` full suite grew from 733 to 734
passed/1 xfailed. See decision 0139. Explicitly out of scope (same boundary as tasks #67/#68):
customer sprites, the town map, the 5 menu-UI packages, and walk-cycle animation (phase "A" only).

**Task #70 (2026-09-24)**: after task #69 merged (PR #246, both CI checks green), the user chose
"customer sprites" as the fourth asset-wiring pass. `assets/raw/customer_v2/customer/` ships 21
anonymous walking figures (`customer_01`-`customer_21`, same 4-direction/2-phase/160x160/feet-
anchored geometry as task #69's staff package, 168 PNGs), copied (flattened from the source's
one-subfolder-per-character layout) into `game/assets/customers/`. Unlike staff, `CustomerState`
has no identity field at all -- only an opaque `customer_id` -- and is never linked to any of the
21 CONFIRMED_OFFICIAL `CUSTOMER_ARCHETYPES` (book pages 134-143): this vertical slice has no
demand/visit-plan mechanic that assigns an archetype per customer, so there is no real value to
thread through the way task #68 threaded `InventoryState.catalog_id` or task #69 relied on
`StaffState.candidate_id`. `_customer_sprite_id_for_id()` therefore derives a sprite deterministically
from each `customer_id`'s own hash (REMAKE_BALANCED_DEFAULT, not list position -- there is no roster
to have a position in), purely so each customer instance renders as a distinct, consistent-looking
person; it carries no demographic or behavioral meaning. A more "plausible" archetype-from-purchased-
product heuristic was considered and rejected as a stronger, unevidenced invention than a plain
hash. Facing-direction derivation and the static "A" phase reuse task #69's exact logic. Tagging
discipline follows the same code-comment + contract-test pattern as tasks #67/#69 (no new
`vertical_slice.json` field). `reference_sim` full suite grew from 734 to 735 passed/1 xfailed. See
decision 0140. Explicitly out of scope: the town map, the 5 menu-UI packages, walk-cycle animation,
and any actual customer-archetype/demand mechanic (this task is display-only).

**Task #71 (2026-09-24)**: after task #70 merged (PR #247, both CI checks green after fixing a
GDScript type-inference parse error), the user chose "menu-UI asset wiring" as the next direction,
having wired all four world-sprite packages (tasks #67-#70). Investigating the 5 menu-UI packages
(`conveni_menu_fixtures_v1`/`_products_v1`/`_staff_v1`/`conveni_additional_assets_v1`/
`conveni_remaining_assets_v1`) surfaced an important evidence-tier distinction: unlike tasks
#67-#70's world sprites (this project's own newly-generated art, REMAKE_BALANCED_DEFAULT), the 3
menu-icon packages are cropped directly from the strategy guide's own printed menu-icon pages (each
manifest entry cites its exact `source_pdf_page`) -- CONFIRMED_VISUAL evidence for the icon artwork
itself. Their IDs also turned out to match this project's existing data with zero gaps: all 35
`fixture_catalog` and all 26 `product_catalog` entries have a matching icon (plus some unused
"extra" icons for fixtures/products this client hasn't implemented yet, e.g. register_2-4, cash),
and the 35 staff face icons reuse the exact same `staff_001`-`staff_035` numbering task #69 already
established. This made for a clean, contained task: added icons to the 3 existing OptionButton
dropdowns (`fixture_catalog_option`/`product_catalog_option`/`hire_candidate_option` in `main.gd`)
via `set_item_icon()`, reusing `store_view._staff_sprite_id_for_candidate()` (task #69's
REMAKE_BALANCED_DEFAULT position-based mapping) for the staff icons rather than inventing a second
numbering. The other 2 packages (store-select icons, ad icons, ground textures, town-map assets)
were left out of scope -- no corresponding screen exists in this vertical slice yet to wire them
into. `reference_sim` full suite grew from 735 to 736 passed/1 xfailed (one new contract test that
also verifies, at the filesystem level, that every catalog entry actually has a matching icon file
on disk, not just that the code claims so). See decision 0141.

**Task #72 (2026-09-24)**: after task #71 merged (PR #248, both CI checks green), the user chose
"town map/building tiles" as the next direction. Investigating `assets/raw/conveni_map_assets_v2/`
surfaced a serious gap that changed the task's scope before any code was written: its 52 sprites are
all town FACILITIES (schools, parks, restaurants, houses, companies, stations, ...) -- none depict a
convenience store (the player's own or a rival's) -- and this client has zero placement data for any
of the 52 facility types (`TownState` is just two counters; `_player_store_position`/`_rival_stores`,
task #59, are abstract distance-math reference points, not map placements, and `_rival_stores`
defaults to empty). Actually rendering a meaningful town map with those 52 sprites would mean
inventing a full facility layout -- guessing an unconfirmed town spatial simulation, exactly what
PROJECT_MEMORY.md section 17 names as a research gap not to be papered over. Presented with this
finding, the user chose the minimal honest option: show only what the data model already tracks. New
`game/scripts/town_view.gd` draws `_player_store_position`/`_rival_stores` as plain colored markers
on the abstract coordinate grid -- no facility sprites at all, so the default scenario shows exactly
one marker (the player's own store at the origin). Wired as a toggle over the existing StoreView in
`main.tscn` (a "Show town map" button flips visibility) rather than a new scene/navigation flow; this
also surfaced and fixed a real latent bug -- `store_view.gd`'s `_unhandled_input()` had no visibility
guard, so taps would have still tried to relocate fixtures while the town view covered it. Bounding-
box math is a pure function tested directly against a synthetic multi-rival roster via a duck-typed
fake object, independent of any real simulation/scenario data. `reference_sim` full suite grew from
736 to 737 passed/1 xfailed (one new contract test, which also asserts `town_view.gd` contains no
`.png`/`ResourceLoader` reference at all, confirming the 52-sprite package really isn't used). See
decision 0142. Explicitly out of scope: any actual facility-placement/town-growth mechanic, and the
52-sprite package itself (revisit only if confirmed or analogy-based placement data ever surfaces).

**Task #73 (2026-09-24)**: after task #72 merged (PR #249, both CI checks green), the user chose to
return to system-side work after the tasks #67-#72 asset-wiring arc. Picked from section 21.3's
candidate list: unlike the other open items there (town facility placement, rival AI, scenario
selection -- each blocked on a whole new subsystem not yet built), "pre-hire résumé stat band" was
the one candidate scoped entirely to the existing `hire_candidate_option` dropdown, with the needed
data (`stamina`/`academic_background`/`agility`/`sociability`) already CONFIRMED_OFFICIAL in
`staff_candidates` since task #32. The third companion book (task #65's find) directly confirms the
original hiring screen never shows the exact number for these 4 résumé stats before hiring, only a
coarse band ("普通" for 40-69, "高い" for 70-100) -- this client's dropdown has shown the exact real
skill numbers since task #56 (a deliberate simplification, not something to walk back single-
handedly), so the confirmed band is appended as extra source-faithful context rather than replacing
the existing numbers. New `main.gd` `_resume_stat_band()` -- CONFIRMED_OFFICIAL, not
REMAKE_BALANCED_DEFAULT (no invented threshold; verified all 35 candidates' values already fall
within the documented 40-100 range). `reference_sim` full suite grew from 737 to 738 passed/1 xfailed
(one new contract test). See decision 0143. Explicitly out of scope: replacing/removing the existing
exact-number display, and the stamina/academic_background/agility/sociability -> real-skill-pair
correlation model itself (unneeded since this client already holds the real skill numbers directly).

**Task #74 (2026-09-24)**: after task #73 merged (PR #250, both CI checks green), the user chose to
directly audit `game/scripts/save_game_service.gd` (the save/load path) for gaps rather than pick a
new feature. `save_game_service.gd` itself is a thin I/O wrapper with no logic issues; the real state
transform lives in `vertical_slice_simulation.gd`'s `save_state()`/`load_state()`. That function's
own comment already documents two deliberate, known gaps (mid-visit customer/staff walk state; task
#48's staff skill growth). Diffing `reset()` against `load_state()` line-by-line line-for-line
surfaced a real, previously-undiscovered one: `reset()` has always cleared `_checkout_queue`
(task #36's FIFO checkout wait list) right after resetting customers/staff, but `load_state()` never
did. A save taken while a second customer was queued at checkout left that customer_id behind after
`customers.reset()` had already discarded the actual customer record -- the next
`_dispatch_checkout_queue()` call would then null-dereference it (`CustomerRoster.customer()` is a
raw dict lookup returning `null` for a missing id) and crash. This is a genuine, reproducible bug a
real player could hit, not a documented tradeoff. Fixed with one line (`_checkout_queue.clear()`,
matching `reset()`'s own convention exactly) plus a new headless_smoke.gd scenario that actually
reproduces the queued state, saves/loads across it, and confirms the loaded simulation both starts
with an empty queue and keeps running (not crashing) afterward. The rest of the audit (every other
`reset()`-touched subsystem's `snapshot()`/`restore_snapshot()` symmetry, plus `town`/
`_player_store_position`/`_rival_stores`, none of which mutate at runtime) turned up nothing else.
`reference_sim` full suite grew from 738 to 739 passed/1 xfailed. See decision 0144.

**Task #75 (2026-09-24)**: after task #74/PR #251 merged, the user pivoted from system-side audits to
the UI directly ("UIとかは? ゲームとして動くように作りこんでいって" -- what about the UI? build it out
so it actually works as a playable game). Auditing `main.gd`/`main.tscn` against `vertical_slice_
simulation.gd`'s own `snapshot()` found two pieces of already-tracked state that had never been
surfaced anywhere in the UI at all: (1) `day_count`/`month_count` -- the UI only ever showed the
intra-day clock (HH:MM), giving the player no way to know what day or month it currently was, even
though this client's entire economic loop (representative-day/month settlement, staff wages, fixture
maintenance, the 100-year game-over clock) revolves around day/month progression; (2) `is_game_over`/
`game_over_reason`/`clear_condition_met` -- every economy action already silently stopped working via
its own `is_game_over` guard once bankruptcy or the 100-year time limit hit, but nothing ever told the
player why, and there was no way back to the menu or to try again short of quitting the app. Added a
`CalendarValue` label (`"Month %d · Day %d of %d (Day %d overall)"`, reusing the existing CONFIRMED_
OFFICIAL `REPRESENTATIVE_DAYS_PER_MONTH`=4 constant rather than hardcoding it again) and a full-screen
`GameOverLayer` overlay (hidden by default; shows the translated bankrupt/time-limit-exceeded reason,
auto-pauses, and offers "Play Again"/"Return to Menu" wired to the exact same `_on_reset_pressed()`/
`_on_quit_to_menu_pressed()` handlers the sidebar's own buttons already use). `clear_condition_met`
(reaching the PROVISIONAL `PLAYER_STORE_COUNT_SCENARIO_TARGET`=10 stores) is a permanent flag the
player keeps playing past, not a one-time event (per `_evaluate_terminal_state()`'s own comment), so
it got a persistent sidebar label instead of a dismissable modal. Pure UI wiring of already-CONFIRMED/
PROVISIONAL simulation state -- no new REMAKE_BALANCED_DEFAULT tag needed (no new number or mechanic
invented). `reference_sim` full suite grew from 739 to 740 passed/1 xfailed (one new contract test,
covering the real `main.tscn`-instantiated UI end-to-end including a genuine bankrupt game over
reproduced via `_evaluate_terminal_state()`, task #65's own technique). See decision 0145. Explicitly
out of scope: a full visual redesign of the sidebar-debug-tool-style UI itself (this task closed only
the highest-value functional gap -- the total absence of end-state feedback -- not a look-and-feel
pass), and a one-time celebratory notification for `clear_condition_met` (chose the simpler always-on
label over adding "already shown" bookkeeping to the UI layer). CI caught a real bug in the first push:
`clear_condition_met` had only ever been added to `save_state()`'s dict, never `snapshot()`'s, so
`_refresh_ui()` (which reads `snapshot()`) crashed every frame the moment this task's own new code ran.
Fixed by adding the missing field to `snapshot()` alongside `is_game_over`/`game_over_reason` (which it
already had), plus a contract test asserting both dicts carry it so this exact class of
`snapshot()`/`save_state()` field drift can't recur silently.

**Task #76 (2026-09-24)**: after task #75/PR #252 merged, the user picked "見た目のビジュアルポリッシュ"
(visual polish) from a menu of UI/gameplay-feel directions. Introduced `game/themes/ui_theme.tres` --
this project's first hand-authored Godot Theme/StyleBoxFlat resource -- giving `PanelContainer`s a
rounded-corner card look and `Button`/`OptionButton`s real normal/hover/pressed/disabled states (a
teal accent), replacing the fully-default engine theme the sidebar had used since task #38. `theme` is
a `Control`-only property (neither `Node2D` nor `CanvasLayer` has it), so it is applied directly to the
`UI/Panel` and `GameOverLayer/Panel` `PanelContainer` nodes (and `main_menu.tscn`'s own `Panel`) rather
than to an ancestor -- Theme cascades to descendant Controls from there with zero node-reparenting, so
no `main.gd` `@onready` path needed to change. Section headers (`Heading`/`EconomyTitle`/
`StaffHiringTitle`) and `CashValue` got accent-color tints for visual hierarchy; `GameOverTitle` got a
distinct warning-red, separate from the existing amber PROVISIONAL notice and green scenario-cleared
label. Pure UI chrome, not simulated game data -- no REMAKE_BALANCED_DEFAULT tag needed, same as this
scene's pre-existing label colors. Since this sandbox has no Godot editor to validate a hand-authored
`.tres` resource before pushing, `headless_smoke.gd`'s real `main.tscn`-instantiated scenario now also
confirms the theme actually parsed (non-null, `default_font_size == 15`, `has_stylebox()` for both
`PanelContainer` and `Button`) rather than silently falling back to the engine default. `reference_sim`
full suite grew from 740 to 741 passed/1 xfailed (one new contract test). See decision 0146. Explicitly
out of scope: restructuring the sidebar's node tree into separate per-section card panels (too much
`@onready`-path risk for this pass), `SpinBox`/`HSeparator` restyling, a custom font (none exists in
this project's assets), and `store_view.gd`'s own `_draw()`-based canvas rendering.

**Task #77 (2026-09-24)**: after task #76/PR #253 merged, the user directly challenged whether recent
work was still tracking a faithful recreation or drifting into an independent design ("あのさ、今更だけど、
ちゃんと初代ザ・コンビニを再現する方向で動いてる？独自路線を突っ走ってない？"). Checking found a concrete,
correctable gap: task #75's calendar format ("Month X · Day Y of Z (Day N overall)") was invented without
consulting `docs/research/official-screenshot-evidence-2026-09-05.md` section 1, which already had
CONFIRMED_OFFICIAL/CONFIRMED_VISUAL evidence for this -- the official PS-version screenshot `ss01` shows
the date as `01年目01月01日` (year/month/day), with no "day N of 4" or running total-day counter on
screen at all. Fixed `main.gd`'s `_refresh_ui()` to `"Year %d · Month %d, Day %d"`, reusing the same
`(month_count / MONTHS_PER_YEAR) + 1` year computation `_evaluate_terminal_state()` already had (not a
new formula); the month-internal day (1-4) itself was already correct, since `REPRESENTATIVE_DAYS_PER_
MONTH`=4 is independently CONFIRMED_OFFICIAL ("1月=4日間×8") -- only the missing Year field and the
invented "of 4 (Day N overall)" suffix were real gaps. Kept the label text in English rather than the
screenshot's literal Japanese, for consistency with the rest of this client's UI text (a project-goal
choice, not an evidence gap: the confirmed *fact* is the year/month/day structure, not the display
language). `docs/research/official-screenshot-evidence-2026-09-05.md` also documents the original's
interior-editing top command structure as five distinct commands (配置/移動/入れ替え/売却/終了, screenshot
`ss02`) -- this client's own "Prototype layout editor" (tap-to-select, tap-to-place/relocate, one Rotate
button) has never been reconciled with that confirmed structure and no `docs/decisions/` file addresses
it; flagged to the user as a separate, larger-scope follow-up (needs new mechanics this client doesn't
have yet, e.g. an explicit fixture-sell action) rather than folded into this narrower text-format fix.
`reference_sim` full suite grew from 741 to 742 passed/1 xfailed (one new contract test, which also
asserts the research file's own `01年目01月01日` citation is present so this evidence can't silently
disappear). See decision 0147.

**Task #78 (2026-09-24)**: the follow-up task #77 flagged -- reconciling this client's ad-hoc "Prototype
layout editor" (tap-to-select, tap-to-place/relocate, one Rotate button) with the confirmed official
5-command interior-edit structure (配置/移動/入れ替え/売却/終了). 配置 (buy) and 移動 (relocate) already
existed; 入れ替え (swap) and 売却 (sell) did not, and needed new mechanics with no confirmed rule behind
them -- asked the user how to handle the two invented pieces before implementing; answer: "REMAKE_
BALANCED_DEFAULTで発明して進める" (invent with the tag and proceed). Added `store_layout.gd` `try_remove_
fixture()`/`try_swap_fixture_positions()` and `vertical_slice_simulation.gd` `try_sell_fixture()`/
`try_swap_fixtures()`, following the exact snapshot/rollback pattern the existing relocate/rotate
actions already use. `FIXTURE_SELL_REFUND_PERCENT := 50` (half the catalog price back) is this client's
own REMAKE_BALANCED_DEFAULT choice, no source states an actual figure; the swap semantics (exchanging
two already-placed fixtures' positions, distinct from single-fixture relocate) are this client's own
REMAKE_BALANCED_DEFAULT reading of what "入れ替え" does interactively, chosen because it is the one
reading not already achievable via two sequential relocates (a fully packed layout can leave no empty
cell for either fixture to move through). Selling is restricted to fixtures with a real fixture_catalog
origin (no price to refund otherwise), never the checkout fixture (this client assumes exactly one, no
reassignment mechanic), and never a fixture still holding stock -- reusing `try_load_sample_layout()`'s
own "reject rather than silently discard inventory" precedent rather than inventing an auto-clear rule.
`economy_state.gd`'s `record_explicit_expense()` assert was relaxed to allow a negative `amount_yen`
(a rebate through the same ledger) -- every existing caller already always passed non-negative amounts,
so this changes no prior behavior. `store_view.gd` gained an `edit_mode` ("move" default / "swap"); only
in "swap" mode does tapping a second fixture emit a new `fixture_swap_requested` signal instead of just
re-selecting -- "move" mode's tap behavior is byte-for-byte unchanged. `main.tscn`/`main.gd` got an
`EditModeOption` dropdown, a `SellFixtureButton`, and a `DeselectFixtureButton` (終了). Found and fixed a
stale test boundary along the way: task #37's own contract test had asserted `try_sell_fixture` must NOT
exist, encoding the "keep sell/remove fixture a separate research question" scope decision from
`docs/research/ss-layout-entrance-register-and-chain-cannibalization-2026-09-06.md` -- updated it to
reflect that this boundary was deliberately revisited (only `try_undo_sample_layout` remains out of
scope from that original note). `reference_sim` full suite grew from 742 to 743 passed/1 xfailed. See
decision 0148.

**Task #79 (2026-09-24)**: after task #78/PR #254 merged, the user picked "操作フローの改善"
(workflow/UX cleanup) as the next direction but immediately raised a second recreation-fidelity
challenge on the option text itself: "商品仕入れとか書いてあるけど、実際の初代ザ・コンビニには
商品の仕入れとかなかったはずだけど？" Investigation found `docs/research/inventory-restock-
boundary-2026-09-05.md` section 9 explicitly marks `manual_restock_action: UNKNOWN` -- only the
autonomous staff-restock mechanic (decision 0089) is CONFIRMED-COMMUNITY, not a player-initiated
restock button, yet task #38/decision 0107 had already shipped one as an always-available generic
product picker. Presented this honestly to the user, who then supplied new direct-play testimony
(CLAUDE.md evidence tier 1, direct-play observation): "対象の商品棚を選択し、中身が減っていると
補充のコマンドが出て、プレイヤーが任意で補充できたはず." Recorded this testimony as a 2026-09-24
addendum to the research note's section 9 (CONFIRMED_COMMUNITY structure: selecting a shelf makes
a restock command available only once its stock is low; the exact threshold/order-lot/UI wording
remain unconfirmed) and redesigned the restock UI accordingly. Removed `main.tscn`'s always-present
`RestockProductOption` dropdown and the `restock_button.disabled = true` default now gates on a new
`main.gd` `_selected_fixture_restock_target()`, which resolves `store_view.selected_fixture()`'s
product via the existing `_product_on_fixture()` helper (task #68) and returns it only when
`stock_units <= simulation._restock_trigger_stock_units_at_or_below` -- reusing decision 0089's
existing threshold rather than inventing a second one. `_on_restock_pressed()`/`_refresh_ui()` were
rewritten around this target instead of an option-list index; the REMAKE_BALANCED_DEFAULT
quantity/cost comment from task #38 is unchanged. Removed every now-dead
`_refresh_restock_product_option()`/`_restock_product_ids` reference across `main.gd` and updated
`headless_smoke.gd`'s UI-level economy scenario to drive `prototype-bread`'s stock down to the
threshold and assert the button stays gated (no charge) until then. `reference_sim` full suite grew
from 743 to 744 passed/1 xfailed (one new contract test asserting the research-note addendum, the
UI wiring, and the CONFIRMED_COMMUNITY/decision-0089 citations survive). See decision 0149.

**Task #80 (2026-09-24)**: after task #79/PR #255 merged, the user picked "操作フローの改善を継続"
(continue workflow-flow improvement) as the next direction. Continuing the same fidelity-check
approach, re-read `docs/research/strategy-guide-third-companion-book-full-extraction-2026-09-24.md`
(added in task #65, but never previously consulted for the manual-restock question) and found an
independent CONFIRMED_OFFICIAL corroboration in its PDF1 p.68-71 Q&A transcription: "player CAN
manually restock via cursor+select but this stunts staff 補充 growth." This upgrades
`manual_restock_action` from task #79's CONFIRMED_COMMUNITY (owner testimony only) to
CONFIRMED_OFFICIAL (independently corroborated by the official strategy guide), and surfaces a
nuance not in the existing corpus: manual restock does not grant the staff `補充` skill growth an
autonomous staff restock does. Checking `vertical_slice_simulation.gd` found this already true with
zero code changes needed -- `_complete_restock()` (decision 0089's autonomous staff task) calls
`_staff_growth.apply_replenish_growth()`, while `apply_explicit_restock()` (task #38's manual-restock
API) never has, a pre-existing asymmetry an existing contract test
(`test_explicit_restock_records_stock_expense_and_event_without_formula`) already locked in place
without anyone knowing why it mattered. Added a CONFIRMED_OFFICIAL-tagged comment documenting that
this match is intentional (not to be "fixed" by a future refactor), upgraded `main.gd`'s
`_selected_fixture_restock_target()` comment's evidence tag and citation, and appended a second
addendum to `docs/research/inventory-restock-boundary-2026-09-05.md` section 9 recording the new
source. Also reconfirmed (no code change) that the restock-cost formula 補充費=仕入単価×数量 the
same guide states (PDF3 p.2) already matches `restock_unit_cost_yen`'s existing use exactly. Flagged
to the user, but explicitly out of this task's scope: the same extraction document contains a large
amount of still-unmined CONFIRMED_OFFICIAL data (exact 5-method advertising cost/effect table, store
rating increase/decrease thresholds, per-product season tags, per-building customer-count tables)
well beyond this task's restock-only focus. `reference_sim` full suite grew from 744 to 745 passed/1
xfailed (one new contract test verifying the upgraded citations and the unchanged no-growth
behavior). See decision 0150.

**Task #81 (2026-09-24)**: after task #80/PR #256 merged, the user asked for a genuinely honest
completion-percentage estimate ("完成を100%とすると今何%？"), answered with a clearly-labeled
subjective estimate (~20-30% toward the stated "Android smartphone game" goal, breaking out core-loop
fidelity vs. content breadth vs. platform readiness vs. unmined source data as separate sub-estimates)
grounded in concrete facts gathered fresh (single `vertical_slice.json` scenario, no second-store/town/
rival spatial simulation in `game/`, zero audio assets, no `export_presets.cfg` at all despite the
stated Android target). The user then asked to actually install a build on their phone. This sandbox
had no Godot editor, Android SDK, or signing keystore at any point -- built the entire toolchain from
scratch in the scratchpad (not committed): the exact Godot 4.3-stable Linux editor binary CI already
uses, its export templates, an Android SDK (`platform-tools`+`build-tools;34.0.0`+`platforms;android-
34` via `sdkmanager`; no NDK/Gradle needed since this project has zero GDExtension/native code, so the
non-gradle template-based export path applies), and a debug keystore. First export attempt failed with
a genuinely unhelpful blank error ("configuration errors:" with no text) -- read godotengine/godot's
own 4.3-stable C++ source directly (`export_plugin.cpp`'s `has_valid_project_configuration()`) and
found a known-quiet failure mode: `!ResourceImporterTextureSettings::should_import_etc2_astc()` sets
`valid = false` without ever appending to the error string. This project's `project.godot` had only
desktop-facing rendering settings and had never enabled ETC2/ASTC texture import (a hard Android
export requirement), so this was a genuine, previously-undiscovered project misconfiguration, not a
tooling bug on this session's part. Fixed with one line
(`textures/vram_compression/import_etc2_astc=true`) -- pure engine/build config, same no-tag precedent
as `renderer/rendering_method.mobile`. Hand-authored `game/export_presets.cfg` (this project's first
ever) by reading the exact `get_export_options()` defaults from the matching Godot source tag, since
no GUI is available in this headless sandbox to generate one interactively; left all `keystore/*`
fields empty so it falls back to the machine-local Editor Settings debug keystore rather than
committing any signing material. The resulting export succeeded end-to-end: a 30MB debug APK,
`apksigner verify` confirming valid v1/v2/v3 signatures, `aapt dump badging` confirming the expected
package/version metadata -- sent directly to the user via `SendUserFile`. Also discovered and fixed an
unrelated latent gap while doing this: the repository had **never** had a `.gitignore` at all, so the
first-ever local texture reimport in this sandbox surfaced 666 untracked `*.png.import` sidecar files
plus a `.godot/` cache directory that would otherwise have been an easy accidental-commit trap for a
future task; added a `.gitignore` (Godot cache/import sidecars, `game/build/`, Python cache) before
touching anything else. No `reference_sim` changes (nothing here touches Python code); no new
`headless_smoke.gd` assertions (a build-tooling task, not a gameplay-logic change) -- verified instead
by the export's own end-to-end success and the signature/badging checks above. See decision 0151.
Explicitly out of scope: release-signed (non-debug) builds, a CI job that builds APKs automatically,
launcher icon art, and any real-device UX pass (touch hit-target sizing, orientation, etc.) -- the ask
was a one-time "let me see it on my phone," not a distribution pipeline.

**Task #82 (2026-09-24, decision 0152)**: after a direct complaint that the playable client did not
look like a recreation of the first title, moved the game-state readout (calendar, clock, cash) out of
the long scrolling action sidebar and into a new always-visible top HUD bar (`UI/TopBar` in
`main.tscn`), matching the layout confirmed in `docs/research/original-screen-visual-register-
2026-09-05.md` entries V001/V005 (CONFIRMED_VISUAL: original screens show a persistent top bar with
year/month-day/weather/time/cash, plus a store-name label -- "本店" for the single store this client
actually simulates). Weather stays out of scope, same precedent as task #77 (decision 0147): no weather
mechanic exists in `game/` yet, so displaying one would be an invented value, not a ported fact. This is
the first task in a while where a real Godot 4.3 binary was available in-session (fetched to scratchpad,
same method as task #81) rather than deferring visual verification to CI -- both `godot --headless
--script res://scripts/headless_smoke.gd` and an `xvfb-run` screenshot of the actual instantiated scene
were used to confirm the new layout renders without overlap before pushing. `reference_sim` (745 passed,
1 xfailed) unchanged since no Python code was touched. Explicitly out of scope: a weather HUD, converting
the sidebar's action controls into the original's modal-window style (PROJECT_MEMORY section 5), and any
floor/wall/fixture sprite art pass -- all flagged as candidate follow-ups, not done here.

**Task #83 (2026-09-24, decision 0153)**: the user's next explicit ask was fixture/floor-tile visual
fidelity. Found that `assets/raw/conveni_additional_assets_v1/` (ingested in an earlier session but never
wired into `game/`) already holds 11 CONFIRMED_VISUAL crops taken directly from an actual first-title
playthrough video (each manifest entry cites its exact source video filename/timestamp/crop coordinates):
a repeatable checkered floor tile, 8 wall edge/corner border pieces, and entrance-in/entrance-out arrow
sprites. Copied them into `game/assets/floor/` and rewired `store_view.gd`'s `_draw()` (new `_draw_floor()`/
`_draw_walls()`, rewritten `_draw_entry_exit()`) to use them in place of the flat placeholder fill/black
border/colored-rect-plus-English-text entry markers, following the asset package's own README usage notes
(edges tile only along their long axis, corners unstretched, not a finished 9-slice set). `_draw_grid()`'s
lines were kept for fixture-placement usability but weakened to near-transparent since the real floor
texture now supplies the visual tile pattern -- pure UI-chrome adjustment, no REMAKE_BALANCED_DEFAULT tag
needed (same precedent as task #76/#82). Verified with the same in-session Godot 4.3 binary as task #82:
headless_smoke.gd passes, and an xvfb screenshot confirmed the real floor/wall/entrance art renders
correctly and matches the source video frame's actual appearance. `reference_sim` (745 passed, 1 xfailed)
unchanged (no Python touched; confirmed no existing contract test asserts the specific color literals or
draw functions this task replaced). Explicitly out of scope, and flagged as the natural next step: the
in-store fixture sprites (shelves/cases/registers) are still task #67's own "remake" invented art, not
evidence-based -- but the same source video frames already sitting in the repo (`assets/raw/
conveni_additional_assets_v1/reference/video_900s.png` and `video_904s.png`) clearly show real fixture
artwork at native resolution and are ready to use for that follow-up; extracting and catalog-ID-matching
individual fixture crops from them is a larger, separate task than this one's floor/wall/entrance wiring.

**Task #84 (2026-09-25, decision 0155 -- originally numbered 0154, renumbered after colliding with PR #261's own 0154)**: user said to keep going autonomously, with a standing reminder
to always keep first-title fidelity in mind. Attempted to start on task #83's flagged fixture-sprite
follow-up first, but cropping candidate regions out of `video_900s.png` for closer inspection showed the
top-row candidates are plausibly a UI menu overlay (an advertising-selection-style red bar), not confirmed
in-world fixtures -- given the real risk of embedding a wrong CONFIRMED_VISUAL claim from a single
ambiguous frame of an NPC store, backed off that approach rather than push through it (flagged in decision
0154 for a future attempt using multiple corroborating frames instead of one). Pivoted to a zero-risk,
already-cross-confirmed data-evidence upgrade instead: `docs/research/strategy-guide-third-companion-
book-full-extraction-2026-09-24.md`'s advertising table (PDF1 p.36-37, itself cross-confirmed word-for-
word by the same book's PDF2 p.120-121 "広告データ") states the exact same cost_yen/trigger_day/
trigger_hour numbers that `baseline_data.py`'s `PROMOTIONS` already had for newspaper/airship/radio/tv
from a CONFIRMED_COMMUNITY wiki citation -- upgraded those three fields on all four entries to
CONFIRMED_OFFICIAL citing the new `STRATEGY_GUIDE_THIRD_COMPANION` constant (no numeric values changed,
since they already matched), and synced `game/data/vertical_slice.json`'s evidence_note strings.
Separately, while reading `promotion.py`'s existing `PROMOTION_DECAY_STAR_THRESHOLD` docstring, found a
CONTRADICTS finding: the third companion book describes the ad popularity boost as universally one-day-
only for every store, while promotion.py's own cited "オールテクニックガイド" describes decay as
conditional on the store being 3-star or below -- recorded in section 21.4 rather than resolved either
way, and `promotion.py`'s existing decay machinery (which deliberately never invents a numeric rate) was
left untouched. `reference_sim`'s existing promotion contract test passed unchanged (it asserts numeric
values, not evidence-tier strings). Explicitly out of scope: implementing the ad decay mechanic itself
(blocked on the contradiction above), the store-rating (★1-5) threshold table (PDF1 p.38-39, the source
document's own note flags its digit-alignment as needing a higher-resolution re-crop before trusting it),
and the fixture-sprite real-extraction task deferred from #83.

**Task #85 (2026-09-25, decision 0156)**: weather. The original HUD always shows the current weather
(`［雨 ］` etc.) and weather affects customer share, but `game/` had no weather state at all
(`demand.is_bad_weather` fixed false). Ported `reference_sim`'s CONFIRMED_OFFICIAL 12x5
`MONTHLY_WEATHER_PERCENTAGES` into a new `weather` config section (contract test asserts an exact match),
rolled with its own `_weather_rng` (so the existing seeded demand sequence is unchanged) once at start and
at every day boundary after month-end settlement, and drove `demand.is_bad_weather` from it (雨・雪/荒天,
same set as `BAD_WEATHER_VALUES`; the 0.6 multiplier is unchanged). Top bar now shows `01年目01月01日
［快晴］ 09:00`. REMAKE_BALANCED_DEFAULT, tagged in code/JSON/tests: the once-per-day roll timing (the
original can change weather mid-day; frequency unknown) and displaying 雨・雪 as 雨 / 荒天 as 荒天 (no
source says when 雪 or which storm type shows). `weather_category_index` is saved (SAVE_SCHEMA_VERSION
4->5; config schema_version 14->15). Also found PR #261's bundled `game/fonts/ConveniJP.ttf` subset lacked
快/晴/曇/荒/天 and had no build script; added `tools/build_conveni_font.py` (same Noto Sans JP 2.004
source at wght 400, keeps every previously shipped glyph plus all characters in ja.po/vertical_slice.json/
game scripts+scenes; same layout features; 250KB->258KB) and a Godot `Font.has_char` smoke check. Note
for future sessions: another workflow (PR #261) now also pushes to main -- always fetch/merge main before
starting a task. Out of scope: mid-day weather changes, per-weather/per-season multipliers (sources are
qualitative only), weather visuals, and feeding weather into `customer_share.gd` (demand already applies
it; avoided double-counting).

**Task #86 (2026-09-25, decision 0157)**: store-rating (★) monthly increase/decrease table corrected.
The user-attached strategy-guide PDFs are available in-session, so the table flagged in section 21.4
as "two near-duplicate printings that differ" was re-read at 5x render from both printings (book p.39 =
PDF1 page 17, book p.75 = PDF4 page 14). They are cell-for-cell identical; the earlier "difference" was
a transcription error, and the shipped `store_rating.py`/`store_rating.gd` thresholds were wrong in 11
cells and lacked the printed ☆☆☆☆☆ (0-star) row (code instead reused the ★1 row for 0-star stores).
Fixed both files, removed the ★1-row fallback, and added a unit test pinning every printed cell plus a
contract test that the GDScript table matches the Python table row for row. The ★5 decrease-side 清掃
cell is printed as a bare "100" (no 未満) on both pages; encoded as "below 100" from its column, noted in
code/docs. Transcription recorded in `docs/research/store-rating-table-reverification-2026-09-25.md`,
with supersession notes added to the two older research docs. Impact: early-game (0-star) stores now
use the easier printed row, and several ★3-★5 thresholds changed.

**Task #87 (2026-09-25, decision 0158)**: live store floor. After playing the Android preview the user
reported: staff never move, entrance and exit are far apart, customers enter one at a time. All three
were this client's own structural problems, not original behavior. (1) main.gd only rolled arrivals
once the store was empty, and step() never admitted anyone, so visits were strictly serialized; new
`tick()` = step() + arrival roll within the concurrency cap, and main.gd now calls only that. (2) With
concurrent shoppers, two customers meeting head-on blocked each other forever (task #66's "just wait"
limitation); added `_try_detour()`/`find_path_avoiding()` -- reroute around occupied cells when possible
(CONFIRMED_COMMUNITY "multiple routes let customers detour around congestion", section 4), still wait in a
1/2-masu corridor with no way around. (3) Exit moved from (8,0) to (1,0), directly beside the entry
(CONFIRMED_VISUAL: entrance_in/entrance_out video crops are side by side). (4) Automatic staff restock
was switched off by default only to keep an old scripted sellout test deterministic; turned it on
(confirmed original staff behavior), trigger level unchanged (REMAKE). New smoke scenario runs the
shipped config through tick() for a full day (>=2 concurrent shoppers, >=10 completed visits, staff
restock starts); older scripted scenarios now disable restock explicitly. Still open: overall customer
volume (demand coefficients REMAKE, far below the ~8 shoppers seen in a video frame), the near-empty
prototype layout (2 shelves / 2 products), staff cleaning/rest movement, and the town map.

**Task #88 (2026-09-25, decision 0159)**: staff rest in the break room. Guide p.16 (re-read from the
scan): 「お客さんがいないとき店員は休憩室で休んでいる。だからレジと休憩室の距離が近いほうが、すぐにレジに
向かうことができて便利なのだ。」 Ported break_room_1/2 (CONFIRMED_OFFICIAL price/maintenance/2x2 from
baseline_data.FIXTURES; previously excluded by task #41 for lack of a mechanic) and put break_room_1 in the
starting store (bottom-right; the guide advises near the register, to be revisited with a guide-published
layout). New `_step_staff_rest()`: while no customer is in the store, idle staff walk to the break-room door
and rest (`StaffState.rest_phase`, kept separate from `state` so existing idle checks are unchanged); once a
customer is in, they walk back to their post, and checkout does not start until the checkout staff member is
back behind the register. Resting staff are drawn inside the room (placement REMAKE_BALANCED_DEFAULT); the
room sprite is cropped from the guide's p.48 store diagram (assets/raw/conveni_guide_diagram_sprites_v1).
Not yet modeled: stamina (CONFIRMED_COMMUNITY: 0 -> back to the break room until fully recovered; no numeric
rates) and cleaning. Legacy scripted smoke scenarios strip the break room explicitly.

**Task #89 (2026-09-25, decision 0160)**: new games start in the strategy guide's p.48 store. Read the
p.48 「未開の土地に開店するなら!」 diagram on a 137 px grid (page rendered at scale 6): the floor is exactly
12x8 tiles (= CONFIRMED_OFFICIAL large_bottom), the only opening is a 2-tile walkway in the top wall, and
it holds 34 one-tile shelves, a 2x2 break room, a 2-tile register, a plant, and an ATM/copier (not placed:
no mechanic). `tools/build_guide_p48_store.py` holds the per-cell table and writes vertical_slice.json's
`guide_starting_store` block. Positions are CONFIRMED_VISUAL; product categories are PROVISIONAL readings;
shelf temperature type comes from DATA2 compatibility; starting stock = shelf capacity. The two liquor-like
shelves hold cold_drink because a new store has no alcohol permit. `GuideStartingStore.apply()` overlays
this on the prototype store and main.gd always uses it. Tests keep the prototype store through the
`use_prototype_store_for_tests` Engine meta, because main.gd can't be preloaded from `--script`. Guide
store also uses:
- empty fixed plan (random 3 wants from all 34 products),
- concurrency cap 8 (video_900s.png shows ~8 shoppers; used as cap = REMAKE),
- 200M yen starting cash (CONFIRMED_COMMUNITY).
main.gd `_fit_store_view()` scales the store to fit; the Android layout is store | shortcuts | panel.
video_900s.png also shows a staff member drawn inside the break room, so task #88's in-room drawing is
now CONFIRMED_VISUAL (the exact spot is still REMAKE). Found, not fixed: baseline_data's
medium_refrigerated_shelf is (1,1), but DATA2 p.86 prints 1x2. Still open: customer volume (demand
coefficients REMAKE; only ~2-3 shoppers at once), archetype-based wants, the outdoor lot and town map,
and shelf art cropped from p.48.

**Task #90 (2026-09-25, decision 0161)**: town map from the guide p.11 beginner-map screenshot. Cropped the
初級マップ start screen (1年目1月1日 00:00 ¥200,000,000) at scan resolution into
assets/raw/conveni_guide_town_v1. The grid was measured on it: tiles are 9.875 x 10.45 px, roads run every
10 columns and every ~13/20 rows, and the railway is row 12. tools/build_guide_town_map.py reads it tile by
tile into vertical_slice.json's `guide_town_map` (41x35 rows of G/D/R/T/B/O). Road/rail positions are
CONFIRMED_VISUAL; per-tile grass/ground/building is PROVISIONAL (colour classification); that the orange
5x5 lot is the player's store is PROVISIONAL. town_view.gd draws this town (buildings use 3 generated
house sprites = REMAKE); the old marker view is the fallback. The Android shortcuts gain 「町／店内」, and
200M starting cash is now CONFIRMED_VISUAL too. Task #72's "no sprites in the town view" test is narrowed to
"only the house sprites on building tiles". Still open: building types, town growth, and choosing a store
site.

**Task #91 (2026-09-25, decision 0162)**: 3-person roster (店長 + 店員2). The user pointed out that stores
have 3 staff. Guide p.6 (CONFIRMED_OFFICIAL) says 「各店舗に店長が必ず必要。店員は2人まで雇用できる」, and the PS
opening flow hires 店長1 + 従業員2. Task #56 had kept only 2 slots, which was wrong. Added staff-3
(role manager, `staff.manager_staff_id`). The manager is the highest-education candidate (guide: a manager
is chosen for education); the 95/95 tie was broken by lower salary (REMAKE). Wages and rating values sum the
whole roster automatically. The smoke rating test now computes security/cleaning/share from the roster
instead of literals written for 2 people. Section 21.3's "manager 3rd slot not implemented" is resolved;
the manager-education growth bonus and スーパー社員 remain open.

**Task #92 (2026-09-25, decision 0163)**: the UI is always Japanese. Every tr() string already had a ja.po
entry; English showed because the locale followed the device, and some text bypassed tr() (event names,
[PAUSED], the price suffix, raw ids like shelf-bread-1/customer-12). main.gd/main_menu.gd now set_locale("ja")
at startup; event names are translated; ids go through _fixture_label/_product_label/_customer_label/
_candidate_label. staff-3 shows as 店長. A contract test requires a translation for every tr() string and
every recorded event name.

**Task #93 (2026-09-25, decision 0164)**: the town map now uses the generated terrain and building
sprites. The user pointed out that the map was bare and ignored the ChatGPT assets; task #90 drew flat
colours and 3 house sprites. conveni_map_assets_v2 also has 121 terrain/infrastructure tiles (README_V2_JA),
and none of them were used. tools/build_guide_town_map.py now also emits:
- 'g' (trees) for grass tiles darker than the screenshot's lower quartile;
- a `buildings` list: 2x2 blocks become 2x2 office/house sprites; single tiles are picked by roof colour
  (blue -> house_small_a, red -> house_small_b, per the sprite brief; white -> shops), 20 sprite types in all.
town_view.gd:
- draws terrain tiles, choosing road straight/T/cross/end by neighbour links (rotated), with level crossings
  where roads cross the rail;
- draws the 本店 mark (video crop) on a concrete lot;
- shows only part of the town at 24px per tile, drag-to-pan, starting centred on the store.
Tile and sprite choice is REMAKE.

**Task #94 (2026-09-25, decision 0165)**: phone store at full size. The generated product overlays have been
drawn since task #68, but on the phone the 12x8 store was shrunk to 0.81 next to the shortcut column and
panel. The phone layout is now: store at scale 1.0 on the left, shortcut column at the right edge, and
the panel as an off-screen drawer. Shortcuts open the drawer, 閉じる closes it; it is moved rather than
hidden so its layout stays valid. The yellow interaction dots now appear only while a fixture is selected.

**Task #95 (2026-09-25, decision 0166)**: the player chooses the store's site. The user pointed out that the
original lets you buy land anywhere, with prices that differ by site, while this client fixed the store on
the p.11 screenshot's orange 5x5 block. That block is now read as the start screen's selection cursor
(inference) and is grass. A new game starts on the town map with 「出店場所を選んで下さい」 and time stopped:
- tap -> 2x2 cursor and 「空地 ¥21,000,000 たばこ○ 酒○ 薬○」 (building name and land/buy-out split when occupied);
- rules (CONFIRMED_OFFICIAL): 2x2 footprint (DATA4), not on road/rail/off-map, no store within 5 squares,
  cost = land (4 areas) + building value / 2;
- price shape (REMAKE, anchored to the guide's examples): 20M floor, +5M on a road, up to +5M by buildings in
  the surrounding 16x16 squares, rounded to 1M, grown by LandValuePolicy's yearly rate; DATA4 building
  prices read as 万円 (PROVISIONAL);
- the site sets demand.nearby_population (2,000 x the site's building squares / the mean site; REMAKE).
Every real new game now starts with ¥200,000,000. Save schema 6 stores the site and the cleared buildings.
Not done: store-size choice (only small is selectable at the PS start, but the p.48 large store is still
granted; ask the user), permits right after the land, town growth, a site chooser for later branches.

**Task #96 (2026-09-25, decision 0167)**: BGM and sound effects, all this project's own (REMAKE). The original
has BGM (the V03 video title) and effects (a clear effect; a horn when parking runs short), but no recording or
score was recovered and its music may not be copied. game/scripts/audio/sound_synth.gd synthesizes everything
at run time (no audio file ships; the APK is at the 30MiB delivery limit): a 132bpm store tune, a 100bpm town
tune (title and site choice), rendered on a worker thread, and effects mapped from events by
vertical_slice.json "sound".event_sfx (door chime on entry, register beep on checkout, purchase, place, anger,
month end, clear fanfare, game over, refusal, button blip). SoundManager autoload; a 音 on/off button in the
panel, saved in user://settings.cfg.

**APK delivery fix (2026-09-25, after task #96)**: the first 0.1.6 APK sent to the user was a stale file.
The headless export printed `Parameter "fd" is null` errors and left the previous build (0.1.5, versionCode 6)
in game/build/android/. The user installed it and still saw the old fixed 5x5 lot. Rule from now on:
- delete the old APK;
- run `godot --headless --path game --import` before `--export-debug`;
- before sending, check the APK: versionCode (aapt2 dump badging) and the new scripts/data inside it.
The correct build was 30.01 MiB, over the 30 MiB delivery limit. Explicit small launcher icons
(game/assets/app_icon/, nearest-neighbour upscales of the register menu icon; platform presentation only)
replace Godot's auto-scaled ~150 KB ones. That brings the APK to 29.50 MiB.

The next large milestone is **turning the single scripted vertical slice into reusable gameplay**:

- connect actor rosters and explicit product plans to evidence-backed observation replay;
- keep provisional client tuning isolated from recovered first-title facts;
- port evidence-backed contracts from the reference simulator only as production features need them;
- recover and replace provisional fixture-edit gating, rotation, cost, and persistence behavior;
- preserve deterministic engine-native smoke coverage while expanding the playable loop;
- continue replacing unknown/provisional rules with observation or reverse-engineering evidence.

- **2026-09-24 Android Japanese preview (decision 0154):** Japanese UI/font, larger Android controls, shortcuts/quick save and separate preview package. Android-only starting cash uses the researched 200-million-yen beginner anchor with a free furnished test shop (REMAKE_BALANCED_DEFAULT). Real scene-flow test verifies purchase/save/load/Continue. Still a vertical slice; no claim of complete recreation. See `docs/handoff/2026-09-24-android-preview-delivery.md`.

## 20. Execution cadence and user-directed work

Scheduled runs are a background cadence, not an exclusive gate for progress.

1. Recurring tasks continue the configured research, video analysis and implementation work.
2. When the user directly asks to continue or implement in an active conversation, begin that
   work immediately; do not wait for the next scheduled run.
3. Start from the latest `main`, avoid overlapping an in-progress branch, run the relevant full
   regression suite, then use a focused branch, PR review and squash merge.
4. Record new evidence under `docs/research/`, deliberate compatibility choices under
   `docs/decisions/`, and durable cross-session status in this file or `docs/handoff/`.

Codexのチャット・PR・マージ運用の詳細は
`docs/handoff/codex-chat-pr-workflow.md` を参照する。一往復ごとには区切らず、一つの目的を
同じチャットで完成させ、マージ前チェック後にPR化する。PRマージ後の独立作業は、古い
作業ブランチへ積まず、最新 `main` から新しいチャットを開始する。

2026-09-18セッションの詳細な引き継ぎ(このセッションで決まった運用ルール、YouTube動画
視聴不可という環境制約、UI表示ギャップ、先送りされた3項目、未検証の動画候補URL等)は
`docs/handoff/2026-09-18-claude-code-session-handoff.md` を参照する。

タスク#39〜#49(2026-09-19、`CLAUDE.md`新設の経緯、標準指令3件の原文、確立された
運用ルール・禁止事項、決定事項の採択背景、残っているタスクの分類、画像・音声を除いた
システム面の完成度評価を含む)の詳細な引き継ぎは
`docs/handoff/2026-09-19-claude-code-session-handoff-3.md` を参照する。

タスク#50(2026-09-19、2冊分のPDF一次資料の全ページ書き起こし、什器維持費・
スタッフ給与の営業時間比例配線、第21節の研究成果カタログ)の詳細な引き継ぎは
`docs/handoff/2026-09-19-claude-code-session-handoff-4.md` を参照する。

タスク#51〜#54(2026-09-19、チェックアウト怒りペナルティのスコープ是正、
「つまみだす」アクション、価格設定メカニクス、治安施設公式の再検証と
データ是正2件)の詳細な引き継ぎは
`docs/handoff/2026-09-19-claude-code-session-handoff-5.md` を参照する。

タスク#56〜#58(2026-09-20、店員雇用アクション、店舗データの建物面積
内訳の移植、町の空間モデル〈店舗間距離〉への着手)の詳細な引き継ぎは
`docs/handoff/2026-09-20-claude-code-session-handoff-6.md` を参照する。

タスク#59〜#61(2026-09-20、Godot版への排他距離ルール配線、土地購入費
公式、治安施設の空間探索)、および証拠規律の解釈に関するユーザーからの
重要な是正(「証拠が完全には揃わなくても類推〈CLAUDE.md優先順位2/3〉で
積極的に埋めていく」という標準方針の再確認)の詳細な引き継ぎは
`docs/handoff/2026-09-20-claude-code-session-handoff-7.md` を参照する。
CLAUDE.mdの規約により、`docs/handoff/`配下で最新の本ファイル(`-7.md`)が
矛盾する旧記載に優先する。

## 21. 2026-09-19 PDF一次資料(2冊)の研究成果カタログ(タスク#50以降)

This section catalogues findings from the 4-PDF research pass that started task #50 (section 19),
so a future session does not have to re-read the 4 research docs from scratch to know what is
still actionable. **The classification below (NEW/CONFIRMS/CONTRADICTS, "actionable" framing) is
Claude's own triage, not confirmed fact** -- the underlying page citations in the linked docs are
the primary evidence; this section is a navigational summary of them.

### 21.1 New primary sources

Two previously-unseen strategy guide books were scanned by the user and transcribed in full by 4
parallel research agents (all pages read, no sampling):

- 「ザ・コンビニ 新人店長実習マニュアル」(~143 pages) -- turned out to be the **same physical
  book** already cited in `baseline_data.py` as `本1.pdf`/`本2.pdf`. Re-transcription functioned
  mostly as independent re-verification (it even reproduced an existing known misprint in the
  customer-visit-schedule table). See `docs/research/strategy-guide-shopkeeper-manual-part1-
  2026-09-19.md` (chapters 1-2, pp.6-71) and `-part2-2026-09-19.md` (chapters 2-4 remainder,
  pp.72-143).
- 「クイックリファレンス」(~95 pages, a physically-separate book from the "full-decode"/"fixture-
  crosscheck" 2026-09-16 source, though its DATA 4 建物 table turned out to already be ported as
  `TOWN_BUILDINGS`) -- see `docs/research/quick-reference-guide-part1-2026-09-19.md` (時間/店舗/
  スタッフ/顧客/町 dense-data front section, pp.2-12, plus a second physically-bound-together
  book of themed store-layout examples, pp.16-47) and `-part2-2026-09-19.md` (店舗レイアウト実例
  continuation + オールテクニックガイド + DATA 1-4, pp.48-95).

### 21.2 Resolved this session

- **Task #50** (fixture maintenance / staff wages scale with configured business hours instead of
  charging a flat 24h-basis figure) -- see section 19 and decision 0119.
- **Task #51** (checkout-anger penalty is store-wide, not scoped to the serving staff member) --
  see section 19 and decision 0120. Re-verified directly against the PDF scan, not just the
  research doc's summary.
- **Task #52** ("eject a customer" (つまみ出す) action, avoiding the anger penalty at the cost of
  their purchase) -- see section 19 and decision 0121, including UI wiring.
- **Task #53** (price-setting/margin mechanic, consumed by both live purchases and the monthly
  rating's `price_change_pct`) -- see section 19 and decision 0122, including UI wiring.
- **Task #55** (incidental-want products for demand-driven customers, lifting decision 0004's
  boundary with the user's explicit go-ahead) -- see section 19 and decision 0124.
- **Section 4 above** (bench/fountain service_bonus and bench maintenance) was stale, still
  showing pre-2026-09-17-correction wiki values instead of the guide-sourced values already live
  in `baseline_data.py`; corrected in place (no code change, this file only).
- **Section 11 above** (promotion popularity-gain table) was likewise stale, still showing
  wiki-derived airship/radio/tv figures (+30/+50/+100) after `baseline_data.py` had already been
  corrected to the guide-sourced +40/+60/+90; corrected in place (task #51, no code change).
- **Bench maintenance 168-vs-160** (section 21.4's item) -- directly re-read book p.118: confirms
  160, matching existing code exactly. The 168 figure was a weaker, indirect (hourly-rate x24)
  reading from the other book; no code change was needed or made.

### 21.3 NEW findings not yet implemented (candidates for future tasks)

Grouped by rough topic, each citing which research doc has the page-level evidence. None of these
have been implemented yet; picking one is a future-session decision, not a standing priority
order.

- **Security facilities (交番/消防署) -- RESOLVED NOT a conflict (re-verified 2026-09-19)**: both
  books were directly re-read (実習マニュアル book pp.46-47; クイックリファレンス book p.10). The
  実習マニュアル states a flat "police box +40 / fire station +30" security bonus within a 7-area
  radius, reduced proportionally if the facility's footprint spills outside that radius. The
  クイックリファレンス states a per-area-unit formula: police box (2x2 footprint) +10 security per
  area-cell within a 16x16-tile radius, max +40; fire station (2x3 footprint) +5/area-cell, max
  +30. These are the SAME formula at two levels of detail, not a disagreement: 2x2=4 cells x 10 =
  40 exactly matches the police box's stated max; 2x3=6 cells x 5 = 30 exactly matches the fire
  station's max. The "flat +40/+30, reduced if the footprint spills outside the range" framing is
  just the fully-contained case of "per-cell-within-range x rate." Confirmed formula: `bonus =
  (footprint_cells_within_the_effective_radius) x per_cell_rate` (police 10/cell, fire 5/cell).
  What remains genuinely blocked is unrelated to this formula: this client's `TownState` (game/) is
  a single scalar population/store_count with no facility-placement or spatial-distance model at
  all (decision 0095), so there is nowhere yet to place an induced police box/fire station or
  compute its distance from the store. Task #61 (decision 0130) implemented the footprint-rectangle-
  vs-radius spatial search itself (`remake_town_spatial.facility_area_tiles_within_range()`), so the
  formula end-to-end is no longer unimplemented in `reference_sim` -- what remains open is purely
  `game/`-side: this client still has no facility-placement mechanic (`TownState` stays non-spatial)
  to actually call it from.
- **Land-purchase cost formula**: empty lot = area land price x number of areas; occupied lot =
  land price + 50% of the existing building's appraised value (実習マニュアル p.7) -- formula
  shape and the 50% rate are both CONFIRMED_OFFICIAL. Implemented in task #60 (decision 0129) as
  `RemakeBalancedLandValuePolicy.land_purchase_cost_yen()`, reusing `current_land_price_yen()`
  reinterpreted as a per-area rate (analogy-based, decision 0095's existing uniform-price
  simplification applied per-area) and sourcing `area_count` from a store variant's CONFIRMED_
  OFFICIAL `total_area_tiles` (task #57) on the inference that "エリア" and "tile" are the same
  unit. `reference_sim`-only: this client still has no land-acquisition/multi-store-placement
  mechanic to attach it to (`try_expand_chain()` is a purely abstract number), so it is not wired
  into `game/` yet -- that boundary (decision 0095/0026) is unchanged, but the formula itself is no
  longer unimplemented.
- **Rival-store mechanics with numbers**: rival withdrawal after continuous deficit takes ~6
  months if left alone (実習マニュアル, stated in 2 scenarios); holding a permit may block nearby
  *rivals* from selling that category too, not just gate the player (実習マニュアル) -- task #58
  (decision 0127) confirmed and ported the exact distance diagram (5/7/11/15 tiles) this mutual-
  exclusion behavior runs on, as `remake_town_spatial.can_acquire_permit_at()`; task #59 (decision
  0128) then wired the Godot-side half of it -- `game/scripts/domain/town_spatial.gd` plus a
  `VerticalSliceSimulation._rival_stores` roster (config-supplied position + held-permits, defaults
  to empty/no-op) -- so `try_purchase_permit()` now actually rejects a purchase blocked by a
  configured rival. What remains open: no source states how many rivals exist, where they sit, or
  which permits they actually hold in a real playthrough, so `_rival_stores`/`remake_town_spatial`'s
  own equivalent stay entirely caller-supplied (test/scenario data only) rather than something this
  client generates on its own; `rival.py`'s `RivalChainRuntime` (reference_sim) still tracks rivals
  by an abstract `location_id: str`, not a spatial position, so it is not the same entity as
  `_rival_stores` above -- the two have not been unified. A 20%-off campaign near a rival branch can
  force its withdrawal (クイックリファレンス); a ¥500,000 rival-store investigation fee exists
  separate from acquisition cost. `remake_rival_policy.py`'s decision policy is wired to a real
  geometric input for the first time (task #58's `trade_area_overlap_ratio()` integration test), but
  still has no production (`game/`) caller -- no rival-AI decision loop exists in Godot to call it
  from, and `trade_area_overlap_ratio()` itself was deliberately not ported into `town_spatial.gd`
  for the same "no caller yet" reason. Task #62 (decision 0131) closed part of "where they sit"'s
  companion question -- how many rivals exist and with what roles at scenario start -- using a
  previously-unimplemented research doc (`scenario-initial-rival-topology-2026-09-06.md`):
  intermediate starts with 1 HQ + 2 branches, advanced with just an HQ that grows branches over
  time, beginner's exact count stays UNKNOWN. `scenario_initial_rival_topology.
  seed_rival_chain_for_scenario()` seeds a `RivalChainRuntime` from this (reference_sim-only); it
  is not yet unified with `_rival_stores` (game/) or with `RemakeBalancedRivalPolicy`'s own
  decisions, so the "which permits they actually hold" and "where they sit" halves of this gap
  remain exactly as open as before. Task #62 also added a `TownState.has_capacity_for_new_store()`
  hard cap (CONFIRMED_COMMUNITY, two independent sources: player+rival combined <= 10 stores per
  map) -- a map-wide construction limit, not the same fact as the intermediate scenario's own "10
  player stores" clear condition.
- **Staff mechanics**: basic hiring (replacing a fixed roster slot's occupant with a different
  candidate from the 35-person pool) implemented in task #56 (decision 0125) -- see section 19's
  task #56 entry. Still NOT implemented, each for the reason noted: PS版固定 3% wage-negotiation
  base-up (no wage-negotiation mechanic exists to attach a base-up rate to); explicit 3-staff-per-
  store cap / 店長 (manager) 3rd slot (this client's roster is a fixed 2 slots, task #56 scoped
  down deliberately, no formula existed to expand it from); a pre-hire stat interpretation band
  (40-69=普通/70-100=高い, cosmetic UI labeling only, not a mechanic with numeric effect); fired
  staff return to the hiring pool after ~1 year with decayed-but-above-rookie stats (qualitative,
  no formula given, and this client has no "fire" action separate from "replace" to begin with);
  80+-year staff can become a "スーパー社員" (all stats 100) at unspecified probability (no trigger
  condition or probability stated anywhere).
- **Building/facility per-time-slot visitor counts**: DATA 4 建物's 朝/昼/夕/夜/深夜/早朝 numeric
  columns (transcribed with an explicit confidence caveat -- see `quick-reference-guide-part2-
  2026-09-19.md` for the row-alignment uncertainty note before using these numbers) plus a
  time-band hour-range definition table (朝=7-11h, 昼=12-15h, 夕=16-19h, 夜=20-23h, 深夜=24-3h,
  早朝=4-6h) not recorded anywhere in the codebase.
- **Facility/scenario data**: ~~都庁 auto-build trigger text (population >20,000, upgrades an
  existing PROVISIONAL wiki note toward CONFIRMED_OFFICIAL)~~ -- done in task #64 (decision 0133):
  `store_events.METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD`/`metropolitan_government_is_induced()`,
  `reference_sim`-only (no `game/` scenario-selection mechanic to attach it to yet); station-spacing rule (2 stations per
  line if lines are >=40 areas apart); a 4-tier (not section 14's provisional 3-tier)
  初級/中級/上級/極上 scenario structure with concrete starting-data blocks (cash/population/
  rival stats/security-facility counts) per map, plus numeric advanced-scenario clear-condition
  targets (10 stores, ~200,000 cumulative visitors, ~¥30,000,000 annual revenue, 30,000 town
  population, all stores 5-star); an attraction-facility footprint/shopping-population table (10
  facility types) closing part of section 17's "facility list and population/demand effects" gap;
  ~~a full building-area breakdown (総面積/建物全体/床面積/店外スペース) for all 6 store variants
  (only `editable_floor`+price were previously ported)~~ -- ported in task #57 (decision 0126) as
  reference-only `StoreVariant` fields in `reference_sim`; large-store upgrade is population-gated,
  not purely a cash transaction; hidden 4th map's shape differs PS vs. Saturn (upgrades its
  existence to CONFIRMED_OFFICIAL from wiki-only CONFIRMED_COMMUNITY); contest prize eligibility
  is specifically gated on cleanliness value.

### 21.4 CONTRADICTS findings flagged for re-verification (deliberately NOT resolved)

Per CLAUDE.md's discipline, these are recorded rather than silently picked one way or the other:

- **Weather table column labels -- RESOLVED 2026-09-24 (task #63)**: a 400dpi targeted rescan of
  クイックリファレンス book page 3 settles this decisively: the columns are 快晴/晴れ/曇り/雨・雪/
  荒天 (荒天 glossed by the guide's own parenthetical as "大雨・雷雨・台風・大雪"), matching
  neither of this session's two prior competing readings (快晴/曇り/雨/台風/荒天, or the older code
  comment's 快晴/大雨/雪/台風/荒天). All 12 monthly rows sum exactly to 100 under this reading
  (the prior reading had 3 rows that did not) -- see decision 0132, `baseline_data.MONTHLY_WEATHER_
  PERCENTAGES`, and the corrected `remake_customer_share.BAD_WEATHER_VALUES`.
- **Business hours option ③ -- RESOLVED 2026-09-24 (task #63)**: the same 400dpi rescan directly
  confirms the source itself prints "AM11:00~AM2:00 (16時間営業)" -- not a scan/OCR misread of
  "AM3:00" as previously guessed. This is an internal inconsistency in the original guide (15h
  actual span, 16h printed label), transcribed verbatim rather than silently corrected -- see
  decision 0132, `baseline_data.BUSINESS_HOURS_PRESETS`.
- **A "parameter growth per work action" matrix and a customer-anger-penalty matrix** on
  クイックリファレンス p.7, potentially bearing on `staff_growth.gd`'s (task #48) +1/skill-pair
  guesses and the checkout-anger magnitude above -- read confidence on the exact column mapping
  was only moderate; flagged, not asserted or acted on.
- **Store-rating table / large-store footprint**: pre-existing known conflicts (already resolved
  in code before this session) were independently rediscovered by this pass, not newly
  introduced -- see `strategy-guide-shopkeeper-manual-part1-2026-09-19.md` and `-part2-
  2026-09-19.md` for the record. A third data point (large-store footprint stated as "16x16" in 4
  unanimous case-study captions, vs. the already-known "14x14"/"18M-vs-24M" conflicts) surfaced in
  `-part2`; still unresolved. **Store-rating half RESOLVED 2026-09-25 (task #86)**: a 5x re-read of
  both printed copies (book p.39 and p.75) found them cell-for-cell identical -- the "conflict" was a
  transcription error, and the shipped thresholds themselves were wrong in 11 cells and missing the
  printed 0-star row. Fixed in code; see `docs/research/store-rating-table-reverification-2026-09-25.md`
  and decision 0157. The large-store footprint half is still unresolved.
- **Station shopping-population figure**: 2,000 on one page vs. 2,240 on another page of the same
  book -- possibly different size tiers rather than a real conflict; not resolved.
- **Promotion popularity-boost decay condition (found in task #84, decision 0155)**: two different
  strategy guides describe the ad-popularity-boost decay differently. The third companion book
  (`strategy-guide-third-companion-book-full-extraction-2026-09-24.md` PDF1 p.36-37) states the
  effect is universal and one-day-only for every store regardless of rating: "広告の効果が持続する
  のは、広告を出したその日だけ。翌日になると上がった人気度がドンドン下がってしまう." The
  "オールテクニックガイド" already cited in `reference_sim/conveni_sim/promotion.py`'s
  `PROMOTION_DECAY_STAR_THRESHOLD` states decay only applies to stores at 3-star or below:
  "ランク評価が3つ星以下の店舗は、1日毎に宣伝の効果が薄れていく." `promotion.py`'s existing
  `PopularityDecayOpportunity` machinery already deliberately records decay events without
  inventing a numeric rate (per its own docstring) -- this newer conflict is a second, more basic
  disagreement about the *condition* under which decay applies at all (universal vs. rating-gated),
  not just its magnitude. Flagged per CLAUDE.md's discipline rather than silently picking one guide
  over the other; not resolved or acted on in task #84.

### 21.5 Deliberately not re-litigated

The customer-archetype visit-schedule table (21 archetypes, 143 rows) and the DATA 4 建物 table
were both independently re-transcribed in full and matched the already-ported
`CUSTOMER_ARCHETYPES`/`CUSTOMER_VISIT_SCHEDULE`/`TOWN_BUILDINGS` field-for-field (including
reproducing an existing known misprint) -- no changes needed, not re-listed as findings above.
