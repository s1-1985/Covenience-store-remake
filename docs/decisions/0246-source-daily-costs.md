# 0246 — 既存解析の日次費用式をnativeへ接続

## 背景・根拠

ユーザー指示によるLEGACY-0246。Muse新規解析は採用せず、自分の既存資料と本体を照合。基点db9b596a1599f8e4b22fe6ac40c4f34c2ff2642b、main688876aおよびPR270/272/273/274/275のHEADを確認。ブランチchatgpt/legacy-daily-costs-20261121。PRは作成後追記。

既存のps1-analysis-checkpoints/analysis/20261103-operating-continuation/source-reference/operating_costs.py（保管commit a1f45981ffc1479e9a8e0b4ff429d4fc4cb85ea4、SHA256はsource_daily_costs.jsonに固定）を根拠とする。8001D8AC/D980/DB5C/DBE4/DD7Cと日次支払の既存読解であり、新たな原EXE/ディスク/CPU解析は行っていない。

同モデルは時給×130の途中をsigned32にしてから100で切捨て除算し、営業時間を乗じる。合計と現金差引もsigned32。什器はアンカーのkind<53だけ対象。現行本体は各算術を64bitで計算し、total>0だけ計上するため符号反転した負額を破棄し、kind53以上にも53行のrate配列を引こうとしていた。

## 決定・実装

- ProgramOperatingCostsに既存の店長倍率/途中積/営業時間積/合計を移植。32bit幅は前回OperatingStatement.signed32を共用。店長は既存native slot0（staff-1）で、勤務時間は従来どおり店舗の営業時間を使用。倍率・時給・営業時間の新規仮値なし。
- nativeの人件費/設備維持費が0以外なら符号付き額を計上する。負額をゼロや絶対値へ置換しない。既存EconomyStateは負額を受け付けるため独自の補助入金は追加しない。
- 支払後の現金もsigned32へ正規化。ゼロ費用の日には従来どおり冗長な0円記録を追加しない。非native経路は変更なし。
- 什器種別0〜52のみ維持費表へアクセスし、未知負番号/53以上を除外。実アプリのlayout.fixtures/outdoor_fixturesという既存配置表現は維持し、原RAMグリッドを新たに実装したとはしない。

## 検証・ビルド

既存operating_costs.pyから21条件を生成。0/8/24時間、通常時給、正負32bit境界、店長の途中130倍と除算、各人/合計、設備料金とkind53除外を照合。build_fixture.pyは既存Pythonモデルを読むだけで原CPU実行ではない。

新daily_costs_smokeでnative人件費の負額計上と現金・月次集計・JSON、維持費の負額/対象外番号/0時間の無記録を確認。制御した極端な時給・料金入力であり、通常プレイの自然到達を主張しない。初回のテスト入力536870912では合計が正になるため、負額破棄を再現する入力2147483647へ訂正した。

Godot4.6.3関連10本成功、SCRIPT ERRORなし: daily_costs、finance_width、annual_personnel、annual_personnel_ui、staff_lifecycle、renovation_editor、graph_sale、donations、rival_advertising、source_people。Python全793件成功、想定失敗0、外部プラグインの非推奨警告1件。

全体headlessは1205step末尾passedへ到達するが、既存_step_manager_reportsのconfig.source_catalog欠落SCRIPT ERROR5回を引き続き検出。全体合格とはしない。

APK0.8.13-daily-costs/code93を従来touchfix署名v2/v3で出力し、修正gdcと新helper収録・smoke非同梱を確認。実機/実聴未確認。詳細docs/handoff/2026-11-21-v0813-build.json。

## 変更ファイル

vertical_slice_simulation.gd、新program_operating_costs.gd/uid、daily_costs_smoke.gd/uid、source_daily_costs.json、fixture生成script、CI、export_presets.cfg、本文、最新handoff/build/status、PROJECT_MEMORY追記。

## 範囲外

全日中取引の32bit化、全会計欄の全生成元/履歴、経費第3欄の全用途、原物理店舗順/全営業RNG、原カード保存、全通知制御列、既存未解決6件（U-1〜U-6）は未完のまま。既存の会計全体が完成したとは呼ばない。
