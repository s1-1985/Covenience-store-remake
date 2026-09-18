# 0094: `game/`(Godot)に広告宣伝を実装する(タスク#25の第3・4段、タスク完了)

## 背景

タスク#25の最後の項目、広告宣伝を実装した。当初は什器購入/許可・商品仕入れと同様に
「必要なデータを`baseline_data.py`から移植し、Godot側に新規実装する」だけの作業だと
想定していたが、実際に調べたところ`reference_sim/conveni_sim/promotion.py`に
`PromotionScheduler`/`StorePopularityRuntime`/`apply_confirmed_triggered_promotion`
という、広告宣伝の予約・発火・人気度反映・課金タイミングまで含めた
evidence-safeな実装が**既に完成した状態で**存在していた。今回はこれをそのまま
Godotへ忠実に移植した。

### `reference_sim`から判明した重要な事実

`promotion.py`のコメント・実装から、以下が確定していることが分かった:

- `trigger_day`/`trigger_hour`は「購入から何日後か」という相対値ではなく、
  **月内の代表日(1〜4日目)・時刻という絶対値**である
  (`PromotionMoment.day`は1〜4の範囲で検証される)。
- 予約は「予約する月と発火する月が一致していること」「予約時点が発火時刻以前
  であること」が条件で、これを満たさない予約は`PromotionScheduler.schedule()`が
  明示的に拒否する("scheduling after the known event time is unresolved"/
  "cross-month advance booking is unresolved")。
- 費用は予約時ではなく**発火時にのみ**課金される
  (`apply_confirmed_triggered_promotion`、V03動画の「day-2 10:00のイベント発火と
  同時に現金がちょうど10万円減る」という直接観測に基づく)。
- 人気度には上限100が存在し、`min(100, before + gain)`で加算される。
- 同じ広告手法は月に1回までしか予約できない(`(year, month, promotion_id)`で
  重複を拒否)。
- 人気度の低下(店舗評価が星3以下だと日々効果が薄れる)という条件自体は
  確定しているが、減衰の具体的な数値式は`reference_sim`自身も未解決のまま
  残している。

これらは全て`reference_sim`側で既に整理済みだったため、本実装は新たな証拠解釈を
行わず、既存の`promotion.py`の設計をそのままGodotのGDScriptに置き換えただけである。

## 決定

### 実装した内容

- `vertical_slice_simulation.gd`に`popularity: int`(0開始、新規開店時の初期値は
  未確定のため0という最も自然な値を採用)、`_promotion_catalog`/
  `_promotions_used_this_month`/`_scheduled_promotions`を追加。
- `try_purchase_promotion(promotion_id) -> bool`: 現在の代表月内日
  (`_days_completed_this_month + 1`)・時刻(`minute_of_day / 60`)が、
  そのカタログエントリの`trigger_day`/`trigger_hour`以前であり、かつ今月
  まだこの広告手法を使っていない場合のみ予約を受け付ける。この時点では
  課金しない。
- `_fire_due_promotions()`: `_advance_minute_of_day()`から毎tick呼ばれ、
  現在の代表月内日・時刻が予約の発火時刻に達した広告を発火させる。
  日境界処理(`_handle_day_boundary`)より**前**に呼ぶことで、月最終日の
  最後のtickで日境界と発火時刻がちょうど重なるケースでも、月が切り替わる
  前の正しい「月内日」で判定できるようにしている。
- `_fire_promotion()`: 費用を`economy.record_explicit_expense()`で計上し、
  `popularity`を`min(100, popularity + popularity_gain)`で更新する。
- `_settle_month_end()`で`_promotions_used_this_month`をクリアし、
  翌月に同じ広告手法を再び予約できるようにする。
- `data/vertical_slice.json`(`schema_version`を9→10に更新)に`promotions`
  セクションを追加。ダイレクトメール(¥100,000/+12/2日目10時)・
  新聞広告(¥500,000/+20/2日目7時)・飛行船(¥1,000,000/+40/3日目15時)・
  ラジオ(¥3,000,000/+60/1日目17時)・テレビ(¥5,000,000/+90/1日目19時)の
  5種、いずれも`reference_sim`の`PROMOTIONS`から確定値のまま移植。

### 何を発明していないか

- 人気度の日次減衰(店舗評価ランクが低いと効果が薄れる)は実装していない。
  `reference_sim`自身がこの数値式を未解決としているため、Godot側でも
  一切減衰させない(人気度は単調増加のみ)。
- 全店舗共通で人気度が上がるという`reference_sim`の仕様(`apply_promotion`が
  複数`store_id`に同時適用する設計)は、このvertical sliceが単一店舗しか
  扱わないため単純化されている(店舗が1つしかないので実質的に等価)。
- 新規開店時の人気度初期値(0)は確定情報ではなく、最も自然な解釈として
  採用した推測である。

## 影響

- `game/scripts/vertical_slice_simulation.gd`: `popularity`/`_promotion_catalog`/
  `_promotions_used_this_month`/`_scheduled_promotions`フィールド、
  `try_purchase_promotion`/`_fire_due_promotions`/`_fire_promotion`メソッドを追加。
  `_advance_minute_of_day()`が日境界処理の前に`_fire_due_promotions()`を呼ぶよう
  変更。`_settle_month_end()`が`_promotions_used_this_month`をクリアするよう変更。
  `_require_config()`が`promotions`キーと各エントリの必須フィールドを検証する
  よう変更。`schema_version`要求を10に更新。
- `game/data/vertical_slice.json`: 前述のとおり`promotions`セクションを追加。
- `game/scripts/headless_smoke.gd`: 未知の広告ID拒否、予約時に課金されないこと、
  同月内の重複予約拒否、発火時の人気度加算とコスト計上の正確性、発火後の
  イベントログ記録、発火時刻を過ぎた予約の拒否を検証するテストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 本機能の存在と
  `reference_sim`由来の確定タイミング・数値であることを検証する新規contract
  テストを追加。

## タスク#25の完了

什器購入(決定書0092)・許可/商品仕入れ(決定書0093)・広告宣伝(本決定書)の
3コミットで、タスク#25「什器購入・商品仕入れ・許可・広告システムをGodotに実装」を
完了とする。
