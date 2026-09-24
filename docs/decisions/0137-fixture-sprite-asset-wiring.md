# 0137: 什器スプライトの配線(タスク#67、アセット統合 第1弾)

## 背景

ユーザーから、天候・土地代・怒った客ペナルティ・通路幅の4件(PR #241〜#243)を
mainへマージした後、次の作業方針として「画像・音声アセットの配線作業へ」との
選択があった。タスク#46で確立された標準方針は「システム面を完全に作り込んで
から、画像・音声を生成・配線する」であり、今セッションで多数のシステム面の
修正が完了したため、このタイミングでの着手は妥当と判断した。

`assets/raw/README.md`を確認したところ、`conveni_fixtures_remake_v3/`
(什器スプライト、v3、ブリーフに基づく作り直し版)が既に用意されており、
`manifest.json`のアセットID一覧が`game/data/vertical_slice.json`の
`fixture_catalog`の`catalog_id`一覧と**完全に一致**していた(35件全て、
差分ゼロ)。什器什器パッケージは他のアセット種別(商品・店員・客・町マップ)
より配線の見通しが良く、依存関係も単純(`store_view.gd`の`_draw_fixtures()`
のみが対象)だったため、今回のスコープを什器スプライトの配線に限定した。

`game/`プロジェクトにはこれまで画像アセットが一切存在せず(`store_view.gd`は
`_draw()`内で色付き矩形のみを描画する完全なプレースホルダー実装だった)、
これがこのプロジェクト初のアセット統合作業となる。

## 決定

### スプライトファイルの配置

`assets/raw/conveni_fixtures_remake_v3/sprites/`から、`fixture_catalog`の
35カタログID全てに一致するPNGファイルを`game/assets/fixtures/`にコピーした
(Godotは`res://`配下のファイルしか読み込めないため、プロジェクト外の
`assets/raw/`から直接参照することはできない)。ファイル名はカタログIDと
完全一致(`<catalog_id>.png`)。

### `store_view.gd`のテクスチャ描画

`_draw_fixtures()`を、可能な場合はテクスチャを`draw_texture_rect()`で
描画し、テクスチャが見つからない場合は既存の色付き矩形+ラベル描画に
フォールバックするよう変更した。`_fixture_texture(catalog_id)`が
`res://assets/fixtures/<catalog_id>.png`を遅延読み込み・キャッシュする。
ピクセルアートがぼやけないよう、ノードの`texture_filter`を
`TEXTURE_FILTER_NEAREST`に設定した。

### 什器カタログシステム以前の3什器(`checkout-1`/`shelf-1`/`shelf-2`)への視覚的フォールバック

タスク#39/#41以前から存在するこの3什器には`catalog_id`が一切付与されて
おらず(カタログシステム導入以前のデータ)、これらの見た目をどうするか
という判断が必要だった。`FALLBACK_VISUAL_CATALOG_ID_BY_KIND`
(`{"checkout": "register_1", "shelf": "medium_ambient_shelf"}`)により、
足跡(footprint)が完全に一致する既存カタログスプライトを表示専用の
代役として割り当てた(`register_1`はカタログ未登録だが什器パッケージ内に
スプライト自体は存在する、`medium_ambient_shelf`は既存カタログの一員)。
これは「これらの什器が実際にそのカタログ品目である」という主張では
なく、単に矩形の代わりに妥当なサイズのスプライトを表示するための
表示専用選択であることを明記した。

## テスト

`headless_smoke.gd`の既存タスク#38経済UIシナリオ(`main.tscn`を実際に
シーンツリーに追加する唯一のテスト)に、`fixture_catalog`の全35エントリ
+フォールバック用`register_1`について、`StoreView._fixture_texture()`が
実際に非nullのテクスチャを返すことを検証するチェックを追加した(ファイル
存在チェックだけでなく、CI上のGodotエディタが実際にテクスチャとして
インポートできることまで確認する)。

- `reference_sim`フルスイート731件パス/1件xfail(この変更は`game/`のみ、
  Pythonコード変更なし)。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないため
  CIで検証(このタスクの性質上、テクスチャの実読み込みはCI環境でしか
  確認できない)。

## 対象ファイル

- `game/assets/fixtures/*.png`(36ファイル、什器35種+フォールバック用
  `register_1`)
- `game/scripts/store_view.gd`
- `game/scripts/headless_smoke.gd`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 商品オーバーレイ(`conveni_products_remake_v3/`)、店員スプライト
  (`staff_v2/`)、客スプライト(`customer_v2/`)、町マップ・建物タイル
  (`conveni_map_assets_v2/`)、メニューUI系5パッケージの配線は今回
  対象外。それぞれ別タスクとして扱う。
- 什器の回転(`try_rotate_fixture_clockwise`)時のスプライト向き変更は
  未対応——回転しても同じテクスチャをそのまま描画する(向きに応じた
  スプライトバリアントは`manifest.json`側に用意されていない)。
- これらのスプライト自体は`CLAUDE.md`の証拠規律上、原作の確認された
  見た目(CONFIRMED_OFFICIAL)ではなく、あくまで本プロジェクト独自の
  新規デザイン(`PROJECT_MEMORY.md`第1節、2026-09-21付方針のもとで
  作成)である。
