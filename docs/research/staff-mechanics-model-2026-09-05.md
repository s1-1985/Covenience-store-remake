# 店員能力モデル・成長・休憩挙動 追加調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 店員35名の完全名簿そのものとは別に、店員データがどのような二層構造で管理されているかを復元する。
- 雇用画面の表示値と、配属後の実務能力値を混同しない。
- 成長上限、店長教育、体力・休憩、雑誌紹介イベントの影響を初代専用資料から整理する。

## 証拠レベル
- CONFIRMED-COMMUNITY: 初代PS/SS専用攻略Wikiで明示される挙動
- PROVISIONAL: 同Wiki内で推測表現・未検証表記があるもの
- HYPOTHESIS: 実装上の推定。原作値として確定しない

---

## 1. 店員候補は35人の有限プール

初代PS/SS専用Wikiでは、店員候補は合計35人と明記される。

さらに10店舗を本格運営する場合、35人中30人を雇う必要があるとされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の意味

店員はランダム自動生成ではなく、固有人物35名の有限マスタとして持つべき。

```text
StaffMaster[35]
```

ただし完全名簿・年齢・給与・各数値はまだ未復元。

---

## 2. 雇用画面と異動画面では、表示される能力体系が別

初代専用Wikiで明記される。

### 雇用画面側

- 給料
- 体力
- 学歴
- 敏捷性
- 社交性

### 異動/配属後の実務側

- 教育
- レジ
- 補充
- 警備
- 清掃
- 接客
- 体力
- 給料

重要なのは、雇用画面で高く見える人物でも、実際の初期レジ等が低い場合があること。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### baseline要求

一つの `staff_skill` 配列だけで表現しない。

```text
StaffCandidateProfile
- salary_display
- stamina_display
- education_background
- agility
- sociability

StaffRuntimeState
- education
- register
- restock
- security
- cleaning
- service
- stamina_current
```

雇用画面値と実働初期値は別フィールドとして保持する。

---

## 3. 雇用画面の能力値は、実務能力の「上限」に対応することが多い

初代専用Wikiでは、雇用時のパラメータと実務側の上限について次の対応が示される。

- 学歴 ≒ 教育
- 教育がレジ・警備の上限
- 敏捷性が補充の上限
- 社交性が接客・清掃の上限
- 給料と体力は雇用時表示値が概ねそのまま実務側へ反映

ただし例外人物が存在する。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 推奨データモデル

```text
SkillCaps
- register_cap      <- usually education
- security_cap      <- usually education
- restock_cap       <- usually agility
- cleaning_cap      <- usually sociability
- service_cap       <- usually sociability
```

`usually` が重要であり、全人物一律の数式にせず、人物別overrideを許容する。

---

## 4. 教育は店員本人の成長上限と、店長としての部下成長速度の両方に関与

初代専用Wikiでは:

- 教育はレジ・警備の上限に関係
- 店長の教育が、同店舗の他店員の能力成長速度に影響
- 教育が低い店長の店では、他店員が何年経っても上限へ届かないことがある

とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### baseline要求

店長は単なる肩書きフラグではなく、育成係数へ使う。

```text
growth_gain = action_growth * manager_education_factor
```

正確な係数式は未確定なので、数式は HYPOTHESIS。

---

## 5. 作業ごとに能力が伸びる

初代専用Wikiで確認できる範囲:

- レジ: レジ打ちをするたびに上昇
- 補充: 補充作業をするたびに上昇
- 清掃: 床を掃除すると上昇
- 警備: 時間経過で上昇する可能性が示唆されるが未確定

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル:
- レジ/補充/清掃の作業成長: CONFIRMED-COMMUNITY
- 警備の時間成長: PROVISIONAL

### 実装上の意味

経験値→レベル方式より、各タスク実行時に該当能力へ直接成長判定を入れる方が原作構造に近い。

---

## 6. 体力は固定上限を持ち、作業で減少し0になると休憩室へ戻る

初代専用Wikiでは:

- 体力はレジ、補充、清掃で減少
- 0になると休憩室で全快まで待機
- 体力が高いほど連続作業時間は長い
- 休憩時間自体も長くなる傾向があるが、往復ロスを含めると高体力ほど効率的

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### baseline要求

```text
WORKING -> stamina decreases
if stamina <= 0:
    state = RETURN_TO_BREAKROOM
BREAK -> stamina recovers
if stamina == stamina_max:
    state = AVAILABLE
```

複数人が同時休憩できる既存Saturn実機記録とも整合する。

---

## 7. 敏捷性は補充上限だけでなく、休憩時の体力回復効率にも関係する可能性

初代専用Wikiでは:

- 通常は休憩中に体力が1ずつ回復
- 敏捷性が高いと2回復する確率が上がるらしい
- 敏捷100では高確率で2回復と記録

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: PROVISIONAL

