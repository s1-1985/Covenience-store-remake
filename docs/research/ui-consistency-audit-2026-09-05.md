# 初代PS版 UI整合性監査：開始資産・総合評価・隠しマップ 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 実画面に見える所持金とシナリオの正式な初期資産を混同しない。
- 上級オーナー評価の確認場所をUI階層として固定する。
- 隠しマップ正式名の表記衝突を再評価する。

---

## 1. 初級の正式初期資産は2億円

初代専用攻略Wiki:
- 初級: 初期資産 2億円
- 中級: 初期資産 1.5億円
- 上級: 初期資産 1.5億円

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

独立したPS実プレイ記録でも:
- 初級は所持金2億円でスタート
- 中級/上級は1億5千万円

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html

証拠レベル: CORROBORATED-FIRST-TITLE

baseline:
```text
Beginner.starting_cash = 200_000_000
Intermediate.starting_cash = 150_000_000
Advanced.starting_cash = 150_000_000
```

---

## 2. 店舗選択スクリーンショットの1億8,000万円は「初期資産そのもの」ではない

PS実画面の店舗選択モーダルでは:
- 01年目01月01日
- 00:00
- 所持金 ¥180,000,000
- 選択中の店舗金額 ¥6,000,000

が確認できる。

Source:
- https://www.gavas.jp/upload/save_image/9180_2.jpg

この画面は年/月日/時刻だけ見ると開始直後に見えるが、初級の正式初期資産は上記複数資料で2億円。

したがって `¥180,000,000` は:
- 土地取得等のセットアップ途中で既に2,000万円支出済み
- 別モード/別手順の画面
- その他の開始前支出

などの可能性がある。

どれかはまだ未確定。

### 研究ルール

**このスクリーンショットを根拠に `starting_cash = 180_000_000` としてはいけない。**

画面から確定できるのは:
```text
current_cash_at_screenshot = 180_000_000
```
だけ。

証拠レベル:
- 画面中所持金: CONFIRMED-VISUAL
- 初級正式初期資産2億: CORROBORATED-FIRST-TITLE
- 2,000万円差額の原因: UNKNOWN

---

## 3. 上級のオーナー評価は `調査 → 全店収支グラフ → 総合評価`

初代専用攻略Wikiは上級について明記:
- クリア条件はオーナー評価を星5にすること
- `オーナー評価とは「調査」→「全店収支グラフ」にある総合評価の事`

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル: CONFIRMED-COMMUNITY-FIRST-TITLE

### UI baseline更新

旧研究では `調査` 内に収支グラフがあることまでは確認済みだったが、今後は階層を次まで固定してよい。

```text
RESEARCH / 調査
  -> ALL_STORE_FINANCIAL_GRAPH / 全店収支グラフ
      -> OVERALL_RATING / 総合評価 (★)
```

上級シナリオクリア判定で見る `owner_rating` は、この表示値と同一概念として扱う。

### ただし未確定
- `全店収支グラフ` 画面内のどこに星が表示されるか
- 月初更新と年次評価表示の関係
- 星の内部計算式

---

## 4. 隠しマップ正式名は「極上」が強い

PS/SS両機種の裏技資料とPSプレイ記録で、初級・中級・上級を全てクリアすると `極上` が出現すると一致。

Sources:
- https://menokenkou.work/konbiniura/
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://kakusi.jp/?p=91850

証拠レベル: STRONG-CORROBORATED

以前、一部PS上級プレイ記録に `特上` 表記があり衝突として保存したが、複数独立資料が `極上` を支持するため:

```text
hidden_map.display_name = "極上"  # strong candidate
```

まで昇格させる。

最終確定はPSのマップ選択画面画像が取れれば CONFIRMED-VISUAL にする。

---

## 5. 今回の実装上の確定事項

```text
ScenarioDefinitions:
  beginner.starting_cash = 200_000_000
  intermediate.starting_cash = 150_000_000
  advanced.starting_cash = 150_000_000

ResearchUI:
  調査
    -> 全店収支グラフ
       -> 総合評価

AdvancedClear:
  target = 総合評価 ★5

HiddenMap:
  unlock = clear beginner + intermediate + advanced
  name = 極上 (strong candidate)
```

---

## 6. 汚染・誤読防止

- PSスクショの1億8,000万円を初級開始資金にしない。
- `ザ・コンビニ2` のシナリオ資金・評価画面を流用しない。
- `特上` 表記は削除せず衝突履歴として残すが、baseline表示名には採用しない。
