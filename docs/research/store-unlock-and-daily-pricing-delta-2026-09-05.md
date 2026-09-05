# 初代PS/SS 店舗解禁・価格日次スナップショット追加調査 2026-09-05

対象: 1997 PS/SS『ザ・コンビニ ～あの町を独占せよ～』のみ。

目的: 攻略本到着待ちの間に、既存Gitに未記録だった店舗タイプの初期選択制限、向き、価格変更の需要反映タイミング、最低地価を回収する。続編の数値表は採用しない。

## Evidence labels
- `SS-DIRECT-PLAY`: 初代SS版を明示した実プレイ記録。
- `PS-DIRECT-PLAY`: 初代PS版を明示した長期実プレイ記録。
- `FIRST-TITLE-WIKI`: PS/SS初代専用Wiki。
- `CROSS-SOURCE-INFERENCE`: 複数ソースの組み合わせから強く示唆されるが、単一画面/表で未確定。

## 1. 初級開始時は最小店舗だけ建設可能（SS）

SS版の初級開始直後を写真付きで追ったプレイ記録では、店舗タイプ選択時に:

- 「はじめはいちばん小さいお店」
- 「大きなお店はまだ作れない」

と明記される。

Source:
- https://mii5.seesaa.net/article/200802article_5.html

判定: `SS-DIRECT-PLAY`

実装上の重要点:
- 3サイズすべてを最初から常時選択可能としてはいけない可能性が高い。
- 少なくともSS初級の開始直後は最小サイズのみが有効。
- 中型/大型の正確な解禁条件は未回収。

```text
StoreSizeAvailability {
  scenario: beginner,
  platform: SS,
  at_game_start: [small],
  medium_unlock: unresolved,
  large_unlock: unresolved
}
```

## 2. 店舗の向きは縦型・横型の2種類（SS）

同じSS初級プレイ記録は、店舗タイプ選択時に「店の向きは2種類（縦型と横型）」と明記する。

Source:
- https://mii5.seesaa.net/article/200802article_5.html

判定: `SS-DIRECT-PLAY`

既存PSスクリーンショットでは店舗候補が2行×3列、計6個表示される。これと組み合わせると、

```text
3 size classes × 2 orientations = 6 store variants
```

という既存仮説を強く補強する。

ただし、PS画面の各列が必ず small / medium / large の順であることは、攻略本または各候補を選択した直接画面で最終確認する。

判定: `CROSS-SOURCE-INFERENCE`

## 3. PS上級長期プレイでは開始直後から中型店を建設できる例がある

初代PS版の上級長期プレイ記録では、上級開始後の本店について「最初から中型店です」と記録される。その後の新規出店でも「最初から中型でオープン」という記録がある。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

判定: `PS-DIRECT-PLAY`

これはSS初級の「開始時は小型のみ」と矛盾するように見えるが、以下のどれかは未解決:
- シナリオごとに初期解禁状態が違う
- 前シナリオのクリア/累積進行で店舗サイズが解禁される
- PS/SS差がある
- 当該PSセーブ側の進行フラグを引き継いでいる

したがって、現時点で `medium_unlock_condition` を推測固定しない。

攻略本で最優先確認する項目:
1. 小/中/大の出現・解禁条件
2. 新規建設と改築で解禁条件が同じか
3. シナリオ間で解禁を引き継ぐか
4. PS/SS差

## 4. 価格変更はその日の客入りへ即時反映されない（SS）

SS版の詳細な実プレイ記録には「価格設定のズル技」が記載されている。

内容を仕様へ還元すると:
- 商品価格を変更しても、その変更は同じ日の客の動向へ影響しない。
- 日付変更直前に安値へ変更すると、次の日の客入りは安値側の条件で決まる。
- 日付変更直後に高値へ戻しても、その日の客入りは安値条件のまま維持される。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

判定: `SS-DIRECT-PLAY`

これは既に回収済みの「日付変更時に顧客独占率が更新され、その日の客入りを決める」挙動を強く補強する。

実装候補:

```text
atDateBoundary():
  dailyCustomerDemandSnapshot = calculateCustomerDemand(
    priceSettings,
    popularity,
    cleanliness,
    service,
    assortment,
    businessHours,
    weather,
    competition,
    surroundingPopulation
  )

onPriceChangedDuringDay():
  sellingPrice = newPrice
  dailyCustomerDemandSnapshot = unchanged
```

注意:
- 天候変化時には顧客独占率が再計算されるという別証拠があるため、完全に「日次1回だけ」とはしない。
- 価格変更自身が日中の再計算トリガではない、という証拠として扱う。
- Remakeでこのズル技を完全再現するかは後で忠実再現/QoLのdecisionにするが、Phase 1では元挙動を記録しておく。

## 5. 最低価格の土地は20,000,000円（初代Wiki）

初代PS/SS専用Wikiのゲームモード攻略は、初級攻略の小ネタとして「最安値の2000万円の土地」を明記する。

Source:
- https://wikiwiki.jp/theconveni1/ゲームモード攻略

判定: `FIRST-TITLE-WIKI`

したがって少なくともゲーム開始周辺の土地マスター/地価系には:

```text
observed_min_land_price_yen = 20_000_000
```

という直接的な初代根拠を持てる。

ただし:
- 全シナリオで常に20,000,000円が絶対下限か
- 年数経過後にも理論下限として残るか
- GavasのPS初級スクリーンショットで200,000,000→180,000,000となった特定区画が実際に20,000,000円だったか

は別問題なので断定しない。

## 6. 中型改築12,000,000円との整合

初代PS中級長期プレイでは、中型への改築に12,000,000円が必要と明記される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

これは既存Gitで回収済みの値であるため新規数値としては追加しないが、店舗解禁調査に重要な補助証拠となる。

同記録ではゲーム中盤に全店舗を中型へ順次改築しており、資金さえあれば繰り返し改築できる描写がある。一方、中型の「最初の解禁条件」は明記されない。

## 7. 続編データの混入禁止を再確認

検索では『ザ・コンビニ2』の詳細表として:
- 店舗数による中型/大型解禁
- 許可料金300万/700万/1000万
- 許可距離5/7/10マス

などが容易に見つかるが、これらは **続編の値** であり、初代PS/SS baselineには採用しない。

初代の中/大型解禁条件、許可料金、許可距離は引き続き未確定とする。

## 8. 今回の実装反映判断

先行固定可能:
- 店舗variantには少なくとも `orientation = vertical | horizontal` を持たせる。
- 店舗サイズは `small / medium / large` の3クラス候補を維持する。
- 店舗サイズ選択にはunlock/availability状態を持たせる。常時全サイズ解放で実装しない。
- 価格変更と「その日の客入りスナップショット」は分離する。
- 価格変更を日中の顧客需要再計算トリガにしない仕様候補を強くする。
- 初代で20,000,000円の最安土地が実在する。

未確定継続:
- 中型/大型の正確な解禁条件
- PS/SSで解禁条件が同じか
- 6店舗候補の全価格と全床寸法
- 大型改築費
- 初代3販売許可の料金と距離
- 日次需要スナップショットと天候再計算の正確な優先順位

攻略本到着後、このファイルのunlock/価格関連仮説をデータ表・操作説明と照合し、`StoreVariantDefinition` と需要更新ルールへ昇格させる。
