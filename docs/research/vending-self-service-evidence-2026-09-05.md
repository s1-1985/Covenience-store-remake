# 初代PS 自動販売機セルフサービス販売の追加証拠 2026-09-05

対象: 1997 PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的: 自動販売機だけの店舗が成立するという既存攻略投稿を、別のPSプレイ記録から補強し、通常棚と自販機の購入フローを分離する必要性を評価する。

## 1. PS版Wazapに自販機だけの店舗が成立する独立記録

PS版初代ページには少なくとも2投稿がある。

- `自動販売機だけの店でも結構売り上げがでます`
- `小型店舗を設置して店員一人だけ置き、お店の中は自動販売機だけにする。結構儲かる`

Sources:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/?WAZAP_LAYOUT=0
- https://wazap.com/game/12333/cheats/?order=zupped

Evidence: `PROVISIONAL-COMMUNITY-PS / TWO-POSTS`。

## 2. 別のPSレビューで「自販機購入後に店内へ入る」客行動を確認

ピコピコ大百科のPS1版レビューには、怒りやすい客を「つまみだす」運用の説明として、客が:

1. 自販機で酒・タバコを買う
2. その後に店へ入店する

という順序の観察が記載されている。

Source:
- https://www.gavas.jp/products/detail.php?product_id=9180

この記述はレビュー本文であり公式仕様表ではないが、通常棚の商品取得→レジ会計という流れとは異なり、**自販機購入が入店前に成立している**ことを強く示唆する。

Evidence: `PROVISIONAL-DIRECT-PLAY-PS / INDEPENDENT-SOURCE`。

## 3. 複数ソースを合わせた構造判断

以下が同時に成立する:

- 自販機だけの店で売上が立つという独立投稿が複数ある
- 自販機で商品購入後、そのまま店へ入る客行動の記録がある
- 初代内装資料では自販機も客がアクセスするdestinationとして経路混雑を起こす

これらを合わせると、自動販売機は通常商品棚とは異なる **セルフサービス販売フロー** を持つ可能性が高い。

現時点の実装候補:

```text
FixtureSaleMode
- CHECKOUT_REQUIRED      # 通常棚/ワゴン等
- SELF_SERVICE           # 自販機候補
```

Confidence for `vending -> self-service without normal checkout`: `STRONG-PROVISIONAL`。

## 4. まだ確定できない細部

以下は攻略本/実機で確認するまで固定しない。

- 自販機だけの店舗でレジを0台にできるか
- 店員1名がシステム上必須か、補充のため実用上置いているだけか
- 自販機在庫の補充は店員タスクか自動処理か
- 自販機購入時に客の所持商品リストへ入るのか、その場で会計完了するのか
- 自販機だけ利用した客が店舗来店者数へどう計上されるか
- 酒/タバコ自販機にも販売許可が必要か（可能性は高いが画面で再確認）

## 5. Remake実装への反映

客AIを単一の:

```text
enter store -> choose products -> checkout -> leave
```

だけに固定しない。

少なくとも将来:

```text
CustomerPurchaseFlow
- normal_store_purchase
- vending_purchase
```

を分岐可能な設計にする。

自販機客については:

```text
approach vending
-> purchase candidate
-> optionally enter store for additional shopping
-> leave
```

という状態遷移を表現できるようにする。

ただし最終挙動は攻略本とPSコンアカ動画で確定する。

## 6. 攻略本到着後の確認項目

『レイアウトデザインセレクション74』『攻略の帝王』で以下を探す:

1. 自動販売機の利用方法説明
2. レジを経由するかの注記
3. 自販機の価格/維持費/容量/注目度
4. 自販機の対応商品種別
5. 自販機だけの店舗サンプル/攻略例
6. 補充担当・在庫処理

ここが確認できれば `FixtureDefinition.saleMode` を確定値へ昇格できる。
