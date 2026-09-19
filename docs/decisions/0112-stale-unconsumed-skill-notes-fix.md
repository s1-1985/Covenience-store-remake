# 0112: `service_skill`/`security_skill`/`cleaning_skill`「未消費」記述の是正(タスク#43)

## 背景

タスク#42(是正)完了後、「配線待ちの確認済みロジックが他に残っていないか」
を再調査した際、`vertical_slice.json`の`staff.skill_evidence_note`が
「service_skill/security_skill/cleaning_skillはデータとして存在するが、
いかなるGDScriptロジックにも消費されていない」と主張しているのを発見した。

実際にコードを確認したところ、この主張は**タスク#27の時点で既に誤りに
なっていた**: `VerticalSliceSimulation._evaluate_store_rating()`が毎月
全スタッフの3スキル値を収集し、`store_value.gd`の
`compute_service_value`/`compute_security_value`/`compute_cleaning_value`
へ渡し、月次スターレーティング(`store_rating.gd`)に反映している
(`headless_smoke.gd`にも既存の単体テストあり)。`demand_policy.gd`の
コメントにも同様の古い主張(「このクライアントにはservice/cleaning/
security/assortmentの遊戯統計値がまだ存在しない」)が残っていた。

`CLAUDE.md`が明文化した「確認済みデータの正確性」の原則に照らし、
根拠(evidence_note・コード内コメント)が実態と食い違ったまま放置される
のは、たとえ挙動に影響しなくても是正すべき事実誤りと判断した。

## 決定

### 3箇所のテキストのみを是正(ロジック変更なし)

- `vertical_slice.json`の`staff.skill_evidence_note`: 「未消費」という
  誤った記述を、実際の消費経路(`_evaluate_store_rating()` →
  `store_value.gd`の3関数 → 月次スターレーティング)への言及に置き換えた。
- `game/scripts/domain/demand_policy.gd`の冒頭コメント: 「service/
  cleaning/security統計値がまだ存在しない」という古い前提を、「タスク#27
  以降統計値自体は存在するが、`demand_policy.gd`の客数発生式(`compute_
  customer_share_percent()`)には配線されておらず、assortment(品揃え)
  統計値は依然として存在しない」という正確な記述に更新した。この
  コメントが本来伝えたい結論(「希釈対象となる0-100スコアがこのクライアント
  にはまだ存在しない」)自体は変わらず正しいため、その部分は維持した。
- `reference_sim/tests/test_game_vertical_slice_contract.py`の対応する
  コメントも同様に更新した(アサーション自体に変更なし、コメントのみ)。

これは純粋なドキュメント/evidence_note是正であり、シミュレーションロジック
・テストのアサーション内容は一切変更していない。

## テスト

- `reference_sim/tests`フルスイート: 657件+xfail1件、全てPASS(挙動変化
  なしを確認)。
- `headless_smoke.gd`: Godot 4.3公式バイナリで実行し、734ステップ変化なく
  PASS。

## 実装ファイル

- `game/data/vertical_slice.json`: `staff.skill_evidence_note`を是正。
- `game/scripts/domain/demand_policy.gd`: 冒頭コメントを是正。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 対応する
  コメントを是正。
