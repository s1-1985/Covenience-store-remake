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
