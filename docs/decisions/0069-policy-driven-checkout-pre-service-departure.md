# 0069 — Policy-driven checkout pre-service departure

## Decision

Add an optional checkout pre-service departure boundary between checkout assignment/ownership and customer service start.

For an `AVAILABLE` staff member already assigned to a checkout and not yet serving a customer, `CheckoutPreServiceDepartureCoordinator` exposes only factual runtime state:

- staff id,
- checkout fixture id,
- waiting customer ids,
- active service count,
- simultaneous staff capacity,
- free service slots,
- current stamina and maximum stamina when known,
- current game minute.

The policy is not consulted when no customer is factually waiting or when no service slot is free.

When consulted, the policy may return:

- `PROCEED_TO_SERVICE`,
- `RETURN_TO_BREAK_ROOM`, or
- `None` for unresolved.

An unresolved decision blocks that staff member from beginning checkout service in the current store step rather than silently assuming the staff remains at the register. `RETURN_TO_BREAK_ROOM` uses the existing stamina-neutral explicit break-room-return transition and therefore does not manufacture stamina depletion.

StoreStep applies this boundary after checkout ownership-conflict resolution and before checkout customer selection. Thus an explicitly selected checkout owner can still leave before service if a caller-supplied policy says so. A newly returning staff member is synced into the existing rest coordinator, but no same-step break-room arrival or recovery is invented.

With no pre-service departure policy supplied, existing checkout behavior remains unchanged.

## Why

First-title dedicated B+ research reports cases where a staff member reacts to checkout demand but, when stamina is low, soon returns toward the break room and leaves the checkout unattended. The observation does not recover the stamina threshold, exact timing, or whether departure occurs before a customer service actually begins or immediately after a service boundary in every case.

A separate pre-service policy seam lets explicit observations or future recovered rules drive that behavior without embedding a guessed low-stamina threshold in checkout assignment or service timing.

## Safety boundary

This decision does not establish:

- a low-stamina threshold,
- a stamina percentage rule,
- a departure probability,
- whether departure happens before the first customer or after one completed customer in every observed case,
- a break-room travel time,
- a rest duration or recovery amount,
- a replacement-staff selection rule,
- a customer anger threshold caused by the unattended checkout,
- PS/SS equivalence.

Unknown stamina remains `None`; it is not treated as zero or full.