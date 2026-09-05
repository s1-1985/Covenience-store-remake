# SS layout, entrance, register orientation, and chain cannibalization evidence (2026-09-06)

## Scope

Target is the 1997 console first title, `ザ・コンビニ ～あの町を独占せよ～`, with this note limited to direct Sega Saturn play evidence. Do not promote the observations below to PS/SS-common behavior until independently confirmed on PS or in a console manual/first-title guide.

No original game images, audio, logos, or copied manual text are stored here.

## Evidence scale used in this note

- **A** — console manual / original game screen / contemporary first-title documentation with direct observable value.
- **B+** — detailed, platform-identified direct play record with substantial play time and explicit observation.
- **B** — platform-identified direct play observation, but exact internal rule remains inferred.
- **C** — secondary/community statement requiring confirmation.

## Source

### S1 — Game Yaoyorozu Retro, Sega Saturn direct-play record

- Platform explicitly identified as **SS (CD-ROM)**.
- Final play: January 2020.
- Estimated play time: **30 hours**.
- The author describes an Initial scenario run and records concrete layout and store-location behavior.
- URL: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

Evidence class for direct observations below: **B+ / DIRECT-PLAY-SS** unless otherwise noted.

## Newly recorded findings

### 1. Blocking the entrance is a meaningful layout-invalid state

S1 states that the interior layout is highly free-form, but specifically singles out **blocking the entrance** as the condition that must not be done. This is useful evidence that the first console title has at least one explicit path/access constraint at the doorway rather than accepting an entirely disconnected customer area.

**Evidence:** B+ / DIRECT-PLAY-SS

**Safe implementation consequence:**

- Model the entrance as a required customer-access node.
- Interior placement validation or customer-path validation must be able to detect an entrance obstruction.
- Do **not** yet assume that every shelf or fixture must be reachable by a modern pathfinding connectivity test; S1 only gives a strong anchor for the entrance itself.

**Still unknown:**

- Whether the game refuses confirmation when the entrance is blocked, allows confirmation but produces zero entry, or applies another penalty.
- Exact entrance footprint and passable cells for every store orientation/size.
- PS behavior.

### 2. Register orientation changes the side/direction from which customers queue

S1 reports that the cash register has a visually non-obvious orientation; when placed facing the opposite way from intended, customers line up on the opposite side/direction.

This is stronger than merely saying that registers have sprites with rotation. Customer queue geometry actually depends on the fixture orientation.

**Evidence:** B+ / DIRECT-PLAY-SS

**Safe implementation consequence:**

A register fixture should expose at least:

```text
orientation
service_position_or_edge
queue_entry_position_or_edge
```

Do not implement registers as rotationally cosmetic fixtures with a direction-independent queue anchor.

**Still unknown:**

- Number of legal register rotations in each store orientation.
- Exact queue anchor offset/cells.
- Whether queue growth direction is fixed or path-selected after the first anchor.
- PS behavior.

### 3. Built-in sample layouts exist and loading one has destructive/non-trivial editing consequences

S1 explicitly uses an included layout sample and later notes that opening/loading the sample is not trivially reversible; the author also complains that there is no convenient single operation to sell all placed interior items at once.

A separate older review of the first title also independently mentions game-provided sample layouts and recommends loading one and modifying it for inexperienced players:
https://ameblo.jp/freeagent/entry-10008302250.html

Because the latter review page does not clearly identify the console platform in the retrieved text, it is used only as supporting context and **not** to promote an SS observation to PS/SS-common status.

**Evidence:**

- Sample-layout existence: **B+ / DIRECT-PLAY-SS**, with secondary corroboration.
- Exact undo/destructive semantics: **B / DIRECT-PLAY-SS** pending screen/manual confirmation.

**Safe implementation consequence:**

- The original UI must include a sample-layout loading path in the interior workflow.
- Do not add an assumed modern undo stack to the fidelity layer until the original behavior is established.
- Keep `load sample`, `sell/remove fixture`, and `restore previous layout` as separate research questions.

**Still unknown:**

- Complete sample list and which samples are offered for each store size/orientation.
- Whether sample loading immediately commits, overwrites a working buffer, or becomes irreversible only after a later confirmation step.
- Exact resale ratio and whether a hidden bulk-sell operation exists elsewhere.

### 4. Player-owned stores can cannibalize one another's customer demand

In S1's SS Initial run, the central main store became severely under-visited despite changes to interior, staff, price, assortment, nearby induced facilities, and a five-star evaluation. The author reports that shortening the business hours of the second and third stores caused customers to return to the main store, and interprets the original placement between those two branches as the cause.

This is strong behavioral evidence that **player-owned stores are not independent demand generators**. At least some portion of local demand is competed for among stores of the same chain.

**Evidence:** B / DIRECT-PLAY-SS

The existence of the observation is direct, but the internal algorithm is inferred; exact catchment radius and allocation formula are unknown.

**Safe implementation consequence:**

Do not implement customer generation as:

```text
customers_for_store = local_population * store_attractiveness
```

independently for every player store with no competition term.

The simulation architecture should permit a shared/local demand pool such as:

```text
local_demand -> candidate open stores -> attraction/availability allocation
```

where player branches and rivals can potentially compete for the same population. The exact formula must remain data-driven/replaceable.

Also, store operating hours must affect eligibility for that demand pool: closing/shortening one branch can redirect potential customers to another open branch.

**Still unknown:**

- Whether the allocation runs per customer, per building/population source, per map tile, or as an aggregate daily/time-slice calculation.
- Distance falloff function.
- Interaction with popularity, price, assortment, store rating, parking, permits, and store size.
- Whether rival stores and player stores use the same competition formula.
- PS behavior.

## Related observations deliberately not promoted here

S1 also describes other behaviors already represented elsewhere in research, including advertising choices, nearby police/fire-station security effects, rival-store survey cost, bankruptcy after a negative settlement, floor dirt/cleaning, parking connectivity, and slow town growth. These are not duplicated as new findings in this note.

## Implementation status after this pass

### Safe to model structurally now

- Entrance access as a first-class customer path node.
- Register orientation with orientation-dependent service/queue anchors.
- Sample layouts as explicit original-UI data, not merely developer presets.
- Shared demand/catchment competition that can include the player's own branches.
- Operating-hours eligibility in customer allocation.

### Not safe to freeze numerically yet

- Exact path-validation rules.
- Queue-cell offsets and queue-length mechanics.
- Sample-layout contents.
- Store catchment radius.
- Customer-attraction equation.
- Same-chain vs rival weighting.
- Any PS/SS-common assertion for these findings.

## Research completion impact

This closes several **structural** unknowns in interior/customer simulation, but does not materially close the major numeric gaps (complete goods/fixtures/staff tables, store dimensions/prices, permit fees/distances, town-building population values, and economy equations). Full fidelity implementation remains premature for final tuning, although the relevant engine interfaces can now be designed to preserve these behaviors.
