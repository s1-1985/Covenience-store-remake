# 店員・客層・原作資料の証拠監査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的: 店員35人、顧客個体、建物と客層、店内運営について初代専用情報を追加し、検索結果へ大量に混入する『ザ・コンビニ2』以降の情報を baseline へ誤採用しないための監査記録を残す。

## 証拠レベル

- CONFIRMED-OFFICIAL: メーカー/現行公式
- CONFIRMED-VISUAL: 初代PS/SSの実画面で直接確認
- CONFIRMED-COMMUNITY: 初代PS/SS専用資料または複数の実機記録で一致
- PROVISIONAL: 初代向け単一記録、表記揺れ、解釈を含む
- HYPOTHESIS: 実装値にしない推測

---

## 1. 店員は35人、10店舗運営では30人必要

初代専用Wikiの店員ページで店員候補は計35人と明記される。

さらに中級の10店舗経営では、1店舗3人として自社だけで30人を雇用する必要があり、候補35人の大半を使うことになるとの攻略上の注意がある。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の意味

- 店員は無限生成キャラクターではなく、有限の固有候補リストとして扱うのが原作に近い。
- 10店舗まで拡張すると人材不足/人選がゲーム性になる。
- baseline の店舗定員は原則3人として扱う候補が強い。

ただし、特殊イベント等で一時的に4人目が店内に存在するかは別途確認する。

---

## 2. 採用能力と実務能力の二層構造を再確認

採用時に見える主な値:

- 給料
- 体力
- 学歴/教育
- 敏捷性
- 社交性

実務側:

- レジ
- 補充
- 警備
- 清掃
- 接客/サービス

初代専用Wikiで確認される関係:

- 教育 → レジ、警備の成長上限に関係
- 敏捷性 → 補充の成長上限に関係
- 社交性 → 清掃、接客の成長上限に関係
- 店長の教育値 → 部下の成長速度に関係
- レジ作業でレジ能力が上昇
- 補充作業で補充能力が上昇
- 掃除で清掃能力が上昇
- 店員の警備合計が店舗警備に影響
- 店員の接客合計が店舗サービスに影響

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 体力と休憩

- レジ/補充/清掃等で体力が減少。
- 体力0になると休憩室へ戻る。
- 原則として全回復するまで休憩。
- 敏捷性が高いほど休憩中に一度に2回復する確率が高いというコミュニティ検証がある。敏捷100で約90%という観測値は式未確定のため PROVISIONAL。

### 給料

Wikiの表示値は24時間営業時の日給として扱われ、短時間営業では支払額が減るとされる。

このため給与は単なる固定日額ではなく営業時間と連動している可能性が高い。

---

## 3. 初代で名前を確認できた店員 — 現時点の監査表

### 初代専用Wikiで確認済み

- 福本考仁
- 奥平康夫
- 金田哲也
- 長沢達也
- 竹中百合子
- 万田町子
- 南田洋次
- 市川智恵子
- 中山光次
- 森山雪之丈
- 田中幸子
- 菅原丈夫
- 雨中星人
- 里中涼子
- 杉村真智子
- 佐々木信雄
- 的場丈二

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

### 初代Saturn版実機記録で追加確認できた名前

- 小宮千秋
- 吉田有紀
- 小田伸行
- 竹中小百合
- 谷口明
- 南田洋次
- 的場丈二

Source:
- https://plaza.rakuten.co.jp/gorogorotaka/diary/202011180000/

証拠レベル: CONFIRMED-COMMUNITY / PROVISIONAL混在

同一人物と思われるものに表記差があるため、完全名簿へ統合する前にPS画面または攻略本で再確認する。

---

## 4. 名前の表記衝突 — 勝手に統合しない

検索中に以下の表記揺れ/衝突を確認した。

| 初代専用Wiki | 他の初代/実機記録 | 状態 |
|---|---|---|
| 竹中百合子 | 竹中小百合 | 要PS/SS差または誤記確認 |
| 福本考仁 | 福本孝仁 | 要画面確認 |
| 菅原丈夫 | 菅原文夫 | 要画面確認 |

