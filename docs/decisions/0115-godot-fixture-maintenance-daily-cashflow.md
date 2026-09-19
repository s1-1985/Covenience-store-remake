# 0115: 什器の`maintenance_yen_per_day`を日次収支へ配線(タスク#46)

## 背景

タスク#45(什器capacity/互換性配線)完了後、ユーザーから「システム面を
先に全て作って、最後に画像・音声生成とその紐付けを行う」という開発順序の
方針が示され、続けて「什器のmaintenance_yen_per_day→日次収支」を選択した。

`fixture_catalog`の全35エントリ(shelf種29、amenity種3、parking種3)は
CONFIRMED_OFFICIALな`maintenance_yen_per_day`(1日あたりの維持費)を
持っているが、タスク#32以降この値は一切消費されておらず、evidence_note
にも「未消費」と明記されたまま据え置かれていた。什器を何個買っても
維持費が一切発生しない状態だった。

## 決定

### `VerticalSliceSimulation._apply_daily_fixture_maintenance()`(新規)

`_handle_day_boundary()`から毎シミュレーション日呼び出す新関数を追加。
現在店舗に配置されている全什器(`layout.fixtures`)を走査し、各什器の
`catalog_id`が`fixture_catalog`由来であればその`maintenance_yen_per_day`
を合計し、1日1回`economy.record_explicit_expense("fixture_maintenance",
...)`として一括控除する。

`catalog_id`を持たない什器(什器カタログ制度導入前からのプロトタイプ
什器`shelf-1`/`shelf-2`、およびカタログに存在しない`checkout-1`)は
参照できる確認済みデータがないため対象外とした(タスク#45の互換性
チェックと同じ据え置き方針)。合計維持費が0円の日(まだ何もカタログ
購入していない、または全て駐車場のようにmaintenance=0の什器のみを
所有している場合)は、無意味な0円の支出記録を毎日残さないよう、
イベント自体を記録しない。

### 「1日」の解釈と月次スケーリングとの整合

`REPRESENTATIVE_DAYS_PER_MONTH=4`/`MONTH_MULTIPLIER=8`(攻略本確認済み
「1月=4日間×8」)という既存の月次投影の仕組みは、4シミュレーション日
分の`economy.cash_yen`の実際の差分を8倍して月次結果として表示する
だけであり、内訳を個別に再計算しない。日次維持費はこの4日間の現金
差分の一部として自然に含まれるため、月次側に特別なスケーリング処理を
追加する必要はなかった(既存アーキテクチャに追加のコード変更なしで
整合する)。

### 対象外とした関連項目: スタッフの給与

調査の過程で、`salary_yen_per_day_24h`(35名のCONFIRMED_OFFICIALな
候補者データの一部)も同様に一切消費されていないことが判明した。ただし
これは`staff_candidates`(採用候補プール)側にのみ存在し、実際に稼働中
の`staff.members`(staff-1/staff-2)エントリ自体には給与フィールドが
存在しない——`candidate_id`経由で`staff_candidates`を逆引きすれば給与額
自体は導出可能だが、今回のタスクはユーザーが選択した「什器の
maintenance_yen_per_day」に限定し、スタッフ給与は範囲外とした。将来の
別タスクとして残す。

## テスト

- `headless_smoke.gd`: 新規シナリオを追加。(1)何もカタログ購入していない
  状態で1日経過しても`fixture_maintenance_charged`イベントが記録され
  ないことを確認。(2)`bench`(maintenance_yen_per_day=160)を購入し、
  1日境界を跨いだ時点で現金が正確にその金額だけ減少し、
  `fixture_maintenance_charged`イベントが1件記録されることを確認。
  Godot 4.3公式バイナリで764ステップでPASS(新規シナリオ追加分、
  既存734ステップから増加)。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_fixture_maintenance_is_charged_daily`を追加。全`fixture_catalog`
  エントリの`maintenance_yen_per_day`が`reference_sim`の`FIXTURES`と
  一致すること、実際の日境界処理に配線されていること、evidence_noteに
  「未消費」という古い主張が一切残っていないこと(タスク#43で是正した
  のと同種の陳腐化チェック)を検証。フルスイート660件(新規テスト含む、
  xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`:
  `_apply_daily_fixture_maintenance()`を新規追加し、`_handle_day_
  boundary()`から呼び出す。
- `game/data/vertical_slice.json`: 全`fixture_catalog`エントリの
  `evidence_note`から「未消費」の記述を除去し、実際の消費経路を記載する
  形に更新(amenity 3件・shelf 27件・parking代表のparking_ground 1件)。
- `game/scripts/headless_smoke.gd`: 新規テストシナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- スタッフ給与(`salary_yen_per_day_24h`)は上記の通り今回の対象外。
- `shelf-1`/`shelf-2`/`checkout-1`(カタログ制度導入前のプロトタイプ
  什器)は引き続き維持費の対象外(確認済みデータがないため)。
- 什器以外の固定費(店舗そのものの家賃・地代等)は依然としてこの
  クライアントに実装されていない。`land_value_policy.gd`(タスク#28)は
  地価の情報表示のみで、地代の支払いという別メカニクスは今回も対象外。
