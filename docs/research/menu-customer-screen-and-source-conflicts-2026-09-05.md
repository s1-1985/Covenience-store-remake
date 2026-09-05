# Menu, customer-screen, and source-conflict evidence — 2026-09-05

Scope: first home-console title only, 1997 PS/SS『ザ・コンビニ ～あの町を独占せよ～』. Do not promote sequel/PC values into this baseline.

## Evidence scale used here

- **CONFIRMED-VISUAL-PS**: directly readable from a PS screenshot.
- **DIRECT-PLAY-PS**: detailed play record explicitly for PS.
- **DIRECT-PLAY-SS**: detailed play record explicitly for SS.
- **CONFIRMED-COMMUNITY-PS/SS**: first-title PS/SS-specific Wiki or corroborated detailed community data.
- **PROVISIONAL**: useful observation, but exact value/causality is not yet safe to hard-code.
- **CONFLICT**: sources disagree; implementation must stay configurable until resolved.

## 1. Top-level / management command evidence

The exact complete command tree remains unresolved, but the following command names and relationships are now directly supported.

| Command / path | Evidence | Notes |
|---|---|---|
| `内装` | DIRECT-PLAY-SS | Interior layout is a first-class management command. A sample layout can be opened. |
| `店員の雇用` | CONFIRMED-COMMUNITY-PS/SS | Hiring screen exposes salary/stamina/academic/agility/sociability. |
| `店員の異動` | CONFIRMED-COMMUNITY-PS/SS | Transfer/assignment screen exposes operational skills including education/register/replenishment/security/cleaning/service. |
| `営業方針` | DIRECT-PLAY-SS / DIRECT-PLAY-PS | Used alongside interior and staff management; price/profit-rate settings are part of operating policy. |
| `販促` | DIRECT-PLAY-SS | Top-level command used for spending money on store/town benefits. |
| `販促 → 宣伝` | CONFIRMED-COMMUNITY-PS/SS | Advertisement submenu contains DM/newspaper/airship/radio/TV. |
| `販促 → 誘致` | DIRECT-PLAY-SS | Facility induction/attraction is operated from promotion. |
| `調査` | DIRECT-PLAY-SS / CONFIRMED-COMMUNITY-PS/SS | Opens store/business information screens. |
| `調査 → 全店収支グラフ` | CONFIRMED-COMMUNITY-PS/SS | Displays owner overall rating used by Advanced clear condition. |
| `調査 → 店舗売上成績` | DIRECT-PLAY-SS | Per-store sales performance screen. Exact Japanese label still needs visual confirmation. |
| `調査 → 売れ筋・欲しかった商品アンケート` | DIRECT-PLAY-SS | Used to detect missing products and stockouts. Exact label needs visual confirmation. |
| `調査 → ライバル店調査` | DIRECT-PLAY-SS + PS corroboration | Costs 500,000 yen; shows basic rival data such as hours/revenue, not interior layout. |

Implementation consequence: build the UI command layer as a hierarchical command graph rather than as independent smartphone pages. Labels marked as description-level evidence should remain data-driven until the manual/original screen provides exact wording.

Sources:
- first-title Wiki: https://wikiwiki.jp/theconveni1/
- staff: https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- game modes: https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- SS play record: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 2. Customer inspection is an explicit player action

The SS play record includes an original-game screenshot and description stating that customer information can be viewed and that the player can `つまみ出す` a customer. The same record describes using this action against shoplifters.

**Evidence: DIRECT-PLAY-SS with screenshot context.**

Minimum baseline interaction model should therefore allow:

```text
SelectCustomer
  -> CustomerInfo
       - customer identity/archetype data (exact fields unresolved)
       - current purchase contents / shopping state (field list unresolved)
       - EjectCustomer action
```

Do not model customers as purely passive simulation entities hidden from the player.

A separate older play account reports that selecting customers reveals what they are buying and that apparently innocent customers can also be ejected, but its platform is not explicit enough for PS/SS baseline promotion. Treat that as **PROVISIONAL** only until a PS/SS-specific screen/manual confirms the exact fields and side effects.

