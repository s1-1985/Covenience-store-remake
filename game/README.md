# Convenience Store Remake — Godot production client

This directory is the first production-client seed for the Android-targeted remake.

The Python code under `reference_sim/` remains the compatibility/reference simulator used to recover, test, and compare first-title behavior. The Godot client is the actual player-facing game implementation and should consume recovered rules only after they are evidence-safe enough to promote out of provisional prototype data.

## Current vertical slice

The initial scene deliberately uses generated primitives and text only. It does not reuse original game sprites, logos, music, text dumps, or other copyrighted assets.

The current playable loop is:

1. one customer enters the store;
2. the customer follows an explicit provisional visit plan across product-shelf interaction points;
3. one unit of each available planned product is added to a basket;
4. after the plan, a customer with a nonempty basket pathfinds to the checkout;
5. the staff member performs a timed prototype checkout;
6. sale cash is added;
7. the customer pathfinds to the exit;
8. the HUD shows game time, cash, aggregate stock, current basket, customer state, staff state,
   completed sales/visits, and the last event;
9. once the store is empty, the next customer now arrives on their own via a demand-driven
   probability roll (see "Customer arrival" below) each simulated minute; the player can still
   force the next admission manually as an override while preserving stock and cash.

### Customer arrival

`scripts/domain/demand_policy.gd` is a REMAKE_BALANCED_DEFAULT port of
`reference_sim/conveni_sim/remake_demand_policy.py`'s guessed customer-arrival rate
(population × store share % × a per-population daily visit rate, spread across opening minutes,
reduced under bad weather). The strategy guide confirms an arrival formula exists
(`strategy-guide-full-decode-2026-09-16.md` section 41, "客数発生式") but never publishes it, so
this rate is a tagged placeholder to retune after playtesting, not a recovered original formula.
`data/vertical_slice.json`'s `demand` block supplies `nearby_population`/`customer_share_percent`
directly because no town/trade-area spatial simulation exists yet in this client; only the
per-minute Bernoulli roll and the single-active-customer admission boundary are enforced here.
This client still deliberately keeps only one active customer at a time -- the demand policy only
automates *when* the next admission happens, not concurrent arrivals, which remain unrecovered.

### Staff task assignment

The second, non-checkout staff member was previously permanent furniture: it never moved or acted.
`scripts/domain/staff_state.gd` now gives any non-checkout staff member a `to_restock` /
`restocking` task cycle, and `vertical_slice_simulation.gd`'s `_assign_idle_restock_tasks()`
dispatches the first idle non-checkout staff member to the first sold-out product (a simple greedy
match, not a skill- or priority-based dispatcher). On completion it restocks the product back to
its own configured `initial_stock_units` and deducts `quantity x restock_unit_cost_yen` from cash,
reusing the same expense/event-log plumbing as the existing manual `apply_explicit_restock`
boundary. Layout edits are now also blocked while any restock task is active, in addition to the
existing active-visit lock.

