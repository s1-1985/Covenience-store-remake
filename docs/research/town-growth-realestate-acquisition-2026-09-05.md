# 町発展・不動産・買収価格の追加証拠 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 町人口が店舗売上とは別に成長しうることを初代専用資料で整理する。
- 臨時休業店舗でも町発展の拠点として意味を持つ攻略を記録する。
- 地価上昇の立地要因と、ライバル店買収価格に収益性が影響する証拠を残す。

---

## 1. 初級では「営業しない自店」を置くだけでも町人口を伸ばせる攻略が成立

初代PS版Wazapの初級攻略では:

- 初級の目的は都庁誘致 = 町人口2万人
- 店舗周辺は地価の上昇幅が大きく、人が住み着きやすい
- 自店を出して `臨時休業` にし、営業せず放置しても人口が増える
- 敵店舗も排除せず町発展に利用できる
- 1万5千人付近で自然増が鈍ったら、店舗を売って大学を誘致
- 大学1つで700〜800人程度増えるとの観測

Source:
- https://wazap.com/cheat/%E5%88%9D%E7%B4%9A%E3%81%AF%E5%83%8D%E3%81%8B%E3%81%9A%E3%82%AF%E3%83%AA%E3%82%A2/105193/

初代専用Wikiでも:
- 最安値2,000万円級の土地へ7店舗ほど出す
- 全店臨時休業
- ライバルが活動する間に町人口が増える
- 支店売却資金で誘致を繰り返せば、ほぼコンビニ経営せず初級クリア可能

と同型の攻略が記録される。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル: CONFIRMED-COMMUNITY（複数初代専用資料で方向一致）

### 実装上の重要な意味

町人口成長を:

```text
population_growth = function(player_sales)
```

だけで表現してはいけない。

店舗の**存在/立地そのもの**が周辺発展を促す要因である可能性が高い。

候補モデル:

```text
TownDevelopmentInfluence
- store_presence
- location_quality
- rival_store_presence
- invited_facilities
- elapsed_time
```

正確な式は未確定。

---

## 2. 初級では町発展とコンビニ収益が切り離されている

Wazap投稿は明示的に `店の売り上げと人口は関係ない` という攻略上の観察を置き、休業店だけで人口を育てる方法を説明している。

初代専用Wikiも `初級だけ「町の発展」というコンビニ経営の評価とは関係がないクリア条件` と整理している。

Sources:
- https://wazap.com/cheat/%E5%88%9D%E7%B4%9A%E3%81%AF%E5%83%8D%E3%81%8B%E3%81%9A%E3%82%AF%E3%83%AA%E3%82%A2/105193/
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

### 注意

これは `売上が町人口へ絶対に一切影響しない` という内部式の完全証明ではない。

確実なのは:
- 高売上を作らなくても人口2万人へ到達可能
- 休業店舗/ライバル店舗の存在と施設誘致で町を発展させられる

というゲーム挙動。

---

## 3. 地価投機の具体的な立地条件

PS版Wazapの `バブル景気かい？` では、年数とともに地価が上がることを利用し:

- 序盤に複数の最小店舗を建てる
- 中央に近い土地
- 道路/線路沿い（特に道路・交差点）
- 役場用地の前
- 酒などの販売許可は不要
- 建てた後は臨時休業
- 維持費をほぼ掛けず、後年高値で売却

という戦略を記録する。

Source:
- https://wazap.com/cheat/%E3%83%90%E3%83%96%E3%83%AB%E6%99%AF%E6%B0%97%E3%81%8B%E3%81%84%EF%BC%9F/105188/

同投稿の観測:
- 約3年で2,000万円だった物件が1億円になる例

初代Wikiにも:
- 開始時2,000万円の土地が2年程度で1億円超

という近い観測がある。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル:
- 強い地価インフレ: CONFIRMED-COMMUNITY
- 交差点/役場前等の個別上昇係数: PROVISIONAL / STRATEGY-OBSERVATION
- 2〜3年で20m→100m: PROVISIONAL RANGE / MULTIPLE OBSERVATIONS

### 実装要求

土地価格更新は少なくとも将来:

