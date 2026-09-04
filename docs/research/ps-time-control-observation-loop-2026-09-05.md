# 初代PS版 時間速度・観察ループ・一時停止境界 追加調査 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』をbaselineとする。

目的:
- 初代PS版にプレイヤー任意の早送り/速度変更があるかを確定する。
- 「速度変更できない」と「一時停止できない」を混同しない。
- 後続作『ザ・コンビニ2』で追加された高速モードを初代へ逆輸入しない。
- 原作の「店を眺める時間」がゲーム体験上どの程度重要かを実装要求へ落とす。

---

## 1. 電撃PlayStationが初代PS版について「経過時間を操作できない」と明記

2013年の電撃PlayStation記事は、1997年3月28日に初代PSで発売されたシリーズ1作目について:

- ゲーム中での経過時間を操作できない
- 店の基盤が整うと、あとは見ているだけでゲームが進行する
- TVや読書をしながらの「ながらプレイ」が成立する
- 放置し過ぎると火災等に気づかず経営危機になる

と説明している。

Source:
- https://dengekionline.com/elem/000/000/722/722919/

証拠レベル: STRONG-SECONDARY / PS-SPECIFIC / PROFESSIONAL-GAME-MEDIA

### 確定できること

初代PS baselineでは、少なくとも通常プレイ中に:

```text
simulation_speed = player cannot freely choose x2/x4/etc.
fast_forward_control = absent
```

とみなしてよい。

「ハードが遅い」という話ではなく、プレイヤー側の時間速度操作機能がないというゲーム仕様上の指摘である。

---

## 2. PS実プレイ記録も「早送り機能があれば」と明示

初代PS版の詳細プレイ記録では:

- 店舗建設/内装が終わり資金がなくなると、年月・町発展・資金蓄積を待つ時間が長い
- `早送り機能でもついていれば` と明確に不満を述べる
- 実際にゲーム機の電源を入れたまま他のことをして待つ
- その間に火災を見逃し、数ヶ月赤字になった例がある

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DETAILED-PLAYLOG

### 電撃記事との一致

独立した2系統の資料がともに:

```text
初代PS = 速度操作/早送りなし
        + 放置/観察しながら時間を進める
```

と描写している。

そのためこれはかなり強いbaseline仕様として扱う。

---

## 3. 『ザ・コンビニ2』では高速モードが存在する — これは続編差分

『ザ・コンビニ2』専用操作資料には:

- START: ゲーム内時間停止
- SELECT: 高速モード切替

が記載される。

Source:
- https://w.atwiki.jp/konbini2/pages/13.html

また現行Console Archives版『ザ・コンビニ2』の公式説明でも、高速モードが続編側の改善点として扱われる。

Source:
- https://www.consolearchives.com/title/csa-0029/

扱い: VERSION-COMPARISON ONLY

### 結論

```text
Konbini 1 PS:
  player speed multiplier -> absent

Konbini 2 PS:
  fast mode -> present
```

この差は、続編の操作表を初代へコピーしてはいけない明確な例である。

---

## 4. 「速度変更不可」≠「一時停止不可」

ここは重要なので別項目として管理する。

電撃記事の「経過時間を操作できない」は、文脈上:

- x2/x4などの早送り
- 任意の速度変更

がないことを強く示す。

しかし次はまだ確定していない:

- STARTボタンで完全停止できるか
- システムメニューを開くと停止するか
- 宣伝/営業方針/調査等のモーダル表示中に停止するか
- 内装編集時に停止するか
- セーブ/ロード画面で停止するか

### 現時点のbaselineデータ

```text
TimeControlSpec
- speed_multiplier_control: ABSENT_CONFIRMED
- explicit_pause_button: UNKNOWN
- pause_when_management_modal_open: UNKNOWN
- pause_when_interior_editing: UNKNOWN
- pause_during_save_load: UNKNOWN
```

説明書本文/PS実機動画で確認するまで、START=一時停止と推測しない。

---

## 5. PC版初代の「管理ウィンドウ中停止」情報はPS版証拠に使わない

後年のWin版比較記事では、Win版『ザ・コンビニ1』について:

- 宣伝
- 営業方針

等のウィンドウが開いている間はゲーム停止だった、と記録される。

Source:
- https://henamap.doorblog.jp/archives/82476899.html

しかしこれはWindows版の話であり、PS版baselineへ直接適用しない。

扱い: PC-VERSION-COMPARISON ONLY

PS/SSは操作体系・UI・時間処理に差がある可能性があるため、別証拠が必要。

---