Source:
- SS play record/screens: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 3. Customer archetype observations

The SS play record explicitly observes visually repeated groups including middle-school students, salaried workers, housewives/madams, elderly men, adults with children, and a visually sweaty group. It also says different stores show different customer tendencies.

**Evidence: DIRECT-PLAY-SS, qualitative only.**

Implementation consequence: keep `CustomerArchetype` and store/location demand mix data-driven. Do not collapse all visitors into one demand profile. Exact archetype list, sex/age labels, purchase weights, spawn weights, and building origins remain unresolved.

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 4. Strong PS visual anchor: store-selection modal and initial cash context

A surviving PS screenshot shows the live town map with a modal titled `店舗を選んで下さい`, six store icons, date/time/weather/money in the upper HUD, and the currently selected store price displayed as `¥6,000,000`.

**Evidence: CONFIRMED-VISUAL-PS.**

The screenshot shows `01年目 01月01日 [快晴] 00:00` and cash `¥180,000,000`. Because Beginner is known to start with 200,000,000 yen and land purchase can occur before store selection, the 180,000,000 cash value must **not** be treated as a scenario-start balance. The safe visual facts are:

- town map remains visible behind the store-selection modal;
- six store icons are presented in one selector;
- selected option can show a 6,000,000-yen store price;
- persistent HUD includes year/month/day, weather, clock, and cash.

Source:
- https://www.gavas.jp/products/detail.php?product_id=9180
- image: https://www.gavas.jp/upload/save_image/9180_2.jpg

## 5. Security / fire causality conflict — prevent a bad hard-code

A 2008 PS-specific play memo says, in effect, that low security causes robbery while low cleaning causes fire. This conflicts with the first-title PS/SS Wiki, which repeatedly links fire risk to security below 100 and notes that 99 is still unsafe.

Sources:
- PS memo: https://satomi2nskw.hatenadiary.org/entry/20081124/1227500976
- first-title FAQ: https://wikiwiki.jp/theconveni1/FAQ
- first-title staff data: https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

Classification:

- `security < 100` increases/allows fire risk: **CONFIRMED-COMMUNITY-PS/SS**, repeated and detailed.
- `cleaning low -> fire`: **CONFLICT / low-confidence single PS recollection**.

Implementation rule: do not add a cleaning-to-fire causal term at this stage. Keep incident risk policy configurable and driven by the stronger security evidence until original manual/strategy-guide data resolves the conflict.

## 6. Town-demand competition: own branches count as competitors

The SS record reports the main store recovering customers only after shortening the hours of the player's own 2nd/3rd branches. The first-title Wiki independently warns against placing own stores too close because they steal customers from one another.

**Evidence: DIRECT-PLAY-SS + CONFIRMED-COMMUNITY-PS/SS.**

Demand allocation must therefore consider nearby open stores regardless of ownership. `same_owner` may affect strategy/UI but must not automatically exclude a store from customer-choice competition.

Sources:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 7. Newly sharpened unknowns

The following are now narrow, testable retrieval targets rather than broad unknowns:

1. Exact text/order of every top-level command and each submenu.
2. Exact fields shown on `CustomerInfo` and whether ejection has popularity/service/complaint side effects.
3. Exact names of the sales-performance and questionnaire screens under `調査`.
4. Whether `販促 → 誘致` hierarchy is identical on PS and SS.
5. Exact six store-selector variants and whether price changes when moving among all six icons.
6. Original incident formula: security vs cleaning vs popularity dependencies for robbery/fire/shoplifting.

These should be targeted with manual page extraction and original-screen capture before inventing rules.

## Research-status note

This run improves command hierarchy and direct customer-interaction reconstruction but does not close the largest numeric-master gaps (complete products, fixtures, six store sizes/prices, permit fees/radius, full 35-staff numeric table, town-building master, exact economy formulas). Full research is therefore **not complete**, though implementation can continue safely where current evidence is explicitly gated by source/confidence.