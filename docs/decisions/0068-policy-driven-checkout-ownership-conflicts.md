# 0068 — Policy-driven checkout ownership conflicts

## Decision

Represent same-checkout staff contention as an explicit runtime boundary instead of letting roster iteration order silently decide who begins service.

A `CheckoutOwnershipConflictCoordinator` detects a conflict only when:

- at least one customer is factually waiting at the checkout,
- multiple `AVAILABLE` staff are already assigned to that same checkout and have not begun service, and
- the number of contenders exceeds the checkout's currently free staff-service slots.

The coordinator exposes the contenders, active staff, waiting customers, configured simultaneous staff capacity and current free slots to a replaceable `CheckoutOwnershipConflictPolicy`.

The policy may return no decision. An unresolved conflict does not choose a winner; the conflicting contenders are prevented from beginning service in that store step.

A resolved decision must account for every contender and may name no more owners than there are free service slots. Each loser receives an explicit disposition:

- `KEEP_CHECKOUT`
- `RELEASE_TO_IDLE`
- `RETURN_TO_BREAK_ROOM`

`RETURN_TO_BREAK_ROOM` uses an explicit roster transition that does not change stamina. This keeps the observed checkout-conflict return separate from the already-supported stamina-exhaustion return path.

The StoreStep orchestration evaluates checkout ownership after generic staff task selection and before checkout customer selection. Only policy-named owners may start service in a resolved conflict. A newly returning loser may be registered by the existing rest coordinator, but no same-step break-room arrival or recovery is invented.

## Why

First-title dedicated B+ research reports that multiple staff can react to the same checkout demand, one can begin register work, and another may return to the break room instead of immediately resuming ordinary work. The evidence does not recover the winner-selection rule or prove that the losing staff always returns to the break room.

Keeping conflict detection factual and winner/loser behavior policy-driven allows direct video observations to be replayed later without promoting one observed outcome into a universal rule.

## Safety boundary

This decision does not establish:

- which staff wins a checkout conflict,
- whether roster order, distance, speed, staff id, skill or arrival time determines ownership,
- whether every losing staff member returns to the break room,
- how long a conflict loser stays away,
- whether stamina affects the loser transition,
- whether the behavior occurs identically with multiple physical checkouts or on both PS and SS,
- any queue-count threshold beyond factual waiting demand,
- any movement/travel time to the checkout or break room.

With no ownership policy supplied, existing checkout behavior remains unchanged.