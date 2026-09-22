# Claude引き継ぎ v2

まずREADME_V2_JA.mdとPACKAGE_INDEX.jsonを読んでください。建物52種＋地形・インフラ121種＝173種です。

1. 既存の建物パス・ID・寸法は維持しています。
2. 追加素材はterrain/manifest.jsonから読み込みます。画像fileはパッケージルート相対です。atlas.jsonのmeta.imageはそのJSONのあるディレクトリ相対です。
3. source_cropsが原寸正本、tiles_64は1セル表示の確認用。推定占有数をゲームの確定仕様として扱わないでください。
4. 新しいIDはmap_で始まります。土地・水・道路・線路等の地面込みPNGなので透過建物より先に描画します。
5. connections_verifiedとseamless_verifiedはfalseです。端点座標、道路幅、岸の色を実際の配置で検証・調整してから接続規則を設定してください。
6. 元の生成建物の真上視点未達はCLAUDE_HANDOFF.mdの通りです。

採否判断の見直しはterrain/selection_report.csvと原画像の行列番号で追跡できます。切り出し矩形は左上含む・右下含まないXYXYです。
