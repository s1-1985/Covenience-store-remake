# Decision 0042 — Capture factual store telemetry without fitting formulas

Date: 2026-09-06

## Context

The representative-day milestone requires comparing simulator output against recovered observations for arrivals, checkout congestion, stamina, stock and cash. The executable core can now run a whole representative day, but those runtime states are spread across customer, checkout, staff, inventory and economy objects.

A comparison layer should not introduce new behavior or fit unknown first-title coefficients merely to make metrics convenient.

## Decision

Add `StoreTelemetryRecorder`, a read-only factual snapshot layer that records at one game-clock instant:

- total customer sessions and counts by explicit `CustomerState`;
- waiting and active checkout customers plus active cashier staff per checkout;
- staff condition, current task/target and known/unknown stamina values;
- inventory units and capacity per slot;
- known cash and whether the ledger remains exact.

The recorder calculates checkout waiting membership directly from current customer state and active service records rather than invoking mutating queue refresh methods.

`RepresentativeDayRunner` captures telemetry:

1. at run start;
2. after every ordinary store step;
3. at 23:59 immediately before day close;
4. at 00:00 after the boundary-only clock advance.

## Evidence-safe boundary

Telemetry does **not** define or fit:

- spawn rates;
- queue patience or abandonment rules;
- checkout or staff-work durations;
- stamina consumption/recovery formulas;
- reorder points or replenishment quantities;
- demand, price, popularity or customer-share coefficients;
- hidden financial events.

Unknown stamina and unknown monetary effects remain unknown in the snapshot.

## Consequence

A complete representative-day run now produces a deterministic, time-aligned trace of the same categories targeted by observation work. Future comparison/fitting code can consume these snapshots without modifying the simulator's behavioral rules.
