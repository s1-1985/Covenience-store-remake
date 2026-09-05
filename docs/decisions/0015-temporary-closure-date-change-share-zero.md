# Decision 0015 — temporary closure is distinct from scheduled closed hours

Date: 2026-09-06

## Context

The first-title FAQ reports that if a store is in `臨時休業` when the date changes, customer share (顧客独占率) becomes 0% and the following day's arrivals can collapse. It also explicitly recommends switching to a normal `7:00–23:00` schedule late at night as a way to avoid that temporary-closure penalty, which means ordinary scheduled closed hours at midnight are **not** equivalent to `臨時休業`.

The FAQ also reports that many operating costs, including labor, stop while the store is closed, while staff may still clean/replenish and replenishment procurement can still spend cash.

Source:
- https://wikiwiki.jp/theconveni1/FAQ

## Decision

1. Add an explicit temporary-closure flag separate from `OperatingHours`.
2. Temporary closure always makes effective `store_open = False`, even if the ordinary schedule is unknown or 24h.
3. At a date change while temporary closure is active, set customer share to 0 using the first-title FAQ as the evidence source.
4. Ordinary scheduled closure at midnight does not force share to 0; it only creates the normal date-change recalculation request.
5. Reopening from temporary closure does not immediately invent a new share value; the next observed/recovered recalculation supplies it.
6. Existing closed-hours labor suppression uses the effective open state, so temporary closure suppresses labor cost too.

## Deferred

This decision does not yet block externally injected customers from being added while closed. Customer-arrival generation remains an explicit caller/observation layer until the spawn formula and exact closure gating are composed.
