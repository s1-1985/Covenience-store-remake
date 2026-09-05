# 初代PS/SS 月次集計・現行復刻・続編混入追加監査 2026-09-05

対象: 1997 PS/SS『ザ・コンビニ ～あの町を独占せよ～』のみ。

目的: 攻略本到着待ちの間に、月末集計の構造、2026年コンソールアーカイブス版のベース機種、駅条件の検索汚染を追加監査する。

## 1. 月の4実働日は「平日3日 + 休日1日」である可能性が強い

2006年の初代SS版プレイ回顧で、本作は1ヶ月を通常の30日としてリアルタイム進行させるのではなく、**平日3日 + 休日1日** の4代表日で進行し、その4日間の売上平均から1ヶ月の売上を求めると明記されている。

Source:
- https://ameblo.jp/freeagent/entry-10008302250.html

同記事は冒頭で1997年3月発売のセガサターン版を自身が購入・プレイした記憶として記述しており、後半でも「SS版では店舗が増えるにつれ非常に遅くなった」と明示するため、少なくともSS初代のプレイ記録として扱える。

既存の初代専用Wikiは:
- ゲーム内時間が進むのは毎月1～4日
- 5日～月末は一気にスキップ

と記録しており、4代表日制と整合する。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

Evidence:
- day1..4 only then skip: `CONFIRMED-COMMUNITY-FIRST-TITLE`
- 4 days = 3 weekdays + 1 holiday: `CONFIRMED-PLAY-SS / SINGLE-SOURCE`
- monthly result derived from 4-day average: `CONFIRMED-PLAY-SS / CONCEPTUAL`

### 実装上の重要性

現時点では月次集計を単純に「1～4日の実売上を合計して終わり」と実装してはいけない。

概念モデルは少なくとも以下を許容する必要がある。

```text
RepresentativeMonth
- weekdaySampleCount = 3
- holidaySampleCount = 1
- simulatedDays = 4
- monthlyAggregation = derived_from(representativeDayResults)
```

### まだ固定してはいけないこと

**正確な月次倍率は未確定。**

『ザ・コンビニ2』Wikiには「4日間の売上と維持費を8倍」と明記されるが、これは続編データである。

Source (CONTAMINATION ONLY):
- https://w.atwiki.jp/konbini2/pages/7.html

初代SSの上記回顧は「4日間の売上の平均から1ヶ月の売上を求める」としか述べておらず、`x8`、`x30`、曜日ウェイト等は示していない。

したがって初代Remakeでは攻略本・実機の月末前後連続記録が取れるまで:

```text
monthly_sales_formula = UNKNOWN
```

を維持する。

## 2. 天候1日が月収へ大きく効く理由を説明できる

同SSプレイ記録は、4代表日のうち1日でも悪天候で客足が途絶えると、その月全体の売上に強く影響すると述べる。

これは既知の「雪などで顧客独占率が大きく下がる」「天候変化時に顧客独占率を再計算」と組み合わせると、原作の月次売上変動が大きい理由を説明できる。

実装テスト候補:

```text
Given identical store configuration
When exactly one representative day changes from clear -> severe weather
Then month-end sales must materially change
```

正確な低下率は固定しない。

## 3. 2026年コンソールアーカイブス版はPS版ベースと強く特定できる

ハムスター公式ページはゲーム本編について「日本版ROMのみ収録」「1997年に32ビット家庭用ゲーム機向けに発売」とだけ記し、PS/SSのどちらのROMかを明記していない。

Official sources:
- https://www.consolearchives.com/title/csa-0023/
- https://store.playstation.com/ja-jp/concept/10017477

一方、2026年7月の実プレイ資料では:
- コンアカ版を「PlayStation版をベースに移植」と記述
- ゲーム内の**メモリーカード画面**からセーブ可能
- ゲーム内表示どおり**90秒待機**
- その前にメモリーカードアクセスでも時間が掛かる
- コンアカ側即時セーブは別系統

と直接プレイ内容が記録されている。

Source:
- https://yamatabode.com/blog-entry-3019.html

同ページには実際のコンアカ版ゲーム内セーブ動画の時刻も掲載されている（1:31:12開始、1:33:16終了）。

さらに2026年7月23日のプレイヤー報告にも:
- 「PS版ベースか」
- メモリーカードへのセーブが本当に90秒掛かった

との独立報告がある。

Source:
- Yahoo!リアルタイム検索上の当日プレイヤー投稿