重要: この種の違いは『ザ・コンビニ2』にも同名/類似名が登場するため、検索結果の世代混同で発生している可能性がある。

baseline データへは現時点で1つに統合せず、`aliases/uncertain_spelling` 相当として保留する。

---

## 5. 富永福子と「スーパー店員」イベント

初代PS版向けの裏技/攻略記録では、店員が80歳を超えた後、年齢更新時に一定確率で全能力100の「スーパー店員」状態になると報告されている。

- 最年長候補として `富永福子`
- 開始年齢58歳
- 最短でも22年経過して80歳に到達する

Sources:
- https://wazap.com/cheat/%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E5%BA%97%E5%93%A1/7161/
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-ai/ai-the-conbini-jokyu.html

証拠レベル: CONFIRMED-COMMUNITY（イベント存在）

確率、判定タイミング、全能力100の対象項目は追加検証が必要。

### ゲームデザイン上の意味

長期間プレイで店員が加齢すること自体が確認できる。したがって Staff には年齢/年更新を持たせる必要がある可能性が高い。

---

## 6. 店員候補プールが一時的に枯れる可能性

PS版Q&Aでは雇用候補を使い切ると `募集者がいません` となり、時間経過後に候補が再度出るという回答がある。

Source:
- https://wazap.com/question/%E5%BA%97%E5%93%A1%E3%81%8C%E3%81%84%E3%81%AA%E3%81%84/248501/

証拠レベル: PROVISIONAL

この仕組みは完全35人固定リストとの整合を要確認。退職/再募集/候補ローテーション等の内部ルールがある可能性がある。

**実装前に確定しない。**

---

## 7. 顧客タイプ — 初代で直接言及される客層

初代PS版の回顧/実機記録で明示される客層:

- 学生
- 老人/おじいさん
- OL
- 主婦
- サラリーマン

Source:
- https://www5f.biglobe.ne.jp/~zelda/konbini1.htm

別の初代SS実機記録では、画面上の集団として:

- 中学生風
- サラリーマン
- マダム/主婦
- 老人
- 親子連れ
- 汗をかいた客

等が確認/言及されている。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY

### 重要

客グラフィックの見た目分類と内部の顧客タイプIDが完全一致するかは未確定。Android版 baseline の archetype 数をこの列挙だけで固定しない。

---

## 8. 建物/立地が客層構成へ影響する

初代PS版のプレイ記録で:

- 学校の近くに出店した2号店では学生客が増える
- 客タイプごとに買う傾向が異なる

と明示される。

Source:
- https://www5f.biglobe.ne.jp/~zelda/konbini1.htm

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の要求

町の建物を単純な `shopping_population` 数値だけにしてはいけない可能性が高い。

将来の world データは少なくとも:

```text
BuildingDemand
- shopping_population
- customer_archetype_weights
- possibly time_of_day_weights
```

のように、人口と客層構成を分離できる形が望ましい。

時間帯重みについては現段階では HYPOTHESIS。

---

## 9. 顧客は個体として「購入内容」を持つ

初代PS/SSの記録では客を選択して情報を見ると、何を購入したか確認できる。

さらにプレイヤーは客を `つまみだす` 操作で直接退店させられ、万引き客への対処として使われる。

Sources:
- https://www5f.biglobe.ne.jp/~zelda/konbini1.htm
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY

### baseline Customer が必要とする状態候補

```text
Customer
- id
- archetype
- position
- target_products
- basket/purchased_products
- state
- patience/anger state
- theft/suspicion state
- exit_reason
```

`patience` 等の具体的内部数値は未確認だが、レジ待ちで怒る状態は確実に存在する。

---

## 10. まとめ買い/ついで買いが原作の重要ループ

初代SS記録では、客は目的の商品1点だけを機械的に買うのではなく、店内移動中に複数商品を合わせて購入する。

レイアウトによって客を店内に回遊させ、複数商品を取らせる戦術が成立する。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY

### 未確定

