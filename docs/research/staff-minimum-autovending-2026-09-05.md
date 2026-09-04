# 店員最小人数・自販機店舗の追加調査 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 「1店舗3人固定」「最低2人」という過去仮説を追加証拠で修正する。
- 自動販売機だけで営業する店舗の存在を記録する。
- 店員数のbaselineデータモデルをハードコードしないための根拠を残す。

---

## 1. PS版攻略投稿に「店員1人」の小型店舗が明記される

初代PS版の攻略投稿では、自動販売機だけで稼ぐ方法として:

- 小型店舗を設置
- 店員を1人だけ置く
- 店内は自動販売機だけにする
- 比較的放置運営できる

という方法が記録されている。

Source:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/

同じ内容は初代PS版攻略一覧にも表示される。

証拠レベル: PROVISIONAL / PS-COMMUNITY-SINGLE-POST

### 重要な修正

過去研究では:

1. PS新規出店標準 = 店長1 + 店員2 = 3名
2. Saturn実機記録 = 小型店を2人体制で運営可能

まで確認していた。

今回さらに:

3. PS攻略記録 = 小型店を1人体制で運営可能

が追加された。

したがって現時点では:

```text
standard_new_store_staff = 3
operational_minimum_staff <= 1
likely_max_staff = 3
```

とするのが最も安全。

**`minimum_staff = 2` をハードコードしてはいけない。**

---

## 2. 新規出店時の3名と、営業中の人数制限は別概念

PS版レビューでは新規出店フローとして:

- 店長1名
- 従業員2名

を雇うことが記録されている。

Source:
- https://codevis.nobody.jp/review-ps/the_convini.html

これは「開店手続き時の標準セット」であり、営業開始後の異動/解雇/配置変更で1〜2人へ減らせる可能性と両立する。

### データモデル候補

```text
StoreStaffingRules
- initial_required_manager: 1
- initial_suggested_workers: 2
- max_total_staff: 3          # strong candidate
- min_operational_staff: 1    # provisional
```

まだ確認が必要:

- 店員0人で店舗を営業できるか
- 自販機のみなら0人でも売れるか
- `店長` を必ず1名残す必要があるか
- 1人体制へする具体的操作（異動/解雇等）

---

## 3. 自動販売機だけの店舗が成立する

初代PS攻略投稿では「店内を自動販売機だけ」にした小型店でも利益が出るとされる。

別投稿でも「自動販売機だけの店でも結構売り上げが出る」と記録される。

Source:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/

証拠レベル: CONFIRMED-COMMUNITY-LIGHT（複数投稿だが詳細検証ではない）

### 重要なゲームロジック上の疑問

通常棚の商品は:

- 商品取得
- レジへ移動
- 会計

が基本ループ。

しかし自販機だけの店舗が1人でかなり放置できるなら、自販機商品は:

A. 客が自販機で購入完了し、レジを通らない

または

B. レジは必要だが補充頻度が低く、1人で処理可能

のいずれか。

現時点では**レジ通過不要とは断定しない**。

実機動画/客の動線で確認が必要。

---

## 4. 自販機は物理的な目的地である

初代専用内装Wikiでは、向かい合わせの自販機群で「奥へ買いに行く客」と「戻る客」が詰まる例がある。

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

証拠レベル: CONFIRMED-COMMUNITY

したがって自販機は単なる自動売上オブジェクトではなく:

- 顧客がそこまで歩く
- interaction sideを持つ
- 客同士の往来を発生させる

販売設備である。

### baseline Fixture model

```text
VendingMachineFixture
- footprint
- interaction_side
- product_family
- capacity
- requires_checkout: UNKNOWN
- restock_behavior: UNKNOWN
```

---

## 5. 1人店舗の意味

もし1人店舗が正常に成立するなら、原作の店舗経営には明確な人件費トレードオフがある。

- 3人: レジ/補充/掃除を並列化しやすい、高人件費
- 2人: 低コストだが混雑/休憩重複リスク
- 1人: 最小人件費、通常店舗では処理能力不足、自販機特化なら成立

これは初代らしい経営判断として再現価値が高い。

ただし「人数ごとの給与合計」と「営業時間による給与補正」の正確な式は未確定。

---

## 6. 今回の訂正履歴

研究上の表現を次のように更新する。

旧:
- `1店舗3人固定に近い`

修正1:
- `3人が標準/上限候補。Saturnでは2人運営可能`

今回の修正2:
- `PS攻略記録では1人運営も可能。最低人数は少なくとも1人まで下げられる可能性が高い`

### 現時点baseline

```text
staffing:
  normal_start: 3
  observed_operating_counts:
    - 1  # PS community strategy, provisional
    - 2  # Saturn detailed playlog
    - 3  # PS standard + many playlogs
  max_total: 3  # strong candidate, not yet official visual
```

---

## 7. 次の確認事項

1. PS実機で1人へ異動できる操作画面
2. 0人営業可否
3. 自販機購入客のレジ通過有無
4. 自販機商品の補充主体
5. 自販機の全種類、価格、容量、維持費
6. 自販機専用商品と通常棚商品カテゴリの対応
7. 1人店で店長/一般店員どちらを残せるか
