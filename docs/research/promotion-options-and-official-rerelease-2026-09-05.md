# Promotion options and official rerelease route — 2026-09-05

## Scope

Target is only the 1997 console release **The Conveni / ザ・コンビニ ～あの町を独占せよ～** on PlayStation / Sega Saturn. Do not import numerical data from later series entries.

## Evidence scale used here

- **DIRECT-PLAY-SS**: a source explicitly identifies the Saturn version and reports observations from actual play.
- **OFFICIAL-PRESERVATION**: current official publisher/platform information about preservation/re-release of the original console game. Useful as an acquisition/verification route, but not automatically proof of an original gameplay parameter until the preserved game/manual is directly inspected.
- **REJECTED-SERIES-MIX**: information found for later entries and intentionally not adopted.

## 1. Promotion / advertising submenu: five named options recovered

A Saturn play record explicitly describes the `販促` command and distinguishes advertising from inducement. Under advertising, the player reports the following five choices:

1. ダイレクトメール
2. 新聞広告
3. 飛行船
4. ラジオCM
5. テレビCM

The same record states that advertising raises store popularity, describes direct mail/newspaper/airship as the lower-to-mid-cost practical choices, and radio/TV CM as very expensive. This is enough to recover the **names and ordering class** of five advertising options, but not their exact prices, effect magnitudes, or activation timing.

**Evidence:** DIRECT-PLAY-SS

**Source:** ゲーム＊やおよろず Retro, SS実機プレイ記録, section 「誘致と宣伝はとりあえず最低限」. The page explicitly labels the platform as SS and says the author last played in January 2020.

Reference URL: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

### Implementation consequence

Represent promotion as at least:

```text
販促
├─ 宣伝
│  ├─ ダイレクトメール
│  ├─ 新聞広告
│  ├─ 飛行船
│  ├─ ラジオCM
│  └─ テレビCM
└─ 誘致
```

Do **not** yet hard-code prices/effects from later entries.

### Explicitly rejected contamination

A later `ザ・コンビニ3` strategy page exposes exact prices/effects for similarly named advertising options. Those values were **not adopted**, because they belong to a later title and therefore violate the first-console-version-only rule.

Status: **REJECTED-SERIES-MIX**

## 2. Police box and fire station affect store security

The same SS play record says that a nearby `交番` and `消防署` substantially raise a store's `警備` parameter. The author treats them as useful defensive inducements and repeatedly recommends placing them near stores.

This strengthens the town-facility model: these facilities are not population-only objects; at least some facilities apply a spatial modifier to store parameters.

**Evidence:** DIRECT-PLAY-SS

### Still unresolved

- exact radius / distance metric;
- exact security bonus per facility;
- whether police box and fire station bonuses differ;
- stacking rule when multiple facilities overlap;
- whether the same behavior is byte-for-byte identical on PS.

## 3. Official 2026 preservation release is a new primary-source acquisition route

Sony's official PlayStation Store page for `コンソールアーカイブス ザ・コンビニ ～あの町を独占せよ～` states that:

- the title is the 1997 32-bit console game;
- the release contains the **Japanese ROM** of the game;
- the package includes a **manual** available in Japanese (also translated to several other languages).

This is highly important for continued research because it creates a currently obtainable official preservation route for direct screen/manual inspection without relying only on secondary web writeups or scans of copyrighted material.

**Evidence:** OFFICIAL-PRESERVATION

Official source: https://store.playstation.com/ja-jp/product/JP0571-PPSA34213_00-HAMPRDC000000001

### Research rule for this source

Treat the current release as a **verification medium**, not as an automatic source of unseen values. Values should only be promoted to DIRECT-ORIGINAL/official-level evidence after the preserved ROM/manual screen itself is inspected. Do not save original screenshots, logos, manual pages, audio, or copied original text into the repository; record only derived facts, measurements, menu structure, and citations.

## 4. Current state of unresolved advertising data

Recovered now:

- `販促 → 宣伝` exists;
- five named advertising options exist on SS;
- advertising raises popularity;
- cost tiers are qualitatively ordered from cheaper practical options toward very expensive radio/TV advertising.

Still unresolved:

- exact cost of all five options;
- exact popularity increase;
- delay / scheduled execution time;
- duration and repeatability rules;
- PS confirmation of all five labels and their displayed order;
- whether promotion values depend on number of stores or scenario.

## 5. Priority next actions

1. Inspect the preserved Japanese manual/game UI through the official current release and transcribe only derived menu/value facts.
2. Search original PS/SS-specific strategy material for the five advertising prices/effects.
3. Cross-check PS footage to determine whether the SS five-option list is platform-common.
4. Continue avoiding later-series numerical tables even when menu labels match.

## Completion assessment

This pass improves the **menu hierarchy / promotion** area and identifies a new official path for direct primary-source recovery, but overall reconstruction research is still incomplete. Major unresolved blocks remain: full product table, all fixtures, all six store size/price/dimension values, permit prices and exclusion distances, all 35 employee numeric stats, full town-facility table, customer/staff AI formulas, economic equations, and full scenario/event conditions.
