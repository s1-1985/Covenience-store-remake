# Decision 0014 — promotion effects occur at fixed events, not immediately

Date: 2026-09-06

## Context

Already-merged first-title research records five regular promotion methods with fixed monthly event times:

- direct mail: +12 at day 2 10:00
- newspaper: +20 at day 2 07:00
- airship: +30 at day 3 15:00
- radio: +50 at day 1 17:00
- TV: +100 at day 1 19:00

Each method can be used once per month, multiple different methods can be combined in the same month, the effect applies to owned stores, and popularity is capped at 100.

Source of record:
- `docs/research/promotion-event-schedule-2026-09-05.md`
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D

The payment timing, late same-month scheduling behavior, cancellation behavior and some target-store edge cases remain unresolved.

Update: Decision 0032 later resolves payment-at-trigger for direct mail only. The remaining methods and edge cases stay unresolved.

## Decision

1. Model regular promotions as scheduled events with fixed day/hour timestamps.
2. Do not apply popularity at selection time.
3. Enforce one scheduled use per method per month.
4. Allow different methods in the same month.
5. Apply the known popularity gain only when the event fires, capped at 100.
6. Require the caller to supply the current eligible target-store list at application time.
7. Do not debit cash in this scheduler until the original payment timing is recovered.
8. Reject same-month scheduling after a method's known event time and cross-month advance booking as unresolved rather than inventing a behavior.

## Deferred

The idol one-day-owner event is intentionally not composed here. Its 10,000-total-visitor threshold and next-day 00:00 effect are documented, but the interaction with representative day 4 -> month-end skipping still needs an explicit calendar decision before implementation.