```text
current_land_value = f(
  base_value,
  elapsed_years,
  surrounding_development,
  nearby_stores,
  infrastructure,
  town_progress
)
```

のように拡張可能にする。

ここで具体式はまだ作らない。

---

## 4. 臨時休業中は維持費がほぼ掛からないため、不動産保有戦略が成立

Wazapの不動産攻略では臨時休業後に `維持費が全然かからない` とされる。

初代専用FAQでも:
- 営業時間外/臨時休業では人件費を含む多くの維持費が発生しない
- 商品補充等があれば仕入代金は減る場合がある

とされる。

Sources:
- https://wazap.com/cheat/%E3%83%90%E3%83%96%E3%83%AB%E6%99%AF%E6%B0%97%E3%81%8B%E3%81%84%EF%BC%9F/105188/
- https://wikiwiki.jp/theconveni1/FAQ

### 意味

「休業して土地を寝かせる」が原作で経済的に成立する。

baselineでは休業店にも:
- 土地/店舗資産価値
- 町発展への存在効果候補

を残す必要がある。

---

## 5. ライバル店の買収価格は、その店の黒字/収益性で上昇するというPS攻略記録

初代PS版Wazap `出店より買収` では:

- 新規支店よりライバル店買収の方が安い場合がある
- 買おうとしている店が黒字になるほど買収金額が上がる
- 伸びそうな店に目星を付け、値上がり前に買うのがよい

と明記される。

Source:
- https://wazap.com/cheat/%E5%87%BA%E5%BA%97%E3%82%88%E3%82%8A%E8%B2%B7%E5%8F%8E/51719/

証拠レベル: PROVISIONAL / PS-COMMUNITY-SINGLE-POST

### 既存長期観測との整合

既存PSプレイ記録では:
- 開始直後はライバル支店約4,500万円の例
- 数年後は2億円〜2億1,200万円の例
- 10年超で2億円超、3億円貯めて買収した例

がある。

このため買収価格モデルには、単なる土地価格だけでなく**対象店舗の収益性**を入力可能にするべき。

候補:

```text
AcquisitionValuation
- land_value
- building/store_size_value
- target_profitability
- target_sales
- customer_share
- age/development factors
```

`target_profitability` は今回証拠が強化されたが、他の各係数はまだ式未確定。

---

## 6. 大学誘致による人口増加観測を強化

PS上級詳細プレイ記録では大学1つで約500〜800人増える観測。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

PS Wazap初級攻略では大学でだいたい700〜800人増えると記録。

Source:
- https://wazap.com/cheat/%E5%88%9D%E7%B4%9A%E3%81%AF%E5%83%8D%E3%81%8B%E3%81%9A%E3%82%AF%E3%83%AA%E3%82%A2/105193/

証拠レベル: CONFIRMED-COMMUNITY / RANGE-OBSERVATION

### 注意

これは `大学の買い物人口 = 700〜800` と同義ではない。

**町人口増加量の観測**として扱う。

---

## 7. 初級では10店舗上限が町発展にも影響

初代Wikiの休業店舗攻略では:

- 自店とライバル合わせて10店舗まで
- 自店の休業支店で枠を埋めすぎるとライバルが新規出店できない
- 町人口をライバルにも増やしてもらうなら、自店を順次売却して枠を空ける必要がある

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

### 意味

10店舗上限は単なる中級クリアの障害ではなく:

- ライバルAIの出店可能性
- 町発展速度
- 自社の土地投機

にもつながるワールド制約。

---

## 8. baselineへの今回の更新

```text
TownDevelopment
- can_progress_without_player_store_sales: true (observed)
- inactive/closed stores can still participate in development context
- rival stores can contribute to town growth
- invited facilities strongly affect population

RealEstate
- land values inflate strongly over years
- high-development locations appreciate more (qualitative)
- closed store holding strategy is viable

Acquisition
- target profitability affects acquisition price (PS community evidence)
```

未確定:
- 人口増加の正確な式
- 各店舗の発展半径
- 地価更新式
- 大学誘致費用/正確な人口効果
- 買収価格の数式
