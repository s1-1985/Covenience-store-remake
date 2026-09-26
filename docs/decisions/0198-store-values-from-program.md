# 0198: 店の値(サービス・警備・清掃)を原作プログラムの式に(タスク#128)

## 背景

ユーザーの依頼(2026-09-26):

> 推測で作っていたアルゴリズムや、未実装のアルゴリズム等、今回得られた情報から実装して

タスク#127で、PS版の実行ファイル(SLPS_007.82)から店の値の式を読んだ
(`docs/research/ps1-executable-formulas-2026-09-26.md`「店の値」)。
プロジェクトの式とは次の点が違っていた。

- 清掃・警備:攻略本は「社員の値の合計 × 1.5/1.65/1.8」と書いている。プログラムは掛けずに割っている。
- 3つの値とも、プログラムは100で打ち切る。
- サービスの平均は整数(端数切り捨て)。
- 交番・消防署:プログラムはマスを数える。種類ごとの上限はない。上限は2×2・3×2の建物の大きさから自然に出る。

## 根拠

CONFIRMED_BINARY(原作プログラムの命令から直接読んだもの)。

| 値 | 番地 | 式 |
|---|---|---|
| サービス | 0x800221D0 | 店員の接客の平均(整数) + 観葉植物2・ベンチ4・噴水30、最大100 |
| 警備 | 0x800224E0 | 店員の警備の合計 × 100 ÷ (250/275/300) + 交番のマス×10 + 消防署のマス×5、最大100 |
| 清掃 | 0x8002287C | 店員の清掃の合計 × 100 ÷ (150/165/180)、最大100 |

- 交番・消防署は、店の敷地から上下左右7マス以内のマスを数える(2×2の敷地なら16×16)。攻略本の「店舗周囲16×16エリア」「最大+40/+30」と合う。
- 証拠の水準 CONFIRMED_BINARY は、`PROJECT_MEMORY.md` 第15節に足す(タスク#129の記録と一緒に)。

## 決定

- `StoreValue`(`game/scripts/domain/store_value.gd`)と `reference_sim/conveni_sim/store_value.py` を、上の式に置き換えた。
  - `CLEANING_DIVISOR`・`SECURITY_DIVISOR`・`VALUE_CAP`・`SECURITY_PER_SQUARE`・`SECURITY_REACH_SQUARES` を定数にした。
- 交番・消防署の加点(`_security_facility_bonus`):
  - 町の建物のうち名前が「交番」「消防署」のものについて、敷地の周り7マスの範囲に入るマスを数える。
  - 誘致した施設も町の建物に入っているので、同じ数え方になる。
  - 購入して更地にした建物は数えない。
- 以前の `inducement_security_bonus()` は、この数を返すようにした。

この作業で、この作品が独自に決めた値(REMAKE_BALANCED_DEFAULT)は新しく増えていない。

## テスト

- `headless_smoke.gd`:
  - `StoreValue` の値を直接確かめる。サービス([10,30],[2,4]) = 26、上限100。警備([10,20],小) = 12、交番の加点40で52、上限100。清掃([5,15],大) = 11。
  - 月末の評価に渡る3つの値が、店員の値から上の式で出した値と一致する。
- pytest:`test_store_value.py`・`test_store_evaluation.py` を新しい式に合わせた。
- `test_game_vertical_slice_contract.py`:`store_value.gd` に CONFIRMED_BINARY・割る数・`VALUE_CAP` があること、シミュレーションが `_security_facility_bonus()` を渡していることを確かめる。

## 変更したファイル

- `game/scripts/domain/store_value.gd`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/conveni_sim/store_value.py`
- `reference_sim/tests/test_store_value.py`
- `reference_sim/tests/test_store_evaluation.py`
- `reference_sim/tests/test_game_vertical_slice_contract.py`

## この作業でしないこと

- 評価(★)と人気の式(タスク#129)。
- 客の来店と店の選び方(タスク#130)。
- 店の大きさの番号(店+0xC70)が「小・小・中・中・大・大」の順であることは推測。プロジェクトの size_tier と数値の組が合うことで裏づけている。
