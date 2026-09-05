# SS early-store operations and acquisition evidence (2026-09-06)

Scope: 1997 Sega Saturn version of **The Conveni: Ano Machi o Dokusen Seyo** only unless otherwise stated. This note deliberately does not import rules from The Conveni 2/3/4/200X.

## Evidence scale used here

- `DIRECT-PLAY-SS`: explicit statement in a play record that identifies the Saturn version.
- `CORROBORATED-SS`: two or more Saturn/first-game sources agree on the behavior.
- `PROVISIONAL-SS`: plausible observation from one Saturn play record, but wording or exact mechanics leave room for interpretation.
- `UNCONFIRMED-PS`: no PS confirmation has yet been collected for the same behavior.

Primary source for this pass:

- 2008 Saturn play diary, "ザ・コンビニ（ＳＳ）", *レトロゲームが好き、とミーコは言った。*  
  https://mii5.seesaa.net/article/200802article_5.html

Useful cross-check source already used elsewhere in this repository:

- First-game dedicated Wiki, staff page  
  https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 1. Beginner scenario initially restricts the player to the smallest store

**Finding:** In the Saturn beginner scenario, the player first chooses a store type, and the play diary explicitly records that only the smallest shop can be built at the beginning; larger shops are not yet available.

- Evidence: `DIRECT-PLAY-SS`
- PS status: `UNCONFIRMED-PS`
- Important limitation: this does **not** establish the exact unlock condition for medium/large stores, nor whether the restriction applies to every scenario. Existing PS advanced-scenario evidence shows a medium store can be opened immediately in that scenario, so availability must not be modeled as a single global progression lock.

### Implementation consequence

Use scenario/start-state-aware availability, e.g.:

```text
ScenarioStoreSizeAvailability {
  scenario_id
  phase_or_condition
  allowed_store_sizes[]
}
```

Do not hard-code `small only until X months` without stronger evidence.

## 2. Store footprint/orientation has two selectable directions

**Finding:** During Saturn store creation, the diary records two orientations: vertical and horizontal.

- Evidence: `DIRECT-PLAY-SS`
- PS status: `UNCONFIRMED-PS`
- Exact tile dimensions remain unknown.

### Implementation consequence

A store definition should support at least two rotated orientations instead of treating each apparent shape as a separate store class. Until exact grids are recovered, preserve orientation separately from size.

```text
StorePlacement {
  size_class
  orientation: VERTICAL | HORIZONTAL
  footprint: unresolved
}
```

## 3. Default operating-hours example: 07:00-23:00; 24-hour operation can change the observed customer mix

The diary opens its first shop from 07:00 to 23:00. Later, after expanding the main shop and seeing weak traffic, the player changes to 24-hour operation and reports a large group arriving around 02:00, with a noticeably different customer mix (many middle-aged men) and increased sales of alcohol/underwear.

### What is supported

- Opening hours are player-configurable and can include 07:00-23:00 and 24-hour operation. `DIRECT-PLAY-SS`
- Customer composition and/or demand is time-of-day sensitive; nighttime trading can expose demand not visible under shorter hours. `DIRECT-PLAY-SS`

### What is **not** yet proven

- Whether changing the opening-hours setting itself directly modifies customer archetype weights.
- Exact hourly arrival curves.
- Exact demographic-to-product preference tables.

The safe model is therefore a time-of-day demand system, not a magical `24h customer bonus`.

## 4. Customers dirty the store; staff clean it

The Saturn diary directly states that customer entry makes the shop dirty and that employees perform cleaning. Early low-skill staff clean slowly because they are also occupied with replenishment and other tasks.

- Evidence: `DIRECT-PLAY-SS`
- Consistency: aligns with the first-game Wiki's use of a cleaning parameter and with other first-game play records.

### Implementation consequence

Dirt should be generated from store/customer activity, while staff cleaning reduces it over time. A simple static daily dirt penalty would not reproduce the observed in-store workload competition.

Candidate structure:

```text
on_customer_activity -> add_dirt(amount unresolved)
staff task scheduler -> CLEAN when required
cleaning skill -> cleaning throughput / cap (exact formula unresolved)
```

## 5. Player can manually replenish merchandise

The diary explicitly notes that the player can replenish products manually and uses this to help low-skill employees who are struggling with cleaning and replenishment.

- Evidence: `DIRECT-PLAY-SS`
- PS status: `UNCONFIRMED-PS`

This is important because replenishment is not purely a staff-AI action. The remake needs a player intervention path distinct from automatic staff replenishment.

Potential command/state split:

```text
ReplenishmentSource = STAFF_AI | PLAYER_MANUAL
```

Exact UI hierarchy and whether manual replenishment consumes time/money beyond stock cost remain unresolved.

