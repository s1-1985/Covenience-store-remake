# 上級オーナー評価・エンディング・隠しマップ追加調査 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 上級の★5判定タイミングを確定度高く整理する。
- クリア時の演出/エンディング遷移を記録する。
- 隠しマップ名の「極上 / 特上」表記衝突を監査する。
- 長期プレイでの買収価格・人口誘致・店舗規模変化を補助証拠として残す。

---

## 1. 上級のオーナー評価は「1年ごと」

PS版上級の詳細実プレイ記録では、放置中に上級をクリアしてしまった後、筆者が明確に:

- `オーナー評価が出るのは1年ごと`
- `1月が来るときに常にチェックしていればクリアの瞬間を見逃さなかった`
- 実際のクリアは `19年目1月`

と記録している。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DETAILED-PLAYLOG

### 実装上の重要な修正

上級のクリア判定を毎月行う前提にしてはいけない。

少なくともPS baselineでは:

```text
onYearEvaluationBoundary():
    ownerRating = calculateOwnerRating()
    if ownerRating >= 5:
        triggerScenarioClear()
```

のような**年次評価**を持つ必要がある。

### まだ未確定

- 判定が厳密に「1月1日 0:00」なのか
- 1月の月次集計時なのか
- 年数更新時の別イベントなのか
- 評価画面が自動表示されるのか、内部更新だけか

したがって `January/year boundary` までは強く、正確なtickは実機/説明書確認待ち。

---

## 2. 上級クリアは10店舗保有を要求しない

同じPS上級プレイ記録で筆者は:

- ライバル4号店を買収して一時的に「我が10号店」としている
- その後も店の売却/再配置があり、「最後の10店舗目を建設する」と考えて資金を貯めていた
- しかしその途中、放置中に上級がクリアしていた
- 筆者自身が `店が10店舗になるまでは終わらないだろうと思い込んでいた` と振り返る

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

### 結論

上級は中級と違い、**自社店舗10店は必須条件ではない**。

上級baselineの勝利条件は、既存研究どおり:

```text
owner_rating >= 5
```

のみを中心に扱う。

ただし★5計算式の入力要因はまだ完全復元できていない。

---

## 3. 上級★5には人口が重要という実プレイ観測

PS上級記録では筆者が:

- ★5を取るにはまず人口を増やす必要があると判断
- 大学を誘致
- 大学1つで人口が約500〜800人増えると観測
- 町人口が2万人を超えると都庁が出現

と記録している。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル:
- 人口/町発展が★5戦略上重要: CONFIRMED-COMMUNITY
- 大学で500〜800人: PROVISIONAL / SINGLE-PLAY OBSERVATION
- 2万人で都庁: CONFIRMED-COMMUNITY（他初代資料とも一致）

### 注意

`ownerRating = function(population)` と単純化しない。

既存初代研究では店舗評価・全店収支・人気/清掃/サービス等も関係するため、人口は全体条件の一部とみなす。

---

## 4. クリア時のエンディング遷移

PS版実プレイ記録では、各級の目標達成時に:

1. 効果音
2. `〇〇が〇〇しました！` 型の達成メッセージ
3. コンビニを斜めから見下ろした静止画へ切り替え
4. スタッフロール
5. スタッフロール終了後も静止画が残る

という流れが記録されている。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DIRECT-OBSERVATION

### 初級との整合

別のPS初級プレイ記録でも、人口2万人到達後に都庁関連の達成メッセージが出て即エンディングへ入ることが記録される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

### baseline実装への意味

最初の互換プロトタイプでは、豪華な3D演出等を追加せず:

```text
scenario objective reached
 -> result message
 -> ending still / original replacement illustration
 -> credits
```

程度の簡潔な遷移で十分原作構造に近い。

原作の静止画自体はコピーせず新規制作する。

---

## 5. 隠しマップ名「極上」と「特上」が衝突

### `極上` とするPS向け複数資料

以下のPS向け資料では、初級・中級・上級をすべてクリアすると出る隠しマップを `極上` とする。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://kakusi.jp/?p=91850
- https://menokenkou.work/konbiniura/

### `特上` とするPS上級後編

同じpinkblueサイトの上級後編では:

- 攻略本引用として `上級編や特上編`
- 上級クリア後セーブすると `特上マップ` に挑戦可能

と記載される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

### 現時点の評価

複数独立/準独立資料が `極上` を支持しているため、**正式表示は「極上」である可能性が高い**。

`特上` は:

- 筆者の記憶/表記揺れ
- 攻略本側の呼称
- 版差

のいずれかを残す。

証拠レベル:
- 隠しマップ存在条件: CONFIRMED-COMMUNITY
- 正式名称 `極上`: STRONG-CANDIDATE
- `特上`: CONFLICTING-SOURCE

最終的にはPSマップ選択画面または説明書/1997攻略本の画像で確定する。

---

## 6. 10年以上経つとライバル買収額が2億円超の例

PS上級実プレイ:

- 10年を超えた時点で敵4号店の買収額が2億円超
- 3億円貯めて買収実行

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: PROVISIONAL / CASE OBSERVATION

### 意味

土地だけでなく、ライバル店の買収価値も長期的な町発展/店舗業績/地価上昇とともに大きくなる。

正確な買収価格式は未確定。

---

## 7. 店舗サイズ変更が客入りを激変させる実例

同PS上級記録:

- 赤字だった8号店を小型→中型へ改築
- 直後に客足が大幅改善
- その後は逆に自社2号店の客まで吸う状況
- 9号店も中型化すると赤字を脱したが、同じほど劇的ではなかった

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: CONFIRMED-COMMUNITY / OBSERVED-BEHAVIOR

### 実装上の意味

店舗規模は単に内装可能面積を増やすだけではなく、顧客独占率/店舗魅力へ直接または間接的に効いている可能性が高い。

しかし:

- サイズそのものに集客係数がある
- 品揃え可能数増加が原因
- サービス/清掃/見た目等を通じた間接効果

のどれかは未確定。

`store_size_attraction_bonus` を今の段階で勝手に作らない。

---

## 8. 長期プレイで時間経過が体感2〜3倍遅くなったという記録

18年目の実プレイで、初期より時間経過が2〜3倍遅く感じると筆者が記録している。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: PROVISIONAL

これは:

- 町オブジェクト/店舗/客増加によるPS実機処理落ち
- ゲーム内部の年数による速度変更
- 単なる体感

の区別がつかない。

baselineのゲームルールとして**絶対に再現しない**。性能特性の歴史的メモだけにする。

---

## 9. 今回のbaseline更新

強く採用できるもの:

```text
Advanced Scenario
- starting_money: 150,000,000 yen  # existing evidence
- objective: owner_rating >= 5
- owner rating evaluation: annual
- likely evaluation window: January/year transition
- store_count_10_required: false

Ending
- objective message
- transition to still image
- credits

Hidden map
- unlock: clear beginner + intermediate + advanced
- display_name: unresolved; "極上" strongly favored
```

未確定のまま残す:

- ★5の正確な計算式
- 年次評価の正確なtick
- 隠しマップの正式表記
- 隠しマップの開始資金/勝利条件
