# Decision 0073: Replay a cause-neutral checkout return as pre-service departure only by explicit interpretation

## Status

Accepted.

## Context

Decision 0072 added `CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM` as a cause-neutral observation. The visible event can come from more than one runtime structure, including a checkout ownership-conflict loser or a checkout-assigned staff member leaving before service.

The observation itself therefore must not automatically select a runtime cause.

The reference simulator nevertheless needs a controlled way to test the hypothesis that a particular observed return corresponds to the pre-service departure seam introduced earlier.

## Decision

Add an observation replay adapter that requires the caller to set:

`checkout_staff_return_means_pre_service_departure=True`

Only under that explicit mapping does an in-coverage `CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM` event become an `ObservedCheckoutPreServiceDepartureRule`.

Each rule preserves:

- explicit staff identity;
- explicit checkout fixture identity;
- chronological occurrence index for that staff/checkout pair;
- the exact observed game minute.

Differing observed/runtime ids are translated only through the existing explicit one-to-one `ObservationIdentityMapping`.

The replay policy leaves the decision unresolved before the next observed return minute. At or after that minute it requests `RETURN_TO_BREAK_ROOM`. The existing runtime coordinator still requires factual waiting checkout demand and a free service slot before consulting the policy, so an observation never manufactures demand or checkout capacity.

The break-room target remains an explicit scenario/runtime input and is not inferred from the observation.

The adapter is wired into the minimal representative-day validation and composed observation replay path so the sequence can be validated end to end:

observed event -> explicit interpretation -> runtime departure policy -> autonomous run -> simulation observation export -> event comparison.

## Consequences

- A source observation can be replayed as one specific causal hypothesis without changing the cause-neutral observation vocabulary.
- Earlier service is not silently invented while waiting for the observed departure minute.
- If runtime facts delay the departure beyond the observed minute, ordinary event comparison exposes the timing delta.
- Multiple observed return occurrences for the same staff/checkout pair are kept in chronological occurrence order.
- Unobserved decisions remain unresolved rather than falling back to a synthetic departure or service rule.

## Explicit non-decisions

This does **not** establish:

- that every checkout-associated break-room return is a pre-service departure;
- that a return observed during a multi-staff conflict has this cause;
- a stamina threshold or probability;
- that low stamina is necessary or sufficient;
- a break-room travel or recovery duration;
- a checkout ownership winner formula;
- a queue-length or waiting-time threshold;
- PS/SS equivalence;
- sub-minute event timing.
