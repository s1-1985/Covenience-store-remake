# 顧客タイプ別の怒りやすさ・待ち行列追加証拠 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 客のレジ待ち/怒りを一律タイマーにせず、客タイプ差を持つ可能性を検証する。
- `つまみだす` 操作が単なる万引き対処だけではなく、待ち行列管理にも使われる証拠を残す。

---

## 1. PS版攻略投稿: 「おじさん・おばさん」が最も怒りやすい

初代PS版のWazap攻略投稿では:

- 客が怒ると店員の能力が下がる
- レジ前で長く待っている `おじさんやおばさん` は `一番怒りやすい`
- 怒る前に `つまみだす` とよい

と明記される。

Source:
- https://wazap.com/cheat/%E5%AE%A2%E3%81%AB%E6%80%92%E3%82%89%E3%82%8C%E3%81%AA%E3%81%84%E3%82%88%E3%81%86%E3%81%AB%E3%81%99%E3%82%8B/51715/

証拠レベル: PROVISIONAL / PS-COMMUNITY-SINGLE-POST

### 意味

全客に同じ待ち時間上限を与えるより、客アーキタイプごとに忍耐/怒りやすさが異なる可能性が高い。

```text
CustomerArchetype
- patience_profile
- shopping_preferences
- visual_archetype
```

ただし正確な数値差は未確定。

---

## 2. 「怒り」は店員能力低下へつながる

初代専用店員Wikiでも、客に怒られると教育・体力以外の店員能力が2低下するとの記録がある。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

初代PS攻略投稿と方向が一致するため:

```text
customer angry at checkout
 -> staff penalty
```

という因果関係は強い。

証拠レベル: CONFIRMED-COMMUNITY（因果関係）

### まだ未確定

- 怒った客がどの店員へペナルティを与えるか
- 待ち時間だけが怒り条件か
- 客タイプごとの正確な閾値
- 怒りによる店舗人気/売上/独占率への直接影響

---

## 3. `つまみだす` はプレイヤーによる個別客への直接介入

既存の初代PS/SS記録では、客を選択して `つまみだす` 操作が可能で、万引き客対処に使えることが確認済み。

今回のPS攻略投稿では、**怒りそうな普通客を先に追い出す**という使い方も記録された。

したがって原作の `つまみだす` は:

- 万引き犯専用コマンドではない
- 選択した顧客個体を強制退店させる汎用操作

と考えるのが自然。

### baseline Customer API候補

```text
forceEjectCustomer(customerId, reason)
```

`reason` は実装ログ用であり、原作にreason入力UIがあるという意味ではない。

---

## 4. 客タイプ差は立地差とも接続する可能性が高い

既存PSプレイ記録:
- 学校付近では学生客が増える
- 客タイプごとに買い物傾向が異なる

今回:
- おじさん/おばさんは怒りやすいというPS攻略記録

これらを合わせると、町の立地は単に「何人来るか」だけでなく:

```text
Building / Area
 -> customer archetype mix
 -> product demand mix
 -> patience / queue risk mix
```

まで変える可能性がある。

最後の `patience / queue risk mix` は HYPOTHESIS だが、データ構造は対応可能にしておく価値が高い。

---

## 5. baseline方針

現時点では一律値を決めず:

```text
CustomerArchetype
- base_patience: UNKNOWN
- anger_multiplier: UNKNOWN

Known qualitative evidence:
- middle-aged/older man/woman visual archetypes: relatively anger-prone
```

として保存する。

正確な客タイプID/数値は1997年PS/SS攻略本、説明書、実機観測で復元する。