## 6. Keeping customers waiting can provoke anger and staff-parameter loss

The Saturn diary reports a queue, then notes that if customers are kept waiting too long they become angry, followed by an observed employee parameter decrease.

- Evidence: `PROVISIONAL-SS`
- Reason for provisional status: the causal chain is strongly implied by the diary but the exact parameter affected, amount, target employee, and trigger threshold are not shown.

### Implementation consequence

Do not yet encode a fixed numeric penalty. Preserve an event hook:

```text
CustomerPatienceExpired -> CustomerAngerEvent
CustomerAngerEvent -> possible StaffParameterPenalty (parameter/value unresolved)
```

This should be reconciled with existing customer-patience research before numerical implementation.

## 7. Acquiring a rival store can preserve its operational state, including staff

A particularly useful Saturn observation appears when the player buys a rival store as the fourth branch. The player reports enlarging the register but otherwise using the acquired shop as-is, and explicitly states that the staff are also retained and can be used immediately.

- Evidence: `DIRECT-PLAY-SS`
- PS status: `UNCONFIRMED-PS`

### Strongest supported interpretation

A rival-store acquisition is not simply `delete rival store -> create blank player store`. At minimum, the acquired store can retain a substantial part of its existing state, and in this observed case its employees remain assigned after ownership changes.

### Still unresolved

- Whether all fixtures and inventories are always inherited.
- Whether every acquired employee becomes permanently part of the player's 35-person hiring pool or is merely reassigned under the hood.
- Whether employee pay/skills are unchanged.
- Whether the register had to be replaced because of capacity/size constraints or was merely a player choice.

### Implementation consequence

Model acquisition as ownership transfer of a store entity, then apply only confirmed conversion rules, rather than recreating the store from scratch.

```text
acquire(rival_store):
  store.owner = player
  preserve(layout?)
  preserve(staff_assignments = observed true on SS)
  preserve(inventory? unresolved)
  preserve(store_parameters? unresolved)
```

## 8. Expansion is not automatically beneficial

After expanding the main shop to improve assortment, the player reports falling sales and reduced traffic, while noting that small stores have lower running costs. This confirms that expansion carries an operating-cost/demand-management trade-off rather than being a strict upgrade.

- Evidence: `DIRECT-PLAY-SS`
- Exact cost model: unresolved.

This complements existing first-game Wiki evidence that larger stores are harder to maintain and can require stronger staff parameters. Do not implement store size as a monotonic multiplier to profit.

## 9. Town-growth / beginner ending cross-check

The same Saturn run reports town population stalling around 19,000, followed later by the metropolitan government building appearing and the beginner scenario ending. This is consistent with existing research that the beginner objective is tied to the town reaching roughly 20,000 population and the government building arriving, but it does not refine the `>= 20,000` vs `> 20,000` boundary.

- Evidence: `CORROBORATED-SS` with existing first-game research
- No new threshold value committed.

## New confirmed/provisional items from this pass

| Item | Status | Platform | Notes |
|---|---|---|---|
| Beginner starts with smallest store only | DIRECT-PLAY-SS | SS | unlock condition unknown |
| Store orientation has vertical/horizontal choices | DIRECT-PLAY-SS | SS | exact footprint unknown |
| 07:00-23:00 and 24h schedules are selectable | DIRECT-PLAY-SS | SS | full schedule UI unknown |
| Nighttime changes observed customer/demand mix | DIRECT-PLAY-SS | SS | exact AI weights unknown |
| Customer activity creates dirt | DIRECT-PLAY-SS | SS | dirt formula unknown |
| Player can manually replenish stock | DIRECT-PLAY-SS | SS | exact menu location unknown |
| Waiting too long can cause anger and apparent staff-parameter loss | PROVISIONAL-SS | SS | threshold/parameter/value unknown |
| Rival-store acquisition can retain staff | DIRECT-PLAY-SS | SS | precise inheritance rules unknown |
| Larger store can have worse economics than a small store | DIRECT-PLAY-SS | SS | exact operating-cost formula unknown |

## Priority follow-ups

1. Confirm on PS whether beginner also starts with only the smallest store and whether the same two orientations are offered.
2. Recover the exact unlock rule for medium/large stores by scenario or progression state.
3. Identify the manual-replenishment UI path and whether it has any special cost/time rule.
4. Test acquisition inheritance separately for fixtures, inventory, staff, staff skills/pay, popularity, security/cleaning and sales history.
5. Recover the customer anger threshold and the exact employee parameter penalty.
6. Derive hourly customer-archetype/demand curves from direct footage or repeated controlled play.

## Copyright / repository hygiene

No original screenshots, audio, logos, manual scans, or copied long-form game text are stored in this repository. Only paraphrased observations, implementation implications, source URLs and evidence levels are recorded.
