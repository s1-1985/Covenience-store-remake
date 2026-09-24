# 0139: 店員スプライトの配線(タスク#69、アセット統合 第3弾)

## 背景

タスク#68(商品オーバーレイ)のマージ後、ユーザーから次の配線対象として
「店員スプライトの配線(推奨)」の選択があった。`assets/raw/staff_v2/staff/`
は白縁除去修正版v2の店員パッケージで、35人分の匿名の歩行スプライト
(`staff_001`〜`staff_035`、各4方向×2フェーズ=280枚、160×160px RGBA、
足元基準アンカー(80,154))を収録する。

`game/`側の`StaffState`には既にタスク#56で`candidate_id`フィールドが
存在し(`vertical_slice.json`の`staff`/`staff_candidates`と紐付け済み)、
`try_procure_product()`の`catalog_id`のような配線漏れは今回は存在しない
——`store_view.gd`側の表示ロジックを追加するだけで済んだ。

一方で、このパッケージ自身は35枚の歩行スプライトを35人の実名候補
(`staff_candidates`)のどれとも紐付けていない——各スプライトに氏名は
描かれておらず、`reference_faces/`が同じ攻略本ページ(127〜133ページ)
から復元した顔写真とスプライトの対応表も一切収録されていない。
`STAFF_CANDIDATES`(`reference_sim/conveni_sim/baseline_data.py`)の
コメントが同じページ範囲(127〜133ページ)からの直接転記であると
明記していることから、掲載順で対応している可能性はあるが、これは
未検証の推測であり、`CLAUDE.md`の証拠規律上CONFIRMEDとして扱うことは
できない。

## 決定

### 候補の配列内位置によるスプライト割り当て(表示専用)

氏名とスプライトの確認済み対応表が存在しない以上、タスク#67/#68の
表示専用フォールバックと同じ判断で、`staff_candidates`配列内の位置
(0始まりindex+1)をそのまま`staff_%03d`に変換して割り当てる
(`_staff_sprite_id_for_candidate()`)。これは「`staff_candidates[N]`が
スプライト`staff_(N+1)`に描かれた本人である」という主張ではなく、
各候補が同じ人物として一貫した見た目で表示されるようにするための、
本プロジェクト独自のREMAKE_BALANCED_DEFAULT表示規約である。

### 静止フレーム(phase "A")固定

パッケージは歩行の2コマ差分(A/B)のみを収録し、専用の待機ポーズは
存在しない。このゲームはtick駆動のシミュレーションであり、他のどの
描画要素にもリアルタイムのアニメーション(delta-time駆動の切り替え)
は存在しないため、A/Bを時間経過で切り替えるタイミング規約を新たに
発明するのではなく、常にphase "A"を使う(REMAKE_BALANCED_DEFAULT、
最小実装)。

### 直近の移動に基づく向きの推定

原典には店員の画面上の向きに関する確認済みルールが存在しないため、
`_staff_facing_direction()`は各店員IDごとに直近の`position`を記録し、
差分ベクトルの主成分(x/yどちらの絶対値が大きいか)から
down/left/right/up のいずれかを選ぶ(タイの場合はy方向優先)。
位置が変化しない場合(アイドル中など)は直前に解決した向きを維持し、
記録がない初回は"down"を既定値とする。これも本プロジェクト独自の
REMAKE_BALANCED_DEFAULT表示規約であり、原作の向き決定ロジックの
再現ではない。

### 足元アンカーに基づく配置

manifestが明記する足元アンカー(80,154)/(160,160)を比率化し
(`STAFF_SPRITE_ANCHOR_FRACTION`)、既存の`_cell_center(position)`
(客・什器の基準点と同じ)にスプライトの足元が来るよう配置する。
描画サイズ(`STAFF_SPRITE_SIZE_PX`、1マス分の2倍)も含め、原作の
画面上表示スケールを示す確認済み資料がないため、いずれも
REMAKE_BALANCED_DEFAULTの表示上の選択である。

## テスト

- `reference_sim`フルスイート734件パス/1件xfail(新規コントラクトテスト
  1件)。タスク#67/#68と同じく、コードコメント+テストアサーションで
  REMAKE_BALANCED_DEFAULTタグの3点セットを満たす(この機能は
  `vertical_slice.json`側に新規データフィールドを追加しないため、
  タスク#67と同様evidence_noteはコード側のみ)。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないため
  CIで検証。追加した検証内容:
  - `staff_candidates`の全35件について、配列内位置から期待される
    `staff_%03d`への解決が正しいこと、かつ4方向すべてで実際に
    テクスチャが読み込めること。
  - 空/未知の`candidate_id`がスプライトなし(空文字列)に解決される
    こと。
  - 実際のロースターメンバー`staff-1`(候補`manda_machiko`、配列内
    5番目)が期待通り`staff_005`に解決されること(生の関数単体だけ
    でなく実データ経由でのエンドツーエンド確認)。
  - `_staff_facing_direction()`を合成座標で直接演習
    (初回は既定で"down"、+x移動で"right"、位置不変で直前の向きを
    維持、-y移動で"up")——特定の移動シナリオの発生に依存しない、
    純粋関数としての検証。

## 対象ファイル

- `game/assets/staff/*.png`(280ファイル、35人×4方向×2フェーズ)
- `game/scripts/store_view.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 客スプライト、町マップ・建物タイル、メニューUI系5パッケージの配線は
  今回対象外。それぞれ別タスクとして扱う。
- 歩行アニメーション(A/B切り替え)は未実装——常にphase "A"固定。
- `candidate_id`から`staff_candidates`内の位置への解決は氏名と
  スプライトの確認済み対応ではない——将来、より強い証拠(例:
  攻略本のスプライトシート自体に氏名が併記されている等)が見つかれば
  差し替える前提の暫定表示規約である。
- `reference_sim`側への同等ロジックの移植は行っていない
  ——`reference_sim`にはそもそも描画層が存在しない。
- これらのスプライト自体は`CLAUDE.md`の証拠規律上、原作の確認された
  見た目(CONFIRMED_OFFICIAL)ではなく、あくまで本プロジェクト独自の
  新規デザインである(タスク#67/#68と同じ評価)。
