# 0135: 新規開店時の土地代=地価×4エリア分をchain_expansion_cost_yenへ反映(タスク#65後半)

## 背景

decision 0134と同じ400dpi再確認の過程で、PDF4(第三の攻略本「攻略&データブック」)の
ライバル対策セクション(印刷頁79)に以下の完全な公式ボックスがあることを直接確認した:

「新規開店時の土地代 = 地価（4エリア分）+建物評価額／2（複数の施設を撤去する場合は
合計額の1/2）」

`reference_sim/conveni_sim/remake_land_value.py`の`land_purchase_cost_yen()`は
タスク#60(decision 0129)で既に実装済みだが、その`area_count`引数は「店舗バリアントの
`total_area_tiles`から取るべき」という類推(CLAUDE.md優先順位2、店舗サイズによって
25〜256タイルまで変動する)に基づいていた。今回発見した本文は、**「新規出店」という
文脈に限っては土地代の面積係数が店舗サイズによらず固定の"4エリア分"である**ことを
直接明記しており、既存の類推とは異なる、より具体的で確認度の高い数値を与える。

さらに調査したところ、`game/scripts/vertical_slice_simulation.gd`の
`chain_expansion_cost_yen()`(タスク#30、複数店舗展開の抽象的コスト)は、実は
`land_purchase_cost_yen()`を一度も呼んでおらず、`current_land_price_yen()`(面積1相当の
単価そのもの)をそのまま費用としていた——つまり暗黙に面積係数×1で計算していたことが
判明した。今回の発見は、この既存ギャップ(decision 0129が「`game/`にはまだ配線先の
土地購入メカニクスがない」としていた箇所)にちょうど当てはまる具体的な配線先そのもの
だった。

## 決定

### `reference_sim/conveni_sim/remake_land_value.py`

`NEW_BRANCH_LAND_AREA_COUNT = 4`(CONFIRMED_OFFICIAL)を追加。`land_purchase_cost_yen()`
自体は既に`area_count`を呼び出し側から受け取る汎用設計だったため関数自体の変更は不要。
docstringを更新し、「新規出店」文脈ではこの固定4を使うべきこと、既存の
`total_area_tiles`類推は他の(まだ存在しない)土地購入文脈に対してのみ有効である可能性が
残ることを明記した。

### `game/scripts/vertical_slice_simulation.gd`

`NEW_BRANCH_LAND_AREA_COUNT := 4`定数を追加し、`chain_expansion_cost_yen()`が
`current_land_price_yen(...)`の結果にこの係数を掛けるよう修正した。「+建物評価額／2」の
項は適用していない——`try_expand_chain()`は特定の土地・既存建物を指定しない抽象的な
経済アクション(decision 0099)のままであり、評価すべき具体的な建物が存在しないため。

## テスト

- `test_remake_land_value.py`: `NEW_BRANCH_LAND_AREA_COUNT == 4`の確認と、
  `land_purchase_cost_yen(..., NEW_BRANCH_LAND_AREA_COUNT, ...)`が単位面積コストの
  ちょうど4倍になることを検証する新規テスト。
- `headless_smoke.gd`: 既存のチェーン展開シナリオに、`chain_expansion_cost_yen()`が
  `LandValuePolicy.current_land_price_yen(...) × NEW_BRANCH_LAND_AREA_COUNT`と一致する
  ことを検証するアサーションを追加。以降のコスト額そのものへの依存(現金をちょうど
  コスト分だけ設定する等)は既に動的取得のため変更不要だった。
- `reference_sim`フルスイート731件パス/1件xfail(既存の無関係なxfail1件は変化なし)。

## 対象ファイル

- `reference_sim/conveni_sim/remake_land_value.py`
- `reference_sim/tests/test_remake_land_value.py`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/headless_smoke.gd`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 「建物評価額／2」の建物撤去費用項目は、具体的な土地・建物が存在する購入フローが
  `game/`に実装されるまで対象外のまま(decision 0129/0060と同じ境界)。
- `total_area_tiles`ベースの類推自体は撤回していない——「新規出店」以外の土地購入文脈
  (例: 既存店舗の移転)に将来使える可能性がある限り、`remake_land_value.py`から
  削除していない。
