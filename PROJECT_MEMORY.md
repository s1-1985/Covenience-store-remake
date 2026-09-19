# Convenience Store Remake — Project Memory

Last updated: 2026-09-18 (JST)

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

The next large milestone is **turning the single scripted vertical slice into reusable gameplay**:

- connect actor rosters and explicit product plans to evidence-backed observation replay;
- keep provisional client tuning isolated from recovered first-title facts;
- port evidence-backed contracts from the reference simulator only as production features need them;
- recover and replace provisional fixture-edit gating, rotation, cost, and persistence behavior;
- preserve deterministic engine-native smoke coverage while expanding the playable loop;
- continue replacing unknown/provisional rules with observation or reverse-engineering evidence.

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
`docs/handoff/2026-09-19-claude-code-session-handoff-4.md` を参照する。CLAUDE.mdの
規約により、`docs/handoff/`配下で最新の本ファイル(`-4.md`)が矛盾する旧記載に優先する。

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

- **Security facilities (交番/消防署)**: both books independently give **quantified** bonuses for
  the first time (previously only qualitative in section 12) -- but the two books disagree on the
  exact shape (flat +40/+30 within a 7-area radius per the 実習マニュアル vs. a per-area-scaled
  +10/area max+40 (police, 2x2) / +5/area max+30 (fire station, 2x3) within a 16x16-tile radius
  per the クイックリファレンス). This needs a side-by-side re-read before implementing, not a
  pick-one guess. No such fixtures exist in `fixture_catalog` yet (blocked since decision 0096).
- **Land-purchase cost formula**: empty lot = area land price x number of areas; occupied lot =
  land price + 50% of the existing building's appraised value (実習マニュアル p.7). Not modeled
  anywhere (`land_value_policy.gd` only models value *growth over time*, not acquisition cost) --
  but this client also has no land-acquisition/multi-store-placement mechanic to attach it to yet
  (same boundary as decision 0095/0026).
- **Incidental-purchase item count**: each customer has ~3 "ついでに欲しい品" beyond their
  destination purchase (クイックリファレンス p.9, CONFIRMED_OFFICIAL with an exact count) --
  upgrades section 7's standing HYPOTHESIS to confirmed, and is exactly the evidence task #43
  said was missing before decision 0004's "no incidental purchase" boundary could be reconsidered.
  Still unimplemented; lifting decision 0004's boundary is a real scope decision, not a
  drop-in fix.
- **Rival-store mechanics with numbers**: rival withdrawal after continuous deficit takes ~6
  months if left alone (実習マニュアル, stated in 2 scenarios); holding a permit may block nearby
  *rivals* from selling that category too, not just gate the player (実習マニュアル); a 20%-off
  campaign near a rival branch can force its withdrawal (クイックリファレンス); a ¥500,000
  rival-store investigation fee exists separate from acquisition cost. None modeled in
  `remake_rival_policy.py`/Godot (no rival-store entity exists at all yet, per decision 0095).
