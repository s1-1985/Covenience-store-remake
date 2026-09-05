# Hidden map, staff profiles, survey cost, and platform-specific notes — 2026-09-05

Scope: 1997 PS/SS 『ザ・コンビニ ～あの町を独占せよ～』 only.

## Evidence labels used
- `CONFIRMED-COMMUNITY`: first-title-specific Wiki or multiple detailed community sources agree.
- `CONFIRMED-PLAY-PS`: detailed PS play record.
- `CONFIRMED-PLAY-SS`: detailed SS play record.
- `PLATFORM-UNRESOLVED`: behavior is reported for one platform and cannot safely be promoted to both.
- `PROVISIONAL-COMMUNITY`: plausible single-source observation.

## 1. Hidden map unlock

### Finding
Clearing the standard Beginner / Intermediate / Advanced maps unlocks a fourth hidden map referred to as `極上`.

### Evidence
- PS-specific Wazap page for the 1997 PlayStation title lists the hidden-map condition as clearing Beginner, Intermediate, and Advanced.
- Independent PS play records describe the available map set as Beginner / Intermediate / Advanced plus `極上`, available to players who cleared the three standard maps.
- A platform-separated retrospective also lists the same hidden-map unlock for both Saturn and PlayStation.

### Confidence
`CONFIRMED-COMMUNITY`, PS-supported.

### Implementation candidate
```text
ScenarioUnlockDefinition
id = gokujou
unlock_condition = clear(beginner) && clear(intermediate) && clear(advanced)
platforms = [PS, SS]
```

The exact `極上` start assets and victory condition are still unresolved. Do not assume that its objective is the same as Advanced merely because one player speculated so.

Sources:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://menokenkou.work/konbiniura/

## 2. Survey / research menu observations

A detailed SS play record explicitly reports that the `調査` command provides at least:
- each store's sales performance
- best-selling / wanted-item questionnaire information
- income/expense graphs
- rival-store survey

The same record says the rival-store survey costs **500,000 yen** and provides basic information such as business hours and earnings, but not the rival interior layout.

### Confidence
- Menu functions: `CONFIRMED-PLAY-SS`; broadly consistent with already known PS screenshots/menu references.
- Rival survey fee 500,000 yen: `CONFIRMED-PLAY-SS`, not yet promoted to cross-platform exact value.

### Implementation candidate
```text
ResearchMenu
- store_sales_performance
- product_questionnaire
- income_expense_graph
- rival_store_survey

rival_store_survey.cost_yen = 500000   # SS-specific until PS-confirmed
```

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

## 3. Additional staff performance profiles from first-title Wiki

The first-title PS/SS Wiki contains more named staff profiles than previously copied into project notes. These are qualitative/partial numeric anchors, not a complete 35-person master.

### Strong early/mid-game candidates
- `福本考仁`: academic background 95, stated second-highest among all characters; high overall values and good initial performance; strong manager candidate.
- `奥平康夫`: high initial operational values; eventually high in most areas except stamina/replenishment.
- `金田哲也`: broadly strong from early through late game; described as a near-Fukumoto profile.
- `長沢達也`: near-Kaneda profile, with higher stamina.
- `竹中百合子`: decent initial values, grows to roughly 80 across the board; relatively good stamina.
- `万田町子`: hiring screen appears mediocre, but education 85; register/security grow to around the same range; good initial values.
- `南田洋次`: decent initial performance; all operational parameters eventually reach 75.
- `市川智恵子`: similar to Minamida but somewhat slower replenishment.
- `中山光次`: low initial values, but all parameters grow strongly; late-game all-rounder with low salary.
- `森山雪之丈`: similar to Nakayama; initially weak, useful after other staff have developed.
- `田中幸子`: rival main-store staff; grows to roughly 75 overall.
- `菅原丈夫`: high initial parameters; final values settle around 70 overall.
- `雨中星人`: agility 100; most other hiring-screen values 40 or 50; operational education is 100 despite hiring display. Register and replenishment grow strongly. Stamina 40 but recovery is fast.

### Caution profiles
- `里中涼子`: hiring-screen values high except stamina, but initial operational values low; strong after development.
- `杉村真智子`: similar to Satonaka with higher sociability; important later but poor early hire.
- `佐々木信雄`: appears decent on hiring screen, but most final values stop around 65.
- `的場丈二`: stamina 95 and agility 95, but very low initial operational values; register is so slow that about one customer/day is reported early. Register remains relatively weak even after growth.

