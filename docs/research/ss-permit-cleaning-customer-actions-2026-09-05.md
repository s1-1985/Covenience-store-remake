# SS permit / cleaning / customer-action delta — 2026-09-05

Scope: 1997 Sega Saturn version of 『ザ・コンビニ ～あの町を独占せよ～』. This file records new implementation-relevant deltas from a detailed SS play record, with first-title Wiki cross-checks where available. Do not generalize SS-only observations to PS unless separately verified.

## Evidence labels

- `CONFIRMED-COMMUNITY-SS`: directly reported from an identified SS play record.
- `CONFIRMED-COMMUNITY-FIRST-TITLE`: first-title PS/SS Wiki statement.
- `CORROBORATED`: independently consistent first-title sources.
- `PROVISIONAL-SS`: plausible SS behavior reported by one source, pending direct screen/manual confirmation.

Primary SS source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

First-title Wiki cross-checks:
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 1. Existing-store sales permits are not a standalone action on SS

**Evidence: CONFIRMED-COMMUNITY-SS**

The SS play record explicitly reports that tobacco/alcohol/medicine permits can be changed when remodeling, but that the player cannot simply acquire only a permit without going through the remodel flow.

Implementation consequence:

```text
ExistingStorePermitChange
  entry_point = RemodelFlow
  standalone_permit_command = false   // SS-confirmed only
```

This should be combined carefully with separate PS observations showing permit application during new-store construction and during later remodeling. The safe cross-platform model is therefore:

- new construction may include permit application;
- an existing store can add permits through remodeling;
- do NOT implement a generic always-available standalone `Buy Permit` action unless PS/SS evidence is later found.

Still unresolved:
- exact permit fees;
- exact competition/exclusion distance;
- whether the same menu wording/flow is identical on PS.

## 2. Attraction cost is facility price plus land price on SS

**Evidence: PROVISIONAL-SS**

The SS record states that facility attraction costs consist of:

```text
induction_total_cost = facility_price + land_price
```

It also reports a single lump-sum payment and believes attraction succeeds reliably once paid. The author explicitly qualifies the certainty of guaranteed success, so the success rule remains provisional.

Implementation consequence:

```text
TownFacilityInductionQuote
  facility_price
  target_land_price
  total = facility_price + target_land_price
```

Do not yet hard-code `success_probability = 1.0` as a PS/SS-wide fact.

## 3. Staff break room can be placed outside the store on SS

**Evidence: CONFIRMED-COMMUNITY-SS**

The detailed SS record says the `店員控え室` can be placed outside the store building.

This is a high-value fixture-placement exception. The fixture model must not assume every staff-use fixture is interior-only.

Provisional fixture flag:

```text
StaffBreakRoom
  placement_zone = INTERIOR_OR_EXTERIOR   // SS-confirmed
```

PS needs independent confirmation before this becomes a common-console invariant.

## 4. Cleaning = 100 stops floor dirt generation on SS

**Evidence: CONFIRMED-COMMUNITY-SS**

The SS record reports that once a store's cleaning parameter reaches 100, the floor no longer becomes dirty.

This is substantially stronger than the already-known statement that high cleaning improves store condition.

Implementation candidate:

```text
if store.cleaning >= 100:
    suppress_new_floor_dirt = true
```

Important uncertainty:
- whether this is literally zero dirt-generation probability or effectively zero in observed play;
- whether PS is identical.

Until a PS/manual cross-check is obtained, keep the rule evidence-tagged rather than treating it as an unqualified shared constant.

## 5. Customer inspection and manual ejection exist on SS

**Evidence: CONFIRMED-COMMUNITY-SS**

The SS record's game-image description states that the player can inspect customer information and can manually eject a customer; the author specifically uses this against shoplifters.

This implies an explicit player-to-customer interaction path, not merely autonomous incident resolution.

Implementation requirement:

```text
CustomerContextAction
  - InspectCustomer
  - EjectCustomer
```

