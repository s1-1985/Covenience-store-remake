# 0199: 評価(★)と人気を原作プログラムの動きに(タスク#129)

## 背景

ユーザーの依頼(2026-09-26):

> 推測で作っていたアルゴリズムや、未実装のアルゴリズム等、今回得られた情報から実装して

これまでの状態:

- 評価:攻略本の表で月末に増減。0〜100に収めていた。新しい店は0点(REMAKE_BALANCED_DEFAULT)。
- 人気:タスク#124(0195)の「知名度」モデル。すべてこの作品の創作だった(REMAKE_BALANCED_DEFAULT)。
  - 満足した客で知名度が上がり、知名度で来客数が0.4〜1.6倍になり、人気が知名度に引き寄せられる。
- 店長の助言(文言251〜258):未実装。
- 宣伝:手持ちが足りなくても実施していた(手持ちが負になることもあった)。

## 根拠

CONFIRMED_BINARY(PS版の実行ファイル SLPS_007.82 の命令から読んだもの)。詳しくは
`docs/research/ps1-executable-formulas-2026-09-26.md` の「月ごとの評価」「人気」と、その追記。

- 評価の表は、攻略本の表とプログラムで1マスずつ一致した。変えていない。
- 評価の点は、月の判定のあと5〜100に収める(0x80028A50)。
- 新しい店は評価10・人気20(0x8001B120/0x8001B12C)。
- お客に怒られたときの −1 は、評価が6以上のときだけ(0x8003600C)。
- 毎日0時に、★の数で人気が −15/−10/−5/−3/0/+5 動く。評価の点を下回らない。上限100(0x80028E60)。
- 月の判定で「良い」が3つ未満なら、店長の値の確率で助言。5項目から乱数で1つ選び、それが「良い」でなかったときだけ出る(0x80028800)。文は実行ファイル内の文字列そのまま。
- 宣伝は、実施のときに手持ちが費用の5倍以上なければ中止。費用はかからない(0x80027888、文言204)。

## 決定

- `StoreRating`(`game/scripts/domain/store_rating.gd`):
  - `RATING_FLOOR`(5)・`NEW_STORE_RATING`(10)・`DAILY_POPULARITY_CHANGE_BY_STARS` を足した。
  - 月の判定の結果に、良くなかった項目(`not_good_items`)を入れる。
  - `next_day_popularity()`・`manager_advice()` を足した。
- `VerticalSliceSimulation`:
  - タスク#124の知名度モデルを外した(`recognition`、`_start_store_growth`、`_apply_recognition`、`_note_visit_outcome`、`popularity_target`、`_grow_store_day`、`store_rules.store_growth`、`DemandPolicy.recognition_factor`)。
  - 新しい店(買収した店も)は評価10・人気20で始まる(`_start_new_store_standing`)。
  - 日の区切りで、月の判定のあとに人気を動かす(`_drift_popularity_day`)。顧客独占率はそのとき計算し直す(毎日計算し直すことは CONFIRMED_COMMUNITY)。
  - ★が変わったら `store_rank_changed`、助言は `manager_advice`、宣伝の中止は `promotion_cancelled` を記録する。画面には原作の文で出す(`phone_ui.gd`)。
- reference_sim の `store_rating.py` にも下限5を入れた。

### この作品の決めごと(REMAKE_BALANCED_DEFAULT)

- 助言の確率は、店長の「社交性」÷100 とした。
  - プログラムは店長の店員データ +0x15 の値を使う。この値は雑誌の4つの出来事すべてで上がる。
  - それが攻略本の店員カードのどの能力に当たるかは、確かめられなかった。社交性は「人に話す力」に近いと考えて選んだ(推測)。
- 買収した店は、新しい店と同じ評価10・人気20で始める。ライバル店の評価と人気は、この作品では持っていないため。
- 3か所の記載:コード(`vertical_slice_simulation.gd`)、`store_rules.evidence_note`、テスト(`_check_store_standing` と `test_store_standing_editing_and_renovation_are_tagged`)。

## 影響

- 知名度モデルがなくなったので、来客数の「0.4〜1.6倍」がなくなり、以前の来客数(1.0倍)に戻る。
  - 原作の「新しい店に客が少ない」仕組みは、人気が店選びの候補に入る確率を決めること(人気+20%)。これはタスク#130で入れる。
- 人気は、★0のあいだは毎日15ずつ下がり、評価の点(新しい店は10)で止まる。宣伝の効果は翌日から薄れる(攻略本 p.36 の「翌日になると上がった人気度はドンドン下がってしまう」と合う)。

## テスト

- `headless_smoke.gd` の `_check_store_standing`:
  - 人気の日ごとの増減(★0で −15、★2で −5、評価の点まで引き上げ、上限100)。
  - 評価の下限5、良くなかった項目が5つとも記録されること。
  - 店長の能力0なら助言なし、100なら原作の文の助言が出ること。
  - 新しい店が評価10・人気20で始まり、1日後に人気10になること。セーブ・ロードで残ること。
  - 手持ちが費用の5倍未満なら宣伝が中止され、お金も人気も変わらないこと。5倍なら実施されること。
  - 買収した店が評価10・人気20で始まること。
- 既存のテストのうち、人気0・評価0で始まることを前提にしていたものを直した。
- pytest:`test_store_rating.py`(下限5)、`test_game_vertical_slice_contract.py`(タグと定数、知名度が残っていないこと)。

## 変更したファイル

- `game/scripts/domain/store_rating.gd`、`demand_policy.gd`、`guide_starting_store.gd`
- `game/scripts/vertical_slice_simulation.gd`、`phone_ui.gd`、`headless_smoke.gd`
- `game/locale/ja.po`、`game/fonts/ConveniJP.ttf`(新しい文言の字)
- `tools/build_guide_p48_store.py`、`game/data/vertical_slice.json`
- `reference_sim/conveni_sim/store_rating.py`、`reference_sim/tests/test_store_rating.py`、`reference_sim/tests/test_game_vertical_slice_contract.py`
- `docs/research/ps1-executable-formulas-2026-09-26.md`(追記)

## この作業でしないこと

- 客の来店と店の選び方(タスク#130)。
- 雑誌の出来事、コンテスト、寄付(タスク#131以降)。
- ライバル店の宣伝(プログラムでは「乱数%4 ≦ ライバルの積極性」かつ資金が費用の10倍以上)。
