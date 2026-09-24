# 0145: カレンダー表示とゲームオーバー/クリアUIの実装(タスク#75)

## 背景

タスク#74(セーブ/ロードのチェックアウト待ち行列バグ修正、PR #251)が
マージされた直後、ユーザーから方向転換の指示があった:
「UIとかは？ゲームとして動くように作りこんでいって」(UIはどうなって
いるか? ゲームとして実際に遊べるように作り込んでほしい)。

これを受けて `game/scripts/main.gd`/`game/scenes/main.tscn` の現状を
確認したところ、シミュレーション側(`vertical_slice_simulation.gd`)が
既に追跡していながら、UIには一切表示されていない2つの状態を発見した:

1. **日付/月の進行**: `day_count`/`month_count`/`_days_completed_this_
   month` は `snapshot()` に含まれていたが、`main.gd`の`_refresh_ui()`
   はこれらを一切読んでいなかった。UIには時刻(HH:MM)しか表示されず、
   プレイヤーは今日が何日目・何ヶ月目かを知る手段が全くなかった。

2. **ゲームオーバー/シナリオクリア状態**: `is_game_over`/
   `game_over_reason`/`clear_condition_met` も同様に`snapshot()`には
   含まれていたが、`main.gd`のどこにも参照がなかった。破産
   (`bankrupt`)または100年の時間切れ(`time_limit_exceeded`)で
   `is_game_over`がtrueになっても、各経済アクションが内部で
   `is_game_over`ガードにより静かに失敗し続けるだけで、プレイヤーには
   何の説明も表示されない——「ゲームとして動く」ための最も基本的な
   終了状態フィードバックが欠落していた。

## 決定

### カレンダー表示の追加

`snapshot()`に`days_completed_this_month`を新規追加(`day_count`/
`month_count`は既存)。`main.tscn`に`CalendarValue`ラベルを`ClockValue`
の直後に追加し、`_refresh_ui()`で
`"Month %d · Day %d of %d (Day %d overall)"`形式(4日=
`REPRESENTATIVE_DAYS_PER_MONTH`、CONFIRMED_OFFICIALな値を再利用、
ハードコードしない)で表示する。新しいデータや数値の発明ではなく、
既に追跡済みの値をUIに露出するだけなので、REMAKE_BALANCED_DEFAULT
タグは不要と判断した。

### ゲームオーバー/クリア画面の追加

- `GameOverLayer`(`CanvasLayer`, layer=5, 既定で非表示)を`main.tscn`
  に追加。全画面を覆う半透明背景+中央パネルに「GAME OVER」見出し、
  理由テキスト、「Play Again」「Return to Menu」の2ボタン。
  `ColorRect`の既定`mouse_filter`(STOP)によって、表示中は背後の
  サイドバー操作を自然にブロックする——個々のハンドラに`is_game_over`
  チェックを追加する必要はない。
- `_refresh_ui()`が`snapshot()["is_game_over"]`を見てこのレイヤーの
  可視性を切り替え、`game_over_reason`("bankrupt"/"time_limit_
  exceeded"のみ、`_trigger_game_over()`の実装から確認済み)を
  プレイヤー向けの英文に変換する`_game_over_reason_text()`を新設。
  ゲームオーバーに達すると同時に`paused`を自動でtrueにする。
- 「Play Again」は既存の`_on_reset_pressed()`(サイドバーの`Reset`
  ボタンと同一ハンドラ)、「Return to Menu」は既存の`_on_quit_to_menu_
  pressed()`をそのまま再利用——新しいリセット/遷移ロジックは書いて
  いない。
- `clear_condition_met`(`player_store_count`が`PLAYER_STORE_COUNT_
  SCENARIO_TARGET`=10店舗に到達、既存コメントの通りPROVISIONAL)は
  ゲームオーバーとは独立した恒久フラグで、達成後もプレイは継続する
  仕様(`_evaluate_terminal_state()`自身のコメント通り)。そのため
  一度きりのモーダルではなく、サイドバーに常時表示される
  `ScenarioStatusValue`ラベル(達成時のみテキストが入る)とした。

## テスト

- `reference_sim`フルスイート740件パス/1件xfail(新規コントラクト
  テスト1件、739→740)。`main.tscn`の新規ノード名、`main.gd`の新規
  シンボル/シグナル接続、`vertical_slice_simulation.gd`の
  `days_completed_this_month`追加、`headless_smoke.gd`の新規UIシナリオ
  の存在を文字列レベルで検証。
- `game/scripts/headless_smoke.gd`: 既存タスク#38の`economy_ui_scene`
  (実際に`main.tscn`をシーンツリーへインスタンス化するテスト)を延長。
  - カレンダーラベルが実際のシミュレーション状態と一致することを確認
    (固定の「Day 0」を仮定せず、`economy_ui_scene.simulation`から都度
    期待値を計算——このシナリオ内で既に複数の`step()`ループが走って
    いるため)。
  - `game_over_layer`が初期状態で非表示であることを確認。
  - `clear_condition_met`を直接trueにして`scenario_status_label`が
    反応することを確認。
  - タスク#65の`bankruptcy_simulation`と同じ手法
    (`economy.cash_yen = -1`→`_evaluate_terminal_state()`直接呼び出し)
    で実際の破産ゲームオーバーを発生させ、オーバーレイの表示・理由
    テキスト・自動ポーズを確認。
  - 「Play Again」(`_on_reset_pressed()`)がオーバーレイを再度隠す
    ことを確認。
  - ローカルにGodot実行環境がないためCIで最終検証。

## 対象ファイル

- `game/scripts/vertical_slice_simulation.gd`
- `game/scenes/main.tscn`
- `game/scripts/main.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- ビジュアルデザインの全面刷新(現状のサイドバー型デバッグUIの見た目
  自体は変更していない)——今回はユーザー指示の中でも最も欠落度の高い
  「ゲームの終了状態が全く見えない」という機能的ギャップに絞った。
  見た目のポリッシュは別タスクとして今後ユーザーに提案する。
- `clear_condition_met`のワンタイム通知(達成した瞬間のポップアップ
  など)は実装していない——恒久フラグを毎フレーム素直に表示する方式
  とし、別途「表示済みフラグ」をUI層に持たせる複雑さを避けた。
