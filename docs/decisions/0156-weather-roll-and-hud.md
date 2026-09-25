# 0156: 月別天候表からの天候ロールとトップバー天候表示(タスク#85)

## 背景

原作のトップバーは常に天候を表示している(公式PSスクリーンショット`ss01`・
`original-screen-visual-register-2026-09-05.md` V001の`[快晴]`、V005の
`[晴れ]`、プレイ動画フレーム`video_900s.png`の`01年目07月04日［雨 ］`)。
また天候は見た目だけでなく客入りに影響する(雪の日は顧客独占率が半分以下に
なりうる、CONFIRMED_COMMUNITY、`customer-share-weather-hours-and-head-store-
bias-2026-09-06.md`第4節)。

`game/`には天候という状態自体が存在せず、`demand.is_bad_weather`が起動時
固定の`false`のままだった。タスク#77・#82ではこれを理由に天候表示を対象外と
していた。一方`reference_sim`には、タスク#63(決定書0132)で400dpi再確認済みの
月別天候パーセンテージ表(CONFIRMED_OFFICIAL、12行すべて合計100)が既にあり、
`game/`側の消費者が無いという理由だけで未配線だった。

なお当初この作業の前に、カレンダーの日本語表記(`01年目01月01日`)への変更を
タスク#85として進めていたが、mainを取り込んだところ並行でマージされた
PR #261(Android日本語プレビュー)が`tr()`+`ja.po`で同じ変更を既に実装して
いたため、重複として破棄し、番号#85をこの天候タスクに充てた。

## 決定

### 確認済み(バケット1)

- 月別の5カテゴリ(快晴/晴れ/曇り/雨・雪/荒天)の出現率:
  `baseline_data.MONTHLY_WEATHER_PERCENTAGES`を`game/data/vertical_slice.json`
  の`weather.monthly_percentages`へそのまま移植。Python契約テストで両者の
  完全一致を検証する。
- 表示文字列`快晴`/`晴れ`/`雨`: 原作HUDで実際に観測された文字列。
  `曇り`は表自体のカテゴリ名。
- 表示形式: `［雨 ］`のように全角角括弧で囲み、1文字の天候は2文字幅に
  空白で揃える(動画フレームの表示どおり)。

### 自前の仮置き(バケット3、REMAKE_BALANCED_DEFAULT)

- ロールのタイミング: ゲーム開始時と各日の境界で1日1回。原作は日中にも
  天候が変わる(`behavior-rules-evidence-2026-09-05.md`)が、その頻度・
  タイミングを記した資料は無い。コードコメント・JSON・テストの3箇所に
  タグを付けた。
- `雨・雪`カテゴリは常に`雨`と表示、`荒天`カテゴリは表自身の総称`荒天`と
  表示。原作がいつ`雪`を出すか、荒天のうち大雨/雷雨/台風/大雪のどれを
  出すかは資料に無い(決定書0132が既に「タグが必要」と指摘済みの箇所)。

### 需要への反映

`雨・雪`と`荒天`を悪天候とし、既存の`demand.is_bad_weather`をロール結果で
上書きする。対象カテゴリは`reference_sim`の`BAD_WEATHER_VALUES`と一致。
倍率0.6自体は既存の`REMAKE_BALANCED_DEFAULT`のまま変更していない。

### 実装

- `vertical_slice_simulation.gd`: `_weather_rng`(需要用`_demand_rng`とは
  別。既存の需要乱数列をずらさないため)、`_roll_weather()`/
  `_apply_weather()`/`weather_category()`/`weather_display_label()`、
  月末処理の後にロールして月替わりで新しい月の行を使う。
  `weather_category_index`をセーブ対象に追加し`SAVE_SCHEMA_VERSION`を4→5、
  設定の`schema_version`を14→15、`_require_config()`で表の形(12行・
  各行合計100・ラベル数一致)を検証。
- `main.tscn`/`main.gd`: トップバーの日付と時刻の間に`WeatherValue`を追加。

### 同梱フォントの再生成

PR #261が同梱した`game/fonts/ConveniJP.ttf`はUIで使う文字だけのサブセットで、
`快`/`晴`/`曇`/`荒`/`天`が含まれていなかった(そのままでは空白の四角に
なる)。生成スクリプトがリポジトリに無かったため、`tools/build_conveni_font.py`
を新設した。google/fonts(jsDelivrミラー経由)の同一バージョン2.004の
Noto Sans JP可変フォントをwght=400で固定し、既存フォントの全文字+
`ja.po`・`vertical_slice.json`・`game/scripts`・`game/scenes`に出現する
全文字+ASCII/かな/全角記号でサブセットする。既存958文字は1つも欠落させず
984文字に(+26)、レイアウト機能は旧版と同じ`ccmp/liga/locl/vert/vrt2`、
サイズは250KB→258KB。元フォントはリポジトリに含めない(SIL OFL、
`game/fonts/OFL.txt`は既存)。

## テスト

- `headless_smoke.gd`: 各カテゴリで`is_bad_weather`が正しく決まること、
  `雨・雪`が`雨`と表示されること、月1=快晴100%/月2=荒天100%の設定で
  月替わり後に新しい月の行からロールされること、同じシードで同じ天候列が
  再現されること、セーブ/ロードで天候と悪天候フラグが復元されること、
  トップバーが`［%s］`形式で現在の天候を表示すること、同梱フォントが
  天候表示の全グリフを持つこと(`Font.has_char`)。表示ラベルを`雪`に、
  フォントを旧版に差し替える2種の意図的な破壊で、それぞれ失敗することも
  確認した。
- `reference_sim`: 新テスト`test_weather_rolls_from_confirmed_monthly_table_
  and_shows_in_hud`(JSONの表と`baseline_data`の完全一致、悪天候カテゴリが
  `BAD_WEATHER_VALUES`に含まれること、3箇所のタグ文字列など)。747件中
  746成功+既存の期待失敗1件。
- `android_preview_smoke.gd -- --android-preview`: 成功。
- スクリーンショットで`01年目01月01日 ［快晴］ 09:01`の表示と、日送りで
  `［曇り］`/`［晴れ］`/`［雨 ］`に変わることを確認。

## 対象ファイル

- `game/data/vertical_slice.json`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/main.gd`
- `game/scenes/main.tscn`
- `game/scripts/headless_smoke.gd`
- `game/fonts/ConveniJP.ttf`
- `tools/build_conveni_font.py`(新規)
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 日中の天候変化(頻度不明のため)。
- 天候ごとの別倍率(雪で半分以下等)や、季節・商品カテゴリ別の天候補正。
  資料は定性的な記述のみで、式は無い。
- 天候に応じた画面演出(雨のグラフィック等)。
- 顧客独占率計算(`customer_share.gd`)への天候入力。`reference_sim`側には
  `BAD_WEATHER_PENALTY`があるが、`game/`側は需要式の倍率で既に悪天候を
  反映しており、二重適用を避けるため今回は配線しない。
