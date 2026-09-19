# 「ザ・コンビニ 新人店長実習マニュアル」第1章 全ページ転記 (Part 1 of 2)

Prepared: 2026-09-19

## 0. Source and scope

Source file: `/root/.claude/uploads/c93fedf4-bdc5-5547-8c6b-e12d6e589ab4/f60ccaf4-downloadfile.PDF`
("PDF file 1 of 2" for this book). Book title: 「ザ・コンビニ 新人店長実習
マニュアル」("The Conveni New Manager Training Manual"). 33 PDF pages, each a
scanned two-page spread; all 33 pages/spreads (book pages 1-71, i.e. the full
第1章 新規開業編 pp.6-42 and 第2章 事業拡大編 pp.44-71 through the start of the
Q&A) were read in full via the `pages` parameter in two batches (1-20, 21-33).
No page was skipped.

**Important cross-check finding up front**: this book is the same physical
source already cited in the codebase as `本1.pdf` / `STRATEGY_GUIDE` (see
`reference_sim/conveni_sim/baseline_data.py`'s `STRATEGY_GUIDE` constant,
which points to `docs/research/strategy-guide-full-decode-2026-09-16.md`).
That prior session already transcribed and ported the large majority of this
book's tables into `baseline_data.py` at `CONFIRMED_OFFICIAL`. Consequently
most of what follows is independent **re-confirmation** (a second read of the
same primary source, useful because it re-derives every number from the raw
scan rather than trusting the prior transcription), with a smaller number of
genuinely **NEW** facts this book states that had not yet been captured
anywhere, and a few **already-known internal conflicts within the guide
itself** that this reading reconfirms with fresh page citations. No new
true contradiction against a previously-CONFIRMED value was found (see
section 12 for the one meaningful internal-conflict case, which the code
already documents).

Evidence tags used below follow `PROJECT_MEMORY.md` section 15:
`CONFIRMED-OFFICIAL` (stated as text/table in this printed guide),
`CONFIRMED-VISUAL` (only visible in a screenshot, not restated in prose).
Per the task brief, guide table/prose content defaults to
`CONFIRMED-OFFICIAL`; in-game screenshot-only numbers not restated in body
text are marked `CONFIRMED-VISUAL`.

---

## 1. Store location, land acquisition (book pp.6-9)

### 1.1 Land purchase cost formula — **NEW**

Book p.6 states explicitly, for an empty lot:

> 必要金額=土地代 ※地代~(エリア地価×エリア数)

and for a lot with an existing building:

> 必要金額=土地代+建物買収費 ※買収費~(建物評価額の50%)

i.e. **land price = area land price × number of areas**, and **buying out an
occupied lot = land price + 50% of the existing building's appraised value**.
`CONFIRMED-OFFICIAL`.

**Cross-check**: `reference_sim/conveni_sim/remake_land_value.py` currently
implements land value **growth over time** as an explicit
`REMAKE_BALANCED_DEFAULT` house rule, with its own docstring stating "No
exact formula... is published" for land value. That remains true for the
*growth* formula. But this specific **acquisition-cost** formula (area price
× area count; +50% of building appraisal for an occupied lot) is a distinct,
simpler fact that is **not represented anywhere in the codebase** — no
existing file computes a building-buyout premium or names "area count" as
the land-price unit. This is a real NEW finding, orthogonal to the
already-known land-value-growth gap.

### 1.2 Recommended-site checklist (book p.6) — CONFIRMS section 13/PROJECT_MEMORY

Five "おすすめ物件" criteria stated in prose: 道路に面している・駅に近い,
地価がほかより高い, アクシデントにあいにくい, 酒・たばこの販売ができる,
役場用地に近い. `CONFIRMED-OFFICIAL` (qualitative, no coefficients). Matches
PROJECT_MEMORY section 13's existing qualitative claims about location
mattering; no numeric formula given (guide explicitly leaves siting
math undetermined) — do not invent one, per CLAUDE.md.

### 1.3 Store-to-store minimum distance / permit exclusion rings (book p.7)

Diagram: concentric rings labeled 5 / 7 / 11 / 15 around a store, captioned
店建設可能 (5), たばこ販売可能 (7), 酒類販売可能 (11), 薬品販売可能 (15).
`CONFIRMED-OFFICIAL`.

**Cross-check: CONFIRMS.** `baseline_data.py`'s `_PERMIT_FEE_AND_DISTANCE_YEN_TILES`
already encodes exactly `tobacco: 7 tiles`, `alcohol: 11 tiles`,
`medicine: 15 tiles`, with a comment citing the same 5/7/11/15 diagram and
correctly noting the 5-tile ring is the store-to-store minimum, not a
permit. My independent re-read matches exactly.

### 1.4 Permit fee table (book p.9)

酒類 3,000,000円 / たばこ類 7,000,000円 / 薬類 10,000,000円, with body text
confirming the sum "合計2千万円になってしまう". `CONFIRMED-OFFICIAL`.

**Cross-check: CONFIRMS.** Matches `PERMITS` exactly (tobacco ¥7,000,000 /
alcohol ¥3,000,000 / medicine ¥10,000,000).

---

## 2. Store size/scale (book pp.10-11) — internal-conflict reconfirmation

Store-selection screenshot (p.10) shows three named sizes with UI-displayed
footprint and cost:

| 規模 | サイズ (screen label) | 建設費用 |
|---|---|---:|
| 小 | 縦10×10 | ¥6,000,000 |
| 中 | 縦12×12 / 横12×12 | ¥12,000,000 |
| 大 | 縦16×16 / 横16×16 | ¥24,000,000 |

`CONFIRMED-VISUAL` (screenshot numbers, restated nowhere else on these two
pages).

**Cross-check: reconfirms an already-documented internal conflict, does
not create a new one.** `baseline_data.py`'s `large_top`/`large_bottom`
`StoreVariant` entries carry `construction_price_yen = 18,000,000` with a
code comment stating verbatim: "the guide's own store-selection screen
(chapter 1) prints 24,000,000 yen for this tier, but its data-table page and
all six of its '大' (large) case-study layouts independently agree on
18,000,000 yen (7 sources vs 1)... an internal conflict in the source
material itself." This session's read of book p.10 is exactly that
chapter-1 store-selection screen, and independently reconfirms the "large =
¥24,000,000" reading on that specific screen. The 18,000,000 value used in
code (majority-source, and independently video-confirmed) is not disturbed;
this is filed as a re-confirmation of the known conflict, not a new one.
Small (¥6,000,000) and medium (¥12,000,000) match the code's `small_*`/
`medium_*` `construction_price_yen` exactly, with no conflict.

Also note: this book's UI screen footprint (10×10/12×12/16×16) is a
different dimension set than the `店舗内` "editable floor" dimensions used
by `STORE_VARIANTS.editable_floor` (5×8, 7×10, 8×12/12×8 etc., sourced from a
separate 店舗データ table not present in this particular PDF). This
distinction is already flagged in the code's comments as a known
"différent notation" gap; nothing new to add here.

