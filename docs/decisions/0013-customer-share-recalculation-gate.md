# Decision 0013 — customer share recalculation is explicit; the formula stays unresolved

Date: 2026-09-06

## Context

First-title PS/SS community evidence reports that customer share (顧客独占率) depends on multiple store/environment factors, including popularity, cleaning, service, nearby population/buildings, assortment, product price, opening hours, weather and competing stores. Security may also matter but is not confirmed.

The same first-title FAQ reports two useful timing observations:

- customer share is evaluated at the date change and that value strongly affects that day's arrivals;
- an in-day weather change can cause customer share to be recalculated and arrivals to change.

Sources:

- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/FAQ

No complete original equation, coefficients, rounding rule or ordering is recovered yet.

## Decision

1. Add an explicit `CustomerShareRuntime` that stores known input context and current share.
2. Do **not** compute a share from those inputs.
3. Record date changes and known weather changes as recalculation requests.
4. Require an external observation/future recovered formula to supply the resulting share percentage.
5. Preserve unknown fields as `None`; security remains an input slot but not a confirmed active coefficient.
6. Do not automatically recalculate on popularity/cleaning/service/price changes until their exact timing semantics are recovered.

## Why

This lets the reference simulator reproduce a measured day/weather transition immediately while keeping the central customer-share black box visible. It also creates a stable place for video observations and guidebook values to land later without silently baking a guessed formula into the runtime.

## Explicit non-decisions

This decision does not determine:

- the customer-share equation;
- price elasticity;
- weather multipliers;
- main-store penalty size;
- competitor-distance weighting;
- security contribution;
- whether every non-weather input change applies immediately or only at the next scheduled recalculation;
- customer arrival counts generated from a share percentage.
