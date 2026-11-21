# 共通人物特性の参照先監査

基点: `8dadb65e92a507f95f6474f3deb42679fd6b843a`。修正: `238b965e250fb5d42b317b4c97ef4232a8c6ba5b`。

| 使用箇所 | 監査結果 |
| --- | --- |
| native店員の障害物回避 | 初期表参照を現役人物の特性へ修正 |
| 旧処理の体力回復 | 初期表参照を現役人物の特性へ修正 |
| native休憩回復 | 元から原回復規則を使用。機敏さ依存の新規則は追加しない |
| 接客/補充/清掃の成長上限 | 元から `_candidate_figures()` を使用 |
| 店長の学歴による成長抽選 | 元から `_candidate_figures()` を使用 |
| 人事/履歴書の数値 | native PS画面と採用候補は現行特性を使用 |
| 店員画像 | 性別/役職の固定属性。能力値の更新対象ではない |
| 初期採用/読込/ライバル配属 | 初期化後の実行値/共通特性再接続は既存処理。今回の移動修正でも同じ共通表を参照 |

出典: 本体 `program_people.gd`, `vertical_slice_simulation.gd`, `ps1_ui.gd`, `phone_ui.gd`, `store_view.gd` と既存復元モデル `staff_loop_selected.py`。原EXEの新しい実行証拠は追加していない。旧回復経路は原作一致の新規主張をせず、既存暫定ルールの参照先だけを揃える。

最初のCIではnative衝突/JSONと既存営業・接客・経路・人事・年初人物は実行できたが、新テストの旧経路にnative用乱数器が残り期待値と不一致、UIは `--android-preview` 未指定で起動できなかった。テスト側で旧経路用乱数器と正しい起動引数を設定し、シェルの否定grepも明示exitへ修正した。成功表示が出てもSCRIPT ERRORがあれば失敗とする。

検証入口: `game/scripts/live_staff_traits_smoke.gd` と `.github/workflows/native-staff-regression.yml`。GitHub ActionsでAPK作成時と同じGodot4.6.3を使う。実行結果はhandoffへ記録する。
