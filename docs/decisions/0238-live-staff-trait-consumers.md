# 0238 — 更新後の人物特性を移動へ反映

## 背景
0.8.8は雑誌受賞・年初強化後の基本特性を共通人物表へ保存するが、native歩行の回避判定だけが初期候補表の機敏さを読み続けていた。旧体力回復経路にも同じ参照漏れがあった。

## 決定
既存の `_candidate_figures()` を両参照へ使用する。回避の抽選回数・経路順・原作の勤務/回復規則は変更しない。native休憩の回復量は従来通り `ProgramRules.resting_energy()` を使い、旧経路の敏捷性依存回復は既存の暫定規則のままである。

## 根拠
既存解析ブランチ `chatgpt/source-reference-archive-20261106` の `ps1-analysis-checkpoints/analysis/20261103-operating-continuation/source-reference/staff_loop_selected.py` は `walking_step(..., sb(staff,0x1b), seed)` と現役人物の機敏さを渡す。年初強化の証拠は `docs/research/annual-personnel-2026-11-21/`、共通特性の実装はdecision0234/0237を参照。今回は原EXEの追加実行は行っていない。

## 確認
更新前なら失敗し更新後なら回避できる同じ乱数条件、初期表の不変、JSON往復、旧回復経路を固定シナリオで確認する。既存の人物営業/接客応答/経路/人事保持/年初人物/UI/町受賞もまとめて確認。結果は最新handoffを参照。

## 範囲外
全営業RNG・行列幾何の完全一致、同時接客全条件、全入力/演出、原カード形式。今回APKは作成せず、配布済み0.8.8とは区別する。実機確認は行っていない。
