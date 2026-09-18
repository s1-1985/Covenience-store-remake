# 0104: `game/`(Godot)のHUDにstar_rating/popularity/land_value/townを表示(タスク#35)

## 背景

`docs/handoff/2026-09-18-claude-code-session-handoff.md`第3.1節が指摘していた
ギャップ: `store_view.gd`のバックエンドには`star_rating`/`popularity`/
`town_population`/`land_value_yen`等の計算ロジックが既に実装済み
(`vertical_slice_simulation.gd`の`snapshot()`が全て返している)だったが、
`main.tscn`のSTORE STATUSパネルにはこれらを表示するLabelノードが一切存在
せず、プレイヤー視点では「バックエンドにはあるのに画面から見えない」状態
だった。この問題は当初の「画像・音声はさておき、ゲームとして操作できない
ってこと?」という疑問の核心に最も近い項目として記録されていた。

同セッションで着手予定だった3.2節(同時複数顧客/待ち行列、サンプルレイアウト
読み込み、什器attention差別化)は、ユーザーに確認の上、今回は対象外とした
(新規タスク番号は未割り当てのまま)。

## 決定

### HUDへのラベル追加

`main.tscn`の`VisitsValue`と`Separator2`の間に、既存の`Title`/`Value`ペアの
パターンを踏襲して2ペア追加した:

- `RatingTitle`/`RatingValue`: 星評価(★/☆5個)+人気度(0〜100)
- `TownTitle`/`TownValue`: 町人口 + ライバル店舗数 + 地価

いずれも`snapshot()`が既に返す値をそのまま表示するだけであり、
シミュレーション側のロジックには一切手を加えていない。

### 表示ロジックの詳細

- 星評価: `star_rating`(0〜5の整数、`store_rating.gd`の
  `star_rank_for_internal_value`で保証済みの範囲)を`★`/`☆`の文字列に変換
  する`_star_rank_text()`をmain.gdに新設。
- ライバル店舗数: `snapshot()`の`town_store_count_including_rivals`は
  「プレイヤー自身の店舗を含む町の総店舗数」であり(`headless_smoke.gd`の
  既存アサーション「rival_store_count must equal
  store_count_including_rivals minus the player's own store」で裏付け)、
  そのまま「ライバル店」として表示すると自店舗数を含んでしまい誤解を招く。
  そのため`snapshot()`の`player_store_count`を差し引いた値を表示した。
- 地価: `land_value_yen`をそのまま`¥`区切り表示。

## テスト

- `headless_smoke.gd`の構造チェック(`main.tscn`のノードパス存在確認)に
  `RatingValue`/`TownValue`を追加。
- Godot 4.3公式バイナリで`headless_smoke.gd`を実行し、全テストPASSを確認
  (`Vertical-slice headless smoke passed in 530 steps.`)。
- Xvfb + 実Godotバイナリで`main.tscn`を実際にレンダリングし、
  「☆☆☆☆☆ (popularity 0)」「population 2,000, 0 rival stores, land
  ¥24,400,000」が意図通り描画されることをスクリーンショットで目視確認。
- `reference_sim/tests`フルスイート(651件+xfail 1件)が全てPASS
  (このタスクはgame/側のUI配線のみで`reference_sim`のデータ・ロジックには
  触れていないため、影響なしを確認する目的)。

## 実装ファイル

- `game/scenes/main.tscn`: `RatingTitle`/`RatingValue`/`TownTitle`/
  `TownValue`ラベルを追加。
- `game/scripts/main.gd`: 上記ラベルの`@onready`束縛、`_refresh_ui()`への
  表示ロジック追加、`_star_rank_text()`ヘルパーを新設。
- `game/scripts/headless_smoke.gd`: 構造チェックに新ノードパスを追加。

## 明示的に対象外とした限界

- 什器の`maintenance_yen_per_day`は既存のevidence_noteが明記する通り、この
  クライアントではまだいかなるロジックにも消費されていない(キャッシュフロー
  への反映は別作業)。今回のHUD表示はあくまで既存の`snapshot()`が返す値の
  可視化であり、新しい経済シミュレーションロジックは追加していない。
- 3.2節の3項目(同時複数顧客/待ち行列、サンプルレイアウト読み込み、什器
  attention差別化)は、ユーザー確認の結果、今回は対象外。
