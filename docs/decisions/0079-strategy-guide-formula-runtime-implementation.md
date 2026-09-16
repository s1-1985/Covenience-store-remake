# Decision 0079: Implement the strategy guide's 8 confirmed formulas in the runtime

## Status

Accepted.

## Context

Decisions 0077/0078 transcribed a set of game formulas and event-trigger conditions
found in the strategy guide's "オールテクニックガイド" (all-technique guide) section into
`docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md` as data, without wiring
them into `reference_sim/conveni_sim`'s runtime. An audit at that point found 7 of 8 such
systems (service/security/cleaning value, the 5-star rating table, 5 event triggers, the
100-year game-over clause, the new-store land-cost formula, and promotion-effect decay)
completely unimplemented in the runtime; only the idol/visitor-milestone event already
existed (`visitor_milestone.py`, and it matches the guide almost exactly). The user asked
directly for these 8 to be implemented into the runtime rather than left as documentation.

## Decision

Read the existing runtime modules (`staff.py`, `promotion.py`, `cleaning.py`, `economy.py`,
`inducement.py`, `manager_magazine_event.py`, `visitor_milestone.py`,
`month_boundary.py`) to match this codebase's established conventions before writing new
code: small, standalone, pure-function/dataclass modules; explicit `ValueError` validation;
and a well-established "confirmed boundary, unconfirmed magnitude" idiom (e.g.
`PopularityDecayOpportunity`, `StaffGrowthOpportunity`) for guide facts that give a trigger
condition but not an exact numeric rate or probability.

For each of the 8 items, the guide's data was re-examined for what is actually a complete,
confirmed formula versus a confirmed boundary with an unconfirmed magnitude (a probability,
an exact deducted amount, etc.). Implemented accordingly:

**Fully specified — implemented as deterministic functions:**

- `store_value.py` (new): `compute_service_value`, `compute_security_value`,
  `compute_cleaning_value`, and `SecurityFacilityCoverage` (police_box/fire_station 16×16-
  range tile-count → capped bonus). All three store-value formulas and the store-size
  multiplier table (1.5/1.65/1.8) are printed explicitly in the guide.
- `store_rating.py` (new): `evaluate_monthly_rating_change`, the full 5-row
  upgrade/downgrade threshold tables, and `star_rank_for_internal_value`. The guide states
  upgrade requires meeting **at least 3 of 5** criteria (not all 5) for +5, and downgrade is
  -1 per failing criterion; both are exact and are implemented as such. Uses the
  "オールテクニックガイド" page's numbers as primary over a near-duplicate table with
  slightly different transcribed figures (see the crosscheck note); a ☆ (0-star) store is
  evaluated against the guide's ★1 row since the table has no row of its own for it.
- `inducement.py` (extended): `compute_new_store_land_cost_yen` (land price for 4 tiles +
  building valuation / 2), replacing the "deliberately does not calculate land cost yet"
  note in the module's own docstring with the now-known formula.
- `store_events.py` (new): `scenario_time_limit_exceeded` (100-year game-over clause,
  alongside the already-implemented bankruptcy path in `economy.py`/`month_boundary.py`),
  `compute_contest_prize_yen` (store count × 10,000,000 yen).

**Confirmed boundary, unconfirmed magnitude — implemented as eligibility/condition checks,
not simulated draws, matching the codebase's existing idiom:**

- `store_events.py`: `donation_event_is_eligible` (cash ≥ 1.5B yen) — the guide only gives a
  floor ("10億円以上") for the deducted amount, not an exact formula, so no deduction amount
  is computed. `magazine_or_contest_event_is_eligible` (population ≥ 10,000 AND stores ≥ 5)
  — the guide says the event "選ばれることもある" (may or may not be picked) once eligible,
  so no probability is rolled. `shoplifting_is_possible` (customer manner > store security)
  — implemented as a pure comparison; wiring it to an actual per-customer "manner" value is
  explicitly left to the caller, since the customer-visit-schedule deep-read (decision 0078)
  kept the guide's 9-column behavior stats as an unlabeled raw tuple rather than a
  confidently-named "manner" field. `FireOrRobberyRisk` (protection boundary via the same
  `SecurityFacilityCoverage`, plus the guide's "popularity > security" comparative hint) —
  no fire/robbery probability is computed, since the guide never gives one.
- `promotion.py` (extended): `promotion_effect_decay_applies` (rating ≤ 3 stars) — the guide
  confirms decay applies below this threshold but never states the daily rate; the existing
  `PopularityDecayOpportunity` "record now, resolve later" machinery already handles
  amount-unresolved decay, so this only adds the newly-confirmed trigger condition as a
  separate helper rather than inventing a rate to plug into that machinery.

**Not wired into `store_runtime.py`'s orchestration.** None of the existing standalone
runtime modules (`promotion.py`, `visitor_milestone.py`, `manager_magazine_event.py`) are
automatically composed into `store_runtime.py` either — that composition is left to callers
and tests throughout this codebase. The 8 new/extended modules follow the same pattern:
they are real, tested, importable runtime code, not documentation, but deciding exactly
when a game step should call them is a separate orchestration task this decision does not
take on.

## Evidence boundary

Every deterministic formula implemented here is printed explicitly in the strategy guide
and cited via a docstring `Source:` comment. Every place a magnitude was *not* confirmed
(the donation deduction beyond its 10億円 floor, event probabilities, the promotion decay
rate) is implemented only as far as the guide actually confirms it, with the gap stated in
the docstring rather than an invented number filling it.

Tests: `reference_sim/tests/test_store_value.py`, `test_store_rating.py`,
`test_store_events.py`, plus new test classes in `test_inducement.py` and
`test_promotion.py` (64 new tests total). Full suite: 540 passed, 1 xfailed (pre-existing,
unrelated).
