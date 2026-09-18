# 0092: `game/`(Godot)に什器購入を実装する(タスク#25の第1段)

## 背景

タスク#25「什器購入・商品仕入れ・許可・広告システムをGodotに実装」は、名前の通り
4つの独立したシステムを束ねている。それぞれが単独でも決定書1本分の規模を持つため、
これまでのタスク(#21〜#24)と同じ粒度を保つべく、4つを1つのコミットにまとめず
順番に実装することにした。本決定書はそのうち最初の1つ、**什器購入**を扱う。

`game/`(Godot vertical slice)の`fixtures`はこれまで、開店時から固定で存在する
棚(shelf)とレジ(checkout)のみで、プレイ中に新しい什器を追加する手段が
存在しなかった。一方`reference_sim/conveni_sim/baseline_data.py`の`FIXTURES`には、
観葉植物・ベンチ・噴水などの什器について、`CONFIRMED_OFFICIAL`(攻略本明記)の
購入価格・維持費・サービス値ボーナスが既に揃っている。

## 決定

### 実装した内容

- `game/scripts/domain/store_layout.gd`に`try_add_fixture(fixture_config: Dictionary) -> bool`
  を追加。既存の`try_move_fixture`/`try_rotate_fixture_clockwise`と同じ
  「候補配列を作り、`_fixture_configs_are_valid()`で検証してから確定する」パターンに
  従う、新規什器追加版。
- `vertical_slice_simulation.gd`に`try_purchase_fixture(catalog_id, instance_id,
  origin_subcell, interaction_subcell) -> bool`を追加。処理順序:
  1. ゲームオーバー/来店中/補充タスク中でないことを確認(既存の
     `try_relocate_fixture`と同じゲート)。
  2. `instance_id`が空でなく、既存什器と重複していないことを確認。
  3. `catalog_id`が什器カタログに存在することを確認。
  4. 現金が購入価格以上であることを確認。
  5. `layout.try_add_fixture()`で配置を試み、失敗したら中断。
  6. 配置後に`_required_routes_are_reachable()`/`_all_staff_are_walkable()`を
     再検証し、既存客の必須ルートや店員の立ち位置を壊す配置ならアトミックに
     ロールバックする(`try_relocate_fixture`と同じ安全策)。
  7. 成功したら`economy.record_explicit_expense()`で購入価格を計上し、
     `fixture_purchased`イベントを記録する。
- `data/vertical_slice.json`に`fixture_catalog`セクションを追加し、
  `reference_sim`の`FIXTURES`から観葉植物(¥1,000)・ベンチ(¥2,000)・
  噴水(¥5,000)の3種を、購入価格・維持費・サービス値ボーナスとともに
  そのまま移植した(すべてCONFIRMED_OFFICIAL、`schema_version`を7→8に更新)。
- `store_view.gd`の描画を、`kind == "shelf"`/`"checkout"`の二択から
  `"amenity"`を含む三択に拡張(什器を購入してもレジと誤表示されないための
  見た目のみの修正)。

### 何を発明していないか、あるいは意図的に残したもの

- `maintenance_yen_per_day`と`service_bonus`はカタログに保持しているが、
  **まだどこにも消費されていない**。日次の維持費控除処理も、店舗評価
  (サービス値)への反映も未実装のままである。前者は既存の日次ループが
  什器の維持費という概念自体をまだ扱っていないための一貫性維持、後者は
  タスク#27(店舗評価をゲームループへ反映)の担当領域であるため、意図的に
  スコープ外とした。
- カタログの什器は`kind: "amenity"`という新しい種別だが、`interaction_subcell`
  は依然として必須(`StoreLayout`のスキーマ上の制約)。この点は什器そのものの
  「使われ方」を発明しないよう、呼び出し側(テスト)が明示的に指定する値のままで
  あり、将来何かに使われることを想定した座標ではない。
- 什器カタログには`reference_sim`にある什器のうち観葉植物・ベンチ・噴水の3種のみを
  移植した。駐車場系(`parking_ground`等)は`blocks_pedestrian`/`parking_capacity`
  という、このvertical sliceにまだ存在しない概念を伴うため、今回は見送った。

### タスク#25の残り

商品仕入れ(仕入れ値に基づく新規商品SKU追加)、許可(タバコ/酒/薬の申請と
それに紐づく販売可否)、広告宣伝の3つは引き続き未実装であり、タスク#25は
今回のコミットでは完了としない。

## 影響

- `game/scripts/domain/store_layout.gd`: `try_add_fixture()`を追加。
- `game/scripts/vertical_slice_simulation.gd`: `_fixture_catalog`フィールド、
  `try_purchase_fixture()`を追加。`_require_config()`が`fixture_catalog`キーと
  各エントリの必須フィールドを検証するよう変更。`schema_version`要求を8に更新。
- `game/scripts/store_view.gd`: 什器種別ごとの色/ラベル分岐を三択に拡張。
- `game/data/vertical_slice.json`: `fixture_catalog`セクション追加、
  `schema_version`を8に更新。
- `game/scripts/headless_smoke.gd`: 有効な購入の成功・重複ID拒否・
  未知カタログID拒否・設置済みセルへの購入拒否・資金不足時の拒否と
  それぞれの副作用なしを検証するテストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 本機能の
  存在と`reference_sim`由来の確定価格であることを検証する新規contractテストを
  追加。
