# 初代PS/SS 店員雇用UIの表示項目 追加調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 店員雇用画面と配属後/異動画面で表示される能力を混同しない。
- Android版の人事UIで必要な列を初代専用資料から確定する。

主要ソース:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY-FIRST-TITLE

---

## 1. `店員の雇用` で表示される主要パラメーター

初代専用店員資料で明示される雇用時項目:

```text
給料
体力
学歴
敏捷性
社交性
```

名前・年齢等の人物情報も固有人材データとして存在するが、今回の資料が明示的に「雇用時パラメーター」として説明している能力列は上記5項目。

### データモデル

```text
StaffHiringProfile
- wage
- stamina
- education_background   # 学歴
- agility                # 敏捷性
- sociability            # 社交性
```

---

## 2. 雇用画面の値は「現在の作業能力」と同一ではない

初代専用資料は、`店員の雇用` と `店員の異動` で表示される能力を明確に分けている。

異動時/配属後に見る実務能力:

```text
レジ
補充
警備
清掃
接客
```

これらの初期値は雇用画面の数値とは別設定。

したがって雇用時に高能力に見える人物でも、実際の初期レジ等が低い場合がある。

### baseline必須

```text
StaffIdentity
  hiring_profile:
    wage
    stamina
    academic
    agility
    sociability

  work_skills:
    register
    restock
    security
    cleaning
    service
```

を別オブジェクト/別フィールド群として保持する。

一枚の5能力を名前だけ変えて流用する実装は禁止。

---

## 3. 雇用値と実務能力上限の関係

初代専用資料による関係:

- 学歴 ≒ 教育
- 教育は `レジ` と `警備` の上限に関係
- 敏捷性は `補充` の上限
- 社交性は `接客` と `清掃` の上限
- 給料と体力は雇用時の値が配属後にもそのまま反映される

ただし例外人物が存在し、厳密な等式ではない。

安全なモデル:

```text
skill_caps = deriveCaps(identity)
# academic/agility/sociability are strong inputs,
# but individual overrides must be representable.
```

人物別overrideを持てるようにする。

---

## 4. 給料表示は営業時間で変わる

初代資料:
- 雇用画面に表示される給料は24時間営業時の1日給料
- 24時間以外の営業時間にした後、`店員の異動` で見ると給料が安くなる

したがって:

```text
wage_display_at_hire = full_day_wage
actual_daily_wage = function(full_day_wage, business_hours)
```

のように基準給と実効日給を分ける必要がある。

正確な比例式は未確定。

---

## 5. 人事画面の正式階層はまだ完全未確定

現在、初代専用資料から用語として:
- `店員の雇用`
- `店員の異動`
- 解雇操作

が存在することは強く確認できる。

ただしトップレベルメニューが正式に:

```text
人事 -> 雇用 / 異動 / 解雇
```

という一つのサブメニューであるか、別導線かはPS説明書/実画面で最終確認が必要。

**『ザ・コンビニ2』の人事メニュー構造をそのまま初代へコピーしない。**

---

## 6. UI実装時の安全な暫定形

正式階層が取れるまで、内部状態は:

```text
StaffManagementState
- HIRE
- TRANSFER_OR_ASSIGN
- DISMISS
- STAFF_DETAIL
```

を持ち、Android側の表示ラベル/ナビゲーションは後から差し替え可能にする。

雇用候補カードには最低限:

```text
name
age?               # visual confirmation pending for exact screen placement
wage
stamina
academic
agility
sociability
```

を表示できる設計にする。

年齢の雇用画面上の正確な表示位置/有無は実画面確認待ちなので `age?` とする。

---

## 7. 次の確認対象

- PS/SSの店員雇用画面スクリーンショット
- 一画面に何人候補が表示されるか
- 顔グラフィックの位置
- 年齢/性別の表示有無
- 決定/戻る/候補切替の操作
- `店員の異動` 画面の完全列
- 店長指定方法
- 解雇確認ダイアログ
