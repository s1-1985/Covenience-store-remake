# Project directives for Claude Code sessions

This file exists so this rule does not depend on any one session remembering
it or one handoff doc being read to the end. Read this file first, then
`PROJECT_MEMORY.md` (the canonical project memory checkpoint), then the most
recent file under `docs/handoff/`.

## What this project is

A faithful recreation of the first home-console release of
**『ザ・コンビニ ～あの町を独占せよ～』** ("The Conveni", PlayStation/Sega
Saturn, 1997). See `PROJECT_MEMORY.md` section 1-2 for the full scope
statement. This is a recreation project, not a new original game inspired by
it. Do not drift toward inventing an unrelated original game.

## The core data-integrity rule

Every piece of game data and every mechanic must trace back to one of:

1. **Recovered evidence** — the strategy guide scans, the first-title wiki,
   direct-play observation, or another primary source, tagged
   `CONFIRMED_OFFICIAL` / `CONFIRMED_VISUAL` / `CONFIRMED_COMMUNITY` per the
   evidence-level scale in `PROJECT_MEMORY.md` section 15.
2. **Analogy-based inference from other confirmed data**, when the exact
   value or mechanic itself was never stated by any source but a *related*
   confirmed data point exists that the missing value can be reasonably
   derived from. Prefer this over (3) whenever a real anchor point exists.
   Example: a product category's exact order-lot size was never stated by
   the strategy guide, but the same guide row *does* state that category's
   shelf `max_capacity` — deriving the placeholder order size from that
   category's own `max_capacity` is analogy-based; picking the same flat
   round number (e.g. `10`) for every category regardless of its own scale
   is not, even if it "feels" conservative.
3. **This project's own invented placeholder**, only when neither (1) nor
   (2) is available — e.g. no related confirmed data exists at all, or the
   research notes explicitly say no formula should be invented from a
   qualitative observation (see `docs/research/checkout-staff-dispatch-
   evidence-2026-09-05.md` section 5 for an example of that explicit
   caveat). This is the last resort, not the default.

**Never skip straight to (3) when (2) is available.** Before hard-coding an
arbitrary constant, check whether the same source row, or another already-
CONFIRMED field on the same entity, gives a real number to anchor it to
instead. A session was corrected on exactly this mistake in task #39→#42:
`initial_stock_units` was first set to a flat `10` for every ported product
category, ignoring that each category's own CONFIRMED_OFFICIAL
`max_capacity` was already sitting in the same source row and available to
derive it from instead. See `docs/decisions/0111-*.md` for the fix.

## Tagging discipline for anything in bucket (3)

Any value or mechanic that is this project's own invention (bucket 3 above,
or a scaling *shape* built on top of a bucket-2 anchor, like the inverse-
proportion formulas in `checkout_timing.gd`/`restock_timing.gd`) must carry
the literal string `REMAKE_BALANCED_DEFAULT` in **all three** of:

1. a code comment at the point it's used or defined,
2. the relevant `evidence_note` field in `game/data/vertical_slice.json` (or
   the equivalent `reference_sim` docstring), and
3. a test assertion (in `reference_sim/tests/test_game_vertical_slice_
   contract.py` or `game/scripts/headless_smoke.gd`) that checks the tag
   text is actually present — not just documented in a decision doc or PR
   description, which a future diff can silently drop.

This applies to `game/scripts/` UI-layer files (like `main.gd`) exactly the
same as it applies to `vertical_slice_simulation.gd`/`domain/*.gd` — a gap
here was itself the subject of an earlier correction (task #38→#38
correction, PR #209); see `PROJECT_MEMORY.md` section 19 for that history.

## Workflow conventions

- Decisions go in `docs/decisions/NNNN-*.md`, one per task, following the
  existing numbering and structure (background / decision / tests /
  files / explicitly-out-of-scope).
- `PROJECT_MEMORY.md` section 19 is a running log of implementation
  checkpoints; append to it, don't rewrite history.
- The most recent file under `docs/handoff/` is the up-to-date session
  handoff; treat older ones as superseded where they conflict (verify
  against the newest `docs/research/*crosscheck*` note before trusting an
  older handoff's claim that something is still unresolved).
- Both test suites (`reference_sim`'s `pytest` and `game`'s
  `headless_smoke.gd` under a real Godot 4.3 binary) must pass before
  a change is considered done.
