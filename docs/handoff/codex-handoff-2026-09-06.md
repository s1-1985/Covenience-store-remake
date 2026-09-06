# Codex handoff — 2026-09-06

## Source of truth

Repository: `s1-1985/Covenience-store-remake`

Current merged `main` at handoff start:

- `5d119162deba1f4e9fac76d63896448030b50788`

Current in-progress branch:

- `chatgpt/godot-vertical-slice`

Do not restart this work from an older branch. Fetch latest `main` first and compare before modifying or rebasing this branch.

## Project goal

The immediate baseline target is a faithful recreation of the first home-console `ザ・コンビニ ～あの町を独占せよ～` gameplay structure, followed by original modernization and new game systems.

The production target is Android. Original copyrighted assets must not be copied into the new game; use original/recreated assets and treat the original game only as a research target.

## Critical implementation principle

Unrecovered original values/formulas must never be silently guessed and promoted to original-game facts.

Use one of these instead:

- explicit `None` / unknown values in the reference simulator;
- replaceable policy seams;
- explicitly labelled provisional values in the playable client.

The Godot vertical slice uses `game/data/vertical_slice.json` with `"provisional": true`. These values exist only to make the first playable client loop visible and must not be treated as recovered first-title constants.

## Reference simulator status

`reference_sim/conveni_sim/` is the headless compatibility/reference simulator. It already supports an autonomous representative day and should now primarily act as a specification/validation oracle rather than the only development target.

The executable flow already covers roughly:

customer demand/admission -> movement -> merchandise -> purchase policy -> inventory pick -> checkout waiting -> staff assignment -> checkout selection -> timed service -> settlement/cash -> stamina/rest -> leave

and staff work including timed replenish/clean, growth, interruption policy, rest, checkout conflict handling and pre-service departure.

Observation replay/comparison currently covers:

- customer arrival replay;
- checkout customer selection/order replay;
- checkout service-start timing;
- checkout duration replay;
- checkout anger timing replay;
- replenish/clean start target/timing replay;
- replenish/clean duration replay;
- replenish/clean interruption replay;
- cause-neutral checkout-associated break-room return observations;
- explicit replay of that return as a pre-service checkout departure.

## Recent merged PRs

### PR #180

`Export checkout staff break-room returns as observations`

Merged as:

- `4912a6759f2c635b26686a33ae4207ff01d744f8`

Added shared observation kind:

- `CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM`

The event is deliberately cause-neutral. It can be exported from:

- a checkout ownership conflict loser explicitly returning to the break room;
- a checkout-assigned staff member explicitly departing before checkout service.

Do not infer stamina threshold, ownership winner formula or break-room timing from this event.

### PR #181

`Replay observed checkout returns as pre-service departure`

Merged as:

- `5d119162deba1f4e9fac76d63896448030b50788`

Added explicit replay mapping so the cause-neutral checkout return event becomes a runtime pre-service departure only when the caller opts in.

Important behavior:

- no causal interpretation without explicit mapping;
- service stays unresolved before the observed return minute;
- the observation does not manufacture waiting demand or checkout capacity;
- break-room target remains an explicit scenario input;
- composed observation replay can round-trip observation -> runtime -> exported observation -> event comparison.

## Playable Godot vertical slice — current branch work

Branch: `chatgpt/godot-vertical-slice`

This is the first move from the headless reference simulator toward the actual Android game client.

Files added/modified so far include:

- `game/project.godot`
- `game/data/vertical_slice.json`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/store_view.gd`
- `game/scripts/main.gd`
- `game/scenes/main.tscn`
- `game/README.md`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `.github/workflows/reference-tests.yml`

### Vertical-slice intent

The first visible loop is intentionally small:

customer enters -> walks to shelf -> takes product -> stock decreases -> walks to checkout -> checkout completes -> cash increases -> customer exits

The store view uses newly drawn primitive shapes/text only, not original game assets.

The scene/UI currently aims to show:

- store grid;
- shelf;
- checkout;
- customer;
- staff;
- game clock;
- cash;
- stock;
- customer/staff state;
- completed-sale count;
- Pause / Step / Reset controls.

### Prototype simulation behavior

`vertical_slice_simulation.gd` is a deliberately provisional client-side model. It uses the JSON scenario data and includes explicit pathing rather than treating the store as an abstract spreadsheet.

The current implementation uses grid/subcell movement and BFS-style route finding around fixture occupancy. The gameplay-sensitive speeds/timings/layout values are provisional, not recovered first-title constants.

## CI / contract work already added

`reference_sim/tests/test_game_vertical_slice_contract.py` validates the production-client scaffold and provisional-data boundary.

The reference test workflow was changed so `game/**` changes trigger CI as well as `reference_sim/**` changes.

## Next work for Codex

Continue on `chatgpt/godot-vertical-slice` unless latest `main` contains a conflicting/newer implementation.

Priority order:

1. Inspect the current branch files and validate GDScript/scene correctness.
2. Add a real Godot headless CI job so Godot itself parses/loads `game/project.godot` and the main scene.
3. Fix any GDScript/scene/runtime errors exposed by that CI.
4. Add/confirm a decision document for the first playable Godot vertical slice and its provisional-data boundary. Before assigning a decision number, inspect latest `main` because decision numbers are being consumed by concurrent work.
5. Run the full existing Python reference suite plus the Godot headless check.
6. Open a focused PR from `chatgpt/godot-vertical-slice` to `main`.
7. Poll CI; fix failures before merging.
8. Merge only with a successful CI and a fixed expected head SHA.
9. Fetch latest `main` after merge.

After the first playable vertical slice is merged, prioritize visible/playable production-client progress over adding more generic analysis seams unless a missing reference-system boundary actually blocks the client.

## Important stale project-memory note

`PROJECT_MEMORY.md` section 19 still says the next large milestone is "one small store running one representative day autonomously". That milestone has already been achieved in the reference simulator.

Do not use that stale wording to redirect work back into endless headless-framework expansion. The current direction is:

1. keep the reference simulator as compatibility oracle;
2. build the actual Godot/Android client;
3. use new observation/disc reverse-engineering evidence to replace provisional/unknown rules as they become known.

It is safe to update section 19 when touching project memory, but preserve historical research content.

## Reverse-engineering / AI workflow direction

The user plans to use ChatGPT/Codex, Claude Code and Gemini Pro together, and may later provide a Sega Saturn disc image extracted from an original disc.

Recommended role split discussed with the user:

- Claude Code: local reverse-engineering/operator work — disc extraction, file inventory, scripts, Ghidra automation, binary/static analysis, Git-local tooling.
- Gemini Pro: large-context cross-analysis of generated decompilation/strings/tables/call graphs and hypothesis clustering.
- ChatGPT/Codex: evidence adjudication, architecture, implementation, tests, PR/CI and integration into the remake.

Keep the original BIN/CUE outside the public repository. Treat it as read-only research evidence. Generate smaller structured findings (JSON/CSV/MD/decompiled snippets) for cross-AI analysis instead of committing original copyrighted binary/assets.

A future `reverse/findings/`-style evidence bridge was discussed: each finding should identify platform, binary/function/offset, claim, confidence and emulator verification without copying original copyrighted assets into the remake.

## Unresolved first-title rules that must not be invented

Examples still unresolved or only partially observed include:

- original customer spawn/demand formula;
- original purchase-choice formula;
- general staff task-priority formula;
- checkout duration formula outside explicitly observed replays;
- checkout stamina formula;
- replenish/clean timing, quantity and stamina coefficients;
- traffic reroute threshold/logic;
- break-room travel duration;
- agility -> recovery probability;
- exact dirt generation rate;
- checkout/register skill growth increment;
- exact customer patience/abandonment threshold;
- anger basis and repeated anger semantics;
- staff-work interruption threshold/formula;
- interrupted-work resume semantics;
- checkout ownership winner formula;
- whether conflict losers always return to break room;
- stamina role in checkout conflict/pre-service departure;
- whether low-stamina staff can leave mid-customer and exact timing;
- complete economic aggregation/month-end formulas;
- production wall-clock/game-time ratio.

Keep these behind explicit policy/data boundaries until evidence is stronger.

## Handoff completion state

At the time of this handoff, the Godot vertical slice branch is intentionally NOT merged yet. The unfinished work is the Godot-native headless CI/validation, any fixes that exposes, decision documentation, PR, CI and merge.
