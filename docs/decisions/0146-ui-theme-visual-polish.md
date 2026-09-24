# 0146: UIビジュアルポリッシュ — 共通テーマリソースの導入(タスク#76)

## 背景

タスク#75(カレンダー表示・ゲームオーバー画面)がマージされた後、
「見た目のビジュアルポリッシュ」の方向をユーザーに選択された。現状の
`main.tscn`/`main_menu.tscn`はGodotの既定テーマそのままで、パネルは
角丸なしの単色、ボタンはホバー/押下フィードバックのない平坦な灰色、
セクション見出しラベルも本文と同じ白一色——デバッグツール的な見た目
のままだった。

## 決定

### `game/themes/ui_theme.tres`(新規Themeリソース)

初めて手書きするTheme/StyleBoxFlatリソース(このプロジェクトでこれ
までに書いたことがない種類のファイル)。ローカルにGodot実行環境が
ないため、構文の妥当性はCIの`godot --headless --editor --path game
--quit`(プロジェクトインポート)でのみ検証可能——過去タスクと同じ
「CIで検証」の方針を踏襲。

- `default_font_size = 15`
- `PanelContainer`用のカード風StyleBoxFlat(角丸10px、淡いボーダー、
  内側マージン)
- `Button`/`OptionButton`用のnormal/hover/pressed/disabledの4状態
  StyleBoxFlat(アクセントカラーのティール系、角丸8px)+文字色

見た目・配色に関する純粋なUI装飾であり、シミュレートされたゲーム
データやメカニクスの発明ではないため、REMAKE_BALANCED_DEFAULTタグは
不要と判断した(既存の`Title`/`PrototypeNotice`ラベルの配色が未タグ
なのと同じ扱い)。

### 適用箇所

`theme`プロパティは`Control`にのみ存在し、`Node2D`/`CanvasLayer`には
存在しない。そのため`Main`(Node2D)や`UI`(CanvasLayer)ではなく、
実際に`Control`である`UI/Panel`(サイドバー全体)と
`GameOverLayer/Panel`(タスク#75のオーバーレイ)の両`PanelContainer`
ノードに直接`theme`を設定した。ここから子孫の`Control`へ自動的に
カスケードするため、ノードの親子構造(`main.gd`の`@onready`パス)を
一切変更せずに済んでいる。`main_menu.tscn`の`Panel`にも同じテーマを
適用し、タイトル画面とプレイ画面の統一感を持たせた。

### セクション見出し・主要数値の配色

- `Heading`(STORE STATUS)/`EconomyTitle`/`StaffHiringTitle`:
  テーマのアクセントカラーに近いシアン系(`Color(0.55, 0.85, 0.87, 1)`)
  で本文と視覚的に区別。
- `CashValue`: 金色系(`Color(0.85, 0.75, 0.35, 1)`)で主要数値を強調。
- `GameOverTitle`: 警告色の赤系(`Color(0.9, 0.35, 0.32, 1)`)——既存の
  amber(PROVISIONAL注記)・green(シナリオクリア表示)とは別の意味を
  持つ配色として区別。
- `main_menu.tscn`の`Title`にも同じアクセントカラーを適用。

## テスト

- `reference_sim`フルスイート741件パス/1件xfail(新規コントラスト
  テスト1件、740→741)。`ui_theme.tres`の存在とキー内容、
  `main.tscn`/`main_menu.tscn`への適用、`headless_smoke.gd`の検証
  コードの存在を文字列レベルで確認。
- `game/scripts/headless_smoke.gd`: 既存の`economy_ui_scene`(実際に
  `main.tscn`をシーンツリーへインスタンス化するテスト)を延長し、
  `UI/Panel`ノードの`theme`が実際に非nullのTheme resourceとして
  ロードされ、`default_font_size == 15`であること、
  `PanelContainer`/`Button`用のstyleboxが実際に登録されていることを
  `has_stylebox()`で確認。手書きのTheme/StyleBoxFlatリソースが
  サイレントにパース失敗して既定テーマへフォールバックする——という
  このサンドボックスでは他に検知手段のない失敗モードを直接検証する。
  ローカルにGodot実行環境がないためCIで最終検証。

## 対象ファイル

- `game/themes/ui_theme.tres`(新規)
- `game/scenes/main.tscn`
- `game/scenes/main_menu.tscn`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- サイドバーのノード構造そのものの再編(セクションごとに独立した
  カードパネルへ分割するなど)——既存の`@onready`パス
  (`$UI/Panel/Margin/Scroll/VBox/XValue`)を壊すリスクが高く、今回は
  ノードの親子関係を一切変更しない安全な範囲(テーマのカスケード・
  既存ラベルの配色オーバーライドのみ)に絞った。
- `SpinBox`(`PriceChangeSpinBox`)・`HSeparator`の再スタイリングは
  対象外——`Button`/`OptionButton`/`PanelContainer`の3種に絞り、
  Theme構文の妥当性検証済みの範囲を広げすぎないようにした。
- カスタムフォント(Godotの既定フォントのまま)——フォントアセットが
  このプロジェクトに一切存在せず、新規調達は本タスクのスコープ外。
- 店舗ビュー(`store_view.gd`のCanvas描画)・町マップの見た目変更——
  Control系UIの装飾に絞り、`_draw()`ベースの独自描画コードは対象外。
