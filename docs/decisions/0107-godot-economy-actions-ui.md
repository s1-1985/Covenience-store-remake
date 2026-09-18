# 0107: `game/`(Godot)の経済アクションをUIに接続(タスク#38)

## 背景

ユーザーから「前回『UIボタンが無いからゲームとして動くレベルではない』と
言われたが、現状の進捗率はどれくらいか」という質問を受け、実際に調査した
ところ、タスク#35〜#37でHUD表示・同時複数顧客・サンプルレイアウト読み込みを
追加した後も、`vertical_slice_simulation.gd`が実装済みの主要な経済アクション
6つが**一切UIから呼べないまま**だったことが判明した:

- 什器の購入(`try_purchase_fixture`)
- 許可証の取得(`try_purchase_permit`)
- 商品の仕入れ(`try_procure_product`)
- 広告の出稿(`try_purchase_promotion`)
- チェーン店舗の拡大(`try_expand_chain`)
- 明示的な補充(`apply_explicit_restock`)

これらは`headless_smoke.gd`からしか呼ばれておらず、プレイヤーは実際には
何も買えない・仕入れられない・広告を打てない・店を増やせない状態だった。
これが「コンビニ経営ゲームとして動くレベル」に対する最大のボトルネックと
判断し、着手した。

## 決定

### 6つのアクションすべてをHUDに接続

`main.tscn`のSTORE STATUSパネルに「Economy actions」セクションを新設し、
各アクションにOptionButton(該当する場合)+ Buttonのペアを追加した。
`main.gd`はconfigの各カタログ(`fixture_catalog`/`permits`/
`product_catalog`/`promotions`)からOptionButtonの選択肢を構築し、対応する
`try_*`/`apply_explicit_restock`関数を呼ぶ。シミュレーション側のロジックは
一切変更していない(既存の検証済み関数をそのまま呼ぶだけ)。

### 什器購入は既存の「タップで配置」フローを再利用

新しい什器を置くUIは、既存の什器移動(relocate)が使っている
`store_view.fixture_relocation_requested`シグナル+タップ操作をそのまま
再利用した。「Buy fixture」ボタンを押すと`store_view.selected_fixture_id`に
`"__new:" + catalog_id`という専用プレフィックス付きの値をセットし(既存の
什器IDとは絶対に衝突しない)、次にプレイヤーが空きセルをタップすると
`_on_fixture_relocation_requested`がこのプレフィックスを検出して新規購入
処理に分岐する。新しい入力モードを追加する必要がなかった。

### 什器のinteraction_subcellは既存の配置慣習から自動導出

カタログには什器の footprint しか記録されておらず、interaction_subcell
(客・スタッフが対話するセル)のデータは無い。既存データを見ると、どの
什器もinteraction_subcellはfootprintの外側1マスに置かれている(例:
陳列棚はfootprintの直前1マス上)。この慣習に従い、`_find_open_interaction_
cell()`がfootprintの上下左右4方向を順に試し、最初に見つかった「現在
歩行可能なセル」を使う。2回目のタップを要求せず、4方向すべて塞がっている
場合は購入を諦める(原作の正確な配置ルールを主張するものではなく、UI上の
利便性のための選択)。

### レイアウト編集エリアはスクロール可能に変更

タスク#35〜38で追加したラベル・ボタン群により、固定サイズのパネルには
収まらなくなったため、`UI/Panel/Margin/VBox`を`UI/Panel/Margin/Scroll/VBox`
(新設のScrollContainer配下)に変更した。`main.gd`の全`@onready`パスと
`headless_smoke.gd`の構造チェックのノードパスを同期した。

### 補充(restock)のコスト・数量

`apply_explicit_restock`は数量・単価を呼び出し側が指定する低レベルAPIの
ため、UIでは「その商品の`initial_stock_units`と同じ数量を、
`restock_unit_cost_yen`単価で」補充する、という単純な既定値を採用した
(原作の正確な発注ロット数の主張ではなく、UIの既定値としての選択)。

## テスト

- `headless_smoke.gd`: 既存の巨大シナリオに影響を与えないことを確認した
  上で、新規に**実際に`main.tscn`をシーンツリーに追加する**テストブロックを
  追加した(このファイルの他の箇所は`vertical_slice_simulation.gd`を直接
  操作するのみで、`main.gd`自体をテストしていなかったため、今回は`@onready`
  束縛の解決を要するUI層のロジックを検証する必要があった)。什器購入→
  許可証購入→什器購入→商品仕入れ→補充→広告購入→チェーン拡大の一連の
  流れをエンドツーエンドで検証。734ステップでPASS(Godot 4.3公式バイナリ)。
- Xvfb + 実Godotバイナリで`main.tscn`を実際にレンダリングし、スクロール前後
  両方のスクリーンショットで新しいUI要素(什器カタログの選択肢と価格表示等)
  が正しく表示されることを目視確認。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_economy_actions_are_reachable_from_the_ui_not_only_headless_smoke`
  を追加し、上記の設計をフィールド単位で検証。フルスイート654件
  (xfail 1件)全てPASS。

## 実装ファイル

- `game/scenes/main.tscn`: ScrollContainerでVBoxをラップ、Economy actions
  セクション(12ノード)を追加。
- `game/scripts/main.gd`: 上記UIの配線、`_find_open_interaction_cell()`、
  各種OptionButton母集団の管理。
- `game/scripts/headless_smoke.gd`: 構造チェックのノードパス更新、シーン
  ツリーに実際に入る新規テストブロックを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テスト
  追加。

## 明示的に対象外とした限界

- 什器の配置は依然として単一タップ+自動導出のinteraction_subcellであり、
  原作の正確な配置UIを再現するものではない。
- 補充の数量・発注ロジックはUIの単純な既定値であり、原作の正確な発注
  フローではない。
- 什器attention差別化(3.2節最後の項目)は今回も対象外。
- 店舗サイズの複数選択(小/中/大)や2店舗目の実シミュレーションは、依然
  として`try_expand_chain()`の抽象的な数字上昇のみで、実際の2店舗目は
  シミュレートされない(タスク#30の既存の割り切り、変更なし)。