Wiki自身が観察ベースの表現であり、正確な確率は未検証。

実装初期では補充上限だけ確定採用し、回復ボーナスはfeature flag / tuning parameterとして保留する。

---

## 8. 客から怒られると複数能力が低下する

初代専用Wikiでは、レジ待ち等で客に怒られると:

- 教育と体力を除く実務能力が約2低下
- 雑誌紹介などで上限を超えて伸びた分も低下する

とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 対象候補

- レジ
- 補充
- 警備
- 清掃
- 接客

正確に常時 `-2` かは原作画面で最終確認余地あり。

---

## 9. 雑誌紹介イベントは店長の能力上限突破を起こす

初代専用Wikiでは、店舗の清掃が高いと店長が雑誌で紹介されることがあり、紹介時に:

- 体力以外の店長能力が上昇
- 通常固定の教育も上昇可能
- 通常の成長上限へ達している能力もさらに上昇可能

とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 重要な実装要求

通常上限と、イベントによる上限超過を区別する。

```text
base_cap
current_value  # event boost can exceed base_cap
```

`current_value = min(current_value, base_cap)` を常時適用すると原作挙動を壊す。

---

## 10. 給料は「1日当たり」で、営業時間に応じて異動画面表示が変わる

初代専用Wikiでは:

- 雇用画面に表示される給料は24時間営業時の1日当たり給料
- 営業時間を短縮してから異動画面を見ると給料表示が安くなる

とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の意味

給与は単純な固定日額ではなく、営業時間比例または勤務時間計算が存在する可能性が高い。

ただし正確な按分式は未確定。

```text
salary_actual_day = f(base_24h_salary, opening_hours)
```

---

## 11. 店員AIはレジ最優先ではない

初代専用FAQでは:

- 客がレジに並んでいても補充等の別タスクがあると、店員はぎりぎりまでレジへ向かわない
- 2人が同時にレジへ向かうと片方が休憩室へ戻ることがある
- レジ対応中の店員が低体力だとすぐ休憩へ戻り、レジ無人状態が発生する
- 後から並んだ客を先に会計することもある

Source:
- https://wikiwiki.jp/theconveni1/FAQ

証拠レベル: CONFIRMED-COMMUNITY

### baseline要求

最適化された現代的AIにしすぎない。

最低限:

```text
Task candidates:
- register
- restock
- clean
- break

Each staff chooses independently.
No global guarantee that register is always covered.
```

ただし、原作の不具合そのものを完全再現する必要はなく、「個別意思決定で空白時間が起き得る」程度を構造として残す。

---

## 12. 現在確認済みの特徴的人物

初代専用Wikiから人物ごとの差が大きいことを確認できる。

例:
- 福本考仁: 学歴95、店長向き
- 万田町子: 雇用画面より実教育が高い例
- 雨中星人: 敏捷100、雇用画面から予想しづらい教育100の例
- 的場丈二: 体力/敏捷は高いが初期レジが極端に低い
- 里中涼子 / 杉村真智子: 雇用画面値は高いが初期実務値が低い

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 意味

「雇用画面値から実務初期値を計算する汎用式」だけでは再現できない人物が存在する。

35名分について、最終的には人物ごとの:

```text
candidate_display_values
runtime_initial_values
runtime_caps / exceptions
```

を個別マスタ化する必要がある。

---

## 13. 今回の確定事項

PS/SS baselineへ強く採用可能:

```text
Staff pool size = 35

Candidate-visible fields:
- salary
- stamina
- education_background
- agility
- sociability

Runtime fields:
- education
- register
- restock
- security
- cleaning
- service
- stamina

Typical cap mapping:
- register/security <- education
- restock <- agility
- cleaning/service <- sociability

Manager education affects subordinate growth.
Task execution grows related skills.
Work consumes stamina; zero stamina triggers break.
Magazine feature can raise fixed education and exceed normal skill caps.
Customer anger can reduce several runtime skills.
Salary display depends on store opening hours.
```

---

## 14. 未確定事項

優先度高:

1. 35名全員の正式氏名
2. 各人の年齢
3. 24h基準給料
4. 雇用画面5項目の全数値
5. 実務6項目の初期値
6. 人物別の正確な上限値/例外
7. 店長教育→部下成長速度の式
8. 作業1回あたりの成長量/確率
9. 体力消費量
10. 休憩回復tickと敏捷補正確率
11. 雑誌紹介イベントの発生条件・上昇量
12. 怒られた時の能力減少量が常に2か
13. 給料の営業時間按分式
14. 雇用・解雇時の費用/制約

完全名簿の復元には、PS/SS原作雇用画面の連続キャプチャ、当時攻略本、または現行コンソールアーカイブス版の実機確認が最も有効。

---

## 15. 出典

初代PS/SS専用:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://wikiwiki.jp/theconveni1/FAQ

後続作の店員表・能力値は本ファイルの根拠に使用していない。
