# 0113: `customer_share_percent`を月次で再計算するよう配線(タスク#44)

## 背景

タスク#43の調査で見つかった2つの優先順位判断待ち候補のうち、ユーザーが
「顧客シェア式の統合を進める」を選択した。

`game/data/vertical_slice.json`の`demand.customer_share_percent`は、
これまで固定の設定値(50.0、REMAKE_BALANCED_DEFAULT)のままで、一度も
再計算されていなかった。一方`reference_sim/conveni_sim/remake_customer_
share.py`には、`popularity`/`service`/`cleaning`/`security`/
`assortment_product_ids`/`opening_minutes_per_day`の6要素から0-100の
シェアスコアを算出する`compute_customer_share_percent()`が既に実装済み
(REMAKE_BALANCED_DEFAULTタグ済み、攻略本は要素の存在は確認しているが
数式は非公開であることを明記)。

さらに調査の過程で、`popularity`(広告等で上昇する人気度、0-100)が
`snapshot()`(UI表示)とセーブ/ロード以外のどこにも使われておらず、
客数シミュレーションに一切影響していないという、それ自体が「確認済みだが
配線されていないデータ」であることが判明した。

## 決定

### `CustomerShare`(新規、`remake_customer_share.py`の移植)

`game/scripts/domain/customer_share.gd`を新設し、
`compute_customer_share_percent(popularity, service_value, cleaning_value,
security_value, assortment_product_count, opening_minutes_per_day) ->
int`を実装。6つの重み(POPULARITY_WEIGHT=0.30/SERVICE_WEIGHT=0.25/
CLEANING_WEIGHT=0.15/SECURITY_WEIGHT=0.10/ASSORTMENT_WEIGHT=0.10/
HOURS_WEIGHT=0.10、合計1.0)と`ASSORTMENT_SATURATION_PRODUCT_COUNT=20`
は`remake_customer_share.py`の値をそのまま転記した。

**意図的に移植しなかった部分**: Python版が持つ`weather`/
`competing_store_ids`による乗算的な希釈・ペナルティ、および「未知の
要素は除外して残りを再正規化する」分岐は、このGodotクライアントでは
移植していない。理由は2つ:
1. `demand_policy.gd`が既に(タスク#27以前から)同じ`RIVAL_DILUTION_
   PER_COMPETITOR`/`MAX_RIVAL_DILUTION`定数を来店客数の見積もり全体に
   適用済みであり、シェアスコア側にも同じ天候・ライバル希釈を重ねて
   適用すると二重計上になる。
2. このクライアントの呼び出し元は常に6要素全てを把握済みであり
   (popularity/service_value/cleaning_value/security_value/在庫商品数/
   営業時間は毎月必ず計算済み)、「未知の要素」が実際に発生するケースが
   存在しないため、その分岐を移植する必要がない。

この2点はファイル冒頭のコメントに明記した。

### `VerticalSliceSimulation._evaluate_store_rating()`への配線

`service_value`/`security_value`/`cleaning_value`(タスク#27で既に月次
計算済み)を`CustomerShare.compute_customer_share_percent()`にそのまま
渡し、追加で`popularity`(既存フィールド、これまで未配線)、
`inventory.products.size()`(現在店舗に並んでいる商品の種類数、
品揃えの広さの直接的な代理指標)、`demand.opening_minutes_per_day`
(既存の確認済み設定値)を渡す。戻り値で`demand.customer_share_percent`
を上書きする。これにより、`demand.customer_share_percent`は「初期値の
まま固定」から「毎月の実績を反映して変動する」値になった。

`service_value`/`cleaning_value`/`security_value`はこのクライアント側で
0-100の範囲に収まる保証がないため(`store_value.gd`の出力値は理論上
100を超えうる)、`CustomerShare`側で0-100にクランプする。これは新しい
上限を発明したのではなく、`store_rating.gd`のCONFIRMED_OFFICIALな
昇格/降格しきい値表がこれら3値を「およそ0-100スケール」として扱っている
既存の事実(例: 5つ星への昇格条件`min_service: 100`)を再利用したもの。

### `vertical_slice.json`の`demand.evidence_note`更新

`customer_share_percent`の設定値が「シナリオ開始時点の初期値としてのみ
使われ、最初の月次評価以降は上書きされる」ことを明記した。

## テスト

- `headless_smoke.gd`: `CustomerShare.compute_customer_share_percent()`の
  直接呼び出しによる単体テスト3件(全要素最大で100、全要素最小で0、
  service_valueが100を超える場合に100へクランプされること)を追加。
  既存の月次レーティングテストシナリオ(`service_value=17.0`/
  `cleaning_value=51.0`/`security_value=57.0`/商品2種/
  `opening_minutes_per_day=960`)に、期待される`customer_share_percent`
  (手計算で25)を検証するアサーションを追加。Godot 4.3公式バイナリで
  734ステップ変化なくPASS(メインの長時間シナリオでは月末評価に
  到達しないため無影響)。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_customer_share_percent_is_wired_into_monthly_store_rating`を
  追加。6つの重み・`ASSORTMENT_SATURATION_PRODUCT_COUNT`・
  `FULL_DAY_MINUTES`が`remake_customer_share.py`の実際の値と一致する
  ことをPython側から直接検証し、重みの合計が1.0であること、
  `weather`/`rival`関連の定数を意図的に移植していないこと、
  `VerticalSliceSimulation`の実際の月次評価処理に配線されていること、
  `evidence_note`が更新されていることを検証する。フルスイート658件
  (新規テスト含む、xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/domain/customer_share.gd`(新規): `CustomerShare`。
- `game/scripts/vertical_slice_simulation.gd`: `CustomerShareScript`の
  preload、`_customer_share`フィールド、月次レーティング評価への配線。
- `game/data/vertical_slice.json`: `demand.evidence_note`を更新。
- `game/scripts/headless_smoke.gd`: 単体テストとレーティングシナリオへの
  アサーションを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- 天候・ライバル希釈をシェアスコア側にも適用することは、二重計上を
  避けるため意図的に対象外とした(`demand_policy.gd`側の既存の適用箇所を
  維持)。
- 品揃えの広さは「現在店舗に並んでいる商品の種類数」という直接的な代理
  指標を採用しており、`ASSORTMENT_SATURATION_PRODUCT_COUNT=20`という
  飽和点自体は`remake_customer_share.py`側で既にREMAKE_BALANCED_DEFAULT
  としてタグ付け済みの値をそのまま再利用しているだけで、新たな数値を
  発明していない。
