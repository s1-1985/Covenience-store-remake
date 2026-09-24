# 0132: 年間カレンダー(平日/休日)の実装 + 天候パーセンテージ表の誤り修正(タスク#63)

## 背景

ユーザーから、以前アップロードした4分割PDF(「新人店長実習マニュアル」「クイックリファレンス」の
原本スキャン)が再度共有され、システム面の作り込みを続けるよう依頼された。`PROJECT_MEMORY.md`
第19節タスク#50/第21節を確認したところ、この4ファイルは物理的に同一の資料で、既に前回セッション
(2026-09-19、タスク#50)で全ページ文字起こし済み(`docs/research/quick-reference-guide-part{1,2}-
2026-09-19.md`等)であることが判明した。ただし第21.4節には、その時点の文字起こしが「中程度の
確信度」としていた未解決のCONTRADICTS項目が複数残っていた。

今回、同じPDFを`pdftoppm -r 400`で該当ページのみ高解像度(400dpi、1ページあたり約2300x3300px)
再展開し、`convert`で該当領域を直接クロップして再確認した結果、以下2点が高い確信度で解決した。

### 1. 天候パーセンテージ表の列見出し

クイックリファレンス書籍3頁の表を400dpiで再読した結果、列見出しは
**快晴・晴れ・曇り・雨・雪・荒天**(5列)であり、脚注「荒天＝大雨・雷雨・台風・大雪」が
明記されている。これは既存コード`remake_customer_share.BAD_WEATHER_VALUES`のコメントが
主張していた列見出し「快晴/大雨/雪/台風/荒天」(2026-09-19セッション時点の中解像度読み取りを
そのまま転記したもの)とも、同セッションの別の読み取り「快晴/曇り/雨/台風/荒天」とも異なる。
高解像度画像で「月|快晴|晴れ|曇り|雨・雪|荒天」という文字を直接確認済み(データ値も12ヶ月分
すべてが100に正確に合計する。旧文字起こしは7月/9月/12月の3行が100にならず`UNCERTAIN`
フラグ付きだった)。

### 2. 年間カレンダー(季節+平日/休日)表

同じ書籍3頁に「年間カレンダー」表があり、季節(冬期/夏期)と、月ごとの代表4日間
(1日〜4日)それぞれの平日/休日フラグを明記している。ほとんどの月は「平日・平日・平日・休日」
だが、1月(休日・平日・平日・休日)・5月(休日・休日・平日・休日)・8月(平日・休日・平日・休日)・
12月(平日・平日・休日・休日)の4ヶ月は追加の休日を持つ。

`reference_sim/conveni_sim/clock.py`の`SimulationClock.representative_day_type`は、
「day==4のみ休日」という単純化を採用しており、そのコメント自身が
「Keep this in the reference harness so it can be replaced if the guidebook contradicts it」
(攻略本が矛盾する証拠を出したら置き換えてよい)と明記していた。今回の再確認はまさにその
矛盾する証拠であり、単純化を修正する。

### 3. 営業時間5パターン(付随して再確認)

同じ書籍2頁の営業時間クロック図も高解像度で再確認した。パターン③は印字上「AM11:00〜AM2:00
(16時間営業)」であり、これは実測15時間で「16時間営業」というラベルと矛盾するが、
今回の再確認で「AM3:00」等のスキャン誤読ではなく、原本の印字自体がこの通りであることを
直接確認した。矛盾を黙って補正せず、印字通りに転記する。

## 決定

### `baseline_data.ANNUAL_CALENDAR`(新規)

`models.AnnualCalendarMonthEntry`(月・季節・4日分の平日/休日フラグ)を新設し、12ヶ月分の
CONFIRMED_OFFICIALデータとして`baseline_data.py`に追加した。

### `clock.py`の`representative_day_type`を`ANNUAL_CALENDAR`参照に変更

`(month, day) -> RepresentativeDayType`の辞書を`ANNUAL_CALENDAR`から構築し、従来の
「day==4のみ休日」ロジックを置き換えた。これにより`SimulationClock(month=1, day=1)`は
これまでの`WEEKDAY`ではなく`HOLIDAY`を返すようになる(1月1日、元日相当と推測されるが、
これはこのプロジェクト自身の推測であり原典に明記されているわけではない)。

### `remake_customer_share.BAD_WEATHER_VALUES`の訂正

列見出しの誤りを修正し、`{"雨", "雪", "雨・雪", "大雨", "雷雨", "台風", "大雪", "荒天"}`に
拡張した(旧`{"大雨", "雪", "台風", "荒天"}`の上位互換。既存の"大雨"/"雪"/"台風"を使う
呼び出し元・テストの挙動は変わらない)。

### `baseline_data.MONTHLY_WEATHER_PERCENTAGES`(新規)

`models.MonthlyWeatherPercentagesEntry`を新設し、12ヶ月分の天候パーセンテージ表を
CONFIRMED_OFFICIALデータとして追加した。全12行が100に正確に合計することをテストで検証する。
まだどこからも消費されない参照専用データ(`StoreVariant.total_area_tiles`等と同じパターン)。

### `baseline_data.BUSINESS_HOURS_PRESETS`(新規)

`models.BusinessHoursPresetEntry`を新設し、営業時間5パターン+24時間営業+臨時休業を
CONFIRMED_OFFICIALデータとして追加した。パターン③の表記矛盾(15時間なのに「16時間営業」)は
`printed_label`フィールドにそのまま転記し、補正しない。`operating_time.OperatingHours`を
再利用して実際の開閉時刻を保持するが、まだどこからも消費されない参照専用データ。

## テスト

- `test_baseline.py`: `ANNUAL_CALENDAR`の12ヶ月×4日全数チェック、`MONTHLY_WEATHER_
  PERCENTAGES`の全12行が100に合計すること、`BUSINESS_HOURS_PRESETS`の7エントリと
  パターン③の矛盾転記を検証する新規テスト4件。
- `test_baseline.py`(`ClockTests`): 旧「day==4のみ休日」前提のテストを、`ANNUAL_CALENDAR`
  全数チェック+3月(典型パターン)+1月(1日=休日の例外)の3テストに置き換え。
- `test_invariants.py`(`CalendarInvariantTests`): 14ヶ月ループの期待値を`ANNUAL_CALENDAR`
  から動的に導出するよう修正(以前はハードコードされた「平日3/休日1」を全月に適用していた)。
- `reference_sim`フルスイート726件パス/1件xfail(既存の無関係なxfail1件は変化なし)。

## 対象ファイル

- `reference_sim/conveni_sim/models.py`
- `reference_sim/conveni_sim/baseline_data.py`
- `reference_sim/conveni_sim/clock.py`
- `reference_sim/conveni_sim/remake_customer_share.py`
- `reference_sim/tests/test_baseline.py`
- `reference_sim/tests/test_invariants.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `game/`(Godotクライアント)側は一切変更していない。`clock.py`の平日/休日概念、天候
  パーセンテージ表、営業時間プリセットのいずれも、現時点で`game/`側にはこれを消費する
  仕組み(需要式の曜日補正、天候ロール機構、営業時間プリセット選択UI)が存在しないため、
  decision 0095/0127等と同じ「reference_simのみ先行、消費者ができてから配線」境界を踏襲する。
- 天候パーセンテージ表から実際に天候値をロールする機構(`weather`入力を生成する仕組み)は
  実装していない。この表は依然として外部から`weather`文字列を供給される側の参照データに
  留まる。将来この表からロールする機構を作る場合も、荒天バケット内のどの具体的な条件
  (大雨/雷雨/台風/大雪)が選ばれるかを決める式は原典に存在しないため、その部分は
  REMAKE_BALANCED_DEFAULTタグが必要になる。
- 季節(冬期/夏期)ラベル自体が何かのゲームロジックに影響するかは原典に明記がなく、
  未消費のまま保持している。