---

## 3. Interior layout mechanics (book pp.14-21) — mostly STRATEGY_EVIDENCE, no new numbers

- "通路の幅は人間ふたり分が基本" (aisle width should fit two people) —
  `CONFIRMED-OFFICIAL` qualitative guidance, matches PROJECT_MEMORY section 4
  ("At least 1 tile of passage... checkout fronts need around 2 tiles").
- Shelves (棚) are one-directional access only; wagons (ワゴン) can be
  accessed from all 4 sides. `CONFIRMED-OFFICIAL`, matches
  `FixtureDefinition` naming convention (shelf vs. wagon) already in code,
  no numeric change.
- "棚やワゴンを使うときは最低1ブロックのあきが必要" (shelves/wagons need at
  least 1 open block around them to be usable) — p.65 Q&A, `CONFIRMED-OFFICIAL`.
  Matches PROJECT_MEMORY section 4's "at least 1 tile of passage" claim.
- Popular items placed toward the back of the store pull customers deeper
  in; items placed right at entrance/register get bought and customers
  leave without seeing the rest. `CONFIRMED-OFFICIAL` prose (pp.18-19),
  matches PROJECT_MEMORY section 4's "popular goods placed deeper...
  influence traffic flow." No coefficient given — do not invent one.
- Placing shelves/wagons directly behind or in front of the register, or
  blocking the entrance, is explicitly called out as a failure mode (p.19,
  p.41 diary). `CONFIRMED-OFFICIAL` behavior rule, not yet enforced as a
  hard validation rule anywhere in `game/scripts/domain/store_layout.gd`
  beyond the existing generic occupancy/reachability checks — **NEW as an
  explicit "don't block register/entrance" rule**, though the underlying
  reachability check already prevents the store from becoming fully
  unplayable.
