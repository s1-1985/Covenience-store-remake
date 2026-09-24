# 0141: メニューUIアイコンの配線(タスク#71、メニューUIアセット統合 第1弾)

## 背景

タスク#67〜#70(什器・商品・店員・客の4パッケージ)を配線し終えた後、
ユーザーから次の方向として「メニューUI系アセットの配線」の選択があった。
`assets/raw/README.md`によれば、メニューUI・その他画面素材として5
パッケージ(`conveni_menu_fixtures_v1`, `conveni_menu_products_v1`,
`conveni_menu_staff_v1`, `conveni_additional_assets_v1`,
`conveni_remaining_assets_v1`)が存在する。

タスク#67〜#70の什器・商品・店員・客スプライトは「本プロジェクト独自の
新規デザイン」(ChatGPT生成、白縁除去修正版)だったが、この5パッケージは
質的に異なる: 各パッケージ自身のREADME(`conveni_menu_fixtures_v1/
README_CLAUDE.md`)が明記する通り、**攻略本の掲載アイコンページを実際に
切り出した**素材であり(「新規描き起こしではありません」)、manifest.json
の各エントリが`source_pdf_page`(掲載ページ番号)を持つ。これは
`CLAUDE.md`の証拠規律上、CONFIRMED_VISUAL(原作関連資料から直接読み取れる
情報)に該当し、タスク#67〜#70のREMAKE_BALANCED_DEFAULT素材とは
評価が異なる。

3パッケージ(`conveni_menu_fixtures_v1`/`_products_v1`/`_staff_v1`)を
実際に調査した結果、ID体系が本プロジェクトの既存データと極めて綺麗に
対応していることが判明した:
- `conveni_menu_fixtures_v1`(45種): IDが`fixture_catalog`の`catalog_id`と
  完全一致。`fixture_catalog`の全35件が過不足なくカバーされている
  (差分ゼロ)。未実装の什器(register_2〜4、コピー機、休憩室、屋内外
  ディスペンサー)向けアイコンが10種類「余剰」として含まれる——将来の
  什器カタログ拡張の材料になり得るが、今回は未使用のまま。
- `conveni_menu_products_v1`(27種): IDが`product_catalog`の`catalog_id`と
  完全一致。`product_catalog`の全26件が過不足なくカバーされている。
  「cash」(現金)が余剰1種——本プロジェクトには存在しない概念で未使用。
- `conveni_menu_staff_v1`(35種): タスク#69で確立した`staff_001`〜
  `staff_035`という同一の番号体系をそのまま維持している
  (README自身が明記: 「店員は staff_001〜staff_035 の既存番号を維持」)。

一方、`conveni_additional_assets_v1`/`conveni_remaining_assets_v1`
(店舗選択アイコン、広告アイコン、地面テクスチャ、町マップ関連、
ウィンドウ部材等)は、このVertical Sliceにまだ存在しない画面
(店舗選択画面、広告UI、町マップ画面)向けの素材であり、配線先となる
既存UI要素が一切ない。したがって今回はこの3パッケージ
(什器・商品・店員メニューアイコン)に限定した。

## 決定

### 既存OptionButtonへのアイコン付与

`game/scripts/main.gd`の既存3つのドロップダウン
(`fixture_catalog_option`/`product_catalog_option`/
`hire_candidate_option`)は、これまでテキストのみでカタログID・候補者名
などを表示していた。各ポピュレート関数(`_populate_fixture_catalog_
option()`/`_populate_product_catalog_option()`/`_refresh_hire_candidate_
option()`)の`add_item()`直後に`set_item_icon()`を追加し、対応する
32pxアイコンを表示するようにした。新しい画面や選択UIを追加するのでは
なく、既存のテキストドロップダウンにアイコンを添えるだけの最小限の
変更である。

店員候補のアイコンは、タスク#69で確立済みの位置ベース番号
(`store_view._staff_sprite_id_for_candidate()`、REMAKE_BALANCED_DEFAULT、
`staff_candidates`配列内の位置から`staff_%03d`を導出)をそのまま再利用し、
新たな対応表は発明していない——この面のみ、タスク#69由来の
REMAKE_BALANCED_DEFAULT前提を引き継ぐ。

### アイコンサイズは32px版を採用

パッケージは32/48/64/128pxの4サイズを提供する。ドロップダウンの
1行分の高さに収まるサイズとして32pxを選んだ——これは表示上の選択に
過ぎず、原作のメニューUIにおける実際の表示ピクセルサイズを主張する
ものではない。

### 素材の配置

`game/assets/menu_icons/fixtures/`・`products/`・`staff/`の3ディレクトリに
各パッケージの`icons_32/`を丸ごとコピーした(什器・商品は未使用の
「余剰」アイコンも含め全件、店員は35件全て)。

## テスト

- `reference_sim`フルスイート736件パス/1件xfail(新規コントラクトテスト
  1件)。今回はコード上のCONFIRMED_VISUAL評価の明記に加え、
  `fixture_catalog`/`product_catalog`の全エントリに対応するアイコン
  ファイルが実際にディスク上に存在することをファイルシステムレベルで
  検証する(コメントの記述だけでなく事実として)。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないためCIで
  検証。既存タスク#38 UIシナリオの`_ready()`呼び出し後、
  `fixture_catalog_option`/`product_catalog_option`/`hire_candidate_option`
  の全項目が実際に非nullのアイコンを持つことを検証する。

## 対象ファイル

- `game/assets/menu_icons/fixtures/*.png`(45ファイル)
- `game/assets/menu_icons/products/*.png`(27ファイル)
- `game/assets/menu_icons/staff/*.png`(35ファイル)
- `game/scripts/main.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `conveni_additional_assets_v1`/`conveni_remaining_assets_v1`(店舗選択・
  広告・地面・町マップ関連)は、対応する画面がこのVertical Sliceに
  まだ存在しないため今回対象外。
- 未実装の什器(register_2〜4等10種)・「cash」商品アイコンは、
  ファイルとしてはコピー済みだが、対応するカタログエントリが存在
  しないため未使用のまま。
- ドロップダウン以外の新規UI(グリッド状のアイコン選択画面等)は導入
  していない——既存のテキストドロップダウンへのアイコン追加のみ。
- これらのアイコン画像自体はCONFIRMED_VISUAL(攻略本からの直接切り出し)
  だが、それを32pxで表示するという選択自体は表示上の判断であり、
  原作の実際のUIピクセルサイズを主張するものではない。
