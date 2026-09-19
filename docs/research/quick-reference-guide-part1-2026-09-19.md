# クイックリファレンス (Quick Reference guide) — Part 1 transcription (book pages 2–47)

Created: 2026-09-19

## 0. Scope and handling policy

This file transcribes **PDF 1 of 2** covering a newly-provided scan of
「『ザ・コンビニ～あの町を独占せよ～』クイックリファレンス」
(*The Conveni Quick Reference*), a **different physical strategy-guide book**
than the one already fully transcribed in
`docs/research/strategy-guide-full-decode-2026-09-16.md` ("book1" below).
Source file: `ed9aac6f-downloadfile2.PDF`, 23 scanned two-page spreads,
covering book pages roughly 2–47 (the book's own "クイックリファレンス"
section, pages 2–12, followed by a second, physically-bound-together book,
「パーソナルデザインBOOK」("Personal Design Book"), pages 16 onward, whose
"パーソナルコンビニデザイン" section (pages 24–47) is store-concept /
product-placement flavor content, not core mechanics). A companion PDF
(part 2) picks up where this one leaves off and is being transcribed by
another session.

Evidence tags follow `PROJECT_MEMORY.md` section 15:
**CONFIRMED-OFFICIAL** (guide text/table/formula), **CONFIRMED-VISUAL**
(only visible in a screenshot, not restated in prose). All facts below are
one of these two unless marked `UNCERTAIN` (low OCR/scan-legibility
confidence — do not implement from an `UNCERTAIN` value without
re-verifying against the original scan first, per this project's existing
convention).

Every fact carries a book page citation. Cross-check status vs. the
existing codebase/docs is marked **NEW**, **CONFIRMS**, or **CONTRADICTS**
inline.

---

## 1. 時間 (Time) — book pages 2–3

### 1.1 Business hours options (page 2, circled-diagram callout)

The 24-hour clock diagram offers 7 choices:

| # | Hours | Guide's own label |
|---|---|---|
| ① | AM10:00–PM6:00 | 8時間営業 (8h) |
| ② | AM7:00–PM11:00 | 16時間営業 (16h) |
| ③ | AM11:00–AM2:00 *(as legible; see note)* | 16時間営業 (16h) |
| ④ | PM0:00–AM4:00 (PM0:00 = noon) | 16時間営業 (16h) |
| ⑤ | PM7:00–AM11:00 | 16時間営業 (16h) |
| ⑥ | 24時間営業 (24h) | — |
| ⑦ | 臨時休業 (temporary closure) | — |

CONFIRMED-OFFICIAL. **UNCERTAIN note on ③**: AM11:00–AM2:00 is only 15
hours, inconsistent with its own "16時間営業" label, while ②/④/⑤ all check
out exactly to 16h. This is very likely a scan/OCR misread of "AM3:00" as
"AM2:00" (11am+16h=3am). Recommend re-verifying against the source scan at
higher resolution before hard-coding; noted here rather than silently
"corrected."

**Cross-check**: NEW. PROJECT_MEMORY.md section 10 only says "Business
hours are configurable, including 24-hour operation and shorter opening
windows" with no options list. This is the first recovery of the exact 7
selectable windows. No current `game`/`reference_sim` code enumerates a
fixed business-hours option list (opening hours are set as arbitrary
start/end minutes in `vertical_slice.json`), so nothing to contradict —
this is new data that could tighten `demand.opening_minutes_per_day`'s
input domain in a future task.

### 1.2 Cost formulas (page 2, callout boxes)

- **補充 (Restock cost)**: "仕入単価×数量分で設置時にかかる費用。その後は1つ
  補充するたびに仕入単価と差し引かれる。" → restock cost = purchase unit
  price × quantity, charged at fixture setup, then per-unit purchase price
  deducted on every subsequent restock. CONFIRMED-OFFICIAL, page 2.
  **CONFIRMS** the existing `sale_price_yen`/`restock_unit_cost_yen`
  per-unit charging model already used by `apply_explicit_restock` /
  `try_procure_product` in `game/scripts/domain/vertical_slice_simulation.gd`.

- **設備費 (Equipment/fixture purchase cost)**: "初期投資に必要な商品や設備
  置き場の準備金。" — the up-front fixture purchase price. CONFIRMED-OFFICIAL,
  page 2. **CONFIRMS** existing `fixture_catalog` purchase-price model.

- **維持費 (Maintenance cost)**: "設備を良好に保つための…電気代として1日に
  必要な費用。**営業時間に応じて**、毎日売上げから差し引かれる。" —
  maintenance is a daily electricity-like cost, deducted from daily sales,
  **scaled to business hours** ("営業時間に応じて"). CONFIRMED-OFFICIAL,
  page 2. **Partially CONTRADICTS** the current implementation:
  `VerticalSliceSimulation._apply_daily_fixture_maintenance()` (task #46,
  decision 0115) deducts each fixture's full `maintenance_yen_per_day`
  once per simulated day regardless of how many hours the store was open
  that day — not prorated by business hours the way this text states.
  This is the same shape of gap task #47 already flagged for wages (see
  below) but for fixture maintenance instead.

