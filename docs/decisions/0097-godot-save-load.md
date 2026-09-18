# 0097: `game/`(Godot)にセーブ/ロードを実装(タスク#28)

## 背景

タスク#28「セーブ/ロードをGodotに実装」に着手した。これまでのタスクと異なり、
セーブ/ロードは`reference_sim`側に対応物が存在しない純粋なエンジン機能
(ゲーム内容の証拠に基づく推測を伴わない)であるため、evidence-safeタグ付けの
対象ではなく、実装上の設計判断の記録が本決定書の主題となる。

## 決定

### 何をセーブ/ロードするか

`VerticalSliceSimulation`に`save_state() -> Dictionary`/
`load_state(data: Dictionary) -> bool`を追加し、以下を対象とした:

- 時刻・日数・月数(`minute_of_day`/`day_count`/`month_count`/
  `_days_completed_this_month`/`_cash_at_month_start`/
  `_revenue_at_month_start`)
- ゲームオーバー/クリア状態(`is_game_over`/`game_over_reason`/
  `clear_condition_met`)
- 人気度・評価(`popularity`/`internal_rating_value`/`star_rating`)
- 保有許可(`_permits_held`)、今月使用済み広告(`_promotions_used_this_month`)、
  予約済み広告(`_scheduled_promotions`)
- 店舗レイアウト(`layout.fixture_snapshot()`) -- 購入/移動/回転した什器を含む
- 在庫(`inventory`の全商品、`try_procure_product`で追加された商品SKUを含む)
- 経済状態(`economy`の現金・売上履歴・支出履歴・月次決算履歴)
- イベントログ全履歴(`event_log`)

### 何を意図的にセーブ/ロードしないか

**アクティブな顧客の来店途中の状態(ルート上の位置・買い物かごの中身・
レジ待ち進捗)と、スタッフの作業途中の状態(ルート上の位置・
`restock_ticks_remaining`)は保存しない。** これらは代表日1日にも満たない
一時的なアニメーション進捗であり、ロード後は`reset()`が既に作る「アイドル状態の
スタッフ陣・新規に案内された1人のデフォルト顧客」がそのまま使われる(この
クライアントの他のリセット境界と同じ扱い)。経路(route)の逐次位置まで
シリアライズする実装コストに対して、プレイヤーへの価値がほぼ無いと判断した。

これにより`load_state()`は「configから導出される状態をいったん完全に
リセットしてから、セーブデータの値を上書きする」という設計になっている
(単に個々のフィールドをパッチするのではない)。具体的には`layout.reset()`/
`inventory.reset()`/`economy.reset()`/`customers.reset()`/`staff.reset()`/
`event_log.reset()`を先に呼び、その後にセーブデータの値を適用し、
`layout.restore_fixture_snapshot()`で什器レイアウトを復元した**後**に
`_start_default_customer()`でデフォルト顧客を案内する。この順序が重要:
什器レイアウトが確定する前に顧客を案内すると、その顧客の経路キャッシュが
後で変わるレイアウトに対して古い(整合しない)ものになってしまう。

この設計の帰結として、`load_state()`は新規構築直後のシミュレーションだけでなく、
既にプレイ中のシミュレーションに対しても安全に呼び出せる(いつでも「ロード」
操作として使える)。

### 互換性チェックと失敗時の扱い

`load_state()`は次の場合に**何も変更せず** `false`を返す(このクライアントの
他の`try_*`系メソッドと同じ、想定内の拒否):

- セーブデータの`scenario_id`が現在の設定と一致しない
- セーブデータの`config_schema_version`が現在の`config.schema_version`と
  一致しない(configの形が変わっていれば、古いセーブは意味を持たない)
- セーブデータの`save_schema_version`(現在1)が一致しない
- `layout.fixture_snapshot_is_valid()`が什器配置を拒否する

一方、必須キーがまるごと欠落しているような**構造的破損**は、`_require_config()`
と同じ規約(`push_error()` + `assert(false)`)に従う。セーブファイルは
プレイヤー操作(`try_*`)に近い実行時データではあるが、このクライアント自身が
生成したもの以外を受け付ける想定がまだ無いため、想定外の構造破損は
「開発者が対処すべき異常」として扱う既存の規約に合わせた。

