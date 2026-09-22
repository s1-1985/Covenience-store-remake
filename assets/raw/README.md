# 生成アセット素材置き場(未統合・ドラフト)

2026-09-22、ChatGPTで生成した画像アセット一式をそのままここへ保管した。**まだゲーム(`game/`)へは一切配線していない。** 実装時にここから取り出して使うための一時置き場。

各パッケージの詳細は、パッケージ内自身の README / handoff ファイルを参照すること(重複を避けるためここには転記しない)。

## 収録パッケージ

| ディレクトリ | 内容 | 参照元ブリーフ | パッケージ内ドキュメント |
|---|---|---|---|
| `conveni_map_assets_v2/` | 町マップ用の地形・建物タイル | `docs/assets/chatgpt-building-sprite-brief-2026-09-22.md` | `README_JA.md`, `README_V2_JA.md`, `CLAUDE_HANDOFF.md`, `CLAUDE_HANDOFF_V2.md` |
| `konbini_PS1_fixtures_ONLY/` | 店内什器(棚・ワゴン等)のスプライト、回転バリエーション込み | (什器リストは未発注、経緯不明) | `README_Claude.md` |
| `the_conveni_staff_assets_draft_for_Claude/` | 店員スプライト(スプライトシート・行ストリップ形式) | (客層/店員リストは`baseline_data.py`の`STAFF_CANDIDATES`) | `README_for_Claude.md` |
| `the_conveni_customer_assets_draft_for_Claude/` | 客スプライト(21客層 × 4方向 × 2フレーム) | 客層リストは会話ログで提示済み(`CUSTOMER_ARCHETYPES`) | `README_for_Claude.md` |
| `konbini_product_assets_for_claude/` | 商品オーバーレイ(什器本体は含まない、1x1基本単位) | 商品カテゴリリストは会話ログで提示済み(`baseline_data.py`のカテゴリ表) | `README_for_Claude.md` |

## 注意事項

- これらは`PROJECT_MEMORY.md`第1節(2026-09-21付)の個人利用限定の方針のもとで作成された素材。
- まだ`game/`側のアセットパイプライン・命名規則・実際の配置ロジックとの整合性は未検証。実装時に各パッケージのマニフェスト(`category_manifest.json`等)とゲーム側のID(`category_id`, `building_id`, `customer_archetype_id`等)の対応付けが必要。
- 各パッケージが「これで確定」と主張していても、`CLAUDE.md`の証拠規律上はこれらの見た目自体がCONFIRMED_OFFICIALな原作再現ではなく、あくまで新規デザインのドラフトであることに注意。
