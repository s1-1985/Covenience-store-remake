# 0252 — 中断理由の独立管理と復帰時の誤操作防止

2026-11-26、PLAY-0252。ユーザーの「進めて」と「都度ビルドしなくていい」に基づく。基点1257d3b299c0c1e536c3720b6f1e51442a03ae2e、branch chatgpt/mobile-resume-20261126。main6282489、作業ライン1257d3、開PRなしを確認し、最新の採用済み作業ラインから分岐した。PR #286 https://github.com/s1-1985/Covenience-store-remake/pull/286。

## 再現・変更

変更前にPAUSED→FOCUS_INを与えると_app_suspended=falseになり、停止中に再開扱いとなる。mobile_resume_smokeでexit1「FOCUS_IN resumed an application that is still PAUSED」を再現。

PAUSED/RESUMEDとFOCUS_OUT/INを独立した2理由として管理し、両方が解除されたときだけ_app_suspendedを解除。通知のたびに壁時計基点をリセットして中断時間を営業へ加算しない。既存の残余accumulatorとユーザー自身のpaused/speedは維持。

停止/フォーカス喪失時には未完の指操作を取り消す。PSメニューの押下待ち/人事ドラッグ/暦演出押下、レールボタン、店内カメラ、什器移動プレビュー、町のピンチ/押下を解除する。メニューの入力内容・選択・配置結果・カメラの縮尺/位置を消す処理ではない。町の古いreleaseは建物選択にならないよう、既存の移動量判定を取消状態にする。

原シミュレーション・乱数・経営数値・原通知規則は変更せず、スマホ用の中断/入力アダプター内の修正とする。自動セーブや新しい原作仕様は追加しない。

## 検証

Godot4.6.3: mobile_resume / store_camera_persistence / mobile_controls / ps1_menu_dispatch / ps1_ui / ps1_touch_audit / menu_usability / renovation_ui / personnel_decision / calendar_ui、10本成功。

新回帰は通知順の交錯、停止中のclock/debt不変、完全復帰時の時計再初期化、古いレール押下/メニューコールバック/什器移動/町選択の非実行、カメラ指解除と縮尺/位置保持、新しいタップが動くこと、手動停止の保持を確認。ライフサイクル通知をコードから再現した自動確認であり、Android OS/実機での確認ではない。

Python804件成功（外部プラグイン非推奨警告1件）。全体headless1205step成功、SCRIPT ERROR/ERROR0件。

## ファイル・収録状態

main.gd、ps1_ui.gd、store_camera.gd、store_view.gd、touch_controls.gd、town_view.gd、新mobile_resume_smoke.gd、CI、本文、RELEASE_ACCEPTANCE、handoff/status、PROJECT_MEMORY追記。

ユーザー指示どおりAPKビルド/版数更新は実施しない。配布済み0.8.14/code94は本変更を含まない。Android実機の通し操作・中断/復帰と長時間負荷、PS版との最終画面/挙動照合、既存未解決6件（U-1〜U-6）は未完のまま。
