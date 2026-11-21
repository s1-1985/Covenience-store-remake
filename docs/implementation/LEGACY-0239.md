# LEGACY-0239 — 既存解析の営業音声接続

- 状態: 実装済み・レビュー待ち
- Muse指示書ID: 未発行。今回のユーザー直接指示に基づく移行作業
- 根拠: docs/research/operating-audio-bridge-2026-11-21/
- branch: chatgpt/source-operating-audio-20261121
- base: chatgpt/ps-ui-touch-audit-20261119 / 9dfa80b98bf584b90d2a5a53b46ad67dc49838af
- PR: #272 https://github.com/s1-1985/Covenience-store-remake/pull/272
- 実装コミット: de25b168de01381988dee94521e93939f22e7190
- 逸脱: 新規解析・仕様変更・独自数値追加なし
- 変更: 原4音源接続、既知7bit昇順/集約、locale、固定テスト、CI、APK89と記録
- 検証: Godot関連10本成功、Python786成功/既存2失敗/想定1、従来署名APK0.8.9生成
- 実機/実聴: 未確認
- Muse確認事項: 原OFF時のフラグ持越し/全生成元、原更新周期と描画更新単位の対応は未完。これは今回の既存動作維持と区別してreadyへ記載してほしい
- 詳細: docs/handoff/2026-11-21-operating-audio.md、2026-11-21-v089-build.json

## 変更ファイル

- .github/workflows/native-staff-regression.yml
- PROJECT_MEMORY.md
- docs/decisions/0239-source-operating-audio.md
- docs/handoff/2026-11-21-operating-audio.md
- docs/handoff/2026-11-21-v089-build.json
- docs/handoff/full-integration-status.json
- docs/implementation/LEGACY-0239.md
- docs/research/operating-audio-bridge-2026-11-21/README.md
- docs/research/operating-audio-bridge-2026-11-21/source-provenance.json
- game/export_presets.cfg
- game/locale/ja.po
- game/scripts/domain/program_audio.gd
- game/scripts/domain/program_people.gd
- game/scripts/domain/source_integration.gd
- game/scripts/main.gd
- game/scripts/operating_audio_smoke.gd
- game/scripts/operating_audio_smoke.gd.uid