旧PS版固有レビューでも:
- メモリーカード14ブロック
- セーブ約90秒
- ロード約70秒

が記録されており、現行版の挙動と一致する。

### 判定

```text
ConsoleArchives2026.basePlatform = PlayStation
confidence = STRONG_CURRENT_PLAY_EVIDENCE
```

ただしハムスター自身が「PS版」と公式明記した資料は未回収なので、ラベルは `CONFIRMED-OFFICIAL-PLATFORM` ではなく `STRONG-CURRENT-PLAY / PS-SIGNATURE` とする。

### プロジェクトへの意味

今後、コンソールアーカイブス版の実機動画・スクリーンショットで観測した挙動は、単なる「PS/SSどちらか不明の復刻」ではなく、**PS baselineの現行検証ルートとして優先度を上げてよい**。

特に以下の検証に向く:
- PS側のUI遷移
- 月末前後の数値推移
- 店舗6種の選択/解禁
- 許可申請画面
- 顧客独占率更新タイミング
- AIタスク優先順位
- PS固有バグの有無

## 4. コンアカ版でも原作の処理落ちが残るという現行観測

2026年8月の現行プレイヤー投稿では、客が増えるとコンアカ版でも処理落ちすることが報告されている。

これはRemakeで処理落ち自体を再現すべきという意味ではない。

むしろ:
- 現行版が原作実行挙動をかなり忠実に保持している
- 客数やAI個体数が多い状況の動画から、原作の同時個体挙動を観察できる

という検証価値を補強する。

Evidence: `CURRENT-PLAYER-OBSERVATION / NON-RULE`

## 5. 「駅間40マス」は初代へ採用しない

2026年のコンアカ初代について、SNS上で「2個目の駅は40マスほど離れないとできない」という回想が見つかる。

しかし、**『ザ・コンビニ2』専用Wikiには駅間40マス以上というルールが明確な数値仕様として存在する**。

Source (Conveni2 only):
- https://w.atwiki.jp/konbini2/pages/7.html

同じ続編FAQには:
- 1駅目人口5,000
- 2駅目人口8,000
- 駅間40マス以上

がセットで記載される。

初代専用Wikiで確実なのは現状:
- 線路上に左右それぞれ駅候補がある
- 人口5,000超付近で駅が出現した初代攻略観測
- 駅の買い物人口2,240

までであり、40マス制約の初代直接証拠はない。

### 判定

```text
first_title.station_min_distance_tiles = UNKNOWN
40_tiles = REJECTED_AS_PROBABLE_SEQUEL_CONTAMINATION
```

これは現在のWeb調査で非常に重要な汚染防止例になる。

## 6. 2026年9月以降は検索汚染がさらに増える

2026年9月3日にコンソールアーカイブス版『ザ・コンビニ2 ～全国チェーン展開だ！～』も配信開始された。

Official source:
- https://www.consolearchives.com/title/csa-0029/

そのため現在の検索では「コンアカ」「ザ・コンビニ」「1997」だけでは初代と2が同時にヒットしやすい。

今後の検索ルール:

```text
required query qualifiers:
- exact title: "ザ・コンビニ ～あの町を独占せよ～"
- or model/platform marker: SLPS-00782 / T-4310G
- explicit exclusion when useful: -"ザ・コンビニ2"
```

続編の完全表が初代より検索上位に出やすいため、数値採用時はページタイトルと対象作品を必ず確認する。

## 7. 今回の実装-ready更新

今回新たに仕様モデルへ反映してよいもの:

```text
MonthlySimulationModel
- simulated_days = 4
- representative_day_types = 3 weekday + 1 holiday   # SS-supported, PS cross-check pending
- aggregation_uses_representative_day_results = true
- exact_formula = unknown

EvidencePriority
- ConsoleArchives2026 -> strong PS-baseline verification route

TownStationDefinition
- min_distance_tiles = unknown
- do_not_import 40 from Conveni2
```

## 8. 次の検証

攻略本到着前にWeb/現行コンアカ動画で優先して探す:
1. 3日目→4日目→5日/月末の連続画面。4日目が休日表示か。
2. 4日各日の売上と月末売上が同一動画に映るケース。倍率/式を逆算する。
3. PSコンアカの店舗サイズ切替画面を連続観察し、6候補の価格/解禁を回収。
4. 許可申請画面の費用数値。
5. 誘致施設選択画面の価格/人口情報。
6. 商品/什器選択画面で表示される価格・容量・維持費。

攻略本本文が届いたら、上記観測値とデータ表を相互検算する。
