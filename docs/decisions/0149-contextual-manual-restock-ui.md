# 0149: 手動補充UIを「棚選択→在庫不足で有効化」の文脈依存型に作り直す(タスク#79)

## 背景

タスク#78(PR #254)がマージされた後、ユーザーから次の指示候補として提示した
「操作フローの改善」の説明文に「商品仕入れ」を含めたところ、ユーザーから2件目の
再現忠実性への指摘を受けた:「商品仕入れとか書いてあるけど、実際の初代ザ・コンビニ
には商品の仕入れとかなかったはずだけど？どういうこと？」

調査の結果:

- 店員による**自律的な**補充(`補充`スキル)はCONFIRMED-COMMUNITYで、
  `docs/decisions/0089-godot-non-checkout-staff-restock-task-assignment.md`
  で実装済み。
- 一方、**プレイヤー自身が任意に押せる**補充ボタンの存在は、
  `docs/research/inventory-restock-boundary-2026-09-05.md`セクション9で
  明示的に`manual_restock_action: UNKNOWN`と記録されており、既存資料では
  未確定のままだった。
- それにもかかわらず、`main.gd`の既存UI(タスク#38、決定書0107)は「任意の
  在庫商品を常時選べるドロップダウン+補充ボタン」という、原作に存在するとは
  一度も確認されていない一般的なUIとして実装されていた。

この事実をそのままユーザーに提示したところ、ユーザーから初代PS版への直接プレイ
経験に基づく新証言を得た:

> 対象の商品棚を選択し、中身が減っていると補充のコマンドが出て、プレイヤーが
> 任意で補充できたはず

これはCLAUDE.mdのevidence tier(1)(recovered evidence: direct-play
observation)に該当するCONFIRMED_COMMUNITY相当の一次証言であり、
`docs/research/inventory-restock-boundary-2026-09-05.md`に追記した
(2026-09-24付)。この証言に基づき、UIを「対象棚を選択→在庫が閾値以下の場合のみ
補充コマンドが有効化される」という文脈依存型に作り直した。

## 決定

### 補充ボタンを常時有効の商品ピッカーから、選択中什器への文脈依存アクションへ変更

- `game/scripts/main.gd`に`_selected_fixture_restock_target()`を新設。
  `store_view.selected_fixture()`(什器移動/入れ替え/売却/回転が既に使っている
  同じ選択状態)で選ばれている什器の上の商品を`store_view._product_on_fixture()`
  で取得し、その`stock_units`が
  `simulation._restock_trigger_stock_units_at_or_below`
  (決定書0089で導入済みの、店員自動補充タスクが使っているのと**同じ**閾値。
  この証言のために新しい閾値を逆算・発明してはいない)以下の場合にのみその商品を
  返す。什器が未選択、対象什器に商品が無い、在庫が閾値超過、のいずれかなら`null`。
- `_on_restock_pressed()`はこのターゲットが`null`なら「Select a shelf whose
  stock is running low to restock it」と案内して何もしない。ターゲットがあれば
  従来通り`apply_explicit_restock()`を呼ぶ(数量・単価の既定値ロジックは
  タスク#38からのREMAKE_BALANCED_DEFAULTのまま変更していない)。
- `_refresh_ui()`で`restock_button.disabled`をこのターゲットの有無に応じて
  切り替え、有効時はボタンのテキストに対象商品名と在庫数を表示するようにした
  (`Restock <product_id> (stock: N)`)。
- `game/scenes/main.tscn`から常時表示の`RestockProductOption`
  (OptionButton)ノードを削除し、`RestockButton`に`disabled = true`の初期値を
  追加した。
- `game/scripts/main.gd`から、この`RestockProductOption`を管理していた
  `_refresh_restock_product_option()`/`_restock_product_ids`/その全呼び出し
  箇所(`_ready()`/`_on_reset_pressed()`/`_on_sell_fixture_pressed()`/
  `_on_load_sample_layout_pressed()`/`_on_procure_product_pressed()`/
  `_on_load_pressed()`)を削除した。

### 研究ノートへの追記

`docs/research/inventory-restock-boundary-2026-09-05.md`セクション9に
2026-09-24付の追記を追加し、上記のユーザー証言全文と、この証言によって
`manual_restock_action`がUNKNOWNから「存在する」へ格上げされたこと、ただし
閾値の正確な値・発注ロット数・コマンドの正確なUI配置は依然未確定であることを
明記した。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  - `test_manual_restock_is_contextual_to_the_selected_low_stock_fixture`
    (新規)で、研究ノートへの追記内容・`main.tscn`から`RestockProductOption`
    が消えたこと・`_selected_fixture_restock_target()`の存在と閾値の再利用・
    `REMAKE_BALANCED_DEFAULT`ではなく`CONFIRMED_COMMUNITY`タグと決定書0089への
    参照・`headless_smoke.gd`側の文脈依存テストの存在、をフィールド単位で検証。
  - `test_economy_actions_are_reachable_from_the_ui_not_only_headless_smoke`:
    ノード一覧から`RestockProductOption`を削除し、
    `apply_explicit_restock()`呼び出し文字列を新しい引数式
    (`product.product_id`)に更新。
  - フルスイート744件(xfail 1件)全てPASS。
- `game/scripts/headless_smoke.gd`の`economy_ui_scene`シナリオに、
  (a) 在庫が閾値より多い間は`_selected_fixture_restock_target()`が`null`を
  返し、その状態で補充を押しても課金されないこと、(b) 在庫を閾値まで下げると
  ターゲットが選択中什器の商品に解決されること、(c) 実際に補充した結果の在庫・
  課金額が従来通り`initial_stock_units`/`restock_unit_cost_yen`ベースである
  こと、を検証するテストを追加。

## 実装ファイル

- `game/scripts/main.gd`
- `game/scenes/main.tscn`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `docs/research/inventory-restock-boundary-2026-09-05.md`

## 明示的に対象外とした限界

- 在庫閾値そのもの(`restock_trigger_stock_units_at_or_below`、現在の
  ベース設定では`0`)は決定書0089由来のPROVISIONAL値のままで、今回の証言は
  「対象を選択したときにコマンドが出る」という**構造**の裏付けであり、
  「何個以下で出るか」という**具体的な数値**の裏付けではない。この数値は
  引き続きPROVISIONALとして扱う。
- 発注ロット数・コストの既定値ロジック(`initial_stock_units`個ぶん、
  `restock_unit_cost_yen`単価)は変更していない。これは引き続き
  REMAKE_BALANCED_DEFAULT(タスク#38)。
- この証言はまだ攻略本/wikiの一次資料で独立に裏付けられていない。今後の
  調査で矛盾する一次資料が見つかった場合は、この実装を再修正する前提で
  CONFIRMED_COMMUNITY(暫定)として扱う。