### 見つけて直した既存の潜在バグ

実装中に2件、既存コードの潜在バグを発見し、セーブ/ロードのために修正した:

1. **`StoreLayout.restore_fixture_snapshot()`の型正規化漏れ**:
   従来は受け取ったスナップショットをそのまま`fixtures`に代入していたが、
   `JSON.parse_string()`は全ての数値をfloatとして返すため、セーブファイルを
   経由したスナップショットは`origin_subcell`等がfloat型になってしまう
   (`_init()`のコメントが警告している「5 vs 5.0」問題そのもの)。
   `_normalize_fixture_configs()`を通すよう修正した。既存の唯一の呼び出し元
   (什器購入/移動/回転の失敗時ロールバック)は常にint型のスナップショットを
   渡すため、この変更は既存呼び出しに対して完全に無害(冪等)。
2. **`EconomyState`の`_settled_customer_ids`を素朴に再構築すると顧客IDが
   衝突する**: 当初、セーブデータの`sale_records`から`_settled_customer_ids`を
   再構築する実装を書いたが、顧客ロースターの状態は保存しない設計のため、
   ロード後の顧客IDは常に`"<prefix>-1"`から採番し直される。もし過去の
   `sale_records`に同じID(例: `"customer-1"`)の決済済み記録が含まれていれば、
   ロード直後に案内される新しい(実際には別の)`"customer-1"`が二度と決済
   できなくなってしまう。これを見つけ、`_settled_customer_ids`はロード時に
   常に空にする(履歴から再構築しない)よう修正した。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`: `save_state()`/`load_state()`/
  `_require_save_data()`を追加。
- `game/scripts/domain/economy_state.gd`: `snapshot()`/`restore_snapshot()`を
  追加。
- `game/scripts/domain/inventory_catalog.gd`: `snapshot()`/`restore_snapshot()`を
  追加。
- `game/scripts/domain/runtime_event_log.gd`: `restore_snapshot()`を追加
  (`_next_sequence`を復元した記録群の最大`sequence`+1として再計算)。
- `game/scripts/domain/store_layout.gd`: `fixture_snapshot_is_valid()`
  (検証専用の公開ラッパー)を追加。`restore_fixture_snapshot()`の
  正規化漏れを修正(前述)。
- `game/scripts/save_game_service.gd`(新規): `SaveGameService`。
  `save_state()`/`load_state()`が返す/受け取るDictionaryと、
  `user://saves/`配下のJSONファイルとの間のI/O境界のみを担当する薄いクラス
  (`scripts/domain/`配下のクラスはI/Oを持たないという既存の規約に合わせ、
  `scripts/`直下に置いた)。`save_to_path()`/`load_from_path()`/
  `save_exists()`/`delete_save()`を提供。

## テスト

- `game/scripts/headless_smoke.gd`: 什器購入・広告予約・1ヶ月経過(広告発火・
  月次決算・評価反映を含む)まで進めたシミュレーションを`save_state()`で
  保存し、別の新規シミュレーションへ`load_state()`で復元して、現金・日数・
  月数・人気度・内部評価値・什器配置・在庫総数・イベントログ件数
  (前述の+1を含む)・売上/月次決算の件数が厳密に一致することを検証。
  さらに`scenario_id`/`config_schema_version`が異なるセーブデータが拒否
  されること、`SaveGameService`による実ファイルの書き込み・読み込み・
  存在確認・削除が正しく機能することを検証。
- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_save_load_round_trips_progress_and_rejects_incompatible_saves`を
  追加。主要メソッドの存在、互換性チェックの実装、意図的に保存しない範囲の
  明記、新規テストの存在を検証する。

## タスク#28の完了

エンジン機能としてのセーブ/ロードを実装し、何を保存し何を保存しないかを
明示的に設計・記録した上で、タスク#28「セーブ/ロードをGodotに実装」を
完了とする。
