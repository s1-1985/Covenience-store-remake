# 日付境界・価格・販売許可・清掃ルール追加調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 日付変更時に何が固定/再計算されるかを、初代専用資料で切り分ける。
- 価格変更のタイミング依存を確認する。
- 販売許可の取得タイミングをPS/SSで分離する。
- 清掃100付近の挙動を、続編データと混同せず記録する。

## 証拠レベル

- CONFIRMED-OFFICIAL: 現行公式/メーカー資料
- CONFIRMED-VISUAL: 初代PS/SS実画面で直接確認
- CONFIRMED-COMMUNITY: 初代PS/SS専用の複数資料または再現性の高い専用Wiki
- PROVISIONAL: 初代向けだが単一資料、機種限定、転記誤差の可能性あり
- HYPOTHESIS: 実装値へ直結させない推測

---

## 1. 日付変更時の顧客独占率が、その日の客入りを決める

初代専用FAQで明記:

- 日付が変わったタイミングの顧客独占率で、その日の客入りが決まる。
- 内装/改築のため臨時休業したまま0時を迎えると、顧客独占率0%として計算され、その日はほぼ客が来なくなる。
- 臨時休業への変更は0時を過ぎてから行うのが安全。
- 23時を過ぎている場合は7時〜23時営業へ変更することでも回避できる。
- 日中に天候が変わった場合も顧客独占率が再計算され、客入りが変化する。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の要求

来店判定を完全リアルタイムで毎分ゼロから再計算するより、少なくとも次の概念を分けられる構造が必要。

```text
DailyDemandState
- base_share_at_day_boundary
- weather_adjusted_share
- planned_arrivals / daily_demand_budget
- current_price_snapshot?   // exact implementation unknown
```

`current_price_snapshot` が存在するかは、次節のSaturn限定裏技から強く示唆されるが、PS baselineではまだ確定しない。

---

## 2. Saturn版では「日付直前だけ安く→日付後に値上げ」で客入りを維持できる裏技が報告される

初代Saturn版の裏技まとめでは:

1. 日付変更直前に全商品の利益率を20%OFFへ設定
2. 日付変更/日次集計を通過
3. 直後に全商品の利益率を50%へ戻す

とすると、客入りは値下げ時の条件のまま維持され、高い利益率で販売できるとされる。

Source:
- https://menokenkou.work/konbiniura/

証拠レベル: PROVISIONAL / SATURN-SPECIFIC

### 非常に重要な機種差

同じ資料のPS1版欄にはこの裏技が掲載されておらず、PS1版で明示されているのは「極上」マップ出現のみ。

したがって:

- `日付境界で客入りが決まる` → 初代PS/SS共通として強い
- `価格率も日付境界でスナップショットされ、日中の値上げがその日の来店量へ効かない` → **Saturn版では強い証拠、PS版は未確認**

と分離する。

### baseline方針

PSを最終基準とする場合、このSaturn裏技をそのまま仕様化しない。

ただし原作内部設計の有力な手掛かりとして:

```text
onDayBoundary():
    attraction = calculateAttraction(store_conditions_at_boundary)
    daily_arrival_plan = buildArrivalPlan(attraction)
```

のような「日単位キャッシュ」構造を候補として残す。

---

## 3. 続編『2』にも同型の価格タイミング裏技が存在するが、初代証拠の代用にはしない

『ザ・コンビニ2』には、23:50頃に利益率0%→日付後すぐ100%へ戻すことで評価と資金を両立する攻略が複数残っている。

Sources:
- https://wazap.com/game/3087/cheats/
- https://wazap.com/question/%E3%81%93%E3%81%AE%E6%96%B9%E6%B3%95%E3%81%AF%E3%80%81%E6%94%BB%E7%95%A5%E6%9C%AC%E3%81%AB%E8%BC%89%E3%81%A3%E3%81%A6%E3%81%84%E3%81%9F%E3%82%82%E3%81%AE%E3%81%AA%E3%81%AE%E3%81%A7%E3%80%81%0D%0A%E7%9F%A5%E3%81%A3%E3%81%A6%E3%81%84%E3%82%8B%E4%BA%BA%E3%81%8C%E3%81%84%E3%82%8B%E3%81%8B%E3%82%82%E3%81%97%E3%82%8C%E3%81%BE%E3%81%9B%E3%82%93%E3%80%82%2B.../136635/

これはシリーズ設計が後続作でも「日付境界評価」を使っていることの補助証拠にはなるが、初代PSの直接証拠にはしない。

扱い: VERSION-COMPARISON ONLY

---

## 4. 販売許可は新規出店時に申請できる — PS実プレイで確認

初代PS版上級プレイ記録では、新規出店時に:

- タバコ
- 酒
- 薬品

の申請可否を立地ごとに確認し、資金事情に応じて申請してから店舗を建設している。

