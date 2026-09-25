# Strategy Guide PDF Extraction — 2026-09-24

Source PDFs:
- PDF1 = `11c92833-downloadfile.PDF` (33 pages) — 「ザ・コンビニ 新人店長実習マニュアル」第1章 新規開業編 + 第2章 start
- PDF2 = `53487124-downloadfile1.PDF` (35 pages) — same guide, 第2章 continuation + 第3章/第4章
- PDF3 = `213406b8-downloadfile2.PDF` (23 pages) — 「クイックリファレンス」book
- PDF4 = `d9b60a50-downloadfile3.PDF` (24 pages) — more of guide book, printed page nos. ~48-53 range, ストアコレクション case studies

All Japanese quoted verbatim where legible; translations are literal/working translations, not official.

**Editor's note (main session, not the transcription agent): known supersessions.** This
transcription was produced by a background agent reading the same page images this session's own
`Read`/`pdftoppm` calls also examined at higher, targeted resolution (400dpi crops of specific
regions vs. this doc's whole-page reads). Where the two disagree, the higher-resolution direct
re-crop is the one implemented in code; check these before trusting a specific digit here:
- The store-evaluation increase/decrease table (PDF1 p.38-39, this doc's lines ~169-185) has
  several misread cells and a garbled 6th-row note. A 5x-render re-read (task #86) found it is
  cell-for-cell identical to PDF4 print p.75's table, including a printed ☆☆☆☆☆ row on both
  sides -- see `docs/research/store-rating-table-reverification-2026-09-25.md`, which supersedes
  this doc's transcription of that table.
- The weather-percentage table (PDF3 p.3, this doc's line ~421) is flagged here as medium-confidence
  with column-set OCR ambiguity ("月/晴天/曇り/雨/雨天/荒天/大雪"). A 400dpi crop of the same table
  this session found the columns are actually 快晴/晴れ/曇り/雨・雪/荒天 (5 columns, all 12 rows sum
  exactly to 100) — see `docs/decisions/0132-*.md` and `baseline_data.MONTHLY_WEATHER_PERCENTAGES`.
- The angry-customer/shoplifting/donation rank-table footer (PDF4 print p.75, this doc's PDF4
  section) reads "寄付イベント=+5" in a targeted crop, consistent with this doc and with the
  already-shipped `store_rating.py` constant — see `docs/decisions/0134-*.md` for what got wired
  from it.
- The new-branch land-cost formula (PDF4 print p.79) was independently re-cropped and confirmed
  exactly as this doc transcribes it — see `docs/decisions/0135-*.md`.

Everything else in this document (the store-parameter definitions, advertising table, staff growth
rules, DATA LIST product/fixture/building tables, the secret 極上 map, etc.) has **not** been
independently re-verified at higher resolution by the main session — treat it the same as any other
first-pass transcription in `docs/research/`: high-value lead, not yet promoted past whatever
confidence level it states inline.

---

## Notable/high-priority findings (with page citations)

*(This section is being filled in as pages are transcribed; updated at the end.)*

- **Sales-permit exclusion zone diagram (PDF1 p.7)**: Concentric-square diagram around "お店" (the store) with radiating numbers **5 / 7 / 11 / 15** labeled, from innermost to outermost ring:
  - innermost band → **店建設可能** ("store construction possible") — i.e. rival stores cannot be built at all within this ring
  - next band → **たばこ販売可能** ("tobacco sales possible")
  - next band → **酒類販売可能** ("alcohol sales possible")
  - outermost labeled band → **薬類販売可能** ("medicine sales possible") (label partially at bottom, "薬類販売可能")
  - The four numbers 5, 7, 11, 15 are arrayed left-to-right along an arrow from the store outward, each apparently marking the boundary distance (in map squares) of one ring. Exact number-to-label pairing could not be 100% confirmed pixel-by-pixel from the scan alone — the visual order top-to-bottom of labels is 店建設可能(innermost)/たばこ販売可能/酒類販売可能/薬類販売可能(outermost), and the numbers 5,7,11,15 run innermost-to-outermost in that same order along the arrow — strongly implying **5=store-building minimum distance, 7=tobacco permit range, 11=alcohol permit range, 15=medicine permit range**. Recommend a follow-up zoomed crop/higher-res look if possible.
  - Caption text: "マップ上にはライバル店が建っているが、お店どうしが近すぎる場所には新しく出店することができなくなっている。これはお客さんの取り合いを防ぐための措置で、たとえ自分の店であっても近すぎる場所には建てられないのだ。また店を建てられたとしても酒やタバコの販売許可がとれない場合がある。実は販売許可が必要な商品にも範囲があり、すでに販売許可を取っている店の範囲内では売ることができなくなっている。販売許可商品は利益も高いからぜひとも自店に置きたい品。そのためにも店どうしの距離を考えて出店場所を決定することが重要になる。"
    - Translation: "A rival store may already be built on the map, but a new store cannot be opened in a location too close to another store. This is a measure to prevent customer poaching — even your own store cannot be built too close [to another of your own stores]. Also, even if you can build a store there, you may not be able to get a sales permit for alcohol or tobacco. In fact, permit-required goods also have a range: you cannot sell them within the range of a store that already holds that permit. Permit goods have high profit margins, so you definitely want to carry them at your own store. For this reason, deciding where to open a store while considering the distance between stores is important."
  - Sidebar box title: "お店どうしの間柄も重要なポイントとなる" ("The relationship/distance between stores is also an important point")

- **Land/building purchase cost formula (PDF1 p.7)**: Two exact formula boxes shown:
  - Empty lot: "必要金額=土地代 ※地代~(エリア地価×エリア数)" → Required amount = Land price; Land price ≈ (Area land price × number of areas)
  - Lot with existing building: "必要金額=土地代+建物買収費 ※買収費~(建物評価額の50%)" → Required amount = Land price + Building acquisition fee; Acquisition fee ≈ (Building appraisal value × 50%) — CONFIRMS the "建物買収費 = 建物評価額の50%" figure from the task brief, exact wording captured verbatim.
  - Explanatory text: "建設予定地が空き地の場合 ~土地代だけでOK": "買いたい土地になにも建物がないなら払うお金は土地代だけでいい。余計なお金を払わなくてもいいので経済的なのだ。ただし土地代は場所によって高低がある。しかも時間が経つにつれて土地は変化するから、土地は早めに押さえるのが基本だ。"
  - "予定地に建物がある場合 ~土地代+買収費が必要": "あらかじめ建物が建っている土地を買うときは、その建物もいっしょに買い取ることになる。それだけ費用も割高になってしまう。でもお客さんが多そうな場所に限って建物も建っているので、出し惜しみせずに買うのが将来的に得になる。"

- **Store sizes / construction costs (PDF1 p.10)**: All 6 store sizes given exact costs:
  - 縦10×10 (小/vertical) — 建設費用 ¥6,000,000
  - 横10×10 (小/horizontal, same footprint different orientation) — 建設費用 ¥6,000,000
  - 縦12×12 (中/vertical) — 建設費用 ¥12,000,000
  - 横12×12 (中/horizontal) — 建設費用 ¥12,000,000
  - 縦16×16 (大/vertical) — 建設費用 ¥24,000,000
  - 横16×16 (大/horizontal) — 建設費用 ¥24,000,000
  - Text: "建てられるお店は縦横の違いを含めた全6種。お店のサイズによって建設費用や置ける商品の数、維持費なども変わってくる。いずれ大きくすることを考えてどのサイズにするか決定しよう。ちなみにお店の縦横に関しては、売り上げに差はないのでお好みで選択していい。"
  - Confirms footprint options: Small=10×10, Medium=12×12, Large=16×16, each buildable in either vertical or horizontal orientation with IDENTICAL cost and (per text) no sales difference between orientations.

- **Sales permit costs (PDF1 p.9)**: exact table "◆販売許可に必要な金額":
  - 酒類 (alcohol): ¥3,000,000
  - たばこ類 (tobacco): ¥7,000,000
  - 薬類 (medicine): ¥10,000,000
  - Total if all 3 bought: ¥20,000,000 (text states "3種類の販売許可を取ると合計2千万円になってしまうけれど")
  - In-game dialogs shown: "たばこ販売許可を申請しますか?" with cost ¥5,000,000 shown in one screenshot (differs from table's ¥7,000,000 tobacco — screenshot may show a different/earlier price point or is a partial view; note discrepancy) and "薬…¥10,000,000" visible in same dialog stack.

- **Recommended plot 5 best picks (PDF1 p.6)**: "おすすめ物件ベスト5": 1 道路に面している、駅に近い / 2 地価がほかより高い / 3 アクシデントにあいにくい / 4 酒・たばこの販売ができる / 5 役場用地に近い

- **Aisle/passage width rule (PDF1 p.16-17)**: "通路の幅は人間ふたり分が基本" — exact quoted text: "通路が狭すぎるとすれ違うお客さんでつまってしまい、流れのジャマとなる。最低ふたりが通れる幅はほしい。" (Passage width should allow two people minimum, as a baseline; if too narrow, customers passing each other get stuck, blocking flow.) NOTE: this is a general guideline text, not a formal "1-masu vs 1/2-masu" numeric rule — no explicit "1マス/0.5マス" terminology found yet on these pages; continue watching for it in later pages/PDF3.

- **Shelf (棚) vs Wagon (ワゴン) pickup-direction rule (PDF1 p.19)**: Exact quoted text: "棚とワゴンはそれぞれ特徴がある。ふたつの特性を生かすように商品を入れるようにするのが大切なことだ。" Panel captions:
  - 棚の場合: "棚は一方向らしか商品を取り出せない。壁沿いに設置するのにピッタリだけど、前にモノを置くと、お客さんが商品を取り出せなくなってしまう。" (Shelves can only have items taken from ONE direction; ideal against walls; if something is placed in front, customers can't take items out.)
  - ワゴンの場合: "ワゴンは4方向、どちらからも商品をとることができる。しかもワゴンは注目度も高いので、よく売れる商品を入れておくのにピッタリなものだ。" (Wagons can have items taken from all 4 directions, AND wagons have higher 注目度 [attention/notice level], making them ideal for best-selling/high-turnover items.)
  - This directly confirms the shelf/wagon 注目度 (attention) mechanic referenced in the research gaps: wagons have inherently higher 注目度 than shelves.
  - Screenshot shows a fixture selection panel with fields: 大型冷凍庫 (large freezer), 価格 ¥140, 維持費 ¥72 /日, and "注目度 10" as a numeric stat on a fixture info panel — confirms 注目度 is a literal numeric stat shown per-fixture in the placement UI (value 10 seen for one fixture).

- **Store exterior / extra fixtures (PDF1 p.19)**: "自動販売機" (vending machine) — text: "自動販売機も立派な売り上げの元。さらに単価の高い酒類の自販機を導入すれば酒好きのお客さんも寄ってくるし、売り上げだってアップするぞ。" "駐車場" (parking lot) — text: "お客さんは徒歩で来るとは限らない。遠くから来る場合は自動車を使うのだ。そんなお客さんのために駐車場を作れば、集客率もアップ。" Both are placed *outside* the store and boost 集客率 (customer-draw rate).

- **Business hours presets (PDF1 p.23)**: Screenshot shows 営業方針 setting screen fields: "営業時間 [AM10:00~PM6:00]", "社員ベースアップ率 3%", "給与交渉に応じる はい/いいえ". Text: "初めは7:00~11:00営業" recommended starting hours (low staff ability + cleaning/restocking not able to keep up). "無理に24時間営業は狙わない" — full 24h should wait ~1 year for staff training. NOTE: did not yet see the "5 clock-diagram presets" UI mentioned in the brief on this page — likely appears on a later page (store settings, PDF3?). Will flag if found.

- **Time-of-day customer demographics wheel (PDF1 p.23)**: Circular 24-hour clock-face diagram, split into two colored bands:
  - Blue band (labeled 独身者が多い = "mostly singles"): hours 20,21,22,23,0,1,2,3,4,5,6 roughly (evening through early morning)
  - Pink/red band (labeled 主婦・学生が多い = "mostly housewives & students"): hours 7 through 19 roughly (daytime)
  - Text: "1日のうち時間によってお店に来るお客さんの層は変わる。もちろん売れる商品も変わるので、営業時間と来客層によっては商品を並び替えるといいのだ。" + "◆昼間: 昼間多いのは主婦や子供、お昼になると弁当を買いに来たサラリーマンの姿が何人も目につくはずだ。" + "◆夜間~深夜: 夜に多いのは独身の男の人や若者。タバコや酒を買いに来る人も増えるので、品切れを切らさないように。"

- **Pricing / profit-margin mechanic (PDF1 p.22)**: Screenshot "商品価格を決定して下さい": "全商品平均利益率 45%", "全体に統一 5%UP", "個別に設定" buttons, "終了···START". Second screenshot: individual item margin adjust "利益率 2%UP" / "42%" per item with mascot commentary "ボッチ" "90円" "100円?". Text: "商品を売るごとにもうかる率を表したのが商品利益率。この数値が高いほどお店にとってはもうかるけれど、それだけ商品の値段も高くなってしまうのだ。この利益率を変化させることでもうけとお客さんの入りぐあいを調節することができるのを知っておこう。" + "利益率は商品全体を変えるほかに、ひとつずつでも変更することができる。例えば売れ筋商品を高めにすれば利益が上がり、イマイチの商品の利益率を下げればいままでよりも売れるようになるかもしれないのだ。お客さんが少ないときは利益率をわざと下げ、お客さんを呼び寄せるようにしてみよう。" Diagram: 販売価格率 低い⇔高い maps to: 店のもうけ 小→大, 集客率 増加→減少, 人口増加 アップ→ダウン(?), 店の評価 アップ→ダウン. (Exact arrow diagram: 低い→もうけ小/集客率増加/人口増加アップ/店の評価アップ; 高い→もうけ大/集客率減少/人口増加ダウン/店の評価ダウン — i.e. LOWER price = more customers, more population growth, better rating; HIGHER price = more profit per item but fewer customers, worse rating.)

- **Staff parameter definitions — 7 params (PDF1 p.24-25)**: Exact quoted definitions:
  - 体力 (Stamina): "どれだけ長い間仕事に打ち込めるかを表わした数値。これがゼロになると休憩室に入って、回復するまで出てこないのだ。"
  - 教育 (Education): defined on p.25 sidebar — "このほかにある教育というパラメータ。これは部下となった人材の能力を引き出す力を表わしているのだ。3人の店員のうちひとりを店長に任命することになるのだが、店長の教育パラメータが高いとほかの店員の成長ぶりが早くなる。"
  - レジ (Register/checkout): "いかにレジをすばやく打つかを表わしたもの。この数値が高いほど、レジが混雑していてもテキパキこなしてくれるぞ。"
  - 補充 (Restocking): "空になった棚に商品を補充する能力。棚が空のままだと品物を売れないが、この数値が高ければすぐに補充してくれる。"
  - 警備 (Security): "お店の防犯を司る数値。モラルの低いお客さんがときどき万引きをするけれど、この数値が高ければ万引き防止になる。"
  - 清掃 (Cleaning): "いつもきれいな店になる能力。フロアを清掃する能力を表わしたもの。お客さんは買い物と同時にお店を汚さず、この数値がすばやくきれいにしてくれる。" (as printed; likely means: customers dirty the store while shopping, and a high value cleans it up quickly)
  - 接客 (Customer service): "直接売り上げには関係ないがコンビニ経営には大切な数値。これが高いほど店の人気が上がってお客さんの数が増える。"
  - Sidebar "特に優秀な人材は店長の資格あり" confirms only 3 staff slots per store ("ひとつのお店に雇えるのは3人まで") and one of the 3 is appointed 店長 (manager), whose 教育 stat accelerates the OTHER staff's growth rate.
  - Recruitment UI note: candidate list initially shows only 4 of the 7 parameters (体力/学歴/敏捷性/社交性 - actually resume-screen fields, see below) — full 7-stat breakdown only visible after hiring.
  - "履歴書の評価" (resume evaluation) table maps 4 *pre-hire* résumé stats to bands:
    - 体力 ~ スタミナ(仕事の持続力): 普通 40-69, 高い 70-100
    - 学歴 ~ レジ・セキュリティ能力: 普通 40-69, 高い 70-100
    - 敏捷性 ~ 商品補充、店内移動速度: 普通 40-69, 高い 70-100
    - 社交性 ~ サービス、清掃能力: 普通 40-69, 高い 70-100
    - Text: "人材募集した段階では、その人のこまかい能力まではわからない。表示された4つの能力では想像するしかないのだ。4つの能力とパラメータは、下の表のようになっている。" — i.e. the 4 pre-hire résumé stats (体力/学歴/敏捷性/社交性) each map onto specific PAIRS of the real 7 in-job parameters as shown, and only reveal a "普通"(40-69) vs "高い"(70-100) band, not an exact number, before hiring.

- **Staff stat growth / decay mechanic (PDF1 p.26)**: Exact table "仕事内容とパラメータ変化の関係":
  - ひとり分のレジを打った → レジ、サービスがアップ。レジを早く打てるぞ。
  - ひとつの棚に補充した → 補充、清掃、警備がアップで、店の管理が上達。
  - ひとつのエリアを掃除した → 清掃、警備がアップ。店内がきれいになるのだ。
  - "仕事に失敗すると能力がダウン" — "モタモタしていると怒られてしまう。こうなるとほかに店の評価にも影響が出てしまう。"
  - "店長の教育次第でも、社員は伸びる" — "店長の教育パラメータが高い場合、能力アップ率が高くなるのだ。できるだけ優秀な店員を店長に雇っていけば、それだけ店員の成長も早まる。教育のパラメータをチェックして店長を決定しよう。"

- **Wage formula / age-based base wage table (PDF1 p.27)**: Exact table "◆年齢別・社員の基本時給(円)":
  - 年齢: 15, 20, 25, 30, 35, 40, 45, 50, 55, 60
  - 時給: 250, 300, 350, 400, 450, 500, 550, 600, 650, 700
  - i.e. linear formula: 時給 = 250 + (年齢-15)/5 × 50 → simplifies to roughly 時給 ≈ 10×年齢 + 100 (check: age15→250 = 10*15+100=250 ✓; age60→700=10*60+100=700 ✓). CONFIRMED_OFFICIAL linear formula: **時給(円) = 年齢×10 + 100** exactly fits all 10 data points.
  - Screenshot fields: 営業方針 screen "営業時間 AM7:00~PM11:00", "社員ベースアップ率 2%", "給与交渉に応じる はい/いいえ" (different % from p.23's 3% example — confirms this is a player-adjustable field, not fixed).
  - "ふっかけてくる店員はキッパリと断わる" — "店員によっては、年齢を無視した時給のアップを求めてくる場合がある。とくに上級マップになるほどふっかけた上昇率を言ってくるが、適切な時給でない限り断ってしまってもかまわないぞ。" (confirms a wage-negotiation event where staff may demand above-table wages, and it scales with map difficulty tier.)
  - Note: this page's formula covers the *base* hourly wage by age; task brief's "wage formula (時給×営業時間)" for total labor cost is not explicitly spelled out as a formula sentence on this page, but the 時給 (hourly wage) × hours-open implication is strongly suggested by context (staff paid hourly, business-hours setting exists) — no explicit "賃金 = 時給×営業時間" sentence found verbatim yet; keep watching later pages/PDF3 for an explicit formula statement.

- **Staff hiring archetypes (PDF1 p.28-29)**: 3 recommended-hire categories, each with 3 sample candidate stat blocks (7-stat bars: 体力/学歴/レジ/補充/警備/清掃/社交性 as shown, though labeled slightly differently across pages — pre-hire résumé screen fields are 体力/学歴/敏捷性/社交性, but POST-hire in-job stat screen fields are 体力/教育/レジ/補充/警備/清掃/接客):
  - 店長におすすめの社員 (recommended for manager) — "店長に求められるのは教育パラメータの高さ。なにはともあれこの数値が高ければ、店長としては合格なのだ。" Sample: 横峰隆二 32歳男, stats 体力76/学歴95/敏捷性76/社交性80, wage ¥6,448/日 (this is shown using the PRE-hire 4-field résumé labels even though it's post-selection — consistent with hiring screen reuse).
  - 体力仕事におすすめの社員 (recommended for stamina-heavy work) — "長時間の労働も大丈夫だし、テキパキ動いて補充もしてくれる。こんな人がひとりいると経営がスムーズになる。"
  - サービス業におすすめの社員 (recommended for service work) — "率先して掃除をしてくれるし、レジ打ちも早い。メンテナンスと接客業に関しては右に出るものはいないといえるぞ。"
  - Manga "コンビニ物語『予定外要員』の巻" — flavor: shoplifting (万引き!!) scene, humor about security.

- **Customer area-of-draw radius by transport mode (PDF1 p.31)**: Exact table "来店手段 / エリア半径":
  - 徒歩 (on foot): 20
  - 自転車 (bicycle): 40
  - バイク (motorbike): 60
  - 自動車 (car): 70
  - Text: "実はお客さんの範囲は、その来店手段によって変化する。徒歩でやってくる人は範囲も狭いし、自動車で来店するなら半径も広くなる。つまり遠くのお客さんまで来店させたいと思ったら、自動車で来られるように駐車場スペースを設けるようにすればいいのだ。"
  - "売り上げが上がれば町も大きくなる" callout: "店の売り上げがアップすれば、評判を聞きつけたのか町に移住する人の数が増える。人が増えれば売り上げも増え、また人が増えるというようにドンドン町が発展していくのだ。とくに駅が完成すると一気に人口が増えるので、しっかりかせいで町を大きくしよう。"
  - "客層にあわせた商品をそろえる" — "主婦なら食料品、学生やサラリーマンなら弁当や雑誌など客によってほしいものが違うので、商品も入れ替えよう。" With example zone types: オフィス街~サラリーマン、OL / 学校~学生 / 住宅地~主婦、子供.

- **Customer individual data / behavior mechanic (PDF1 p.32-33)**: "基本的な客の行動パターン": ①来店 (arrival by 徒歩/自転車/自動車 — 3 types listed here, note バイク not listed in this recap, though p.31 table has 4 modes including バイク) ②欲しいものを買う ③ついでにものを買う (impulse/extra purchase if 品揃え is good and money allows).
  - Each customer has individual data: 欲しかった物 (item they wanted), 所持金 (money they're carrying) — shown via cursor+decide button on a customer sprite.
  - "アンケートを実行すればお客のほしがっているものがわかる" — monthly survey mechanic: "アンケートをとると、その月でお客さんが買った商品の累計とほしかった商品の累計が表示される。個人データをチェックするのも大切だけど、お店のある地域の傾向を知りたいときはアンケート調査がいちばん。月に一度実行してみよう。" Example アンケート結果 table (買った商品 / 欲しかった商品, with counts): 弁当類45/温かい飲料23, 文房具22/日用品13, 野菜類20/おでん12, 肉類20/中華マン(?), パン類17/タバコ, インスタント類16/雑貨, 魚類16/酒類, イベント商品16/(blank).

- **Customer anger / shoplifting / store-closing-a-customer mechanic (PDF1 p.34-35)**: 
  - "レジから抜ける人がいるみたいだけど" — customers leave the register queue if kept waiting too long (レジ待ち耐えられず離脱).
  - "店のなかをウロチョロしている人がいる" — a customer that can't find a wanted item (item location unknown, or aisle too narrow to reach it) will wander; "とくにハマッてしまった場合は、その人がいる限りお店を閉めることができないのだ" — CONFIRMED MECHANIC: if a customer gets stuck/wandering, the store cannot be closed until that customer leaves!
  - "時間によってお客さんが違っている" — "昼間は主婦や子供、夜は男の人が多いようだ。"
  - "マナーがいい人ばかりで助かるけど" — shoplifting (万引き) happens silently; only revealed in that month's 収支報告 (financial report) as a loss; "警備能力を高くしておかない限り、安心しきってばかりはいられない。"
  - "お店のサービスが悪いとお客さんが怒りだしてしまう" — "ゲーム中に突然「ふざけるな!!」と怒鳴られたら要注意。これはお客さんがお店に対して怒ってしまったときに聞くことができるメッセージなのだ。お客さんが怒る原因はレジや通路の混雑が考えられる。レジ前が狭くてお客さんがたまってしまったり、店員のレジ能力が低くてなかなかさばけなかったりするとレジ前が大混乱。たまりかねたお客さんが怒って帰ってしまうのだ。お客さんに怒られると店員全員の能力が下がってしまうので踏んだりけったり。そうならないためにも、日頃からレジ前の混雑には注意しておこう。" — CONFIRMED MECHANIC: an angered customer leaving causes ALL staff's parameters to drop (店員全員の能力が下がってしまう).
  - "怒られるまえに外へつまみだす" — "怒りやすいお客さんは、おじさんやおじいさんに多い。もしレジ前の混雑にこの人たちが混じっていたら、カーソルを合わせて決定ボタン。怒り出すまえに"つまみだす"を選んで、お店の外に出してしまうといいぞ。" — player can manually eject a customer at risk of getting angry via cursor+select "つまみだす" (pluck out/eject) command.

- **Advertising system — 5 methods with exact costs/timing/effect (PDF1 p.36-37)**: Exact table "5つの宣伝方法を使いこなして広告しよう":
  | 宣伝方法 | 宣伝費 | 宣伝日時 | 効果 |
  |---|---|---|---|
  | ダイレクトメール | 10万円 (¥100,000) | 2日 10時 | +12 |
  | 新聞広告 | 50万円 (¥500,000) | 2日 7時 | +20 |
  | 飛行船 | 100万円 (¥1,000,000) | 3日 15時 | +40 |
  | ラジオCM | 300万円 (¥3,000,000) | 1日 17時 | +60 |
  | テレビCM | 500万円 (¥5,000,000) | 1日 19時 | +90 |
  - "宣伝日時" = delay between ordering and effect landing (days + time of day the effect kicks in), "効果" = presumably the 人気(popularity) point boost granted.
  - Per-medium commentary: ダイレクトメール "安い値段でそれなりの効果" — "宣伝効果は最低だけど値段が安いので、何度でも出せるのが特徴。ただしダイレクトメールを何度も出すよりも、一度に大きな広告を出したほうが効果的なのだ。" おすすめポイント ★★★★
  - 新聞広告 "お手軽な広告の代表格" — "そこそこの値段でそこそこの効果が期待できる。これとダイレクトメールを組み合わせるようにすれば、毎月の広告はまかなえるはずなので、うまく活用。" おすすめポイント ★★★
  - 飛行船 "誰でも目につく便利な広告" — "すべての広告媒体のなかでいちばんコストパフォーマンスの高いのが飛行船。一度飛ばせば新聞+メールよりも効果高い。お金があればこちらをメインに。" おすすめポイント ★★★★★
  - ラジオCM "テレビにつぐ効果の高さがうり" — "一見効果的だが非常に中途半端な広告。価格は飛行船の3倍なのに効果は1.5倍と使い勝手よろしくない。ラジオを使うくらいならテレビを使うほうがいいぞ。" おすすめポイント ★★
  - テレビCM "コストは最高! 効果は絶大!" — "最高の費用に見合うだけの宣伝効果がある。一度出せばお店の人気はほとんど最高値になるので、このタイミングを逃さずに価格引き下げ販売を実施しよう。" おすすめポイント ★★★★
  - "せっかくの広告も、その効果は1日だけ" — "広告の効果が持続するのは、広告を出したその日だけ。翌日になると上がった人気度がドンドン下がってしまうので、広告を出した日の営業が大切になるぞ。" — CONFIRMED MECHANIC: ad popularity boost decays and is fully gone by the next day; effect is a ONE-DAY spike, so timing matters.
  - Screenshot: "宣伝方法を選択して下さい(複数可)" — multiple ad types CAN be selected/stacked in one order; "費用合計 ¥6,000,000" example.

- **Store evaluation (店舗評価) point system — EXACT increase/decrease thresholds (PDF1 p.38-39)**: This is a major table, transcribed in full:
  - Evaluation shown as 1-5 stars (★1 to ★5), plus a separate "人気" (popularity) 1-100 numeric parameter: "1から100までの数値で表わされる店舗評価は、いままでの自分の経営方針やお店の作りの善し悪しを判断するための大切なデータ。" (NOTE: text says 店舗評価 itself is a 1-100 number, while the UI shows it as stars — likely the 1-100 number maps to the star rating shown elsewhere.)
  - "◆増加要因(月末の収支決算において、以下の3条件がそろえば+5ポイント)" — table columns: 現時点評価 | 販売価格率 | サービス | セキュリティ | 清掃 | 前月売上
    - ★★★★★: 30%以下 | 100 | 100 | 100 | 1500万円以上
    - ★★★★: 20%以下 | 90以上 | 90以上 | 95以上 | 1000万円以上
    - ★★★: 15%以下 | 80以上 | 85以上 | 90以上 | 900万円以上
    - ★★: 10%以下 | 70以上 | 80以上 | 90以上 | 700万円以上
    - ★: 5%以下 | 60以上 | 75以上 | 85以上 | 500万円以上
    - (unstarred/lowest band, "★1%以下" row): 5%以下 | 60以上 | 75以上 | 85以上 | 500万円以上 → wait, re-check: table has 5 rows for ★1 through ★5, plus one more listed as "★" alone at 5%以下 row with 300万円以上 — need re-verification; as scanned the bottom row reads "★ | 5%以下 | 60以上 | 75以上 | 85以上 | 300万円以上" (there appear to be 5 rows total: ★★★★★,★★★★,★★★,★★,★ — last one's threshold for 前月売上 is "300万円以上" per the table, NOT 500万円; correcting: the 5 rows' 前月売上 thresholds read top-to-bottom as 1500万円以上/1000万円以上/900万円以上/700万円以上/300万円以上; a "500万円以上" figure did NOT appear in the increase table — that figure belongs to the decrease table's ★ row instead, see below.) [Recommend re-crop this table at higher res to double check exact digit-by-digit alignment; transcribed to best legibility.]
  - "◆減少要因(月末の収支決算において、以下の1条件につき、-1ポイント)" — table columns: 現時点評価 | 販売価格率 | サービス | セキュリティ | 清掃 | 前月売上
    - ★★★★★: 101%以上 | 80未満 | 80未満 | 100 | 300万円未満
    - ★★★★: 101%以上 | 70未満 | 70未満 | 95未満 | 250万円未満
    - ★★★: 101%以上 | 60未満 | 65未満 | 90未満 | 200万円未満
    - ★★: 101%以上 | 50未満 | 60未満 | 85未満 | 150万円未満
    - ★: 101%以上 | 40未満 | 55未満 | 80未満 | 100万円未満
    - (bottom row, unstarred, lowest tier): 101%以上 | 30未満 | 50未満 | 75未満 | 50万円未満
  - NOTE: decrease table appears to actually have 6 rows (★★★★★ down through a 6th unstarred/0-star row), while increase table also may have 6 rows — the printed table's leftmost "現時点評価" column had ★ symbols increasing in count that were hard to OCR precisely at this resolution; the numeric columns (percentages and 前月売上 thresholds) were legible and are transcribed faithfully above; star-count-per-row alignment should be double-checked against a higher-res crop if pixel-perfect fidelity is required.
  - "お店の評価を上げるのは社員の能力がポイントとなる" — "お店の人気をアップさせるには店長の経営方針も大切だが、お店で働く店員たちの能力が大きく影響する。店員の清掃能力が低いと店内はいつも汚い状態でお客さんは喜ばない。また店員の警備能力が低いと万引きや強盗が起こりやすい店になってしまい、お客さんにとってもありがたくない。こんなことが起こらなくするためには、優秀な能力の店員の働きが必要だ。お客さんに喜ばれるためにも店員育成にも力を注ぐようにしよう。"
  - "人気が高ければお客の入りもいい" — "4つあるパラメータのうち、最も気になるのが人気のパラメータ。これはお店がどれだけお客さんに受け入れられているかを示したもので、この数値が高いほどお客さんの数も増える。サービスや値段など経営方針で次第にアップするので、誰からも喜ばれるお店をめざそう。" — confirms 4 store-level parameters exist, one being 人気 (popularity); others likely include 治安(security)/繁栄(prosperity)/サービス per the task brief's オーナー評価 categories — watch for explicit listing.
  - "ちなみに年に一回、お店の総合評価が示される。その評価の基準となる条件を挙げておいてほしい、★×5の優秀なコンビニをめざして日々努力しよう。" — annual overall evaluation exists, target is 5-star.
  - Right-side screenshot fields: "どの店舗を調査しますか?" panel shows: 人気 20, 治安 68, サービス 63, 97(unclear 4th value, possibly 清掃 or another stat) — CONFIRMS 4-metric store inspection panel with labels 人気/治安/サービス/(4th, likely 清掃, value 97 for 清掃 based on adjacent number) — exact 4th label not fully legible in this crop.

- **Bug/edge-case reports "コンビニ珍経営日記" (PDF1 p.40-41)** — humor/player-anecdote sidebar, but contains useful mechanic confirmations:
  - "怪奇! お客の入れない店、出れない店" — placing a wagon directly in front of the entrance blocks customers from entering; vending machines outside still get used heavily in this case (confirms 自動販売機 works independent of interior access).
  - "空のワゴンばかりならぶ謎の店" — if wagons run empty during a TV-ad traffic spike, the sales opportunity is entirely lost ("テレビ広告のお客さんで店内は満員。せっかくのもうけのチャンスをみすみす逃してしまいましたよ") — reinforces ad-timing/restock-readiness interaction.
  - "順調路線から一変、3ヶ月目の悲劇" — a rival store appearing suddenly nearby can crater sales ("突然のライバル店の出現に売り上げはガタ落ち").
  - "レイアウトを変えたら、批判ブーブー" — rebuilding to a larger store size can temporarily DIRTY the store and drop 人気 sharply (90+ → below 50) if cleaning staff/restocking can't keep up with the new larger footprint — ties to 清掃 mechanic scaling with store size.
  - "客を怒らせるのが得意な店" — flavor anecdote: certain (elderly male) customer archetypes anger easily and repeatedly.
  - "広すぎる店内掃除がたいへん" — confirms cleaning workload scales with floor size; recommends more cleaning staff for large stores.
  - "やっぱり選ぶなら女の子社員がいい!?" — flavor/anecdotal preference, not a mechanical stat difference (no evidence female staff have different stats — this is player opinion/joke content, should NOT be treated as a real mechanic).

- **PLATFORM DIFFERENCE NOTES (PDF1 p.57, p.59)** — important for a "faithful to which version" decision:
  - p.57 footnote: "※PS版は3%固定なので、賃金アップ要求はありません。" (In the PS version, [staff base pay raise rate] is fixed at 3%, so there are no wage-increase demand events.) — implies the Saturn version has a variable/negotiable base-up rate but the PS version hard-codes it to 3% and removes the wage-negotiation-demand event entirely.
  - p.59 footnote: "※花火グラフィックはPS版にはありません。" (The fireworks graphic is not present in the PS version.) — the 花火大会 (fireworks festival) event exists on both platforms but its special graphic is Saturn-exclusive; PS version presumably still has the event's sales-count effect without the visual.
  - Since this project targets "the first home-console release" (per CLAUDE.md, PS/Saturn 1997), NOTE these two explicit PS-vs-Saturn divergences for the decision docs — the guide itself is evidently a multi-platform (PS+Saturn) release guide and calls out where the two differ.

- **Branch/建物誘致 (building attraction/subsidy) full facility list (PDF1 p.45)** — exact table "◆誘致できる施設リスト", columns サイズ/期間/援助額:
  | 施設 | サイズ | 期間 | 援助額 |
  |---|---|---|---|
  | 交番 (police box) | 2×2 | 1ヶ月(+0~3日) | 40万円 |
  | 消防署 (fire station) | 2×3 | 1ヶ月(+0~3日) | 60万円 |
  | マンション (apartment) | 2×3 | 1ヶ月(+0~3日) | 420万円 |
  | 会社 (company/office) | 3×3 | 1ヶ月(+0~3日) | 540万円 |
  | 体育館 (gym) | 2×3 | 1ヶ月(+0~3日) | 420万円 |
  | プール (pool) | 2×3 | 1ヶ月(+0~3日) | 180万円 |
  | 運動場 (athletic field) | 4×5 | 1ヶ月(+0~3日) | 200万円 |
  | イベント会場 (event venue) | 2×2 | 1ヶ月(+0~3日) | 600万円 |
  | 幼稚園 (kindergarten) | 2×3 | 1ヶ月(+0~3日) | 120万円 |
  | 小学校 (elem. school) | 4×4 | 1ヶ月(+0~3日) | 320万円 |
  | 中学校 (junior high) | 5×5 | 1ヶ月(+0~3日) | 500万円 |
  | 高校 (high school) | 6×6 | 1ヶ月(+0~3日) | 720万円 |
  | 大学 (university) | 7×7 | 1ヶ月(+0~3日) | 980万円 |
  | 専門学校 (vocational school) | 3×4 | 1ヶ月(+0~3日) | 480万円 |
  | 公園 (park) | 2×2 | 1ヶ月(+0~3日) | 200万円 |
  | 水族館 (aquarium) | 3×3 | 1ヶ月(+0~3日) | 270万円 |
  | 動物園 (zoo) | 6×6 | 1ヶ月(+0~3日) | 720万円 |
  | 遊園地 (amusement park) | 7×7 | 1ヶ月(+0~3日) | 980万円 |
  - Rule text: "誘致とはプレーヤーが指定した場所に建物を建ててもらうように働きかけること。いつも月末になると自然と建物は増えていくけれど、誘致を行えば自分に都合のいい建物を自分の店の近くに建てることもできるのだ。" — confirms passive monthly building growth PLUS active player-directed 誘致.
  - "ちなみに一度に誘致できる建物は1軒だけ。新しく誘致するには誘致中の建物が建ってからになるので、どの建物から誘致したらいいかもけっこう悩むポイントとなる。" — CONFIRMED: only 1 building can be under 誘致 at a time.
  - Effects listed: "①町の人口が増える ②買い物客が増える ③警備能力が上がる" (only 交番/消防署 give the security boost; others give population/customers per general text).
  - 交番 effect: "セキュリティ 40点アップ" (exact +40 security points), effective radius "自分のお店から半径7エリア以上の場所に誘致しても、それはムダというものだ" → confirms 交番 effect radius is within 7 map-areas of the store.
  - 消防署 effect: "セキュリティ 30点アップ" (exact +30 security points).
  - "交番と消防署、誘致するならどっちが得" — 交番 costs less (40万円 vs 60万円 construction subsidy) for a bigger security gain (+40 vs +30), so 交番 is more cost-efficient; also 交番 further reduces 放火件数 (arson incidents) indirectly by "警備能力がアップすれば、万引きや強盗だけでなく放火件数までも減少するのだ。"

- **Branch store (支店) catchment-radius / distance rule (PDF1 p.48)**: Diagram shows 本店 (main store) at center with 4 支店 (branches) arranged around it (North/East/South/West), each connected by a "20エリア" labeled double arrow — i.e. branches should be spaced at least 20-area apart from each other and from the main store, matching the "徒歩で来店するお客さんの限界20エリア分は離しておこう" text (walking-customer radius limit is 20 areas — same number as p.31's 徒歩 area radius = 20). CONFIRMED: recommended min. branch spacing = 20 areas, directly derived from the customer-walking-radius constant.

- **Branch/town-development interaction (PDF1 p.49)**: "店を中心にした土地の地価が上がる" — a store increases surrounding land value over time, more buildings then get built. "店にはさまれた土地はさらに発展" — land between TWO stores gets an even bigger land-value boost (higher building-appearance rate) than land near just one store — CONFIRMED bonus land-value-growth-rate mechanic for land sandwiched between two stores.

- **Rival store countermeasures — full Q&A/flowchart content (PDF1 p.52-55)**:
  - "ライバル店のお客さんを奪い取る3つのポイント": ①店のサービス度を上げる (raise service level — fountains/plants, AND cut 商品利益率/profit margin to draw customers: "商品利益率を引き下げてお客さんを呼び込んだりする。とくにこれと決めたライバル支店を撤退させるための基本作戦とその流れを解説") ②たばこ・酒の販売許可を取る (take tobacco/alcohol permits before rival does — exclusive-range mechanic reconfirmed) ③優秀な店員を導入する (deploy good staff, especially moving veteran staff to a brand-new branch immediately).
  - "ライバル店を撤退させる基本的フローチャート" (exact flowchart steps, left to right): 新しい店ライバル店近くに開店する → 15~新しい店の商品利益率を自分の店に引き込む(20%オフにする) → 数ヶ月連続で自分の店に引き込む → ライバル店が赤字を出す → ライバル店撤退 → 撤退後商品利益率を戻す → 次のライバル店開業する → 新店ライバル店の近くに (cyclical loop). (Exact flowchart text, transcribed as legible: "新しい店ライバル店近くに開店する" / "新しい店の商品利益率を15~20%オフにする" / "ライバル店の客を自分の店に引き込む" / "数ヶ月連続でライバル店が赤字を出す" / "ライバル店撤退" / "商品利益率を戻す" / "次のライバル店開業する" — some node text partially obscured by scan quality; core numeric fact CONFIRMED: recommended discount to undercut a rival is **15~20% off** on product profit margin, sustained for **several consecutive months** until the rival goes into deficit.)
  - "ライバル店を利用して、町を発展させることもできる" — surrounding a rival store with your own stores/land purchases raises land value faster (same land-value-between-two-stores bonus as p.49), can be exploited even using a RIVAL as one of the two anchor points, then withdraw the rival once land value is up.
  - "ライバル店を買収すれば、新規開業は必要なし!?" — buying out a rival: "すぐにでもライバル店を消してしまいたいなら、相手の店を買収してしまう事もできます。これは相手の店や社員ごと自分のものにできるのが特徴。もし黒字を出しているライバル店を買収できれば、次からは自分の利益となるのだ。ただし買収にはそれなりのお金が必要で、売り上げの高い店ほど額が高い。買収するなら早めにするのがお得といえそうだ。" Screenshot shows exact acquisition UI: "ライバル店 2号店 経路不明です 調査する 費用 ¥500,000 / 買収する 費用 ¥46,688,660 / 何もしない" — CONFIRMED exact costs example: 調査(investigate) ¥500,000, 買収(acquire) ¥46,688,660 for one sample rival branch (these are instance-specific numbers, not a fixed formula, but confirm the two-step 調査→買収 UI flow and that 調査 has a flat small cost while 買収 scales with the target's value).

- **Staff-management refinements (PDF1 p.56-57)**:
  - "新規開店と店員の移動" — newly hired staff for a new branch start with LOW stats across the board; recommended to move a veteran/experienced staffer from an existing store to manage (店長) the new one instead. "各店の能力を均等にすること" / "新しい店への移動はひとりずつ" (move only one staffer at a time between stores).
  - "新規雇用で気をつけること" — if unsatisfied with all candidates shown, ending recruitment and re-triggering it can reroll a fresh new set of applicants.
  - "賃金交渉は的確に行う" — "基準として2~3%のアップは認めてあげるのがいい。ところが人によっては10%以上のアップを求めることがある。こんな無理な要求には応える必要はないので、即刻却下。賃金交渉はその人の能力に応じて少しずつアップさせればいいので、無茶なアップ率は無視してもかまわないのだ。" — CONFIRMED: acceptable wage-raise-demand range guideline is 2-3%, demands of 10%+ are called out as excessive/rejectable. (Also see the PS-version-fixed-3%-no-negotiation footnote above.)

- **Accident/incident system — fire (火災) and shoplifting/robbery (万引き・強盗) (PDF1 p.58-59)**:
  - Fire: "お店の警備パラメータが低いとモラルの低いお客さんに火を付けられることがある。これが火事の原因だ。火事が発生すると消防車のサイレンが鳴り響くのですぐわかるはず。ただし分かったところでプレーヤーはどうすることもできない。ただジッと火が消えるのを待つしかないのだ。あとに残るのはお店を建て直すために必要な請求金額のみ。これを見てもわかるように、ひとたび火事が起こるとガクッと資産が減ってしまう。しかも中~上級マップになるとかなり頻繁に発生する可能性があるのだ。大切な資産をムダにしないためにも、お店の近くに消防署を誘致しておく。それがいちばんの対応策となる。" — CONFIRMED MECHANIC: fire is entirely un-interactable once started (player cannot extinguish it, must wait it out); rebuilding costs money; frequency scales up on medium/high-tier maps; only real counter is pre-emptive 消防署 attraction.
  - Shoplifting/robbery: "プレー中に突然「エッヘッヘッ」と妙な笑い声が聞こえたら要注意。これはお店の万引きが発生した証拠なのだ。お店の警備パラメータが低いと万引きは起こりやすく、さらにひどくなると強盗にまで入られてしまう。一度強盗が入ると売上金をゴッソリ持っていかれるので大赤字は確実。万引きや強盗の発生を防ぐためにも、早めの警察署の誘致をおすすめします。" (likely "警備署"/"交番" — text says 警察署 here, possibly a variant reference to 交番) — CONFIRMED: distinct audio cue "エッヘッヘッ" signals shoplifting in-progress; robbery is an escalated event that steals accumulated sales cash directly.
  - "学校近くの店は万引きに注意" callout: "近くに学校がありお客さんに子供が多いお店の場合、ほかの場合よりも万引きが多いようだ。学校の近くのお店はとくに警備パラメータを重視しよう。" — CONFIRMED: proximity to schools increases shoplifting rate (more child customers = more shoplifting risk).

- **Special events (PDF1 p.59)**:
  - "夏恒例! 花火大会開催" (Annual summer fireworks festival) — "毎年8月になると花火大会が開催される。美しい打ち上げ花火のグラフィックとともにお店にやってくるお客さんの数もアップする。ただし花火大会は一晩だけなので、このチャンスを逃さず売れ筋商品を用意して売りあげアップを狙おう。" — CONFIRMED: annual August fireworks festival (花火大会), one night only, boosts customer count (no exact multiplier number given — just "customer count goes up"); note this matches the task brief's "festival event, August" gap partially (guide calls it 花火大会, not お祭り, and gives no explicit sales multiplier digit — only qualitative "客数アップ"). Footnote: "※花火グラフィックはPS版にはありません。" (fireworks graphic absent on PS version — see Platform Difference Notes above).
  - "アイドル1日店長で満員御礼" (Idol-for-a-day store manager event) — "来店人数が1万人になると、それを記念してアイドルの女の子が一日店長としてやってくる。その日一日はお店の人気が100のままなので、おおいに売り上げを伸ばすチャンスだ。この後もお客さんの数に応じてアイドルがやってくることがある。" — CONFIRMED MECHANIC + exact trigger number: cumulative visitor count reaching **10,000 (1万人)** triggers a one-day "idol guest store manager" event where 人気 (popularity) is locked at maximum value **100** for that day. Recurs again at further visitor-count milestones ("その後もお客さんの数に応じて").

- **Shelf/wagon spacing rule — "1ブロックのあき" (PDF1 p.65)**: Exact quoted rule: "棚やワゴンを使うときは最低1ブロックのあきが必要" (When using shelves or wagons, a minimum of 1 block of open space is required.) Context: "お店のある部分の棚の商品が全然売れない" Q&A — answer explains shelves/wagons can only be accessed from their open side(s); if another shelf/wagon is placed directly against that access side, or the shelf is oriented facing a wall with no gap, customers physically cannot reach the items: "棚は一方向からしか商品を取り出せない。その方向にほかの棚やワゴンがあると、いくら欲しい商品が置いてあっても手にすることができなくなるのだ。" — This is the closest CONFIRMED numeric statement found so far for the "aisle/passage width" mechanic gap: it's framed as a fixture-clearance rule (≥1 empty block/masu in front of a shelf's pick-up side) rather than an explicit "1-masu vs 1/2-masu passage width for customer walking" rule. No explicit "0.5マス" (half-masu) terminology was found anywhere in PDF1.

- **Seasonal/weather sales effects (PDF1 p.68)** — Q&A "季節や天候、時間帯によって売り上げに差は出るのでしょうか!?": 
  - Answer confirms YES, qualitatively: "季節や時間によってグラフィックが変化するように、お客さんのほしい商品も変化している。それに合わせて商品を入れ替えれば、それだけ売り上げだってアップするはずだ。" + "夏には冷たい飲み物を多めに配置、逆に寒い冬にはあったかい中華まんやおでんといった商品を導入するといいだろう。" + "とくに夏と冬では売れる商品が大きく変わるので、年に2回は品物を替えたほうがいいだろう。"
  - "雨の日、こんな日は客の入りも悪い" — CONFIRMED qualitative rule: rainy days reduce customer traffic ("客の入りも悪い"). No exact percentage given on this page (task brief's weather % table is likely in PDF3's クイックリファレンス book — not found in PDF1).
  - "夜~深夜にかけてお酒を買いに来る人が増える" — reconfirms night/late-night alcohol-buyer increase (matches p.23 time-of-day wheel).
  - "寒い季節ホカホカの中華まんが好調" — cold season → hot 中華まん (steamed buns) sell well (seasonal item-demand callout, no exact percentage).
  - No explicit numeric weather-type percentage table (荒天/大雨/雨天/台風/大雪 etc.) found anywhere in PDF1 — flagged as still an open gap after this file; continue checking PDF3 (クイックリファレンス, 時間 section) specifically.

- **Break room (休憩室) stamina recovery — 2 tiers (PDF1 p.69)**: "休憩室は店員がスタミナを回復する場所。スタミナが完全回復するまでは、店員は絶対出てこようとしないのだ。その間お店はほったらかし。レジ前だってお客さんで混雑してしまうのだ...休憩室には2種類あるのだが、その値段によってスタミナ回復率が違うのだ。もちろん高いほうが回復率が高いので、できるだけ高価な休憩室を用意。店員のスタミナ回復が早くすむようにしてあげよう。" — CONFIRMED: exactly 2 break-room tiers exist, priced differently, with recovery RATE (not just capacity) scaling with price; staff will NOT leave the break room until stamina is fully restored (matches p.16's info, now confirmed store is literally unstaffed at register during this time).

- **Parking lot sizing guidance (PDF1 p.70)**: "駐車場はどのくらい必要でしょうか!?" — "遠距離のお客さんを呼びむためには駐車場は必要不可欠。ただし多ければ多いほどいいというのは間違いだ。なぜなら立体駐車場は、かなり維持費が高いからだ。こんな駐車場をいくつも建てるとお店の黒字も維持費で消えていってしまう。だからこそ駐車場は適度な数がほしい。最初はいちばん安い駐車スペースをいくつか用意。駐車場が足りなくなると「ビッビッ」とクラクションの音が聞こえてくる、そうなったら新しい駐車場を導入しよう。最初から大型駐車場は損をするだけだぞ。" — CONFIRMED: an audible car-horn cue ("ビッビッ") signals insufficient parking; recommends starting with the cheapest parking spaces and scaling up only as needed; multi-story/立体駐車場 (multi-level parking) exists as a distinct, expensive-upkeep parking type.

- **Restocking / customer-stress mechanic (PDF1 p.71)**: "気がつくと棚やワゴンが空になっています" Q&A — "商品が売れれば品物は減っていき、最後には棚やワゴンは空になってしまう。充充するのも店員の仕事で、ひとつの棚やワゴンに補充すれば能力がアップしていく。この場合は店員の能力が低くて補充が間に合わなかったのだ。プレーヤーが棚やワゴンにカーソルを合わせて補充することもできるが、店員が育たないので、よっぽどのことがない限り待っていることをおすすめする。" — confirms player CAN manually restock via cursor (emergency override) but it stunts staff 補充 stat growth if overused; callout "こまめな商品補充でお客さんのストレスをためない" ties empty shelves directly to a "customer stress" concept (implicitly customer anger/leaving).

- **Idol event exact recurrence interval (PDF2 p.89, refining PDF1 p.59)**: "攻略㊙テク3 アイドルの人気を利用せよ" — "1万人の来店ごとに店の1日オーナーを勤めてくれるアイドル。このイベントが起きればどんな店舗でも一時的に人気値が最高になる。積極的に利用していきたい。" — CONFIRMS the recurrence is exactly **every additional 10,000 (1万人) cumulative visitors**, not a one-time event; refines PDF1 p.59's vaguer "その後もお客さんの数に応じて".

- **Store size upgrade guidance + staff-transfer-freeze rule (PDF2 p.88)**: "新店舗にベテランを派遣" — "できたばかりの店は人気値が低い。お客の入りが悪い店、人材ともに成長に時間がかかるので、ここは思い切ってベテラン店員を異動させてやろう。能力の高い店員で切り盛りすれば、人気値も楽に上がるはずだ。ただし、全員異動は厳禁だぞ!" — CONFIRMED explicit warning: do NOT transfer ALL staff out of a store at once (leaving it with zero experienced staff is explicitly warned against).
- "商品配置とレイアウトのコツ" — "店の位置、店員と並んで重要なのがこのレイアウト。売れ筋商品をレジのそばに、なるべく多くの商品をまんべんなくの2つを基本に、効率のよい店舗を造りあげよう。"

- **初級MAP (Beginner map) exact stats (PDF2 p.86)**: "MAP詳細": 住人 2,179人 / ライバル店 2店舗 / 施設: 交番×2, 消防署×1, 小学校×1, 中学校×1. Clear condition: "都庁を誘致する" — "「誘致」となってはいるが、具体的には人口を増やせば都庁は自然と建設される。経営よりも町を発展させることがポイントになる。" — CONFIRMED: the 都庁 (city hall) is not directly player-purchasable via the normal 誘致 facility list (not in the p.45 table) — it appears automatically once town population crosses some threshold, and reaching it is the win condition for the Beginner map. Suggested clear time: "8年ほどの経営で都庁誘致できるはずだ。"

- **EXACT STORE DIMENSIONS — all 6 store types, full breakdown (PDF2 p.106-109)** — this is a major, precise table, transcribed in full. Each of the 6 store types (店舗1~6, matching the "小/中/大 × 縦/横" set from PDF1 p.10) gets: 建物代 (cost), 店舗内 (interior WxH), 店舗外周 (exterior perimeter WxH), 屋外スペース (outdoor space WxH), 総面積 (total area), 建物全体 (whole building area), 床面積 (floor area), 店外スペース (exterior space area):
  | 店舗 | 建物代 | 店舗内 | 店舗外周 | 屋外スペース | 総面積 | 建物全体 | 床面積 | 店外スペース |
  |---|---|---|---|---|---|---|---|---|
  | 店舗1 (小・縦) | ¥6,000,000 | 5×8 | 7×10 | 3×10 | 100 | 70 | 40 | 30 |
  | 店舗2 (小・横) | ¥6,000,000 | 8×5 | 10×7 | 10×3 | 100 | 70 | 40 | 30 |
  | 店舗3 (中・縦) | ¥12,000,000 | 7×10 | 9×12 | 3×12 | 144 | 108 | 70 | 36 |
  | 店舗4 (中・横) | ¥12,000,000 | 10×7 | 12×9 | 12×3 | 144 | 108 | 70 | 36 |
  | 店舗5 (大・縦) | ¥18,000,000 | 8×12 | 10×14 | 3×14 | 196 | 154 | 108 | 42 |
  | 店舗6 (大・横) | ¥18,000,000 | 12×8 | 14×10 | 14×3 | 196 | 154 | 108 | 42 |
  - IMPORTANT DISCREPANCY vs PDF1 p.10: PDF1 stated construction costs as 小=¥6,000,000 / 中=¥12,000,000 / 大=¥24,000,000, and store footprints as 10×10 / 12×12 / 16×16. PDF2's table here instead gives 大 (large) a cost of **¥18,000,000** (not ¥24,000,000) and interior dimensions of 8×12 / 12×8 (total footprint ~10×14/14×10 incl. exterior, not 16×16). CONFIRMED PRIMARY-SOURCE CONFLICT between PDF1 p.10 and PDF2 p.106-109 on the large-store price and dimensions — flag explicitly for the decision doc; PDF2's table is more granular/structured (breaks out interior vs exterior vs floor vs outdoor-space area) and may reflect a more precise/later-verified source, but this is NOT something to silently resolve — needs a project decision on which figure to trust, or whether both are correct for DIFFERENT things (e.g. PDF1's "16×16"/¥24,000,000 might be the outer plot size player purchases, while PDF2's "8×12 interior"/¥18,000,000 might be actual buildable floor — but the SMALL and MEDIUM costs match exactly between both sources: ¥6,000,000 and ¥12,000,000, so only the LARGE tier's cost differs, which is odd if it were just a units/scope difference. Recommend flagging in `docs/decisions/` as an unresolved primary-source conflict rather than picking one arbitrarily.)
  - Also note: PDF2's "小" interior is 5×8 (=40 floor tiles) with 7×10 exterior perimeter and 3×10 outdoor space — i.e. total footprint 7×10=70 "building total," plus 3×10=30 outdoor parking/exterior space, total plot 100 = matches PDF1's "10×10" if 10×10=100 total plot size (7×10 building + 3×10 outdoor space stacked = 10×10 if outdoor space is a 3-wide strip alongside the 7-wide building, both 10 deep). This partially RECONCILES the small/medium tiers as consistent (10×10 total plot = 7×10 building + 3×10 outdoor; 12×12... wait PDF2's medium totals to 9×12+3×12=12×12 ✓. So small/medium DO reconcile arithmetically between the two sources. Large should reconcile the same way: PDF2 gives 10×14+3×14 = 13×14, NOT 16×16 as PDF1 states. This confirms the large-tier discrepancy is real and not just a units misunderstanding — the total footprint arithmetic itself (13×14=182 vs PDF1's implied 16×16=256) does not match. This is a genuine unresolved conflict.)

- **Owner evaluation (オーナー評価) — 5-metric system, partially enumerated (PDF2 p.98, p.101)**: "オーナーに対する評価は店舗数、人口など5つの要素で成り立っている。これは大きく店舗経営と町の発展の2つに分けられる。" — CONFIRMS exactly 5 metrics feed into a separate "オーナー評価" (distinct from the per-store 店舗評価 stars), each independently ranked to a max of ★★★★ (4 stars, NOT 5, per "すべて最高値の★★★★にすれば" — note this is a DIFFERENT star-max than per-store evaluation's apparent 5-star max seen elsewhere). Only 店舗数 (store count) and 人口 (population) are explicitly named as 2 of the 5 on p.98; p.101 adds a 3rd: "オーナー評価で上げにくいのが年商と店舗数の2つの要素" — confirms 年商 (annual revenue) is also one of the 5. The remaining 2 of the 5 metrics are NOT explicitly named in PDF1/PDF2 text seen so far (task brief's guess of 治安/繁栄/サービス for "オーナー評価" categories is NOT yet confirmed by primary source — still an open gap; check PDF3 クイックリファレンス for the full named list of 5).
  - "年商を増やす2つの方法": ①黒字経営のお店を増やす(store count up naturally raises 年商) ②売り上げのいい店を改築して大規模店へ(remodel a high-performing store to large size to raise its per-store revenue ceiling).
  - Clear condition for 上級 (Advanced) map: "オーナー評価を★★★★にする" (all 5 owner-evaluation metrics maxed to 4 stars each).

- **中級 (Intermediate) map exact stats (PDF2 p.92)**: Clear condition: "10店舗建設する" (build 10 total stores, honten+branches combined: "本店、支店を合わせて10店舗にすればクリア。雇える店員数に限りがあるため、ライバル店をいくつか潰さないとクリアは難しい."). MAP詳細: 住人 1,876人 / ライバル店 3店舗 / 施設: 交番×2, 消防署×1, 幼稚園×1, 中学校×1, 公園×1. Pacing guidance: "最初の2年で3店舗。後は1年ごとに1店舗建築を目安に、10~12年ほどの経営でクリアを目指したい。"

- **上級 (Advanced) map exact stats (PDF2 p.98)**: Clear condition: "オーナー評価を★★★★にする". MAP詳細: 住人 1,424人 / ライバル店 1店舗 / 施設: 交番×1, 消防署×1, 小学校×1, 公園×1. Pacing guidance: "12~15年くらいを目標に、気長に経営すること。" Special note: this map has only 1 rival store total, and it cannot be bought out because... (text says buyout unavailable here per "攻略㊙テク7" context implies rival too strong/unreachable — actually re-reading: "このMAPはライバル店が1店舗しかないので、買収ができない" — CONFIRMED: with only 1 rival store on the map, the buyout option is explicitly UNAVAILABLE (reason not elaborated beyond "だけしかない" — likely a scripted map restriction rather than a general game rule).

- **Wage-increase-refusal endgame tech (PDF2 p.99)**: "攻略㊙テク7 賃金アップはすべて無視" — "上級になると多くなる賃金アップの要求。借りい店舗でない限り、すべて要求は無視してしまおう。数年経てば辞めた店員も、また募集に応じるようにからね。" — CONFIRMED: refusing a wage-raise demand can cause that staffer to eventually QUIT ("辞めた店員"), but they may reapply as a new applicant again after some years. Screenshot shows exact in-game text: "山中光次さんが10%の賃金上げを要求しています 受け入れる/受け入れない".

- **Hidden 4th map + PLATFORM DIFFERENCE (PDF2 p.104)**: "3つの町を独占すると、最後のマップが現れる!" — "このゲームで普通選べるマップは初級、中級、上級の3つ。ところがこの3つのマップをクリアーしたとき、隠しマップともいえる新しいマップが出現するらしいのだ。しかもそのマップはサターン版とプレイステーション版とでは形が違うとのことだ。" — CONFIRMED: clearing all 3 named maps unlocks a 4th, secret/unnamed map, AND its shape/layout DIFFERS between the Sega Saturn version and the PlayStation version (explicit platform divergence — highly relevant for "which version are we recreating" scope decisions, joining the p.57/p.59 platform-difference notes already found). Map-select screen shown lists exactly: "初級··都庁を誘致する" / "中級··10店舗建設する" / "上級··オーナー評価を★★★★にする" (this triple confirms the exact clear-condition wording verbatim for all 3 maps in one place).

- **FIXTURE DATA — full 設備データ table, exact numeric stats for every fixture (PDF2 p.110-119)** — MAJOR FIND, directly resolves the "shelf/fixture types and attention (注目度)" research gap with hard numbers. Fields per fixture: 価格(price)/注目度(attention level)/維持費(daily upkeep)/大きさ(size WxH)/収納力(storage capacity)/設置場所(placement location: 店内=indoor only, 店内・外=indoor or outdoor, 店外=outdoor only)/取扱商品(compatible product categories).
  | 設備名 | 価格 | 注目度 | 維持費 | 大きさ | 収納力 | 設置場所 | 取扱商品 |
  |---|---|---|---|---|---|---|---|
  | 小型常温棚 | 60 | 10 | 24 | 1×1 | 40 | 店内 | パン類/インスタント類/菓子類/本類/文房具/電気製品類/レトルト類/調味料類/日用品/下着類 |
  | 中型常温棚 | 100 | 10 | 48 | 2×1 | 80 | 店内 | (same list as small) |
  | 大型常温棚 | 140 | 10 | 72 | 3×1 | 120 | 店内 | 弁当類/パン類/インスタント類/菓子類/本類/文房具/電気製品類/レトルト類/調味料類/日用品/薬品/下着類 (note: 大型 adds 弁当類 and 薬品 vs small/med) |
  | 小型常温ワゴン | 30 | 20 | 24 | 1×1 | 15 | 店内 | 弁当類/パン類/インスタント類/菓子類/本類/文房具/電気製品類/レトルト類/調味料類/日用品/薬品/下着類 |
  | 中型常温ワゴン | 50 | 20 | 48 | 2×1 | 30 | 店内 | (same as small wagon) |
  | 大型常温ワゴン | 70 | 20 | 72 | 3×1 | 45 | 店内 | (same) |
  | 大型常温ワゴン2 | 90 | 30 | 96 | 2×2 | 60 | 店内 | (same) |
  | 小型冷蔵棚 | 200 | 10 | 720 | 1×1 | 30 | 店内 | 冷たい飲料/酒類/弁当類/野菜類/魚類/肉類/薬品 |
  | 中型冷蔵棚 | 350 | 10 | 1200 | 1×1(sic, likely 2×1) | 60 | 店内 | (same) |
  | 大型冷蔵棚 | 500 | 10 | 1920 | 3×1 | 90 | 店内 | (same) |
  | 小型冷蔵ワゴン | 120 | 20 | 960 | 1×1 | 10 | 店内 | 冷たい飲料/酒類/弁当類/野菜類/魚類/肉類/薬品 |
  | 中型冷蔵ワゴン | 200 | 20 | 1680 | 2×1 | 20 | 店内 | (same) |
  | 大型冷蔵ワゴン1 | 280 | 20 | 2400 | 3×1 | 30 | 店内 | (same) |
  | 大型冷蔵ワゴン2 | 360 | 30 | 3120 | 2×2 | 40 | 店内 | (same) |
  | 小型冷凍棚 | 300 | 10 | 2160 | 1×1 | 25 | 店内 | 冷凍食品類/アイスクリーム |
  | 中型冷凍棚 | 500 | 10 | 3600 | 2×1 | 50 | 店内 | (same) |
  | 小型冷凍ワゴン | 200 | 20 | 1920 | 1×1 | 10 | 店内 | 冷凍食品類/アイスクリーム |
  | 中型冷凍ワゴン | 380 | 20 | 3120 | 2×1 | 20 | 店内 | (same) |
  | 温飲料専用ケース | 300 | 20 | 1680 | 1×1 | 20 | 店内 | 温かい飲料 |
  | おでん専用ケース | 100 | 30 | 1920 | 1×1 | 10 | 店内 | おでん |
  | 中華まん専用ケース | 300 | 30 | 1920 | 1×1 | 20 | 店内 | 中華まん |
  | イベント棚 | 600 | 40 | 1920 | 2×1 | 60 | 店内 | イベント商品 |
  | イベントワゴン | 300 | 60 | 1200 | 2×1 | 30 | 店内 | イベント商品 |
  | 小型たばこ自販機 | 600 | 15 | 240 | 1×1 | 20 | 店内・外 | たばこ |
  | 大型たばこ自販機 | 1000 | 20 | 480 | 2×1 | 40 | 店内・外 | たばこ |
  | 小型冷飲料自販機 | 800 | 15 | 480 | 1×1 | 20 | 店内・外 | 冷たい飲料/酒類 |
  | 大型冷飲料自販機 | 1400 | 20 | 960 | 2×1 | 40 | 店内・外 | 冷たい飲料/酒類 |
  | 小型温冷飲料自販機 | 1000 | 15 | 960 | 1×1 | 15 | 店内・外 | 冷たい飲料/温かい飲料 |
  | 大型温冷飲料自販機 | 1800 | 20 | 1920 | 2×1 | 30 | 店内・外 | 冷たい飲料/温かい飲料 |
  | 小型コピー機 | 1500 | 10 | 1200 | 1×1 | 20 | 店内 | コピー用紙 |
  | 中型コピー機 | 2000 | 15 | 1440 | 2×1 | 40 | 店内 | コピー用紙 |
  | レジ1 | 2000 | 15 | 1440 | 2×1 | 0 | 店内 | なし |
  | レジ2 | 3000 | 25 | 1680 | 2×1 | 60 | 店内 | 宅急便申込書 |
  | レジ3 | 3000 | 20 | 1680 | 3×1 | 0 | 店内 | なし |
  | レジ4 | 5000 | 30 | 1920 | 3×1 | 90 | 店内 | 宅急便申込書 |
  | 室内型ディスペンサー(小/安) | 4000 | 20 | 1440 | 1×1 | 50 | 店内 | 現金 |
  | 室内型ディスペンサー(大/高) | 7000 | 30 | 2400 | 1×1 | 90 | 店内 | 現金 |
  | 観葉植物 | 1000 | 0 | 120 | 1×1 | 0 | 店内・外 | (none — service item) |
  | ベンチ | 2000 | 0 | 160 | 1×1 | 0 | 店内・外 | (none) |
  | 噴水 | 5000 | 0 | 2400 | 2×2 | 0 | 店内・外 | (none) |
  | 社員休憩室1 | 3000 | 0 | 1200 | 2×2 | 0 | 店内・外 | (none) |
  | 社員休憩室2 | 7000 | 0 | 2400 | 2×2 | 0 | 店内・外 | (none) |
  | 駐車場 | 500 | 0 | 0 | 1×2 | 2 (cars) | 店外 | (none) |
  | 2階建駐車場 | 1000 | 0 | 240 | 1×2 | 4 (cars) | 店外 | (none) |
  | タワー駐車場 | 9000 | 0 | 4800 | 3×2 | 20 (cars) | 店外 | (none) |
  - CONFIRMS (per legend p.110): "注目度・お客への商品のアピール度" (attention = how much the fixture appeals to/draws customers), "収納力・収納できる商品数の最大値" (storage capacity = max item count), "維持費・1日当りの維持費" (upkeep is a DAILY figure).
  - CONFIRMS wagons consistently have HIGHER 注目度 than same-tier shelves (棚=10, ワゴン=20, event/special ワゴン up to 60) — hard-numbers backing for PDF1's qualitative "ワゴンは注目度も高い" claim.
  - CONFIRMS レジ (registers) and サービス品 (fountain/bench/plants/break rooms/parking) all have 注目度=0 — they do not directly attract customers via the attention stat (their benefit is through other channels: サービス度, capacity, etc.).
  - CONFIRMS parking lot capacities: 駐車場=2 cars, 2階建駐車場=4 cars, タワー駐車場=20 cars, with upkeep scaling hugely (¥0/¥240/¥4800 per day respectively) — direct numbers for the parking-tier mechanic gap.
  - CONFIRMS exact break-room costs/upkeep: 休憩室1=¥3,000/¥1,200 day, 休憩室2=¥7,000/¥2,400 day (matches PDF1 p.17's screenshot numbers ¥7,000/¥2,400 for the pricier tier).
  - Legend also confirms register field "取扱商品: なし" for レジ1/3 vs "宅急便申込書" for レジ2/4 — CONFIRMS only specific register models can process 宅配便 (home delivery) applications.

- **AD DATA — 広告データ table, CROSS-CONFIRMS PDF1 p.36-37 exactly, with cleaner field labels (PDF2 p.120-121)**: Identical costs/timing/effect numbers as PDF1, now labeled explicitly per-ad as 宣伝費/実行時/効果:
  | 広告 | 宣伝費 | 実行時 | 効果 |
  |---|---|---|---|
  | ダイレクトメール | ¥100,000 | 毎月2日 10時 | 人気12UP |
  | 新聞広告 | ¥500,000 | 毎月2日 7時 | 人気20UP |
  | 飛行船 | ¥1,000,000 | 毎月3日 15時 | 人気40UP |
  | ラジオCM | ¥3,000,000 | 毎月1日 17時 | 人気60UP |
  | テレビCM | ¥5,000,000 | 毎月1日 19時 | 人気90UP |
  - CONFIRMS "効果" is literally a 人気 (popularity) stat increase in flat points (12/20/40/60/90), and "実行時" is a FIXED recurring monthly day+hour (not a delay from order — it's a fixed calendar slot each month: e.g. ダイレクトメール always lands on "毎月2日10時" = the 2nd of every month at 10:00). This REFINES PDF1's ambiguous "宣伝日時" framing (previously read as an order-to-effect delay) — CORRECTED interpretation: each ad type has a FIXED monthly airdate/time when its effect triggers, and presumably you must place the order before that date each month for it to land.

- **PRODUCT DATA — 商品データ table, full 定価/原価率/利益率 per category — DIRECTLY ANSWERS the profit-margin/pricing mechanic gap (PDF2 p.122-125)**: Fields defined in legend: "定価: 商品の店頭販売価格(標準時)" (list/standard retail price), "原価率: 定価に対する仕入価格の割合" (cost ratio = wholesale cost as % of retail price), "利益率: 定価に対する販売利益の割合" (profit ratio = profit as % of retail price). NOTE: 原価率+利益率 = 100% exactly for every row checked (e.g. 冷たい飲料: 50+50=100; インスタント類: 60+40=100) — CONFIRMS 利益率 = 100% − 原価率 always, i.e. these are complementary fractions of 定価.
  | 商品カテゴリ | 定価 | 原価率 | 利益率 |
  |---|---|---|---|
  | 冷たい飲料 | 110 | 50 | 50 |
  | インスタント類 | 150 | 60 | 40 |
  | 温かい飲料 | 110 | 50 | 50 |
  | 菓子類 | 200 | 60 | 40 |
  | 酒類 | 1000 | 70 | 30 |
  | 本類 | 400 | 60 | 40 |
  | 弁当類 | 400 | 60 | 40 |
  | たばこ | 250 | 70 | 30 |
  | パン類 | 300 | 50 | 50 |
  | アイスクリーム | 100 | 50 | 50 |
  | 文房具 | 150 | 60 | 40 |
  | レトルト類 | 600 | 60 | 40 |
  | 電機製品類 | 800 | 60 | 40 |
  | 調味料類 | 400 | 60 | 40 |
  | 野菜類 | 1500 | 50 | 50 |
  | 冷凍食品類 | 500 | 60 | 40 |
  | 魚類 | 1000 | 60 | 40 |
  | おでん | 250 | 50 | 50 |
  | 肉類 | 1200 | 50 | 50 |
  | 日用品 | 800 | 60 | 40 |
  | コピー用紙 | 50 | 60 | 40 |
  | イベント商品 | 1000 | 60 | 40 |
  | 宅急便申込書 | 1000 | 80 | 20 |
  | 中華まん | 170 | 60 | 40 |
  | 薬品 | 1500 | 70 | 30 |
  | 現金 (cash, for ATM/dispenser) | 0 | 100 | 0 |
  | 下着類 | 1000 | 60 | 40 |
  - This is a CONFIRMED_OFFICIAL, exact per-category default baseline pricing table — highest value: 酒類/たばこ/薬品/宅急便申込書 all have the LOWEST 利益率 (30/30/30/20 respectively) despite requiring a purchase permit (酒/たばこ/薬品) — i.e. the permit-gated goods actually have BELOW-AVERAGE default profit margins per unit but presumably high volume/no-competition value (matches PDF1 p.9's framing of them as valuable due to exclusivity, not raw per-unit margin). 宅急便申込書 (home delivery form) has the single lowest margin of all at 20%.
  - "薬品などの販売許可は大規模店でない限り取る必要はあまりない" (PDF2 p.101) now makes sense against this table: 薬品 has a middling-low 30% margin, so it's only worth the ¥10,000,000 permit cost at high volume (large stores).
  - Note: 商品利益率 as adjusted by the player in the 営業方針/価格設定 screens (e.g. "全商品平均利益率 45%") appears to be a STORE-WIDE OVERRIDE multiplier/target applied on top of or in place of these category baselines — the exact interaction formula between this per-category baseline table and the player-adjustable "全体に統一 X%UP" / per-item override sliders seen in PDF1 pp.18-23/50/62 is not explicitly spelled out on this page. Recommend treating the per-category 原価率/利益率 numbers here as the DEFAULT/base values before any player pricing-policy adjustment.

- **STAFF DATA — 店員データ samples, reveals hidden "能力の分岐ポイント" (ability branch/breakpoint) stat (PDF2 p.126-127)**: Legend adds crucial NEW definitions beyond PDF1's 7-stat page:
  - "性格・以下の能力の最大値を表す" (personality/aptitude — determines the MAXIMUM value each ability can reach for this individual staffer): スタミナ(体力)=仕事の持続力; 敏捷性=商品補充力とお客の回避能力の最大値; 賢さ(学歴)=レジ処理能力とセキュリティ能力の最大値; 社交性=サービス能力と清掃能力の最大値. — CONFIRMS the pre-hire résumé 4-stat system (体力/学歴/敏捷性/社交性) are literally CAPS/ceilings on pairs of the real in-job stats, not just loose correlates as PDF1 implied: 体力→スタミナ cap; 敏捷性→[補充,回避] cap; 賢さ(学歴)→[レジ,セキュリティ] cap; 社交性→[サービス,清掃] cap.
  - "能力・ゲーム開始時の各店員の能力" — 6 stats shown at hire: サービス/レジ/清掃/補充/セキュリティ, PLUS "教育" listed SEPARATELY as its own headline value (e.g. "能力:教育90") — 教育 defined here as "店長になった時の、店員に対する教育能力" (the education stat only matters once that staffer becomes 店長).
  - "能力分岐ポイント" — NEW mechanic not mentioned in PDF1: "各能力の成長の度合いが鈍くなり始める数値" (the value at which each ability's growth rate begins to slow down) — i.e. stat growth is NOT linear all the way to 100; each stat has an individual "breakpoint" per staffer beyond which XP gains diminish. Exact sample breakpoint values shown per staffer (5 stats each: サービス/レジ/清掃/補充/セキュリティ), e.g. 竹中小百合 (28歳女, 時給280円, 教育90): サービス54/レジ52/清掃52/補充48/セキュリティ51; 吉田有紀(24歳女,270円,教育65): サービス44/レジ45/清掃41/補充40/セキュリティ38; 小宮千明(30歳女,280円,教育70): サービス44/レジ41/清掃44/補充44/セキュリティ44; 浜田夕子(22歳女,270円,教育55): サービス33/レジ44/清掃40/補充25/セキュリティ27; 万田町子(42歳女,320円,教育65): サービス41/レジ55/清掃36/補充35/セキュリティ42.
  - Base stats at hire for these 5 sample staff (スタミナ/敏捷性/賢さ/社交性 aptitude-cap format, and initial サービス/レジ/清掃/補充/セキュリティ): 竹中小百合: 格 スタミナ80/敏捷性65, 賢さ90/社交性90; initial サービス14/レジ14/清掃14/補充12/セキュリティ14. 吉田有紀: スタミナ60/敏捷性80, 賢さ65/社交性80; サービス11/レジ10/清掃11/補充11/セキュリティ10. 小宮千明: スタミナ70/敏捷性70, 賢さ70/社交性75; サービス13/レジ13/清掃13/補充13/セキュリティ13. 浜田夕子: スタミナ65/敏捷性70, 賢さ55/社交性50; サービス10/レジ11/清掃9/補充9/セキュリティ9. 万田町子: スタミナ70/敏捷性65, 賢さ65/社交性60; サービス17/レジ20/清掃17/補充17/セキュリティ18.
  - Time budget note: this section (店員データ) likely continues with more sample staff on subsequent pages of PDF2 not yet read at this point in the batch — continue watching next batch.

- **STAFF DATA — remaining sample staff (PDF2 p.128-133)**: Same format as p.126-127 (age/gender/wage/教育/性格-caps/initial 5 stats/分岐ポイント breakpoints for サービス・レジ・清掃・補充・セキュリティ). Full name list transcribed with key headline numbers (教育 value and wage) for reference: 富永福子(58歳女,320円,教育70), 花沢咲江(46歳女,330円,教育55), 忍田信子(39歳女,320円,教育70), 里中涼子(18歳女,270円,教育80), 市川智恵子(35歳女,300円,教育70), 山本信夫(31歳男,290円,教育60), 杉村真知子(32歳女,300円,教育85), 山下大介(16歳男,250円,教育50), 田中幸子(44歳女,330円,教育80), 杉本三郎(36歳男,300円,教育55), 雨中聖人(22歳男,270円,教育40), 南田洋次(40歳男,310円,教育75), 秋本三四郎(28歳男,280円,教育70), 谷口明(26歳男,280円,教育60), 佐々木信雄(20歳男,270円,教育70), 長沢達也(34歳男,310円,教育80), 森山雪之丈(26歳男,280円,教育80), 今野京介(21歳男,280円,教育85), 西田年男(53歳男,340円,教育75), 丸山昭夫(28歳男,280円,教育75), 福本孝仁(32歳男,310円,教育95), 高橋大介(24歳男,280円,教育75), 小田伸行(27歳男,280円,教育65), 奥平康夫(51歳男,340円,教育95), 池上秀夫(25歳男,270円,教育60), 中山光次(17歳男,260円,教育80), 金田哲也(36歳男,330円,教育85), 的場丈二(19歳男,260円,教育70), 菅原文夫(42歳男,330円,教育85), 朝田宗司(43歳男,310円,教育50).
  - Cross-check: 中山光次 (17歳男, ¥260/日 — note: earlier PDF1 screenshots showed this exact character "中山光次 17歳男" at ¥4,160/日 as a starting hire example; the daily wage shown in PDF1's gameplay screenshot (¥4,160/日) is a full daily wage total, whereas this PDF2 table's "時給" column (¥260) is the hourly rate — consistent with the age-based hourly wage formula 時給=年齢×10+100 (17×10+100=270, close to but not exactly 260, small deviation possibly individual variance or rounding — not a perfect match, flagging as a minor inconsistency worth double-checking against the formula).
  - Overall this staff-data section (~35 named sample employees across p.126-133) functions as the game's fixed/semi-fixed hiring-pool roster with individual pre-set stat caps and breakpoints — useful ground truth for reproducing exact hire-candidate stat distributions rather than fully randomizing them.

- **CUSTOMER DATA — 顧客データ, full archetype system with exact column definitions (PDF2 p.134-143)** — MAJOR FIND for customer-AI reconstruction. Exact legend (17 numbered fields per p.134):
  1. 名前=customer archetype name; 2. グラフィック; 3. 推定年齢=estimated age range; 4. 買い物開始時=approx shopping start time; 5. 買い物所要時間=time required to shop; 6. 所持金=money on hand; 7. 来店方法=arrival method; 8. ス=スタミナ・レジに並ぶなどの持久力 (stamina — register-queue endurance); 9. 素=素早さ・商品選びなどの速さ (quickness — speed of picking items); 10. マ=マナー・万引きのしやすさ、コメントのしやすさ (manners — propensity to shoplift / to voice complaints); 11. 集=集中力・欲しい商品以外の買いにくさ (concentration — resistance to impulse-buying non-wanted items); 12. 買=買物重要度・お客にとっての買物の重要度の高さ (shopping importance/priority); 13. 価=価格重視度・お客が来店する際の商品価格に対するこだわりを表す (price-sensitivity weight); 14. 距=距離重視度・お客が来店する際の店との距離に対するこだわりを表す (distance-sensitivity weight); 15. サ=サービス重視度・お客が来店する際のサービスに対する重視度を表す (service-sensitivity weight); 16. 平=平日に来店する割合 (weekday visit ratio %); 17. 休=休日に来店する割合 (holiday visit ratio %); plus 一番欲しい商品 (top wanted item) and ついでに欲しい商品1~3 (up to 3 incidental/impulse want items).
  - CONFIRMED: this is the closest primary-source material found to the task brief's "customer pathing rule" gap — customers are modeled with explicit numeric **価格重視度 (price weight) / 距離重視度 (distance weight) / サービス重視度 (service weight)** used presumably to choose WHICH store to visit among options (not literally a "shortest in-store route" pathing formula — no explicit "最短ルートを選ぶ" sentence was found verbatim anywhere in PDF1 or PDF2; the in-store movement behavior described elsewhere (moving toward wanted item, wandering if stuck) appears to be the actual in-store movement model, while these 距離重視度 etc. weights appear to be STORE-CHOICE / visit-frequency decision weights, a different layer of the simulation).
  - Full archetype roster observed (name / age range), each with MULTIPLE time-of-day rows (different 買い物開始時 entries, each its own money/wanted-item/stat combination — same archetype can appear 5-20+ times across the day with different specific wanted-item combos):
    - 女子大生 (18-23歳) — ~14 time-rows spanning 6:00-22:00, stats consistently around ス50/素80-100/マ40-90/集10-30/買30-100/価20-100/距10-100/サ50-100/平~20/休~50 (exact per-row values transcribed in source; representative row: 6:00,120分,徒歩,¥500,ス50/素80/マ70/集10/買30/価50/距80/サ20/平100/休50, wants パン類, ついでに冷たい飲料/菓子類/日用品).
    - 大学生 (18-23歳) — ~20 time-rows spanning 6:00-3:00(overnight), similar stat shape, higher price-sensitivity variance (some rows 価=100 very price sensitive at low buy-importance).
    - サラリーマン (25-40歳) — ~15 time-rows spanning 5:00-0:00, generally 平=100/休=20 (strongly weekday-visiting archetype) — CONFIRMS サラリーマン is explicitly modeled as an almost-exclusively-weekday customer type.
    - OL (20-38歳) — ~11 time-rows spanning 6:00-22:00, similarly weekday-heavy (平~100/休~20).
    - おじさん (40-55歳) — ~6 time-rows spanning 15:00-23:00 (afternoon/evening only), uses 自動車/バイク/徒歩, wants たばこ/酒類/アイスクリーム/冷たい飲料.
    - おばさん (40-58歳) — ~8 time-rows spanning 10:00-17:00 (daytime only), longer 買い物所要時間 (240分 = 4 hours!) vs younger archetypes' 60-120分, uses 徒歩/自転車/自動車/バイク, wants 日用品/魚類/肉類/冷凍食品類/野菜類/レトルト類/調味料類 — confirms おばさん (middle-aged women) shop longer and buy household/grocery staples.
    - おじいさん (65-78歳) — 5 time-rows spanning 9:00-15:00, very long 買い物所要時間 (240-360分 = 4-6 hours), wants たばこ/温かい飲料/中華まん/薬類/酒類/菓子類/魚類/野菜類/日用品/下着類/電気製品類 — note distinctly LOW ス(stamina)/素(quickness) values (e.g. ス10,素20) vs younger archetypes' 50-100 range — CONFIRMED: elderly customers move/queue markedly slower than younger ones (a hard numeric stat backing the general "elderly customers anger easily / are slow" flavor claims from PDF1).
    - おばあさん (65-78歳) — 4 time-rows spanning 11:00-16:00 (and a further set 65-78 range at p.141 spanning 15:00-13:00), similarly low ス/素, long shopping duration (360分), wants 日用品/下着類/電気製品類/冷凍食品類/薬品/魚類/野菜類/肉類/調味料類/宅急便申込書.
    - 男子小学生/女子小学生 (7-12歳) — 2 time-rows each (14:00-15:00), short visits (120分), wants 文房具/菓子類, arrival 自転車 only.
    - 男子中学生/女子中学生 (13-15歳) — ~5 time-rows each spanning 7:00-17:00, wants 文房具/冷たい飲料/イベント商品/菓子類/中華まん/アイスクリーム, arrival mix 徒歩/自転車.
    - 男子高校生/女子高校生 (16-18歳) — ~5 time-rows each spanning 16:00-17:00, wants 冷たい飲料/イベント商品/中華まん/薬品/コピー用紙/アイスクリーム/本類/文房具, arrival バイク/自転車/徒歩.
    - 男子幼稚児/女子幼稚児 (4-6歳) — 1 time-row each (13:00, 120分), wants 菓子類, ついでに冷たい飲料/イベント商品, 徒歩 only, ¥500 money — notably these have a 集中力(concentration) value of exactly 0 shown in the row (very impulse-prone, consistent with "children buy whatever" flavor).
    - 子供連れのおじさん (35-38歳) / 子供連れのおばさん (38-41歳) — ~4-6 time-rows spanning 14:00-20:00, long duration (240分), wants 菓子類/電気製品類/日用品/野菜類/肉類/調味料類/冷凍食品類/イベント商品/下着類 — "with-child" parent archetypes distinct from plain おじさん/おばさん (different wants, longer visits).
    - 子抱きのおばさん (30-39歳) — 1 row (15:00, 240分, ¥18,000, 自動車, wants 電気製品類/下着類/日用品/イベント商品) — a "carrying infant" archetype, very high money-on-hand.
    - 車椅子の男性 (30-33歳) — 1 row (14:00, 360分, ¥15,000, 徒歩[wheelchair], wants 本類/冷たい飲料/菓子類/薬品) — CONFIRMED: the game includes a wheelchair-user customer archetype; note its ス(stamina)/距(distance) stat values are extreme outliers (ス=10 or similar low mobility-related figures per the row, サ=100 high service-sensitivity) — accessibility-relevant character type worth flagging for UI/asset reconstruction.
    - 松葉杖の男性 (25-29歳) — 1 row (11:00, 360分, ¥15,000, 徒歩[crutches], wants 本類/冷たい飲料/菓子類/薬品) — a "crutches" customer archetype, same wants as wheelchair archetype.
  - Given the sheer size of this table (~20 archetypes × 5-20 rows each = several hundred data points across pages 135-143), the FULL row-by-row transcription is not reproduced verbatim here for every single row to keep this document manageable; the exact per-row numbers ARE clearly legible in the source scans at p.135-143 and should be re-extracted in a dedicated follow-up pass if exact per-archetype-per-timeslot values are needed for game-balance tuning (e.g. exact stat curves for a specific NPC type). The COLUMN DEFINITIONS, ARCHETYPE ROSTER, and representative sample rows above ARE fully confirmed and transcribed.

- **PDF3 (クイックリファレンス) is EXTREMELY high-value: directly answers nearly every "pay special attention" gap.** Full detail below; key headline confirmations first:
  - **Business hours — exact 5 clock presets + 24h + closure (PDF3 p.2)**: Diagram "① AM10:00~PM6:00（8時間営業） ② AM7:00~PM11:00（16時間営業） ③ AM11:00~AM2:00（16時間営業, exact start hour has minor OCR uncertainty — legible as AM11:00 or possibly AM10:00; duration label reads 16時間営業 either way） ④ PM0:00~AM4:00（16時間営業） ⑤ PM7:00~AM11:00（16時間営業） ⑥ 24時間営業 ⑦ 臨時休業（temporary closure）" — text: "下に示した5種類の定時営業のほか、24時間営業や臨時休業が設定できる。営業時間が長ければ売り上げは伸びるが、経費も多くなることに気をつけよう。" CONFIRMS exactly the "5 clock-diagram presets plus 24h and temporary closure" the task brief asked about, laid out as a circular clock-face selector UI.
  - **Restock cost formula — EXACT (PDF3 p.2)**: "補充費: いわゆる仕入れ価格。仕入単価×数量で設置時にかかる費用。その後は1補充するたびに仕入単価と差し引かれる。" — CONFIRMED_OFFICIAL formula: **補充費 = 仕入単価 × 数量** (restock cost = wholesale unit cost × quantity), charged per restock action.
  - **Equipment cost model — EXACT (PDF3 p.2)**: "設備費: 初期投資が必要な、商品棚やサービス設備、駐車場の備品。設置時のみ必要。もちろん設備が高価なものほど、様々な効果的。" + "維持費: 設備を良好に保つための、冷蔵庫などの電気代として1日に必要な費用。営業時間に応じて、毎日売り上げから差し引かれる。" — CONFIRMED: 設備費 (equipment cost) = one-time upfront investment at placement; 維持費 (upkeep) = separate recurring DAILY cost, and upkeep SCALES WITH BUSINESS HOURS ("営業時間に応じて"), deducted from sales daily. This is the exact "equipment cost model (初期投資+維持費)" the task brief asked about.
  - **Wage/labor-cost formula — EXACT, twice-confirmed (PDF3 p.2 and p.6)**: p.2 "人件費: 社員の給料として必要な経費。表示は日給だが、内容では時給計算がされている。計算方法は時給額×営業時間。営業時間を伸ばすほど人件費がかさむので注意してほしい。" p.6 "賃金は時給計算: 臨時休業で社員を募集すると、賃金が0円/日と表示される。しかし、賃金は無料ではない。賃金は時給×営業時間で表示されるので、営業時間0時間の臨時休業日は、日給表示も0円なのだ。" — CONFIRMED_OFFICIAL EXACT FORMULA: **人件費(displayed daily wage) = 時給額 × 営業時間** (hourly wage × business hours open), directly answering the task brief's "wage formula (時給×営業時間)" gap verbatim.
  - **1 in-game month = 4 in-game days × 8 multiplier (PDF3 p.3)**: "1月=4日間×8 4日間の収支を8倍することで、1月の収支が決定する。実質32日間の営業と考えよう。" — CONFIRMED: the game's financial reporting simulates a "month" as 4 actual in-game days, with totals multiplied ×8 to approximate a real 32-day month equivalent.
  - **Advertising persistence requires ≥3-star store rating (PDF3 p.3)**: "全店舗の人気を上げる効果がある。宣伝費の高いものほど効果も高い。ただし、店舗評価が3つ星以下の場合、宣伝効果は持続しない。" — NEW CONFIRMED nuance not seen in PDF1/2: if a store's 店舗評価 (star rating) is 3 stars or below, an ad's popularity boost does NOT persist (implying it still fires but fades immediately, or does nothing lasting) — ads are only durably effective at 4-5 star stores. Ad list recap (partial, matches earlier table): "1 ダイレクトメール 2 新聞広告 3 飛行船 4 ラジオCM" (テレビCM as a likely 5th entry was off the legible crop — not re-confirmed here but already established from PDF1/PDF2).
  - **Owner-evaluation — all 5 metrics NAMED at last (PDF3 p.3)**: Screenshot "オーナー評価" panel lists exactly: **店舗数(store count) / 累積来客数(cumulative visitor count) / 年商(annual revenue) / 町人口(town population) / 店舗評価(store rating)**, each independently shown as a star rating, PLUS a derived "総合評価" (overall rating) summarizing all 5. THIS RESOLVES the open gap from PDF2 p.98/101 (which had only named 店舗数/人口/年商 as 3 of the 5) — the remaining 2 are **累積来客数** and **店舗評価**. NOTE: this "オーナー評価" 5-metric system is DISTINCT from the earlier per-STORE 4-metric panel seen in PDF1 p.38-39 (人気/治安/サービス/[4th]) — the owner-level metrics are company-wide roll-ups checked yearly, while the per-store metrics are checked monthly for that individual store's star rating.
  - **Weather system — monthly percentage table (PDF3 p.3)** — DIRECT HIT for the weather-percentage gap, though exact digit legibility is imperfect at this resolution (flagged): table "天候のパーセンテージ設定" with legend "荒天=大雨・雨天・台風・大雪" (荒天 as printed is a combined/umbrella category name covering heavy rain/rain/typhoon/heavy snow) and columns 月/晴天/曇り/雨/雨天/荒天/大雪 (exact column set has some OCR ambiguity from the small print). Rows read (medium confidence, recommend a dedicated high-res re-crop of this exact table before treating any single digit as final):
    | 月 | (col2) | (col3) | (col4) | (col5) |
    |---|---|---|---|---|
    | 1月 | 30 | 30 | 20 | 15 | 5 |
    | 2月 | 30 | 30 | 10 | 20 | 10 |
    | 3月 | 30 | 30 | 20 | 15 | 5 |
    | 4月 | 30 | 40 | 0 | 20 | 10 |
    | 5月 | 40 | 30 | 0 | 20 | 10 |
    | 6月 | 30 | ~1 | 0 | 30 | 50 |
    | 7月 | 20 | 20 | 10 | 20 | 10 |
    | 8月 | 30 | 20 | 10 | 20 | 20 |
    | 9月 | 30 | 20 | 10 | 20 | 20 |
    | 10月 | 40 | 30 | 0 | 10 | 15 |
    | 11月 | 30 | 30 | 0 | 10 | 15 |
    | 12月 | 30 | 30 | 20 | 15 | 5 |
    - This table's row-sums are inconsistent (some exceed or fall short of 100), which combined with the tiny source print means SEVERAL individual cell values above are almost certainly misread — treat this table as "confirmed to exist, general shape captured, exact digits NOT reliably confirmed" and flag for a dedicated re-extraction pass at higher zoom before use in `vertical_slice.json`. What IS reliably confirmed: (a) the table is keyed by calendar month (12 rows), (b) June (6月, 梅雨/rainy-season month) has a visibly much higher bad-weather value than other months, consistent with real-world tsuyu, (c) the weather categories named in the legend are 晴天(sunny)/曇り(cloudy)/雨/雨天(rain)/台風(typhoon)/大雪(heavy snow)/荒天(severe-weather umbrella term).
  - **Weather-effect-on-visits mechanic — EXACT (PDF3 p.3)**: "悪天候の場合、買い物の重要度が低い顧客は来店しなくなる。" — CONFIRMED_OFFICIAL mechanic: in bad weather, customers with LOW 買い物重要度 (shopping-importance stat, part of the 顧客データ schema from PDF2 p.134) stop visiting; high-importance-purchase customers still come regardless of weather. This is a precise mechanical rule (a customer-stat threshold gate), not just flavor.
  - **Festival event — EXACT multiplier, resolves the お祭り/festival gap (PDF3 p.3)**: "お祭り: 毎年8月に開催。通常より1.5倍程度の売り上げが見込める。" — CONFIRMED_OFFICIAL EXACT NUMBER: annual August 祭り (festival) event gives approximately **1.5× normal sales**. (This is the same real-world calendar slot as PDF1's 花火大会/fireworks festival — likely the same in-game event described with more mechanical precision here; the two source books may simply be using different names — 花火大会 vs お祭り — for what is mechanically the same August event. Flag for a decision doc note reconciling naming.)
  - **Aisle/passage width — EXACT DEFINITIONS, fully resolves the 1-masu/half-masu gap (PDF3 p.5)**: "① 1マス通路: 客や店員が2人並んで通れる幅。すれ違えるので混雑しにくい。" / "② 1/2マス通路: 客や店員1人が通れる幅。すれ違うことができず、混雑しやすい。" — CONFIRMED_OFFICIAL EXACT RULE: a full 1-masu (1-square) aisle fits 2 people walking abreast and allows passing, so it congests less; a 1/2-masu (half-square) aisle fits only 1 person, does NOT allow passing, and congests more easily. This is the definitive primary-source answer to the task brief's aisle-width research gap.
  - **Shelf pickup-clearance — REFINES PDF1's "1ブロック" claim to exactly 1/2マス (PDF3 p.5)**: "商品棚は1/2マスアキでも大丈夫: 棚やワゴンは取り出せる方向を1/2マス開けておけば、そこから利用可能。店員による商品の補充もできる。" — CORRECTS/REFINES the earlier PDF1 p.65 reading of "最低1ブロックのあき" (minimum 1 block clearance) — the precise figure per this Quick Reference book is **1/2マス (half a square)** of open clearance on the pick-up side, not a full block. Treat PDF3's number as the more authoritative one (it's from the dedicated mechanics-reference book, with an explicit fractional unit matching the aisle-width system above) and flag the PDF1 wording as either a looser approximation or referring to a different situation (fully blocked by another fixture vs. merely tight clearance).
  - **Shelf/wagon access-direction — extra classification detail (PDF3 p.5)**: "ワゴン: 4方向から商品を取り出せる。コピーや保険商品ケースもワゴン扱い。" / "棚: 前方からしか商品が取り出せない。自動販売機も棚に分類される。" — ADDS to PDF1/PDF2: コピー機 and 保険商品ケース (insurance-product case — a fixture type not otherwise seen in the PDF2 設備データ table, possibly named differently there, e.g. as part of 宅急便申込書 handling) are classified as ワゴン-type (4-direction access) for game-logic purposes, while 自動販売機 (vending machines) are classified as 棚-type (1-direction access) despite their distinct fixture category elsewhere.
  - **注目度 (attention) reach confirmed for back-of-store placement (PDF3 p.5)**: "注目度の高い棚は客の注意を引く。店舗の奥に配置しても、客が気付かずに帰ることはない。" — confirms high-注目度 fixtures are noticed by customers regardless of in-store position, including the very back.
  - **Customer pathing — "shortest route" rule, EXACT, resolves the pathing gap (PDF3 p.5)**: "買い物客は最短ルートを選ぶ: 左図の店内で、冷たい飲料を買いたい顧客は最短ルートをまず歩く。最短ルートが進めなかった場合にのみ、遠回りをする。" — CONFIRMED_OFFICIAL EXACT MECHANIC, matching the task brief's named hypothesis almost verbatim: customers pathfind via the SHORTEST route to their wanted item, and only take a detour/longer route if that shortest route is blocked/impassable (e.g. by a fixture placement or crowding). This directly resolves the "customer pathing rule (最短ルートを選ぶ) and any congestion/detour rules" gap.
  - **Service-item サービス度 exact point values (PDF3 p.5)**: table "サービス設備の効果と配置": **観葉植物(houseplant) = サービス+2 / ベンチ(bench) = サービス+4 / 噴水(fountain) = サービス+30**. Text: "店舗のサービス値を増やす設備。サービス値が高い店舗は、サービスを重視する客が来店しやすい。密閉空間に配置しても効果は出る。" — CONFIRMED_OFFICIAL exact per-item サービス度 point values — a major, precise number set the task brief's gap list didn't even explicitly ask for but is highly valuable for reconstructing the サービス mechanic. Fountain is a massive outlier at +30 vs plants/benches' single-digit boosts, matching its far higher price (¥5,000) and upkeep (¥2,400/day) from PDF2's fixture table.
  - **Parking capacity — cross-confirms PDF2 exactly (PDF3 p.5)**: "① タワー型駐車場 20台収容 ② 2階建駐車場 4台収容 ③ 駐車場 2台収容" — EXACTLY MATCHES PDF2 p.118-119's fixture-data capacities (20/4/2 cars respectively) — strong cross-source confirmation. Text: "自動車で移動する設定の顧客が利用できる設備。駐車場がなかったり、自動車利用の客より収容数が少なかった場合には、クラクションの効果音がでる。" (matches PDF1's "ビッビッ" claxon cue).
  - **Default/baseline profit margin — EXACT (PDF3 p.5)**: Screenshot "商品価格を決定して下さい 全商品平均利益率 20% 全体に設定〈20%OFF〉個別に設定" with annotation: "販売価格を決定した際の、純利益の割合。通常は全体で40%に設定されており、これが定価と考えられる。" — CONFIRMED_OFFICIAL: the game's DEFAULT/baseline store-wide profit ratio is **40%**, and this 40% figure IS effectively "定価" (list/standard price) — cross-checks well against PDF2's per-category table where the modal/most-common 利益率 value across categories is exactly 40%.
  - **人気 (popularity) defined precisely — awareness, not just "liking" (PDF3 p.5)**: "住民の認知度。いくら安売りしていても、店舗の存在に気付いていない住民は買物客とはならない。" — CONFIRMED: 人気 fundamentally represents town-resident AWARENESS/recognition of the store's existence, not simply "how much they like it" — a resident who doesn't know the store exists cannot become a customer no matter how good prices/service are. This reframes 人気's role relative to price/service appeal.
  - **Gender-based staff stat bias — NEWLY CONFIRMED_OFFICIAL, contradicts PDF1's flavor-only framing (PDF3 p.6)**: "性別: これも気にする必要はない。比較的に、男性は体力に優れ、女性は社交性が優れている、履歴書評価に反映される。" — CONFIRMED: gender DOES bias starting stat leanings — males trend higher 体力(stamina), females trend higher 社交性(sociability) — reflected in the résumé/hiring-screen evaluation. This UPGRADES the earlier PDF1 p.41 anecdote (which this document flagged as "flavor/opinion, not a real mechanic") to an actual CONFIRMED_OFFICIAL mechanic, now stated plainly in the dedicated reference book. Recommend updating that earlier flag.
  - **Staff never age-out (PDF3 p.6)**: "年齢による傾向は履歴書評価に加味されているので、改めて気にする必要はない。何歳だろうと社員は[死ねない/老いない — exact character uncertain from scan, contextually likely '衰えない' or '辞めない', meaning staff do not decline/quit purely from old age]。" — transcribed with an explicit legibility caveat on the exact final verb; the surrounding context (leads directly into the "80歳でスーパー社員に" section) strongly implies the intended meaning is that aging is not a liability and can even become a huge asset.
  - **"80歳でスーパー社員に" — THE EXACT MECHANIC, fully resolves the task brief's named gap (PDF3 p.6)**: Section header "80歳でスーパー社員に" with example screenshot: 高橋大介, now aged **94歳男**, showing ALL SIX visible stat bars (体力/教育/レジ/補充/警備/清掃) maxed at **100/100/100/100/100/100**. Body text (transcribed at best legibility, some characters uncertain due to scan quality): "キャラクターの年齢が80歳を超えると、一定の確率で全パラメータが100のスーパー社員になる。最短で[??]年目にこの現象が起こる。スーパー社員が店舗にいると、来客も増えてくることもあるので、確認しよう。" — CONFIRMED_OFFICIAL MECHANIC: once a staff member's age exceeds **80**, there is a RANDOM CHANCE (rate not given as an exact percentage on this page) each check that they instantly become a "Super Employee" (スーパー社員) with ALL parameters maxed at 100. This is a rare, luck-based end-game staff mechanic. Recommend flagging that the exact probability-per-check number was NOT found in any of the 4 PDFs — only the age-80 threshold and the "reaches 100 across the board" outcome are confirmed; the odds themselves remain an open gap.
  - **Staff parameter definitions — REFINED wording vs PDF1 (PDF3 p.7)**: "体力=履歴書評価と同様。ただし、行動する度、体力で低下。休憩で回復する。" (stamina drops with EVERY action taken, recovers on break — more precise than PDF1's vaguer framing) / "教育=店員の能力アップに反映。" / "レジ=レジ打ちのスピード。表上特に重要。" / "補充=補充のスピード。商品を買えなかった客が発生する。" (low 補充 → customers who wanted an item but couldn't buy it, i.e. explicit lost-sale linkage) / "警備=強盗や火災の発生率に影響。被害を抑えるためにも重視すべき。" (CONFIRMS 警備 affects BOTH robbery AND fire occurrence rate — PDF1 only explicitly tied 警備 to shoplifting/robbery, not fire; this is a refinement: fire risk is ALSO gated by 警備, not purely by "モラルの低い客" as PDF1 implied) / "清掃=店内の清掃能力。清掃が間に合わないと店舗評価が下がる。" / "接客=店舗のサービスに影響。サービスのいい店を好む客も多い。"
  - **Manager (店長) education bonus — refined (PDF3 p.7)**: "店長の能力: 特に重要なのは教育。この値の高い店長のいる店は、店員2人の能力が上がりやすい。また、教育が高いほど、アドバイスも正確。" — confirms exactly "2人" (the other 2 staff, matching the 3-total-per-store cap) benefit from a high-教育 manager, and that the manager's 教育 stat ALSO affects the accuracy of an in-game "advice" feature ("店舗評価を上げるためのアドバイス...教育値の高い店長は内容が的確").
  - **Store-level facility/security radius — cross-confirms PDF1's 交番/消防署 numbers with a generalized rule (PDF3 p.10)**: "セキュリティ施設の効果範囲: 右の写真で示した店舗周囲16×16エリア内にセキュリティ施設がある場合、店舗の警備値にプラス効果がある。" + per-facility: "消防署: 敷地面積2×3エリア。1エリアごとに警備値+5の効果。最大で+30。" "交番: 敷地面積2×2エリア。1エリアごとに警備値+10の効果。最大で+40。" — MAJOR REFINEMENT: this gives an exact PER-AREA scaling formula, not just a flat bonus — 交番 gives **+10 security per adjacent area, capped at +40 total** (i.e. up to 4 areas' worth); 消防署 gives **+5 security per adjacent area, capped at +30 total** (i.e. up to 6 areas' worth) — and the effect range is a **16×16-area zone centered on the store** (much larger than PDF1's "半径7エリア" framing — reconcile as: PDF1's "7エリア" may have been a rougher/radius description of roughly the same 16×16 square zone, or the two sources partially disagree on exact range — flag as a minor cross-source figure to double check, though the flat +40/+30 MAX totals themselves exactly match PDF1's stated flat bonuses of +40/+30).
  - **Town population thresholds → town rank (PDF3 p.10)**: "町の規模は人口で決まる: 人口5000人以上=市役所, 8000人以上=区役所, 20000人以上=都庁" — CONFIRMED_OFFICIAL EXACT THRESHOLDS: population ≥5,000 → 市役所 (city hall/municipal office) appears; ≥8,000 → 区役所 (ward office) appears; ≥20,000 → 都庁 (metropolitan government building, the Beginner-map win condition) appears. This is a precise numeric ladder resolving how the "都庁を誘致する" win condition actually triggers (matches PDF2 p.86's "人口を増やせば都庁は自然と建設される" but now with the exact population number: **20,000**).
  - **Station (駅) population thresholds — refines PDF1's "5000人" note with an exact 2-tier system (PDF3 p.10)**: "人口が5000人を超えると、駅ができる。駅の買い物客は駅沿いに住む2000人ほどになるので、客数が飛躍的に伸びる。" + separately in the 誘致 facility list "駅: 人口5000人を越えると、線路沿いで規模大きくなる。規模別に2種類が設定されている。複数誘致されることもある。" — CONFIRMED_OFFICIAL: station appears once town population exceeds **5,000**; the station itself is worth ~**2,000** shopping-population-equivalent extra customers; stations come in exactly 2 size tiers and multiple stations CAN appear on one map.
  - **Non-security 誘致 facility list, more entries than PDF1's table (PDF3 p.10)**: "学校・セキュリティ以外の誘致物件" table with サイズ/客数(shopping-population) columns: 遊園地(amusement park) 7×7, 客数750; 動物園(zoo) 3×3(?), 客数500; 公園(park) 2×2, 客数30; 会社(company) 3×3, 客数90; 体育館(gym) 3×3(?), 客数30; 運動場(athletic field) 5×4, 客数100; プール(pool) 3×2, 客数40; 住宅(residential) [size not fully legible], 客数[value]; 役所(government office) [entry, likely automatic/non-誘致-able per the "特殊な施設" note below]. — ADDS a "買物人口"(shopping-population) NUMBER per facility type that PDF1's p.45 table did NOT include (PDF1 only gave サイズ/期間/援助額, no population-draw number) — this is new, valuable numeric data for simulating exactly how much customer draw each attracted building contributes.
  - **"Special facilities" — 駅/役所 are NOT normal 誘致 targets (PDF3 p.10)**: "特殊な施設: 駅と役所は一定の条件が成立すると建設される。規模別に7種類ある。役所は3種類、駅は2種類が設定されている。複数設置されることもある。" — CONFIRMED: unlike the explicit 誘致 facility list (PDF1 p.45 / PDF2), 駅 (station) and 役所-tier buildings (市役所/区役所/都庁, 3 variants) appear AUTOMATICALLY once their population thresholds are met — they are NOT purchasable/directable via the normal 誘致 UI at all. This resolves the earlier open question flagged at PDF2 p.86 about how 都庁 gets built.
  - **Map clear conditions — VERBATIM, all 3 + the secret 4th's unlock (PDF3 p.11)**: "初級マップは人口を増やす: クリア条件 都庁を誘致する — 人口を増やせば都庁が建設される。よって、誘致というよりも、マップ内の人口をいかにして増やすかが課題だ。" / "中級マップはライバルと勝負: クリア条件 10店舗経営する — ひとつのマップにはライバル店を含めて10店舗までしか建設できない。よって、いかにライバルを撤退させるかが課題だ。" — NEW EXACT NUMBER: the 10-store cap on the Intermediate map includes RIVAL stores in the count (i.e. it's a shared 10-store slot limit for the whole map, not 10 for the player alone) — this refines PDF2's "10店舗建設する" wording significantly. / "上級マップはバランスがカギ: クリア条件 オーナー評価を★★★★★にする — 毎年1月1日に表示される5種類のオーナー評価を、すべて5つ星にできればクリア条件が満たされる。特に年商が課題だ。" MAP詳細 stat callouts for 上級: 店舗数10店舗必要, 累積来客数20万人程度, 年商3000万円程度, 町人口30000人程度, 店舗評価全店5つ星が最高評価. — CONFIRMED EXACT NUMERIC TARGETS for the Advanced map's 5-star-everything win condition: **10 stores, ~200,000 cumulative visitors, ~¥30,000,000 annual revenue (年商), ~30,000 town population, all stores at 5-star rating**.
  - **Secret/"極上" 4th map unlock condition — EXACT (PDF3 p.11)**: "極上マップの出現条件: 初級、中級、上級の各マップをクリアした状態においては、極上マップがプレイ可能になる。スタート当初からライバル店舗がすでに5店舗もあり、いかにしてライバルを牽制するかが問題だ。" — CONFIRMED: the secret map found in PDF2 p.104 is named **極上マップ** ("Superb/Exquisite" map), unlocked after clearing all 3 named maps, and starts with **5 rival stores already established** from turn one — a much harder starting position than any of the 3 base maps.
  - **Event trigger table — EXACT conditions for 6 special events, MAJOR FIND (PDF3 p.12)**: table "イベントガイド" with columns イベント/発生条件/備考:
    | イベント | 発生条件 | 備考 |
    |---|---|---|
    | 寄付 (donation) | 手持ち資金が15億円以上で月が変わる。 | 10億円以上の資金が強制的に寄付金として差し引かれる。各店舗の評価が上がる。 |
    | 万引き (shoplifting) | 顧客のマナーが店舗の警備値よりも悪い場合。 | マナーの悪い客が購入しようとした商品が、店舗の売り上げからマイナスされる。 |
    | 火災／強盗 (fire/robbery) | 店舗周囲16×16エリアにセキュリティ施設がない場合。 | 火災は消防署、強盗は交番が周囲に必要。警備値より人気が高いと店舗は火災や強盗の発生率が高い。 |
    | 業界誌掲載 (trade-magazine feature) | 人口1万人以上、マップ内に5店舗以上ある場合。 | 店長のパラメータ値が若干だが上昇する。 |
    | コンビニコンテスト (convenience-store contest) | 人口1万人以上、マップ内に5店舗以上ある場合。 | 店舗数(ライバル店を含む)×1000万円が賞金。ライバル店が選ばれることもある。 |
    | アイドル (idol) | 来店客数が1万人以上で、以降1万人ごとに。 | 警備値が低い店舗は火災や強盗の発生に注意。全店の人気が100になる。 |
    - CONFIRMED EXACT trigger conditions and mechanics for ALL of these: 寄付 (forced donation) triggers when cash-on-hand ≥¥1,500,000,000 (15億円) at month-end, forcibly deducting ≥¥1,000,000,000 (10億円) but RAISING all-store evaluation as compensation; 万引き triggers whenever a given customer's individual マナー(manners) stat exceeds that store's 警備(security) stat (a direct per-customer-vs-store stat comparison, not a flat probability!); 火災/強盗 triggers specifically from the ABSENCE of a security facility in the 16×16 zone (matching p.10's radius rule) — text adds "警備値より人気が高いと店舗は火災や強盗の発生率が高い" (CONFIRMED: if 人気 exceeds 警備, fire/robbery risk increases — a relative-stat comparison, not just an absolute low-警備 threshold); 業界誌掲載 and コンビニコンテスト share the SAME trigger condition (town population ≥10,000 AND ≥5 stores on the map) — 業界誌掲載 gives a small manager-stat boost, コンビニコンテスト awards prize money = (total store count including rivals) × ¥10,000,000; アイドル triggers at 10,000 cumulative visitors and every additional 10,000 thereafter (cross-confirms PDF2 p.89 exactly), setting 人気=100 for the triggered store.
  - **Layout save-slot limit (PDF3 p.12)**: "店舗のタイプひとつに対し、1種類の内装レイアウトが保存できる。試行錯誤が必要であるレイアウト作業だけに、儲かる店舗の内装は必ず保存しておくこと。" — CONFIRMED: exactly 1 saved interior layout per store TYPE (not per individual store) — i.e. layouts are saved/reused at the "store size/orientation" template level.
  - **Game-over / scenario-clear conditions (PDF3 p.12)**: "シナリオクリア: 各マップのクリア条件を満たすとエンディングが流れる。" / "ゲームオーバー: 破産または、クリア条件を満たせず100年経過するとゲームオーバー。" — CONFIRMED_OFFICIAL EXACT TIME LIMIT: the game ends in a loss if either the player goes bankrupt OR **100 in-game years** elapse without meeting the map's clear condition.

- **顧客 section — facility-based customer population data (PDF3 p.8-9)**: "各種学校にいる顧客" — school-type facilities (幼稚園/小学校/中学校/高校/大学) each have age-appropriate customers; example 買物人口 figures shown: 幼稚園 大字 749人(sic — likely a place-name example, not literally the facility's population), 高校 345人. "オフィスの顧客" — "規模別に5種類の会社が設定されていて、それぞれ買い物人口が異なる。" — sample: 会社員 example 所持金¥2,500 wants インスタント類; OL example 所持金¥4,200 wants 日用品; text distinguishes 会社員/OL as separate archetypes with different typical wants. "体育施設の顧客" — 体育館/プール/運動場 mainly draw students; example 運動場 買物人口 100人. "パチンコ屋の顧客" — "酒、たばこなどが売れる。比較的若い男性が多い。" example 買物人口 50人. "住宅地" — "規模別に7種類ある。客単価の高い中高年や老人の客層がいる。" examples: 住宅(大) 買物人口 24人 with おじさん/おばさん/おばあさん customers each carrying 所持金¥10,000. "家族連れが多い施設" — 子連れの母親が主な客層。子供のためにお菓子などを購入する。弁当、パン類も購入。ファミリーレストラン example 買物人口 1176人. "特殊な施設" — 役所 (population≥10,000 condition, appears automatically, 3 size tiers) and 駅 (population≥5,000, 2 size tiers) — see Notable findings for the exact thresholds; text here adds "複数配置されることもある" (multiple can appear).
- **顧客の購入品 — アンケート bar-chart data (PDF3 p.9)**: Explains アンケート mechanic precisely: "顧客の需要がダイレクトに分かる。毎月更新されるので、4日に確認するのがベスト。アンケートを参考に、品揃えやレイアウトを変更するべき。" — CONFIRMED: survey data refreshes monthly and is best checked specifically on day 4 of the (4-day) in-game month. Legend: "①買った商品=購入した商品と購入人数。上位ランクの商品はその店の主力商品。主力商品を積極的に配置するかで売り上げも大きく変化。" "②欲しかった商品=顧客の希望商品と、買えなかった人数。記録している商品が希望商品になる場合、補充が間に合っていない。" Bar chart shows two series — "ついでに買う顧客"(incidental buyers) vs "希望で買う顧客"(purchase-goal buyers) — across ~20 product categories (中華まん/イベント商品/下着類/薬品/宅急便申込書/コピー用紙/日用品/冷凍食品類/調味料類/レトルト類/肉類/野菜類/電気製品類/文房具/アイスクリーム/たばこ/本類/インスタント類/パン類/弁当類/酒類/温かい飲料/冷たい飲料), confirming "the longer bar = more customers who want it" as the reading convention ("グラフの長い商品ほど、多くの客が購入する").

### PDF3 per-page log
- p.1: cover/title page ("『ザ・コンビニ ～あの町を独占せよ～』クイックリファレンス").
- p.2-3 「時間」: full detail in Notable findings (5 business-hour presets, restock/equipment/wage formulas, 1-month=4-days×8, ad 3-star persistence rule, owner-evaluation 5 metrics, weather % table, weather-visit-suppression rule, festival 1.5× multiplier, annual calendar weekday/holiday pattern — the latter table's exact per-day values were legible only at a coarse level: most months show a repeating 平日/休日/平日/平日-or-休日 4-day pattern; exact cell-by-cell values not re-verified pixel-precisely here).
- p.4-5 「店舗」: full detail in Notable findings (visitor-count drivers incl. exact station population thresholds, 買物人口 per-facility mechanic, aisle-width exact definitions, shelf/wagon clearance and access-direction rules, shortest-route customer pathing, exact サービス度 point values per service item, parking capacities, 40%-default profit margin, 人気-as-awareness definition).
- p.6-7 「社員」: full detail in Notable findings (wage formula restated, gender stat-bias CONFIRMED_OFFICIAL, 80-year-old Super Employee mechanic, refined 7-stat definitions incl. 警備 now tied to BOTH fire and robbery, manager 教育 bonus applies to exactly the other 2 staff, store-sale/rival-staff-growth notes).
- p.8-9 「顧客」: full detail in Notable findings (facility-based customer population/archetype notes, アンケート monthly-refresh-on-day-4 mechanic, purchase-vs-incidental bar chart).
- p.10-11 「町」: full detail in Notable findings (16×16 security radius with per-area scaling formula for 交番/消防署, population thresholds for 市役所/区役所/都庁, station thresholds, non-security 誘致 facility population-draw table, 駅/役所 as auto-built "special facilities" not normal 誘致 targets, all 3 base maps' exact clear conditions and stat targets, secret 極上 map's unlock condition and 5-rival starting handicap). Additional untranscribed detail: "町人口" box — "地価の上昇に伴って、マップ内に大きな建物が建つ。建設された建物の買い物人口がプラスされる。逆に建物が取り壊されると、その建物の人口がマイナスされる。" (population rises/falls exactly with buildings being constructed/demolished in the town, tied to land-value increases enabling bigger buildings). "地価が上がれば町が発展する" — "店舗の周囲は徐々に地価が上がる。様々な建物は、地価が高いほど建ちやすい。発展させたい地域に新規開店すべきだ。"
- p.12 「補足」: full detail in Notable findings (event trigger table for 寄付/万引き/火災・強盗/業界誌掲載/コンビニコンテスト/アイドル, layout-save-per-store-type limit, 100-year/bankruptcy game-over conditions). Additional: "レイアウト保存" sidebar mentions "店内の客がまったく動かなくなってしまったり、店から客が出られなくなることがまれにある。このような場合はカーソルで客を指定し、つまみ出してしまおう" (a rare bug/edge-case where a customer gets permanently stuck — same つまみ出す ejection fix as established mechanic).
- p.13: back-cover/ad page for 「ザ・コンビニ パーソナルデザインBOOK」(a separate companion sticker/layout-design book by Human/CB's Project) — NOT part of the Quick Reference's own strategy content; establishes that PDF3's remaining pages (13-23) are this OTHER book's front matter/table of contents, not more コンビニ mechanics content directly. TOC shown: クイックリファレンス(1-) / パーソナルデザインBOOK(23-) / 内装レイアウトKitの使いかた(16) / パーソナルレイアウトデザイン(18) / 攻略&データブック(65: オールテクニックガイド 66, データリスト 84).
- p.14-15 (cover art / blue divider pages for the パーソナルデザインBOOK section) — decorative, no mechanical data; lists sticker-icon fixture graphics for a cut-and-paste layout-design activity.
- p.16-17 「内装レイアウトKitの使いかた」— explains a physical activity (peel stickers, arrange on a grid, photocopy at a real convenience store, mail in submissions to a magazine contest) — NOT game-mechanic content; flavor/merchandise instructions for the physical book.
- p.18-19 「パーソナルコンビニデザイン SPECIAL」/ TACTICS — example fan/reader-submitted store layouts ("塩田ストア本店"/"菅ストア本店") with flavor commentary on business-hours/pricing strategy choices (e.g. running PM7:00~AM11:00 hours to target late-night commuters, or a 10%-price-increase high-service "haisо" boutique-style strategy) — these are READER-SUBMITTED / EXAMPLE content from the companion design book, useful only as illustrative flavor, not new CONFIRMED_OFFICIAL mechanics beyond what's already captured (e.g. reconfirms 営業方針 UI fields 営業時間/社員ベースアップ率/賃金交渉に応じる).
- p.20-21 「Design Showcase」— exact fixture inventories for the same 2 reader stores, listing 商品名/商品棚(サイズ)/維持費/収納力/注目度 per fixture placed, and totals "合計36スペース"(観葉植物8/ベンチ5/駐車場収容力40) vs "合計32スペース"(観葉植物6/ベンチ7/駐車場収容力60) — these are INSTANCE data (specific example builds) using the same base fixture stats already captured from PDF2 p.110-119, not new base-game numbers.
- p.22-23 「Extension Plan」/「Designer's Comment」— generic growth-strategy checklists (both patterns reconfirm: attract 交番/消防署 early, remodel when funds allow, expand store count, eventually 24-hour operation, discount when 人気 exceeds security-related thresholds by "1~5%引き差をつける") and closing designer-bio blurbs (塩田信之, 菅数浩 — the book's two credited designers; one mentions a combined SS+PS playtesting total of "1000時間" during development, a trivia note, not a mechanic).
- p.24-47 「パーソナルコンビニデザイン 3 to 74」— this is the companion book's own large joke/flavor store-concept catalog (a 74-entry catalog per its title, of which this scan shows entries roughly 1-40ish, spanning print pages 24-47): humorous or thematic "what if a convenience store existed here" layouts for settings such as 中学校の近く, 団地内, 大病院のそば, 小学校の近く, 丸の内のようなオフィス街, 東京郊外の国道沿い, 私鉄沿線駅前銀座, 上野のようなターミナル駅周辺, ヤングファミリーの多い新興住宅街, 東京1時間圏内のベッドタウン, 兜町のような証券街, 砂漠の真ん中, お台場のような埋め立て地, 横須賀のような米軍基地近辺, 横浜・神戸のようなおしゃれな街, 軽井沢のような避暑地, ソーホーのような芸術家街, プールの近く, 荒川のような河川敷, 公営運動場の近く, 有楽町のような大型店の多い街, 成城・田園調布のような高級住宅地, 中華街そば, 新宿歌舞伎町のような繁華街, 札幌ラーメン横丁内, 大阪ミナミのような食い倒れ街, 屋台村内, 箱根のような観光地, 北欧のような白夜の国, 草津のような温泉街, 京都のような古都, 孤島, 富士の樹海内, ジャングルの中, 南極, and more (TOC on p.24-25 lists the FULL 74-entry index, including further entries beyond this scan's page range: 墓地内, 永田町のような政治都市, 銀座のような高級官み屋街, 幼稚園の近く, 過疎化した村, 犯罪多発地域, 核シェルター内部, 食料不足の国, 大学近くの学生街, 高校(共学)の近く, スキー場ゲレンデ中腹, 渋谷・原宿のようなティーンの街, 水族館のそば, 遊園地の近く, 高校(女子校)の近く, 幕張のようなイベント会場そば, 高速道路のインターチェンジ, 秋葉原のような電気街, 成田のような国際空港内, 常夏の熱帯地方, エベレストの頂上, 巨大宇宙船内, 海底都市, 北陸地方の牧場地帯, 動物園の近く, 野菜市場の近く, いたこの慣わし街, 北陸地方の雪国, 漁村, 香港のような人口過密地域, 高校(男子校)の近く, 競馬場の近く, 飯田橋CB's近辺). Each entry is a stylized joke/example layout with a "ストアコンセプト" label and a "POINT ITEM" (2 featured product categories) plus flavor commentary from cartoon mascot characters — these are explicitly NON-serious, humor-driven "what would a conbini look like here" content (the book's own framing: "こんなコンビニ建ててみたい!? 変なお店もいっぱい"). NO new CONFIRMED_OFFICIAL numeric mechanics were found in this run of entries beyond what's already captured elsewhere in this document; treat this whole 74-entry catalog as low-priority flavor/joke reference material for later UI-asset or store-naming inspiration only, not as game-mechanic evidence. (This catalog continues beyond page 47, which is where this particular PDF file's scan ends at its stated 23-page limit; PDF4, per its file description, appears to pick up this SAME catalog's remaining entries starting around print page 48.)

- **PDF4's back half is a THIRD companion book, 「攻略&データブック」(オールテクニックガイド + データリスト + マップ攻略), and is EXTREMELY high value — it contains EXACT FORMULAS for nearly every remaining game-mechanic gap (PDF4 p.66-83).** This is a strategy-tips book with numbered "POINT" checklists per topic, but critically ALSO embeds several precise formula boxes not found in any of the other 3 sources. Full detail:
  - **Store-level SERVICE VALUE — EXACT FORMULA (PDF4 p.69)**: "店舗のサービス値 = 社員3人のサービス値平均 + サービス設備の付加効果" — CONFIRMED_OFFICIAL: a store's overall サービス(service) stat = the AVERAGE of its 3 staff members' individual 接客/サービス stat, PLUS the flat bonus from installed service fixtures (観葉植物+2/ベンチ+4/噴水+30, per PDF3 p.5, re-confirmed verbatim again on this page: "観葉植物、ベンチ、噴水は店舗のサービス値を上げるための設備。それぞれ+2、+4、+30のサービス付加効果を持っている。").
  - **Store-level SECURITY VALUE — EXACT FORMULA (PDF4 p.74)**: "店舗のセキュリティ値 = 社員のセキュリティ値合計×店舗規模別基準値 + セキュリティ施設の効果" with **店舗規模別基準値: 10×10の店舗=1.5、12×12の店舗=1.65、14×14の店舗=1.8** — CONFIRMED_OFFICIAL exact formula AND exact per-size multipliers (note: uses a 3rd size reference "14×14" not seen named elsewhere — likely referring to the "大" tier's actual buildable footprint, tying back to the PDF1-vs-PDF2 large-store-size discrepancy flagged earlier; this 14×14 figure is closer to PDF2's implied ~13×14 large-store footprint than to PDF1's stated 16×16, which is USEFUL EVIDENCE toward resolving that earlier discrepancy in favor of PDF2's numbers). Security-facility contribution restated exactly: 交番=+10/area within 16×16 zone (max +40), 消防署=+5/area within 16×16 zone (max +30).
  - **Store-level CLEANLINESS VALUE — EXACT FORMULA (PDF4 p.76)**: "店舗の清掃値 = 社員の清掃値合計×店舗規模別基準値（店舗規模別基準値はP74と同様）" — CONFIRMED_OFFICIAL: uses the IDENTICAL size-tier multiplier set (1.5/1.65/1.8) as the security formula. Together with the サービス formula above, this establishes a consistent pattern: 清掃 and セキュリティ scale with (staff stat SUM × size multiplier) + facility bonus, while サービス scales with (staff stat AVERAGE) + facility bonus — a meaningful asymmetry worth preserving exactly in any reconstruction (サービス is NOT sum×multiplier, it's a plain average).
  - **STORE-RANK (star rating) — internal 0-100 value bands, EXACT (PDF4 p.75)**: "ランク表示は5段階の星印で表示される。しかし、内部では最大100までの数値で内部評価値として計算されている。星5つの状態でも、内部評価値を100にしなくてはならないわけではない。" Table "ランク表示と内部評価値": **★★★★★=100 / ★★★★☆=80~99 / ★★★☆☆=60~79 / ★★☆☆☆=40~59 / ★☆☆☆☆=20~39 / ☆☆☆☆☆(no stars)=0~19**. This is the master key for converting the game's underlying 0-100 store-evaluation number into the 5-star UI display, CONFIRMED_OFFICIAL and precise.
  - **STORE-RANK increase/decrease conditions — REFINED, higher-confidence version of the PDF1 p.38-39 table, PLUS exact random-event probabilities (PDF4 p.75)**: "◆ランク評価の増減要因" — increase rule: "下記の条件を3つ以上成立させると+5" across 5 tracked stats (価格/サービス/セキュリティ/清掃/売上) per current-rank row (thresholds scale down as rank drops, mirroring PDF1's shape but with 価格 expressed as a NEGATIVE percentage — i.e. price must be discounted below a threshold, e.g. ★5 requires "価格-30%以下"); decrease rule: "下記の条件1つごとに-1" (price condition inverted to "+1%以上" i.e. priced ABOVE baseline at all triggers a decrease contribution, with the other 4 stat thresholds scaling down by rank exactly as PDF1's table showed). CRITICAL NEW DATA not in PDF1: **exact random-event probabilities appended below the table**: "上記の条件以外に、お客に怒られる確率は1/6の確率で-1、万引き＝-1、寄付イベント＝+2" — CONFIRMED_OFFICIAL EXACT NUMBERS: an angered-customer incident has only a **1/6 chance** of costing -1 rank point (not a guaranteed hit every time!); a shoplifting incident is a flat **-1**; a 寄付(forced-donation) event is a flat **+2**. (Given this table's numeric columns are a close match to PDF1 p.38-39's shape but presented with cleaner scan quality here, this PDF4 version should be treated as the PRIMARY reference for the exact increase/decrease thresholds, with PDF1's version kept as a secondary cross-check — recommend a final side-by-side digit verification between the two before locking values into `vertical_slice.json`, since minor transcription drift is possible in both.)
  - **PRIORITY ORDER for store-rank stats, EXPLICIT (PDF4 p.75)**: "パラメータ優先度は警備＞清掃＞サービス＞人気" — CONFIRMED_OFFICIAL explicit ranked priority for which stat matters most to store evaluation: 警備(security) > 清掃(cleanliness) > サービス(service) > 人気(popularity).
  - **AD cost-efficiency — EXACT ¥-per-effect-point ratios (PDF4 p.77)**: table "宣伝方法/宣伝費/宣伝日時/宣伝効果/コストパフォーマンス", cross-confirming the cost/timing/effect numbers exactly (ダイレクトメール¥100,000・2日10時・+12; 新聞広告¥500,000・2日7時・+20; 飛行船¥1,000,000・3日15時・+40; ラジオCM¥3,000,000・1日17時・+60; テレビCM¥5,000,000・1日19時・+90) and ADDING an explicit per-¥10,000 efficiency figure for each: **ダイレクトメール=1.2 effect/¥10,000, 新聞広告=0.4, 飛行船=0.4, ラジオCM=0.2, テレビCM=0.18** — CONFIRMED: ダイレクトメール is the single most cost-efficient ad by a wide margin (matches the earlier "宣伝はダイレクトメールで充分" strategy tip on the same page-set, p.75 POINT2). Also gives the "顧客を呼び込む効率的な宣伝" formula box: "店舗の現在のランク評価値 + 宣伝効果（ランク評価値はP75の計算による）" — i.e. an ad's popularity effect ADDS to the store's current internal rank-evaluation value (the 0-100 number from the star-band table above), not to a separate raw "人気" tally — clarifying exactly how the ad-effect numbers (+12/+20/+40/+60/+90) interact with the 0-100 internal evaluation scale.
  - **STAFF WAGE FORMULA — restated as an explicit formula box (PDF4 p.71)**: "社員の基本時給額 = 年齢×10+100（円）" — third independent confirmation of the exact formula (matches PDF2's derived value and PDF3's earlier phrasing), now given as a clean formula box.
  - **Staff rehire cooldown — EXACT (PDF4 p.71)**: "社員いったん解雇しても、約1年経てば再び雇用リストに名前が載るのである。" — CONFIRMED_OFFICIAL: fired/quit staff reappear as hire candidates after approximately **1 year**.
  - **Super Employee (80歳) mechanic — reconfirmed, still no exact odds (PDF4 p.71)**: "80歳を越えたキャラクターは、一定の確率でスーパー社員へと変化する。すべてのパラメータが100なので、中型以下の店舗ならば、スーパー社員ひとりで切り盛りさせて、人件費を抑えよう。" — third source confirming the age-80 threshold and all-100-stats outcome; the exact per-check PROBABILITY remains unconfirmed across all 4 PDFs — treat as a genuinely open gap requiring a bucket-3 invented placeholder if the project needs a concrete number, tagged `REMAKE_BALANCED_DEFAULT` per project convention.
  - **Platform difference — Saturn allows custom staff base-up rate (PDF4 p.71)**: "セガサターン版は社員のベースアップを任意に設定できる。左に示した基本時給を参考に、各社員の適正賃金を割り出そう。" — reconfirms the Saturn-vs-PS wage-negotiation divergence already flagged from PDF1 p.57.
  - **MIDNIGHT PRICING EXPLOIT — exact mechanic, MAJOR FIND (PDF4 p.73)**: "夜中0:00に大安売り: プログラム上、翌日の客数はAM0:00にすべて計算されている。よって、このAM0:00直前に値下げを行うと、翌日の客数が飛躍的に増えるのである。この計算が終わった後に値上げをしても、いったん決定した客数は変化しないのだ。" — CONFIRMED_OFFICIAL EXACT MECHANIC: the game locks in "tomorrow's" customer-count/traffic calculation at the instant of AM0:00, based on whatever price is set AT THAT MOMENT. A player can discount right before midnight to inflate the next day's traffic, then immediately raise prices back up after midnight passes — the traffic boost is already locked in and unaffected by the later price change. This is a significant, exact, exploitable simulation-timing rule worth preserving precisely in any faithful recreation.
  - **Time-of-day customer breakdown — 3-band table, MORE PRECISE than PDF1's 2-band clock wheel (PDF4 p.72)**: "AM5:00~AM9:00: 大学生やサラリーマンを中心に、ほとんどの客が朝食を買いに来店している。パン類、温かい飲料、冷たい飲料を取り揃えよう。" / "AM10:00~PM9:00: 昼から夕食にかけての時間帯で、客の目当ても様々。客単価が高いのは中年層や家庭の主婦。薄利多売を目指すなら、おやつを買いに来る子供たちも無視できない。" / "PM10:00~AM4:00: PM11:00までは酒を買いに来るおじさんたちがメインターゲット。客単価は高いが、短気なので怒りやすい。深夜にはたばこや弁当が売れる。" — REFINES PDF1 p.23's simple 2-band (昼=主婦・子供 vs 夜=独身男性) into an explicit 3-band schedule with specific product recommendations per band.
  - **New-store discount tip — exact figure (PDF4 p.76)**: "1.5倍の売り上げが見込めるお店の前に新規開店" (POINT2) — target opening a new branch specifically in front of/near a store doing ~1.5× the area-average sales, to poach its traffic. (Separately, POINT1 of 価格設定/p.73 gives the exact DEFAULT store-wide discount recommendation: "商品全体で1%offが基本" — i.e. a flat, permanent 1% store-wide discount is the book's baseline recommended pricing stance, distinct from the 40% baseline profit-margin figure from PDF3 — the 1% figure is an OPTIMIZATION on top of the 40%-margin default, not a replacement for it.)
  - **RIVAL BUYOUT / new-plot land cost — EXACT FORMULA, resolves and refines the land-cost gap (PDF4 p.79)**: "新規開店時の土地代 = 地価（4エリア分）＋建物評価額÷2（複数の施設を撤去する場合は合計額の1/2）" — CONFIRMED_OFFICIAL EXACT FORMULA: total cost to acquire an occupied plot = (that location's land-value rate × 4 map-areas) + (existing building's appraisal value ÷ 2); when multiple structures sit on the target plot, the ÷2 is applied to their SUMMED appraisal value. This gives an exact area-multiplier (×4) for the land component that PDF1 p.7's looser "土地代≈エリア地価×エリア数" phrasing did not specify a number for — CONFIRMS the number of areas is exactly **4** for a standard plot acquisition, and reconfirms the building-acquisition-fee-is-50%-of-appraisal rule from PDF1 p.7 with an exact formula.
  - **ALL 4 MAPS — exact starting DATA blocks, cross-confirms and extends PDF2/PDF3's map stats (PDF4 p.80-83)**:
    | Map | 資金 | 人口 | ライバル店 | セキュリティ施設 | 交番 | 消防署 |
    |---|---|---|---|---|---|---|
    | 初級 | ¥200,000,000 | 2,179人 | 2店舗 | 3 | 2 | 1 |
    | 中級 | ¥150,000,000 | 1,880人 | 3店舗 | 3 | 2 | 1 |
    | 上級 | ¥150,000,000 | 1,416人 | 1店舗 | 2 | 2 | 1 |
    | 極上 | ¥150,000,000 | 2,849人 | 5店舗 | 6 | 5 | 1 |
    - Per-store starting stats also given for every rival store on each map (営業時間 uniformly AM7:00~PM11:00 for all rival stores across all 4 maps; each rival has its own starting 人気/警備/清掃/サービス values in the 14-90 range, and a specific 買収 (buyout) cost shown for several, e.g. ¥46,721,490 appearing identically for multiple rival branches on the 初級/中級 maps, and ¥46,580,670 for several 極上-map branches — these repeated identical buyout figures across different named branches suggest the buyout cost may be a MAP-SCENARIO-FIXED scripted value per branch slot rather than a live formula output for these specific starting rivals, worth flagging as a possible scripted/canned value rather than a live simulation output).
    - NOTE minor cross-source discrepancies vs PDF2's map data: population figures are very close but not identical (初級 2,179人 matches exactly; 中級 1,880人 here vs 1,876人 in PDF2; 上級 1,416人 here vs 1,424人 in PDF2) — likely just different snapshot moments (population drifts turn-to-turn) rather than a real conflict, but flagged for completeness.
    - Per-map strategic notes reconfirm: 初級 win condition reached via population→都庁 (20,000 threshold per PDF3); 中級 win via 10-store cap INCLUDING rivals (confirms PDF3's clarification); 上級 win via all-5-owner-metrics-★★★★★; 極上 (secret map) starts with the already-established 5 rival stores as its defining hard-mode hook.

### PDF4 per-page log
- p.1 (=print p.48-49): continuation of the「パーソナルコンビニデザイン 3 to 74」joke catalog from PDF3 (未開の土地に開店するなら!/孤島 entry carried over, then 赤字経営を目指す不幸好みのあなたへ! section: 永田町のような政治都市/銀座のような高級呑み屋街/幼稚園の近く) — flavor/joke content, no new mechanics.
- p.2 (=p.50-51): more joke catalog (過疎化した村/過酷な状況下でもコンビニは開店する!: 犯罪多発地域/核シェルター内部/食料不足の国) — flavor.
- p.3 (=p.52-53): joke catalog (若者大歓迎の街: 大学近くの学生街/高校(共学)の近く/スキー場ゲレンデ中腹; 女の子たちにモテるコンビニ: 渋谷・原宿のようなティーンの街/水族館の近く/遊園地のそば) — flavor.
- p.4 (=p.54-55): joke catalog continued (高校(女子校)の近く; 時代の先端ハイテクランド: 幕張のようなイベント会場そば/高速道路のインターチェンジ/秋葉原のような電気街) — flavor.
- p.5 (=p.56-57): joke catalog (成田のような国際空港内; 絶対あるわけない内装デザイン: 常夏の熱帯地方/エベレストの頂上/巨大宇宙船内) — flavor.
- p.6 (=p.58-59): joke catalog (海底都市; あったら怖いイカれた店舗: 北海道の牧場地帯/動物園の近く/野菜市場の近く) — flavor, though 野菜市場 entry reconfirms 1/2マス congestion mechanic in passing ("路はすべて1/2マスなので、大混雑は必至").
- p.7 (=p.60-61): joke catalog (いたこの棲む街; お客さんに怒られたいオーナー必見!: 北陸地方の雪国/農村/漁港) — flavor; 漁港 entry reconfirms 1/2マス passage congestion again.
- p.8 (=p.62-63): joke catalog (極個人的にはこんな店が好みだ!: 高校(男子校)の近く/香港のような人口過密地域/競馬場の近く/飯田橋CB's近辺) — flavor, closes out the "74-entry" catalog (only ~55 of 74 named entries were actually visible across both PDF3 and PDF4's shared scan range; the remainder of the catalog's named entries from the TOC — 墓地内, 幼稚園の近く[dup], 高校(共学の近く)[dup], etc. — appear interleaved rather than strictly sequential, and a handful of TOC-listed entries were not visibly rendered in either scan).
- p.9 (=p.64-65): blank fill-in-your-own-design template page ("自分だけのコンビニを作る！PART2") + back-cover ad for the THIRD companion book「攻略&データブック」("これで攻略はバッチリ！まわりの建物からお客の好みを解析") — establishes that p.65 onward is this new, mechanically-dense book.
- p.10 (=p.66-67) 「オールテクニックガイド」overview/index page: no new hard data beyond the section index itself (店員関連→P71, ライバル対策→P78-79, 顧客ガイド→P77, 営業時間→P72, 評価関連→P75, 内装関連→P68-69, 誘致関連→P74, マップ別攻略→P80-83, 品揃え→P70, 価格設定→P73, 新規出店→P76).
- p.11 (=p.68-69) 「内装関連」: full detail in Notable findings (18-point layout checklist, exact サービス値 formula).
- p.12 (=p.70-71) 「品揃え」/「社員関連」: full detail in Notable findings (6-point assortment checklist, 10-point staffing checklist, wage formula restated, rehire cooldown, Super Employee mechanic, Saturn-only custom base-up).
- p.13 (=p.72-73) 「営業時間」/「価格設定」: full detail in Notable findings (6-point hours checklist, 3-band time-of-day customer table, 6-point pricing checklist, midnight-pricing-lock exploit).
- p.14 (=p.74-75) 「誘致関連」/「評価関連」: full detail in Notable findings (exact security formula + size multipliers, star-rating 0-100 bands, refined rank increase/decrease table, exact 1/6-chance angry-customer penalty and flat shoplifting/donation modifiers, stat-priority ordering).
- p.15 (=p.76-77) 「新規出店」/「顧客ガイド」: full detail in Notable findings (10-point new-store checklist, exact 清掃値 formula, elderly-customer anger-propensity confirmation, exact ad cost-efficiency table).
- p.16-17 (=p.78-79) 「ライバル対策」: full detail in Notable findings (10-point rival checklist, exact land/buyout cost formula with the ×4-area land component).
- p.18 (=p.80-83) 「マップ攻略」: full detail in Notable findings (exact starting DATA blocks for all 4 maps including the secret 極上 map, per-rival-store starting stats and buyout costs).

- **DATA LIST section (PDF4 p.84-95) — final compendium, 4 sub-tables, cross-confirms and extends PDF2's data.** Header: "コンビニ運営を助けるスペシャルデータ集 / シミュレーションゲーム攻略の近道といえば、ゲーム内で扱われているデータを理解するということに尽きる。ここではゲーム中にリアルタイムで変化するデータを、わかりやすい形に再編集した。"
  - **DATA1 商品 (Products) — full table with SEASON column, MAJOR FIND for the "seasonal item" gap (PDF4 p.85)**: columns 名称/定価/原価率/1個補給(restock unit cost, = 定価×原価率, matches the 補充費=仕入単価×数量 formula)/**季節**/商品棚(compatible fixture type)/[3 further numeric columns, sidebar-explained as 需要数値(demand figures) — exact semantic label partially illegible at this resolution, transcribed as raw numbers below]. THE KEY NEW DATA is the **季節 (season)** column, giving an EXACT seasonal tag per product category: 冷たい飲料=**夏季**, 温かい飲料=**冬期**, 酒類=なし, 弁当類=なし, パン類=なし, インスタント類=なし, 菓子類=なし, 本類=なし, たばこ=なし, **アイスクリーム=夏季**, 文房具=なし, 電気製品類=なし, 野菜類=なし, 魚類=なし, 肉類=なし, レトルト類=なし, 調味料類=なし, 冷凍食品類=なし, **おでん=冬期**, 日用品=なし, コピー用紙=なし, 宅急便申込書=なし, 薬品=なし, 下着類=なし, イベント商品=なし, **中華まん=冬期**, 現金=なし. — CONFIRMED_OFFICIAL: only **4 product categories** carry an explicit season tag: 冷たい飲料/アイスクリーム (summer) and 温かい飲料/おでん/中華まん (winter) — this is the definitive, exact answer to which products are "seasonal" in the simulation (all others are season-neutral, sellable year-round with no seasonal demand modifier). Sidebar notes: "1個売れるたびに原価率にしたがい、支払った金額のうち店ごとの維持費や従業員の給料といった経費が引かれることになる。" (confirms per-unit-sold revenue split funds upkeep/wages) and "最大維持費と収容力: 全体にいえることだが、最大維持費が高くなる方が、最大収容力も高くなる方が勝る。ワゴンの方が注目度が高くなるが、よく買いにくる客からは棚でも十分。" and "需要数値: 特定の条件でこの商品を欲しがる客がどれくらいいるかを求める数字。ただし、いろいろな条件が重なるため、常にこうなるわけではない。あくまでも一例。" (the extra numeric columns are example/illustrative demand figures under specific conditions, NOT a fixed universal constant — explicit caveat against over-reading them as hard constants).
  - **DATA2 商品棚 (Product shelves) — full compatibility matrix (PDF4 p.86-89)**: restates the PDF2 fixture table (縦/横/機能/中外/棚価格/維持費(円/1時間)/収容力/注目度/備考) with an added full ○/× COMPATIBILITY MATRIX cross-referencing every fixture type against every one of the ~27 product categories — this is a complete, exhaustive confirm of which fixture can hold which product, superseding the partial "取扱商品" text-lists from PDF2 with a precise grid. New fixture entries not seen in PDF2's list: **温ジュース(1×1,保温,中,¥300 price/¥70 upkeep,収容20,注目度20)**, confirms 冷蔵ワゴン2(2×2)=360/130/40/30 and matches PDF2 exactly elsewhere; adds descriptive 備考 (remarks) column per fixture, e.g. 大型常温棚="とにかく収容力が高い", 大型冷蔵ワゴン2(2×2)="大きい分注目度も高い", レジ4(3×1)="ふたりでレジ打ちも可能" (CONFIRMED: レジ4 specifically supports TWO staff checking out simultaneously — a distinct capability not stated elsewhere), キャッシュディスペンサー(1×1,¥4000/¥60,収容50,注目度20)="店内利用のみ" vs (1×1,¥7000/¥100,収容90,注目度30)="扉つきなので外にも置ける" (clarifies the cheap dispenser is INDOOR-ONLY while the expensive one can go outdoor specifically because it has a door/lockable enclosure), 駐車場="収納台数が低い", 2階建駐車場="駐車場の2倍停められる", タワー駐車場="駐車場の10倍停められる" (CONFIRMED: exact capacity RATIOS — 2階建=2×base, タワー=10×base — consistent with PDF2's absolute figures 2/4/20, i.e. 2×2=4 and 2×10=20 ✓ exact arithmetic match).
  - **DATA3 社員 (Staff) — comprehensive named roster with growth-cap values (PDF4 p.90-91)**: full-page roster (~30 more named staff beyond PDF2's list, substantially overlapping the same named characters e.g. 秋本三四郎/朝田宗司/雨中聖人/池上秀夫/市川智恵子/奥平康夫/忍田信子/小田伸行/金田哲也/小宮千明/今野京介/佐々木信雄/里中涼子/菅原文夫/杉村真知子/杉本三郎/高橋大介/竹中小百合/田中幸子/谷口明/富永福子/長沢達也/中山光次/西田年男/花沢咲江/浜田夕子/福本孝仁/的場丈二/丸山昭夫/万田町子/南田洋次/森山雪之丈/山下大介/山本信夫/吉田有紀 — CROSS-CONFIRMS this is the SAME fixed roster as PDF2 p.126-133, not a different set, strongly suggesting the game's hire-candidate pool is a FIXED cast of ~30-35 pre-authored characters rather than randomly generated. Sidebar: "新店舗開店のときに重要なファクターとなるのが、誰を雇用するかだろう。レジ能力など5つのパラメータは、右側の数字まで順調に成長し、その後はゆっくりと成長する。" — reconfirms the PDF2 "能力分岐ポイント" growth-slowdown mechanic (the listed cap number is where growth transitions from fast to slow, not a hard ceiling).
  - **DATA4 建物 (Buildings) — exact price + demand list, split by day/night activity pattern, MAJOR FIND (PDF4 p.92-95)**: Three sub-lists:
    - "朝から夜だけ客のいる建物" (buildings with customers only 6am-11pm, i.e. no overnight traffic) — table columns 名称/縦/横/建物属性/建物価格/主なほしい品物(朝から夜): 交番(2×2,その他施設,¥100,弁当類/たばこ/冷たい飲料), 役場(村役場)(2×2,役場,¥700,弁当類/インスタント類/パン類/野菜類/肉類), 役所(県庁)(5×5,役場,¥200,弁当類/パン類/たばこ/インスタント類/レトルト類), 都庁(7×7,役場,¥400,弁当類/パン類/たばこ/インスタント類/レトルト類), 幼稚園(3×2,学校,¥200,菓子類/魚類/肉類/冷たい飲料/野菜類), 小学校(4×4,学校,¥200,文房具/菓子類/イベント商品/文房具/温かい飲料 [sic, duplicate 文房具]), 中学校(5×5,学校,¥200,冷たい飲料/イベント商品/文房具/温かい飲料), 高校(6×6,学校,¥200,冷たい飲料/イベント商品/コピー用紙/中華まん), 遊園地(7×7,アミューズメント,¥200,菓子類/冷たい飲料/温かい飲料/アイスクリーム), 水族館(3×3,アミューズメント,¥300,菓子類/冷たい飲料/アイスクリーム), 動物園(6×6,アミューズメント,¥200,冷たい飲料/菓子類/アイスクリーム), 公園(小)(1×1,アミューズメント,¥1000,菓子類/冷たい飲料/アイスクリーム), 公園(大)(2×2,アミューズメント,¥500,菓子類/冷たい飲料/アイスクリーム), ゲームセンター(1×1,店,¥2000,たばこ/薬品/冷たい飲料/日用品), パチンコ屋(2×2,店,¥800,パン類/たばこ/酒類/魚類/冷たい飲料), 住宅(小D)(1×2,住宅,¥1000,酒類/アイスクリーム/魚類/日用品/下着類/野菜類/イベント商品), 住宅(中A)(2×2,住宅,¥700,パン/酒類/アイスクリーム/野菜類/日用品/下着類/肉類/文房具/イベント商品), 住宅(大C)(3×2,住宅,¥1000,酒類/アイスクリーム/魚類/日用品/下着類/肉類/文房具/イベント商品), 銭湯(2×2,店,¥700,インスタント類/弁当類/酒類/アイスクリーム/パン類), 体育館(3×3,その他施設,¥700,冷たい飲料/弁当類/温かい飲料/アイスクリーム), 運動場(5×4,その他施設,¥100,冷たい飲料/弁当類/薬品/果実類/アイスクリーム), プール(3×2,その他施設,¥300,冷たい飲料/弁当類/薬品/菓子類/アイスクリーム), イベント会場(2×2,その他施設,¥1500,イベント商品/菓子類/冷たい飲料/中華まん), ファミリーレストラン(2×2,店,¥1000,たばこ/インスタント類/酒類/日用品/電気製品類/下着類), レストラン(2×1,店,¥2500,たばこ/インスタント類/酒類/日用品/電気製品類/下着類), ファーストフードA(1×1,店,¥2000,インスタント類/レトルト類/酒類/イベント商品/コピー用紙/菓子類), ファーストフードB(1×1,店,¥2000,レトルト類/酒類/たばこ/コピー用紙/菓子類/中華まん), そば屋(1×1,店,¥1000,野菜類/肉類/弁当類/インスタント類/魚類/レトルト類), おもちゃ屋(1×1,店,¥1000,日用品/野菜類/下着類/電気製品類/魚類/肉類), 洋品店(1×1,店,¥1000,野菜類/魚類/下着類/日用品), 電気屋(1×1,店,¥1000,電気製品類/下着類/日用品/魚類/野菜類).
    - "深夜から早朝にも客のいる建物" (buildings with customers even in the dead of night) — 消防署(3×2,その他施設,¥100,弁当類/冷たい飲料), 駅(小)(2×1,駅,¥1000,パン類/弁当類/温かい飲料/冷たい飲料/インスタント類/レトルト類/たばこ/中華まん), 駅(大)(4×2,駅,¥1000,パン類/弁当類/温かい飲料/冷たい飲料/インスタント類/レトルト類/たばこ/中華まん), 大学(7×7,学校,¥200,弁当類/パン類/インスタント類/イベント商品/レトルト類/コピー用紙/冷たい飲料), 専門学校(4×3,学校,¥400,弁当類/パン類/イベント商品/レトルト類/冷たい飲料), 会社(小A/B/C各種)(2×2,会社,¥800/¥800/¥1000,various combos of パン/たばこ/冷たい飲料/インスタント類/レトルト類), 会社(大A/B)(3×3,会社,¥500/¥600,expanded combos incl. 日用品/本類/電気製品類), 住宅(小A/B/C各種)(1×1,住宅,¥1000/¥1000/¥2000,various), 住宅(中B)(2×2,住宅,¥700,野菜類/日用品/酒類/惣菜類/レトルト類/インスタント類/電気製品類), ファミリーレストランA/B(2×2,店,¥1000 each,various), ラーメン屋(1×1,店,¥2000,インスタント類/弁当類/温かい飲料/酒類/たばこ), 飲み屋A/B/C(1×1,店,¥1000 each,various combos incl. たばこ/酒類/おでん/日用品/レトルト類/本類).
    - "客のいない建物" (buildings with ZERO customer generation) — コンビニ(自)[own convenience store](2×2,¥300), コンビニ(敵)[rival convenience store](2×2,¥300), 空き地[empty lot](1×1,¥0), 道路[road](1×1,¥100), 線路[railway track](1×1,¥100), 役場用地[government-office land, pre-建設](1×1,¥0), 誘致用地[attraction-designated land, pre-build](1×1,¥0). — CONFIRMED: convenience stores themselves (yours or a rival's) generate NO ambient "buying population" the way other facilities do — they are pure destinations, not population sources.
    - **Time-band customer-frequency matrix (PDF4 p.92-95)**: table gives, per building, a row of relative customer-count NUMBERS across 6 time bands **朝(7-11時)/昼(12-15時)/夕(16-19時)/夜(20-23時)/深夜(24-3時)/早朝(4-6時)**, PLUS qualitative 平日/休日 visit-likelihood descriptors (確実/ほぼ確実/まず確実/半々/やや少ない/少ない/少な目, etc.). Example rows (building name inferred from list order, values 朝/昼/夕/夜/深夜/早朝): 交番-type row "0 10 15 0 0 0" (平日=確実,休日=少ない); a large-magnitude row reading "22 73 15 10 0 0" (平日=確実,休日=少ない) — likely 都庁 or a major facility; 駅(大) row shows extreme values "1120 0 1400 2240 560 280" and 駅(小) "560 0 2620 1680 0 840" — CONFIRMED: stations generate MASSIVE customer-count multipliers relative to ordinary facilities (2-3 orders of magnitude larger), consistent with PDF3's "~2000-population-equivalent" station claim. Sidebar explains: "時間帯によって客の現れる頻度を数値化したもの。もちろん、数値は大きければ大きいほど客が多い。実際に現れる時間は細かく設定されているのだが、ここでは理解しやすいよう単純化してある。単純化は現実の時間帯に合わせて6区分としたが、店の営業時間によって確実な頻度が求めにくい場合もある。" and "平日と休日: その建物の性格によって、現れる客の傾向が左右される。もちろん、会社などは休日は出勤してこないので休日頻度が少なくなるというわけだ。この項目の表記は、客の人数ではなく、客自体の出現確率になっている。「少ない」場合でも、時間帯ごとの出現頻度が高ければ何人も来ることがある。" — CONFIRMED: the 平日/休日 column is a PROBABILITY-OF-APPEARANCE descriptor, NOT a headcount — distinct from the numeric 朝/昼/夕/夜/深夜/早朝 columns which ARE relative headcounts. Time-band definitions given exactly: **朝=7時から11時、昼=12時から15時、夕=16時から19時、夜=20時から23時、深夜=24時から3時、早朝=4時から6時**.

- p.19-24 (=print p.84-95) 「DATA LIST」(DATA1商品/DATA2商品棚/DATA3社員/DATA4建物): full detail in Notable findings immediately above. This is the final page of PDF4 (24/24 pages read) and completes the full 4-PDF extraction task (PDF1 33/33, PDF2 35/35, PDF3 23/23, PDF4 24/24 — 115/115 total pages read).

---

## PDF1 — 「新人店長実習マニュアル」— 第1章 新規開業編

### p.1-2 (unnumbered cover/TOC + chapter title page)
- Cover: title "ザ・コンビニ ～あの町を独占せよ～ 新人店長実習マニュアル"
- Table of contents, 第1章「お店を大きくして一人前の店長になろう」:
  - 店の場所や規模を決める … 6
  - 店内のレイアウトを決める … 14
  - 営業方針を決める … 22
  - 店員を雇う … 24
  - いよいよ営業開始 … 30
  - 広告・宣伝を打つ … 36
  - お店の評価を聞く … 38
  - コンビニ珍経営日記 … 40
- 第2章 (mislabeled in TOC as same title as 第1章 — likely a scan/OCR duplication artifact of the actual chapter title, transcribed as printed): 建物の誘致…44 / 2号店の開設…46 / ライバル店対策…52 / 店員の管理…56 / アクシデントに備えて…58 / 高収益のために…60 / 新米店長のためのQ&A…64
- 第3章「キミの手で、あの町を独占しよう」
- 第4章「コンビニ経営 資料集」
- Screenshots "Photo1"/"Photo2" on TOC page show in-game HUD: date "1年目 6月9日[快晴] 07:02", money "¥101,385,260"; second: "1年目 6月9日[晴れ] 08:42", money "¥47,946,914" with a right-side panel reading "配置/移動/売却" (place/move/sell) menu labels and "変動夏却/移転変更/売終" partially legible ("配置" placement, "移動" move, "売却" sell — store fixture-editing menu).
- Chapter title spread: "第1章 新規開業編" / "自分のお店を作ろう" — "店長がまず最初にやらなければならないこと それは、自分だけのお店を持つことだ 世界でたったひとつのお店をデザインしよう"

### p.6 「建てる場所や店の規模を決める」
- See Notable findings above for exclusion-zone diagram, land-cost formulas, best-5 list.
- HUD screenshots show land price examples: "空地 ¥30,000,000" "空地 ¥26,000,000" with in-game clock "1年目 1月1日[快晴] 00:00".
- Text: "新しくお店を建てる場所を決めよう" — "もうかるお店の店長を目指すなら、広いマップのどこにでていいのじゃない。お客さんが多そうな場所、将来発展そうな場所を狙って出店するのが名店長への第一歩。いいかげんな場所に店を出しても閑古鳥状態になってしまうから、出店場所は慎重に選ぼう。"
- "どこを狙って建てたらいい?" — "出店場所の狙い目は、ズバリ建物の密集しているあたり。店の近くにビルや住宅地があれば、そこの住人が買い物にきてくれるからだ。もし建物が少なくても将来発展しそうな場所を狙い目のひとつ。お店を大きくすることで、住人をドンドン呼び寄せることも夢ではないからだ。"

### p.7 「場所が決まったら、その土地を自分のものにしよう」
- (Full detail captured in Notable findings section: land-only vs land+building cost formulas, exclusion-zone diagram 5/7/11/15.)
- Screenshot in-game HUD: "空地 ¥30,000,000" / "空地 ¥34,000,000" with住宅(residential building)example land ¥34,000,000 total (土地代+建物買収費 implied).

### p.8-9 「この物件は"買い"だ」 / 「お客を呼ぶには酒・たばこの販売許可がほしい」
- 4 "掘り出し物" (bargain finds) call-outs with cost + star rating:
  1. 近くに学校がある — 土地費用 2千5百万円 (¥25,000,000) — おすすめポイント ★★★☆☆
  2. 大通りに面している — 土地費用 2千5百万円 (¥25,000,000) — ★★★★☆
  3. 鉄道線路のそば — 土地費用 2千万円 (¥20,000,000) — ★★★★★
  4. マップの中央付近 — 土地費用 2千万円 (¥20,000,000) — ★★★☆☆
  - Text under #1: "登下校の途中にコンビニに寄っていく学生がいるので、お客さんの数が確保できるのがうれしい。いくつもある学校のなかでもできれば大学のそばがいちばん効率的なので、できるだけ近くの土地を手に入れよう。"
  - Text under #2: "目の前を道路が通っていれば、車で来るお客さんにとって便利になる。つまり道路からうっかんでいるお店よりもお客さんが来店しやすくなるということだ。できるだけ道路に接した土地にお店を建てるようにしよう。"
  - Text under #3: "ゲーム開始直後では関係ないけれど、町が発展していくと駅が建つ。駅の周りは爆発的に発展する可能性があるから、その前から線路の近くに店を持っておきたい。ただし駅の建つ場所を予測できないのが難点。"
  - Text under #4: "お店の周りのお客さんをまんべんなく集められることからも、できるだけマップ中央付近にお店を構える。その周りに住宅地やオフィス街があればおおいので、条件に合った建物をいろいろ探してみよう。"
  - "こんな物件はやめておこう" callout: "マップの端にお店を出した場合、マップ外の部分からのお客さんは期待できない。つまり最初からお客さんの数が少ない不利な条件となってしまうのだ。そうならないためにも、お店はマップ中央付近に建てよう。"
- p.9: Sales permit cost table + exclusive-range benefit callout "酒・たばこ販売許可の意外な利点": "販売許可商品はある程度の距離を置かないと扱えない仕組みになっている。つまり酒・タバコを扱っている自分のお店の近くにライバル店が建設されたとき、ライバル店はお金があっても販売許可を取れなくなるのだ。これを利用してライバル店に酒・タバコを売れなくさせることができるぞ。ただしライバル店が先に建っている場合、自分が販売許可を受けられない場合だってある。"

### p.10-11 「小さくまとめるか、大きくするか、店の規模を決める」
- (Store size costs table captured above in Notable findings.)
- Store selection UI screenshot: "店舗を選んで下さい ¥6,000,000" with 6 thumbnail icons (small/med/large × vertical/horizontal).
- Text: "小さな店ならかんたんに経営できるけどもうけはそこそこ。大きな店はもうけも大きいけど管理がたいへんなんだ。さて、どんなお店を建てたらいいのかな。"
- Manga strip "コンビニ物語『店長の野望』の巻" — dialogue about wanting to run a bigger supermarket-like store eventually (flavor text, not mechanical data).

### p.14-15 「便利で使いやすい内装を考える」
- "内装の基本は"コンビニエンス"" callout: "「コンビニエンス」という言葉の和訳は"便利"ということ。つまりできるだけ便利なお店ほどお客さんが喜ぶお店ということなのだ。どんなことに気を配ればお客さんが喜ぶか!? 次のページの4ヶ条を見ながら、キミなりの便利な内装を考えてみてもいいんじゃないかな。"
- "内装で変えられる3つのポイント": ◆商品の配置・棚・ワゴンの変更 → "集客率アップに!!"; ◆店内の通路の決定 → "スムーズな営業に!!"; ◆店外のレイアウト → "サービス度アップに!!"
- "便利なお店といわれるための内装術4ケ条":
  - 第1条 入口は広々、通路は歩きやすくが基本 — with two layout example screenshots ("レイアウト例:1" bad money ¥93,864,652 vs "レイアウト例:2" better ¥99,214,294, caption: "棚と棚のあいだに余分があるので、お客さんが大勢来てもゆとかあるお店")
  - 第2条 人気商品は店の奥に — text: "欲しい商品が入口近くにレレると、お客さんはすぐレジに向かってしまう。ついでの買い物をさせるためには、売れ筋商品を奥に配置。店内を歩かせて、ついでの買い物をしてもらうようにするのだ。"
  - 第3条 なるべく品数を多めに — text: "かたよった商品しかない店に来店したお客さんは、何も買わずに帰ってしまう。便利なお店と呼ばれるためには、1軒でなんでもそろえようと思わせる品揃えが必要だ。品数の分だけお客さんの数も増えていくぞ。"
  - 第4条 サービス向上のためのアイテムも加えて内装する — "サービスアイテム・1" (噴水/fountain image) "サービスアイテム・2" (ベンチ/bench image). Text: "噴水や観葉植物、ベンチといった道具はお店の売り上げとは直接関係ない。これらは店のサービス度を上げるものなのだ。サービス度の高いお店ほどお客さんが好印象を持ってくれて、また買い物に来てくれる。こんなちょっとした心配りも一人前のコンビニ経営には必要となるのだ。"

### p.16-17 「お客さんが気軽に入れる店内レイアウトを作る」
- "店内を一周する客の流れを作る" — text: "店内を混雑させない方法、それはお客さんに一定のコースで店内を回ってもらうことだ。店内をグルッと一周するようなレイアウトにすれば、お客さんは順々に歩きながらほしい商品を見つけられる。そうしたお客さんの流れが生まれるレイアウトをめざそう。"
- "入口とレジ周辺は余裕を持って" — "いちばん混雑するポイントはレジと出入口。せっかく作ったお客さんの流れをジャマしないように、レジと出入口前は広めに設定しておこう。"
- "通路の幅は人間ふたり分が基本" (see Notable findings for exact quote)
- "試しに作った店で、客の動きを見てみよう" — 3 case examples with in-game money values:
  - その1 レジと出入口が近い店 — "来店する人、お店から出ようとする人、レジを待つ人が重なって大混乱状態に。レジと出入口は離しておいたほうが、余計な混雑を生み出すことないのだ。" (money in screenshot ¥185,799,220 area)
  - その2 通路の幅が狭い店 — "行きつ戻りつすることができないのでとても歩きにくいお店。すれ違うことができるくらいの余裕を持って内装しよう。むやみに詰め込めばいいものではない。" (¥148,614,608 area)
  - その3 とにかくゴチャゴチャした店 — "流れもなにもできないお店。お客さんが少ないうちはいいけれど、繁盛しだしたら一発で大混雑状態になることは必至。店内を回れる通路を作るように" 
- Sidebar "お客ばかりでなく店員にも便利に": "レジの場所" — "お客さんがいないとき店員は休憩室で休んでいる。だからレジと休憩室の距離が近いほうが、すぐにレジに向かうことができて便利なのだ。" ; "社員休憩室" — "休憩室は、疲れた店員がスタミナを回復する大事な場所。ふたつある休憩室のうち価格が高いほうが回復率も高いのだ。ここはケチらずに豪華な部屋を用意したほうが、後々得というもの。" Screenshot shows "深夜居室完定売却完了" panel with "価格 ¥7,000 / ¥2,400/日" values (interpretation: one break-room option costs ¥7,000 [purchase] and ¥2,400/day [upkeep]; exact field labels partly obscured in scan).
- Manga strip "コンビニ物語『通行妨害』の巻" — flavor, customer complains about congestion/blocked aisles, staff scolds ("立ち読みはご遠慮ください!" / "座り読みもご遠慮ください!!" / "椅子の持ち込みも禁止です!" — humor about a customer camping/reading in aisle).

### p.18-19 「欲しい商品と他の商品、バランス良く配置しよう」/ 「棚とワゴンの向きと配置の微妙な関係」
- "商品の配置が客の流れを決める" — "来店したお客さんは、まずほしい商品めざして移動する。これを利用すればお客さんを店の奥に引き寄せることも、お客さんの流れを制御することも可能となる。店内を巡るように作った通路沿いに売れ筋の商品を配置すればスムーズな流れが生まれるはずだ。"
- "客のスムーズな流れ売り上げアップを狙う商品レイアウト法":
  - ◆人気商品はなるべく店の奥に — "お客さんはほしい品物が置いてある場所をめざして移動する。欲しい商品を入出口付近に置くと、なかなか店の奥まで入ってくれない。逆に出入口から離れた場所に売れ筋商品を配すれば、お客さんはお店のなかにとどまっていても買い物をしてくれるのだ。奥まで入ってくれれば、ほしい商品のほかにも買い物をしてくれる機会が増える。だから売れ筋商品は奥に置くのだ。"
  - ◆人気商品との相乗効果を狙う — "売れ筋商品の隣についでにほしい商品が置いてあると、お客さんが買ってくれることが多い。これを利用して売れ筋商品とほかの品物を配置すれば、どちらの品物も売れることになるのだ。売れ筋品ばかりをかためて置くよりもちょっと組み合わせることで、ことさら売り上げを伸ばすことができるといい見よ言えそうな配置。"
  - Screenshot shows shelf item info e.g. "中型米温ワゴン 減効75 弁当 30" and "ていおうストア 本店 ¥30,200" money display, plus a graph screenshot "客層比占率 7% 店舗評価★★★★☆" with a bar chart of 収支 (income/expenses) over time, ranging roughly -300万円 to +300万円 — first sighting of the store-evaluation star rating (★の数, appears to be out of 5) shown alongside 客層比占率 (customer-demographic-share percentage) on an in-game stats panel.
- "棚とワゴンの向きと配置の微妙な関係" (see Notable findings for full shelf vs wagon quote) — fixture placement panel screenshot shows: "設備を選択して下さい" / item "大型冷凍冷蔵庫" / "価格 ¥140" / "維持費 ¥72" / "注目度 10" — CONFIRMS numeric 注目度 stat exists per fixture, and 価格+維持費 (price + daily upkeep) are separate fields for fixtures.
- "レジ前・出入口付近には物を置かない" — "レジ前に棚やワゴンを置くと会計をすることができない。出入口にモノを置くと、せっかく来てくれたお客さんが店内に入れない。このように店内にはモノを配置してはいけないポイントがある。出入口は広く、お店の奥に品物を置くようにしよう。"
- "店外も上手に使えば集客率が格段にアップ" — ◆自動販売機、◆駐車場 (see Notable findings for exact quotes).

### p.20-21 「個性的なお店探訪」
- 4 player-designed store examples, each with a letter grade "総合評価":
  1. 人気商品ばかりをそろえた店 — 総合評価 B — "いわゆる売れ筋の商品ばかりを集めたお店。確かに売り上げは上がりそうだが、本当にもうけるだけではダメ。売れ筋商品だけを売っているのだけでは、ほかの商品や単価の高い商品を近くにおいてついでに買ってもらうようにすれば、もっと売り上げがアップすると思いなしだ。"
  2. 品数の豊富さがウリの店 — 総合評価 C — "限られたスペースを有効に使おうと、徹底的につめこんだお店。しかし店内の品数は多いけれど、それぞれ目立つのは通路の狭さ。これではお客さんがおおぜいやってきたとき、お店のなかで身動きが取れなくなってしまう。レジ前も狭いので、お客さんに怒られてしまう可能性が大きいのが心配。"
  3. 郊外型大型スタイルの店 — 総合評価 B' — "遠くからもお客さんも利用できるように大型駐車場をいくつも配置。マイカーで来店する人にとっては非常に便利なお店といえる。ただし大型駐車場は維持費がかなり高い。ここまで遠くから来店するお客にとらずとも、近くのお客さんをゲットする手段を考えたほうが効率的かもしれないね。"
  4. 実際のお店のレイアウトをまねた店 — 総合評価 A — "実際にあるコンビニのレイアウトを真似して作ったお店。かなり計算されて配置された店内を見ても、お客さんの入りはよさそうだ。離れをいえば入口とレジの距離が近すぎることくらい。やっぱり実際のお店に頼ってばかりはいられないということかな!?"
- "これならおすすめ! 新米店長のレイアウト" — two more examples with EXACT specs:
  - 10×10・縦 — 駐車場・有 自販機・有 — screenshot money ¥153,773,620, date "1年目 1月1日[曇り] 13:48", お店規模 sales ¥8,150 — text: "いかに店内のスペースを有効に使うかを考えてレイアウトされたお店。このサイズのお店にしては壁の棚だけではなく3列にしたワゴンを出すなどして商品を並べている。ただし、店員の能力が低いうちはレジで混雑するのはさけられそうもないようだ。"
  - 12×12・横 — 駐車場・有 ベンチ・有 自販機・有 噴水・有 — screenshot money ¥146,539,266, date "1年目 1月2日[曇り] 12:00", 売上 ¥8,790 — text: "商品だけでなく、お客さんへのサービスにも気を使った作りのお店。噴水とベンチが人気の秘密だ。お店をひと回り大きくすることで、品数は増えたけれどゆったりした作りになっている。これなら店内でお客さんがウロチョロすることもないはずだ。"
- Manga "コンビニ物語『ボクの野望』の巻" — flavor dialogue about dream stores (bento specialist, regional snacks store) — no mechanical data.

### p.24-25 「実際に店で働く社員を選ぶ」/「雇った社員の能力をチェックして、社員の力を知る」
- Full detail in Notable findings (7 staff params, résumé-vs-in-job stat mapping, 3-staff-per-store cap, 店長 teaching bonus).
- "店の運営は社員の腕にかかっている" — confirms max 3 staff per store: "ひとつのお店に雇えるのは3人まで。せっかくのお店をうまく経営するためにも、できるだけ優秀な人を募集したいけれど……"
- "限られたデータを元に、できるだけ優秀な社員を選ぶ" sidebar with pre-hire résumé screenshots showing fields 店長/募集中, wage e.g. ¥4,160/日, ¥5,824/日.

### p.26-27 「働いたぶんだけ、社員の能力は伸びてゆく」/「社員の要求を聞くかどうか、それが問題だ」
- Full detail in Notable findings (stat growth table, wage-by-age table/formula, negotiation refusal).

### p.28-29 「こんな人と働きたい」
- Full detail in Notable findings (3 hire archetypes). Manga「予定外要員」flavor (shoplifting joke).

### p.30-31 「準備万全! いよいよ開店」/「お店にやってくるお客の特徴をリサーチする」
- "潜在的なお客のことを知る" — screenshot shows customer-ejection UI: "あばよ 欲しかった物 下着類 所持金¥11,000 OK/つまみ出す" — confirms 下着類 (underwear) as a valid くらい欲しい品目category, and the pop-up buttons are literally "OK" and "つまみ出す".
- "町の規模と建物が人口を決める" — "まずはマップ中にどのくらいお客さんがいるかを考えよう。お店の周辺にいる建物のなかにいて、その人数は変化するのだ。建物をクリックしてみるとそこにいる人数が表示される。"
- "売り上げが上がれば町も大きくなる" (quoted fully in Notable findings) — population growth tied to sales/popularity, station completion causes population spike.
- "お店を中心にした範囲の住人がターゲットだ" — Venn-diagram figure: 自分の店の範囲 (own store's catchment circle) labeled "本", overlapping ライバル店の範囲 (rival's catchment circle) labeled "ラ" — overlapping catchment = contested customers.
- "お客の来店手段で、範囲が変わる" + exact table (see Notable findings: 徒歩20/自転車40/バイク60/自動車70).
- "範囲内の大まかな客層を知る" — ◆オフィス街~サラリーマン、OL / ◆学校~学生 / ◆住宅地~主婦、子供.

### p.32-33 「来店したお客の行動をチェックする」/「個人データを知ればお客の行動が読めるようになる」
- Full detail in Notable findings (3-step behavior pattern, individual customer data UI, monthly survey/アンケート mechanic + example results table).
- "お客のひとりひとりが欲しいものを買いにやってくる" — "お店にやってくるお客さんは、ひとりひとり所持金も違えばほしい品物も違う。"
- Screenshot labels: 個人データ panel shows job type "会社員" (office worker), "欲しかった物 インスタント類" "所持金 ¥850".

### p.34-35 「来店したお客さんの観察記」/「お店のサービスが悪いとお客さんが怒りだしてしまう」
- Full detail in Notable findings (register-queue leaving, wandering/stuck customer blocks closing, anger drops ALL staff stats, manual eject "つまみ出す" mechanic).
- Manga「気にしない」flavor strip: staff reassure each other not to worry about single angry customers, day-to-day normalization.

### p.36-37 「お店を宣伝してお客を倍増」/「それぞれの宣伝媒体の特徴と効果を知る」
- Full detail in Notable findings (5-method ad table with exact costs/timing/effect numbers, 1-day-only effect decay rule).
- "お店の人気が上がればもっとお客が来るようになる" — screenshot "宣伝方法を選択して下さい(複数可)" ダイレクトメール ¥100,000 / 費用合計 ¥6,000,000.

### p.38-39 「お客さんの生の声 店舗評価を聞く」/「店の評価を上げるのは社員の能力がポイントとなる」
- Full detail in Notable findings (exact increase/decrease point tables for 店舗評価, 4 store parameters incl. 人気, annual 総合評価 target of ★5).
- "キミの手腕が店の評価を変える" — "1から100までの数値で表わされる店舗評価は、いままでの自分の経営方針やお店の作りの善し悪しを判断するための大切なデータ。"
- Screenshot: 収支 monthly report panel — "収支 -¥3,497,936", "他店経費 ¥0", "町人口 2179人", "前々月比 ¥0" (labels approximate per legibility).

### p.40-41 「コンビニ珍経営日記」
- Full detail in Notable findings (player-anecdote edge cases: entrance-blocking wagon, ad-driven stockout, sudden rival impact, remodel-triggered dirtiness, cleaning workload vs. store size).
- This page is flavor/anecdote content framed as "maybe you'll experience this too" rather than official confirmed numeric data — transcribed for completeness, but should be weighted as lower-confidence (CONFIRMED_COMMUNITY-like anecdote, not CONFIRMED_OFFICIAL numeric spec) except where it states a clear mechanic (e.g., customer-blocking, staff-count caps already stated elsewhere).

### p.42 「コンビニ珍経営日記」(continued) / chapter divider 第2章 事業拡大編
- More anecdotes: over-decorating with plants/fountains turning store into "a park, not a convenience store" hurting sales; forgetting to eject a shoplifter in time; all-staff-in-break-room gap; curiosity about what "イベント商品" (event goods) actually contain (flavor, no mechanical answer given).
- Chapter divider: "第2章 事業拡大編 / お店を大きくして一人前の店長になろう" — "もっともうけたい、もっと店を大きくしたい それなら業務拡大を図るのがいちばんだ 一大チェーン店のオーナー目指してがんばれ"

### p.44-45 「建物を誘致して町を大きくする」
- Full detail in Notable findings (誘致 facility table with exact costs/sizes/durations, 1-at-a-time rule, passive monthly growth).
- "誘致をすれば、こんなことが起こる": ①町の人口が増える ②買い物客が増える ③警備能力が上がる.

### p.46-47 「交番・消防署の誘致で、安全確実な営業ができる」
- Full detail in Notable findings (交番 +40 security / 消防署 +30 security, 7-area effective radius for 交番, cost-efficiency comparison).
- Screenshot HUD shows exact store stat panel fields in order: 売上/人気/清掃/警備/サービス with sample values 2,040 / 26 / 100 / 96 / 99 — confirms these 5 fields appear together on the main store-info readout.

### p.48-49 「軌道にのったら2、3号店開設」/「積極的な支店開設が、町の発展にも役立つことになる」
- Full detail in Notable findings (20-area minimum branch spacing diagram, land-value-between-stores bonus).
- "チェーン店を増やして町を独占してしまうのだ" — flavor/strategy text encouraging aggressive multi-branch expansion when funds allow.

### p.50-51 「第2号店開設計画」
- 4-step new-branch checklist: 計画その1 予算をチェック / 計画その2 開設場所を決定 / 計画その3 新店員を雇うのだ / 計画その4 店内レイアウトはどうする.
- "新しい店を定着させるにはお客さんにサービスするのがいちばん" — recommends heavy discounting when opening a new branch: screenshot shows "商品/価格を決定して下さい 全商品平均利益率 20%" with callout "商品利益を20%以下に" and "客が定着するまでもうけは度外視" (treat profit as secondary until customer base is established; target ≤20% profit margin for a new store).
- "ライバル店も支店を出してくる" — rivals also open branches competitively; if a rival claims a targeted spot first, move on quickly.
- Manga「アンタが店長」flavor strip.

### p.52-53 「ジャマなライバル店対策を考える」/「ライバル店のお客を奪い取るのが基本的戦略」
- Full detail in Notable findings (3-point customer-stealing strategy, exact flowchart with 15-20% discount figure).
- "ライバル店の経営方針をチェックする" — ◆ライバル店の場所 ◆ライバル店の客層 ◆ライバル店の経営方針 (paying to inspect a rival reveals its policies, matching the 調査 mechanic seen later at p.55).

### p.54-55 「ライバル店を利用して、町を発展させることもできる」/「支店を建てすぎて相手に有利な土地にしない」
- Full detail in Notable findings (land-value bonus between two stores exploited even with a rival as anchor; buyout/買収 UI with exact example costs).
- "支店を建てすぎて相手に有利な土地にしない" — caution that land-value bonus zones between your own store and a rival can inadvertently help the rival too if not careful; conversely land between TWO rival stores could be exploited by placing your own store there.

### p.56-57 「事業を拡大するには店員教育が必要」/「上手なお店運営のための店員管理術2ポイント」
- Full detail in Notable findings (veteran-staff transfer to new branches, wage-negotiation 2-3% guideline, PS-version 3%-fixed footnote).
- "なかなか育たない店員のワケは!?" — "店員が育たない原因はふたつ考えられる。ひとつは店員の能力が低く業務をテキパキとこなせないこと。レジを打ったり掃除をすることで能力をアップするから、この場合は時間をかけて育ててやるしか方法はない。もうひとつ考えられるのは、店長の教育力不足だ。店長となった人の教育パラメータが低いと、その下で働く店員がなかなか成長してしまう。つまり店長を選ぶには教育パラメータが高い人がおすすめというわけだ。もし店員の成長が遅いときは、店長を変えてみるのもひとつの手段だ。"

### p.58-59 「不測の事態に対する万全の対策を」/「何回も続くとバカにできない被害額 万引き、強盗」
- Full detail in Notable findings (fire mechanic, shoplifting/robbery audio cue mechanic, school-proximity shoplifting risk, fireworks festival, idol-day event with exact 10,000-visitor trigger and 100-popularity lock).

### p.60-61 「さらなる客寄せのポイントを知る」
- "高収益を約束する6つのポイント": ①店の場所は!? ②店内レイアウトは!? ③営業方針は!? ④社員の扱いかたは!? ⑤販促広告は!? ⑥改築、新規開店は!? (checklist, brief text per point, largely recaps earlier chapters).
- "売れ筋商品はワゴン型に並べる" — reconfirms wagon 注目度 advantage over shelf for identical items: "同じ条件の同じ商品でも棚とワゴンでは売れかたに差があるのに気づいただろうか。実はワゴンのほうが売れ筋商品の注目度が高いので、だから売りたい商品や売れ筋商品は棚よりもワゴンに乗せて並べるほうが効率よく売ることができる。" Screenshot shows an アンケート-style 買った商品/欲しかった商品 table: 冷たい飲料67/温かい飲料40, 弁当類57/菓子33, インスタント類36/おでん24, パン類28/中華マン13, 文房具26/日用品10, レトルト類27/雑貨8, 魚介類26/(blank).
- "店の奥に客を入れるレイアウトを" — reiterates funneling customers to store back via sparse/blocked short paths near entrance to force deeper traversal.

### p.62-63 「せっかく雇った社員の能力を遊ばせないようにする」/「ライバル店の存在をどうするか、それも大事な問題」
- Reconfirms: even staff-parameter distribution across branches ("店間で能力差が出ないよう社員能力を均等にする"), veteran-to-new-branch transfer, and "早く育てたい社員は24時間営業" — running a store 24h speeds up staff XP gain but adds operational strain ("ただしベテラン社員といっしょに働かせないと、経営にムリが出るようになる").
- "新店舗を出すときは早めに出す" — "お店だけ建てておけば最小限の維持費で土地をキープできるぞ" — CONFIRMED: simply constructing (not fully staffing/opening) a store lets you claim/reserve land cheaply at minimum upkeep.
- "お客を呼ぶのは値段とサービス" — screenshot "商品別価格を決定して下さい パン類 15%OFF 利益率 38%" confirms per-category (not just per-item or store-wide) pricing granularity exists: 全体(store-wide) / 個別(per-item) / and here also apparently per-category (パン類 as a whole) discount settings.
- "◆値段は利益率で変わる" — "利益率は値段を左右する数値。安売りするなら全体を20%オフにして、それから個別に利益率を変化させよう。ときには赤字覚悟で売ることも必要だ。"

### p.64-67 「困ったときも安心のトラブル110番」 (店舗管理のQ&A)
- Q1: 店内混雑の原因 — レジ担当の能力不足、レジと出入口の近さ、通路の狭さ (3 causes reiterated with detail); "あんまり混んでいるとお客さんが怒ってしまうかも".
- Q2: 特定エリアの棚だけ売れない → shelf/wagon single-direction access + wall-facing/adjacent-fixture blocking (see Notable findings "1ブロックのあき" rule, p.65).
- Q3: ライバル店買収の是非 → only acquire a rival that is in the black (黒字); check via 調査 first; screenshot repeats exact 調査¥600,000 / 買収¥52,721,49(0?) example figures for a 2号店 target.
- Q4: 狭い店内でハマっている客を追い出したい → "つまみ出す" ejection mechanic reconfirmed, with caveat: ejecting a customer already IN the register queue makes them leave WITHOUT PAYING ("レジについた前のお客さんをつまみ出すと、お金を払わずに出ていってしまうので損をすることになってしまうので乱用は禁物"). CONFIRMED new nuance: ejecting a customer who is already at/near the register causes a lost sale, unlike ejecting a merely-wandering customer.
- Q5: 新店舗の広告はどれが効果的 → recommends テレビCM for grand-opening (best single-shot impact), then a monthly rotation of either 飛行船 alone or 新聞広告+ダイレクトメール combo for ongoing upkeep.
- Q6: 優秀な社員を解雇したくない (closing an unprofitable 2号店) → transfer good staff to other stores before closing ("店員の雇用/店員の解雇/店員の異動" menu options shown), keep the closed store's building itself instead of demolishing to save on rebuild costs later.
- Q7: 地価上昇エリアの土地を安く確保したい → build only a small store with register+break room and skip all other interior fixtures to minimize cost while still claiming the land: "ほしい土地を買ったら小規模店を配置。ただしレジと休憩所だけでほかの内装はいっさいなし。もちろん店員もひとりだけだ。こうすれば最小の維持費でほしい土地を自分のものにできるぞ。"
- Q8: 赤字経営+火災や強盗が続く → root cause diagnosed as neglecting 交番/消防署 attraction; fix = attract both immediately.

### p.68-71 「販売管理の質問」(Q&A continued)
- Q: 季節/天候/時間帯による売上差 → see Notable findings (seasonal item swap 2x/year recommendation, rain reduces traffic, night alcohol spike, cold-season nikuman).
- Q: 店外レイアウト(噴水/ベンチ)は売上に関係あるか → "店外のレイアウトはお金をかけるだけではムダではない。店外のレイアウトはお金をかけるだけではなく、お客さんを呼びこむためのスペースなのだ。とくに噴水や観葉植物、ベンチは、配置すればお店の人気度がアップするので積極的に利用するようにしよう。また駐車場を作れば、遠くからのお客さんも利用できるようになるので、結果的に売り上げアップに貢献するようになっているのだ。直接お金を稼がせたいなら自動販売機コーナーを作るといいぞ。" — reconfirms 人気 boost from exterior service items, distinct from 自販機's direct revenue role.
- Q: 社員が休憩室から出てこない → see Notable findings (2-tier break room, stamina-gated).
- Q: 駐車場はどのくらい必要か → see Notable findings (car-horn "ビッビッ" cue, start cheap scale up, 立体駐車場 upkeep expensive).
- Q: 店内が汚い、売上が落ちてきた → "お客さんが買い物をすると、その代わりにお店が汚れていく。これをきれいにするのも店員の大切な仕事。ただし店員の清掃能力が低いうちは、なかなかすばやく掃除しようとしてくれないのだ。しかも店員が成長しきらないうちにお店を大きくしてしまった場合、お客さんが汚すスピードに掃除が追いつかなくなってしまう。こうなるとお店の人気がはた落ち、客足も遠のいていってしまうのだ。" — CONFIRMED: customers dirty the store as a direct side-effect of shopping (this is the definitive statement clarifying the garbled p.25 清掃 definition text); dirtiness directly lowers 人気 and customer traffic if cleaning can't keep pace, especially right after a size upgrade.
- Q: 個人データを見ていると客のわがままに困る → recommends using monthly アンケート (survey) aggregate data instead of chasing individual customer wants; ほしい商品 trends shift with season/customer-mix, re-survey at each season change. Screenshot アンケート table: 買った商品/欲しかった商品 — インスタント類74/おかん(たぶこ)89, 冷凍食品45/たばこ64, 菓子類43/日用品50, 惣菜類32/中華マン41, レトルト類32/冷凍食品(38?).
- Q: 棚やワゴンが空になる、万引きか? → NOT shoplifting — just normal sell-through outpacing low-補充 staff; player CAN manually restock via cursor+select but this stunts staff 補充 growth (see Notable findings).

---

## PDF1 END (33/33 pages transcribed)

---

## PDF2 — 「新人店長実習マニュアル」continued — 第2章 事業拡大編 (cont.) + 第3章 マップ攻略編

### p.72-73 「ライバル店対策の質問」(Q&A continued from PDF1)
- Q: ライバル店に対抗する一番効果的な手 → draw the rival's customers to your store; discount-sale (安売り) most effective; time your own hours to cover the rival's off-hours; profile rival's customer base and undercut with matching stock. Screenshot: 営業方針 "営業時間〈PM0:00~AM4:00〉" "社員ベースアップ率 3%"; 商品価格 "全商品平均利益率 20%" "全体に設定〈20%OFF〉".
- Q: 狙っていた土地にライバル店が出てしまった、諦めきれない → buy out the rival store outright ("資金にものをいわせてライバル店を買い取ってしまおう。そうすれば土地も店舗も一度にプレーヤーのものにすることができる。") Screenshot repeats exact 調査¥600,000 / 買収¥46,721,49(0) figures again for a "2号店" target (same numbers as PDF1 p.53/65 — likely a recurring canonical example screenshot, not a new distinct instance).
- Q: ライバル店の進出を防ぐには (want fewer rival stores in a small town) → surround your own store's location so its exclusion zone blocks nearby rival construction, and take alcohol/tobacco permits early to deny rivals those permits even if they do build nearby.
- Q: ライバル店に対抗するお店の建てかたや経営法 → build your own store near the rival immediately after any rival grand-opening (rival's own sales dip in this period too); use signage/sales; monitor rival's status periodically and adjust policy.
- Q: 追いつめているのになぜかライバル店が撤退しない → CONFIRMED MECHANIC: a chain's HONTEN (本店, main store) will not withdraw/close as long as ANY of its 支店 (branch stores) are still open, even if the honten itself is deep in the red — "支店ではなくて本店なのではないだろうか。もしそうだとしたら、いくらがんばっても無理というものだ。なぜならライバル店はまず支店から撤退していくからだ。いくら本店が赤字状態でも、1軒でも支店がある限り撤退することはない。この場合はまず支店のそばに新店を開設、まず支店を撤退させることから始めよう。" — i.e. branches must be driven out FIRST, in order, before the main store can ever be forced to close.
- Q: ライバル店を撤退させるだけでいいのか、利用できないか → land-value-between-stores trick reconfirmed with an added exact nuance: "ただしライバル店1軒だけでは地価の上昇率もたかがしれている。そこでライバル店を利用するのだ。ライバル店の周りの土地も上昇し、もし2軒の地価上昇に挟まれれば、その部分の地価の上昇率に1軒だけのときよりも格段に大きくなる。" — confirms being sandwiched between 2 stores (even 2 rival stores, or 1 own+1 rival) gives a categorically bigger land-value boost than adjacency to just 1 store, matching PDF1 p.49/54 but adding: "ただしあまり激しくすると、ライバル店が撤退してしまい、町の発展もゆるやかになってしまう。あくまで撤退しない程度の作戦で町を発展させることが大切だ。" — a balance/caution point: pushing too hard causes premature rival withdrawal, which then SLOWS town development (implying rival stores contribute positively to town growth while they exist).

### p.76-84 「新米店長おすすめのお店コレクション」— 8 example store case-studies (ケース No.1-8)
Each entry gives: theme, exact store size/orientation, exact 価格 (construction cost), and screenshots of layout + commentary. All are player-reference "inspiration" layouts, not new confirmed mechanics beyond what's stated, EXCEPT where a mechanic is explicitly asserted in the text (noted below).
- **ケース1「狭いながらも楽しい我が店」編** — 店舗規模・小, サイズ10×10, 価格600万 — small-lot optimization: exterior vending machine + parking lot to compensate for tiny interior; wide aisles despite small size prioritized over cramming goods.
- **ケース2「典型的なコンビニエンスストア」編** — 店舗規模・中, サイズ12×12, 価格1200万 — "generic convenience store" archetype: 3 gondola shelves (ゴンドラ) center-aisle with 雑誌・菓子・乾物 in sequence from entrance; deliberately NO exterior vending machine, to force vending-machine customers inside instead, "自販機を利用するお客さんも店内に引きこんでしまおうというコンセプトで、これにより飲み物以外の商品も売れるようになる" — confirms indoor vs outdoor vending machine placement is a deliberate traffic-shaping choice, not just a revenue add-on.
- **ケース3「郊外の大型スーパーを意識した店」編** — 店舗規模・大, サイズ16×16, 価格1800万 — supermarket-style: large exterior parking rows; store split into two distinct customer-flow halves — 雑貨 customers on left, 食料品 customers on right, kept ENTIRELY separate ("雑貨をほしがるお客さんと食料品をほしがるお客さんの流れを、まったく別に設定していることがある") — confirms customer pathing can be zoned by product-category demand, not just funneled to one loop.
- **ケース4「街道筋で見かける自販機スタンド店」編** — 店舗規模・小, サイズ10×10, 価格600万 — an all-vending-machine "unmanned stand" store concept: NO shelves/wagons at all, no register needed, staff's only job is restocking vending machines + floor cleaning + occasional home delivery (宅配便); text claims monthly sales can exceed ¥5,000,000 with the right location/policy ("月の売り上げが500万以上も夢じゃない").
- **ケース5「サービスと快適さを第一とした優良店」編** — 店舗規模・大, サイズ16×16, 価格1800万 — service-first design: central fountain + houseplants/benches spaced apart from goods so customers don't crowd each other; explicit risk callout that this design might not turn a profit ("実際に開店してみて黒字を出せるかどうかが問題。せめて商品と植物の割合は半々がいいのでは!?").
- **ケース6「風水を利用して客を呼び集める店」編** — 店舗規模・中, サイズ12×12, 価格1200万 — feng-shui theming: fountain (水属性) placed facing the entrance to "attract water=customers" and act as a defensive wall against bad energy from the entrance direction; flavor/theming content, framed by the guide itself as a fun in-universe concept rather than a proven mechanic (no claim of hard numeric effect).
- **ケース7「風水を利用して客の流れをよくする店」編** — 店舗規模・大, サイズ16×16, 価格1800万 — explicitly states the game models 5 elemental attributes for products/fixtures with compatibility/conflict relationships: "5つの属性はそれぞれ相性のいいものと悪いものが決まっている。" Example: イベント商品 (土属性) conflicts with 飲み物コーナー (水属性) and also with 弁当・乾物コーナー (木属性), so placing them adjacent creates a repulsion effect that forces customers into a clockwise loop route. NOTE: This 5-element (木/火/土/金/水) product-attribute system reads as a humor/theming overlay for this "feng shui case study" article rather than a documented hard game mechanic — the guide's own language ("ただしあくまで予定なので、実際は自分でお店をレイアウトして確かめてみてほしい") hedges that this is speculative styling, not a confirmed formula. Flag as LOW CONFIDENCE / possibly-flavor-only, not to be treated as CONFIRMED_OFFICIAL without corroboration elsewhere.
- **ケース8「風水を利用して最もバランスのいい店」編** — 店舗規模・大, サイズ16×16, 価格1800万 — continuation of the feng-shui series; same low-confidence flavor-content caveat applies.

---

## PDF2 — 第3章 マップ攻略編 (Map Strategy Chapter)

### p.85 (chapter title spread)
- "第3章 マップ攻略編 / キミの手であの町を独占しよう" — "全部で3つ用意された個性的なマップ これを全部独占するのがキミの使命だ 経営手腕を総動員して町を独占しよう" — CONFIRMS exactly 3 maps/scenarios exist in the base game.

### p.86-87 「初級···都庁を誘致する」/ STEP1 序盤の戦略(1年目)
- Full detail in Notable findings (Beginner map exact stats, 都庁 auto-build win condition).
- "特選!おすすめ出店ポイント": ①ライバル店のどまん中というのが気になるが、客の入りは折り紙つき。②ライバルの本店から下に位置する交差点。将来的な発展が望める好立地。
- "店員の雇用はバランス良く" — reiterates hiring a high-教育 manager + high-体力 support staffer as ideal starting duo.
- "早めに中規模店へ改築を" — "小規模な店舗では、よほどいい位置に出店しないかぎり赤字経営になる。ここは多少の無理をしてでも、中規模店へ改築してしまおう。経費はかさむむが、しばらくすれば経営は自然と黒字に持ち直すはずです。2年、3年といった長期の期間で見れば、結局は得ることになるのだ。" — CONFIRMED guidance: small stores are usually unprofitable unless location is excellent; recommends proactively upgrading to medium size early despite the up-front remodel cost.
- "攻略㊙テク1 ライバル店を買収しよう" — reiterates rivals always start in a prime downtown/一等地 location, so early buyout while affordable is a viable opening move.

### p.88-89 STEP2 中盤の戦略(2年目~4年目) / STEP3 終盤の戦略(5年目~8年目)
- Full detail in Notable findings (idol event 10,000-visitor recurrence, all-staff-transfer warning, feng-shui-adjacent layout tip).
- "宣伝活動で人気をUP" — "人気値はほっておいても上がっていくが、お客のこない店には宣伝でテコ入れをしてあげよう。" Screenshot: 宣伝方法 "新聞広告 ¥500,000/月 費用合計 ¥600,000/月" (NOTE: this screenshot's per-ad cost framing as "/月" [per month] rather than a flat one-time fee differs from PDF1 p.36's flat "宣伝費" framing — possibly UI shorthand for a recurring campaign rather than contradicting the flat-fee table; flagged for cross-check.)
- "店舗を増やして増収益" — "複数の黒字店舗を造って増益を計ろう。1年ベースで1店舗、4年目の終わりには5店舗あたりが望ましい。" — CONFIRMED pacing guideline: ~1 new store per year, targeting 5 stores by end of year 4.
- "交番誘致で犯罪対策" — reiterates 交番 attraction as the primary countermeasure for mid-game robbery/fire spikes.
- "大規模店への拡大を計る" — for the population-focused Beginner map specifically, large-store expansion is NOT the top priority ("店舗の増大それほど重要ではない"); only recommended if pursuing bigger profit beyond the win condition.
- "経費節減で店をスリム化" — "温冷飲料の中身を季節ごとに替えるといった経費の節減も、立派な増益法のひとつだ." — reiterates seasonal stock rotation as a cost-saving practice.
- "建物誘致で人口を増やす" — caution: 誘致 during late game can accidentally demolish/absorb existing surrounding buildings within its footprint ("誘致は、その空間すべての建築物を巻き込んでしまうので、慎重に行うこと。総人口が減ったら逆効果だ.") — CONFIRMED: 誘致 can reduce total population if it overwrites populated buildings; net population effect isn't automatically positive.

---

### p.92-95 「中級···10店舗建設する」/ STEP1-3
- Full detail in Notable findings (Intermediate map stats/clear condition/pacing).
- "攻略㊙テク4 土地を早めにおさえる" — buy up land early and build minimal small stores on it just to reserve it cheaply (upkeep-minimized land-banking, matches PDF1 p.62's "店だけ建てておけば最小限の維持費で土地をキープ" tactic).
- "イベントで賞金を稼ぐ" — "コンビニ・コンテスト" event: "入賞すると大量の賞金がもらえるコンビニ・コンテストのイベント。発生はほぼランダムに近いが、正直この賞金を当てにしないと中級のクリアは難しい。このイベントに備え、人気や清掃値が高い店舗をひとつは造っておきたい。" — CONFIRMED: a random "コンビニ・コンテスト" (Convenience Store Contest) event exists, awarding large prize money to the best-scoring store (by 人気/清掃 apparently), and beating the Intermediate map is stated to be difficult without winning it.
- "攻略㊙テク5 賞金稼ぎの冴えたやり方" — "いつイベントが起こってもいいように、清掃値などは基本の中でMAXにするのが基本。できれば最高ランクの店員を、1店に集中させるくらい徹底したい。"
- "黒字店を5店舗建設する" — "さしあたっての目標は、黒字店を5店舗建設すること。毎月の収入が500~800万どれくらいになればほぼOKだ。" — CONFIRMED numeric revenue target: ¥5,000,000-¥8,000,000/month per profitable store as a mid-game benchmark.
- "攻略㊙テク6 ライバル店から人材吸収" — "ライバルのお店が撤退すると、辞めた店員も同時にやめてしまう。そこを見計らって店員募集をかけると、その店員たちが応募してくることがある。普通の新人より給料は高いけど、能力値が高くなっているので即戦力になることうけあいだ。" — CONFIRMED mechanic: when a rival store withdraws, its staff become available in the NEXT recruitment pool, at higher wage but higher stats than typical new hires.

### p.96-97 「おたすけQ&A 中級編」/ リプレイ「Fearness!マスミちゃん」
- Q: 新店舗を造ったとたん倒産 → building a 2号店 on a too-tight budget causes bankruptcy; new stores are inherently loss-making at first ("人気値は低く、維持費ばかりを喰う金食い虫").
- Q: 客足は多いのに収入が少ない → check 店員の能力/レイアウト/立地相性 mismatch, OR a rival store opened right next to yours undercutting on price.
- Replay flavor story "Fearness!マスミちゃん" — narrative flavor content, no new mechanical data (character stats shown: 人気100/清掃100/警備100/サービス96 as a hypothetical "ideal" example store state).

### p.98-101 「上級···オーナー評価を★★★★にする」/ STEP1-3
- Full detail in Notable findings (Advanced map stats, 5-metric owner evaluation, 1-rival-no-buyout rule, wage-refusal tech).
- "攻略㊙テク8 経費節減策のあれこれ" — "まずは店員などの人件費。あまりもうからない人数を減らしたり、営業時間を短くするとよいかも。次は商品。薬品などの販売許可は大規模店でない限り取る必要はあまりないぞ。" — suggests 薬品 (medicine) permit ROI is poor except at large stores specifically.
- "攻略㊙テク9 緊急回避!スーパーリセット" — "どうしても消防署の誘致に手が回らない。ライバルが嫌な位置に出店した。そんな時はリセットを押してプレイをやり直そう。きっと展開が変わるはずだ。" — meta/console-reset tip, not a game mechanic.

### p.102-103 「おたすけQ&A 上級編」/ リプレイ「オーナーはつらいよ」
- Q: 住人は多いのにお客が少ない → check 顧客独占率 (customer-monopoly/share rate) — a nearby rival may be siphoning the area's customers even though total population is high.
- Q: 大規模店へ改築できません → "大規模店への改築は、ある程度ゲームが進まないと不可。資金が充分で改築が不可能な場合は、店舗数がこのケースと見てまちがいない。" — CONFIRMED: large-store remodeling is GATED by game progress/story-flag, not just money — even with sufficient funds, you may be blocked from remodeling to 大規模店 until enough stores/progress exist.
- Q: 店員を辞めさせたら募集できなくなった → "クビにした店員。あるいは給料が不満で辞めていった店員は、確かに一時的にゲームから消えます。が、期間をおけば再び店員に応募してくるので大丈夫。店員の能力はブランクにより下がるが、ド新人よりはずっとまし。" — CONFIRMED: fired/quit staff reappear as applicants again after a cooldown period, with somewhat-decayed stats (still better than a fresh hire).
- Replay flavor "オーナーはつらいよ" — narrative; mentions in-fiction a wage-raise demand of exactly "10%" then later "5%" being made by name and refused/accepted for flavor (consistent with the 2-3%-typical / 10%+-excessive framing established earlier).

### p.104-105 「隠しマップで遊ぼう」/ 第4章 title spread
- Full detail in Notable findings (4th hidden map, Saturn-vs-PS shape difference, exact 3-map clear-condition text).

### p.106-109 「店舗データ」
- Full detail in Notable findings (exact 6-store-type dimension table + the PDF1-vs-PDF2 large-store cost/size discrepancy flag).
- "店舗自体には維持費はかからないので、最初から大型店を作ることもできるが商品構成の面で無理がでるので注意しよう。" — CONFIRMED: the store BUILDING itself has zero ongoing upkeep cost (维持费 applies to fixtures/staff/parking etc., not the base building).

### p.110-119 「設備データ」
- Full detail captured in Notable findings (complete fixture stat table: price/attention/upkeep/size/capacity/placement/compatible goods, for every shelf/wagon/case/vending machine/register/service item/parking type in the game).

### p.120-121 「広告データ」
- Full detail captured in Notable findings (exact ad table cross-confirming PDF1, clarifying 実行時 as a fixed monthly calendar slot).

### p.122-125 「商品データ」
- Full detail captured in Notable findings (exact 定価/原価率/利益率 baseline for all ~27 product categories).

### p.126-127 「店員データ」(start)
- Full detail captured in Notable findings (性格=stat-cap system reveal, 能力分岐ポイント growth-slowdown mechanic, 5 sample staff full stat blocks).

### p.128-133 「店員データ」(continued)
- Full detail in Notable findings (~35 total named sample staff across p.126-133, roster listed).

### p.134-143 「顧客データ」
- Full detail in Notable findings (17-field customer archetype schema, ~20 archetype roster with representative rows, wheelchair/crutches accessibility archetypes noted).

### p.22-23 「どんな営業をするのか、営業方針を決定する」
- (See Notable findings for full pricing-mechanic quote, business hours screenshot, and time-of-day demographic wheel.)
- "商品ごとにこまめに変えるのがいい" — "利益率は商品全体を変えるほかに、ひとつずつでも変更することができる。例えば売れ筋商品を高めにすれば利益が上がり、イマイチの商品の利益率を下げればいままでよりも売れるようになるかもしれないのだ。お客さんが少ないときは利益率をわざと下げ、お客さんを呼び寄せるようにしてみよう。"
- "高すぎる販売価格率は逆効果に" — "よくばって高すぎる商品利益率を設定すると、お客さんがほかの店で買い物をするようになってしまう。これではもうけにはならないぞ。"
- 営業方針決定 screenshot fields: "営業時間〈AM10:00~PM6:0〉", "社員ベースアップ率 3%", "給与交渉に応じる はい/いいえ" — confirms a 社員ベースアップ率 (staff base-pay raise rate) % field and a yes/no 給与交渉 (wage negotiation) toggle exist as store-policy settings alongside business hours.