- **人件費 (Labor cost)**: "社員の給料として必要な経費。表示は日給だが、
  内部では**時給計算**がされている。計算方法は**時給×営業時間**。営業時間を
  伸ばすほど人件費がかさむので注意してほしい。" — daily wage display, but
  internally computed as **hourly_wage × business_hours_per_day**.
  CONFIRMED-OFFICIAL, page 2. **Independently restated** on page 6 (社員/
  雇用/賃金は時給計算): "賃金は時給×営業時間で表示される…営業時間0時間の
  臨時休業日は、日給表示も0円なのだ。" (temporary-closure days with 0
  business hours show ¥0 wage). Two independent statements of the same
  exact formula in this one book, both CONFIRMED-OFFICIAL.
  **CONTRADICTS** the current implementation: `_apply_daily_staff_wages()`
  (task #47, decision 0116) explicitly says "charged in full rather than
  prorated by hours worked, since this client has no shift/hours-worked
  tracking for staff at all to prorate against" and charges each staff
  member's full `salary_yen_per_day_24h` every simulated day regardless of
  configured opening hours. This guide passage is exactly the missing
  formula task #47 said didn't exist yet — **wages should be
  `hourly_rate × opening_minutes_per_day/60`, not a flat per-day charge**,
  and the field name `salary_yen_per_day_24h` itself (already in
  `vertical_slice.json`) hints the ported number is a **24-hour-basis**
  daily figure, i.e. the true hourly rate = `salary_yen_per_day_24h / 24`.
  This is the single highest-value CONTRADICTS finding in this document —
  flag for the user/next implementation task.

Screenshot example values (CONFIRMED-VISUAL, page 2, illustrative only):
restock confirmation for 弁当類 shows ¥19,200; a fixture's own 補充単価
¥1,600 / 維持費 ¥1,200/日; staff panel shows 人件費 ¥7,040/日, total 経費
¥8,976/日.

### 1.3 Month aggregation (page 2–3, "1月" box)

"**1月＝4日間×8** 4日間の収支を8倍することで、1月の収支が決定する。実質32日間
の営業と考えよう。" CONFIRMED-OFFICIAL, page 2–3.

**CONFIRMS exactly** — this is the literal source `reference_sim/conveni_sim/
month_aggregation.py`'s `MONTH_MULTIPLIER_SOURCE` docstring already cites
verbatim ("strategy guide quick reference (\"時間\", book page 2-3)"), and
`game/scripts/domain/vertical_slice_simulation.gd`'s `_settle_month_end()`
(task #90/decision 0090) already implements this formula. No change
needed; this transcription is simply the primary-source confirmation that
docstring was citing sight-unseen (or from a prior partial read) — now
directly verified against the actual scan.

Also on page 3: "毎月1日に前月の収支と人口増減が表示される。ここで指す収支と
は、日常の経費を差し引いた純利益。**宣伝費や設備費、コンストの賞金などは他経費
に一括で表示される。**" — promotion costs, fixture purchase costs, and
contest prize money are all lumped into a single "other expenses" line on
the monthly report, separate from the daily-operations net profit figure
used for the ×8 multiplier. CONFIRMED-OFFICIAL, page 3. **NEW** — this is
a previously-unrecorded detail about what the "4-day net result" going
into the ×8 formula does and does not include (a real answer to one of
`month_aggregation.py`'s own open questions, "how each representative
day's own net result is computed... which costs are already netted out").
Not yet wired into any code.

### 1.4 Promotion (page 3, "宣伝" box)

"全店舗の人気を上げる効果がある。宣伝費の高いものほど効果は高い。**ただし、店舗
評価が3つ星以下の場合、効果は持続しない。**" CONFIRMED-OFFICIAL, page 3.

The box lists the 5 promotion types **in order only, with no cost or
popularity-gain numbers on this page**: 1 ダイレクトメール, 2 新聞広告,
3 飛行船, 4 ラジオCM, 5 テレビCM. This is a materially different page than
what the task brief assumed ("this book's page 3 shows a promotion
cost/popularity table") — **this Quick Reference book's page 3 does NOT
restate the numeric cost/popularity table**; book1 (`strategy-guide-full-
decode-2026-09-16.md` section 2) is the only source with the actual
numbers, already reconciled in `baseline_data.py`'s `PROMOTIONS` (see
section 9 below for the full comparison against PROJECT_MEMORY.md section
11's community-sourced table). The ordering here (direct mail < newspaper
< airship < radio < TV) is consistent with both existing tables' cost
ranking, so **CONFIRMS** relative ordering only.

**NEW finding**: "店舗評価が3つ星以下の場合、効果は持続しない" — promotion's
popularity effect does not persist if the store's star rating is 3 stars
or below. This qualitative gate is not represented anywhere in
`reference_sim/conveni_sim/promotion.py` or `game/scripts/domain/
vertical_slice_simulation.gd`'s promotion firing logic at all (currently
popularity gain always applies once a scheduled promotion fires,
regardless of `star_rating`). Genuinely new, actionable mechanic.

### 1.5 Owner evaluation categories (page 3, "1年" screenshot)

Screenshot (CONFIRMED-VISUAL, page 3) shows a 5-category yearly "オーナー
評価" (owner evaluation) panel: 店舗評価 / 累積来客数 / 年商 / 町人口 / 総合
評価 (store rating / cumulative visitor count / annual revenue / town
population / overall rating), each independently star-ranked
(★★★★★ shown for all 5 in the example). **NEW** — names, for the first
time, the exact 5 criteria behind PROJECT_MEMORY.md section 14's
"advanced: reach 5-star owner evaluation" scenario goal (previously
PROVISIONAL/unnamed). See also section 6.3 below (page 11) for the
advanced scenario's numeric targets for these same 5 categories.

### 1.6 Annual calendar — weekday/holiday per representative day (page 3)

年間カレンダー table, columns 季節/月/1日/2日/3日/4日 (season / month / the
4 representative days of that month):

| 季節 | 月 | Day 1 | Day 2 | Day 3 | Day 4 |
|---|---|---|---|---|---|
| 冬期 | 1月 | **休日** | 平日 | 平日 | 休日 |
| 冬期 | 2月 | 平日 | 休日 | 平日 | 休日 |
| 冬期 | 3月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 4月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 5月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 6月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 7月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 8月 | 平日 | 休日 | 平日 | 休日 |
| 夏期 | 9月 | 平日 | 休日 | 平日 | 休日 |
| 冬期 | 10月 | 平日 | 休日 | 平日 | 休日 |
| 冬期 | 11月 | 平日 | 休日 | 平日 | 休日 |
| 冬期 | 12月 | 平日 | 休日 | 平日 | 休日 |

CONFIRMED-OFFICIAL, page 3, moderate confidence (a dense small-print
table; the January exception — day 1 = holiday, plausibly New Year's Day —
is internally consistent and increases confidence in the read, but full
re-verification against the scan is recommended before hard-coding).

**NEW.** No day-type (weekday/holiday) concept exists anywhere in
`reference_sim` or `game` today — `clock.py`/the Godot day counter only
track a raw day-of-month index, with no weekday/holiday distinction and no
consumer of one. This also introduces a previously-unseen coarse two-season
split (冬期 Oct–Mar / 夏期 Apr–Sep) distinct from the 12-month weather-%
table in 1.7 below; its gameplay meaning (utility cost basis? nothing
currently reads it) is not stated on this page.

### 1.7 Weather percentage-by-month table (page 3)

"天候のパーセンテージ設定 (**荒天＝大雨・雷雨・台風・大雪**)"

Header row: 月 / 快晴 / 曇り / 雨 / 台風 / 荒天 (month / clear / cloudy /
rain / typhoon / storm — where 荒天 is explicitly glossed as an umbrella
category "heavy rain・thunderstorm・typhoon・heavy snow").

| 月 | 快晴 | 曇り | 雨 | 台風 | 荒天 | Row sums to 100? |
|---|---:|---:|---:|---:|---:|---|
| 1月 | 30 | 20 | 15 | 5 | 30 | ✓ 100 |
| 2月 | 30 | 20 | 10 | 10 | 30 | ✓ 100 |
| 3月 | 30 | 20 | 15 | 5 | 30 | ✓ 100 |
| 4月 | 30 | 20 | 15 | 5 | 30 | ✓ 100 |
| 5月 | 40 | 30 | 20 | 5 | 5 | ✓ 100 |
| 6月 | 1 | 9 | 30 | 50 | 10 | ✓ 100 |
| 7月 | 20 | 20 | 15 | 20 | 20 | ✗ 95 — `UNCERTAIN` |
| 8月 | 30 | 20 | 15 | 20 | 15 | ✓ 100 |
| 9月 | 30 | 20 | 15 | 10 | 15 | ✗ 90 — `UNCERTAIN` |
| 10月 | 40 | 30 | 10 | 10 | 10 | ✓ 100 |
| 11月 | 30 | 20 | 15 | 5 | 30 | ✓ 100 |
| 12月 | 30 | 20 | 15 | 10 | 5 | ✗ 80 — `UNCERTAIN` |

CONFIRMED-OFFICIAL for the table's existence/columns; individual cell
values are transcribed as legible but **flagged `UNCERTAIN` at reduced
confidence for July/September/December specifically** (rows that do not
sum to 100%, unlike every other row) — do not implement these three rows'
exact digits without re-scanning at higher resolution. June's outlier
shape (1% clear / 9% cloudy / 30% rain / 50% typhoon / 10% storm) is
plausible for 梅雨 (rainy season) and is *not* flagged as uncertain since
it sums correctly, but is unusual enough to be worth a second look too.

**CONTRADICTS a category-naming assumption already baked into the
codebase.** `reference_sim/conveni_sim/remake_customer_share.py` line
47–50:

```python
BAD_WEATHER_VALUES = frozenset({"大雨", "雪", "台風", "荒天"})
"""Matches the guide's own 5-way weather category table (quick reference,
"天候のパーセンテージ設定": 快晴/大雨/雪/台風/荒天); everything but 快晴
counts as bad weather here."""
```

This comment already cites "quick reference" (i.e. this exact book) and
claims the 5 columns are **快晴/大雨/雪/台風/荒天** (clear / heavy-rain /
snow / typhoon / storm), i.e. that 大雨 (heavy rain) and 雪 (snow) are each
their own peer column. This transcription instead reads the actual header
as **快晴/曇り/雨/台風/荒天** (clear / cloudy / rain / typhoon / storm),
with 荒天 defined by its own parenthetical as the umbrella "大雨・雷雨・台風
・大雪" — i.e. 大雨/雪 are not separate columns at all, they're two of the
four things bundled inside 荒天. **This is a genuine CONTRADICTS finding
between this transcription and an assumption already embedded (with a tag
claiming to match this very book) in a REMAKE_BALANCED_DEFAULT constant
consumed by `compute_customer_share_percent()`.** Practically, `曇り`
(cloudy) is not currently a recognized weather value anywhere in
`BAD_WEATHER_VALUES`'s domain at all (only 大雨/雪/台風/荒天 are), so if
"曇り" is ever passed as a `weather` input it would currently fall through
as "good weather" (not penalized) — consistent either way, since the
guide doesn't say cloudy is bad. The real risk is that "雨" (plain rain)
and "曇り" (cloudy), if they are the actual category names, do not match
any string this codebase's weather-input producers use today (unverified
— no weather-condition enum was found in `reference_sim`/`game` beyond
this frozenset and `PopularityDecayContext`; nothing currently emits or
consumes literal weather strings elsewhere in the pipeline).
**Recommend the guide's exact column headers be re-verified against the
original scan before this is either fixed or left as-is**, since both this
transcription and the existing code comment cannot be correct
simultaneously, and this reader's own confidence in the small-print header
is moderate, not certain.

---

## 2. 店舗 (Store) — book pages 4–5

### 2.1 Catchment / land value factors (page 4, "来店数を稼ぐ")

- "付近に人口が多いほど、店舗への来店客も増える。**地価の上がりやすい地域が好
  立地**となる。" CONFIRMED-OFFICIAL, page 4. CONFIRMS PROJECT_MEMORY.md
  section 8's "surrounding building population" factor.
- **ライバル店 (rival store)**: "ライバル店舗との距離が近いと、顧客を取り合う
  ことになる。顧客の選択基準は**販売価格やサービス面、あるいは店舗への距離**
  だ。" CONFIRMED-OFFICIAL, page 4. CONFIRMS section 8's factor list
  (price, service, rival proximity) with an explicit tri-factor customer
  choice model (price / service / distance) not previously stated together
  this plainly.
- **線路沿い (along a railway line)**: "**人口5000人を超えると、駅に設置で
  きる。駅の買い物人口は2000人**なので、客が飛躍的に伸びる。" CONFIRMED-
  OFFICIAL, page 4. **CONFIRMS and quantifies** PROJECT_MEMORY.md section
  13's "one documented case reports a station appearing after town
  population exceeds 5,000" (previously CONFIRMED-COMMUNITY/anecdotal;
  this is now a CONFIRMED-OFFICIAL population threshold of >5,000, plus a
  **new** figure: the station facility's own shopping population = 2,000).
- **交差点 (intersection)**: "コンビニと距離が同じ場所から店舗の地価が上昇。
  交差点は2本の道路の影響を受けるので発展しやすい。" CONFIRMED-OFFICIAL,
  page 4. NEW — not previously recorded; relevant to a future spatial
  land-value model (`remake_land_value.py` currently has no
  road/intersection input variable at all — see its own admission of "no
  exact formula, urbanization input variable... published").
- **買物人口 (shopping population)**: "コンビニを除いて、マップ内のすべての
  施設には固有の**買い物人口**が設定されている。買物人口の総数が多い建物の
  近辺は来店数が増える。" CONFIRMED-OFFICIAL, page 4. NEW/CONFIRMS —
  formalizes the per-facility "shopping population" stat referenced
  throughout this book (see section 5 below for the facility table) as the
  driver of nearby store visits; matches the general shape (not exact
  formula) of `TownState.population` already in `game/scripts/domain/
  town_state.gd`, but that file has no per-facility breakdown at all
  (single scalar `population`), so this is a real, unimplemented gap.

### 2.2 Price margin / discount UI (page 4, "利益率" box)

"販売価格を決定して下さい / **全品目平均利益率 20%** / 全品に設定 <20%OFF>
/ 個別に設定" (screenshot UI, CONFIRMED-VISUAL). Body text: "利益率＝販売価格
の利益の割合。**通常は全体で40%に設定**されており、これが定価と考えられる。"
CONFIRMED-OFFICIAL, page 4.

**NEW — high value.** This is direct evidence of the exact price-setting
mechanic PROJECT_MEMORY's task #27 (decision 0096) noted was entirely
absent: "`price_change_pct=0` (no price-setting mechanic exists yet)".
The guide shows: (a) a baseline "default"/list price margin the game
considers 40% overall, (b) a global "all items X% off list price" slider
(example shown at 20% off), and (c) a per-item override
("個別に設定"). This is the confirmed shape of the missing mechanic
`store_rating.gd`'s `price_change_pct` input was always meant to feed —
not yet implemented anywhere.

- **人気 (Popularity)**: "住民の認知度。いくら安売りしていても、店舗の存在に
  気付いていない住民は買物客とはならない。" CONFIRMED-OFFICIAL, page 4.
  CONFIRMS the existing `popularity` stat's role (awareness gate, not a
  pure demand multiplier) already used by `try_purchase_promotion`/
  `customer_share.gd`.
- **アイドル (Idol) event**: "1万人来店を記念して、1日人気アイドルが○日オー
  ナーになります" (screenshot). CONFIRMED-VISUAL, page 4. CONFIRMS
  `visitor_milestone.py`/`chain_visitor_milestone.gd`'s existing
  10,000-visitor milestone event (task #30) — this page doesn't restate
  the "+100 popularity" number (that's from book1/page-12's イベントガイド
  table transcribed in section 7 below), just the trigger condition and
  flavor.

### 2.3 Parking (page 5)

"① タワー型駐車場 **20台収容** ② 2階建駐車場 **4台収容** ③ 駐車場 **2台収容**"
CONFIRMED-OFFICIAL, page 5. **CONFIRMS exactly** PROJECT_MEMORY.md section
4's already-recorded parking capacities (ground=2, two-story=4, tower=20)
and `baseline_data.py`'s `FIXTURES` parking entries (task #34).

**NEW**: "自動車で移動する設定の顧客が利用する設備。駐車場がなかったり自動車
利用の客が少なかった場合には、**クラクションの効果音**が出る。" — customers
set to arrive by car use parking; if there's no parking (or too little for
the number of car-driving customers), a car-horn sound effect plays. Not
currently modeled (no "insufficient parking" feedback/penalty exists in
`game`/`reference_sim`); flavor/UX detail, low implementation priority.

### 2.4 Service fixture bonuses (page 5, "サービス設備の効果と配置")

| Fixture | This page (page 5) | PROJECT_MEMORY.md section 4 (existing) |
|---|---:|---:|
| 観葉植物 (potted plant) | **+2** | +2 — CONFIRMS |
| ベンチ (bench) | **+4** | +3 — **CONTRADICTS** |
| 噴水 (fountain) | **+30** | +25 — **CONTRADICTS** |

CONFIRMED-OFFICIAL, page 5. Two of three service-fixture bonus values
**contradict** the figures already recorded in PROJECT_MEMORY.md section 4
(sourced from the first-title wiki, `wikiwiki.jp/theconveni1/内装`,
CONFIRMED-COMMUNITY tier) and presumably also whatever
`reference_sim/conveni_sim/baseline_data.py`'s `FIXTURES` entries for
`bench`/`fountain` currently encode as `service_bonus` (not independently
re-checked here, but PROJECT_MEMORY and that module are expected to agree
since PROJECT_MEMORY section 4 is this project's own summary of that
data). **This guide (CONFIRMED-OFFICIAL, an official printed strategy
guide) should be treated as at least as authoritative as the wiki
(CONFIRMED-COMMUNITY)** per this project's own evidence-tier ordering —
flag prominently for a decision on which value to adopt, mirroring how the
project already resolved the airship/radio/TV popularity-gain conflict in
favor of the (other) strategy guide over the wiki (see `baseline_data.py`
lines 474–483).

Also: "店舗のサービス値を増やす設備。サービス値が高い店舗は、サービスを重視
する客が来店しやすい。**密閉空間に配置しても効果は出る。**" CONFIRMED-
OFFICIAL, page 5. **NEW**: service fixtures' bonus applies even placed in
an enclosed/unreachable space — i.e. they need not be walkable-adjacent to
count, unlike ordinary product fixtures. Not modeled today;
`store_layout.gd`'s route-feasibility checks apply uniformly to every
fixture type regardless of kind.

### 2.5 Aisle width / congestion rules (page 5, "通路の幅とすれ違い")

- **① 1マス通路 (1-tile aisle)**: "客や店員が**2人並んで通れる幅**。**すれ違
  えるので混雑しにくい**。" CONFIRMED-OFFICIAL, page 5.
- **② 1/2マス通路 (half-tile aisle)**: "客や店員**1人が通れる幅**。**すれ違
  うことができず、混雑しやすい**。" CONFIRMED-OFFICIAL, page 5.

**CONFIRMS and meaningfully sharpens** PROJECT_MEMORY.md section 4's
existing, vaguer note ("At least 1 tile of passage is recommended in
normal aisles; checkout fronts need around 2 tiles"). The actual rule is
sub-tile granular: a full 1-tile-wide aisle allows two people to pass each
other (low congestion); a half-tile aisle allows only one person through
at a time and cannot be passed (congestion-prone). `store_grid.py`/
`store_layout.gd`'s current pathing has no half-tile/sub-cell passage-
width concept at all (their occupancy grid is whole-tile), so this is a
real, unimplemented mechanic, not just a documentation gap.

### 2.6 Shelf vs wagon interaction direction (page 5)

"商品棚のタイプは2種類 — **ワゴン**: 4方向から商品を取り出せる。コピーや保温
商品ケースもワゴン扱い。 / **棚**: **前方からしか商品が取り出せない**。自動
販売機も棚に分類される。" CONFIRMED-OFFICIAL, page 5.

**NEW mechanic, currently unimplemented.** `game/scripts/domain/
vertical_slice_simulation.gd`'s `_find_open_interaction_cell()` (task
#38) derives exactly one interaction cell per fixture from a single fixed
convention ("every current fixture's interaction cell sits exactly one
subcell outside its own footprint"), with no distinction between
`wagon`-kind (should support 4-directional access) and `shelf`-kind
(front-only) fixtures. `fixture_catalog` already has a `kind` field that
could carry this distinction, but nothing currently derives per-kind
interaction-direction rules from it. Also NEW: "商品は1/2マスアキでも大丈夫
— 棚やワゴンは取り出せる方向を1/2マス開けておけば、そこから利用可能。店員に
よる商品の補充もできる。" (a half-tile gap on the correct side is sufficient
for both customer purchase and staff restock interaction).

### 2.7 Shelf attention / shortest-route pathing (page 5)

- "**商品棚の注目度が客を呼ぶ** — 注目度の高い棚は客の注意を引く。店舗の奥に
  配置しても、客が気付かずに帰ることはない。" CONFIRMED-OFFICIAL, page 5.
  CONFIRMS/refines PROJECT_MEMORY.md section 7's HYPOTHESIS that "Large
  wagons may have higher `attention`... affect incidental purchase
  probability" — this page states attention's effect is about *noticing*
  a product at all (even placed deep in-store), a distinct claim from
  incidental-purchase probability specifically.
- "**買い物客は最短ルートを選ぶ** — 左図の店内で、冷たい飲料を買いたい顧客は
  最短ルートをまず歩く。**最短ルートが進めない場合にのみ、遠回りをする**。"
  CONFIRMED-OFFICIAL, page 5. CONFIRMS the shortest-path-first,
  detour-only-when-blocked pathing model already implemented via BFS in
  `store_layout.gd` (previously only CONFIRMED-COMMUNITY per PROJECT_
  MEMORY.md section 4's "Multiple routes can allow customers to detour
  around congestion").

---

## 3. 社員 (Staff) — book pages 6–7

### 3.1 Hiring (page 6)

- **Wage formula**: see section 1.2 above (independently restated here,
  CONFIRMED-OFFICIAL, page 6) — "賃金は時給×営業時間で表示される…営業時間0
  時間の臨時休業日は、日給表示も0円なのだ。"
- **年齢 (Age)**: "年齢による傾向は履歴書評価に加味されているので、改めて気
  にする必要はない。**何歳だろうと社員は死なない。**" CONFIRMED-OFFICIAL,
  page 6. NEW (no death/retirement mechanic exists in this client at all,
  consistent with this confirmation that none should).
- **性別 (Gender)**: "比較的、**男性は体力に優れ、女性は社交性が優れている**
  が、履歴書評価に反映される。" CONFIRMED-OFFICIAL, page 6. NEW — no
  gender-based stat tendency is modeled in `staff_candidates`/`STAFF_
  CANDIDATES` today (their stats are per-individual only).
- **履歴書評価の意味 (résumé-stat meaning) table**: 経験(experience)=player/
  rival-store work history; 体力(stamina)=continuous-work endurance;
  学歴(education)→register/education-parameter ceiling; 敏捷性(agility)→
  mainly restock-ability; 社交性(sociability)→service/cleaning-parameter
  source. CONFIRMED-OFFICIAL, page 6. **CONFIRMS** PROJECT_MEMORY.md
  section 6's existing claims ("Education is related to register/security
  ceilings...", "Agility relates to replenishment ceiling...",
  "Sociability relates to customer service and cleaning ceilings") from an
  independent (different-book) source.
- **店員数 (staff headcount cap)**: "各店舗に**店長が必ず必要**。**店員は2人
  まで**雇用できる。**スーパー社員は3人まで店員として数える。**店舗評価は社
  員数に応じて設定されることもある。" CONFIRMED-OFFICIAL, page 6. **NEW** —
  confirms the per-store roster cap is exactly 1 manager (店長) + up to 2
  regular staff (店員), i.e. 3 total under ordinary circumstances (a "Super
  Employee," see below, counts as 3 staff on its own for headcount
  purposes — read literally this could mean a single Super Employee fills
  the entire 2-employee-plus-manager quota, but the exact interaction is
  not spelled out further on this page). `game`'s vertical slice currently
  hardcodes exactly 2 active staff (`staff-1`/`staff-2`) with no explicit
  manager/employee role distinction or hiring-cap enforcement — consistent
  in scale, but the manager role and the cap itself are unimplemented.
- **賃金アップ (wage-raise) event**: "**セガサターン版のみに発生するイベント。**
  ベースアップ3%か、5%以上の要求を断っても、ほぼあきらめる。" CONFIRMED-
  OFFICIAL, page 6. NEW, but explicitly platform-scoped to the Sega Saturn
  release only — flag as SS-exclusive, lower priority for a PS-baseline
  recreation per PROJECT_MEMORY.md section 2's framing (PS/SS both are the
  target, but this text itself singles out SS).
- **"80歳でスーパー社員に" (Super Employee at 80)**: "キャラクターの年齢が
  80歳を超えると、一定の確率で**全パラメータが100のスーパー社員**になる。
  最高は**22年に1度**。スーパー社員がやってくることもあるので、確認しよう。"
  CONFIRMED-OFFICIAL, page 6, with a CONFIRMED-VISUAL screenshot example
  (94-year-old candidate, all 6 shown stats = 100). **NEW — entirely
  unmodeled mechanic**: no staff-aging, retirement-replacement, or
  "Super Employee" candidate-generation system exists in `reference_sim`
  or `game` today.

### 3.2 Parameters (page 7)

- **店長の能力 (manager ability)**: "特に重要なのは教育。この値の高い店長の
  いる店は、**店員2人の能力が上がりやすい**。また、教育が高いほど、アドバイ
  スも正確。" CONFIRMED-OFFICIAL, page 7. **CONFIRMS** PROJECT_MEMORY.md
  section 6's "store-manager education affects staff growth," now with the
  specific mechanism named (manager's own education stat accelerates the
  *other two* staff members' growth rate) — not yet ported (task #48
  explicitly listed "the manager-education growth bonus (no 'who is the
  manager' designation exists among `staff.members`...)" as not
  implemented).
- **各数値の意味 (per-stat meaning) table**, CONFIRMED-OFFICIAL, page 7:
  - 体力 (stamina): as in résumé eval; consumed by acting, restored by
    resting.
  - 教育 (education): affects staff ability growth rate; **cap = 100**
    ("教育値100は上限" — NEW explicit numeric ceiling confirmation).
  - レジ (register): checkout speed; "**最大のポイントとして特に重要**"
    (explicitly called out as especially important to maximize).
  - 補充 (restock): restock speed; **"商品を買えなかった客の割合に影響"**
    — NEW: restock skill is explicitly stated to affect the *rate of
    customers who couldn't buy the product they wanted* (a stockout/lost-
    sale link), not just restock task duration. `restock_timing.gd`
    (task #40) currently only scales restock *duration*, with no
    stockout-probability effect at all.
  - 警備 (security): "**強盗や火災の発生率に影響**する" — CONFIRMS
    PROJECT_MEMORY.md section 12 ("Security below 100 can allow serious
    incidents such as fire") and additionally ties security explicitly to
    *robbery* rate too, not just fire.
  - 清掃 (cleaning): affects in-store cleanliness feel; "清掃が間に合わない
    と店舗評価が下がる" — CONFIRMS the existing `compute_cleaning_value()`
    → monthly star-rating pipeline (task #27).
  - 接客 (customer service): affects the store's サービス値 (service
    value) directly — CONFIRMS existing `service_skill` → `compute_
    service_value()` wiring.

- **パラメータの上昇下降 (parameter growth/penalty matrix), page 7** — `UNCERTAIN`,
  moderate-to-low confidence on the exact column mapping (dense small
  print; **recommend re-verification against the original scan before any
  implementation change**), but the qualitative shape read is:

  | Action | Read as affecting |
  |---|---|
  | 1人分のレジを打つ (serve 1 checkout) | レジ **+1** only |
  | 1つ棚に商品を補充する (restock 1 shelf) | 補充 **+1**, and a second **+1** on what appears to be 警備 |
  | 1エリアを清掃する (clean 1 area) | 警備 **+1**, 清掃 **+1** |
  | 1人のお客を怒らせる (anger 1 customer) | **four `-1` penalties** across what appear to be 補充/警備/清掃/接客 |

  If this reading is correct, it would be a significant finding against
  two already-implemented REMAKE_BALANCED_DEFAULT/CONFIRMED-COMMUNITY
  constants:
  - `game/scripts/domain/staff_growth.gd` (task #48, decision 0117)
    currently applies **checkout → register_skill +1 AND service_skill
    +1** (2 skills) and **restock → replenishment_skill +1 AND cleaning_
    skill +1 AND security_skill +1** (3 skills) — this table instead
    reads as checkout affecting only レジ (register) alone, and restock
    affecting only 補充+警備 (replenishment+security, not cleaning), plus
    an entirely separate **cleaning task** (**not implemented at all** in
    `game` today — task #48 explicitly noted "no standalone cleaning
    task/mechanic exists in this client at all") that grows 警備+清掃.
  - `game/scripts/domain/checkout_anger.gd` (task #49, decision 0118)
    currently uses `SKILL_DELTA := -2` (tagged CONFIRMED-COMMUNITY, citing
    5 affected skills: register/replenishment/security/cleaning/service,
    "education/stamina unaffected") — this table instead reads as **-1**
    (not -2) across what looks like 4 parameters, not 5, and does not
    obviously include レジ (register) among the penalized ones despite
    checkout anger being a checkout-time event.

  Given the transcription-confidence caveat above, **this row is flagged
  as the second-highest-priority item for re-verification** in this
  document (after the weather-table category-naming contradiction in
  section 1.7) — it potentially touches two already-"confirmed" numeric
  constants currently live in `game/`, but this reader's confidence in the
  exact column-to-skill mapping is not high enough to assert a firm
  CONTRADICTS without a second look at the source scan.

---

## 4. 顧客 (Customer) — book pages 8–9

### 4.1 Customer archetypes and facility shopping populations (page 8)

CONFIRMED-OFFICIAL prose + CONFIRMED-VISUAL screenshot examples, page 8:

- 幼稚園児/小学生 (kindergartner/elementary): "1人あたりの購入額（客単価）が
  低いのが難点。お菓子が売れる。" Example: 物件名 幼稚園, 買物人口 36人.
- 中学生/高校生/大学生: "男女の設定を持ち、文房具やコピー、イベント商品など
  が売れる。大学生は酒やたばこも買う。" Example: 物件名 大学, 買物人口 749人;
  女子高生 試したかった物=冷たい飲料, 所持金¥2,000; 大学生 試したかった物=
  コピー用品, 所持金¥3,000.
- オフィスの顧客 (office workers): "**規模別に5種類の会社**が設定されてい
  て、それぞれ買い物人口が異なる。" 会社員 試したかった物=インスタント類,
  所持金¥2,500 / OL 試したかった物=日用品. NEW — 5 distinct office-building
  size tiers, each with its own shopping population (only one example
  value, 会社 3x3=90 buyers, is otherwise recorded on page 10 — see 6.1).
- 体育施設の顧客 (sports-facility customers): "体育館、プール、運動場など。
  主に学生が利用する施設。" 物件名 運動動(運動場か), 買物人口 100人.
- 子連れの母親 (mothers with children): "子供のためにお菓子などを購入する。
  弁当、パン類も売れる。" 幼稚園=買物人口504人 / 遊園地=買物人口642人 (as
  examples of facilities this archetype originates from).
- 家族連れの多い施設: ファミリーレストラン example (buyer count illegible).
- 住宅地 (residential): "**規模別に7種類ある。**客単価の高い中年や老人の客層
  がいる。" 住宅=買物人口24人 (example) / 住宅=買物人口4人 (smaller example).
  Screenshot: おじさん 試したかった物=酒, 所持金¥10,000; おばさん 試したか
  った物=日用品, 所持金¥10,000; おじいさん, 所持金¥10,000. NEW — 7 distinct
  residential size tiers.
- パチンコ屋の顧客: "酒、たばこなどが売れる。比較的若い男性が多い。" 物件名
  パチンコ屋, 買物人口 50人.
- 特殊な施設 (special facilities — station/city hall): "**駅と役所は一定の
  条件が成立すると建設される。規模別に3種類ある。駅は2種類が設定されている。**
  複数配置されることもある。" 物件名 都庁(metropolitan govt HQ), 買物人口
  1176人; 物件名 駅(station), 買物人口 2240人 (a second, larger example than
  page 4's 2,000-buyer station figure — **UNCERTAIN whether this is a
  different station size tier or a scan-read discrepancy with 2.1's
  2,000-person figure; both numbers appear near each other in the same
  book and should be reconciled against the original scan**). Separately:
  "人口が1万人を越えると建設される。人口に応じて規模が大きくなる。" —
  **NEW**: this population-triggered facility is 役所 (city/ward office),
  triggered at **town population > 10,000**, with **3 size tiers**,
  distinct from and in addition to 駅 (station)'s >5,000-population,
  2-type threshold from section 2.1 (page 4). PROJECT_MEMORY.md section 13
  only records the station threshold; the city-hall threshold is entirely
  new.

### 4.2 Demand survey + incidental purchases (page 9)

- **アンケートの注目点 (survey)**: "客の需要がダイレクトに分かる。**毎月更新
  されるので、4日に確認するのがベスト。**アンケートを参考に、品揃えやレイア
  ウトを変更すべき。" CONFIRMED-OFFICIAL, page 9. NEW — confirms a
  monthly-refreshing, day-4-best-checked "customer demand survey" UI
  feature; not implemented in `game` (no equivalent panel exists).
- Two bar charts, "① 買った商品" (items bought) and "② 欲しかった商品"
  (items wanted but unavailable), per product category — CONFIRMED-VISUAL,
  page 9, single-playthrough example data (not a general game-data table);
  exact bar values not confidently legible at this resolution and not
  transcribed digit-by-digit here to avoid presenting low-confidence
  numbers as fact.
- **"「購入希望商品」と「ついでに欲しい商品」" — the single highest-value
  finding on this page**: "顧客は購入希望の品を求めて来店する。希望の品を購
  入した後、時間が許せばそのほかの商品も購入する。**それぞれの顧客に3品程度
  の「ついでに欲しい品」があるので**、それらを揃えておくことも大切だ。左の
  グラフに顧客全体の需要を示した。グラフの長い商品ほど、多くの客が購入す
  る。" CONFIRMED-OFFICIAL, page 9.

  **NEW — directly upgrades a standing HYPOTHESIS to CONFIRMED-OFFICIAL
  with an exact number.** PROJECT_MEMORY.md section 7 currently reads:
  "The community research suggests destination-product demand plus
  incidental/add-on purchasing... this remains a hypothesis and must not
  yet be treated as an exact formula." `decision 0004` deliberately leaves
  "incidental/add-on purchase probability" entirely absent from `game`,
  and task #43's audit explicitly blocked fixture-attention
  differentiation on exactly this missing piece. This page now confirms:
  each customer has **approximately 3 "ついでに欲しい品" (incidental-want
  items)** in addition to their primary destination purchase, drawn from a
  store-wide weighted demand ranking (the bar chart). This is the single
  most implementation-actionable NEW finding in this document — it
  unblocks the previously-deferred incidental-purchase system with a
  concrete magnitude, not just a mechanism.

  The demand-ranking bar chart itself lists (CONFIRMED-VISUAL, ranking
  order only, not exact magnitudes) roughly 25 product categories split
  into "ついでに買う顧客" (incidental buyers, pink) vs. "希望で買う顧客"
  (destination buyers, blue) series, with 温かい飲料/冷たい飲料 (hot/cold
  drinks) appearing to have the longest combined bars (highest overall
  demand) and 中華まん/イベント商品/下着類/薬品 among the shortest. Exact
  per-category percentages are not confidently legible and are not
  transcribed here.

---

## 5. 町 (Town) — book pages 10–11

### 5.1 Town population and land value (page 10)

- "地価の上昇に伴って、マップ内に新たな建物が建つ。建設によって新たな買い物
  人口が、町の人口にプラスされる。逆に、建物が取り壊されると、その建物の人
  口がマイナスされる。" CONFIRMED-OFFICIAL, page 10. CONFIRMS the general
  shape of `TownState`'s population tracking, though still no per-facility
  breakdown exists in `game` (single scalar `population`).
- "誘致の効果 — セキュリティ施設は店舗の警備値を上げる。それ以外の施設は人口
  を増やすことが目的。人口の多い大学や遊園地を優先して誘致すべき。"
  CONFIRMED-OFFICIAL, page 10. CONFIRMS PROJECT_MEMORY.md section 13's
  "Facilities such as universities and police can be attracted
  intentionally."
- "地価が上がれば町が発展する — 店舗の周囲は徐々に地価が上がる。様々な建物
  は、地価が高いほど建ちやすい。発展させたい地域に新規開店すべきだ。"
  CONFIRMED-OFFICIAL, page 10. Screenshot examples of vacant-land asking
  price: ¥20,000,000 and ¥23,000,000.

### 5.2 Non-school/security attraction-facility table (page 10)

| 施設 | サイズ | 客数 |
|---|---|---:|
| 遊園地 (amusement park) | 7x7 | 750 |
| 動物園 (zoo) | 5x2 | 500 |
| 会社 (company) | 3x3 | 90 |
| 体育館 (gym) | 3x2 | 30 |
| プール (pool) | 3x2 | 40 |
| 水族館 (aquarium) | 3x3 | 60 |
| 公園 (park) | 2x2 | 30 |
| 住宅 (housing) | 2x2 | 24 |
| 運動場 (athletic field) | 5x4 | 30 |
| イベント会場 (event venue) | 2x2 | 260 |

CONFIRMED-OFFICIAL, page 10. **NEW — fills a research gap directly named
in PROJECT_MEMORY.md section 17** ("Full facility/building list and
population/demand effects" was listed as an open Priority-A gap). No
equivalent footprint/shopping-population table for attraction facilities
exists anywhere in `reference_sim` or `game` today; `TownState` has no
facility model at all.

### 5.3 Security facility bonuses (page 10)

"セキュリティ施設の効果範囲 — 右の写真で示した店舗周囲**16×16エリア**内にセ
キュリティ施設があれば、店舗の警備値にプラス効果がある。"

- **消防署 (fire station)**: 買物人口 12人. "敷地面積**2x3**エリア。1エリア
  ごとに**警備値+5**の効果。**最大で+30**。"
- **交番 (police box)**: 買物人口 8人. "敷地面積**2x2**エリア。1エリアごと
  に**警備値+10**の効果。**最大で+40**。"

CONFIRMED-OFFICIAL, page 10. **NEW — quantifies** PROJECT_MEMORY.md
section 12's previously-qualitative "Police box / fire-station attraction
is a practical way to maintain security." Gives exact footprints (fire
station 2x3, police box 2x2), effect radius (16×16 tiles around the
store), per-area-unit bonus (fire +5/area up to +30 max; police +10/area
up to +40 max), and each facility's own shopping-population contribution
(12 and 8 respectively). Not implemented in `game` — task #27 (decision
0096) explicitly listed "the police-box/fire-station security-facility
bonus (no such fixtures or spatial search exist)" as deliberately out of
scope.

### 5.4 Map tiers and scenario clear conditions (page 11)

| Tier | Clear condition (page 11 heading) | Detail |
|---|---|---|
| 初級 (beginner) | 都庁を誘致する (attract the metropolitan govt HQ) | "人口を増せば都庁が建設される。誘致というより、マップ内の人口をいかにして増やすかが課題だ。" |
| 中級 (intermediate) | 10店舗経営する (operate 10 stores) | "ひとつのマップにはライバル店を含めて10店舗までしか建設できない。よって、いかにライバルを撤退させるかが課題。" |
| 上級 (advanced) | オーナー評価を★★★★★にする (5-star owner rating) | "毎年1月1日に表示の5種類のオーナー評価を、すべて5つ星にできればクリア条件が満たされる。特に年商が課題だ。" |

CONFIRMED-OFFICIAL, page 11. **CONFIRMS exactly** PROJECT_MEMORY.md
section 14's three previously-PROVISIONAL scenario goals — now upgradable
to CONFIRMED-OFFICIAL (beginner: population/metropolitan-govt attraction
✓; intermediate: 10-store ✓; advanced: 5-star owner rating ✓).

Advanced-tier numeric clear-condition targets (page 11, "クリア条件" panel,
CONFIRMED-VISUAL): 店舗数=10店舗必要 / 累積来客数=20万人程度 / 年商=3000万
円程度 / 町人口=30000人 / 全店舗評価=全店5つ星が最高. **NEW** — concrete
numeric targets for all 5 owner-evaluation categories named in section 1.5
above (10 stores, ~200,000 cumulative visitors, ~¥30,000,000 annual
revenue, 30,000 town population, all stores 5-star), extending
PROJECT_MEMORY.md section 14 (which only had a beginner-tier population
figure of ~20,000, for the *different* beginner scenario) and directly
answering part of section 17's "Exact scenario start conditions and
victory/failure conditions" gap.

"極上マップの出現条件 — 初級、中級、上級の各マップをクリアした状態でプレイ
すると、**極上マップ**がプレイ可能になる。スタート当初からライバル店舗がす
でに**5店舗**あり、いかにしてライバルを牽制するかが問題だ。" CONFIRMED-
OFFICIAL, page 11. **CONFIRMS** PROJECT_MEMORY.md section 14's "A hidden
additional map/mode is also reported after clearing the standard modes,"
and quantifies it: named 極上マップ ("Ultimate" map), unlocked after
clearing all 3 standard tiers, starts with 5 rival stores already present.

---

## 6. 補足 (Supplement) — book page 12

### 6.1 Layout save / troubleshooting

"店舗のタイプひとつに対し、1種類の内装レイアウトが保存できる。試行錯誤が必
要なレイアウト作業だけに、儲かる店舗の内装は必ず保存しておくこと。" CONFIRMED-
OFFICIAL, page 12. NEW — confirms only 1 saved layout per store *type*
(not per individual store); `game`'s existing sample-layout system (task
#37) has no such per-store-type single-slot constraint.

"トラブル — 店内の客がまったく動かなくなってしまったり、店から客が出られな
くなることがまれにある。このような場合はカーソルで客を指定し、つまみ出して
しまおう。" CONFIRMED-OFFICIAL, page 12. NEW — confirms the original game
itself has known customer-pathing deadlock bugs, with an official
"manually remove a stuck customer" escape hatch. Relevant precedent, not
currently modeled (no stuck-customer detection/removal exists in `game`).

### 6.2 Event guide table (イベントガイド)

| イベント | 発生条件 | 備考 |
|---|---|---|
| 寄付 (donation) | 手持ち資金が15億円以上で月が変わる | 10億円以上の資金が強制的に寄付金として差し引かれる。各店舗の評価が上がる。 |
| 万引き (shoplifting) | 顧客のマナーが店舗の警備値よりも悪い場合 | マナーの悪い客が購入しようとした商品が、店舗の売上からマイナスされる。 |
| 火災/強盗 (fire/robbery) | 店舗周囲16×16エリアにセキュリティ施設が無い場合 | 火災は消防車、強盗は交番が周辺に必要。警備値より人気が高いと発生しやすい。 |
| 業界誌掲載 (trade-magazine feature) | 人口1万人以上、マップ内に5店舗以上ある場合 | 店長のパラメータ値が若干だが上昇する。 |
| コンビニコンテスト (Conveni contest) | 人口1万人以上、マップ内に5店舗以上ある場合 | 店舗数(ライバル店を含む)×1000万円が賞金。ライバル店が選ばれることもある。 |
| アイドル (idol) | 来店数が1万人以上で、以後1万人ごとに | 警備値の低い店舗が選ばれることもある。全店の人気が100になる。 |

CONFIRMED-OFFICIAL, page 12. **NEW/CONFIRMS mixed**:
- Donation (寄付) is entirely NEW — not recorded anywhere in PROJECT_
  MEMORY.md: cash ≥ ¥1.5 billion at month-end forces a mandatory donation
  of the amount over ¥1 billion, raising all stores' rating.
- Shoplifting/fire/robbery: CONFIRMS PROJECT_MEMORY.md section 12's list
  ("shoplifting, robbery... security below 100... fire") and directly
  matches section 5.3's newly-transcribed 16×16-tile security-facility
  radius — same radius, cross-confirmed from a different page of the same
  book.
  - "警備値より人気が高いと発生しやすい" — NEW: fire/robbery risk is framed
    relative to popularity exceeding security, not simply security <100 in
    absolute terms as PROJECT_MEMORY.md section 12 currently states — a
    refinement worth reconciling.
- Trade-magazine feature/contest: population ≥10,000 AND ≥5 stores on the
  map. CONFIRMS PROJECT_MEMORY.md section 12's event list and
  `store_events.gd`'s existing (task #30) magazine/contest eligibility
  gate — the contest prize formula "(store count incl. rivals) × ¥10M" is
  already ported per PROJECT_MEMORY.md task #30's own note, so this is
  primarily a CONFIRMS/cross-reference.
- Idol: CONFIRMS section 11's "+100 popularity" (via "全店の人気が100にな
  る") and the 10,000-visitor-then-every-10,000 trigger, matching
  `visitor_milestone.py` exactly.

### 6.3 Scenario clear / game over conditions

"シナリオクリア — 各マップのクリア条件を満たすとエンディングが流れる。"
"ゲームオーバー — **破産**または、**クリア条件を満たさず100年経過**すると
ゲームオーバー。" CONFIRMED-OFFICIAL, page 12. **CONFIRMS exactly**
`store_events.scenario_time_limit_exceeded`'s existing 100-year time limit
(task #27/decision 0091 area) and the bankruptcy terminal condition
(`MonthBoundaryBankruptcyPolicy`) — both already implemented, now
independently reconfirmed from this second book.

---

## 7. Design Showcase example fixture/product tables — book pages 20–21

Two fully-worked example store layouts ("塩田ストア本店"/"菅ストア本店"),
each with a per-product placement table: 商品名 (product) / 商品棚（サイズ）
(fixture type + footprint) / 維持費（時間）(maintenance, unit labeled
"time" — see caveat) / 収容力 (capacity) / 注目度 (attention).

**Caveat on the 維持費（時間） column**: its header literally reads
"maintenance (time)," and its values (single/double/triple-digit numbers
like 1, 2, 3, 40, 100, 150) are far smaller than `baseline_data.py`'s
`FIXTURES`' already-CONFIRMED_OFFICIAL per-day yen maintenance figures for
comparable fixtures (hundreds to thousands of yen/day). This column's unit
is therefore **not confidently yen-per-day** and is presented here
verbatim without assuming a direct correspondence — flagged `UNCERTAIN`
as to what exactly it measures (possibly a relative index, or a per-hour
figure). Treat this table as illustrative "which fixture SKU + size was
used for which product, in one example store" reference data, not a new
base pricing source; `baseline_data.py`'s `FIXTURES` (from book1's own
DATA LIST table) remains the authoritative base fixture-pricing source.

塩田ストア本店 (パターン1, 合計36スペース, 観葉植物×8, ベンチ×5, 駐車場収
容力40):

| 商品名 | 商品棚(サイズ) | 維持費(時間) | 収容力 | 注目度 |
|---|---|---:|---:|---:|
| パン類 | 常温棚(1x3) | 3 | 120 | 10 |
| パン類 | 常温棚(1x1) | 1 | 40 | 10 |
| 弁当類 | 常温棚(1x3) | 3 | 120 | 10 |
| 冷たい飲料 | 冷蔵ワゴン(1x2) | 100 | 70 | 20 |
| 温かい飲料 | 温ジュース×2 | 140 | 40 | 20 |
| 酒類 | 冷蔵ワゴン(1x2) | 100 | 70 | 20 |
| レトルト類 | 常温棚(1x2) | 2 | 30 | 10 |
| インスタント類 | 常温棚(1x2) | 2 | 30 | 10 |
| 菓子類 | 常温棚(1x2) | 2 | 80 | 10 |
| 日用品類 | 常温棚(1x2) | 2 | 80 | 10 |
| 文房具類 | 常温棚(1x2) | 2 | 80 | 10 |
| アイスクリーム | 冷凍棚(1x1) | 150 | 50 | 10 |
| 肉類 | 冷蔵ワゴン(1x1) | 40 | 10 | 20 |
| 野菜類 | 冷蔵ワゴン(1x1) | 40 | 10 | 15 |
| 下着類 | 常温棚(1x1) | 1 | 40 | 30 |
| 本類 | 常温棚(1x1) | 1 | 40 | 30 |
| イベント商品 | イベントケースワゴン | 50 | 30 | 40 |
| おでん | おでん | 80 | 10 | 30 |
| たばこ | たばこ自販機 | 80 | 10 | 30 |
| コピー用紙 | コピー機(1x1) | 50 | 20 | 10 |
| 宅急便申込書 | レジ(1x2) | 70 | 30 | 25 |

菅ストア本店 (パターン2, 合計32スペース, 観葉植物×6, ベンチ×7, 駐車場収容
力60):

| 商品名 | 商品棚(サイズ) | 維持費(時間) | 収容力 | 注目度 |
|---|---|---:|---:|---:|
| 酒類 | 冷蔵ワゴン(2x2) | 130 | 40 | 30 |
| 冷たい飲料 | 冷蔵ワゴン(1x2) | 70 | 20 | 20 |
| 菓子類 | 常温棚(1x2) | 2 | 30 | 20 |
| 冷凍食品 | 冷凍ワゴン(1x2) | 130 | 20 | 20 |
| アイスクリーム | 冷凍ワゴン(1x2) | 130 | 20 | 20 |
| たばこ | 常温棚(1x2) | 2 | 80 | 60 |
| パン類 | 常温棚(1x2) | 2 | 80 | 40 |
| イベント商品 | イベントケースワゴン(1x2) | 80 | 60 | 40 |
| 本類 | 常温棚(1x2) | 2 | 80 | 10 |
| 文房具 | 常温棚(1x2) | 2 | 80 | 10 |
| 弁当類 | 常温棚(1x2) | 2 | 80 | 10 |
| 野菜類 | 冷蔵棚(1x1) | 50 | 60 | 60 |
| 肉類 | 冷蔵棚(1x1) | 50 | 60 | 60 |
| 魚類 | 冷蔵棚(1x1) | 50 | 60 | 60 |
| おでん | おでん | 80 | 10 | 30 |
| 宅急便申込書 | レジ(1x3) | 80 | 90 | 30 |

CONFIRMED-VISUAL/CONFIRMED-OFFICIAL (printed table), page 20–21, moderate
confidence on individual cells given table density — spot-check before
implementation use. Two general callout notes accompanying both tables
(CONFIRMED-OFFICIAL, page 20): "(*1) ワゴンの方が多い棚とワゴンの違いは収
容できる商品の点数と注目度。よくよく考えないと個数が少ない割に注目度も低か
ったりするので注意が必要" (wagons vs. shelves trade off capacity against
attention — not a strict upgrade either way) and "(*2) ベンチなどを多めに
配置 — ベンチ、観葉植物、噴水は直接的にサービス度に影響を及ぼすものだ."

---

## 8. Store-concept flavor pages — book pages 26–47 (summary only)

Pages 26–47 ("パーソナルコンビニデザイン") are themed store-concept design
advice — a real store photo/type or fictional locale (e.g. "中学校の近く,"
"丸の内のようなオフィス街," "軽井沢のような避暑地," "南極," "孤島") paired
with a small full-layout screenshot and a "POINT ITEM" callout naming 1–2
product categories recommended for prominent placement given that theme.
These are qualitative design/flavor guidance, not additional confirmed
mechanics or numeric data, and are not transcribed field-by-field here.
Representative POINT ITEM pairings (all CONFIRMED-VISUAL/CONFIRMED-
OFFICIAL, page as noted, for future scenario/level-design flavor use
only):

- 中学校の近く (p.27): 冷たい飲料 + パン類
- 小学校の近く (p.27): アイスクリーム + 菓子類
- 大病院のそば (p.27): 薬品 + 日用品
- 丸の内のようなオフィス街 (p.28): 冷たい飲み物 + 弁当類
- 東京郊外の国道沿い (p.29): 日用品 + 薬品
- 私鉄沿線駅前銀座 (p.30): 野菜類 + たばこ
- 上野のようなターミナル駅近辺 (p.31): 弁当類 + 現金 (cash/ATM-like fixture)
- 東京1時間圏内のベッドタウン (p.33): 野菜類 + 内類(肉類)
- 兜町のような証券街 (p.33): パン類 + たばこ
- ヤングファミリーの多い新興住宅街 (p.33): レトルト類
- 大型パチンコ店の横 (p.34): たばこ + 酒類
- お台場のような埋め立て地 (p.35): パン類 + アイスクリーム
- 横須賀のような米軍基地近辺 (p.35): アイスクリーム + インスタント類
- 軽井沢のような避暑地 (p.37): パン類 + アイスクリーム
- ソーホーのような芸術家街 (p.37): 酒類 (洋酒中心) + 本類
- プールの近く (p.39): 冷たい飲料 + おでん
- 荒川のような河川敷 (p.39): 弁当類 + パン類
- 公営運動場の近く (p.39): 弁当類 + たばこ
- 有楽町のような大型店の多い街 (p.40): 冷たい飲料 + 肉類
- 成城・田園調布のような高級住宅地 (p.40): 酒類 + 肉類
- 中華街そば (p.40): 中華まん + 肉類
- 新宿歌舞伎町のような繁華街 (p.41): 酒類 + たばこ
- 札幌ラーメン横丁内 (p.43): 冷たい飲料 + 中華まん
- 大阪ミナミのような食い倒れ街 (p.43): 薬品 + たばこ
- 屋台村内 (p.43): 弁当類 + 冷たい飲料
- 箱根のような観光地 (p.44): 酒類 + 菓子類
- 北欧のような白夜の国 (p.44): 菓子類 + 本類
- 草津のような温泉街 (p.44): 酒類 + 冷たい飲料
- 京都のような古都 (p.45): 弁当類 + 温かい飲料
- 孤島 (p.46): 本類 + 電気製品類
- 富士の樹海内 (p.46): 薬品 + たばこ
- ジャングルの中 (p.46): 肉類 + 下着類
- 南極 (p.47): 菓子類 + おでん

---

## 9. Cross-check summary

Rough counts across this document: **≈19 NEW** findings (not previously
represented anywhere in the codebase/docs), **≈15 CONFIRMS** findings
(match an existing CONFIRMED/PROVISIONAL/HYPOTHESIS claim, upgradable or
already-implemented), **≈5 CONTRADICTS/flagged-uncertain-but-high-stakes**
findings. (Approximate — several entries are mixed NEW+CONFIRMS.)

### 9.1 Promotion cost/popularity table — explicitly requested comparison

**This Quick Reference book's own page 3 does not restate a promotion
cost/popularity numeric table at all** (section 1.4 above) — it only lists
the 5 promotion types in cost-ascending order with two qualitative rules.
There is therefore **no new table from this specific source to compare
against PROJECT_MEMORY.md section 11**. For completeness, the pre-existing
three-way comparison already on record (not new information from this
transcription, restated here for visibility since the task asked for a
careful check):

| Promotion | PROJECT_MEMORY §11 (wiki, CONFIRMED-COMMUNITY) | book1 (strategy guide, CONFIRMED-OFFICIAL, `strategy-guide-full-decode` §2) | `baseline_data.py` `PROMOTIONS` (as currently coded) |
|---|---:|---:|---:|
| Direct mail | ¥100,000 / +12 | ¥100,000 / +12 | ¥100,000 / +12 |
| Newspaper | ¥500,000 / +20 | ¥500,000 / +20 | ¥500,000 / +20 |
| Airship | ¥1,000,000 / **+30** | ¥1,000,000 / **+40** | ¥1,000,000 / **+40** (guide wins) |
| Radio | ¥3,000,000 / **+50** | ¥3,000,000 / **+60** | ¥3,000,000 / **+60** (guide wins) |
| TV | ¥5,000,000 / **+100** | ¥5,000,000 / **+90** | ¥5,000,000 / **+90** (guide wins) |

This conflict (wiki vs. book1) was already found and deliberately resolved
in favor of book1 in `baseline_data.py` (comment at lines 474–480, citing
independent confirmation "on four separate primary-source pages"). This
Quick Reference book neither confirms nor further disputes either side of
that existing resolution.

### 9.2 Highest-priority items for the reviewer

1. **Wage formula CONTRADICTS current implementation** (§1.2): the guide
   states, twice independently, `wage = hourly_rate × business_hours`;
   `game`'s `_apply_daily_staff_wages()` currently charges a flat full-day
   amount regardless of configured opening hours.
2. **Weather category-naming CONTRADICTS an existing code comment**
   (§1.7): `remake_customer_share.py`'s `BAD_WEATHER_VALUES` comment
   claims the guide's 5 columns are 快晴/大雨/雪/台風/荒天; this
   transcription reads them as 快晴/曇り/雨/台風/荒天 with 荒天 defined as
   an umbrella of 大雨・雷雨・台風・大雪. Needs re-verification before
   either side is trusted.
3. **Service fixture bonuses CONTRADICT PROJECT_MEMORY §4** (§2.4): bench
   +4 (not +3), fountain +30 (not +25); potted plant +2 matches.
4. **Parameter growth/anger-penalty matrix** (§3.2) potentially contradicts
   two already-"confirmed" constants (`staff_growth.gd`'s +1 skill-pair
   assumptions, `checkout_anger.gd`'s -2 magnitude) — flagged `UNCERTAIN`
   pending a higher-confidence re-read, but too high-stakes to omit.
5. **Incidental purchase count = ~3 items/customer** (§4.2): upgrades a
   standing HYPOTHESIS to CONFIRMED-OFFICIAL and unblocks the
   previously-deferred incidental-purchase/fixture-attention system.
6. **Fixture maintenance also scales with business hours** (§1.2), same
   shape of gap as the wage formula but for `_apply_daily_fixture_
   maintenance()`.
7. **Security facility bonuses quantified** (§5.3): fire station
   (2x3, +5/area, max +30) and police box (2x2, +10/area, max +40) within
   a 16×16-tile radius — previously only qualitative.
8. **Price-margin/discount UI mechanic** (§2.2): confirms the shape of the
   still-unimplemented price-setting mechanic (`price_change_pct`).
9. **Advanced-scenario numeric clear-condition targets** (§5.4): 10
   stores / ~200k cumulative visitors / ~¥30M annual revenue / 30k town
   population / all-5-star rating.
10. **Attraction-facility footprint/population table** (§5.2) and
    **city-hall population threshold >10,000** (§4.1) fill named gaps in
    PROJECT_MEMORY.md section 17.

### 9.3 Items needing re-verification before implementation

Flagged `UNCERTAIN` above and repeated here for visibility: business-hours
option ③'s end time (§1.1); weather-percentage table digits for July/
September/December specifically (§1.7); the weather table's column-header
naming generally (§1.7, ties into item 2 above); the parameter growth/
anger-penalty matrix's exact column mapping (§3.2, ties into item 4
above); the station shopping-population figure (2,000 on page 4 vs. 2,240
on page 8 — possibly different size tiers, §4.1); and the Design Showcase
tables' 維持費（時間） column unit (§7).