近隣ライバル店が薬品権利を持っているため、薬品のみ申請不可という例も確認される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

### 確定できること

- 販売許可の可否は立地決定時点で確認される。
- 近隣店舗の既存許可が排他要因になる。
- 少なくともPS版では新規出店時に許可を申請できる。

---

## 5. Saturn版では「改築」経由で販売許可申請できる裏技が報告される

初代Saturn版の裏技:

1. 販売許可が必要な土地に、許可を取らず店を建設
2. `改築` を選ぶ
3. 販売許可を申請
4. 配置画面まで進んで申請画面へ戻る
5. 申請料を払わず許可が取得できる場合がある

Source:
- https://menokenkou.work/konbiniura/

証拠レベル: PROVISIONAL / SATURN-SPECIFIC / BUG

### 重要な結論

この裏技から少なくともSaturn版では「改築フロー内に販売許可申請画面が存在する」可能性が非常に高い。

ただし:

- PS版でも改築時に販売許可申請できるか → 未確認
- 申請取消ができるか → 未確認
- Saturnのバージョンによって裏技自体が修正済みの可能性あり

baselineではPS実画面/説明書で確認するまで `permit_change_on_remodel` を確定しない。

---

## 6. 販売許可の「排他」自体は初代共通として強い

初代専用FAQ:

- 敵味方を問わず、すでにコンビニがある場所の近くでは酒・タバコ等の販売許可が下りづらい。
- 競合を撤退させる、買収後に売却するなどで状況を変えられる。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

PS上級プレイ記録でも、敵3号店の薬品許可が近いため自店では薬品申請不可となった実例がある。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

証拠レベル: CONFIRMED-COMMUNITY

### 未確定

- 排他半径
- タバコ/酒/薬で距離が違うか
- 許可申請費
- 自店の既存許可も新規自店を阻害するかの厳密条件

『2』『3』の完全数値表は流用禁止。

---

## 7. 清掃値と床汚れ — 初代専用Wikiの表記をそのまま保存

初代専用店員Wikiでは:

- 店員の清掃能力が店舗の「清掃」に影響
- `店舗の清掃の数値が100以下だと床に汚れが発生する`
- 床を掃除すると清掃能力が1上昇

と記載される。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY（記載内容）

### 注意: 「100以下」は挙動として不自然な可能性あり

同Wikiの記述を字面どおり読むと `100` でも床汚れが発生することになる。

一方、後続作『3』では `清掃100未満のとき床に汚れが発生` と明記されているが、これは初代の直接証拠ではない。

Source for comparison only:
- https://www.lemono.jp/kouryaku/conveni3/shop.html

### baseline方針

初代PS/SSについては:

```text
if cleanliness < 100:
    can_spawn_dirt = true
```

と仮実装する可能性は高いが、**初代PS実機で100時に汚れが本当に止まるか確認するまで確定値にしない**。

データ上は:

```text
cleanliness_dirt_threshold:
  value: 100
  comparator: UNKNOWN  # < or <=
```

として扱うのが安全。

---

## 8. 清掃能力と店舗規模の関係

初代専用Wikiでは、大型化すると清掃維持が難しくなること、能力の低い店員を揃えると大型店で汚れが深刻になる実プレイが確認される。

Sources:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

ただし初代の正確な「店舗規模別清掃基準値」は未復元。

『3』には規模別基準値があるが、これは初代へ流用しない。

---

## 9. 今回の重要な修正事項

### 以前の表現を修正

以前の研究メモで「清掃100なら床が汚れない」と断定気味に扱った箇所がある場合、現時点では次に修正する。

- **清掃100が安全閾値である可能性は高い**
- しかし初代専用Wikiの文章は `100以下で汚れ発生` と書かれており、比較演算子に矛盾が残る
- PS実機確認までは `100で完全停止` をCONFIRMEDにしない

### Saturn限定の裏技をPS baselineへ混ぜない

- 価格日付境界裏技 → Saturn欄で確認、PS欄には無し
- 許可料無料バグ → Saturn欄で確認、PS欄には無し

したがって、これらは「原作シリーズの内部構造を推測する証拠」には使えるが、PS互換仕様として直接実装しない。

---

## 10. 次に検証すべき点

1. PS版で日中の価格変更が当日の客入りへ即時影響するか
2. PS版で改築時に酒/タバコ/薬の許可申請が可能か
3. PS版で店舗清掃100時に床汚れが完全停止するか
4. 利益率UIの最小/最大/刻み
5. 許可申請費
6. 許可排他半径
7. 価格率が顧客独占率のどの段階で評価されるか
8. 天候変化時に価格条件まで再評価されるか、天候係数だけ再計算されるか

これらは説明書、現行Console ArchivesのPS版実機、1997年PS/SS攻略本で確認する。
