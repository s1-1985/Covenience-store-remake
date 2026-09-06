# Decision 0051: keep rival-chain evolution as explicit state transitions until AI formulas are recovered

## Context

First-title PS/SS research confirms that rival stores are not static scenery. Rival branches can close under competitive pressure, the rival chain can later open a replacement store at another location, rival branches can be acquired, and headquarters/branch roles are distinct. Research also records eventual headquarters closure and chain disappearance in long play.

The original rules that decide *when* a rival closes, how much cash the rival owns, how long it waits before reopening, which parcel it chooses, what it charges, and how acquisition prices are calculated are still unresolved. Those rules must not be reconstructed from later titles or invented from modern management-game conventions.

Primary repository evidence:

- `docs/research/progression-events-town-evidence-2026-09-05.md`
- `docs/research/first-title-wiki-full-scan-delta-2026-09-05.md`
- `docs/research/ps-longplay-rival-economy-events-2026-09-05.md`

## Decision

Add a small `RivalChainRuntime` that stores only factual chain/store state and accepts explicit transitions from an observation source or future replaceable AI policy.

The runtime represents:

- headquarters versus branch role;
- active, closed and acquired store state;
- explicit store opening at a caller-supplied location;
- explicit closure with an evidence/policy source string;
- explicit branch acquisition and buyer identity;
- transition history;
- chain extinction as the factual condition that no rival store remains active.

The runtime deliberately has no profit/loss update method that can implicitly close a store. A future economy/AI policy must make that decision and then call the explicit transition API.

Headquarters acquisition is rejected because first-title research explicitly distinguishes buyable rival branches from the non-buyable rival headquarters. Headquarters closure remains an explicit transition because its trigger is not yet reconstructed.

## Unresolved boundary

Do not hard-code any of the following in this layer:

- loss amount or duration required for closure;
- rival cash, borrowing or bankruptcy model;
- reopening delay;
- site-selection or expansion scoring;
- player/rival total-store-cap enforcement context;
- product prices or customer-share strategy;
- acquisition-price formula;
- permit acquisition behavior;
- exact cause/order of final headquarters closure;
- PS/SS differences not directly evidenced.

The confirmed map-wide ten-convenience-store cap belongs in a future world/chain coordinator that can see both player and rival stores; it is intentionally not guessed from rival-local state.

## Consequences

This creates a stable data-driven seam for later rival AI. Research can add exact policy inputs without changing the chain state representation, while video replay can already record observed closure/reopening/acquisition sequences faithfully.
