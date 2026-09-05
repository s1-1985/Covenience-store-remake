# Decision 0023 — Keep customer purchase choice behind a replaceable policy

Date: 2026-09-06

## Decision

Customer product choice is not implemented as a fixed random table or a modernized utility-maximizing AI. The reference simulation exposes a replaceable purchase-policy boundary that receives the customer's current merchandise stop, current basket state, and the in-stock offers at that fixture.

The policy may:

- buy one supplied offer with an explicit quantity,
- explicitly skip the current merchandise stop,
- or return no decision and leave the customer waiting at the current stop.

Sale price and checkout/self-service flow belong to caller-supplied merchandising data, not to the customer policy. A policy therefore cannot invent a different price or silently convert a staffed-checkout product into self-service.

## Why

First-title research supports several qualitative facts but not the original equation:

- products may differ between primary-destination and add-on purchase roles,
- customer groups appear to differ in spending power and product affinity,
- fixture attention may affect add-on purchases,
- event products appear price-sensitive for younger customers.

The exact weights, budget distribution, primary/add-on probabilities, fixture-attention effect, price elasticity, and quantity rules remain unresolved. Hard-coding any of those now would turn a research oracle into an invented remake balance model.

Source summary:

- `docs/research/customer-purchase-role-merchandising-2026-09-05.md`
- `docs/decisions/0005-guide-ready-master-schema.md`
- `docs/decisions/0011-explicit-purchase-baskets-without-choice-ai.md`

## Explicit no-purchase transition

The customer lifecycle now has an explicit transition for leaving a visited merchandise fixture without buying. This is infrastructure only. It does not assert how frequently original customers browse without purchasing.

A no-purchase transition:

- does not change inventory,
- does not add a basket line,
- does not mark the fixture as a purchased/interacted fixture,
- only advances the already supplied merchandise route.

## Validation boundary

The coordinator only exposes offers whose inventory slot:

- belongs to the fixture the customer has actually reached,
- currently has stock greater than zero.

A purchase decision must reference one of those offers and cannot exceed current stock. The existing store-runtime guards still enforce staffed-checkout requirements and inventory mutation rules.

## Still unresolved

- primary destination selection,
- add-on selection probability,
- product weights,
- customer archetype preferences,
- spending-power/budget distribution,
- fixture attention formula,
- price elasticity,
- multi-unit purchase distribution,
- repeated purchases from one fixture,
- whether all planned merchandise stops represent intention, browsing, or both.

These remain replaceable policy/master-data concerns until video or guide evidence resolves them.