The customer lifecycle must therefore support forced exit/ejection as a first-class state transition:

```text
IN_STORE -> EJECTED -> EXITING -> DESPAWNED
```

Open questions:
- exact UI route/button for selecting a customer;
- what customer fields are shown;
- whether ejection can target any customer or only suspicious/shoplifting customers;
- consequences of ejecting an innocent customer;
- exact PS parity.

## 6. Bankruptcy check is reported at end-of-day on SS

**Evidence: CONFIRMED-COMMUNITY-SS**

The SS play record reports that if cash is negative at the end of the day, bankruptcy occurs at that point and the game ends.

Implementation candidate:

```text
EndOfDay:
    if cash < 0:
        trigger BankruptcyGameOver
```

This should not yet be generalized to every transient negative-balance state during a day. The observation points specifically to the day boundary.

Cross-check still required against PS/manual and the monthly skip/aggregation path.

## 7. Player-owned stores can cannibalize each other's demand

**Evidence: CORROBORATED (SS direct play + first-title Wiki strategy wording)**

The SS play record describes a persistently empty main store positioned between two player-owned branches. Reducing the operating hours of branches 2 and 3 caused customers to return to the main store. The author concluded that the branches were taking the main store's customers.

The first-title Wiki independently warns that stores placed too close compete for customers and recommends spacing stores apart. Its wording is not limited to rival-owned stores.

Implementation consequence:

`CustomerShare` / destination competition must consider nearby stores regardless of ownership, not only rival-chain stores.

```text
candidate_competing_stores = nearby open stores
// ownership does not automatically exclude a store from demand competition
```

This is important because chain expansion can reduce another branch's traffic even when total chain capacity rises.

Still unresolved:
- exact radius/weighting;
- whether same-chain competition has a different coefficient from rival competition;
- how scheduled closing changes the destination snapshot during the day.

## 8. Interior sample layout exists and is destructive/non-undoable in the observed SS flow

**Evidence: CONFIRMED-COMMUNITY-SS for existence; PROVISIONAL-SS for exact destructive semantics**

The SS record says an interior `sample` is available and useful for understanding fixture/register orientation. It also warns that after opening/applying the sample, the player could not simply undo the change, and there was no convenient `sell all` action.

UI/model implications:

- interior editing includes a sample-layout operation;
- register orientation is visually non-obvious enough that sample layouts were useful;
- baseline-faithful UI should not assume modern undo/redo or one-click clear-all existed.

Exact command labels and confirmation dialogs remain unverified.

## 9. Entrance accessibility is a practical layout invariant

**Evidence: CONFIRMED-COMMUNITY-SS observation**

The SS record notes that customers enter regardless of arbitrary interior arrangement so long as the entrance is not blocked. This supports treating entrance reachability as a hard or near-hard store-layout constraint while allowing otherwise free fixture placement.

Implementation direction:

- preserve free layout;
- validate/handle blocked entrance distinctly from ordinary congestion;
- do not over-constrain layouts simply because they are inefficient.

## 10. Current confidence / remaining gaps

Newly narrowed in this pass:
- existing-store permit acquisition flow;
- attraction-cost composition;
- a fixture placement exception (staff break room outdoors);
- an exact cleaning=100 behavioral threshold candidate;
- manual customer inspection/ejection;
- bankruptcy timing candidate;
- same-chain demand cannibalization;
- sample-layout behavior.

Still high priority:
1. exact tobacco/alcohol/medicine permit fees and exclusion distance;
2. PS confirmation for the SS-only rules above;
3. full customer-info UI fields and innocent-ejection consequences;
4. town-facility price/land-cost tables;
5. complete fixture master and placement-zone rules;
6. exact dirt-generation and cleaning formulas;
7. bankruptcy interaction with day-5-to-month-end aggregation.

Research is not complete yet; implementation can use these as evidence-tagged compatibility rules, but PS/SS-common constants should remain separated from SS-only observations until corroborated.
