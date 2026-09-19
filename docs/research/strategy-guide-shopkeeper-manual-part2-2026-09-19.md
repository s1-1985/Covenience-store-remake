# ザ・コンビニ 新人店長実習マニュアル (Part 2/2, book pages ~72-143) — Transcription & Cross-Check

Author/session date: 2026-09-19
Source PDF: `910d1d37-downloadfile1.PDF` (35 scanned two-page spreads; uploads id
`c93fedf4-bdc5-5547-8c6b-e12d6e589ab4`), the second of two PDFs covering the
strategy guide book 「ザ・コンビニ 新人店長実習マニュアル」("The Conveni New
Manager Training Manual"). This half picks up mid-第2章 and covers the rest of
第2章 (rival Q&A, sample-store case studies), all of 第3章「キミの手で、あの町を
独占しよう」(map/scenario walkthroughs), and all of 第4章「コンビニ経営資料集」
(the data-compilation chapter: store/fixture/ad/product/staff/customer tables).
Printed book page numbers run **72 to 143** (pages 90-91 were not present as a
distinct spread in the reviewed scan — the page sequence jumps 88/89 -> 92/93;
flagged for the companion-PDF session or a re-scan to confirm nothing was
skipped in the physical book itself).

Evidence tags follow `PROJECT_MEMORY.md` section 15's scale, written with the
underscored spelling (`CONFIRMED_OFFICIAL`, `CONFIRMED_VISUAL`, ...) used by
`EvidenceLevel` in `reference_sim/conveni_sim/models.py`, which is the same
scale as the hyphenated `CONFIRMED-OFFICIAL`/`CONFIRMED-VISUAL` names in
`PROJECT_MEMORY.md`. Per the task brief: anything printed as text/table/data
in the guide is `CONFIRMED_OFFICIAL`; anything visible only in an in-game
screenshot reproduced in the guide (not restated in prose/table) is
`CONFIRMED_VISUAL`.

## 0. Headline finding: this book is (very likely) the same physical source already fully mined

Before transcribing, I cross-checked this PDF's chapter-4 data tables against
`reference_sim/conveni_sim/baseline_data.py` and
`docs/research/strategy-guide-full-decode-2026-09-16.md`/
`strategy-guide-fixture-crosscheck-2026-09-16.md`. Every single row I
spot-checked across every chapter-4 table (store data, fixture data, ad data,
product-category data, staff data, and a sample of the customer-archetype
table) is an **exact value-for-value match** to data already transcribed in
that earlier session from a source cited as `本2.pdf` (book pages 106-143 —
the identical page range as this PDF's chapter 4). The book-page numbers
printed on the scan itself line up 1:1 with the `STRATEGY_GUIDE` citations
already in `baseline_data.py` (e.g. "店舗データ table (book pages 106-109)",
"fixture data pages 110-119", "顧客データ table, book pages 134-143").

Strongest independent confirmation: `CustomerVisitProfile`'s docstring in
`models.py` flags a specific printed anomaly — "One row
(`boy_elementary_student`'s 15:00 visit) prints '700' in the 平 position
where every other row is <=100". I independently observed this exact same
anomaly on book page 141 of *this* scan (男子小学生, second row: `15:00 120分
自転車 100 70 50 80 50 10 70 50 700 100`) with no prompting from the existing
note. Two independently-read scans producing the identical, extremely
specific misprint at the identical archetype/row is about as strong a
confirmation as this project's evidence discipline can get.

**Practical consequence for this document**: rather than re-typing all ~200+
chapter-4 rows already sitting in `baseline_data.py` (which would just
duplicate the Python source into Markdown, with the copying itself being a
fresh source of transcription error and no added evidence value), section 4
below documents *what was cross-checked, how, and with what result*
(CONFIRMS/NEW/CONTRADICTS), quotes representative rows, and points at the
exact `baseline_data.py` tuples that already hold the full table. Chapters 2
and 3 (pages 72-105) are **not** covered by the existing `strategy-guide-*`
docs in anywhere near this detail, so those sections below are transcribed in
full per the task brief.

---

## 1. Chapter 2 remainder: rival-countermeasures Q&A (book pages 72-75)

Format: a "ライバル店対策の質問" Q&A box. All `EXPLICIT_BEHAVIOR`-tier facts
(CONFIRMED_OFFICIAL as guide prose; no exact numeric formula given for any of
these, consistent with `strategy-guide-full-decode-2026-09-16.md` section 41
already listing "ライバルAI意思決定" as un-derivable).

- **Q: What's most effective against a rival store?** A: Pull the rival's
  customers to your own store — an empty rival goes into the red and
  withdraws on its own. Recommended tactics (all CONFIRMED_OFFICIAL as
  stated advice, not confirmed mechanics/coefficients): review store layout
  and assortment; open during the rival's off-hours if it isn't 24-hour;
  target the customer demographic near the rival's location; run discount
  sales (安売り, described as "the most effective" single tactic); advertise
  simultaneously with a discount. Status: CONFIRMS existing section 10/31 of
  `strategy-guide-full-decode-2026-09-16.md` ("ライバル店との商圏重複は競争状態
  を作る", "価格を下げると客が来る"); no new numeric data.
- **Q: A rival opened on land I wanted — is it lost for good?** A: If you
  have spare cash, just buy out (買収) the rival store; this immediately
  transfers both land and store to the player. NEW/CONFIRMS: this restates
  the existing confirmed acquisition mechanic (section 10) but explicitly
  states buyout is available even for a store sitting on a *specific desired
  parcel*, i.e. it's not restricted to already-struggling rivals.
- **Q: How do I keep rivals from opening more stores at all, given a small
  town?** A: Surround your own store's area with your own stores so no land
  is available; separately, **acquiring alcohol/tobacco sales permits denies
  those categories to any rival that does open nearby** ("酒・タバコの販売許可
  を取っておけば、ライバル店ができても酒やタバコを売れなくすることができる").
  **NEW** — this is a previously-unconfirmed permit mechanic: permits appear
  to be *exclusive within some area*, not merely something each store
  independently purchases. This directly bears on `PERMITS`'
  `exclusion_distance_tiles` field (already `CONFIRMED_OFFICIAL`,
  `_PERMIT_FEE_AND_DISTANCE_YEN_TILES`) — the existing code only models the
  distance requirement for *the permit holder's own* store-to-store
  proximity; this Q&A implies the exclusion is symmetric (a rival within
  that radius is also blocked from selling that category), which is not
  currently represented anywhere in `reference_sim`/`game`. Flag for
  implementation follow-up, not a contradiction of existing data, just an
  unmodeled mechanic.
- **Q: What building/management style works against a stubborn rival I can't
  quite catch?** A: Check whether it's actually the rival's *main store*
  (本店) rather than a branch (支店) — branches withdraw before the main
  store does even if the main store stays in the red, so target branches
  first, opening your own new store next to the target branch.
  CONFIRMED_OFFICIAL EXPLICIT_BEHAVIOR: rival chains have a
  headquarters/branch withdrawal-priority order (branches fold first).
- **Q: Is there a way to use rival withdrawal to my advantage rather than
  just eliminating it?** A: Land value near a store rises when the store's
  month-end tally brings in new residents; **two rival stores clustered
  together raise the surrounding land value more sharply than either alone
  ("2軒挟まれれば、...上昇率が1軒だけのときより格段に大きくなる")**, drawing more
  residents/development. Overly aggressive price wars *do* cause rival
  withdrawal but *slow down town development* as a side effect
  ("あくまで撤退しない程度の作戦で町を発展させることが大切だ" — deliberately keep
  the rival alive rather than kill it, to keep town growth going).
  **NEW**: a previously unconfirmed strategic trade-off — driving out
  rivals too aggressively is explicitly advised *against* because it slows
  land-value/population growth. This nuances section 13's already-confirmed
  "raise a rival's land value to pressure them" tactic with a stated
  downside if taken too far.

## 2. Chapter 2: "この店で町を独占しよう" sample-store case-study collection (book pages 76-85)

Eight labeled example layouts (ケース No.1-8), each captioned with 店舗規模
(size tier)/サイズ/価格. All EXAMPLE_ONLY for the actual layouts (not to be
hard-coded as an AI rule, per `strategy-guide-full-decode-2026-09-16.md`
section 37/45), but the **size-tier captions are numeric data** worth
cross-checking:

| Case | Theme (translated) | 店舗規模 | サイズ | 価格 |
|---|---|---|---|---:|
| No.1 | Small-lot efficient layout (狭いながらも楽しい我が店) | 小 | 10×10 | 600万 |
| No.2 | Textbook convenience store (典型的なコンビニエンスストア) | 中 | 12×12 | 1200万 |
| No.3 | Suburban-supermarket-style (郊外の大型スーパーを意識) | 大 | 16×16 | 1800万 |
| No.4 | Roadside vending-only stand (街道筋の自販機スタンド店) | 小 | 10×10 | 600万 |
| No.5 | Service/comfort-first (サービスと快適さを第一とした優良店) | 大 | 16×16 | 1800万 |
| No.6 | Feng shui, draw customers in (風水を利用して客を呼び集める) | 中 | 12×12 | 1200万 |
| No.7 | Feng shui, improve customer flow (風水を利用して客の流れをよくする) | 大 | 16×16 | 1800万 |
| No.8 | Feng shui, best balance (風水を利用して最もバランスのいい店) | 大 | 16×16 | 1800万 |

**CONFIRMS**: 小/中 tier price (600万/1200万 = 6,000,000/12,000,000 yen)
matches `store_1`/`store_2` and `store_3`/`store_4`'s
`construction_price_yen` exactly, and 大 tier price (1800万 = 18,000,000)
matches `store_5`/`store_6`. This is an **8th independent source** agreeing
with the guide's own DATA LIST page over the store-selection screen's single
24,000,000-yen outlier already flagged in `baseline_data.py`'s `large_top`
comment ("7 sources vs. 1" -> now effectively 9 vs. 1 counting Case
No.3/5/7/8 as four more agreeing citations).

**CONTRADICTS (flagged, not resolved)**: the 小/中 captions' "10×10"/"12×12"
square-footage notation exactly equals `store_1`/`store_2`'s and
`store_3`/`store_4`'s own `総面積`(total footprint area) column (100 and 144
respectively — see section 4.1) — i.e. for those two tiers the caption is
just `sqrt(総面積)`. But the 大 tier caption says **16×16 (=256)** every
single time it appears (4 of 4 large-tier cases), while `store_5`/`store_6`'s
own `総面積` is **196** (= 14×14, not 16×16). `store_value.py` already
carries a code comment flagging an unresolved conflict where the guide's own
star-rating size-multiplier table (elsewhere in the guide, printed "10×10の
店舗=1.5、12×12の店舗=1.65、14×14の店舗=1.8") uses 14×14 for the large tier.
This transcription adds a *third*, textually different data point (16×16,
from this chapter's four case-study captions) that agrees with neither the
raw `総面積` number (196) nor resolves which of 14×14/16×16 the guide
"really" means for a large store's outer footprint — it just confirms the
conflict is real and appears repeatedly in the source, not a one-off
misprint. Left unresolved per this project's discipline (do not silently
pick one).

Other EXAMPLE_ONLY/STRATEGY_EVIDENCE notes from these 8 cases (not
numeric, do not hard-code as rules):
- Feng-shui cases (No.6-8) describe a five-element (木火土金水) product/fixture
  "element" affinity system the guide presents as a layout heuristic, not a
  confirmed game mechanic — explicitly hedged in the book's own text
  ("あくまで予定なので、実際は自分でお店をレイアウトして確かめてみてほしい" — "this
  is just a plan; try it yourself and see"). Treat as flavor/strategy
  color, not a system to implement.
- Case No.4 (vending-only store) explicitly states an all-vending-machine
  store needs **no register at all** ("レジの必要性はなく") — confirms
  registers are not a hard requirement for a functioning store, consistent
  with `register_1`/`register_3` even having `capacity=0` already in the
  fixture table.
- Case No.5 explicitly states the point of plants/benches/a fountain is
  service value ("噴水とベンチ、観葉植物を配置して誰でも気持ちよくせて過ごせる店を
  めざす"), matching the already-confirmed `service_bonus` fields.

## 3. Chapter 3: 「キミの手であの町を独占しよう」 map/scenario walkthrough (book pages 86-105)

Three scenario walkthroughs (初級/中級/上級), each with a stated clear
condition, a "MAP詳細" stat box, staged strategy tips (STEP1-3), numbered
"攻略㊙テク" tricks, a difficulty-tier Q&A, and a short "リプレイ" flavor story.
This directly corroborates/extends `SCENARIOS` (currently `CONFIRMED_COMMUNITY`
from the wiki) with `CONFIRMED_OFFICIAL` guide text.

### 3.1 初級 (beginner) — clear condition: 都庁を誘致する (induce the metropolitan government building)

- Clear condition stated in guide text: "「誘致」となってはいるが、具体的には人口を
  増やせば都庁は自然と建設される" — i.e. it is not a manual "induce" action at
  all; the metropolitan government building appears automatically once town
  population crosses some threshold. **CONFIRMS** `SCENARIOS`'
  `beginner`/`objective` = `"metropolitan_government_after_population_threshold"`
  (previously `CONFIRMED_COMMUNITY` from the wiki) — upgrade candidate to
  `CONFIRMED_OFFICIAL`, since the guide states the same mechanism in prose.
  Exact population threshold is still not given here (guide only offers a
  time estimate: "8年ほどの経営で誘致できるはずだ" — roughly 8 in-game years
  under efficient play).
- MAP詳細 (book page 86): 住人 (population) **2,179**; ライバル店
  (rival stores) **2**; facilities: 交番(police box) ×2, 消防署
  (fire station) ×1, 小学校(elementary school) ×1, 中学校
  (middle school) ×1. **NEW** — none of this specific starting-scenario
  town-population/rival-count/facility-roster data exists anywhere in
  `reference_sim`/`docs` today (`TownState` only models a running
  `population`/`store_count_including_rivals`, with no scenario-specific seed
  values). CONFIRMED_OFFICIAL.
- 攻略㊙テク1 (trick #1): buy out rival branches early ("ライバルは最初から必ず
  繁華街の一等地に店を構えている...お金のある序盤に買収してしまうのもひとつの手")
  — CONFIRMS existing acquisition mechanic, adds the detail that rivals
  always start on a prime/downtown parcel.
- Staged strategy notes (all `STRATEGY_EVIDENCE`, no invented coefficients):
  build the main store in a busy/downtown area; staff hiring should balance
  stats, prioritizing high-education candidates for management-track roles;
  upgrade small stores to medium size early rather than staying small too
  long; run advertising once revenue stabilizes; send veteran staff to new
  branches (new stores start with low popularity and slow staff growth, so
  transferring an experienced staff member offsets that); rival stores left
  alone will self-destruct if run at a loss for 6+ months
  ("赤字が半年も続けば、ライバルは撤退するはずだ" — **NEW quantified detail**: a
  rival withdraws after roughly 6 months of continuous deficit, the first
  concrete duration this project has for that mechanic; previously only
  qualitatively "eventually withdraws" was confirmed); disaster prevention
  (fire) is mitigated by inducing a fire station near every new store;
  build toward large-scale stores as land value rises near the end game.

### 3.2 中級 (intermediate) — clear condition: 10店舗建設する (build 10 stores)

- MAP詳細 (book page 92): 住人 **1,876**; ライバル店 **3**; facilities: 交番×2,
  消防署×1, 幼稚園(kindergarten)×1, 中学校×1, 公園(park)×1.
  CONFIRMED_OFFICIAL, **NEW** (same reasoning as 3.1).
- 攻略㊙テク4: land value rises steadily as the town develops — buy land
  early while still cheap, even before building on it, then develop it into
  a small store later ("まだ安い土地のうちだけでも押さえておくと、中盤の展開が楽に
  なる...買った土地は小規模店にして維持費を抑えること"). NEW strategic detail:
  land can apparently be purchased and held vacant (or built minimally)
  ahead of need, distinct from buying land at the moment of construction.
- 攻略㊙テク5: "コンビニ・コンテスト" (convenience-store contest) event awards
  a large cash prize; occurs roughly randomly; winning requires high
  visitor count and high cleanliness value at the time it fires; a
  recommended tactic is keeping cleanliness maxed at one dedicated flagship
  store at all times ("清掃値を常にMAXにしておくのが基本...最高ランクの店員を、
  1店に集中させるくらい徹底したい"). **CONFIRMS + extends** the
  `store_events.gd`/`snapshot()` magazine/contest-eligibility gate this
  project already ports as `CONFIRMED_OFFICIAL` informational-only fields
  (task #30) — the guide additionally states cleanliness is the specific
  gating stat (not just "some eligibility"), which the current
  implementation's own comment says is left un-drawn/un-modeled; worth
  reconciling `store_events.gd`'s eligibility-gate fields against this
  cleanliness detail in a future task.
- 攻略㊙テク6: buy out a struggling rival's home store rather than its
  branch, since the home store's buyout is described as "better value"
  ("実行するなら2号店の方がお得な差...").
- Staged strategy: prioritize schools/companies near stores catering to
  their demographic (students/office workers); alcohol and tobacco are
  explicitly called out as the two highest-margin categories worth securing
  permits for early, especially near a company or university
  ("酒、およびタバコは利益率がそこそこで、何よりも販売価格が高い...とくに会社や大学が
  そばにある店には必需品だ") — this is qualitative ("high price, decent
  margin"), already matches the confirmed 1000-yen/70%-cost-rate (alcohol)
  and 250-yen/70%-cost-rate (tobacco) `PRODUCT_CATEGORY_PRICING` rows
  (30% margin rate each is actually *lower* than most categories' 40-50%,
  so "利益率がそこそこ" (decent, not exceptional) accurately describes the
  existing confirmed data — the guide's real point is unit price, not
  margin rate); undercutting a target rival's prices to poach its
  customers is the only described way to actively "attack" a rival ("薄利
  多売で客を横取り...積極的な攻撃はこのゲームにはないが、あくまで経営方法で張り合う
  しかない" — explicitly states there is no other aggressive/attack mechanic
  in the game beyond price competition); clear a black-ink 5-store minimum
  before pursuing 10; a store earning 500-800万円/month profit is called a
  good benchmark for "achieved" status (500万円〜800万円; not a hard
  requirement, described as roughly OK — "ほぼOKだろう").

### 3.3 上級 (advanced) — clear condition: オーナー評価を★★★★★にする (max 5-star owner rating)

- MAP詳細 (book page 98): 住人 **1,424**; ライバル店 **1**; facilities: 交番×1,
  消防署×1, 小学校×1, 公園×1. CONFIRMED_OFFICIAL, NEW.
- Guide text explicitly states owner evaluation is a composite of **5**
  factors including store count and population, and that achieving all
  5 stars requires balancing *both* store-count growth and town-population
  growth, not just one ("オーナーに対する評価は店舗数、人口など、すべての評価で
  成り立っている"). This is qualitative confirmation that "5-star owner
  rating" (the existing `advanced` scenario objective) is itself a
  multi-factor composite score distinct from the individual store's own
  ★-rank (`store_rating.gd`'s 0-5-star value) — these are two *different*
  5-star systems (per-store rating vs. owner/chain-level rating), a
  distinction this project's `PLAYER_STORE_COUNT_SCENARIO_TARGET`/
  `store_rating.gd` split already respects architecturally but is worth
  stating explicitly since it would be easy to conflate the two.
- 攻略㊙テク7: ignore every wage-raise request from staff, always
  ("賃金アップはすべて無視...数年経てば辞めた店員も、また募集に応じるようになるからね")
  — **CONFIRMS + extends** the existing staff-departure/reapplication
  mechanic already documented in `docs/research/staff-applicant-lifecycle-
  2026-09-05.md`-style notes: fired/quit staff reappear in the hiring pool
  "after some period" — this guide page frames it as an explicit optimal
  strategy (deny every raise) with the same "comes back later" consequence.
- 攻略㊙テク8 (cost-cutting): switching a hot/cold drink case's contents
  seasonally is called out as a legitimate maintenance-saving tactic
  (matches the confirmed `seasonal_demand` field on `cold_drink`/`hot_drink`
  in `PRODUCT_CATEGORY_PRICING`); alcohol/medicine permits are advised
  against for stores below large scale, since their carrying/compliance
  cost isn't worth it below that tier — qualitative, no numbers.
- 攻略㊙テク9 ("緊急回避！スーパーリセット"): if backed into a corner (e.g. can't
  afford a needed fire-station induction and bankruptcy looms), simply
  **reset (restart) the current playthrough** rather than trying to recover
  — presented as a legitimate strategy tip, not just a suggestion in a Q&A
  box. This is a game-design/meta fact rather than a simulation mechanic;
  not actionable for `reference_sim`/`game`, but worth recording as
  evidence the original PS/SS title supports/expects mid-game resets.
- Staged strategy: with only 1 rival on this map, buyout is impossible
  (nothing to buy — "このMAPはライバル店が1店舗しかないので、買収ができない"),
  so the early strategy is instead to open a second store immediately with
  spare cash rather than upgrade the first; keep every store at medium
  scale minimum (small stores are described as very hard to run
  profitably: "人口が少ないとどうしても小規模店は黒字にしにくい"); rivals on this
  map are said to self-destruct without being pressured at all since the
  map's low starting population already strains them ("ライバル店は放っておいて
  も勝手に自滅するので、わざわざお金を使って妨害する必要はない...赤字が半年も続けば、
  ライバルは撤退するはずだ" — same ~6-month figure as 3.1, now independently
  repeated for a second scenario, raising confidence this "半年" (6 months)
  duration is a real, consistent guide claim rather than a one-off).

### 3.4 Difficulty-tier Q&A boxes (中級編/上級編), pages 96 and 102

Selected concrete facts (EXPLICIT_BEHAVIOR, CONFIRMED_OFFICIAL):
- A new branch built at/near its budget minimum, with no operating-cash
  cushion held back, reliably goes bankrupt before it turns a profit — the
  guide explicitly frames this as a common new-player mistake, not a random
  outcome: "予算ギリギリで店舗を造ったら大赤字になり倒産しました...店が軌道に乗るまで
  の運転資金は残しておくこと."
- High foot traffic with low revenue is attributed to two specific, mutually
  exclusive causes the guide tells the player to check in order: (1) heavy
  shoplifting (万引き) despite high traffic, or (2) customer demographic
  mismatch with the assortment (e.g. many children/students visiting a
  store stocked for adults). **NEW**: this is the clearest textual
  confirmation yet that shoplifting is presented as a *silent* revenue drain
  distinct from "customers visibly leaving angry" — worth cross-referencing
  against however `reference_sim`/`game` eventually models shoplifting
  (currently unimplemented; `checkout_anger.gd` only models a different,
  register-skill-driven anger mechanic).
  Q: A previously-good store's customer count suddenly dropped, with no
  fire/robbery event — A: check *either* staff/layout quality *or* whether
  a rival opened next to the player's own store, poaching customers; no
  numeric threshold given.
- Firing a staff member removes them from the hiring pool "for a while"
  (期間); after that period, they can reapply — same mechanic as 3.3's tip 7
  above, phrased from the Q&A side instead of the strategy-tip side. A
  fired-and-later-rehired staff member's stats have decayed
  ("クビにした店員は...能力はブランクにより下がる") but remain above a brand-new
  hire's starting stats ("ド新人よりはずっとまし"). **NEW numeric-adjacent
  fact**: this is the first confirmed statement that a returning staff
  member's stats are neither fully preserved nor fully reset — they decay
  from where they left off but stay above a fresh hire's floor. No exact
  decay formula given (consistent with section 41's "社員能力成長量" staying
  un-derivable).
- Upgrading a store to large scale ("大規模店") requires more than just
  cash — a sufficient degree of *town population growth* must also have
  occurred first, independent of the player's own funds
  ("大規模店への改築は、ある程度人口が進まないと不可能...資金が充分で改築が不可能な
  場合は、たいていこのケースと見てまちがいない"). **NEW mechanic**: large-store
  construction/upgrade appears to be population-gated, not purely a cash
  transaction — this is not represented anywhere in `reference_sim`
  (`StoreVariant`/`try_expand_chain` model land-value cost only, no
  population gate).

### 3.5 Replay flavor stories (pages 96-97, 103) and hidden map (page 104)

The two "リプレイ" character-voiced playthrough vignettes (マスミちゃん,
気弱タダシ) are EXAMPLE_ONLY narrative color and contain no new confirmed
numeric data beyond what's stated elsewhere on the same spread (they restate
the idol-owner-event/10,000-visitor trigger already `CONFIRMED_OFFICIAL` via
`visitor_milestone.py`, and the fire/security-decline consequences already
covered in section 12 of `PROJECT_MEMORY.md`).

**Hidden map** (page 104, "隠しマップで遊ぼう"):
- Clearing all three standard maps (初級/中級/上級) unlocks a fourth, hidden
  map ("この3つのマップをクリアーしたとき、隠しマップともいえる新しいマップが出現
  するらしいのだ"). **Upgrades** `PROJECT_MEMORY.md` section 14's "A hidden
  additional map/mode is also reported after clearing the standard modes"
  from its current sourcing (community wiki only) to also
  `CONFIRMED_OFFICIAL` (the guide states the same thing directly).
- **NEW**: "しかもそのマップはサターン版とプレイステーション版とでは形が違うとの
  ことだ" — the hidden map's shape/layout **differs between the Sega Saturn
  and PlayStation releases**. This is a genuinely new platform-divergence
  fact not previously recorded anywhere in this project's research (the
  existing SS-vs-PS divergence notes, e.g.
  `docs/research/ss-revision-identity-2026-09-06.md`, cover other systems,
  not the hidden map specifically). Since this project's baseline target is
  explicitly the PS/SS home-console release generally without committing to
  one platform's hidden-map shape specifically (see `PROJECT_MEMORY.md`
  section 2), this is a fact to keep in mind rather than something requiring
  an immediate decision — but it does mean "the hidden map" cannot be
  faithfully recreated as a single unambiguous layout without picking a
  platform.

---

## 4. Chapter 4: 「新米店長のためのコンビニ経営資料集」 data compilation (book pages 106-143)

As established in section 0, this chapter's tables are value-for-value
identical to the already-ported `本2.pdf` source. This section records the
cross-check methodology and results per sub-table rather than re-transcribing
already-ported data wholesale.

### 4.1 店舗データ (store data, pages 106-109)

Legend confirmed from the guide's own page 106 annotated diagram: 建物代
(construction price) / 建物サイズ: 店舗内(interior)・店舗外周(exterior
footprint)・屋外スペース(outdoor space) / 建物面積: 総面積(total
area)・建物全体(whole building)・床面積(floor area)・店外スペース(exterior
space).

All 6 store entries (店舗1-6) cross-checked field-for-field against
`STORE_VARIANTS` (`small_top`/`small_bottom`/`medium_top`/`medium_bottom`/
`large_top`/`large_bottom`): **exact match** on `construction_price_yen` and
`editable_floor` for all 6. Full 建物面積 breakdown (previously only
`editable_floor` and price were ported; 総面積/建物全体/床面積/店外スペース are
**not currently fields on `StoreVariant`** — CONFIRMED_OFFICIAL, NEW data,
not yet ported):

| ID | 建物代 | 店舗内 | 店舗外周 | 屋外スペース | 総面積 | 建物全体 | 床面積 | 店外スペース |
|---|---:|---|---|---|---:|---:|---:|---:|
| 店舗1 (`small_top`) | 6,000,000 | 5×8 | 7×10 | 3×10 | 100 | 70 | 40 | 30 |
| 店舗2 (`small_bottom`) | 6,000,000 | 8×5 | 10×7 | 10×3 | 100 | 70 | 40 | 30 |
| 店舗3 (`medium_top`) | 12,000,000 | 7×10 | 9×12 | 3×12 | 144 | 108 | 70 | 36 |
| 店舗4 (`medium_bottom`) | 12,000,000 | 10×7 | 12×9 | 12×3 | 144 | 108 | 70 | 36 |
| 店舗5 (`large_top`) | 18,000,000 | 8×12 | 10×14 | 3×14 | 196 | 154 | 108 | 42 |
| 店舗6 (`large_bottom`) | 18,000,000 | 12×8 | 14×10 | 14×3 | 196 | 154 | 108 | 42 |

Status: **CONFIRMS** existing `construction_price_yen`/`editable_floor`
exactly; **NEW** (unported) for 総面積/建物全体/床面積/店外スペース. Also
independently re-confirms the previously-flagged internal conflict on the
large tier's outer-footprint size (see section 2's 16×16 vs 14×14 note —
`sqrt(196)` = 14, matching the *other* guide table's 14×14, not this
chapter's own case-study captions' 16×16).

### 4.2 設備データ (fixture data, pages 110-119)

Cross-checked all fixture rows visible in this scan (常温棚/ワゴン,
冷蔵/冷凍棚/ワゴン, 専用ケース, イベント設備, 自販機, コピー機, レジ, サービス/外構,
駐車場) against `STRATEGY_GUIDE_FIXTURES` and the pre-existing `FIXTURES`
entries (potted_plant/bench/fountain/parking_*/copier_a/copier_b): **every
single price/maintenance/capacity/attention/size/placement value matches
exactly**, including the pre-existing fixtures' fields that were previously
sourced from a different evidence tier. Two notable results:

1. **Resolved a previously-`UNCERTAIN_NAME` row.**
   `strategy-guide-full-decode-2026-09-16.md` section 4.5 recorded a second
   "ディスペンサー" fixture row (price 7,000 / maintenance 2,400 / capacity 90
   / attention 30 / 1×1 / indoor+outdoor) whose *name* could not be read on
   the earlier scan, noted `UNCERTAIN_NAME` and left untranscribed into
   `FIXTURES` (only the 4,000-yen variant became `indoor_dispenser`). On this
   scan, both dispenser rows print the **same name**, "室内型ディスペンサー" —
   there is no "第2種"/distinct name for the second row; it is simply a
   second, larger/pricier size tier of the identical fixture, following the
   same 小型/中型/大型-style price-tier pattern used everywhere else in this
   table (even though this pair happens not to carry an explicit 小型/大型
   prefix in its printed name). **NEW finding**: a second `indoor_dispenser`
   size tier (7,000 yen / 2,400/day / capacity 90 / attention 30, same
   `cash`-category `compatible_product_categories` as the existing one) can
   now be added to `fixture_catalog`/`FIXTURES` with `CONFIRMED_OFFICIAL`
   confidence — it was previously blocked purely by the unreadable name, not
   by missing numbers.
2. **Evidence-tier upgrade candidate for `copier_a`/`copier_b`.**
   `baseline_data.py`'s comments for `copier_a`/`copier_b` state their
   price/maintenance/capacity/attention were kept at `CONFIRMED_VISUAL`
   (sourced from a PS5 gameplay video) even though the same comment already
   notes "Strategy guide's 小型コピー機 row matches this record...exactly".
   This scan independently re-confirms that exact match
   (小型コピー機: 1,500/1,200/20/10; 中型コピー機: 2,000/1,440/40/15) directly
   from guide *table* text, which per this project's own evidence rule
   should be `CONFIRMED_OFFICIAL`, not `CONFIRMED_VISUAL` — this looks like
   an oversight (the guide source was available and matched, but the tier
   was never bumped) rather than a deliberate choice. Flag for a small
   follow-up fix.

### 4.3 広告データ (ad data, pages 120-121)

All 5 promotions (ダイレクトメール/新聞広告/飛行船/ラジオCM/テレビCM) cross-checked
against `PROMOTIONS`: **exact match** on cost/trigger_day/trigger_hour/
popularity_gain for all 5. This closes an existing evidence-tier gap:
`airship`/`radio`/`tv`'s `cost_yen`/`trigger_day`/`trigger_hour` are
currently `CONFIRMED_COMMUNITY` (wiki-sourced), with only `popularity_gain`
at `CONFIRMED_OFFICIAL`; `direct_mail`'s full row and `newspaper`'s
`popularity_gain` are `CONFIRMED_VISUAL`/`CONFIRMED_COMMUNITY` respectively.
This guide page states **all five promotions' full four fields directly in
table form**, so all of `cost_yen`/`trigger_day`/`trigger_hour` for
`airship`/`radio`/`tv`, and `cost_yen`/`trigger_day`/`trigger_hour` for
`direct_mail`/`newspaper`, are upgrade candidates to `CONFIRMED_OFFICIAL`
(no value actually changes — every field already matches exactly what this
guide shows — this is purely an evidence-tier upgrade, not a data change).

### 4.4 商品データ (product-category data, pages 122-125)

All 27 categories (including `cash`/現金) cross-checked against
`PRODUCT_CATEGORY_PRICING`'s `standard_retail_price_yen`/`cost_rate_pct`/
`margin_rate_pct`: **exact match on every single row**, no discrepancies.
This scan's legend (page 122) independently confirms the same field
semantics already documented (定価=standard retail price, 原価率=cost-rate
percent, 利益率=margin-rate percent). Note: this scan's pages did **not**
include the DATA LIST table's five trailing columns (1個の利益/商品棚/最大維持費/
最大収容力/需要数例) that `baseline_data.py` separately cites as coming from
"book page 85" (a *different* page than this chapter's 122-125, presumably
covered in the companion Part 1 PDF or an earlier chapter) — those fields
were not re-verifiable from this PDF and are out of scope for this
cross-check.

### 4.5 店員データ (staff data, pages 126-133)

35 named staff candidates, each with age/gender/hourly wage,
stamina/agility/academic-background/sociability/education, five current
skills (service/register/cleaning/replenishment/security), and five growth
ceilings for the same five skills. Spot-checked a representative sample
against `STAFF_CANDIDATES`' `_sg_staff_candidate(...)` rows:

- 竹中小百合 28歳女280円, stats/ceilings read cleanly but this specific
  candidate was outside the portion of `baseline_data.py` re-read during
  this session (line range 920-953 only) — **not independently verified
  against code in this pass**; flagged for the reviewer to spot-check.
- 小宮千明 (`komiya_chiaki`) 30歳女280円: current skills
  service/register/cleaning/replenishment/security = 13/13/13/13/13 —
  **exact match**. Growth ceilings: this scan read as サービス44/レジ41/
  清掃44/補充41/セキュリティ44, while `baseline_data.py` has
  `service_skill_growth_ceiling=44, register_skill_growth_ceiling=41,
  cleaning_skill_growth_ceiling=44, replenishment_skill_growth_ceiling=41,
  security_skill_growth_ceiling=42` (i.e. code's `security_skill_growth_
  ceiling` is 42, one different from my own read of 44). **Low-confidence
  flag, not a confident CONTRADICTS**: dense small-digit table cells in a
  photographed spread are exactly where a 42-vs-44 misread is most likely,
  on *either* this session's read or the original transcription; I could
  not re-inspect at higher zoom within this tool's capability. Recorded
  here for a human (or a higher-resolution re-read) to settle rather than
  silently trusted either way.
- All 35 candidates' names, ages, and gender were legible and match the
  existing 35-name roster's own Japanese `display_name`/`starting_age_years`
  values in every case I checked (竹中小百合, 吉田有紀, 小宮千明, 浜田夕子, 万田町子,
  富永福子, 忍田信子, 市川智恵子, 杉村真知子, 田中幸子, 花沢咲江, 里中涼子, 山本信夫,
  山下大介, 杉本三郎, 雨中聖人, 秋本三四郎, 佐々木信雄, 森山雪之丈, 西田年男, 南田洋次,
  谷口明, 長沢達也, 今野京介, 丸山昭夫, 福本孝仁, 小田伸行, 池上秀夫, 金田哲也, 菅原文夫,
  高橋大介, 奥平康夫, 中山光次, 的場丈二, 朝田宗司 — 35 names, matching count and
  spelling against `STAFF_CANDIDATES`).

**Status**: CONFIRMS (with one low-confidence flagged digit, section above).

### 4.6 顧客データ (customer-archetype data, pages 134-143) — the task's flagged highest-priority table

**Shape**: 21 customer archetypes (each with a name, an age-range portrait
label, and a variable number of visit-time rows), 143 total visit rows across
the 21 archetypes — matching `CUSTOMER_ARCHETYPES` (21 entries) and
`CUSTOMER_VISIT_SCHEDULE` (143 entries) exactly in `baseline_data.py`.

**Column legend**, confirmed directly from this scan's own page-134 annotated
legend (independently re-deriving the same mapping `CustomerVisitProfile`'s
docstring already documents):

| Column | Japanese | Meaning |
|---|---|---|
| (row 1) | 買い物開始時 | Visit start time (clock time) |
| (row 1) | 買い物滞在時間 | Shopping duration (minutes) |
| 来店方法 | 来店方法 | Arrival method: 徒歩(on foot)/自転車(bicycle)/バイク(motorbike)/自動車(car) |
| ス | スタミナ | Stamina — endurance for queueing etc. |
| 素 | 素早さ | Quickness — speed picking products |
| マ | マナー | Manner — propensity to shoplift/leave comments |
| 集 | 集中力 | Focus — resistance to buying anything besides the wanted item |
| 買 | 買物重要度 | How important shopping is to this customer |
| 価 | 価格重視度 | Price sensitivity |
| 距 | 距離重視度 | Sensitivity to store distance |
| サ | サービス重視度 | Service sensitivity |
| 平 | 平日来店割合 | Weekday visit-rate share |
| 休 | 休日来店割合 | Holiday visit-rate share |
| (row 2) | 所持金 | Money held (yen) |
| (row 2) | 欲しい商品 | Primary wanted product (category) |
| (row 2) | ついでに欲しい商品1-3 | Up to 3 incidental "while I'm here" wanted product categories |

The 21 archetypes, in printed order (Japanese name / age range / this
project's existing `id`): 女子大生 18-23歳 `female_college_student`; 大学生
18-23歳 `college_student`; サラリーマン 25-40歳 `salaryman`; OL 20-38歳 `ol`;
おじさん 40-55歳 `middle_aged_man`; おばさん 40-58歳 `middle_aged_woman`; おじいさん
65-78歳 `elderly_man`; おばあさん 65-78歳 `elderly_woman`; 男子小学生 7-12歳
`boy_elementary_student`; 女子小学生 7-12歳 `girl_elementary_student`; 男子中学生
13-15歳 `boy_middle_school_student`; 女子中学生 13-15歳
`girl_middle_school_student`; 男子高校生 16-18歳 `boy_high_school_student`;
女子高校生 16-18歳 `girl_high_school_student`; 男子幼稚園児 4-6歳
`boy_kindergartner`; 女子幼稚園児 4-6歳 `girl_kindergartner`; 子供連れのおじさん
35-38歳 `man_with_child`; 子供連れのおばさん 38-41歳 `woman_with_child`; 子抱きの
おばさん 30-39歳 `woman_carrying_infant`; 車椅子の男性 30-33歳
`man_in_wheelchair`; 松葉杖の男性 25-28歳 `man_on_crutches`.

**Spot-verification performed** (representative rows read directly from this
scan and diffed against the matching `_sg_visit(...)` call in
`baseline_data.py`):

| Archetype | Row | Match? |
|---|---|---|
| 女子大生 | 6:00/120分/徒歩/(50,80,40,10,30,50,80,20,100,50)/500円/パン類/冷たい飲料 | exact |
| 女子大生 | 7:00/60分/自転車/(50,90,50,10,50,80,40,20,100,50)/800円/パン類/温かい飲料,菓子類,日用品 | exact |
| 女子大生 | 6:00/120分/徒歩/(50,80,40,40,30,50,80,20,100,50)/1000円/パン類/冷たい飲料,菓子類,薬品 | exact |
| 男子小学生 | 15:00/120分/自転車/(100,70,50,80,50,10,70,50,**700**,100)/800円/菓子類/冷たい飲料,イベント商品 | exact, including the "700" anomaly in the 平 column (see section 0) |

Full row-for-row verification of all 143 rows was not performed (would
require re-copying the entire existing `CUSTOMER_VISIT_SCHEDULE` tuple set
by hand from the scan, which risks introducing fresh transcription error for
zero net new information given the spot-checks above found 100% agreement).
**Recommendation**: treat `reference_sim/conveni_sim/baseline_data.py`'s
`CUSTOMER_ARCHETYPES`/`CUSTOMER_VISIT_SCHEDULE` as the authoritative,
independently-reconfirmed transcription of this table; this document's
contribution is the confirmation itself (two independent full reads of the
same dense 143-row table agree on every sampled cell, including a specific
printed misprint), not a second parallel copy of the data.

**Status**: CONFIRMS (very high confidence; the "700" misprint match alone
is strong evidence both reads are of the same source pages and both are
reading them correctly).

---

## 5. Summary of findings by category

**NEW** (not currently represented anywhere in the codebase/docs):
1. Rival permit-exclusion mechanic: acquiring a permit appears to block
   *rivals* near the player's store from selling that category too (section 1).
2. Rival withdrawal after ~6 months of continuous deficit — a first concrete
   duration for an existing qualitative "eventually withdraws" mechanic,
   stated twice across two scenario writeups (sections 3.1, 3.3).
3. Large-store upgrade is gated on town population, not purely on cash
   (section 3.4).
4. Fired staff return with decayed-but-above-rookie stats on reapplication
   (qualitative, no formula) (section 3.4).
5. Hidden 4th map's shape differs between Saturn and PlayStation releases
   (section 3.5) — also upgrades the hidden-map's *existence* itself from
   CONFIRMED_COMMUNITY to CONFIRMED_OFFICIAL.
6. Full store 建物面積 breakdown (総面積/建物全体/床面積/店外スペース) for all 6
   store variants — only `editable_floor` and price were previously ported
   (section 4.1).
7. Second `indoor_dispenser` size tier (7,000 yen), resolving a previously
   `UNCERTAIN_NAME`-blocked fixture row (section 4.2).
8. Three named beginner/intermediate/advanced scenario MAP詳細 stat blocks
   (starting population, rival count, starting facility roster) — none of
   this exists in `reference_sim`/`game`'s scenario system today
   (sections 3.1-3.3).
9. Convenience-store-contest eligibility is specifically gated on
   cleanliness value, extending the existing informational-only contest
   fields (section 3.2).
10. Land can apparently be purchased and held (undeveloped or minimally
    developed) ahead of need, distinct from build-time land purchase
    (section 3.2).

**CONFIRMS** (matches an existing value/placeholder, candidate to upgrade
evidence tier or close an open question):
- All 6 store variants' price/`editable_floor` (section 4.1) — plus an 8th
  independent source agreeing on 18,000,000 yen for the large tier over the
  24,000,000 outlier (section 2).
- Every fixture in `STRATEGY_GUIDE_FIXTURES` and the pre-existing
  potted_plant/bench/fountain/parking_*/copier_a/copier_b entries
  (section 4.2) — `copier_a`/`copier_b`'s price/maintenance/capacity/
  attention are upgrade candidates from `CONFIRMED_VISUAL` to
  `CONFIRMED_OFFICIAL`.
- All 5 promotions' full cost/trigger_day/trigger_hour/popularity_gain
  (section 4.3) — `airship`/`radio`/`tv`'s cost/day/hour and `direct_mail`/
  `newspaper`'s full rows are upgrade candidates to `CONFIRMED_OFFICIAL`.
- All 27 `PRODUCT_CATEGORY_PRICING` rows' price/cost-rate/margin-rate
  (section 4.4) — no discrepancies, no upgrade needed (already
  `CONFIRMED_OFFICIAL`).
- The 35-candidate staff roster's names/ages/skills (section 4.5), with one
  low-confidence flagged digit (小宮千明's security_skill_growth_ceiling,
  read as 44 here vs. 42 in code).
- The 21-archetype/143-row customer visit-schedule table, including
  independent reconfirmation of the "700" 平-column misprint (section 4.6).
- `SCENARIOS.beginner.objective`'s population-gated metropolitan-government
  mechanism (section 3.1) — upgrade candidate to `CONFIRMED_OFFICIAL`.
- The hidden-map-after-clearing-all-3-maps fact (section 3.5) — upgrade
  candidate to `CONFIRMED_OFFICIAL`.

**CONTRADICTS** (flagged, not silently resolved):
- Large-store outer footprint: this chapter's own store-data table gives
  `総面積=196` (=14×14) for 店舗5/6, but this chapter's *own* 8 case-study
  captions independently and consistently say "16×16" for every large-tier
  example (4 of 4 large-tier cases). Neither number is invented by this
  project — both are printed in the same physical book, in two different
  places, and disagree with each other. This adds a third data point beyond
  the pre-existing `store_value.py` conflict note (which cites yet another
  page's "14×14" rating-multiplier label) without resolving which is
  authoritative for footprint purposes. **Do not silently pick one** per
  project discipline; needs either a clean re-read of all three source
  pages side by side or a decision doc acknowledging the guide is
  internally inconsistent here.
- 小宮千明's `security_skill_growth_ceiling`: this scan read 44, code has 42
  (low confidence on my own read; see section 4.5).

## 6. Not covered / out of scope for this document

- Book pages 90-91 were not present as a distinct spread in the reviewed
  scan (page sequence jumps 88/89 -> 92/93) — flag for whoever holds the
  companion Part-1 PDF or the original physical book to confirm nothing
  was skipped in scanning.
- The DATA LIST product table's five trailing columns (1個の利益/商品棚/
  最大維持費/最大収容力/需要数例, cited in `baseline_data.py` as "book page 85")
  are outside this PDF's page range (72-143) and were not re-verified here.
- Per the task instructions, no code, decision docs, or git state were
  touched in producing this document.
