# 0106: `game/`(Godot)にサンプルレイアウト読み込み機能を実装(タスク#37)

## 背景

3.2節の残り2項目のうち2件目。
`docs/research/ss-layout-entrance-register-and-chain-cannibalization-2026-09-06.md`
第3節が記録する証拠:

- サンプルレイアウトの存在: **B+ / DIRECT-PLAY-SS**(二次資料による裏付けあり)。
- 読み込みが「簡単には元に戻せない」破壊的操作であること: **B / DIRECT-PLAY-SS**。
- サンプルの具体的な中身(什器配置そのもの)、サンプル数、店舗サイズ別の
  対応関係、正確な取り消し/売却の仕組みは**すべて未確認**。

この証拠の非対称性(「機能が存在し破壊的である」ことは確認済みだが「中身」は
一切未確認)を踏まえ、今回のタスクは**メカニズム自体**(読み込み・コスト計算・
検証・破壊的上書き)をCONFIRMEDな要件として実装し、**サンプルの具体的な中身**は
このプロジェクト独自のプレースホルダーとして明示的にREMAKE_BALANCED_DEFAULTと
タグ付けする方針を取った。

## 決定

### サンプルデータの設計方針

`vertical_slice.json`に`sample_layouts`(新規必須セクション)を追加し、2件を
定義した:

- `default_layout`: 現在の初期配置(checkout-1/shelf-1/shelf-2)と全く同じ
  内容。「元の配置に戻す」という無料の選択肢として機能する。
- `with_bench`: 同じ3什器に加え、`bench`什器(catalog購入)を1つ追加した配置。

どちらも各エントリの`evidence_note`に「原作から回収したサンプルではなく、
このプロジェクト独自のプレースホルダーである」ことを明示している。原作の
実際のサンプル内容を主張するものではない。

### 什器の再利用は無料、新規追加分のみ通常価格で課金

`try_load_sample_layout(sample_id)`は、現在のレイアウトに**既に存在するID**の
什器はそのまま再利用(移動扱い、無料)し、サンプルにのみ存在する**新規ID**の
什器だけを、その`fixture_catalog`の通常購入価格で課金する。「レイアウトの
入れ替え」であって「什器の売却」ではないため、研究ノートが明示的に未確定と
した「正確な売却比率」を発明する必要が一切ない。

### 取り消し(undo)・売却機能は実装しない

研究ノートの「`load sample`、`sell/remove fixture`、`restore previous layout`は
別々の未解決課題として扱うこと」という指針に従い、**取り消し操作は一切
実装していない**(`restore_fixture_snapshot`を内部的に使うのは失敗時の
アトミックなロールバックのみで、プレイヤー向けの「元に戻す」機能ではない)。
これは原作の「簡単には元に戻せない」というCONFIRMED-VISUAL級の証拠と整合する。

### 在庫が孤立する組み合わせは拒否

現在の店舗にある什器のうち、商品が仕入れ済み(`inventory.products`に
`fixture_id`が存在する)ものが、読み込もうとするサンプルに含まれていない場合、
その読み込みは**拒否**する(在庫を静かに破棄する独自ルールを発明するのではなく、
安全側に倒して拒否する)。現時点で定義済みの2サンプルはどちらも常に
checkout-1/shelf-1/shelf-2を含むため、この経路は現状発火しないが、将来サンプルが
増えた場合の安全網として実装した。

### レジ什器IDの保持は必須

`_checkout_interaction`は`simulation.checkout_fixture_id`という固定IDで
`layout.interaction_for_fixture(...)`を呼び出す(`interaction_for_fixture`は
存在しないIDに対してアサートで落ちる)。そのため、サンプルの什器一覧に
`checkout_fixture_id`と一致するレジ什器が含まれていない場合は、
検証段階で明示的に拒否する(クラッシュではなく通常の失敗として扱う)。

### 他のレイアウト編集操作と同じロック

`try_purchase_fixture`等と同様、`not customers.all_settled()`
(入店中の客がいる間はロック)と`_any_restock_task_active()`でガードしている。

## スキーマバージョン

`sample_layouts`という新規必須トップレベルセクションを追加したため、
`schema_version`を13→14に更新(`VerticalSliceSimulation._require_config()`の
アサートも同期)。

## UI

`main.tscn`にOptionButton(`SampleLayoutOption`、サンプル一覧)と
Button(`LoadSampleLayoutButton`)を追加。`main.gd`が`config["sample_layouts"]`
から選択肢を構築し、選択されたサンプルIDで`try_load_sample_layout`を呼ぶ。
これにより、この機能はテスト専用の内部APIではなく、実際のプレイ操作からも
到達可能。

## テスト

- `headless_smoke.gd`:
  - `default_layout`読み込みが常に無料で成功すること。
  - `with_bench`読み込みが資金不足時は拒否され、資金確保後は成功し、什器が
    追加されること。
  - 同じサンプルを再読み込みしても既に所有済みの什器には課金されないこと。
  - 未知のサンプルIDは拒否されること。
  - 入店中の客がいる間はロックされること(他の編集操作と同じ)。
  - 在庫が仕入れ済みの什器を含まない不完全なサンプル(テスト専用に構築)は
    拒否されること。
  - 全体で704ステップ(既存614 + 新規90)でPASS。Godot 4.3公式バイナリで確認。
- Xvfb + 実Godotバイナリで`main.tscn`を実際にレンダリングし、
  (1) 客が入店中はロックメッセージが表示されること、(2) 客の会計完了後に
  `with_bench`サンプルを読み込むとベンチが実際に描画され、現金が正しく
  (2000円)減額されることをスクリーンショットで目視確認。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_sample_layouts_can_be_loaded_and_are_destructive_not_undoable`を追加し、
  上記の設計をフィールド単位で検証。`schema_version`の期待値を13→14へ更新。
  フルスイート653件(xfail 1件)全てPASS。

## 実装ファイル

- `game/data/vertical_slice.json`: `sample_layouts`セクションを新設、
  `schema_version`を14へ。
- `game/scripts/vertical_slice_simulation.gd`: `_sample_layout_catalog`の
  読み込み、`try_load_sample_layout()`を新設。`_require_config()`を更新。
- `game/scenes/main.tscn`: `SampleLayoutOption`/`LoadSampleLayoutButton`を追加。
- `game/scripts/main.gd`: 上記UIの配線。
- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テスト追加、
  `schema_version`の期待値を更新。

## 明示的に対象外とした限界

- サンプルの中身自体(什器配置)は原作から回収したデータではなく、この
  プロジェクト独自のプレースホルダー(REMAKE_BALANCED_DEFAULT)。
- 店舗サイズ別のサンプル対応関係は不明のため、現状は店舗サイズに依存しない
  単一のサンプル集合のみ。
- 取り消し・売却機能は意図的に未実装(研究ノートの指針通り、別課題として
  据え置き)。
- 3.2節の残り1項目(什器attention差別化)は今回も対象外。`docs/decisions/0004`の
  「deliberately absent: incidental/add-on purchase probability」という
  明示的な据え置きと衝突するため、着手にはユーザー確認が必要。
