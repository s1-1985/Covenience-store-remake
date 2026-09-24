# 0140: 客スプライトの配線(タスク#70、アセット統合 第4弾)

## 背景

タスク#69(店員スプライト)のマージ後、ユーザーから次の配線対象として
「客スプライトの配線(推奨)」の選択があった。`assets/raw/customer_v2/
customer/`は白縁除去修正版v2の客パッケージで、21人分の匿名の歩行
スプライト(`customer_01`〜`customer_21`、各4方向×2フェーズ=168枚、
160×160px RGBA、足元基準アンカー(80,154)、タスク#69の店員パッケージと
同一のジオメトリ)を収録する。ソース側のディレクトリ構成は
`sprites/<id>/<direction>_<phase>.png`(キャラクターごとのサブフォルダ)で、
タスク#67〜#69の平坦な`sprites/<id>_<direction>_<phase>.png`とは異なる
ため、`game/assets/customers/`へコピーする際に平坦化した。

タスク#69の店員と異なり、`CustomerState`(`game/scripts/domain/
customer_state.gd`)には識別子的なフィールドが一切存在しない
——`customer_id`(例: `customer-3`、`concurrent-a`、`eject-ui-customer`)
のみを持ち、`reference_sim/conveni_sim/baseline_data.py`の
`CUSTOMER_ARCHETYPES`(21客層、攻略本134〜143ページからCONFIRMED_OFFICIALで
転記済み)のいずれとも紐付いていない。このVertical Sliceには「来店客に
客層を割り当てる」という需要・来店計画メカニクス自体が実装されて
おらず、タスク#68の`InventoryState.catalog_id`のように「既に分かっている
値を配線し直すだけ」の実データは存在しない。

## 決定

### customer_idのハッシュに基づくスプライト割り当て(表示専用、客層とは無関係)

実データの紐付けが一切存在しない以上、タスク#69の「配列内位置」方式は
適用できない(そもそも位置を持つロースターが存在しない)。代わりに、
各`customer_id`文字列のハッシュ値を21で割った余りから`customer_%02d`を
決定的に導出する(`_customer_sprite_id_for_id()`)。これは特定の客層
(`CUSTOMER_ARCHETYPES`)への割り当てを主張するものでは全くなく、単に
同一の客インスタンスが常に同じ見た目で描画されるようにするための、
本プロジェクト独自のREMAKE_BALANCED_DEFAULT表示規約である
——年齢・性別・購買行動などいかなる意味も持たない。

商品を購入する客層から見た目を逆算する(例:たばこ購入客層=成人男性)
といった、より「それらしい」割り当て方法も検討したが、これは未確認の
需要・客層行動を前提とした一段と強い創作になるため採用しなかった
(証拠なき推測の積み増しであり、単純なハッシュ割り当てより誠実さで
劣る)。

### 静止フレーム・向き推定・アンカー配置

タスク#69の店員と全く同じ判断を踏襲する:
- パッケージは歩行の2コマ差分(A/B)のみを収録するため、常にphase "A"を
  使用する(REMAKE_BALANCED_DEFAULT)。
- 画面上の向きは直近の`position`差分から推定する(`_customer_facing_
  direction()`、店員と同一ロジック、客IDごとに独立して記録)。
- manifestの足元アンカー(80,154)/(160,160)を比率化し、既存の
  `_cell_center(position)`にスプライトの足元が来るよう配置する。

## テスト

- `reference_sim`フルスイート735件パス/1件xfail(新規コントラクトテスト
  1件)。この機能も`vertical_slice.json`に新規データフィールドを追加
  しないため、タスク#67/#69と同様コードコメント+テストアサーションで
  REMAKE_BALANCED_DEFAULTタグの3点セットを満たす。`CustomerState`に
  客層関連のフィールドが実際に存在しないことも回帰的にテストで確認する
  (`assertNotIn("archetype", customer_state)`)。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないためCIで
  検証。追加した検証内容:
  - 21種×4方向すべてで実際にテクスチャが読み込めること。
  - `_customer_sprite_id_for_id()`が同一IDに対して決定的であること、
    命名規約(`customer_NN`)に従うこと、空文字列に対してはスプライト
    なしに解決されること。
  - `_customer_facing_direction()`を合成座標で直接演習(タスク#69の
    店員版と同じ4パターン)。

## 対象ファイル

- `game/assets/customers/*.png`(168ファイル、21人×4方向×2フェーズ、
  ソース側のサブフォルダ構成を平坦化して配置)
- `game/scripts/store_view.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 町マップ・建物タイル、メニューUI系5パッケージの配線は今回対象外。
- 歩行アニメーション(A/B切り替え)は未実装——常にphase "A"固定
  (タスク#69と同じ)。
- 客層(`CUSTOMER_ARCHETYPES`)を来店客に実際に割り当てる需要・来店計画
  メカニクス自体の実装は、本タスクのスコープ外(表示層のみ)。将来
  それが実装された場合、このハッシュ割り当ては実際の客層データに
  置き換えられるべき暫定実装である。
- `reference_sim`側への同等ロジックの移植は行っていない
  ——`reference_sim`にはそもそも描画層が存在しない。
- これらのスプライト自体は`CLAUDE.md`の証拠規律上、原作の確認された
  見た目(CONFIRMED_OFFICIAL)ではなく、あくまで本プロジェクト独自の
  新規デザインである(タスク#67〜#69と同じ評価)。
