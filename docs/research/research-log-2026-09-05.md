# Research Log — 2026-09-05

Scope: first home-console 『ザ・コンビニ ～あの町を独占せよ～』 (PS/SS, 1997). Avoid mixing sequel-only data unless explicitly marked as comparison evidence.

## A. Store-opening sequence is becoming clear

Multiple first-title retrospectives independently describe the opening flow as:

1. choose land/location,
2. decide whether to obtain regulated sales permits,
3. choose store size/type,
4. hire one manager + two employees,
5. place register/rest room/fixtures/products,
6. set business policy and open.

The three regulated merchandise groups repeatedly identified are:
- tobacco,
- alcohol,
- medicine/pharmaceuticals.

First-title sources:
- https://codevis.nobody.jp/review-ps/the_convini.html
- https://sinsasinsa.client.jp/index-game-2-ps1-9.htm
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

Confidence: **CONFIRMED-COMMUNITY (multi-source)**.

## B. Exact selectable business-hour presets found

A first-title PS review records six selectable schedules:

- 24 hours
- 07:00–23:00
- 10:00–18:00
- 10:00–02:00 next day
- 12:00–04:00 next day
- 19:00–11:00 next day

Source:
- https://codevis.nobody.jp/review-ps/the_convini.html

Confidence: **CONFIRMED-COMMUNITY**, pending direct visual/manual verification.

Implementation implication: business hours are probably a fixed preset enum in the original, not arbitrary open/close time pickers. Do not implement a free-form scheduler in the baseline unless later evidence contradicts this.

## C. Price/profit controls

The same first-title review states:
- profit rate can be adjusted by merchandise item/category,
- a bulk/all-products setting also exists.

Source:
- https://codevis.nobody.jp/review-ps/the_convini.html

Confidence: **CONFIRMED-COMMUNITY**, exact min/max/step still unknown.

## D. Live HUD and city-map information — visual evidence

A preserved PS screenshot shows the city map behind a store-selection modal. The top HUD visibly contains:
- game year/month/day,
- weather,
- time,
- current cash.

One screenshot shows the initial state as roughly:
- Year 01 / Jan 01
- clear weather
- 00:00
- ¥180,000,000 cash

The store-selection modal in that screenshot displays a ¥6,000,000 figure for the currently highlighted store option.

Another preserved original screenshot shows building hover/info text:
- `役所`
- `買い物人口 250人`

This establishes that buildings have an explicit `shopping population` value exposed to the player, rather than nearby demand being entirely hidden.

Visual sources:
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://dengekionline.com/elem/000/000/722/722931/

Confidence: **CONFIRMED-VISUAL**.

## E. Store-view UI / modal-window style — visual evidence

Original PS screenshots show:
- a top-down 2D store grid,
- tiny autonomous customers and staff rendered in the live store,
- management dialogs layered over the live store rather than replacing it with a totally separate screen,
- a product-selection dialog using a 4×3 icon grid in at least one captured state,
- visible text `商品を選択して下さい` and selected category `調味料類`.

Source:
- https://dengekionline.com/elem/000/000/722/722934/

Confidence: **CONFIRMED-VISUAL**.

Important design implication: the remake should preserve the feeling of manipulating the business while still seeing the simulated store underneath. On Android this can be translated into touch-friendly sheets/modals, but the live simulation should remain visually central.

## F. Customer direct intervention: `つまみだす`

Multiple first-title play records describe selecting a customer / viewing customer information and manually ejecting the customer (`つまみだす`). Players use this against thieves or troublesome customers, and one source explicitly describes customer info as viewable.

Sources:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://www.gavas.jp/products/detail.php?product_id=9180

Confidence: **CONFIRMED-COMMUNITY (multi-source)**.

Implementation implication: individual customer entities are not merely visual particles. They need selectable identity/state sufficient for a customer-info interaction and manual ejection.

## G. Layout reuse

A period player account states that a completed interior layout can be saved and reused when constructing the next store.

Source:
- https://ameblo.jp/freeagent/entry-10008302250.html

Confidence: **PROVISIONAL / single-source** until manual confirmation.

This is important because it changes multi-store play from repetitive rebuilding into template reuse.

## H. Store staffing count

Independent first-title sources agree on:
- 1 manager
- 2 employees
- 3 people per store

Sources:
- https://sinsasinsa.client.jp/index-game-2-ps1-9.htm
- https://ameblo.jp/freeagent/entry-10008302250.html

Confidence: **CONFIRMED-COMMUNITY (multi-source)**.

## I. Additional first-title behavioral notes worth verifying

From first-title records:
- One day's cash ending below zero causes bankruptcy/game over.
- Tobacco/alcohol/medicine permissions may only be obtainable during construction/remodeling, not as a standalone action. This is reported for the SS version and needs PS/manual verification.
- Staff break rooms can be placed outside the shop.
- Parking can function even without an obvious pedestrian connection.
- If cleanliness reaches 100, one play record reports that the floor stops becoming dirty.

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

Confidence: **PROVISIONAL**, verify individually.

## J. Research source discovery: original-era guidebooks

Two potentially high-value printed sources have been identified.

### 1. 『ザ・コンビニ あの町を独占せよ パーフェクトガイド』
- Publisher: Shogakukan
- Publication year: 1996
- 152 pages
- ISBN: 9784093850803

Bibliographic source:
- https://www.books.or.jp/book-details/9784093850803

This appears associated with the 1996 PC original, so it is useful for system lineage but must not be blindly treated as PS/SS data.

### 2. 『ザ・コンビニ ～あの町を独占せよ～ レイアウトデザインセレクション74』
- CB's Project
- Published: 1997-04
- 95 pages
- ISBN: 9784889914344
- Contents reportedly include: quick reference, interior-layout kit usage, personal layout designs, strategy/data book, technique guide, data lists.

Bibliographic source:
- https://books.rakuten.co.jp/rb/880163/

This is particularly promising for reconstructing PS-era layout rules and data tables. If a legal accessible copy/page preview can be found, prioritize it.

## K. Important contamination warning: sequel data

Search results for 『ザ・コンビニ2』 are much richer than for the first title, and many fixture tables online are sequel-only. Some values are similar but not identical.

Example: sequel fixture data lists plant/bench/fountain values that differ from the first-title Wiki's values. Therefore:

**Do not import Conveni 2 fixture/product numbers into the baseline data unless direct first-title evidence supports them.**

First-title source of record for currently known fixture values:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

## L. Next research sprint

Highest priority:
1. Extract the PS manual screen-by-screen / page-by-page.
2. Identify every original top-level command and submenu.
3. Build a first-title-only product/fixture matrix with source per row.
4. Determine exact store types/tile dimensions from first-title evidence.
5. Determine customer archetypes and shopping-population mapping by building.
6. Determine customer patience/anger/queue logic.
7. Determine staff autonomous task priority.
8. Verify price/profit-rate min/max/step.
9. Verify exact scenario names, starting cash, victory conditions and hidden mode unlock.
10. Separate PS/SS differences where they exist.