- 目的商品数
- ついで買い確率
- 商品カテゴリ間の相関
- ワゴンの「注目度」が正確に何へ効くか

『ザ・コンビニ2』には詳しい商品×客層表があるが、初代へ流用しない。

---

## 11. 客の忍耐に客層差がある可能性

初代PS向け攻略投稿では、おじさん/おばさん系の客がレジ待ちで怒りやすいという経験則が報告される。

Source:
- https://wazap.com/cheat/%E6%80%92%E3%82%8B%E5%AE%A2%E3%81%B8%E3%81%AE%E5%AF%BE%E5%87%A6/210888/

証拠レベル: PROVISIONAL

客 archetype ごとの忍耐時間を実装する根拠候補にはなるが、正確な値や序列はまだ hard-code しない。

---

## 12. 店員の遅いレジが「怒り→店員能力低下」へつながる

複数の初代記録で:

1. レジ行列が発生
2. 待たされた客が怒る
3. 店員の能力が下がる

という悪循環が確認できる。

Sources:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY

これは単なる「客を逃す」だけでなく、人材育成にも行列がダメージを与える設計。

---

## 13. プレイヤーが手動で商品補充できる可能性

初代SS版のプレイ記録に、店員の補充が遅い際に `プレイヤーが商品の補充を出来るので手伝ってあげる` という記述がある。

Source:
- https://plaza.rakuten.co.jp/azumakasi/diary/201101050000/

証拠レベル: PROVISIONAL

### 重要性

事実なら、プレイヤーは方針設定だけのマネージャーではなく、ライブ店内へ直接介入できる。

説明書または別の初代資料で corroborate するまでは baseline 操作として確定しない。

---

## 14. 自販機だけの小型店でも運営可能という報告

初代PS向け攻略投稿では、小型店舗・店員1人・自販機中心/自販機のみの構成でも利益を出せるという戦術がある。

Source:
- https://wazap.com/cheat/%E8%87%AA%E8%B2%A9%E6%A9%9F%E3%81%AE%E3%81%BF%E3%81%AE%E5%BA%97/7165/

証拠レベル: PROVISIONAL

### 推測してはいけない点

この記録だけで「自販機はレジを通らない」「補充不要」等とは断定できない。

ただし自販機類が通常棚と異なるオペレーション負荷を持つ可能性を示すため、商品設備モデルでは `sales_mode` を将来分離できる設計が望ましい。

---

## 15. 内装編集/雇い直しによる原作の抜け道

初代専用攻略Wikiに以下の挙動が報告される。

- 閉店中/営業時間外に内装編集へ入ると店内の汚れが一気に消える
- 疲労した店員を解雇→即再雇用すると体力全快状態で戻る

Source:
- https://wikiwiki.jp/theconveni1/%E5%B0%8F%E3%83%8D%E3%82%BF%E3%83%BB%E8%A3%8F%E6%8A%80

証拠レベル: CONFIRMED-COMMUNITY（原作挙動/抜け道）

### 再現方針

「原作互換」の範囲を決める際に別途 `docs/decisions/` で判断する。

- 経営上意味のある本来仕様は再現する
- 明白なバグ/抜け道は必ずしも再現しない
- ただし互換性検証のため、原作に存在した事実は研究記録へ残す

---

## 16. 原作資料として価値の高い攻略本を特定

### 『ザ・コンビニ あの町を独占せよ 必勝攻略法』

- Fighting Studio
- 双葉社
- 1997年5月
- 111ページ
- PS/SS対象
- 各種データ、全マップ、隠しマップまで掲載と書誌説明

Source:
- https://www.kinokuniya.co.jp/f/dsg-01-9784575160543

優先度: VERY HIGH

### 『ザ・コンビニ ～あの町を独占せよ～ レイアウトデザインセレクション74』

- 1997年
- PS/SS対応との中古書誌情報
- レイアウトKit、攻略&データ、テクニック、データリストを含む
- 現存写真では多数の什器アイコンを並べたレイアウト素材ページが確認できる

