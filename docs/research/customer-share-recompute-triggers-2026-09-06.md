# 顧客独占率の再計算トリガー調査（2026-09-06）

## 対象

1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』のみ。
後続作の仕様・数値は採用しない。

## 結論

顧客独占率／その日の客入りは、店舗パラメータ変更のたびに完全リアルタイム再計算されるモデルではない可能性が高い。
現時点の初代専用資料とSS実機記録を組み合わせると、少なくとも以下の境界が観測される。

1. **日付変更時（0:00）に顧客独占率が再計算され、その値がその日の客入りへ強く反映される。**
2. **天候が日中に変化した場合は、例外的にその時点で顧客独占率が再計算され、客入りも変化する。**
3. **商品価格を日中に変更しても、その変更は同日の客入りへ直ちには反映されないというSS実機記録がある。**

したがって実装では、`customerShare` / `dailyDemandSnapshot` を毎フレーム全入力から再計算するのではなく、明示的な再計算イベントを持つ設計が原作挙動に近い。

---

## Evidence 1: 0:00の日付境界で客入りが決まる

### 内容

初代PS/SS専用攻略Wiki FAQでは、内装・改築のため臨時休業したまま0時を迎えると、顧客独占率0%としてその日の客入りが決まり、その後再開してもその日1日は客が来なくなると説明されている。

また、長期休業店を再開する際は日付変更直前に営業状態へ戻すと、次の日からすぐ客が来るとされる。

### Evidence level

**B+ / FIRST-TITLE-DEDICATED-COMMUNITY / REPRODUCIBLE-BEHAVIOR**

一次資料ではないが、初代PS/SS専用Wikiで具体的な再現手順を伴う挙動として記録されている。

### Source

- 初代PS/SS専用攻略Wiki「FAQ」
  - https://wikiwiki.jp/theconveni1/FAQ
  - 「内装・改築後に客が急に来なくなった」節

---

## Evidence 2: 天候変化は日中再計算トリガーになる

### 内容

同FAQでは、1日の途中で天候が変化することがあり、その際にも顧客独占率が再計算されて客入りが変化すると記録されている。

別ページ「顧客独占率」でも、天候が顧客独占率の入力要素であり、雪の日には条件によって半分以下まで落ちる場合があるとされる。

つまり、日次スナップショットだけで完全固定されるわけではなく、少なくとも**天候変更イベントは日中の再計算を発火する**。

### Evidence level

**B+ / FIRST-TITLE-DEDICATED-COMMUNITY / CROSS-PAGE-CONSISTENT**

### Sources

- 初代PS/SS専用攻略Wiki「FAQ」
  - https://wikiwiki.jp/theconveni1/FAQ
- 初代PS/SS専用攻略Wiki「顧客独占率」
  - https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87

---

## Evidence 3: 日中の価格変更は客入りへ即反映されない

### 内容

SS版を約30時間プレイした実機記録には、価格変更を利用した次の挙動が記録されている。

- 日付変更直前に商品価格を安くする。
- 0時を跨いだ後に商品価格を高く戻す。
- その日については、安値時に決まった客入りを維持したまま高値販売できる。

記録者はこれを「価格設定のズル技」として利用している。

この観測が正しいなら、商品価格は顧客独占率の入力要素ではあるが、**価格変更操作そのものは日中の再計算トリガーではない**。

### Evidence level

**B / DIRECT-PLAY-SS / PLAYER-RECORDED-EXPLOIT**

攻略Wikiより一次性は高い実機長期記録だが、フレーム単位の比較検証ではないためBに留める。

### Source

- ゲーム＊やおよろず Retro「ザ・コンビニ ～あの町を独占せよ～」SS版ゲーム備忘録
  - https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
  - 雑記帳 → 裏技 → 「価格設定のズル技」

---

## 実装への示唆

暫定的には以下のようなイベント駆動構造が安全。

```text
CustomerDemandState
  currentShare
  dailyDemandSnapshot
  lastRecomputeReason

recompute triggers:
  DAY_BOUNDARY_00_00     -> confirmed/probable
  WEATHER_CHANGED        -> confirmed/probable
  PRICE_CHANGED          -> do NOT immediately recompute (SS evidence)
  STORE_OPEN_STATE_CHANGED -> unresolved except at day boundary
  INVENTORY_CHANGED      -> unresolved
  SERVICE_CHANGED        -> unresolved
  POPULARITY_CHANGED     -> unresolved
  CLEANLINESS_CHANGED    -> unresolved
  NEARBY_BUILDING_CHANGED -> unresolved
```

重要なのは、価格・人気・サービス・清掃などが「顧客独占率の入力である」ことと、「それらの値が変更された瞬間に客入りが再計算される」ことを分離する点である。

---

## 既存researchとの整合

既存の `customer-share-weather-hours-and-head-store-bias-2026-09-06.md` では、顧客独占率の入力要素として人気・清掃・サービス・周辺人口・品揃え・価格・営業時間・天候を整理済みである。

今回の追加は、**入力項目ではなく再評価タイミング**を定義するもの。

既存の「日付境界スナップショット」仮説を補強する一方で、天候変化時には日中でも再評価されるため、単純な「0時に1回だけ計算」実装では不足する。

---

## 未確定

以下はまだ確定していない。

- PS版でも価格変更 exploit が完全に同一か。
- 人気・清掃・サービス値の変化が日中即時再計算を起こすか。
- 営業時間変更を0時以外に行った際の即時再計算有無。
- 品切れ／新規商品設置が日中再計算を起こすか。
- 近隣店舗の開閉・撤退・買収時の再計算タイミング。
- 周辺建物の新設・誘致完了時に即再計算されるか、翌日反映か。
- 天候変更時に全店舗一括再計算されるのか、可視／稼働店舗だけか。
- `顧客独占率` 表示値と実際のスポーン需要が完全に同一スナップショットを参照するか。

---

## 現時点の実装可否

**イベント駆動の需要再計算基盤は実装開始可能。**

ただし最終式や全再計算トリガーを固定する段階ではない。

安全な実装は、再計算理由をenum等で明示し、未確認トリガーを後から追加・無効化できる構造にすること。