## 6. 原作の「観察ループ」は偶然の待ち時間だけではない

電撃PlayStationは「ながらプレイ」を本作の魅力の一つとして評価している。

さらに既存研究では:

- 客が個別に歩く
- 店員が自律作業する
- レジ渋滞が起きる
- 客が怒る
- 補充/清掃が滞る
- 万引き/火災/強盗等が発生する
- レイアウトにより客導線と年間売上が変わる

ことが確認済み。

つまり時間が流れている間にプレイヤーがやることは「何もない」のではなく:

```text
WATCH
 -> NOTICE PROBLEM
 -> OPEN MANAGEMENT ACTION
 -> CHANGE LAYOUT / STAFF / PRICE / PROMOTION
 -> WATCH RESULT
```

という観察型フィードバックループである。

### Remakeでの重要性

高速化だけを優先して客/店員を視認できない速度にすると、原作の診断ゲーム性を失う。

最初のvertical sliceでも:

- 客の目的地
- 店員の作業状態
- レジ列
- 品切れ
- 汚れ
- 怒り/退店

を見て原因を推測できる表示を優先する。

---

## 7. Android版での方針 — 互換baselineとUX改善を分離する

原作互換ルールとしては:

```text
ORIGINAL_COMPAT_MODE
- simulation speed: 1x equivalent only
- no player fast-forward control
```

を基準にする。

ただしAndroid版で30分〜数時間ただ待つ体験をそのまま強制する必要はない。

エンジン内部は将来:

```text
SimulationClock
- logical_tick_rate
- render_rate
- speed_multiplier
```

を分離できるようにしておく。

その上で将来のオリジナル/快適版として:

```text
OPTIONAL_QOL_DEVIATION
- x2 / x4 etc.
```

を追加する余地を残す。

重要なのは、高速化を原作仕様として扱わず**deliberate deviation**として記録すること。

---

## 8. PSハード由来の処理落ちは再現しない

PS版レビュー/長期プレイでは:

- 店舗数増加で処理が重くなる
- 長期プレイで時間進行が体感遅くなる
- セーブ/ロードが長い

等の記録がある。

これらは原作ルールではなくハード/実装性能由来と考える。

したがって:

```text
Do NOT emulate:
- PS frame drops
- slow save/load
- simulation slowdown caused by hardware load
```

一方で、大量の顧客/店員が存在しても論理シミュレーション結果が変わらない性能設計は必要。

---

## 9. 時間モデルの既存確定事項との接続

既存研究で初代は:

- 月1〜4日をリアルタイム進行
- 5日〜月末を一気に集約
- 0時の日付境界で当日の顧客独占率/来店量に関わる評価
- 天候変化時にも顧客独占率再計算の観測

が強く確認済み。

したがって原作の時間感覚は:

```text
Month
  Day 1: watch live simulation
  Day 2: watch live simulation
  Day 3: watch live simulation
  Day 4: watch live simulation
  Day 5..month end: aggregate/skip
```

であり、プレイヤーはDay 1〜4そのものを高速化できない。

これは「1ヶ月を30日リアルタイムで待つ」ゲームではないことにも注意する。

---

## 10. 実装テスト項目

将来実装時に最低限テストする:

1. 1x論理時間で客/店員挙動を観察可能。
2. UI描画fpsとシミュレーションtickを分離。
3. アプリ負荷が上がっても論理的な時間進行を勝手に遅くしない。
4. 代表4日→月次集約をゲームロジックとして実装。
5. 将来speed multiplierを追加しても日付境界/イベント時刻/広告時刻が壊れない。
6. pause policyはPS証拠が得られるまで設定可能なポリシー層として分離。

候補:

```text
ClockPolicy
- ORIGINAL_PS_COMPAT
- MODERN_QOL
```

ただしMODERN_QOLは初期再現版完成後に検討する。

---

## 11. 未確定 / 次に調査すること

Priority A:

- PS初代のSTARTボタン機能
- SELECTボタン機能
- 通常店内画面での明示pause手段
- 町マップでのpause手段
- 内装編集中に時計が止まるか
- 販促/調査/営業方針ウィンドウ中に時計が止まるか
- 人事/雇用中に時計が止まるか
- セーブ/ロード中のゲーム時間状態

入手経路:

1. PS1説明書本文スキャン
2. 初代PS長尺プレイ動画
3. 1997年PS/SS攻略本の操作ページ
4. 現行Console Archives版の実機操作記録

『ザ・コンビニ2』のSTART/SELECT割当は、この穴を埋める根拠には使わない。