This is a PROVISIONAL prototype task-assignment rule, not a recovered original staff-AI policy --
the strategy guide only confirms that register-assignment AI behavior exists and is imperfect
(PROJECT_MEMORY.md section 19 / `ps-gameplay-economy-evidence-2026-09-05.md` section 10), without
publishing its trigger, priority, or dispatch logic. It is **disabled by default**
(`data/vertical_slice.json`'s `simulation.restock_task_enabled: false`) because this vertical
slice's existing sellout scenario deliberately demonstrates a shelf staying empty after the last
unit sells -- see decision 0089 for why enabling it by default would silently invalidate that
scenario, and for the dedicated test configuration that exercises this feature instead.

### Representative-day / month cycle

`minute_of_day` used to just wrap silently at midnight forever, with no concept of a "day" or
"month" at all. `vertical_slice_simulation.gd` now counts each midnight crossing as a day
(`day_count`) and, every `REPRESENTATIVE_DAYS_PER_MONTH` (4) days, settles a month: it takes the
net change in cash across those 4 days and multiplies it by `MONTH_MULTIPLIER` (8), applying the
difference as a lump-sum `month_end_settlement`. Unlike the demand/restock features above, **this
multiplier is `CONFIRMED_OFFICIAL`, not a guess** -- the strategy guide states it directly
("1月=4日間×8"), and `reference_sim/conveni_sim/month_aggregation.py` already carries the same
citation. What neither the guide nor this client invents is *how* each representative day's own
result is computed internally; both simply turn an already-tracked 4-day cash change into the
displayed monthly figure. See decision 0090.

### Bankruptcy and time-limit game over

Every month-end settlement now also evaluates whether the scenario has ended terminally, using two
**CONFIRMED**, not guessed, rules:

- **Bankruptcy**: PS footage and an SS play record support game over when cash is negative at a
  day/month boundary (`reference_sim/conveni_sim/month_boundary.py`'s
  `MonthBoundaryBankruptcyPolicy.bankrupt_when_negative`). No zero-cash sample is known, so cash
  exactly equal to zero is explicitly left unresolved -- this client leaves it unresolved too and
  does **not** treat it as bankruptcy.
- **Time limit**: the guide's second game-over path, 100 years without meeting the scenario's own
  clear condition (`reference_sim/conveni_sim/store_events.scenario_time_limit_exceeded`). This
  client has no scenario/clear-condition system yet, so `clear_condition_met` defaults to `false`
  (never met) until a future scenario layer sets it.

Once either condition fires, `is_game_over` becomes `true` and every mutating method
(`step()`, `tick_idle_for_demand()`, `start_next_customer()`, `apply_explicit_restock()`, layout
edits, ...) becomes a no-op; nothing invents what should visually happen next (no ending screen,
no restart flow) beyond that frozen, inspectable state. See decision 0091.

### Fixture purchase

`VerticalSliceSimulation.try_purchase_fixture(catalog_id, instance_id, origin_subcell,
interaction_subcell)` adds a brand-new fixture from `data/vertical_slice.json`'s
`fixture_catalog` -- currently potted plant / bench / fountain, with purchase prices ported
directly from `reference_sim/conveni_sim/baseline_data.py`'s `FIXTURES` (**CONFIRMED_OFFICIAL**,
not a guess). It reuses `try_relocate_fixture`'s safety checks (atomic rollback if the new
fixture would block a required route or trap a staff member) and its expense/event-log plumbing.
Each catalog entry also carries `maintenance_yen_per_day`/`service_bonus`, but **neither is
consumed anywhere yet** -- daily maintenance deduction and store-evaluation service value remain
future work (the latter is task #27's job). See decision 0092. This is the first of task #25's
four planned systems (什器購入・商品仕入れ・許可・広告).

### Permits and product procurement

`VerticalSliceSimulation.try_purchase_permit(permit_id)` pays a one-time fee (tobacco
¥7,000,000 / alcohol ¥3,000,000 / medicine ¥10,000,000, **CONFIRMED_OFFICIAL** from
`reference_sim/conveni_sim/baseline_data.py`'s `PERMITS`) and `has_permit(permit_id)` reports it
afterward. `try_procure_product(catalog_id, instance_id, fixture_id)` adds a new product SKU
from `data/vertical_slice.json`'s `product_catalog` to an existing, unoccupied fixture --
currently just `tobacco` (sale price ¥250 / procurement cost ¥175, also CONFIRMED_OFFICIAL, ported
from the guide's たばこ category pricing). Both a permit-gated fixture
(`small_tobacco_vending`, added to `fixture_catalog`) and the `tobacco` product itself refuse to
purchase/procure without the `tobacco` permit held first. See decision 0093 for what this
deliberately does **not** model: each permit's confirmed exclusion-distance-from-other-stores
rule (7/11/15 tiles) is left unenforced -- it would need an actual spatial map of rival-store
locations, which task #26 (below) deliberately did not build -- and fixture-to-category
compatibility (e.g. only refrigerated fixtures for cold drinks) isn't checked either.

### Advertising / promotions

`reference_sim/conveni_sim/promotion.py` already had a complete, evidence-safe design for this
(`PromotionScheduler`/`StorePopularityRuntime`/`apply_confirmed_triggered_promotion`); this ports
it faithfully rather than reinterpreting the evidence. Key confirmed facts from that module:
`trigger_day`/`trigger_hour` are an **absolute** representative-day-of-month (1-4) and hour, not
"days after purchase"; a promotion can only be scheduled if the current moment is at or before its
trigger this month; cost is debited only when the event actually fires, not at purchase time
(confirmed by direct video observation: "cash falls by exactly ¥100,000 as the day-2 10:00 event
fires"); popularity is capped at 100; and each promotion method can only be used once per month.
`VerticalSliceSimulation.try_purchase_promotion(promotion_id)` schedules a promotion from
`data/vertical_slice.json`'s `promotions` catalog (direct mail/newspaper/airship/radio/tv, all
**CONFIRMED_OFFICIAL or CONFIRMED_COMMUNITY** pricing/timing from `reference_sim`'s `PROMOTIONS`);
`_fire_due_promotions()` (checked every tick, before day-boundary handling so a trigger landing on
a month's last tick still resolves against the correct day) applies the cost and `popularity`
gain once due. Deliberately not modeled: the guide-confirmed daily popularity decay for
low-rated stores, since `reference_sim` itself leaves the decay amount unresolved. See decision
0094. **This closes out task #25** (fixture purchase, permits/procurement, and advertising).

### Town, rival dilution, and land value

`reference_sim/conveni_sim/town.py`'s `TownState` is ported as-is (`town_state.gd`): just tracked
`population`/`store_count_including_rivals`, no invented spatial map, facility placement, or
population-growth simulation -- `reference_sim` itself has none of those either, and
`PROJECT_MEMORY.md` section 17 lists the general town-growth formula as an open research gap, not
something to guess at. `VerticalSliceSimulation` constructs `town` from `data/vertical_slice.json`'s
new `town` section and wires exactly one real gameplay effect from it: rival dilution. It sets
`demand.rival_store_count = max(0, town.store_count_including_rivals - 1)` (excluding the player's
own store), and `DemandPolicy.expected_arrivals_per_minute()` now scales down by
`min(MAX_RIVAL_DILUTION, RIVAL_DILUTION_PER_COMPETITOR * rival_store_count)` --
**CONFIRMED_OFFICIAL/COMMUNITY-adjacent constants** (0.08 per competitor, capped at 0.6) reused
unchanged from `reference_sim/conveni_sim/remake_customer_share.py`, but applied to the whole
expected-visitor estimate rather than that module's 0-100 customer-share score, since this client
has no service/cleaning/security/assortment stats yet to feed that score. Defaults to zero rivals
(a no-op), so every existing test that never sets `town` is unaffected. `land_value_policy.gd`
ports `reference_sim/conveni_sim/remake_land_value.py`'s `RemakeBalancedLandValuePolicy` formula
(local development from population/store density, times annual 5% inflation) verbatim as another
tagged **REMAKE_BALANCED_DEFAULT** placeholder, exposed as `snapshot()`'s `land_value_yen` purely
for display -- no purchase/sale mechanic consumes it yet. Deliberately **not** implemented: any
actual spatial/map simulation, rival store placement, distance-based trade-area overlap or permit
exclusion-distance enforcement, and the rival AI decision function
(`remake_rival_policy.py`'s `RemakeBalancedRivalPolicy.decide()`) -- there is no rival-store entity
in Godot yet for such a decision to act on. See decision 0095. **This closes out task #26.**

### Store rating (★ rank)

`reference_sim/conveni_sim/store_rating.py`/`store_value.py` are direct transcriptions of the
strategy guide's own published ★-rank table and service/security/cleaning-value formulas
(書籍頁74-75) -- **CONFIRMED_OFFICIAL**, not this project's own guess. `store_rating.gd`/
`store_value.gd` port them verbatim: a 0-100 internal evaluation value maps to 0-5 stars at fixed
breakpoints, and each representative month, at least 3 of (price change / service / security /
cleaning / sales) meeting the current rank's upgrade thresholds grants +5, while each of those 5
criteria falling below the rank's downgrade thresholds costs -1. `VerticalSliceSimulation` calls
`_evaluate_store_rating()` from `_settle_month_end()`, feeding it: the average of all staff
`service_skill` values plus the summed `service_bonus` of purchased amenity fixtures (service
value); staff `security_skill`/`cleaning_skill` totals times the store's `size_tier` multiplier
(security/cleaning value); the representative month's sales revenue extrapolated x8 (same
4-day-to-month rule as decision 0090); and `price_change_pct = 0`, since this vertical slice has no
price-setting mechanic yet. `internal_rating_value`/`star_rating` update and a
`store_rating_evaluated` event is recorded every month end. Staff `service_skill`/`security_skill`/
`cleaning_skill` are new static, config-supplied **REMAKE_BALANCED_DEFAULT** fields on
`StaffState` -- the guide's own skill-growth model (work-event counting, manager-education bonus,
`reference_sim/conveni_sim/staff.py`) has not been ported to this client at all yet, so these
values never change on their own. The store's `size_tier` ("small") is also a
REMAKE_BALANCED_DEFAULT house-rule mapping: the guide only defines three tiers by exact dimensions
(10x10/12x12/14x14 tiles) and this prototype's 7x6 store matches none of them. Deliberately **not**
implemented: the police-box/fire-station security-facility bonus (no such fixtures or spatial
search exist yet) and the guide's per-event rating deltas (an angry customer at 1/6 odds, -1;
shoplifting, -1; a donation, +5) -- their trigger events aren't wired into this client either. See
decision 0096. **This closes out task #27.**

### Save / load

`VerticalSliceSimulation.save_state()`/`load_state(data)` are a pure engine feature -- there is no
`reference_sim` counterpart to port, so this is a design-decision record rather than an
evidence-tagging one (decision 0097). They round-trip time/day/month counters, game-over/clear
state, popularity/rating, held permits, scheduled/used promotions, the store layout (including
purchased/moved/rotated fixtures), full inventory (including procured product SKUs), and the
complete economy (cash, sale/expense/month-end history) and event log. Deliberately **not**
saved/restored: the active customer's mid-visit walk state and staff members' mid-task walk/restock
state -- both are transient sub-representative-day animation progress that a fresh `reset()`
already produces on its own, the same as this client's other reset boundaries. Because of that,
`load_state()` resets every subsystem to its config-derived starting point first, applies the saved
fields, restores the layout, and only *then* admits a fresh default customer -- admitting one
before the layout is restored could leave its cached route stale against fixtures that are about to
change. `load_state()` rejects (returns `false`, no mutation) a save with a different
`scenario_id`/`config_schema_version`/`save_schema_version` than the running config, the same
"expected, recoverable rejection" convention as this client's other `try_*` methods; a structurally
corrupted save (missing keys entirely) instead asserts, matching `_require_config()`'s own
convention. `save_game_service.gd`'s `SaveGameService` is a thin I/O boundary (kept out of
`scripts/domain/`, which stays I/O-free) turning that Dictionary into/from a JSON file under
Godot's `user://saves/`. Implementing this surfaced and fixed two existing latent bugs: `StoreLayout
.restore_fixture_snapshot()` wasn't normalizing float-typed coordinates from a JSON round-trip, and
naively rebuilding `EconomyState`'s settled-customer guard from saved sale records would have
permanently blocked the freshly re-admitted customer of the same recycled id from ever completing a
sale. **This closes out task #28.**

Each successful checkout also appends an immutable prototype sale record linking the customer,
minute-of-day, basket lines, and total. This ledger is factual telemetry for the explicit slice;
its IDs and shape are not a reconstruction of an original receipt system.

The runtime also retains a cause-neutral event timeline for admissions, product visits,
pickup/unavailability, checkout, exit, and accepted layout edits. A versioned provisional
observation snapshot exposes those events with sales and inventory for future evidence comparison;
it is not an original event format or causality model.

An explicit non-UI restock boundary can return a caller-specified quantity to a known product while
recording the caller-specified procurement total as an immutable expense. It deliberately contains
no capacity, reorder trigger, supplier-price, delivery, or autonomous staff-selection formula.

Each manual admission now creates a distinct customer record. Completed records are retained rather
than reusing one mutable customer object. The current slice intentionally permits only one active
customer because original concurrent-arrival and collision rules have not yet been recovered.
An additional non-UI admission boundary accepts a caller-provided unique customer ID and explicit
known-product order for future observation replay; it still makes no arrival or purchase decision.

The store renderer also shows the tile/subcell grid, fixture footprints, interaction points, entry/exit points, customer, and staff.

## Important evidence boundary

`data/vertical_slice.json` is explicitly marked `provisional: true`.

Its layout, tick rate, shopping duration, checkout duration, initial cash, stock, and price exist only to make the first visible client executable. They are **not claims that the original PS/SS game used those values or formulas**.

As original behavior becomes confirmed through research, observation replay, emulator experiments, or later disc reverse engineering, production rules should replace provisional inputs deliberately and with tests.

## Run

1. Install Godot 4.x.
2. Import `game/project.godot`.
3. Run the project (`F6/F5` depending on editor workflow; the configured main scene is `res://scenes/main.tscn`).

Controls:

- **Pause / Resume** — pause automatic prototype ticks.
- **Step** — execute exactly one prototype simulation step while paused.
- **Reset** — restore the initial vertical-slice state.
- **Admit next customer** — manually force the next visit instead of waiting for the automatic
  demand-driven arrival roll to succeed (see "Customer arrival" above).
- **Prototype layout relocation** — after a visit finishes, tap/click a fixture and then an empty
  grid cell. Invalid or route-breaking moves are rejected atomically. This interaction is
  PROVISIONAL and is not a reconstruction of the original construction menu.
- **Rotate selected fixture clockwise** — rotate the selected fixture by one quarter turn after a
  visit. The control, pivot, and interaction-point transformation remain PROVISIONAL even though
  fixture rotation itself is visually confirmed in first-title research.
- **Reset** also discards layout edits and restores the complete configured prototype scenario.
- **Space** — Pause / Resume shortcut.

## Headless validation

With Godot 4.3 available, load the main scene and execute the deterministic vertical slice without a display:

```bash
godot --headless --path game --script res://scripts/headless_smoke.gd
```

The smoke script first loads and instantiates the configured main scene, then verifies repeat visits
through sellout: each stocked visit completes a sale,
stock and cash stay consistent, and a later empty-shelf visit exits without creating revenue. CI
runs both the Godot import and this executable smoke check in addition to the Python contracts.

## Architecture direction

- `scripts/vertical_slice_simulation.gd` — deterministic prototype orchestration and combined
  read-only snapshots; no rendering.
- `scripts/domain/store_layout.gd` — store bounds, fixture occupancy, interaction points, and
  static pathfinding.
- `scripts/domain/inventory_state.gd` — provisional product identity, shelf stock, and price state.
- `scripts/domain/inventory_catalog.gd` — product-ID lookup, aggregate stock, explicit fixture
  bindings, and sellout reconciliation.
- `scripts/domain/economy_state.gd` — cash and completed-sale settlement state.
  It also retains immutable cause-neutral sale records for reconciliation and later observation
  export, plus month-end settlement records for the CONFIRMED_OFFICIAL 4-day x8 month cycle.
- `scripts/domain/customer_state.gd` — one customer's route, phase, position, explicit visit plan,
  basket lines, and action timers.
- `scripts/domain/customer_roster.gd` — unique customer identity, retained visit state, and the
  explicit single-active-customer admission boundary.
- `scripts/domain/staff_state.gd` — one staff member's identity, position, and prototype task state,
  including the PROVISIONAL `to_restock`/`restocking` cycle for non-checkout staff.
- `scripts/domain/staff_roster.gd` — configured staff membership and the explicitly selected
  provisional checkout staff; task *assignment* across non-checkout staff now happens in
  `vertical_slice_simulation.gd`'s `_assign_idle_restock_tasks()`, not here.
- `scripts/domain/runtime_event_log.gd` — immutable sequenced facts for deterministic observation
  export; event names and timestamp shape remain provisional.
- `scripts/domain/demand_policy.gd` — REMAKE_BALANCED_DEFAULT per-minute customer-arrival
  probability, ported from `reference_sim/conveni_sim/remake_demand_policy.py`; decides only
  *whether* the next customer arrives, not concurrent arrivals.
- `scripts/store_view.gd` — generated 2D visualization only.
- `scripts/main.gd` — client orchestration and HUD binding.
- `scripts/headless_smoke.gd` — Godot-native deterministic executable check.
- `data/vertical_slice.json` — explicit provisional inputs.
- `scenes/main.tscn` — player-facing scene composition.
- `reference_sim/` — compatibility oracle and evidence-backed validation, not a runtime dependency of the Godot app.

The vertical slice now composes reusable engine-native layout, customer, staff, inventory, and
economy state objects plus explicit actor rosters. Customer admission is now demand-driven via a
separately identified, tagged-guess policy (`demand_policy.gd`) rather than only manual, but
concurrency (more than one active customer) remains unimplemented and unrecovered. The next
production steps are to connect actor rosters and explicit product plans to evidence-backed
observation replay, introduce genuine concurrency only behind a separately identified policy, and
expand store interaction without changing unresolved original rules silently.
