# 0114: 什器の`capacity`/`compatible_product_categories`を仕入れ処理へ配線(タスク#45)

## 背景

タスク#43の調査で見つかった2候補のうち、ユーザーが先に「顧客シェア式の
統合」(タスク#44)を選び、続けて「什器のcapacity/互換性を実際に配線」を
選択した。

`reference_sim/conveni_sim/baseline_data.py`の`FIXTURES`は、什器kind=
"shelf"の29エントリ全てにCONFIRMED_OFFICIALな`capacity`(在庫収容上限)
と`compatible_product_categories`(仕入れ可能な商品カテゴリの一覧)を
持っている。タスク#39・#41でこれらのエントリを`fixture_catalog`へ移植した
際、両フィールドは「攻略本には確認済みだが、什器×商品の互換性チェックや
在庫上限チェック自体がこのクライアントに存在しないため未消費」と
evidence_noteに明記した上で意図的に据え置いていた(決定書0093でも同様の
理由で据え置き)。今回、この据え置きを解消し、実際に配線した。

## 決定

### `fixture_catalog`への`capacity`/`compatible_product_categories`追加

29のshelf種什器エントリ全てに、`reference_sim`の`FIXTURES`から直接
転記した`capacity`(整数)と`compatible_product_categories`(商品
カテゴリidの配列)を追加した。配列の各要素は`product_catalog`の
`catalog_id`と完全に同じ語彙(タスク#39で商品カテゴリを直接カタログid
として移植したため)。amenity/parking種の6エントリには追加していない
(`reference_sim`側でも該当フィールドが`None`であり、商品を保持しない
什器のため対象外)。

### `try_procure_product()`への互換性チェック配線

仕入れ対象の`fixture_id`が実際に`fixture_catalog`由来の什器で、かつその
カタログエントリが`compatible_product_categories`を持つ場合のみ、
仕入れようとする商品の`catalog_id`がその一覧に含まれているかを検証する。
含まれていなければ仕入れを拒否する。

一方、`fixture_id`が`fixture_catalog`由来ではない(`catalog_id`を持た
ない)場合——具体的には、タスク#31以前からのプロトタイプ什器`shelf-1`/
`shelf-2`(什器カタログ制度が導入される前からシナリオに直書きされている
初期什器)——は、参照できる確認済みデータが存在しないため、チェックを
スキップして従来通り無制限のまま扱う。新しいルールを発明してまで
プロトタイプ什器に適用することはしなかった。

### `try_procure_product()`への在庫上限(capacity)キャップ配線

同様に、仕入れ先の什器カタログエントリが`capacity`を持つ場合、実際に
仕入れる数量を`min(product_catalog側のinitial_stock_units, その什器の
capacity)`にキャップする。

これが必要な理由: タスク#42で`product_catalog`側の`initial_stock_units`
は「そのカテゴリの`PRODUCT_CATEGORY_PRICING.max_capacity`」(カテゴリ
単位の一般的な最大値、例: パン類=120)を使うよう是正済みだが、実際に
購入した特定の什器の`capacity`はサイズによって異なる(例:
`small_ambient_shelf`=40、`medium_ambient_shelf`=80、
`large_ambient_shelf`=120)。カテゴリの一般的な上限が、実際に置いた
什器の実際の収容力を上回るケースが普通に発生するため、両方とも
確認済みデータでありながら矛盾しうる。この矛盾は「小さい方を採用する」
という素直な解釈で解消した——新しい数値を発明したのではなく、既存の
2つの確認済み制約を正しく組み合わせただけである。

仕入れ時にこうしてキャップされた数量がそのまま`product.initial_
stock_units`として保存されるため、その後の補充(`apply_explicit_
restock`ボタンや自動補充`_complete_restock`)は追加のコード変更なしに
この上限を尊重する(補充は常に`product.initial_stock_units`を目標に
行われるため)。

## テスト

- `headless_smoke.gd`: 
  - 既存のたばこ仕入れテスト(タスク#42是正で動的化済み)を、什器
    capacity側の値も動的に読み取って期待数量・期待コストを算出するよう
    更新(`small_tobacco_vending`のcapacity=20 < たばこのinitial_stock_
    units=40のため、実際の仕入れ数量が40→20に変わる)。
  - 経済UIのE2Eテストで、たばこ仕入れ先を`small_ambient_shelf`から
    `small_tobacco_vending`に変更(前者はたばこと互換性がないため今回
    拒否されるようになった)。
  - 新規シナリオ: `small_ambient_shelf`を購入し、互換性のない`tobacco`
    の仕入れが拒否されること、互換性のある`bread`の仕入れが受理される
    ことを検証。
  - Godot 4.3公式バイナリで734ステップ変化なくPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_fixture_capacity_and_compatibility_are_wired_into_procurement`
  を追加。29のshelf種エントリ全ての`capacity`/`compatible_product_
  categories`が`reference_sim`の`FIXTURES`と完全一致すること、
  amenity/parking種にはどちらのフィールドも存在しないこと、
  `compatible_product_categories`に列挙された全カテゴリが実際に
  `product_catalog`のエントリとして存在すること、`copy_paper`/
  `parcel_delivery_form`(タスク#41でコピー機・レジ関連什器を対象外と
  したことと整合して、どのshelf什器からも互換対象として列挙されて
  いないこと)を検証。`VerticalSliceSimulation`の実際の仕入れ処理に
  互換性チェック・容量キャップの両方が配線されていることを検証。
  フルスイート659件(新規テスト含む、xfail 1件)全てPASS。

## 実装ファイル

- `game/data/vertical_slice.json`: `fixture_catalog`の29エントリに
  `capacity`/`compatible_product_categories`を追加、evidence_noteを更新。
- `game/scripts/vertical_slice_simulation.gd`: `try_procure_product()`に
  互換性チェックと容量キャップを追加。
- `game/scripts/headless_smoke.gd`: 既存テストの動的化、新規互換性
  テストシナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- `shelf-1`/`shelf-2`(什器カタログ制度導入前からのプロトタイプ什器)は
  引き続き互換性・容量チェックの対象外。新しいルールを後付けで発明する
  のではなく、確認済みデータが存在しないものには手を加えない、という
  従来の方針を維持した。
- `copy_paper`/`parcel_delivery_form`カテゴリは、対応する什器
  (コピー機・レジ)がタスク#41で意図的に対象外とされているため、
  依然としてどのshelf種什器からも仕入れられない。これは今回のタスクの
  対象外ではなく、それら2つの什器を将来的に追加しない限り解消しない
  既存の制約。
