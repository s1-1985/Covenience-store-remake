# Decision 0056: compare observation timelines only through explicit identities and coverage

## Context

The reference simulator can now export representative-day runtime events into the same `GameplayObservationTimeline` vocabulary used by video annotations. Aggregate representative-day metrics are useful, but they can hide where two runs diverge: a day can have the same customer count while arrivals, queue entry, anger, checkout completion, replenishment or cleaning occur at different game times.

The original first-title formulas and tolerances remain unresolved. Video annotations also use researcher-assigned entity ids that need not equal simulator ids. Automatically pairing events by nearest timestamp would therefore invent customer/staff/fixture correspondence and could make a wrong model appear closer to the source than the evidence supports.

## Decision

Add an event comparison layer with these rules:

1. Compare only events inside one caller-supplied `ObservationDayCoverage` window.
2. Report per-`ObservationKind` observed count, simulated count and signed count delta.
3. Match individual events by an explicit signature:
   - observation kind;
   - customer id;
   - staff id;
   - fixture id.
4. Literal ids that are already equal may match directly.
5. Different observed and simulated ids match only through `ObservationIdentityMapping` supplied by the caller.
6. Identity mappings are one-to-one; two observed entities cannot collapse onto one simulated entity.
7. Repeated events sharing one explicit signature are paired chronologically by ordinal occurrence.
8. For matched events report signed simulated-minus-observed game-minute delta and, when both sides have numeric values, signed numeric delta.
9. Preserve unmatched observed and unmatched simulated events explicitly.
10. Do not add a tolerance, score, pass/fail threshold or nearest-time fallback.

`validate_minimal_day_with_event_comparison()` composes the existing coverage-aware metric reduction, one autonomous representative-day run, simulation timeline export and this event comparator in one call. An optional caller-supplied checkout anger policy may still be wired through the scenario; the validation layer does not choose one.

## Why

This gives source-video annotations and the reference simulator a common factual diff surface while preserving unknown behavior. The comparison can show exactly where the model is early, late, missing or overproducing events without asserting that a particular difference is acceptable or that two differently labeled entities are the same.

## Non-decisions

This does not define:

- acceptable game-minute error;
- a weighted similarity score;
- customer/staff/fixture identity inference;
- nearest-time event matching;
- video-time to game-time conversion;
- sub-minute engine timing;
- a patience or anger formula;
- whether repeated anger events share one original-game trigger;
- any original AI or queue ordering rule.
