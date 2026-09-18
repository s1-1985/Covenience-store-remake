# 0100: `game/`(Godot)の店舗グリッド寸法・動線を既存研究(攻略本準拠)に合わせる(タスク#31)

## 背景

ユーザーから「初代ザ・コンビニを再現するんやぞ？さっきのモック画面も、
入口と出口が離れてるとか、本来はあり得んからな」という直接の指摘を受けた。
確認したところ、`game/data/vertical_slice.json`の店舗グリッドは以下の
問題を抱えていた:

1. **`width_tiles=7, height_tiles=6`という寸法が、いかなる研究資料にも
   裏付けのない、単なる仮置きの数値だった**。一方で`reference_sim`側には
   既にこの問題を解決済みの確定データが存在していた:
   `reference_sim/conveni_sim/baseline_data.py`の`STORE_VARIANTS`は
   `docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md`
   第3節/第9節(2026-09-17追記)で記録された通り、攻略本の店舗データ表
   (書籍106-109ページ)から`small_top.editable_floor = (5, 8)`タイルを
   **CONFIRMED_OFFICIAL**として転記済みであり、さらに以前のセッションで
   「衝突する内容は攻略本準拠」という明示的なユーザー許可のもとこの数値へ
   解決されていた。この確定済みデータがこのファイルへ移植されずに
   放置されていた。
2. **入口`[0,0]`と出口`[0,10]`が店舗の対角線上、離れた位置に配置されて
   いた**。これは`docs/research/store-dimensions-and-fixture-costs-2026-09-05.md`
   第5節の通路幅観測(最低1マス通路、レジ前2マス、出入口前2マス、循環
   動線推奨)や`docs/research/strategy-guide-full-decode-2026-09-16.md`
   第20.3節の動線ガイダンスと整合しない、根拠のない配置だった。

## 決定

### 店舗寸法

`STORE_VARIANTS['small_top'].editable_floor = (5, 8)`(タイル、
`subcells_per_tile=2`のため実際のサブセルグリッドは10×16)を
`vertical_slice.json`の`store.width_tiles`/`height_tiles`にそのまま
移植した。

寸法の裏付けと限界を`size_tier_evidence_note`に明記した:

- 攻略本は同じ「小型」サイズについて2つの向き(5×8と8×5)を掲載しており、
  どちらが「上段」でどちらが「下段」に対応するかという対応関係自体は
  research note側でも未確定(推測)であることを明記した上で、
  `small_top`(5×8)を採用した。
- 旧`7x6`のプレースホルダーは、このデータと一度も突き合わせされずに
  放置されていたことを明記し、supersedeした。

### 入口・出口配置

入口・出口を対角の隅ではなく、**同じ(手前側の)壁**に配置し直した
(`entry_subcell=[0,0]`, `exit_subcell=[8,0]`)。根拠は
`store-dimensions-and-fixture-costs-2026-09-05.md`第5節の通路幅観測と、
`strategy-guide-full-decode-2026-09-16.md`第20.3節の循環動線・デッドエンド
最小化ガイダンス。

新しいグリッド上でチェックアウト/棚2つ/入口/出口を配置し直す際、以下を
Pythonで書いた4方向BFS(`store_layout.gd`の`_fixture_configs_are_valid`/
`has_path`と`vertical_slice_simulation.gd`の`_required_routes_are_reachable()`
を模した検証スクリプト)で事前検証してから実ファイルへ反映した:

- 入口→(`visit_plan_product_ids`の順で)各棚のinteraction→レジのinteraction
  →出口、の経路が全て到達可能であること。
- レジ前・出入口前に最低限の空きセルがあること(通路幅観測に基づく)。
- スタッフ開始位置(`start_subcell`)が壁に埋まっていないこと。
- `headless_smoke.gd`内の全テストケース(什器購入・拒否・リロケーション
  テストで使われる座標)が新グリッド境界内に収まり、意図した衝突/非衝突
  条件を引き続き満たすこと。

### `headless_smoke.gd`のハードコード座標の全面更新

旧グリッド(7×6タイル=14×12サブセル)を前提にしていた全ての`Vector2i(...)`
リテラルを`grep`で洗い出し、それぞれのテストが検証している意味(成功配置
なのか、意図的な拒否テストなのか)を個別に確認した上で座標を更新した。
座標の値に依存せず`_any_restock_task_active()`ゲートなどより早い段階で
拒否が発生する2箇所は、値が無関係であることを確認した上で意図的に
変更しなかった。

### 描画スケールの調整

`game/scripts/store_view.gd`の`SUBCELL_PIXELS`を`42.0`から`36.0`へ変更した。
新グリッド(10×16サブセル)は`main.tscn`のStoreView配置(原点(40,100)、
ステータスパネルがx=690から開始)と1280×720ウィンドウの制約下で、
`36.0`なら幅360px/高さ576pxに収まり、ステータスパネルとの重なりや
ウィンドウ下端からのはみ出しを避けられることを計算で確認した。

### `store_value.gd`のコメント整理

`STORE_SIZE_VALUE_MULTIPLIER`(`small`/`medium`/`large` → 1.5/1.65/1.8)は
本タスクで解決した`editable_floor`寸法(5×8など)とは**別の**、攻略本
「オールテクニックガイド」誘致関連ページが独自に掲載する
「10×10=1.5・12×12=1.65・14×14=1.8」という寸法表記に由来する値であり、
`reference_sim/conveni_sim/store_value.py`側は元々この点を明記していたが
Godot側のコメントには反映されていなかった。両者を混同しないよう、
Godot側のコメントにも同じ注記を追加した(値そのものは変更していない)。

## 検証

- ダウンロード済みのGodot 4.3公式バイナリを使い、
  `godot --headless --path game --script res://scripts/headless_smoke.gd`
  を実行し、新グリッド上で全テストがPASSすることを確認した
  (`Vertical-slice headless smoke passed in 515 steps.`)。
- Xvfb + ソフトウェアラスタライズで`main.tscn`を実際にレンダリングし、
  スクリーンショットで入口/出口が同じ壁に近接して配置され、
  チェックアウト・棚2つ・ステータスパネルがウィンドウ内に正しく収まって
  いることを視覚的に確認した。
- `reference_sim/tests`のフルスイート(649件、期待される1件の
  `expectedFailure`を除き全てPASS)、および
  `test_game_vertical_slice_contract.py`の30件
  (`test_entry_shelf_checkout_exit_route_is_reachable`含む)が
  引き続きPASSすることを確認した。

## 実装ファイル

- `game/data/vertical_slice.json`: `store.width_tiles`/`height_tiles`/
  `exit_subcell`/`size_tier_evidence_note`、`fixtures`配列(checkout-1/
  shelf-1/shelf-2の座標)、`staff.members`の`start_subcell`を更新。
- `game/scripts/headless_smoke.gd`: 新グリッドに合わせて全ハードコード
  座標を更新。
- `game/scripts/store_view.gd`: `SUBCELL_PIXELS`を42.0→36.0に変更。
- `game/scripts/domain/store_value.gd`: `STORE_SIZE_VALUE_MULTIPLIER`の
  コメントに、寸法表記の混同を避けるための注記を追加(値は不変)。

## タスク#31の完了

店舗グリッドを攻略本準拠のCONFIRMED_OFFICIALな寸法(5×8タイル)へ置き換え、
入口・出口を同じ壁に隣接配置することでユーザー指摘の不自然な動線を解消した。
既存の全自動テストがPASSし、実際のGodotバイナリによる実行・視覚確認でも
新レイアウトが正しく機能することを確認したため、タスク#31を完了とする。
