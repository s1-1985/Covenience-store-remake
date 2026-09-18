# 0098: `game/`(Godot)に基本メニューUIを実装(タスク#29)

## 背景

タスク#29「基本メニューUIをGodotに実装」に着手した。これまでの構成では
`project.godot`の`run/main_scene`が直接ゲームプレイ画面(`scenes/main.tscn`)
を指しており、タイトル画面や、既存プレイの再開/終了操作が一切なかった。
また、タスク#28で実装した`save_state()`/`load_state()`/`SaveGameService`は
バックエンドのメソッドとしては完成していたが、プレイヤーがそれを呼び出す
UI導線が存在しなかった。本タスクはこの2点を埋める、純粋なエンジン/UI機能
(`reference_sim`に対応物のない領域)である。

## 決定

### 実装した内容

1. **`scenes/main_menu.tscn` / `scripts/main_menu.gd`(新規)**: タイトル
   画面。「New Game」「Continue」「Quit」の3ボタン。`Continue`は
   `SaveGameService.save_exists()`がfalseの間は無効化される。
   `project.godot`の`run/main_scene`をこのシーンへ変更した。
2. **`scripts/game_launch_state.gd`(新規、autoload)**: Godotの
   `change_scene_to_file()`はシーン間で直接パラメータを渡せないため、
   「Continueが押されたか」を伝えるための最小限の状態を持つautoload
   singletonを追加した(`continue_from_save: bool`一つのみ)。
   `project.godot`の`[autoload]`セクションに`GameLaunchState`として登録。
3. **`scripts/main.gd`の変更**: `_ready()`冒頭で
   `GameLaunchState.continue_from_save`を確認し、trueならフラグを消費
   (falseに戻す)した上で`SaveGameService.load_from_path()`を呼ぶ。falseの
   場合(メインメニューを経由しない直接起動を含む)は何もせず、通常通り
   configから新規状態で開始する。ゲームプレイ画面自体にも「Save」
   「Load」「Quit to Menu」の3ボタンを追加した(`UI/Panel/Margin/VBox/
   MenuButtons`)。Save/Loadはタスク#28で実装済みの`SaveGameService`を
   そのまま呼び出すだけで、新しい保存機構は作っていない。

### 設計上の判断

- **New Gameは既存セーブを削除しない**: 「New Game」ボタンは単に
  `continue_from_save`をfalseにしてゲームプレイ画面へ遷移するだけで、
  `SaveGameService.delete_save()`は一切呼ばない。既存のセーブファイルを
  黙って消す破壊的副作用を避けるため。プレイヤーが後で明示的に「Save」を
  押した時だけ、上書きされる。
- **`GameLaunchState`のフラグは読み取り後に必ず消費する**: `main.gd`は
  読み取った直後に`continue_from_save`をfalseへ戻す。そうしないと、
  一度Continueで入った後にリセットや別シーンからの再訪問で意図せず再度
  ロードが走ってしまう。
- **既存のセーブ/ロードイベントログ挙動との整合**: タスク#28の
  `load_state()`は、ロード完了後に新しいデフォルト顧客を案内する際に
  `customer_entered`イベントを1件追加する(決定書0097参照)。UIからの
  「Load」ボタンでも同じ`load_from_path()`を呼ぶだけなので、この挙動は
  変わらない。
- **`main.tscn`は変更せず、ゲームプレイ画面としてそのまま存続**:
  タイトル画面を新設するにあたり、既存のゲームプレイ画面
  (`scenes/main.tscn`)自体を作り直す必要はなかった。`run/main_scene`が
  変わっただけで、`main.tscn`は「メインメニューから遷移する先」として
  従来通り機能する。

### CIでの検証

`godot --headless --script res://scripts/headless_smoke.gd`は`_initialize()`
内で直接呼ばれる非対話型スクリプトであり、`SceneTree`のルートへ
`add_child()`されない`instantiate()`だけでは`_ready()`(および`@onready var`)
が実行されないことを確認した上で、以下の2段階でテストを構成した:

1. **構造検証**(既存の"instantiate → free"パターンを踏襲):
   `main.tscn`/`main_menu.tscn`をロード・インスタンス化できることに加え、
   本タスクで追加した各`@onready var`が参照するノードパス
   (`SaveButton`/`LoadButton`/`QuitToMenuButton`、
   `NewGameButton`/`ContinueButton`/`QuitButton`/`StatusLabel`)が実際に
   存在することを`get_node_or_null()`で確認する。`_ready()`が実行されない
   ため、これらのノードパスの誤りはこの検証がなければCIで検出できない。
2. **静的プロパティ検証**: `main_menu.tscn`の`ContinueButton`が
   `disabled = true`をデフォルトとして持つこと(セーブファイルが無い状態の
   起動を想定した初期状態)を検証する。

`_ready()`自体(ボタン接続、`GameLaunchState`アクセスなど)の実行時挙動は、
既存の"instantiate without add_child"パターンをこのタスクのために変更
すると、これまで9タスク分安定して動いていたCI検証の前提を変えてしまう
リスクがあるため、あえて手を付けなかった。したがって`GameLaunchState`
autoloadの実際の解決可否は、このCI実行が初めての実地検証となる
(このリスクはPR説明に明記している)。

## 実装ファイル

- `game/scenes/main_menu.tscn`(新規)
- `game/scripts/main_menu.gd`(新規)
- `game/scripts/game_launch_state.gd`(新規、autoload)
- `game/project.godot`: `run/main_scene`を`main_menu.tscn`へ変更、
  `[autoload]`セクションに`GameLaunchState`を追加。
- `game/scenes/main.tscn`: `MenuButtons`(Save/Load/Quit to Menu)を追加。
- `game/scripts/main.gd`: `GameLaunchState`連携、Save/Load/Quit-to-Menuの
  ボタンハンドラを追加。
- `game/scripts/headless_smoke.gd`: 上記2シーンのノードパス構造検証を追加。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_godot_entry_scene_and_scripts_exist`を`run/main_scene`の変更・
  新規ファイルの存在に合わせて更新。
  `test_basic_menu_ui_wires_new_game_continue_quit_and_in_game_save_load`
  を新規追加し、New Game/Continue/Quit・`GameLaunchState`によるフラグの
  受け渡しと消費・in-game Save/Load/Quit to Menuの配線・New Gameが
  `delete_save`を呼ばないことを検証する。

## タスク#29の完了

タイトル画面(New Game/Continue/Quit)と、ゲームプレイ画面からのSave/Load/
Quit to Menuを実装し、タスク#28で作った保存機構に初めてプレイヤー向けの
UI導線を与えた上で、タスク#29「基本メニューUIをGodotに実装」を完了とする。