### Confidence
`CONFIRMED-COMMUNITY` for the listed Wiki statements. Approximate words such as `around 70/75/80` must stay approximate until guidebook numeric tables are recovered.

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 4. Staff salary calibration clue

The first-title Wiki states that the hiring-screen salary is the **daily salary for 24-hour operation**, and notes that many characters correspond to roughly **250-300 yen/hour** when divided over 24 hours.

This is not an exact payroll formula, but it gives a useful sanity range for reverse-engineering once actual staff daily salaries are obtained.

### Confidence
`CONFIRMED-COMMUNITY` for the 24h daily-salary semantics; hourly range is descriptive/community commentary, not a formal rule.

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 5. Platform-specific permit exploit: do not merge into common baseline

There is conflicting community evidence about the permit-fee exploit.

### Saturn-supported report
A Saturn-specific retrospective describes a sequence where the player:
1. constructs without the relevant permit,
2. enters remodel,
3. applies for the permit,
4. proceeds to the layout screen,
5. returns to the application screen,
which can leave the permit granted without subtracting the fee.

The source notes that some versions may have fixed the exploit.

### PS uncertainty
A Wazap entry lives under the PS title page, but the submitter explicitly says it was tested on Saturn and only assumes PS might also work. Another platform-separated retrospective lists the exploit only under Saturn and lists only the hidden-map unlock under PS.

### Decision
Tag as:
`PLATFORM-UNRESOLVED`, with strong Saturn evidence and insufficient PS confirmation.

Do **not** implement this as a common PS/SS baseline bug unless direct PS evidence appears.

Sources:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/
- https://menokenkou.work/konbiniura/

## 6. Saturn customer-share timing exploit

A Saturn-specific retrospective reports that customer traffic can be manipulated by setting all product margins to 20% below normal just before date change, allowing the daily calculation to occur, then resetting margins to +50%; the day's traffic remains based on the lower-price calculation while sales use the later higher prices.

This strongly supports the already documented architectural rule that customer attraction/share is calculated at discrete timing boundaries rather than continuously from current price.

### Confidence
`PROVISIONAL-COMMUNITY` / `SS-SPECIFIC` exploit detail.

### Implementation implication
The faithful simulation should calculate daily customer demand from a snapshot of store conditions at the relevant recalculation point, rather than querying live price continuously for already-scheduled visitors.

Source:
- https://menokenkou.work/konbiniura/

## 7. Guidebook image search status

Current image/search results recovered only covers and bibliographic evidence, not readable interior data tables.

- `必勝攻略法`: current auction image confirms physical title/edition, but no readable internal data table was surfaced in this pass.
- `攻略の帝王`: current auction images explicitly show PlayStation / Sega Saturn compatibility on the cover; still no readable internal Chapter 4 data table surfaced.
- `レイアウトデザインセレクション74`: current Mercari listing identifies SS/PS and includes multiple listing images, but accessible search text did not expose readable numeric data pages.
- `店舗拡大ガイドブック`: current used listings exist; no readable interior numeric pages surfaced in this pass.

Therefore the remaining exact master-table bottleneck remains interior-page access, not identification or availability of the books.

Sources:
- https://books.rakuten.co.jp/rb/880163/
- https://jp.mercari.com/item/m73569515174
- current Yahoo Auctions image-search results for the first-title strategy guides

## 8. New resolved vs unresolved ledger

### Newly resolved / strengthened
- Hidden `極上` map unlock after clearing Beginner + Intermediate + Advanced: PS-supported, cross-community agreement.
- Extended named staff performance profiles from the first-title PS/SS Wiki.
- `調査` menu contains store sales, questionnaire, graphs, rival survey in SS detailed play record.
- Rival survey cost 500,000 yen is anchored for SS.
- Customer-attraction calculation is further supported as snapshot/timing-based by an SS exploit report.

### Still unresolved
- Exact `極上` starting money and victory condition.
- PS exact rival-survey fee.
- Full 35-person numeric staff table.
- Exact salary scaling/rounding for shortened business hours.
- Cross-platform status of the permit-free exploit.
- Exact permit fees and distance radii for the first console title.
- The remaining store/fixture/product/town master tables.

## 9. Contamination warning

Searches continue to return detailed numeric pages for 『ザ・コンビニ3』 and other sequels. Values such as later-title store dimensions, permit fees, effect radii and month-end formulas are excluded from the original-title baseline unless deliberately tagged `remake_balanced_default`.
