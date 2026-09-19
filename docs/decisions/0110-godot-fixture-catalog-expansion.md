# 0110: `game/`(Godot)の什器カタログを45種類中35種類へ拡充(タスク#41)

## 背景

PR #211(タスク#40、replenishment_skill配線)のマージ後、引き続き
「新規発明より配線待ちの確認済みロジックを優先する」方針で次候補を探した。
`reference_sim/conveni_sim/baseline_data.py`の`FIXTURES`には攻略本の
DATA LIST什器表からtranscribeされたCONFIRMED_OFFICIALな什器が45種類
存在するが、`vertical_slice.json`の`fixture_catalog`にはタスク#32
(`small_ambient_shelf`/`small_tobacco_vending`)とタスク#34(駐車場3種)
で移植した8種類のみが存在していた。`try_purchase_fixture`/`main.gd`の
`fixture_catalog_option`はどちらも既に`catalog_id`に対して完全に汎用的な
実装であり、`store_view.gd`の描画も`kind`が`"checkout"`/`"amenity"`/
`"parking"`以外なら既定の青色「SHELF」表示にフォールバックする(タスク#34の
駐車場分岐追加時に確認済みの既存挙動)ため、`kind: "shelf"`として追加する
限りコード変更は一切不要と判断した。

## 決定

### 45種類中27種類を新規に`fixture_catalog`へ追加(`kind: "shelf"`)

常温/冷蔵/冷凍の棚・ワゴン各サイズ、ホットドリンクケース/おでんケース/
中華まんケース、イベント什器、たばこ/コールド/ホット&コールド自販機の
大型版を追加した。各エントリは`footprint_tiles`/`purchase_price_yen`/
`maintenance_yen_per_day`を`reference_sim`から直接転記した
(全てCONFIRMED_OFFICIAL、攻略本のDATA LIST什器表)。`capacity`
(什器ごとの在庫収容上限)と`compatible_product_categories`(什器ごとの
仕入れ可能カテゴリ)も`reference_sim`側では確認済みだが、タスク#39で
商品側の`compatible_fixtures_text`を未消費のまま残したのと同じ理由
(どの棚にも任意の商品を仕入れられる、という既存の緩い挙動を変えない
ため)、今回もカタログのフィールドとしては追加していない。

`large_tobacco_vending`のみ、既存の`small_tobacco_vending`の前例に倣い
`required_permit_id: "tobacco"`を付けた(たばこ専用什器という性質への
このクライアント独自のゲーティング判断であり、攻略本が「什器の所有自体に
許可証を要求する」と述べているわけではない、という既存の免責と同一)。

### 45種類中10種類を意図的に対象外とした

以下の10種類は、このクライアントに存在しないメカニクスに対応する什器
であり、単純なデータ移植では済まないため除外した:

- `register_1`〜`register_4`(レジ4種): このクライアントは単一レジ
  (`checkout_fixture_id`固定・単一`_checkout_queue`)しか実装しておらず、
  複数レジの同時運用・客の振り分けは一切シミュレートされない。第2レジを
  「買える」ようにしても実際には機能しない(誤解を招く)ため対象外。
- `copier_a`/`copier_b`(コピー機2種): コピーサービスというメカニクス
  自体が未実装のため対象外。
- `indoor_dispenser`(キャッシュディスペンサー): タスク#39で商品側の
  `cash`カテゴリを除外したのと同じATM類似メカニクスに対応する什器で、
  同じ理由で対象外。
- `break_room_1`/`break_room_2`(休憩室2種): スタッフの休憩・スタミナ
  回復メカニクスが未実装のため対象外。
- `vending_machine`: `reference_sim`側でも`sale_mode='self_service_
  candidate'`のみで、footprint/価格/維持費など主要フィールドが全て
  `None`(未確認)の不完全なプレースホルダーエントリであり、移植できる
  確定データ自体が存在しない。

## テスト

- `headless_smoke.gd`: Godot 4.3公式バイナリで実行し、既存の734ステップが
  変化なくPASSすることを確認(`main.gd`/`store_view.gd`ともに変更なしの
  ため無影響)。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_shelf_fixture_catalog_expansion_ports_confirmed_reference_sim_data`
  を追加。10種類の除外対象が実際にカタログに含まれないこと、それ以外の
  未移植分が過不足なく追加されていること、追加された全エントリが
  `reference_sim`の`FIXTURES`と`footprint_tiles`/`purchase_price_yen`/
  `maintenance_yen_per_day`単位で一致すること、`large_tobacco_vending`
  以外に`required_permit_id`が付与されていないこと、`store_view.gd`が
  既定の"SHELF"フォールバック表示を保持していること(新しい描画分岐を
  追加していないことの確認)を検証する。フルスイート657件(新規テスト
  含む、xfail 1件)全てPASS。

## 実装ファイル

- `game/data/vertical_slice.json`: `fixture_catalog`に27エントリを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- 上記10種類(レジ4種・コピー機2種・キャッシュディスペンサー・休憩室2種・
  データ不完全なvending_machine)は今回も対象外。それぞれ対応する
  メカニクス(複数レジ運用・コピーサービス・ATM・スタッフ休憩)が実装
  されない限り、意味のある形では移植できない。
- `capacity`(什器ごとの在庫収容上限)と`compatible_product_categories`
  (仕入れ可否)は確認済みデータのまま未消費。任意の棚にどの商品でも
  仕入れられる現状の緩い挙動、および在庫上限が事実上無制限という現状の
  挙動は変更していない。
