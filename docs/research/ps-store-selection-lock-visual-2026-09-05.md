# PS版 店舗6候補・開始時解禁状態の直接画像証拠 2026-09-05

対象: 1997 PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的: これまでSS実プレイ記録やアイコン形状から推定していた店舗サイズ/向き/解禁状態を、PS実機スクリーンショットで直接確認する。

## 1. PS店舗選択画面に6候補が2行×3列で表示

ピコピコ大百科のPS1版掲載画像に、ゲーム開始直後の店舗選択画面がある。

Source:
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://www.gavas.jp/upload/save_image/9180_2.jpg

画面上で直接確認できる:
- `01年目01月01日`
- `[快晴]`
- `00:00`
- 所持金 `¥180,000,000`
- `店舗を選んで下さい`
- 店舗アイコンが **2行×3列 = 6候補**
- 左上候補選択時の表示価格 `¥6,000,000`

Evidence: `CONFIRMED-SCREENSHOT-PS`。

## 2. 開始時に選択可能なのは左列2候補、残り4候補はグレーアウト

同画像では:
- 左上候補: カラー表示、選択中
- 左下候補: カラー表示
- 中央上/中央下: 暗色グレー表示
- 右上/右下: 暗色グレー表示

となっている。

したがってPS版のこの開始状態では、6候補すべてが同時解禁されているわけではなく、**2候補のみ選択可、4候補はロック状態**と読むのが自然。

Evidence: `CONFIRMED-VISUAL-PS` for 2 active + 4 disabled appearance.

### 実装上の意味

店舗variantを単なる6個の常時選択可能リストとして実装しない。

```text
StoreVariantDefinition
- sizeTier
- orientation
- unlocked
- constructionPrice
```

解禁判定をStoreVariantごと、またはSizeTierごとに持てるようにする。

## 3. 6候補は「3サイズ × 2方向」構造を強く支持

6アイコンは列ごとに外観規模が段階的に大きく見え、各列に上下2種類の向き違いとみられる候補が存在する。

既存の初代資料では:
- 店舗規模として小型/中型/大型が存在
- 店舗向きとして縦型/横型が存在
- SS初級開始時は最小店舗のみ建設可能という実プレイ記録

がある。

これらを合わせると:

```text
6 variants ≈
small_vertical
small_horizontal
medium_vertical
medium_horizontal
large_vertical
large_horizontal
```

という対応はかなり強い。

ただし、**画像だけで上段=縦型/下段=横型、またはその逆を断定しない**。

Evidence:
- 3 size tiers: confirmed by first-title sources
- 2 orientations: confirmed by first-title play sources
- 6 = 3×2 mapping: `STRONG-INFERENCE`
- exact row/orientation mapping: `UNKNOWN`

## 4. PS初級開始時も小型2方向のみ解禁の可能性が高い

既存SS初級記録では「最小店舗のみ建設可能」とされる。

今回のPS画像で左列2候補だけが有効、残り4候補が無効に見えるため、PS側でも少なくともこの開始状態では:

```text
small variants: unlocked
medium variants: locked
large variants: locked
```

の可能性が非常に高い。

ただし画像掲載元がシナリオ名を同じ画面内に表示していないため、初級であることは周辺証拠（開始資産・既知開始フロー）と合わせた判断として扱う。

Confidence: `STRONG-PS-VISUAL / scenario context inferred`。

## 5. 左上小型候補の建設価格6,000,000円を再強化

左上候補選択時に `¥6,000,000` が明示されるため:

```text
PS StoreVariant[left_top_small].constructionPrice = 6_000_000
```

は直接画像証拠。

左下候補も同一サイズ帯と見られるが、同じ画像では左下選択時価格を表示していないため:

```text
PS StoreVariant[left_bottom_small].constructionPrice = UNKNOWN
```

を維持する。

向きだけ違う同サイズなら同額である可能性は高いが、攻略本/実機切替で確認する。

## 6. 既存のPS/SS解禁差調査との整合

既存PS上級長期プレイでは開始時から中型店を建設した例がある。

したがって解禁条件は単純なゲーム年数だけでなく:
- シナリオ
- 過去クリア状態
- 難易度
- PS/SS差

のいずれか/複合で変わる可能性が残る。

今回の画像は「開始時4候補がロックされる状態がPSにも存在する」ことを確定方向へ進めたが、解禁条件そのものは未確定。

## 7. 攻略本到着後に最優先で照合する項目

1. 6候補の正式な小/中/大・縦/横対応
2. 各候補の建設価格
3. 各候補の編集可能グリッド寸法
4. 中型・大型の解禁条件
5. シナリオ別初期解禁差
6. PS/SS差

これらが埋まれば `StoreVariantDefinition` を確定マスターへ昇格できる。