- **Staff mechanics**: PS版固定 3% wage-negotiation base-up; explicit 3-staff-per-store cap; a
  pre-hire stat interpretation band (40-69=普通/70-100=高い); fired staff return to the hiring
  pool after ~1 year with decayed-but-above-rookie stats (qualitative, no formula given); 80+-year
  staff can become a "スーパー社員" (all stats 100) at unspecified probability. None implemented
  (no hiring/firing UI exists yet at all, per section 17's "スタッフ雇用・解雇UI" gap).
- **Building/facility per-time-slot visitor counts**: DATA 4 建物's 朝/昼/夕/夜/深夜/早朝 numeric
  columns (transcribed with an explicit confidence caveat -- see `quick-reference-guide-part2-
  2026-09-19.md` for the row-alignment uncertainty note before using these numbers) plus a
  time-band hour-range definition table (朝=7-11h, 昼=12-15h, 夕=16-19h, 夜=20-23h, 深夜=24-3h,
  早朝=4-6h) not recorded anywhere in the codebase.
- **Facility/scenario data**: 都庁 auto-build trigger text (population >20,000, upgrades an
  existing PROVISIONAL wiki note toward CONFIRMED_OFFICIAL); station-spacing rule (2 stations per
  line if lines are >=40 areas apart); a 4-tier (not section 14's provisional 3-tier)
  初級/中級/上級/極上 scenario structure with concrete starting-data blocks (cash/population/
  rival stats/security-facility counts) per map, plus numeric advanced-scenario clear-condition
  targets (10 stores, ~200,000 cumulative visitors, ~¥30,000,000 annual revenue, 30,000 town
  population, all stores 5-star); an attraction-facility footprint/shopping-population table (10
  facility types) closing part of section 17's "facility list and population/demand effects" gap;
  a full building-area breakdown (総面積/建物全体/床面積/店外スペース) for all 6 store variants
  (only `editable_floor`+price were previously ported); large-store upgrade is population-gated,
  not purely a cash transaction; hidden 4th map's shape differs PS vs. Saturn (upgrades its
  existence to CONFIRMED_OFFICIAL from wiki-only CONFIRMED_COMMUNITY); contest prize eligibility
  is specifically gated on cleanliness value.
- **Price-margin/discount UI shape**: a global "all items X% off list price" slider plus a
  per-item override, baseline 40% margin -- confirms the shape of the still-unimplemented
  price-setting mechanic `store_rating.gd`'s `price_change_pct` field has always awaited (always
  hardcoded to 0 today, no UI exists).

### 21.4 CONTRADICTS findings flagged for re-verification (deliberately NOT resolved)

Per CLAUDE.md's discipline, these are recorded rather than silently picked one way or the other:

- **Weather table column labels**: this session's independent read of クイックリファレンス p.2-3
  gives 快晴/曇り/雨/台風/荒天, but `remake_customer_share.py`'s `BAD_WEATHER_VALUES` comment
  already claims (citing the same book) 快晴/大雨/雪/台風/荒天. Needs a higher-resolution rescan
  before either is trusted; not changed.
- **Business hours option ③**: transcribed as "AM11:00-AM2:00" labeled "16時間営業" (only 15h,
  inconsistent with its own label) -- very likely a scan/OCR misread of "AM3:00", but not
  corrected without a clearer rescan.
- **A "parameter growth per work action" matrix and a customer-anger-penalty matrix** on
  クイックリファレンス p.7, potentially bearing on `staff_growth.gd`'s (task #48) +1/skill-pair
  guesses and the checkout-anger magnitude above -- read confidence on the exact column mapping
  was only moderate; flagged, not asserted or acted on.
- **Store-rating table / large-store footprint**: pre-existing known conflicts (already resolved
  in code before this session) were independently rediscovered by this pass, not newly
  introduced -- see `strategy-guide-shopkeeper-manual-part1-2026-09-19.md` and `-part2-
  2026-09-19.md` for the record. A third data point (large-store footprint stated as "16x16" in 4
  unanimous case-study captions, vs. the already-known "14x14"/"18M-vs-24M" conflicts) surfaced in
  `-part2`; still unresolved.
- **Station shopping-population figure**: 2,000 on one page vs. 2,240 on another page of the same
  book -- possibly different size tiers rather than a real conflict; not resolved.
- **小宮千明's security_skill_growth_ceiling**: read as 44 in this session's scan vs. 42 in
  existing code -- low-confidence, could be a misread on either side, not asserted as a real
  contradiction.

### 21.5 Deliberately not re-litigated

The customer-archetype visit-schedule table (21 archetypes, 143 rows) and the DATA 4 建物 table
were both independently re-transcribed in full and matched the already-ported
`CUSTOMER_ARCHETYPES`/`CUSTOMER_VISIT_SCHEDULE`/`TOWN_BUILDINGS` field-for-field (including
reproducing an existing known misprint) -- no changes needed, not re-listed as findings above.
