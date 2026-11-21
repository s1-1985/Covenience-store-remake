# CSRM-001 v1 — APK収録・検証報告

- 採用指示書: muse/analysis / 030e468f1b21684d3304026c858e387e5f5d9b45 / docs/muse/ready/CSRM-001.md、v1
- 対象基準: 9dfa80b98bf584b90d2a5a53b46ad67dc49838af
- 実装ブランチ: chatgpt/source-operating-audio-20261121
- PR: #272 https://github.com/s1-1985/Covenience-store-remake/pull/272
- 状態: 収録・検証記録済み、差分を含めMuseレビュー待ち

## 対応状態

| 段階 | 状態 |
| --- | --- |
| decision0238コード | 実装済み。238b965e25/a65af72a14が現在HEADの祖先であることを確認 |
| 関連テスト | 指定Godot8本成功。全体テストは下記の既知失敗を保持 |
| APK収録 | 0.8.9-operating-audio / code89、収録確認済み |
| Android実機/実聴 | 未実施（ユーザー待ち） |

## 成果物とソース

Conveni-v0.8.9.apkはゲームファイルが実装コミットde25b168de01381988dee94521e93939f22e7190に一致する作業ツリーから出力した。ビルド時点は同コミット作成前であり、コミットから再チェックアウトして作ったとは表現しない。アップロード用Gitツリーとローカルのステージ済みツリーのSHA一致を確認。APK内ではmain/program_audio/program_people/source_integration/vertical_slice_simulationの5gdcが0.8.8から更新され、smoke/testsは非同梱。詳細はdocs/handoff/2026-11-21-v089-build.json。

- package: com.conveniremake.touchfix
- versionName: 0.8.9-operating-audio、versionCode: 89
- size: 45,073,676bytes
- SHA256: cbe305d026f4f4b80b6bc887546ef9fa832536a10c4d7f3b5949069de9cadb95
- certificate SHA256: 4e1ea772ac6aea449573f8c151028082d011f82945170272b8dc61b43bec29a4
- apksigner: verifies、v2=true / v3=true、署名鍵はGit非収録

## 今回実行した確認

Godot4.6.3の指定8本：live_staff_traits/source_people/staff_response/source_geometry/staff_lifecycle/annual_personnel/annual_personnel_ui/town_pressはすべて成功。既存音声関連10本との重複を除くと今回15本の関連smokeが成功している。

Python全789件：786成功、2失敗、1想定失敗。失敗名は以下の通り。

- GameVerticalSliceContractTests.test_slim_engine_template_keeps_what_the_game_uses：古いテンプレート指定文字列の期待値に不一致
- GameVerticalSliceContractTests.test_store_site_is_chosen_freely_with_a_land_price_per_site：main.gdの旧サイト選択ガードの文字列期待値に不一致
- 想定失敗：StoreStepKnownIssueTests.test_a_failing_purchase_phase_does_not_leave_the_clock_advanced

広域headless_smokeも実行し失敗を再確認。出力：`ERROR: the town map must be legible and fit left of the side panel`、_initialize headless_smoke.gd:2799 → _fail:3344。全体成功とはしない。これらの修正はCSRM-002へ残す。完全な実行ログはローカルcsrm-001-checks/とcsrm-001-pytest.logに保持し、本体/APKへ大量ログを追加しない。

## 指示書との差分・変更ファイル

Muse指示書の保存前に、ユーザー直接指示の別作業LEGACY-0239で音声4項目とAPK89を作成済みだった。このため今回の報告対象は音声変更を含む後継ブランチと成果物であり、0238だけの別APKは作成していない。0239は別作業が使用済みのため、本作業の決定は0240とした。CSRM-001採用後にはゲームロジックを追加変更していない。

CSRM-001による変更は本報告、docs/decisions/0240-apk-verification-handoff.md、PROJECT_MEMORY第19節追記と任意のヘッダ日付是正、検証結果を追記するビルド記録。ゲーム側の版数・locale・ロジック変更はLEGACY-0239側で記録済み。

## Museへの確認事項

上記の後継ブランチ/既作成成果物を使う対応差分の受け入れ可否。既知失敗の解消はCSRM-002で進める。ユーザーに毎回の指示書中継は求めない。
