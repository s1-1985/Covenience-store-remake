# 初代PS 大学人口アンカーと施設誘致タイミング 2026-09-05（再検証）

対象: 1997 PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的: 町建物マスターの未確定項目のうち、大学の人口規模、誘致後の建設待ち時間、町施設の出現経路を初代PS資料だけで再整理する。

## 1. 大学の人口増加レンジを 500～800人へ修正

PS版初代Wazapの攻略投稿「初級は働かずクリア」では、大学1件で人口が概ね700～800人増えるという実プレイベースの目安が示されている。

Source:
- https://wazap.com/cheat/%E5%88%9D%E7%B4%9A%E3%81%AF%E5%83%8D%E3%81%8B%E3%81%9A%E3%82%AF%E3%83%AA%E3%82%A2/105193/

Evidence: `PROVISIONAL-COMMUNITY-PS / DIRECT-PLAY-ESTIMATE`

一方、PS版上級の長期プレイ記録では、大学誘致による人口増加について約500～800人という、より広いレンジが明記されている。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

Evidence: `DIRECT-PLAY-PS / OBSERVED-APPROXIMATE`

両者は「大学は数百人規模の大型人口施設」という点では一致するが、500～699人の可能性を排除できない。したがって、従来の `700..800` を確定レンジとして扱うのは狭すぎる。

現時点の安全な観測レンジ:

```text
TownBuildingPopulationAnchor
building = university
observed_population_delta_min = 500
observed_population_delta_max = 800
exact_value = UNKNOWN
source = PS direct-play estimates
confidence = provisional-to-strong behavioral anchor
```

重要: `University.shoppingPopulation = 750` のような固定値にはしない。攻略本の町施設データ表または原作画面で固定値を確認するまで、500～800人は観測包絡線として扱う。

初代専用Wikiでは駅の人口表示が2,240で「大学以上」と説明されており、大学が駅より小さい人口規模であるという関係とも矛盾しない。

Wiki source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

## 2. 大学は誘致後、建つまで約1～2か月待つPS観測

同じPS上級長期プレイ記録では、大学を誘致した後に完成まで「ひと月ふた月」待つ進行が記録されている。

Evidence: `DIRECT-PLAY-PS / OBSERVED-APPROXIMATE`

したがって大学については、単なる「非ゼロの建設待ち時間」より一段具体的に、次の観測レンジを保持できる。

```text
university_construction_delay_observed_months = 1..2
exact_rule = UNKNOWN
```

ただし、これは攻略者による長期プレイ記録上の概算表現であり、常に固定1か月または2か月なのか、月途中の誘致タイミングで見かけ上変わるのか、乱数や施設種別差があるのかは未確定である。

この1～2か月レンジを消防署・警察・遊園地など全施設へ無条件に一般化しない。

## 3. 施設誘致は即時ACTIVEではない

別のPS長期プレイ記録でも、火災対策として消防署を誘致した直後、完成前に再度火災が起きている。よって町施設には少なくとも建設待ち状態が必要である。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

Evidence: `DIRECT-PLAY-PS / BEHAVIOR`

最低限の状態遷移候補:

```text
INDUCED / PLANNED
-> UNDER_CONSTRUCTION / WAITING
-> ACTIVE
```

## 4. 町施設には「プレイヤー誘致」と「自動発展」の両方がある

PS中級・上級の長期プレイ記録では、プレイヤーが自店経営やライバル対策を続ける間に、駅・大学・遊園地・中学校・高校などが新たに出現し、既存店舗の客入りが変化する事例がある。上級記録では大学誘致後の進行中に近隣へ動物園ができる例もある。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

Evidence: `DIRECT-PLAY-PS / TOWN-GROWTH-BEHAVIOR`

したがって、町施設をすべて `player induced` として生成する設計は不適切である。少なくとも出現起源を分離できるようにする。

```text
TownFacilityOrigin
- PLAYER_INDUCED
- AUTONOMOUS_GROWTH
- SCENARIO_TRIGGERED
```

駅や都庁のように人口閾値と結びつく施設は `SCENARIO_TRIGGERED` または専用の自動出現ルールとして扱い、通常のプレイヤー誘致と同一処理にしない。

## 5. 初級の都庁出現は人口到達後の月境界発火が有力

PS長期プレイ記録では、大学誘致等で町人口が20,000人へ到達した後、次の月に都庁到来通知が出てエンディングへ移行する流れが観測されている。

Evidence: `DIRECT-PLAY-PS / SINGLE-RUN`

初代専用Wikiの「人口20,000超で都庁が自動的に来る」という記述と合わせると、常時監視で即終了するより、人口条件成立後に月境界イベントを予約する設計が有力である。

実装候補:

```text
if town_population reaches metropolitan_threshold:
    queue metropolitan_arrival

on monthly boundary:
    metropolitan_arrival
    beginner_clear_sequence
```

ただし閾値が `>= 20,000` か `> 20,000` かは未確定である。

## 6. TownBuildingDefinitionへの反映

```text
TownBuildingDefinition
id
name
shoppingPopulationExact?          # 攻略本/原画面で確認できた場合のみ
observedPopulationMin?            # university: 500
observedPopulationMax?            # university: 800
inductionCost?
constructionDelayExactMonths?
constructionDelayObservedMin?     # university: 1
constructionDelayObservedMax?     # university: 2
allowedOrigins[]                  # PLAYER_INDUCED / AUTONOMOUS_GROWTH / SCENARIO_TRIGGERED
activationTiming
source
confidence
```

観測レンジと原作固定マスター値を同じフィールドへ混ぜないこと。

## 7. 店員給与スケールの既存アンカー

初代専用Wikiは、雇用画面の日給が24時間営業基準であり、短時間営業では異動画面の給料表示が下がると説明している。また、体感的な換算として時給250～300円程度の店員が多いという記述がある。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

Evidence: `PROVISIONAL-COMMUNITY-FIRST-TITLE / SCALE-ANCHOR`

これは正確な給与式ではないため、個別店員の日給をこの換算から逆算しない。

## 8. 未確定

- 大学の正確な固定人口/買い物人口値
- 「人口増加」と建物画面の「買い物人口」が同一値か別値か
- 大学の正確な誘致費
- 大学のfootprint
- 大学の建設期間が固定値か、誘致日/月境界等で変動するか
- 消防署・警察・遊園地等の施設別建設期間
- 各施設が自動発展・誘致の両方に対応するか
- 自動発展施設の出現条件・候補地決定式
- 都庁発火条件が `20,000以上` / `20,000超` のどちらか

これらはPS/SS対応攻略本の町施設データ表、説明書、PS原作画面・実機動画を優先して詰める。
