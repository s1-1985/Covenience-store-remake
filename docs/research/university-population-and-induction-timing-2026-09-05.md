# 初代PS 大学人口アンカーと施設誘致タイミング 2026-09-05

対象: 1997 PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的: 町建物マスターの未確定項目のうち、大学の人口規模と「誘致した施設が即時完成するか」を初代PSプレイ記録だけで詰める。

## 1. 大学1件の人口増加は約700～800人というPS攻略投稿

PS版初代Wazapの攻略投稿「初級は働かずクリア」では、人口が伸びにくくなる初級終盤の対策として大学誘致を勧め、大学1件で「だいたい700人～800人」増えるという実プレイベースの目安が記載されている。

Source:
- https://wazap.com/cheat/%E5%88%9D%E7%B4%9A%E3%81%AF%E5%83%8D%E3%81%8B%E3%81%9A%E3%82%AF%E3%83%AA%E3%82%A2/105193/

Evidence: `PROVISIONAL-COMMUNITY-PS / DIRECT-PLAY-ESTIMATE`

これは攻略本の固定マスター値ではないため、`University.shoppingPopulation = 750` のように単一値へ確定してはいけない。現時点では次のレンジとして保持する。

```text
TownBuildingPopulationAnchor
university_observed_population_delta = 700..800
source = PS community direct-play strategy
confidence = provisional
```

## 2. 別のPS長期プレイ記録が大学700～800人級と整合

PS版を11年以上進めた詳細プレイ記録では:

- 町人口約18,000人まで到達
- 大学を2件誘致しても20,000人には届かなかった
- その後、さらに大学1件を誘致すると20,000人へ到達

という経過が記録されている。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

Evidence: `DIRECT-PLAY-PS`

この記録だけでは各大学の正確な人口増加量は逆算できないが、大学が「数百人規模」の大型人口施設であること、Wazapの約700～800人という観測レンジと矛盾しないことを確認できる。

また初代専用Wikiでは駅人口が2,240人で「大学以上」と説明されているため、大学が2,240人未満であることとも整合する。

Wiki source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 3. 施設誘致は即時完成ではない

同じPS長期プレイ記録では、火災対策として消防署を誘致した直後について、施設が「建つまでに少しかかる」ため、完成前に再度火災が発生したと記録されている。

Evidence: `DIRECT-PLAY-PS / BEHAVIOR`

したがってRemakeの施設誘致を:

```text
pay induction cost -> facility instantly active
```

と実装するのは避ける。

最低でも:

```text
INDUCED / PLANNED
-> UNDER_CONSTRUCTION or WAITING
-> ACTIVE
```

のような遅延状態を表現できる設計にする。

正確な建設期間（日/月単位）は未回収なので、ここでは固定しない。

## 4. 初級の都庁出現は人口到達直後ではなく次月発火のPS観測

同PSプレイ記録では、最後の大学誘致で町人口が20,000人に到達した後、**次の月**に「都庁がやってきました」に相当する通知が出て、その直後にエンディングへ入ったと記録されている。

Evidence: `DIRECT-PLAY-PS / SINGLE-RUN`

初代専用Wikiの「人口20,000超で都庁が自動的に来る」という記述と合わせると、初級クリア判定は人口条件を常時監視して即終了するのではなく、月境界イベントとして処理される可能性が高い。

現時点の実装候補:

```text
if town_population >= metropolitan_threshold:
    queue metropolitan_arrival

on next monthly boundary:
    metropolitan_arrival
    beginner_clear_sequence
```

ただし閾値の比較演算子（`>= 20000` か `> 20000`）は資料表現が揺れるため、攻略本/実機で最終確認する。

## 5. 店員給与スケールの追加アンカー

初代専用Wikiは、雇用画面の日給が24時間営業基準であり、短時間営業では異動画面の給料表示が下がると説明している。さらに体感的な換算として「時給250～300円くらいの店員がザラ」と記載されている。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

Evidence: `PROVISIONAL-COMMUNITY-FIRST-TITLE / SCALE-ANCHOR`

これは正確な給与計算式ではないが、攻略本値が回収できない場合の給与式検証レンジとして使える。例えば日給6,000～7,200円級が一般的候補になることを示すが、個別店員の給与をこの換算から逆算して確定しない。

## 6. TownBuildingDefinitionへの反映

```text
TownBuildingDefinition
id
name
shoppingPopulationExact?      # 攻略本値
observedPopulationMin?        # 今回: university 700
observedPopulationMax?        # 今回: university 800
inductionCost?
constructionDelay?            # unknown exact, but non-zero behavior supported
activationTiming
source
confidence
```

初級都庁は通常のプレイヤー誘致施設と同じ処理へ単純化せず、人口閾値による自動予約イベントを持てる構造にする。

## 7. 未確定

- 大学の固定買い物人口値か、誘致ごとに人口が変動するのか
- 大学の正確な誘致費
- 大学のfootprint
- 消防署等の正確な建設待ち期間
- 都庁発火条件が `20,000以上` / `20,000超` のどちらか
- 都庁出現からエンディングまでの正確なフレーム/イベント順

これらは攻略本の町施設データ表とPS実機動画を優先して詰める。
