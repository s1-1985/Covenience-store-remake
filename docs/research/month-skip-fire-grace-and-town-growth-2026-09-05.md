# Month-skip, early-fire grace, and town-growth anchors — 2026-09-05

Scope: first PlayStation / Sega Saturn title only. This note records newly isolated details from the first-title PS/SS Wiki and PS play records. No copyrighted game assets or long verbatim text are stored here.

## Evidence labels used here

- `CONFIRMED-COMMUNITY-PS/SS`: first-title Wiki explicitly scoped to PS/SS and internally consistent with other evidence.
- `DIRECT-PLAY-PS`: detailed PS play record.
- `PROVISIONAL-COMMUNITY`: useful observation but not sufficiently exact/reproducible to hard-code as a formula.

## 1. Month skip does not apply a full-month popularity decay

Source: first-title PS/SS FAQ.

The first four days of a month are simulated in real time, and day 5 through month end is skipped/aggregated. The FAQ additionally states that during this skipped period the popularity parameter is reduced only by the equivalent of one day, not repeatedly for every skipped calendar day.

Evidence: `CONFIRMED-COMMUNITY-PS/SS`

Implementation consequence:

```text
MonthSkipResult
  simulated_days = 4
  skipped_days = calendar_days_in_month - 4
  popularity_decay_application_count = 1   // current best evidence
```

Do NOT implement the month skip as a naïve loop that applies the ordinary daily popularity decay once for every skipped day. Other economy/traffic aggregation rules are still unresolved and must not be inferred from this one parameter.

Source:
- https://wikiwiki.jp/theconveni1/FAQ

## 2. Fire appears suppressed during an initial grace period

The same FAQ notes that even with security below 100, fire does not appear to occur during the first several months of a game. The Wiki does not define the exact month count.

Evidence: `PROVISIONAL-COMMUNITY`

This is distinct from the better-established rule that security below 100 leaves the store exposed to fire, including at security 99. Therefore a plausible model is:

```text
FireRisk
  if scenario_age < unknown_initial_grace_period:
      effective_probability ~= 0
  else:
      probability increases when store_security < 100
```

The exact start month, probability curve, and whether robbery shares the same grace period remain unknown. Do not hard-code a numeric grace duration yet.

Source:
- https://wikiwiki.jp/theconveni1/FAQ

## 3. Store enlargement increases required operating parameters

The first-title strategy page explicitly warns that enlarging a store raises the required parameter levels and can make the store harder to operate, including increasing the chance of fire if security can no longer be maintained. It also states that the revenue gain from enlargement may be only about 1.5x in the observed strategy context.

Evidence: `CONFIRMED-COMMUNITY-PS/SS` for the qualitative requirement increase; `PROVISIONAL-COMMUNITY` for the approximately 1.5x revenue observation.

Implementation consequence:

Store size must not be represented only as more floor area and more fixture capacity. The store-size definition should be able to affect target/required operating parameters, for example:

```text
StoreSizeDefinition
  id
  editable_width
  editable_height
  construction_cost
  remodel_cost
  cleaning_requirement_scale
  security_requirement_scale
  service_requirement_scale?   // still unverified
```

The exact scaling formula is not yet recovered.

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 4. Town population naturally plateaus around 15,000 without induction in beginner strategy

The first-title Wiki's beginner strategy says that if the player does not repeatedly induce facilities, town population growth becomes very slow at roughly 15,000 people. The same page recommends universities as the best cost-performance induction target for pushing toward the 20,000-population metropolitan-government condition.

Evidence: `PROVISIONAL-COMMUNITY`

This is not proof of a hard-coded cap of 15,000. It is an observed development plateau and should be modeled as evidence that autonomous town growth weakens substantially before the beginner victory threshold.

Implementation consequence:

Do not implement population as a constant linear monthly increase. Town growth should be able to slow as development matures and then receive discrete boosts from induced/autonomously spawned facilities.

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 5. Two station slots and a dedicated civic-building site are strongly suggested

The strategy page states that stations can later appear at two rail locations, one on the left and one on the right, and that the open civic site in the lower-left area later receives city hall / metropolitan-government development.

Evidence: `CONFIRMED-COMMUNITY-PS/SS` as map-structure observation; exact scenario-specific trigger sequence remains unresolved.

This strengthens a location-constrained town-building model rather than treating all automatic facilities as freely placeable.

Suggested structure:

```text
TownSpecialSiteDefinition
  id
  site_type            // station_slot, civic_site, etc.
  fixed_map_position
  allowed_buildings
  trigger_condition
  scenario_mask
```

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 6. New-shop priority is partly driven by land-price inflation, not only chain-count goals

The strategy page records land that can cost roughly 20 million yen early later exceeding 100 million after about two years. This was already known as an observation, but the page explicitly connects that inflation to the recommendation to open branches before spending heavily on enlargements.

Evidence: `PROVISIONAL-COMMUNITY`

This reinforces the need for dynamic land pricing tied to town development/time rather than a static lot-price table. Exact formula remains unknown.

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 7. Existing PS remodel evidence remains consistent

A detailed PS play record independently states that remodeling an existing store to medium size costs 12,000,000 yen and describes postponing alcohol/medicine permits until the medium-store remodel because cash was scarce.

Evidence: `DIRECT-PLAY-PS`

This remains a remodel-cost anchor only; it does not prove that a newly constructed medium store costs exactly 12,000,000 yen.

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

## Unresolved items after this pass

- Exact daily popularity decay amount and whether all causes of popularity loss share the month-skip exception.
- Exact initial fire grace duration and whether robbery/shoplifting share it.
- Store-size requirement scaling formula.
- Full six-store price/dimension table.
- Exact autonomous population-growth equation and building spawn probabilities.
- Exact triggers for both station slots and the civic-site transition sequence.
- Exact land-price evolution formula.
- Permit fees and exclusion distance for tobacco/alcohol/medicine.

## Implementation readiness impact

These findings are useful enough to shape interfaces and state transitions now, especially `MonthSkipResult`, `FireRisk`, `StoreSizeDefinition`, and fixed town special sites. They are not sufficient to freeze the economic formulas. Full production implementation should still keep these values data-driven and replaceable while research continues.
