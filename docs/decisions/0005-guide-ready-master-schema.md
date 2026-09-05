# Decision 0005 — Make master tables guide-ready before guide arrival

Date: 2026-09-05

## Decision

Add nullable, evidence-tagged schema slots for product, customer-archetype and remaining fixture-master fields now, before the ordered strategy guides arrive.

## Why

The next major research jump is expected to come from strategy-guide data lists. Without a stable schema, every photographed table would first require deciding where each value belongs. Defining the slots now lets guide extraction become a data-entry/verification task rather than another architecture task.

## Fixture fields added

- purchase price
- capacity
- compatible product categories
- interaction sides
- attention
- security bonus

Existing fields such as footprint, maintenance, service, parking capacity and pedestrian blocking remain.

## Product master slots

- display name
- category
- temperature zone
- procurement cost
- standard retail price
- compatible fixtures
- required permit
- primary-purchase eligibility
- add-on-purchase eligibility
- audience affinities

No product row is fabricated merely to fill the schema.

## Customer-archetype slots

- display/visual archetype
- origin-building affinities
- spending-power profile
- preferred primary products
- preferred add-on products
- patience profile
- anger profile

Qualitative evidence may fill individual fields later while all numerical behavior remains unknown.

## Completeness audit

`master_audit.py` defines the minimum fields that currently block implementation for fixtures/products and the research fields sought for customer archetypes. A field counts as known only when it contains an `EvidenceValue`; plain untagged values are rejected by the audit.

This makes future progress reports reproducible from actual populated master fields instead of subjective row counts.

## Important rule

`None` remains the canonical unknown value. Missing guide data must never be converted to zero, sequel data or an unlabeled guess.
