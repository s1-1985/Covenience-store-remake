# PS/SS 販売許可フローとプラットフォーム差異 2026-09-05

対象: 1997年 PlayStation / Sega Saturn 版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 酒・タバコ・薬の販売許可について、PS/SSで共通とみなせる部分と、SS固有とみられる挙動を分離する。
- Remakeで「PS/SS版」を一括実装する際に、SS固有バグをPS仕様へ誤混入しない。

主要ソース:
- 初代PS/SS専用攻略Wiki FAQ: https://wikiwiki.jp/theconveni1/FAQ
- Wazap! 2008年投稿「許可申請料がタダ」: https://wazap.com/cheat/%E8%A8%B1%E5%8F%AF%E7%94%B3%E8%AB%8B%E6%96%99%E3%81%8C%E3%82%BF%E3%83%80/425512/

---

## 1. 販売許可は酒・タバコ・薬の3系統

2008年のSS実機投稿では、土地購入時に `酒・タバコ・薬` の3種すべてが扱える土地を選ぶ手順が明示されている。

初代専用FAQでも、既存コンビニの近隣では酒・タバコ等の販売許可が下りづらくなるとされる。

証拠レベル:
- 3種の独立許可が存在: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC
- 正確な申請料: UNKNOWN
- 正確な排他距離/判定式: UNKNOWN

既存研究ノートの「3種は個別許可」という方針を補強する。

---

## 2. 許可取得は店舗サイズ選択/改築フローと結びついている

SS版裏技投稿の手順では:

1. 酒・タバコ・薬が扱える土地を購入
2. 最初の出店時には許可申請をしない
3. 内装完成後、営業開始前に `改築` を選ぶ
4. 再び店舗サイズ決定画面へ入る
5. その画面で `許可` と `所持金` を確認する
6. 許可申請後、内装画面へ進む

とされる。

この記述から、少なくともSS版では:
- 店舗サイズ/改築画面に販売許可状態または申請操作が存在する
- 同画面で所持金も確認できる
- 許可申請後に内装画面へ遷移する

というUI状態遷移が読み取れる。

証拠レベル: PROVISIONAL-HIGH-VALUE / SS-PLAY-RECORD

### 実装上の意味

販売許可を独立した全画面メニューとして決め打ちしない。

最低限、以下の状態を分離できる構造にする:

```text
StorePlanningState
- selected_store_size
- permit_eligibility { alcohol, tobacco, medicine }
- permit_owned { alcohol, tobacco, medicine }
- cash
- next: interior_layout
```

ただしPS版で同一UI配置かは未確認。

---

## 3. SS版では「改築→申請→内装キャンセル」で申請料を回避できるとの実機報告

2008年投稿者は「一応サターン版で出来た」と明記している。

手順上は、改築画面で許可申請を行ったあと内装画面へ進み、何もせずキャンセルして前画面へ戻ると、許可欄が `申請済み` になるとされる。

投稿者の結論は、酒・タバコ・薬の許可を無料で取得できるというもの。

証拠レベル: PROVISIONAL-HIGH-VALUE / SS-SPECIFIC-BUG

これは正常仕様ではなく、**SS版の状態遷移/課金コミット順に起因するバグ候補**として扱う。

---

## 4. PS版では同じ裏技が成立しないという追試報告

同ページの2011年ユーザーコメントに:

- `PS版では無理でした`

という追試結果がある。

証拠レベル: PROVISIONAL / PS-NEGATIVE-REPLICATION

単一コメントなので絶対確定ではないが、少なくとも:

```text
SS: exploit reported working
PS: same exploit reported not working
```

というプラットフォーム差が存在する可能性が高い。

### Baseline方針

Remakeの共通baselineでは、この無償取得バグを**通常仕様として採用しない**。

忠実再現モードでプラットフォーム差を再現する場合のみ:
- `platform_profile = PS`
- `platform_profile = SS`

のように差異を切り替えられる余地を残す。

PS baselineへSS固有挙動を混ぜない。

---

## 5. 販売許可の立地判定は既存コンビニの存在に依存

初代専用FAQでは、ゲーム開始時に建物の多い場所で酒・タバコ等を置けないケースについて、近くのライバル店が原因と説明される。

さらに「敵味方関係なく」既にコンビニが近くにある場合は許可が下りづらくなり、撤退させる、または買収後に売却することで置けるようになるとされる。

証拠レベル: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC

したがって判定は単純な土地属性だけではなく、少なくとも周辺店舗状態を参照する。

安全な暫定モデル:

```text
PermitEligibility
- parcel/base eligibility
- nearby convenience stores
- permit type
- UNKNOWN additional factors
```

未確定:
- 判定半径
- 自店/他店の距離重み
- 3許可で別々の距離か
- 申請料
- 一度取得した許可が改築/周辺発展で失効するか

---

## 6. 新規確定/未確定整理

### 今回追加できるもの

- SS版で酒・タバコ・薬3種の許可申請を改築フローから操作する実機報告あり。
- SS版では申請後の内装キャンセルにより申請料を回避できるバグ報告あり。
- 同手順はPS版では成立しなかったという追試報告あり。
- よってPS/SS間に販売許可状態遷移の差異がある可能性を正式に追跡対象とする。

### 依然未確定

- PS/SSそれぞれの正規の申請料
- PS版の正確な許可申請UI階層
- SS版の正確な許可申請UI階層
- 各許可の立地判定半径
- 申請料の引落しタイミング
- SS裏技が全SSリビジョンで再現するか

---

## 7. 実装開始時のガードレール

販売許可は以下をデータとして分離する:

```text
PermitDefinition
- id: alcohol | tobacco | medicine
- fee: UNKNOWN
- eligibility_rule: UNKNOWN

StorePermitState
- eligible
- owned
- applied

PlatformQuirkProfile
- ps
- ss
```

現段階では申請料や距離を仮値で埋めない。

SS無償取得は `PlatformQuirkProfile.ss` の検証済みバグ候補としてのみ保持し、共通経営ロジックには入れない。
