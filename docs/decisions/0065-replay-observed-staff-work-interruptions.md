# 0065 — Replay explicitly observed replenish/clean interruptions

## Decision

Add explicit observation kinds for `REPLENISH_INTERRUPT` and `CLEAN_INTERRUPT` and allow complete in-coverage work-start -> work-interrupt pairs to drive the optional `StaffWorkInterruptionPolicy` when the caller explicitly opts in.

The replay plan stores per-staff/per-task chronological occurrence rules. Each rule contains only the explicitly measured game-minute span from work start to interruption. Partial starts or interruption events remain unpaired rather than receiving an imputed threshold.

The replay policy does not create checkout demand. Even after the observed elapsed threshold is reached, the runtime `StaffWorkInterruptionCoordinator` still requires an actual waiting checkout customer before it releases the work assignment. If the observed threshold and simulated checkout-demand timing disagree, the interruption occurs later and the existing event comparison reports that time mismatch.

The simulation observation exporter writes the explicit interruption event after checkout queue entry and before replacement staff-task / checkout-service-start events in the same game minute, matching the store-step execution order.

## Why

First-title B+ research shows staff may continue another task while checkout demand exists, but the exact interruption condition is unknown. Video observations can measure specific start/interruption spans without proving a general threshold formula. Replaying those explicit spans lets downstream task arbitration be tested without promoting one observed value into a universal first-title rule.

## Safety boundary

This decision does not establish:

- a global checkout interruption threshold,
- a queue-count formula,
- an elapsed-work formula,
- a probability of interruption,
- an inferred interruption when only checkout service start is visible,
- task resume progress,
- target choice after interruption,
- platform-specific PS/SS behavior,
- sub-minute timing or video/game-time conversion.

Unobserved work interruptions remain unresolved.