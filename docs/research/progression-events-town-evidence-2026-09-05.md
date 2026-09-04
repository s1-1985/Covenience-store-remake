# 進行・イベント・町発展の追加証拠 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』

## 1. シナリオ/マップ構造

初級・中級・上級の3標準マップがあり、3つすべてをクリアすると「極上」マップが出現するという複数資料が一致。

初級:
- 初期資金 2億円
- 町人口2万人到達 → 都庁出現/誘致でクリア

中級:
- 初期資金 1.5億円
- 自社10店舗でクリア
- 町全体のコンビニ上限が10店舗のため、ライバル店が残っている場合は撤退/買収等で枠を空ける必要がある

上級:
- 初期資金 1.5億円
- オーナー評価★5でクリア
- オーナー評価は「調査」→「全店収支グラフ」にある総合評価

Sources:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://kakusi.jp/?p=91850

証拠レベル: CONFIRMED-COMMUNITY（複数独立資料）。

## 2. 上級のオーナー評価は年次判定の可能性が高い

上級プレイ記録では「オーナー評価が出るのは1年ごと」と明記され、1月到達時にクリア演出を見逃した例がある。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

初代専用Wikiでは、星4状態で各店舗パラメータを100にし、月初を迎えると星5へ上がると説明される。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

「評価表示は年1回」「内部更新は月初にも影響」の関係は説明書/実機で要追加検証。

## 3. 町人口5000人で駅が発生する事例

初代専用Wikiでは、町人口が5000人を超えるとライバル支店近くの線路上に駅が発生した事例があり、その駅の買い物人口は2240人と記録されている。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

別のPS版プレイ記録でも町の発展に伴い複数の駅が自然発生し、駅近くの店舗が大きく伸びることが確認される。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

baseline要件:
- 線路/駅候補地をworldデータとして持つ
- 町人口・地価・周辺開発等をトリガーに駅が自然発生する仕組みを持つ
- 駅は大規模な買い物人口ソース

駅の発生条件の完全式・複数駅条件はまだ未確定。

## 4. 都庁は人口2万人がトリガー

初級のクリア条件として、町人口2万人で都庁がやって来る/建つことが複数資料で一致。

Sources:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://codevis.nobody.jp/review-ps/the_convini.html

証拠レベル: CONFIRMED-COMMUNITY。

## 5. 大学は強力な人口増加施設

上級プレイ記録では、大学1件の誘致で人口が約500〜800人増えると記録される。大学建設には1〜2ヶ月程度待つ場面もある。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

この数値は後続作の詳細データと似るが、ここでは初代PS版プレイ記録から直接得た範囲のみ採用する。

## 6. 交番・消防署は警備維持の主要手段

初代専用FAQでは警備100未満だと火災がかなりの確率で起き、店の大型化や客に怒られることで警備が下がるため、交番/消防署を過剰なくらい誘致することを推奨している。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

SS版レビューでも交番・消防署が近隣店舗の警備を大きく上げる重要施設と説明される。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

PS版プレイ記録では各店舗の近くに交番・消防署を誘致する運用が常態化し、消防署完成前に再び火災が起きた例もある。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

初代固有の誘致費・効果半径・警備加算値はまだ完全確定していない。ザ・コンビニ2の詳細値は流用禁止。

## 7. 火災・強盗

初代PS/SSの実プレイ記録で火災・強盗が繰り返し確認される。

火災:
- 店そのものが消滅するのではなく、内装が焼失して実質開店休業状態になる記録がある
- 放置中に火災へ気づかず数ヶ月赤字化した例あり

強盗:
- 警備不足時に発生

Sources:
- https://ameblo.jp/freeagent/entry-10008302250.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

## 8. コンビニコンテスト

複数の初代PSプレイ記録で「コンビニコンテスト」イベントを確認。プレイヤーまたはライバル店が選ばれることがあり、受賞時に大きな賞金/資金増が発生する。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

正確な発生条件・評価基準・賞金額は未確定。

## 9. スーパー店員（80歳イベント）

初代上級プレイ記録では攻略本情報として、79歳の店員が80歳になる年に一定確率で「全能力100」のスーパー店員へ変化することがあると記録されている。最年長候補でも開始時58歳程度で、到達まで22年以上かかる旨も記録。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

Wazapにも「80歳を越えると一定確率でオール100」と同様の初代PS情報がある。

Source:
- https://wazap.com/game/12333/cheats/

証拠レベル: CONFIRMED-COMMUNITYだが、正確な発生タイミング/確率は未確定。

## 10. ライバルAIは撤退後に再出店する

中級プレイ記録では、価格競争でライバル支店を閉店させても、ライバルが別の場所へ新店舗を出すことが繰り返し確認される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

上級ではライバル支店買収→最終的に本店閉店、ライバルチェーン消滅まで確認される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

baseline rival modelの最低要件:
- 店舗単位損益
- 閉店判定
- チェーンとしての新規出店
- 買収価格
- 本店/支店区分
- 販売許可保有
- 他店との顧客競合

## 11. 土地・地価インフレ

PS版レビューでは町の繁華化・年数経過で地価が上昇し、後年ほど新規出店/誘致が高価になると記録される。

Source:
- https://codevis.nobody.jp/review-ps/the_convini.html

初代専用Wikiでも、序盤2000万円程度の土地が後年1億円超まで高騰する例がある。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

実装上はworld tile/parcelへlandValueを持たせ、町発展と時間経過の両方で変化する仕組みが必要。

## 12. 店舗上限10

中級攻略と複数プレイ記録から、1マップに存在できるコンビニはプレイヤー+ライバル合計10店舗までというルールが強く支持される。

Sources:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

これは中級シナリオの「自社10店舗」を成立させる主要ルール。

## 13. 未確定項目
- 極上マップの正確な初期資金/クリア条件
- オーナー評価の完全計算式
- 駅発生の全条件/駅間距離/最大数
- 都庁の正確な出現位置/予約地ルール
- 大学・学校・遊園地等の初代固有誘致費/買い物人口/サイズ
- 交番/消防署の初代固有效果半径と警備加算
- コンビニコンテストの発生条件/賞金
- スーパー店員の正確な確率
- ライバルAIの資金モデル/新規出店ロジック
