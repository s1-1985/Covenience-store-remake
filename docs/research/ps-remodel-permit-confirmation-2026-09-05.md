# PS版：改築時の販売許可申請を確認 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

この文書は `day-boundary-economy-permits-2026-09-05.md` の「PS版でも改築時に販売許可申請できるか未確認」という箇所を**訂正する追加証拠**である。

## 結論

**PS版でも、既存店舗の改築時にタバコ・酒・薬の販売許可を追加申請できる。**

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

---

## 1. PS版中級プレイ記録の明示的な記述

PlayStation版の中級プレイ記録では、新店舗を安く確保するために:

- タバコ・酒・薬の申請が可能な土地を選ぶ
- 資金不足のため最初はタバコだけ申請
- 小型店として開店
- 酒・薬は「中型に改築するときで十分」と判断

という運用が明記されている。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

同記録では中型店舗への改築費について `1,200万円` とも記録される。

### ここから確定できること

PS版では:

```text
New Store Construction
  -> permit application possible
  -> open store

Existing Store
  -> Remodel
  -> additional permit application possible
```

というフローが存在する。

したがって実装データでは:

```text
permit_application_contexts:
  - NEW_CONSTRUCTION
  - REMODEL
```

をPS baselineへ入れてよい。

---

## 2. 申請可能性と実際の取得を分ける

立地選定時にタバコ・酒・薬すべてが申請可能な土地でも、資金都合で一部だけ取得して小型店を始め、後から改築時に残りを取得できる。

これはゲーム戦略上かなり重要。

### 原作らしい判断

- 好立地を土地価格が安いうちに先に確保
- 初期投資を抑える
- 小型店で最低限営業
- 資金が貯まったら中型へ改築
- 同時に追加販売許可を取得
- 品揃えと客単価を引き上げる

つまり販売許可は「出店時に一度だけ決める不可逆フラグ」ではない。

---

## 3. 近隣競合の許可排他は、後から申請する場合にも重要

同じPS版記録群では、近隣ライバルが薬品許可を取得済みのため、自店で薬品申請できない例がある。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

このため、後から改築時に申請する戦略にはリスクがある。

```text
土地取得時: 3許可とも申請可能
↓
タバコだけ取得して開店
↓
数ヶ月後、近隣ライバルが先に酒/薬を取得して出店？
↓
後から自店が申請できなくなる可能性
```

この競争まで原作で実際に発生するかは未確認だが、許可可否が周辺店舗状況依存なのでデータモデル上は**申請時点で再判定できる設計**にしておくべき。

この段落の競争シナリオ自体は HYPOTHESIS。

---

## 4. Saturn版の無料許可バグとの切り分け

Saturn版では「改築→販売許可→配置画面→申請画面へ戻る」操作で申請料を払わず許可取得できる裏技が報告される。

Source:
- https://menokenkou.work/konbiniura/

ここから分かるのは:

- PS: 改築時の追加許可申請そのものは正常仕様として存在
- SS: 同じ/類似フローに申請料回避バグがある版が存在

ということ。

**無料取得バグはPS baselineへ入れない。**

---

## 5. 中型改築費1,200万円

PS中級プレイ記録では:

- 小型→中型への改築に1,200万円
- 「中型には1200万あればできる」と複数回記載

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

### 注意

まだ未確定:

- 小型店建設費
- 中型店新規建設費
- 中型→大型改築費
- 改築費が店舗外観/向きで変わるか
- 改築時に既存内装資産がどう精算されるか

`1,200万円`だけを確定候補として保持する。

---

## 6. 今回の訂正

以前の研究ファイルにある:

> PS版でも改築時に販売許可申請できるか → 未確認

は、以後このファイルによって次へ更新する。

> **PS版でも改築時に販売許可申請可能。**

ただし以下はなお未確定:

- 許可取消が可能か
- 申請費
- 排他距離
- 改築を伴わず経営方針画面等から申請できるか
- 申請可否を再判定するタイミング

---

## 7. baseline実装への要求

販売許可システムは最低限:

```text
PermitType = TOBACCO | ALCOHOL | MEDICINE

StorePermitState
- owned_permits
- currently_available_permits

canApplyPermit(store, permitType, worldState)
applyPermit(store, permitType, cost)
```

のように、**現在の町状態を引数に再判定可能**な構造にする。

出店時にしか呼べない一回限りの処理として埋め込まない。