- Outdoor space usage: vending machines, parking are explicitly called out
  as ways to make exterior space productive ("店外を上手に使えば集客率が
  格段にアップ"), p.19. Qualitative, `CONFIRMED-OFFICIAL`. No outdoor/
  exterior spatial model exists in `game/` yet (same gap task #34 already
  documented as out of scope).

---

## 4. Business policy: pricing and hours (book pp.22-23)

- 商品利益率 (product margin rate) can be set store-wide (e.g. "全体に設定
  5%UP") or per-product. `CONFIRMED-OFFICIAL`/`CONFIRMED-VISUAL` (screenshot
  shows "全商品平均利益率 45%"). Matches `store_rating.py`'s
  `price_change_pct` input concept (percent change from standard price) —
  **CONFIRMS** that this field is store-controllable at both global and
  per-item granularity, matching `docs/research/strategy-guide-full-decode-
  2026-09-16.md` section 12 and section 22.1's already-noted
  `individual_override`/`global_price_policy` design.
- Diagram (p.22) explicitly ties 販売価格率 (sale price ratio) direction to
  five other variables' direction, all qualitative, no coefficients: 低い
  ⇄ 高い maps to もうけ小⇄大, 集客率増加⇄減少, 人口増加⇄減少, 店の評価
  アップ⇄ダウン. `CONFIRMED-OFFICIAL` causal-direction evidence only.
  Matches `store_rating.py`'s existing modeling of `price_change_pct` as one
  of five rating inputs — **CONFIRMS** the qualitative direction, adds no
  new coefficient (none should be invented, per CLAUDE.md and the guide's
  own silence on the exact multiplier).
- Business-hours policy screen shows: 営業時間 (e.g. AM10:00~PM6:00), 社員
  ベースアップ率 (staff base-up rate, e.g. 3%), 賃金交渉に応じる
  (respond to wage negotiation: はい/いいえ). `CONFIRMED-VISUAL`.
- Recommended starting hours: "初めは7:00〜11:00営業" (start with a short
  window while staff skill/replenishment can't keep up with longer hours),
  then extend once staff have grown; full 24-hour operation is explicitly
  discouraged for roughly the first year ("開店から1年くらいは店員育成の
  ため閉店時間を設定した営業を心がけよう"). `CONFIRMED-OFFICIAL`. Matches
  PROJECT_MEMORY section 10's existing "24-hour operation is not always
  economically optimal" — **CONFIRMS**, and adds the concrete example
  window (7:00-11:00) plus the "~1 year" staff-maturity guidance, which
  were not previously recorded verbatim.
- "営業時間帯によって来店客層が変わる" (customer demographics vary by time
  of day) — pie chart: 昼間 (daytime) skews 主婦・学生 (housewives/
  students), 夜間〜深夜 (night/late) skews 独身者 (singles); night/late
  buyers lean toward alcohol/tobacco. `CONFIRMED-OFFICIAL` qualitative.
  Matches PROJECT_MEMORY section 6/10's existing framing that opening hours
  affect customer mix; no numeric time-band coefficient given.

### 4.1 Wage negotiation fixed at 3% on PS — **NEW**

Book p.57 footnote states explicitly: **"※PS版は3%固定なので、賃金交渉の
アップ率は無視してもかまわない"** — "the PS version has a fixed 3% [wage
base-up rate], so the wage-negotiation-requested increase percentage can be
ignored." This is a concrete, platform-specific (PS, matching this
project's own PS/SS baseline target) rule: whatever raise a staff member's
individual wage-negotiation event nominally requests, the actual effective
base-up rate on PS is always 3%, matching the `社員ベースアップ率` field
shown on the business-policy screen (section 4 above). `CONFIRMED-OFFICIAL`.

**Cross-check**: no `wage_negotiation`, `base_up_rate`, or equivalent
mechanic exists anywhere in `reference_sim/` or `game/scripts/domain/` —
`staff.members`' `salary_yen_per_day_24h` (task #47) is a static value with
no negotiation/raise mechanic wired at all. This is a genuinely **NEW**,
previously-unrecorded, concrete rule (not merely "wages can rise" but "the
requested raise is always overridden to 3% on this platform").

---

## 5. Staff hiring and stats (book pp.24-29)

- Store can employ up to 3 staff ("ひとつのお店に雇えるのは3人まで").
  `CONFIRMED-OFFICIAL`. Cross-check: `PROJECT_MEMORY.md` section 6 does not
  currently state this cap explicitly; `game/`'s vertical slice currently
  models exactly 2 active staff (`staff.members`), well under this cap, so
  no contradiction, but this 3-person-per-store cap itself is **NEW**
  explicit confirmed data (not previously recorded verbatim anywhere found
  in `docs/research/`).
- 7 hiring-time parameters named explicitly on the post-hire staff card:
  体力 (stamina), 学歴 (education), レジ (register), 補充 (replenishment),
  警備 (security), 清掃 (cleaning), 接客 (service/customer-facing).
  `CONFIRMED-OFFICIAL`, matches `StaffCandidate`'s existing 5 operational +
  stamina/education fields.
- **Before hiring**, only 4 parameters are visible on a candidate's
  application card: 体力, 学歴, 敏捷性 (agility), 社交性 (sociability) —
  the other parameters "本当の能力までは想像できない" (the true
  register/replenish/security/cleaning/service numbers cannot be inferred
  before hiring). `CONFIRMED-OFFICIAL`. This matches PROJECT_MEMORY section
  6's "Hiring-screen stats and transfer/assignment-screen operational
  stats are distinct" claim — **CONFIRMS** that split precisely, with the
  exact 4-vs-7 field boundary.
- **Threshold table mapping the 4 pre-hire stats to post-hire ceilings —
  NEW, with concrete numeric bands** (book p.24 box "影響をおよぼす能力"):

  | 事前能力 | 影響先 | 普通 | 高い |
  |---|---|---|---|
  | 体力 | スタミナ(仕事の持続力) | 40〜69 | 70〜100 |
  | 学歴 | レジ・セキュリティ能力 | 40〜69 | 70〜100 |
  | 敏捷性 | 商品補充、店内移動速度 | 40〜69 | 70〜100 |
  | 社交性 | サービス、清掃能力 | 40〜69 | 70〜100 |

  `CONFIRMED-OFFICIAL`. This gives an explicit 0-100 scale interpretation
  band (40-69 = "普通"/normal, 70-100 = "高い"/high) for each of the 4
  pre-hire stats, and confirms the education→register/security,
  agility→replenishment/movement-speed, sociability→service/cleaning
  mappings already implied qualitatively by PROJECT_MEMORY section 6
  ("Education is related to register/security ceilings... Agility relates
  to replenishment ceiling... Sociability relates to customer service and
  cleaning ceilings" — **CONFIRMS** those three mappings exactly) — but the
  **40-69/70-100 numeric bands themselves are new**; no threshold table for
  interpreting these 4 stats exists anywhere in `baseline_data.py` or
  `store_value.py` today.
- 店長の教育パラメータ (manager's own 教育 stat) controls how fast
  subordinate staff grow, and "店長能力が低いと教育効果が十分出ない"
  (low manager ability blunts the training effect). `CONFIRMED-OFFICIAL`
  qualitative. Matches PROJECT_MEMORY section 6's "store-manager education
  affects staff growth" and task #48's already-noted (and deliberately
  unported, no "who is manager" designation) manager-education growth
  bonus gap — **CONFIRMS** the existence of this mechanic, still no
  coefficient given (guide gives none), so task #48's decision to leave it
  unported remains correct.
- **Work-type → skill growth diagram (book p.26 box "仕事内容とパラメータ
  変化の関係") — CONFIRMS existing code exactly:**

  | 作業 | 成長する能力 |
  |---|---|
  | ひとり分のレジを打った | レジ、サービスがアップ |
  | ひとつの棚に補充 | 補充、清掃、警備がアップ |
  | ひとつのエリアを掃除 | 清掃、警備がアップ |

  `CONFIRMED-OFFICIAL`. This is the exact source diagram already cited in
  `reference_sim/conveni_sim/staff.py`'s `WORK_GROWTH_SKILL` and
  `staff_growth_resolution.py` (task #48/decision 0117): checkout growing
  register+service, replenish growing replenishment+cleaning+security,
  clean growing cleaning+security. My independent transcription matches the
  already-ported mapping exactly — **CONFIRMS**. The *increment amount*
  (+1) for the two `EVIDENCE_BACKED_UNIT_GROWTH` entries
  (replenish→replenishment, clean→cleaning) stays outside what this page
  states (guide shows only which skills grow per task, not by how much),
  so the existing REMAKE_BALANCED_DEFAULT-vs-evidence split in that file is
  unaffected.
- "仕事に失敗すると能力がダウン" (failing a task can lower a skill) —
  `CONFIRMED-OFFICIAL` qualitative, matches `checkout_anger.gd`'s already-
  ported `-2` skill delta mechanic conceptually (task #49), though this
  page's "失敗" framing is about a staff member botching a task, not
  specifically the customer-anger trigger `checkout_anger.gd` models — a
  related but not identical mechanic; flagged for awareness, not a
  contradiction.
- Salary table (book p.27, "◆年齢別・社員の基本時給(円)"):

  | 年齢 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 時給 | 250 | 300 | 350 | 400 | 450 | 500 | 550 | 600 | 650 | 700 |

  `CONFIRMED-OFFICIAL`. **Cross-check: CONFIRMS exactly.** Matches
  `baseline_data.py`'s `SALARY_TABLE` verbatim (ages 15-60, wages 250-700).

---

## 6. Opening, trade-area radius, customer research (book pp.30-33)

- Trade-area radius by mode of transport (book p.31, "来店手段 / エリア
  半径" table): 徒歩20 / 自転車40 / バイク60 / 自動車70. `CONFIRMED-OFFICIAL`.
  **Cross-check: CONFIRMS exactly.** `baseline_data.py`'s
  `TRADE_AREA_RADIUS_TILES` (`TradeAreaRadiusEntry`) already carries this
  table verbatim, cited to the same book p.31.
- "店の売り上げがアップすれば評判を聞きつけた人が移住してくる人の数が
  増える" (higher sales attract more residents to move in, growing the
  town) — `CONFIRMED-OFFICIAL` qualitative causal link between store sales
  and population growth. Matches PROJECT_MEMORY section 13's "land values
  rise as the town develops" framing but adds the specific sales→migration
  causal direction; no formula given.
- 建物クリックで人口を確認できる (clicking a building shows its resident
  count) — `CONFIRMED-VISUAL` UI behavior, no new number.
- Customer archetype-to-building mapping (book p.31 box "客層にあわせた
  商品をそろえる"): オフィス街→サラリーマン・OL, 学校→学生, 住宅地→主婦・
  子供. `CONFIRMED-OFFICIAL`. **CONFIRMS** PROJECT_MEMORY section 7's
  "Observed customer groups include office workers, students, housewives"
  claim with an explicit source-building mapping.
- Customer individual-data inspection (p.32-33): the single most important
  field on a customer's personal-data popup is "欲しい商品" (wanted item);
  a survey (アンケート, run at most once effectively per month —
  "月に一度実行してみよう") reveals aggregate 買った商品 (items bought)
  and ほしかった商品 (items wanted) counts store-wide. `CONFIRMED-OFFICIAL`.
  Matches PROJECT_MEMORY section 7's customer-preference framing —
  **CONFIRMS**, and clarifies survey cadence guidance (monthly), though
  this is presented as player advice, not an enforced cooldown, so it
  should not be hard-coded as a rule.

---

## 7. Customer behavior / anger, staff-penalty visual (book pp.34-35)

- Angry customer causes "店員全員の能力が下がってしまう" (**every** staff
  member's ability drops, not just the one serving) when a customer gets
  angry enough to storm out. `CONFIRMED-OFFICIAL`, with a screenshot
  showing a specific staff card's stats visibly reduced after an angry-
  customer event. **Potential scope difference from existing code**:
  `checkout_anger.gd` (task #49, decision 0118) applies its `-2` penalty
  only to "the currently serving staff member," not to the whole roster.
  This guide passage says the effect is store-wide ("店員全員"). This is
  worth flagging explicitly: **not a hard CONTRADICTS** (both are drawn
  from the same underlying CONFIRMED_COMMUNITY `-2` magnitude per
  `checkout_anger_penalty.py`'s own citation, and task #49's own decision
  doc may already be aware of the wiki's "affects the roster" framing and
  deliberately scoped it down to the serving staffer as a REMAKE_BALANCED_
  DEFAULT simplification) — but this guide page is an **independent,
  official-tier restatement that the effect is store-wide**, which is
  stronger evidence than the existing CONFIRMED_COMMUNITY tag and is worth
  a follow-up look at whether `checkout_anger.gd`'s single-staff-member
  scoping should be revisited.
- Mechanic to preempt an angry customer: selecting an about-to-be-angry
  customer and choosing "つまみ出す" (eject them) before they explode
  avoids the store-wide penalty, but ejecting a customer who was just
  quietly leaving instead (rather than one who is actually about to get
  angry) wastes a legitimate sale. `CONFIRMED-OFFICIAL` mechanic — **NEW**,
  not modeled anywhere in `game/` (no "eject customer" action exists).
- Anger is reported as disproportionately common among older male
  customers ("怒りやすいお客さんは、おじさんやおじいさんに多い").
  `CONFIRMED-OFFICIAL` qualitative — no archetype-specific anger-
  probability modeling exists in code; do not invent a coefficient.

---

## 8. Advertising (book pp.36-37)

Full table (book p.36, "5つの宣伝方法を使いこなして広告しよう"):

| 宣伝方法 | 宣伝費 | 宣伝日時 | 効果 |
|---|---:|---|---:|
| ダイレクトメール | 10万円 | 2日10時 | +12 |
| 新聞広告 | 50万円 | 2日7時 | +20 |
| 飛行船 | 100万円 | 3日15時 | +40 |
| ラジオCM | 300万円 | 1日17時 | +60 |
| テレビCM | 500万円 | 1日19時 | +90 |

`CONFIRMED-OFFICIAL` (explicit table, not just a screenshot).

**Cross-check: CONFIRMS `PROMOTIONS` exactly, and upgrades evidence tier
for several fields.** `baseline_data.py`'s `PROMOTIONS` already has the
exact same cost/trigger_day/trigger_hour/popularity_gain for all 5 methods.
However, only `popularity_gain` on airship/radio/tv is currently tagged
`CONFIRMED_OFFICIAL` — `cost`/`trigger_day`/`trigger_hour` for
newspaper/airship/radio/tv are still tagged `CONFIRMED_COMMUNITY` (wiki),
and direct_mail's four fields are tagged `CONFIRMED_VISUAL` (a single video
frame). Since this printed guide table states **all four fields for all
five promotions** explicitly in one place, every one of those 19 currently-
lower-tier fields (5 promotions × 4 fields, minus the 3 already-official
`popularity_gain`s) is now a candidate to be upgraded to `CONFIRMED_OFFICIAL`
citing this same book p.36 table — no values need to change, only the
evidence tier.

Also note: "このときに価格を下げたりサービスをよくすれば、いままで別の店に
行っていたお客さんもだんだんこちらのお店を利用してくるようになるのだ" —
ties advertising to price/service synergy, purely qualitative, no new
coefficient. And: "翌日になると上がった人気度はドンドン下がってしまう" —
popularity decays daily after a promotion fires, `CONFIRMED-OFFICIAL`
qualitative, **matches** decision 0094's already-documented "guide-confirmed
daily popularity decay for low-rated stores is not modeled... `reference_sim`
itself leaves the decay amount unresolved" — this passage is consistent with
that but still gives no decay rate; nothing to add numerically.

---

## 9. Store rating / evaluation (book pp.38-39) — reconfirms known table conflict

Book pp.38-39 (this same "本1.pdf" book) show the full ★-rank
increase/decrease condition table. My independent transcription:

**Increase (月末決算で3条件クリアなら+5):**

| 現時点評価 | 販売価格率 | サービス | セキュリティ | 清掃 | 前月売上以上 |
|---|---|---|---|---|---|
| ★★★★★ | 30%以下 | 100 | 100 | 100 | 1500万円以上 |
| ★★★★ | 20%以下 | 90以上 | 90以上 | 95以上 | 1000万円以上 |
| ★★★ | 15%以下 | 80以上 | 85以上 | 90以上 | 900万円以上 |
| ★★ | 10%以下 | 70以上 | 80以上 | 85以上 | 700万円以上 |
| ★ | 5%以下 | 60以上 | 75以上 | 80以上 | 500万円以上 |

**Decrease (月末決算で1条件につき-1):**

| 現時点評価 | 販売価格率 | サービス未満 | セキュリティ未満 | 清掃未満 | 前月売上未満 |
|---|---|---|---|---|---|
| ★★★★★ | 101%以上 | 80 | 80 | (100) | 300万円 |
| ★★★★ | 101%以上 | 70 | 70 | 95 | 250万円 |
| ★★★ | 101%以上 | 60 | 65 | 90 | 200万円 |
| ★★ | 101%以上 | 50 | 60 | 85 | 150万円 |
| ★ | 101%以上 | 40 | 55 | 80 | 100万円 |

`CONFIRMED-OFFICIAL` (explicit printed table).

**Cross-check: this exact discrepancy is already known and documented in
code.** `reference_sim/conveni_sim/store_rating.py`'s module comment states
verbatim that it uses "書籍頁74-75... as the primary reading over the
near-duplicate table on 書籍頁38-39, whose security/cleaning thresholds
differed slightly on manual transcription." My fresh, independent read of
book pp.38-39 (this file) reproduces exactly that documented discrepancy —
comparing my transcription above to the code's currently-active pp.74-75-
sourced `UPGRADE_THRESHOLDS_BY_CURRENT_STARS`/`DOWNGRADE_THRESHOLDS_BY_
CURRENT_STARS`:

- Upgrade ★★★ row: code has service=85/security=90/cleaning=95; this
  reading (p.38) has service=80/security=85/cleaning=90.
- Upgrade ★★ row: code has cleaning=90; this reading has cleaning=85.
- Upgrade ★ row: code has cleaning=85; this reading has cleaning=80.
- Downgrade ★★★★★ row: code has below_service=100/below_cleaning=80; this
  reading has below_service=80/cleaning shown as bare "100" (ambiguous —
  possibly "100未満" cropped, or an intentionally-unreachable condition).
- Downgrade rows generally show the same pattern-level shape as the code
  but with several individual cells off by 5-10 points.

**This is not a new contradiction** — it is the exact same book-internal
pp.38-39-vs-pp.74-75 conflict the code already flags and has already
resolved in favor of pp.74-75 (chosen as "primary" specifically because
pp.38-39 is the one flagged as possibly mistranscribed). This session's
transcription of pp.38-39 is recorded here for the record/future
re-verification, but does **not** by itself justify changing the currently-
coded pp.74-75 values, since pp.74-75 is not in this particular PDF file
(it is presumably in the companion `本2.pdf`/Part 2 book covered by the
sibling research agent) and this session cannot re-verify pp.74-75 against
this source.

Additional pp.38-39 facts, not previously flagged as conflicting:

- Evaluation is 1-100 scale, publicly reported once a year as a headline
  ("年に一回、お店の総合評価が示される... ★×5の優秀なコンビニをめざして").
  `CONFIRMED-OFFICIAL`. This "once a year" headline cadence is distinct from
  the monthly increase/decrease mechanic itself (which fires every
  representative month per `store_rating.py`) — worth noting as a UI/
  reporting-cadence detail, not a contradiction of the monthly mechanic.
- Low security directly enables 万引き (shoplifting) and 強盗 (robbery):
  "店員の警備能力が低いと万引きや強盗が起こりやすいお店になってしまい".
  `CONFIRMED-OFFICIAL`, matches PROJECT_MEMORY section 12 — **CONFIRMS**.

---

## 10. Diary / anecdotes (book pp.40-42) — flavor with embedded rules

The "コンビニ珍経営日記" comic-diary page is mostly flavor text, but two
entries restate confirmed mechanics and are worth citing precisely:

- "やっぱり万引きだった" / "やっぱり休憩だった" confirm shoplifting and the
  break-room-occupancy mechanic exist as in-fiction observable events
  (already covered above / PROJECT_MEMORY section 12). No new numbers.
- 学校近くの店は万引きに注意 box (p.59, same theme recurs): stores near a
  school see more shoplifting than average because of the higher child
  customer share. `CONFIRMED-OFFICIAL` qualitative causal claim — **NEW**
  as an explicit stated causal link (school proximity → more shoplifting),
  though no probability coefficient is given, consistent with CLAUDE.md's
  instruction not to invent one.

---

## 11. Facility inducement (book pp.44-45)

Full list with size/period/cost (book p.45, "◆誘致できる施設リスト"):

| 施設 | サイズ | 期間 | 援助額 |
|---|---|---|---:|
| 交番 | 2×2 | 1ヶ月(+0~3日) | 40万円 |
| 消防署 | 2×3 | 1ヶ月(+0~3日) | 60万円 |
| マンション | 2×3 | 1ヶ月(+0~3日) | 420万円 |
| 会社 | 3×3 | 1ヶ月(+0~3日) | 540万円 |
| 体育館 | 2×3 | 1ヶ月(+0~3日) | 420万円 |
| プール | 3×2 | 1ヶ月(+0~3日) | 180万円 |
| 運動場 | 4×5 | 1ヶ月(+0~3日) | 200万円 |
| イベント会場 | 2×2 | 1ヶ月(+0~3日) | 600万円 |
| 幼稚園 | 2×3 | 1ヶ月(+0~3日) | 120万円 |
| 小学校 | 4×4 | 1ヶ月(+0~3日) | 320万円 |
| 中学校 | 5×5 | 1ヶ月(+0~3日) | 500万円 |
| 高校 | 6×6 | 1ヶ月(+0~3日) | 720万円 |
| 大学 | 7×7 | 1ヶ月(+0~3日) | 980万円 |
| 専門学校 | 3×4 | 1ヶ月(+0~3日) | 480万円 |
| 公園 | 2×2 | 1ヶ月(+0~3日) | 200万円 |
| 水族館 | 3×3 | 1ヶ月(+0~3日) | 270万円 |
| 動物園 | 6×6 | 1ヶ月(+0~3日) | 720万円 |
| 遊園地 | 7×7 | 1ヶ月(+0~3日) | 980万円 |

`CONFIRMED-OFFICIAL`.

**Cross-check: CONFIRMS `TOWN_FACILITIES` exactly**, field for field
(footprint and `inducement_aid_yen`), for every one of these 18 facilities —
`police_box`, `fire_station`, `mansion`, `company`, `gym`, `pool`,
`athletic_field`, `event_hall`, `kindergarten`, `elementary_school`,
`middle_school`, `high_school`, `university`, `vocational_school`, `park`,
`aquarium`, `zoo`, `amusement_park`. No discrepancies found in this table.
Also confirms the "1ヶ月(+0~3日)" construction-delay window applies
uniformly to every facility, matching `TownFacilityAnchor`'s existing
`construction_delay_is_nonzero` concept (currently only set `True` for
`fire_station` — this reading shows the +0~3 day variance is stated
identically for **all 18** facilities, not fire-station-specific, so that
field could in principle be generalized, though this is a code-shape
observation, not a data correction).

---

## 12. Police box / fire station security effect (book pp.46-47) — **NEW, resolves a previously-documented research gap**

This is the single highest-value new finding in this book. Prose and boxed
callouts state explicitly:

> ◆交番の場合 (セキュリティ40点アップ)
> ◆消防署の場合 (セキュリティ30点アップ)

i.e. inducing a police box raises the store's security stat by **+40**, and
a fire station by **+30**. `CONFIRMED-OFFICIAL`.

The same two pages also state an explicit **effective range** condition:

> 自分のお店から半径7エリア以上の場所に誘致しても、それはムダというもの
> なのだ。せっかくお金を出して誘致するのだから、自分のお店に有利になる
> 場所に誘致するのは当たり前。できるだけ近くの土地に狙って誘致しよう。

— the facility must be within **7 areas** (same "エリア" unit as the
trade-area-radius table in section 6) of the store to have any effect at
all; beyond that radius, security is unaffected. It further states the
police box's smaller 2×2 footprint (vs. the fire station's 2×3) makes it
easier to fit entirely within that effective range, and that a facility
whose footprint spills outside the effective radius has its security
contribution reduced proportionally ("範囲内から建物がはみ出すと、それだけ
警備能力が減少してしまう"). `CONFIRMED-OFFICIAL`.

**Cross-check: NEW, and directly resolves an already-documented open
research gap.** `docs/research/facility-induction-crosscheck-2026-09-05.md`
section 8 explicitly lists "交番・消防署の初代での正確な警備加算値"
("the exact security-point-addition value for police box/fire station in
the first title") as an **unresolved UNKNOWN**, and separately notes (its
line ~181) that a numeric source *was* seen for this but was deliberately
**not adopted**, because it was judged to be for a later/sequel title, not
this first title. This book — the same `本1.pdf` primary source already
used elsewhere in this project for PS/SS-specific data — gives concrete,
first-title-sourced numbers (+40 / +30) plus the 7-area effective-radius
rule and the footprint-overlap-reduces-effectiveness rule. No file in
`reference_sim/` or `game/scripts/domain/` currently models any numeric
security bonus for police_box/fire_station, or any facility-effective-range
concept at all (`TownFacilityAnchor` carries no security-effect field
today; `_evaluate_store_rating()`'s `security_value` computation is driven
purely by staff `security_skill`/store `size_tier`, with no facility term).
This is genuinely new, actionable, high-confidence data that should be
strongly considered for implementation (it fills exactly the gap
`facility-induction-crosscheck-2026-09-05.md` flagged as needing this kind
of primary source).

Also on these pages: "交番と消防署、誘致するならどっちが得" box states the
police box is the more cost-effective choice overall (smaller footprint,
lower aid cost, higher security-per-yen) — matches the already-coded aid
costs (¥400,000 vs ¥600,000) and adds no new number beyond what's above.

---

## 13. Branch expansion and land value growth (book pp.48-49, 54-55)

- **Branch spacing guidance: ≥20 areas apart — NEW strategic number, ties
  to already-confirmed trade-area-radius table.** Book p.48: "支店どうしは
  ある程度近くの距離をあけてマップをカバーするのがいいのだ。目安として
  徒歩で来店するお客さんの限界20エリア分は離れておこう." `CONFIRMED-
  OFFICIAL`. This explicitly reuses the walking trade-area radius (20 areas,
  section 6's `TRADE_AREA_RADIUS_TILES`) as the recommended minimum spacing
  between the player's own branches, so their trade areas don't fully
  overlap. This specific "branches should be ≥ walking radius apart"
  strategic rule is **not currently represented** in `town_state.gd` or
  `chain_visitor_milestone.gd` (task #30's chain-expansion model is purely
  economic/abstract, with no spatial placement at all yet, consistent with
  task #26's documented decision to defer the spatial map). Diagram (p.48)
  shows exactly "20エリア" between 本店 and each of 4 支店 arranged around
  it.
- Opening a branch raises nearby land value, which in turn makes more
  buildings appear, which increases customer count further — a positive
  feedback loop explicitly stated in prose (p.49). `CONFIRMED-OFFICIAL`
  qualitative, matches PROJECT_MEMORY section 13 and `remake_land_value.py`'s
  already-cited "地価は都市化と年数経過の両方で上昇" evidence — **CONFIRMS**,
  no new coefficient.
- Land squeezed between two of the player's own stores develops faster
  than land near just one store (p.49 diagram, "店にはさまれた土地は
  さらに発展... ふたつのお店の影響をうけて1軒のときよりも地価の上昇率が
  高い"). `CONFIRMED-OFFICIAL` qualitative — **NEW** detail (overlap of two
  *own* stores' influence compounds land-value growth), distinct from the
  already-known "squeeze a rival with land value" tactic (below). No
  coefficient given.
- Deliberately inflating land value around/between a rival store and the
  player's own store(s) to squeeze the rival's economics, with two
  explicit geometric patterns shown (p.54: sandwiching a rival between the
  player's main store and a branch; p.55: placing the player's own store
  between two rival branches to benefit from both stores' zones), then
  retreating the rival once land is built up. `CONFIRMED-OFFICIAL`
  qualitative. **CONFIRMS** `remake_land_value.py`'s own docstring citation
  ("deliberately inflating land value near a rival store is a viable
  competitive tactic," citing `strategy-guide-full-decode-2026-09-16.md`
  section 31.3) with a fresh, independent page citation and two concrete
  geometric patterns; no new coefficient (none should be invented).
- Acquiring (買収) a rival branch: cost scales with the rival branch's own
  sales (a profitable rival branch costs more to acquire; "買収するなら
  早めにするのがお得" — buy early before the price rises). `CONFIRMED-
  OFFICIAL` qualitative, matches PROJECT_MEMORY section 13's "Rival stores
  can be acquired" — **CONFIRMS**, no formula given for the exact
  acquisition price, consistent with the existing "推測禁止" list in
  `strategy-guide-full-decode-2026-09-16.md` section 41.

---

## 14. Second-store opening procedure, rival countermeasures (book pp.50-55)

- New-branch procedure named explicitly as a 4-step checklist: 予算チェック
  → 開設場所を決定 → 新店員を雇う → 店内レイアウト (p.50). `CONFIRMED-
  OFFICIAL` STRATEGY_EVIDENCE, purely procedural, no numbers.
- New-branch opening tactic: set the new branch's margin rate to ≤20%
  ("商品利益を20%以下に"), deliberately running thin/no margin, to win
  customers away from an established rival while the new branch builds a
  customer base. `CONFIRMED-OFFICIAL`, ties to the already-known price↔
  customer-count trade-off (section 4), gives a concrete recommended
  number (20%) but as player *advice*, not a hard game rule — should not
  be hard-coded as a required threshold.
- Rival stores also open their own branches, including sometimes at a site
  the player was targeting, "先に建てられるとどうしようもない" (once a
  rival claims a site first, nothing can be done) — no siting-priority
  formula given. `CONFIRMED-OFFICIAL` qualitative.
- **Rival-store retreat tactics with concrete numbers — NEW.** Book p.53's
  flowchart and prose:
  1. Cut the player's own product margin rate 15-20% below normal near the
     rival's branch to pull its customers away: "新しい店の商品利益率を
     15〜20%オフにする."
  2. Sustain this for several months in a row until the rival branch posts
     losses: "数ヶ月連続で赤字を出す."
  3. The rival branch then withdraws ("ライバル店撤退").
  4. Repeat against its next branch, working back toward the rival's main
     store.

  `CONFIRMED-OFFICIAL`. Cross-check: no rival-AI retreat-threshold logic
  exists anywhere in `reference_sim/` or `game/` yet (no rival-store entity
  is simulated at all — consistent with task #26's documented scope
  decision to defer rival AI entirely). This gives concrete numbers (15-20%
  discount, "several months" of consecutive losses) for a future rival-AI
  implementation, but per `strategy-guide-full-decode-2026-09-16.md`
  section 41 item 19 ("ライバルAI意思決定" is explicitly on the
  "existence confirmed, formula unconfirmed" list), "several months" is not
  a precise trigger count and should not be hard-coded as an exact N
  without further evidence — flagged as strategy-tier evidence for a
  future rival AI's general shape, not a ready-to-code threshold.
- Three listed tactics for winning a rival's customers generally (p.53):
  raise service (fountains/plants, lower margin), get tobacco/alcohol
  permits the rival lacks, hire better staff and move veterans to the new
  branch immediately. `CONFIRMED-OFFICIAL` qualitative, matches multiple
  already-confirmed mechanics (service fixtures, permits, staff transfer)
  — **CONFIRMS**, no new numbers.
- Rival branches can be evaluated before acquiring: "調査する 費用
  ¥500,000" is shown as a distinct paid action from "買収する" itself
  (screenshot, p.55/p.65). `CONFIRMED-VISUAL` — a ¥500,000 rival-
  investigation fee, separate from acquisition cost. **NEW**, not
  represented in any rival-store model in the codebase (none exists yet).

---

## 15. Staff management across a chain (book pp.56-57, 62-63)

- New-branch staff start at low stats regardless of experience elsewhere;
  moving a proven staff member from an existing store to a new one is the
  recommended fix, and staff-to-staff transfer keeps growth per-individual
  rather than per-store. `CONFIRMED-OFFICIAL`, **CONFIRMS** PROJECT_MEMORY
  section 6's "new-store veteran investment... evidence that ability values
  persist per-individual, not per-store" framing (from the earlier
  full-decode doc section 24.6) exactly.
- Wage-negotiation guidance (general, not PS-specific): accept 2-3% base
  raises as reasonable, some staff ask for 10%+ and can be refused outright
  without necessarily losing them ("即刻却下"). `CONFIRMED-OFFICIAL`
  qualitative — superseded in practice on PS by the fixed-3% rule in
  section 4.1 above (this text appears to describe the general/other-
  platform mechanic that the p.57 footnote then says is fixed at 3% on PS
  specifically — i.e. the negotiation UI exists and can nominally request
  any percentage, but the platform always resolves it to 3%).
- "新規開店では新規員は必ずひとり以前の経験者を移動、と同時に新しい店員も
  雇う" (always move one veteran to a new branch while also hiring fresh
  staff there) — same as above, no new number.
- 24-hour operation recommended specifically as the fastest way to grow a
  *new hire's* skill quickly ("早く育てたい社員は24時間営業"), at the cost
  of operational smoothness if mixed with only-veteran staffing.
  `CONFIRMED-OFFICIAL` qualitative — ties 24h hours to staff-growth rate,
  which is not currently modeled (growth in `staff_growth.gd` is purely
  per-completed-task, decoupled from opening-hours length); worth noting as
  a plausible future analogy-based link (more open hours → more completed
  tasks → more growth opportunities), not a new direct coefficient.

---

## 16. Incidents / accidents (book pp.58-59)

- Fire (火事) cause: "お店の警備パラメータが低いとモラルの低いお客さんに
  火をつけられる" (low security enables a low-morals customer to start a
  fire) — `CONFIRMED-OFFICIAL`, **CONFIRMS** PROJECT_MEMORY section 12's
  "Security below 100 can allow serious incidents such as fire" claim.
- Fire consequence: the burned building must be rebuilt at cost, and a
  fire event is explicitly described as capable of wiping out a large
  fraction of accumulated assets ("資産がガクッと減る"); higher-difficulty
  maps see fires more frequently ("中〜上級マップとなるとかなり頻繁に
  発生する可能性がある"). `CONFIRMED-OFFICIAL` qualitative, no numeric
  rebuild cost or probability given.
- Shoplifting (万引き) and robbery (強盗) are explicitly linked as a
  severity progression: frequent unresolved shoplifting escalates into
  robbery ("たびたびとひどくなると強盗にまで発展してしまう"), and a
  robbery event is called out as guaranteed to cause a large cash loss
  ("一度強盗が入ると売上金をゴッソリ持っていかれるのは確実"). `CONFIRMED-
  OFFICIAL` qualitative — **CONFIRMS** PROJECT_MEMORY section 12's listed
  incident types with an explicit shoplifting→robbery escalation
  relationship not previously recorded.
- Fireworks festival event — **NEW**: "毎年8月になると花火大会が開催
  される。美しい打ち上げ花火のグラフィックとともにお店にやってくるお客さん
  の数もアップする。ただし花火大会は一晩だけなので、このチャンスを逃さず
  売れ筋商品を用意して売り上げアップを狙おう." — every August, a one-night
  fireworks festival temporarily increases customer count; a footnote adds
  "※花火グラフィックはPS版にはありません" (the fireworks *graphic* does
  not exist on PS, implying the underlying customer-count-boost event
  itself still fires on PS, just without the SS-exclusive visual).
  `CONFIRMED-OFFICIAL`. Not present anywhere in `docs/research/` under a
  fireworks/花火 search, and not modeled in `reference_sim`/`game/` at all
  — genuinely new annual scheduled-event data, plus a useful PS-vs-SS
  platform-difference note (relevant since this project targets the PS/SS
  baseline and should not port the SS-only firework visual as if it were
  common to both, while the underlying demand-boost mechanic likely does
  apply to this project's PS baseline).
- Idol one-day-owner event: triggers at 10,000 cumulative visitors, raises
  popularity to 100 for that day only, and is stated to recur at each
  further 10,000-visitor milestone ("来客人数が1万人になると... その日
  一日はお店の人気度が100のままになる... この後もお客さんの数に応じて
  アイドルがやってくるチャンスも"). `CONFIRMED-OFFICIAL`. **CONFIRMS**
  PROJECT_MEMORY section 11's already-recorded fact and
  `visitor_milestone.py`'s already-ported `ChainVisitorMilestoneRuntime`
  (task #30) exactly — independent re-confirmation of the +100-popularity/
  10,000-visitor rule with a precise page citation (book p.59).

---

## 17. Sales/layout optimization tips (book pp.60-61)

Six-point "高収益を約束する6つのポイント" checklist (店の場所, 店内
レイアウト, 営業方針, 社員の扱いかた, 販促広告, 改築・新規開店) —
`CONFIRMED-OFFICIAL` STRATEGY_EVIDENCE, purely organizational, restates
already-covered mechanics with no new numbers. Wagon-vs-shelf sell-through
difference restated again ("同じ条件の同じ商品でも棚とワゴンでは売れかたに
差がある... ワゴンのほうが注目度が高い") — matches the already-confirmed
`attention` field differing between shelf/wagon `FixtureDefinition` rows
(e.g. `small_ambient_shelf` attention=10 vs `small_ambient_wagon`
attention=20) — **CONFIRMS**.

---

## 18. Q&A troubleshooting (book pp.64-71)

All Q&A entries in this range are STRATEGY_EVIDENCE / qualitative advice,
each restating a mechanic already covered above rather than introducing new
numbers:

- Congestion causes (低いレジ能力 / 狭い通路 / レジと出入口が近い) —
  restates section 3/PROJECT_MEMORY section 4.
- Shelves/wagons are one-directional and need ≥1 open block around them —
  restates section 3.
- Ejecting an angry-about-to-happen customer via "つまみ出す" — restates
  section 7, with the added caution that ejecting a *non-angry* customer
  who was leaving anyway is a wasted sale.
- Newly-opened branch advertising guidance: a single large ad (TV) is more
  effective than several small ones for a brand-new store; established
  stores should keep advertising monthly via cheaper combined methods
  (airship, or newspaper+direct mail together) — `CONFIRMED-OFFICIAL`
  qualitative, no new numeric values beyond the already-covered promotion
  table.
- Firing (解雇) staff and redistributing the roster evenly across stores is
  offered as an alternative to layoff when a branch closes — `CONFIRMED-
  OFFICIAL` qualitative, no new mechanic.
- Securing land before it appreciates: buying the land immediately and
  placing only a small store (register + break room, no other fixtures) is
  presented as the minimum-cost way to "hold" a plot ("最小の維持費で
  ほしい土地を自分のものにできるぞ") — `CONFIRMED-OFFICIAL` STRATEGY_
  EVIDENCE, confirms land can be held with a minimal, deliberately
  under-built store; no new numeric constant.
- Fire/robbery persisting despite red ink: root-caused to neglecting
  police/fire station inducement, not to the deficit itself — restates
  section 12/16, reinforcing the security→incident-rate causal link.
- Seasonal demand: warm drinks/oden sell better in winter, cold drinks
  better in summer; assortment should be swapped roughly twice a year
  ("年に2回は品物を替えたい"); rainy days reduce foot traffic; late-night
  buyers skew toward alcohol. `CONFIRMED-OFFICIAL` qualitative — **CONFIRMS**
  PROJECT_MEMORY section 8's "weather" factor and section 30 of the
  existing full-decode doc's `Weather`/`Season` boundary; the "twice a
  year" reassortment cadence is a piece of player advice, not an enforced
  rule, and no sales-multiplier coefficient is given (consistent with
  CLAUDE.md: do not invent one).
- Break rooms: two tiers exist, and the more expensive tier recovers staff
  stamina faster ("値段によってスタミナ回復率が違うのだ... 高いほうが
  回復率が高い") — `CONFIRMED-OFFICIAL` qualitative, matches PROJECT_
  MEMORY's existing break-room framing (fixture data table already prices
  `break_room_1`/`break_room_2` at ¥3,000/¥7,000 purchase, ¥1,200/¥2,400
  maintenance) — **CONFIRMS** that the price tiers map to different
  recovery *rates*, though no numeric recovery-rate value is given for
  either tier (still `UNKNOWN`, do not invent one; `game/` has no break-
  room/stamina-recovery mechanic implemented at all yet regardless).
- Parking: no fixed "how many spaces is enough" number is given; guidance
  is purely to start with cheap ground parking and add capacity reactively
  if customers start honking ("クラクションの音を聞こえる"), avoiding
  large towered parking early because of its high maintenance cost.
  `CONFIRMED-OFFICIAL` qualitative, consistent with existing
  `parking_ground`/`parking_two_story`/`parking_tower` maintenance costs
  already in `FIXTURES` (¥0/¥240/¥4,800 per day) — **CONFIRMS** the
  cost-scaling shape, no new number.
- Dirtiness: customers dirty the store as a byproduct of shopping; low-
  cleaning-skill staff fall behind, especially right after a store is
  enlarged before staff have grown into the new size. `CONFIRMED-OFFICIAL`
  qualitative, matches the existing cleaning-skill/`store_value.py`
  framing — **CONFIRMS**, no new number.
- Empty shelves/wagons: caused by low replenishment skill, not
  automatically by shoplifting (a common player misconception the guide
  explicitly corrects: "まさか、万引きにあったとか!?... 店員の能力が低くて
  補充が間に合わなかった"). `CONFIRMED-OFFICIAL` — useful design note that
  stockouts are primarily a staff-throughput problem, matching this
  project's own `restock_timing.gd`/`RestockTiming` inverse-skill-scaling
  model — **CONFIRMS** the underlying causal story qualitatively.

---

## 19. Summary tally

Approximate counts across this document's findings (a "finding" is one
bullet/table/fact, not one page):

- **NEW** (not represented anywhere in `reference_sim/`, `game/`, or
  `docs/research/` before this read): **~14** — most notably: the land
  acquisition-cost formula (section 1.1), the police-box/fire-station
  security bonus + 7-area effective range (section 12, resolves an
  explicitly-flagged prior research gap), the PS-fixed-3%-wage-negotiation
  rule (section 4.1), the 40-69/70-100 pre-hire stat interpretation bands
  (section 5), the 3-staff-per-store cap (section 5), the ≥20-area branch-
  spacing guidance (section 13), the rival-retreat 15-20%-discount/
  several-months tactic (section 14), the ¥500,000 rival-investigation fee
  (section 14), the "eject an angry customer" mechanic (section 7), the
  August fireworks festival event + PS/SS graphic difference (section 16),
  and a few smaller STRATEGY_EVIDENCE-tier behavior notes.
- **CONFIRMS** (matches an already-CONFIRMED or already-REMAKE_BALANCED_
  DEFAULT/PROVISIONAL value or mechanic, upgradeable or reinforcing):
  **~30+** — the permit fee/exclusion-distance table, the full 5-promotion
  table (with a note that several fields can now be upgraded to
  CONFIRMED_OFFICIAL evidence tier), the full 18-facility inducement list,
  the salary table, the trade-area-radius table, the checkout/replenish/
  clean skill-growth diagram, the education/agility/sociability→skill
  mappings, the price-rating five-factor causal diagram, the shoplifting/
  fire/security causal chain, the idol-one-day-owner milestone, the wagon-
  vs-shelf attention difference, and numerous qualitative behavior notes
  already recorded in PROJECT_MEMORY.md sections 4/6/7/8/10/12/13.
- **CONTRADICTS** (a hard, unresolved conflict with a currently-CONFIRMED
  value): **0 new ones.** The one genuine internal conflict rediscovered
  here (large-store construction price ¥24,000,000 on the chapter-1
  selection screen vs. ¥18,000,000 everywhere else, section 2; and the
  store-rating pp.38-39-vs-pp.74-75 threshold table, section 9) was
  **already known and already resolved in code** before this session, with
  the code's existing resolution unaffected by this independent re-read.

---

## 20. Notes for the reviewer

- This book (`本1.pdf`) has already been extensively ported into
  `baseline_data.py`; the highest-value contribution of this pass is the
  section 12 police/fire-station security-bonus finding, which was an
  explicitly open research gap, plus the smaller NEW items in section 19.
- Sections 9 and 2's reconfirmed internal conflicts are left as-is per this
  task's brief ("do not silently resolve them") — they were already
  flagged and already resolved one way in code before this session; this
  document only adds a second independent transcription for the record.
- The companion PDF ("file 2 of 2") is being read by a separate agent in
  parallel; cross-check that agent's findings against this one where topics
  overlap (particularly store-rating pp.74-75, product/fixture DATA LIST
  tables, and the 35-candidate staff roster, none of which are in this
  file).
