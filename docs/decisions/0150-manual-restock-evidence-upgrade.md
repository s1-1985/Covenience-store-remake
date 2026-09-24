# 0150: 手動補充の証拠をCONFIRMED_COMMUNITYからCONFIRMED_OFFICIALへ格上げ(タスク#80)

## 背景

タスク#79(PR #255)で、手動補充UIを「対象棚を選択→在庫が閾値以下でのみ
補充コマンドが有効化される」文脈依存型に作り直した。この時点での根拠は、
プロジェクトオーナー本人の直接プレイ証言(CLAUDE.mdのevidence tier(1)、
CONFIRMED_COMMUNITY相当)のみで、攻略本・wiki等の既存資料には独立の
裏付けが無いと記録していた。

タスク#79のマージ直後、ユーザーが「操作フローの改善を継続」を選択したため、
同じ路線で他の操作フローの整合性を確認する過程で、
`docs/research/strategy-guide-third-companion-book-full-extraction-
2026-09-24.md`(タスク#65で既にリポジトリに追加されていた、公式攻略本PDF
1-4・全115ページの全文書き起こし)を、この「手動補充」の論点で初めて参照した。

この文書のPDF1 p.68-71「販売管理の質問」Q&Aセクションに、以下の記述が
見つかった:

> Q: 棚やワゴンが空になる、万引きか? → NOT shoplifting -- just normal
> sell-through outpacing low-補充 staff; player CAN manually restock via
> cursor+select but this stunts staff 補充 growth (see Notable findings).

これは公式攻略本(CONFIRMED_OFFICIAL)による、プロジェクトオーナー証言とは
独立の裏付けである。

## 決定

### `manual_restock_action`をCONFIRMED_OFFICIALへ格上げ

`docs/research/inventory-restock-boundary-2026-09-05.md`セクション9に
「追記2」を追加し、上記の攻略本Q&A原文とその出典(PDF1 p.68-71)を記録した。
これにより`manual_restock_action`は、タスク#79時点の「オーナー証言のみ
(CONFIRMED_COMMUNITY)」から「公式攻略本による独立裏付けあり
(CONFIRMED_OFFICIAL)」へ格上げされる。

### 新しく判明したニュアンス: 手動補充は店員の`補充`スキルを成長させない

この攻略本の記述には、既存資料には無かった追加情報も含まれていた:
プレイヤーによる手動補充は、店員が自律的に行う補充タスクと異なり、
店員の`補充`スキルの成長に寄与しない("stunts staff 補充 growth")。

`game/scripts/vertical_slice_simulation.gd`を確認したところ、
**この点についてはコード変更が一切不要だった**:

- `_complete_restock()`(店員の自律補充タスク、決定書0089)は
  `_staff_growth.apply_replenish_growth(staff_member)`を呼び、`補充`
  スキルを成長させる。
- `apply_explicit_restock()`(プレイヤーの手動補充、タスク#38)は、
  この攻略本記述が見つかる前から`_staff_growth`を一切呼んでいなかった
  (`reference_sim/tests/test_game_vertical_slice_contract.py`の
  `test_explicit_restock_records_stock_expense_and_event_without_formula`
  が既存の`assertNotIn("_staff_growth", explicit_restock_body)`アサーション
  でこれを検証済みだった)。

つまり、この非対称性は今回確認された公式ルールと既に一致していた。この
一致が意図的な設計だったのか、あるいは「補充コストの計算式だけをapply_
explicit_restockに実装し、成長ロジックまで律儀にコピーしなかった」という
単なる実装上の割り切りの結果だったのかは、既存のコミット履歴・決定書には
記録が残っていない。このタスクでは、`apply_explicit_restock()`に
CONFIRMED_OFFICIALタグ付きのコードコメントを追加し、この一致を明示的に
ドキュメント化した(今後の変更でこの非対称性が誤って「揃える」方向に
リファクタリングされないようにするための記録)。

### 補充コスト計算式もCONFIRMED_OFFICIALとして再確認

同じ攻略本(PDF3 p.2)に「補充費: いわゆる仕入れ価格。仕入単価×数量で
設置時にかかる費用。その後は1補充するたびに仕入単価と差し引かれる。」との
記述があり、`補充費 = 仕入単価 × 数量`という式がCONFIRMED_OFFICIALで
明記されていることを確認した。これは`game/data/vertical_slice.json`の
`restock_unit_cost_yen`フィールドと`apply_explicit_restock()`/
`_complete_restock()`の`quantity * product.restock_unit_cost_yen`という
既存実装と完全に一致しており、コード変更は不要。

### `main.gd`のコードコメント更新

`_selected_fixture_restock_target()`のコメントを、タスク#79の
「CONFIRMED_COMMUNITY(オーナー証言のみ)」から、今回の攻略本裏付けを
引用した「CONFIRMED_OFFICIAL」表記に更新した。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  - 既存の`test_manual_restock_is_contextual_to_the_selected_low_stock_
    fixture`内の、`main.gd`コードコメントの評価タグを検証するアサーションを
    `CONFIRMED_COMMUNITY`→`CONFIRMED_OFFICIAL`に更新。
  - 新規`test_manual_restock_evidence_is_upgraded_by_the_strategy_guide_qa`
    を追加。研究ノートへの「追記2」の存在、攻略本原文の引用、`main.gd`の
    コメントが更新後のタグと出典ファイル名を含むこと、
    `vertical_slice_simulation.gd`の`apply_explicit_restock()`が依然として
    `_staff_growth`を呼ばないこと(=挙動は変更されていないこと)とその
    新しいコメントの内容、`_complete_restock()`側は引き続き
    `apply_replenish_growth`を呼ぶこと、をフィールド単位で検証。
  - フルスイート745件(xfail 1件)全てPASS。

## 実装ファイル

- `docs/research/inventory-restock-boundary-2026-09-05.md`
- `game/scripts/main.gd`(コメントのみ、ロジック変更無し)
- `game/scripts/vertical_slice_simulation.gd`(コメントのみ、ロジック変更無し)
- `reference_sim/tests/test_game_vertical_slice_contract.py`

## 明示的に対象外とした限界

- 攻略本記述にも、補充コマンドが出現する正確な在庫閾値や、プレイヤー補充
  1回あたりの発注数量(ロットサイズ)は明記されていない。これらは引き続き
  PROVISIONAL/REMAKE_BALANCED_DEFAULTのまま。
- この攻略本抽出文書(`strategy-guide-third-companion-book-full-extraction-
  2026-09-24.md`)自体の冒頭注記が明示する通り、今回参照したQ&Aセクションは
  「まだ高解像度での独立再検証を経ていない一次書き起こし」であり、
  文書内の一部項目(天候表・寄付イベント額・新店舗土地代式)のみが既に
  高解像度で再検証済みとされている。このQ&A記述自体はまだその再検証対象に
  含まれていないため、将来的な高解像度再クロップで文言の細部(特に
  日本語原文からの意訳部分)が修正される可能性は残る。
- この攻略本抽出文書には、この決定書のスコープを大きく超える大量の
  未実装CONFIRMED_OFFICIALデータ(広告5種の正確なコスト/効果表、店舗評価の
  増減閾値表、季節商品タグ、建物別客数表など)が含まれていることを確認した。
  これらは別タスクとしてスコープ外とし、ユーザーに次の方向性として提示する。