Sources:
- https://books.rakuten.co.jp/rb/880163/
- https://jp.mercari.com/item/m28575216207

優先度: VERY HIGH

原作の画像素材自体をリポジトリへコピーしない。数値/仕様を読み取れる場合だけ出典付きで研究文書化する。

### 『ザ・コンビニ完全研究 全機種対応』

- Zest
- 1997年12月
- ISBN 9784916090812

Sources:
- https://www.amazon.co.jp/dp/4916090817
- https://www.books.or.jp/book-details/9784916090812

PC/PS/SS差の照合に使える可能性が高いが、「全機種対応」のため版差を明記して利用する必要がある。

---

## 17. 最大の情報汚染源: 『ザ・コンビニ2』店員データ

検索では初代店員名を調べても、非常に頻繁に『ザ・コンビニ2』の完全店員表が上位へ出る。

さらにシリーズ間で同名/類似名が再利用されているため、**名前が一致するだけでは初代の証拠にならない。**

禁止:

- 2の能力値を初代キャラへコピー
- 2の年齢/給料を初代へコピー
- 2の35人名簿を初代名簿の穴埋めに使用

許可:

- 「検索結果が続編由来か」の照合
- シリーズ内変更点の比較
- 初代で再確認すべき名前候補を抽出するだけ

---

## 18. 現時点での店員名簿復元状況

- 初代専用Wikiで明示: 17名
- 初代SS記録から追加候補: 少なくとも5名程度
- PS向けスーパー店員資料から富永福子を追加
- 表記衝突あり
- 35名の完全な「PS baseline 名簿 + 初期値 + 上限値」は未完成

### 完了条件

店員データは以下が35名全員について揃うまで「完全復元」としない。

```text
StaffCandidate
- canonical_name
- platform/source
- starting_age
- salary
- stamina
- education
- agility
- sociability
- initial_register
- initial_restock
- initial_security
- initial_cleaning
- initial_service
- growth/ceiling notes
```

値が不明な欄は null のまま保持し、続編で補完しない。

---

## 19. 顧客システムの現時点の確度

### CONFIRMED-COMMUNITY

- 客は個体として店内を移動する
- 客層が複数ある
- 客層ごとに購買傾向が違う
- 周辺建物/立地で客層が変化する
- 客を選択して購入内容を見る
- まとめ買い/ついで買いがある
- レジ待ちで怒る
- 客をつまみ出せる
- 万引き客が存在する

### PROVISIONAL

- 客層ごとの具体的忍耐値
- 学生が万引きしやすい等の確率差
- 各カテゴリ×客層の正確な購入表
- 各建物の customer archetype weights

### HYPOTHESIS

- ついで買いの数式
- 時間帯別 archetype weights
- 商品間相関

---

## 20. 次の優先調査

1. 攻略本/説明書画像から35人完全名簿を回収
2. PS版とSS版の店員名表記差を確定
3. 客タイプ全種類とスプライト分類を実画面で数える
4. 学校、住宅、会社、役所、駅等の建物→客層対応を集める
5. プレイヤー手動補充を別ソースで確認
6. 自販機の会計/補充フローを確認
7. レジ待ち怒り判定の客層差を検証
8. 客情報ウィンドウに表示される全フィールドを確認
9. 店員候補の再募集/枯渇ルールを確認
10. 加齢・退職・スーパー店員の正確な判定を確認

---

## 21. baseline設計への暫定結論

この調査から、前回のプロジェクトのように店舗運営を集約数値へ潰す設計は避ける。

原作らしい最低モデル:

```text
Town building -> customer archetype mix
          ↓
Individual customer spawn
          ↓
Physical path through fixtures
          ↓
Primary purchase + incidental purchases
          ↓
Queue / anger / theft / checkout / exit

Staff candidate traits
          ↓
Operational skills + stamina
          ↓
Autonomous register/restock/clean/rest decisions
          ↓
Skill growth and store-level service/security
```

ただし数式・全データは未完成なので、本格実装開始の根拠としてはまだ調査継続が必要。