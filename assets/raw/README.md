# 生成アセット素材置き場(未統合・ドラフト)

2026-09-22、ChatGPTで生成した画像アセット一式をそのままここへ保管した。**まだゲーム(`game/`)へは一切配線していない。** 実装時にここから取り出して使うための一時置き場。

2026-09-23、客・店員・什器・商品の4パッケージについて、初回版(v1)に誤りがあったため修正版(v2、白縁除去)に差し替えた。旧パッケージ(`konbini_PS1_fixtures_ONLY/`, `the_conveni_staff_assets_draft_for_Claude/`, `the_conveni_customer_assets_draft_for_Claude/`, `konbini_product_assets_for_claude/`)はリポジトリから削除済み。町マップ/建物パッケージ(`conveni_map_assets_v2/`)は今回の差し替え対象外、そのまま。

2026-09-23(同日中)、`docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md`のブリーフをもとに、什器・商品の2パッケージを再度v3として作り直し、差し替えた。旧`fixtures_v2/`・`products_v2/`はリポジトリから削除済み。客・店員(`staff_v2/`, `customer_v2/`)・町マップ/建物(`conveni_map_assets_v2/`)は今回の差し替え対象外、そのまま。

2026-09-24、5パッケージを追加した(`conveni_menu_fixtures_v1/`, `conveni_menu_products_v1/`, `conveni_menu_staff_v1/`, `conveni_additional_assets_v1/`, `conveni_remaining_assets_v1/`)。**これらは既存の什器/商品/店員スプライトの置き換えではない。** 各パッケージ自身のREADMEが「メニュー表示専用、店内・町マップのスプライトを置き換えないでください」「既存セットは上書きしない、IDを追加登録する」と明記しており、攻略本・プレイ動画からの直接切り出し(AI再生成ではない)によるメニューUI用アイコン・広告/店舗選択アイコン・入口/地面/枠パーツ等の**別カテゴリ**として追加した。既存カテゴリの削除は行っていない。

各パッケージの詳細は、パッケージ内自身の README / handoff ファイルを参照すること(重複を避けるためここには転記しない)。

## 収録パッケージ

### ワールド表示用(店内・町マップに配置するスプライト)

| ディレクトリ | 内容 | 参照元ブリーフ | パッケージ内ドキュメント |
|---|---|---|---|
| `conveni_map_assets_v2/` | 町マップ用の地形・建物タイル | `docs/assets/chatgpt-building-sprite-brief-2026-09-22.md` | `README_JA.md`, `README_V2_JA.md`, `CLAUDE_HANDOFF.md`, `CLAUDE_HANDOFF_V2.md` |
| `conveni_fixtures_remake_v3/` | 店内什器(棚・ワゴン等)のスプライト(v3、ブリーフに基づく作り直し版) | `docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md` | `README_CLAUDE.md`, `reference/claude_brief.md` |
| `staff_v2/` | 店員スプライト(v2、白縁除去修正版) | 客層/店員リストは`baseline_data.py`の`STAFF_CANDIDATES` | `START_HERE_JA.md`, `staff/README_JA.md` |
| `customer_v2/` | 客スプライト(21客層、v2、白縁除去修正版) | 客層リストは会話ログで提示済み(`CUSTOMER_ARCHETYPES`) | `START_HERE_JA.md`, `customer/README_JA.md` |
| `conveni_products_remake_v3/` | 商品オーバーレイ(什器本体は含まない、v3、ブリーフに基づく作り直し版) | `docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md` | `README_CLAUDE.md`, `reference/claude_brief.md` |

### メニューUI・その他画面素材(攻略本・プレイ動画からの直接切り出し、AI再生成ではない)

| ディレクトリ | 内容 | パッケージ内ドキュメント |
|---|---|---|
| `conveni_menu_fixtures_v1/` | 什器選択メニュー用アイコン(45種、攻略本切り出し) | `README_CLAUDE.md` |
| `conveni_menu_products_v1/` | 商品選択メニュー用アイコン(27種、攻略本切り出し) | `README_CLAUDE.md` |
| `conveni_menu_staff_v1/` | 店員選択メニュー用顔アイコン(35種、staff_001〜035対応、攻略本切り出し) | `README_CLAUDE.md` |
| `conveni_additional_assets_v1/` | 店舗選択アイコン(6種)、広告アイコン(5種)、入口部材、地面テクスチャ、外周線、状態表示(たばこ/酒/薬)、カーソル(計28点) | `README_CLAUDE.md` |
| `conveni_remaining_assets_v1/` | `conveni_additional_assets_v1`への追加分(町マップの自店舗マーク、建物誘致メニュー18枠、広告チェック状態、ウィンドウ9分割部材、火災アニメ・飛行船の新規生成候補) | `README_CLAUDE.md` |

## 注意事項

- これらは`PROJECT_MEMORY.md`第1節(2026-09-21付)の個人利用限定の方針のもとで作成された素材。
- まだ`game/`側のアセットパイプライン・命名規則・実際の配置ロジックとの整合性は未検証。実装時に各パッケージのマニフェスト(`category_manifest.json`等)とゲーム側のID(`category_id`, `building_id`, `customer_archetype_id`等)の対応付けが必要。
- 各パッケージが「これで確定」と主張していても、`CLAUDE.md`の証拠規律上はこれらの見た目自体がCONFIRMED_OFFICIALな原作再現ではなく、あくまで新規デザインのドラフトであることに注意。
