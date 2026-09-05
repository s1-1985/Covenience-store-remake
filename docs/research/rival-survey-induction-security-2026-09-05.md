# ライバル調査・誘致警備・販売許可フロー交差検証 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 初代PS/SS版以外の情報を混ぜず、ライバル調査、誘致施設の警備効果、販売許可と改築の関係を追加検証する。
- PS版とSS版で同じと断定できない挙動は分離して記録する。

## 証拠レベル

- CONFIRMED-COMMUNITY / SS-SPECIFIC / DIRECT-PLAY: SS版を実機で約30時間プレイした詳細記録。
- CONFIRMED-COMMUNITY / PS-SPECIFIC / DIRECT-PLAY: PS版上級・中級を実際に進行した詳細プレイ記録。
- STRONG-INFERENCE: 複数の初代専用実機記録が同じ方向を示すが、画面または説明書で未確定。

---

## 1. ライバル店調査の費用

SS版実機プレイ記録では、メニューの「調査」からライバル店を調べる際、50万円を要すると記録されている。

取得できる内容は、営業時間や収益などの基本情報で、相手店舗の内部レイアウトまでは確認できないとされる。

Evidence:
- SS版実機約30時間のプレイ記録。
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

判定:
- `rival_store_survey_cost = 500000` は SS baseline で CONFIRMED-COMMUNITY。
- PS版で完全に同額かは未直接確認のため、共通値として固定する前にPS画面で再確認する。

実装メモ:
```text
SurveyAction
- target: own_store | rival_store
- cost
- revealed_fields[]
```

ライバル調査で内装を直接読める設計にはしない。

---

## 2. 誘致施設「交番」「消防署」は店舗警備を上げる

SS版の詳細実機記録では、交番・消防署が近隣店舗の「警備」を大幅に上げる施設として明示されている。特に交番は1店舗に1つ置く運用が有効とされる。

初代専用Wikiでも、警備100を維持するため交番・消防署の誘致が強く推奨されており、警備99でも火災が起こり得ると反復観測されている。

Evidence:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

判定:
- 交番・消防署が近隣店舗の警備パラメータへ正の効果を与える: CONFIRMED-COMMUNITY。
- 正確な加算値、効果半径、重複加算式: 初代では未確定。

重要:
- 『ザ・コンビニ2』専用Wikiには具体的な +40/+30 等の表が存在するが、これは続編データなので初代へ流用しない。

---

## 3. 販売許可は改築フローと強く結び付いている

SS実機記録の攻略メモでは、「たばこ・酒・薬品」の許可は改装時のみ取得可能で、改装を伴わず許可だけを得ることはできないと記録されている。

一方、PS版実機上級プレイでは、新規店舗建設時にタバコ・酒を申請して建設し、近隣の敵店舗が薬品許可済みであるため薬品を申請できなかった事例がある。

Evidence:
- SS: https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- PS: https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

整理:
- 新規出店時に許可申請できる: PSで CONFIRMED-COMMUNITY。
- 既存店で後から許可を取る場合、改築フローを経由する: SSで CONFIRMED-COMMUNITY。
- PS既存店も全く同じUI制約か: 未確定。

既存のSS固有キャンセル技と合わせ、販売許可はプラットフォーム差異を持つ可能性があるため、許可ロジックをUIと完全に一体化させない。

---

## 4. 周辺競合店の許可状態が申請可否に影響する

PS版上級プレイでは、敵3号店がすでに薬品許可を持ち、その店舗が近いため、自店では薬品を申請できないと明記されている。

同じ記録ではタバコ・酒は申請可能であった。

判定:
- 許可種別ごとに立地判定が独立している: STRONG-INFERENCE。
- 周辺の他店が同種許可を保有していることが申請可否へ影響する: CONFIRMED-COMMUNITY / PS-SPECIFIC。
- 正確な距離、敵味方共通判定、土地中心距離か店舗外形距離か: 未確定。

実装では当面:
```text
PermitType
- tobacco
- alcohol
- medicine

PermitEligibilityQuery
- candidateStoreLocation
- nearbyStores
- permitType
- platformRules
```

のように、許可種別ごとに判定できる構造が安全。

---

## 5. 町の自動発展と誘致は併存する

SS実機プレイでは、プレイヤーが交番・消防署などを誘致しつつ、最終的に区役所まで町が発展したことが記録されている。

PS版上級記録でも、駅・遊園地・大学などがゲーム進行中に出現している。

判定:
- プレイヤー誘致施設と、自動発展/人口トリガー施設は別系統として併存する: STRONG-INFERENCE。
- 区役所の出現条件、誘致可能か自動出現か、人口条件: 未確定。

このため TownBuildingDefinition には最低でも以下を分ける。

```text
spawn_mode:
- player_induced
- automatic_growth
- population_triggered
- scenario_triggered
- unknown
```

---

## 6. 調査メニューの追加復元

SS実機記録から「調査」で少なくとも以下が確認される。

- 各店舗の売上成績
- 売れ筋アンケート
- 収支グラフ
- ライバル店調査（有料）

既存研究で確認済みの「全店収支グラフ」「顧客独占率」と合わせても、まだ全階層は未完成。

特に「売れ筋アンケート」は、商品の置き忘れ・品切れ対策に利用できる情報画面として存在する。

Evidence:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

---

## 7. 新たに確定/強化された事項

1. SS版ライバル店調査費用 50万円。
2. ライバル店調査では営業時間・収益等の基本情報を見られるが、内部レイアウトまでは見られない。
3. 交番・消防署は近隣店舗の警備を上げる。
4. 新規出店時にタバコ・酒・薬品の許可申請が可能。
5. 既存店で後から許可を取る場合、SSでは改築フロー経由。
6. 近隣競合店舗の同種許可保有が申請可否へ影響する事例がPS版で確認できる。
7. 「調査」配下に売れ筋アンケートが存在する。

---

## 8. 未確定事項

- PS版ライバル調査費用も50万円か。
- ライバル調査画面で見られる全項目。
- 交番・消防署の初代での正確な警備加算値。
- 誘致効果半径と重複処理。
- 各販売許可の申請料。
- 許可排他判定の正確な距離式。
- PS版既存店での追加許可取得UI。
- 区役所の出現条件と買い物人口。
- 売れ筋アンケートの全表示項目。

---

## 9. 汚染防止

検索中に『ザ・コンビニ2 ～全国チェーン展開だ！～』の誘致データ表が多数ヒットする。
そこには交番/消防署の具体的な費用、買い物人口、警備加算値等が掲載されているが、本調査では初代の証拠として採用しない。

初代baselineへ入れる値は、初代PS/SSの説明書、原作画面、初代専用攻略資料、PS/SS実機プレイ記録で裏付けられたものだけとする。
