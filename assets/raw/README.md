# 生成アセット素材置き場(未統合・ドラフト)

2026-09-22、ChatGPTで生成した画像アセット一式をそのままここへ保管した。**まだゲーム(`game/`)へは一切配線していない。** 実装時にここから取り出して使うための一時置き場。

2026-09-23、客・店員・什器・商品の4パッケージについて、初回版(v1)に誤りがあったため修正版(v2、白縁除去)に差し替えた。旧パッケージ(`konbini_PS1_fixtures_ONLY/`, `the_conveni_staff_assets_draft_for_Claude/`, `the_conveni_customer_assets_draft_for_Claude/`, `konbini_product_assets_for_claude/`)はリポジトリから削除済み。町マップ/建物パッケージ(`conveni_map_assets_v2/`)は今回の差し替え対象外、そのまま。

2026-09-23(同日中)、`docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md`のブリーフをもとに、什器・商品の2パッケージを再度v3として作り直し、差し替えた。旧`fixtures_v2/`・`products_v2/`はリポジトリから削除済み。客・店員(`staff_v2/`, `customer_v2/`)・町マップ/建物(`conveni_map_assets_v2/`)は今回の差し替え対象外、そのまま。

各パッケージの詳細は、パッケージ内自身の README / handoff ファイルを参照すること(重複を避けるためここには転記しない)。

## 収録パッケージ

| ディレクトリ | 内容 | 参照元ブリーフ | パッケージ内ドキュメント |
|---|---|---|---|
| `conveni_map_assets_v2/` | 町マップ用の地形・建物タイル | `docs/assets/chatgpt-building-sprite-brief-2026-09-22.md` | `README_JA.md`, `README_V2_JA.md`, `CLAUDE_HANDOFF.md`, `CLAUDE_HANDOFF_V2.md` |
| `conveni_fixtures_remake_v3/` | 店内什器(棚・ワゴン等)のスプライト(v3、ブリーフに基づく作り直し版) | `docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md` | `README_CLAUDE.md`, `reference/claude_brief.md` |
| `staff_v2/` | 店員スプライト(v2、白縁除去修正版) | 客層/店員リストは`baseline_data.py`の`STAFF_CANDIDATES` | `START_HERE_JA.md`, `staff/README_JA.md` |
| `customer_v2/` | 客スプライト(21客層、v2、白縁除去修正版) | 客層リストは会話ログで提示済み(`CUSTOMER_ARCHETYPES`) | `START_HERE_JA.md`, `customer/README_JA.md` |
| `conveni_products_remake_v3/` | 商品オーバーレイ(什器本体は含まない、v3、ブリーフに基づく作り直し版) | `docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md` | `README_CLAUDE.md`, `reference/claude_brief.md` |

## 注意事項

- これらは`PROJECT_MEMORY.md`第1節(2026-09-21付)の個人利用限定の方針のもとで作成された素材。
- まだ`game/`側のアセットパイプライン・命名規則・実際の配置ロジックとの整合性は未検証。実装時に各パッケージのマニフェスト(`category_manifest.json`等)とゲーム側のID(`category_id`, `building_id`, `customer_archetype_id`等)の対応付けが必要。
- 各パッケージが「これで確定」と主張していても、`CLAUDE.md`の証拠規律上はこれらの見た目自体がCONFIRMED_OFFICIALな原作再現ではなく、あくまで新規デザインのドラフトであることに注意。
