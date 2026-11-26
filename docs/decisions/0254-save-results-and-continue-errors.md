# 0254 — 保存結果の再表示と続きからの失敗処理

2026-11-26、PLAY-0254。基点5f60c233d6c01666b7f1cff5a8c3d283e68fe412、branch `chatgpt/mobile-resume-20261126`。main6282489と開PR #286のHEADを確認し、同PRへ追加する。ユーザー指示「続けて」「都度ビルドしなくていい」に従う。

## 背景と判断

通常の保存/読込UIの確認で、PSシステムの結果通知は継承元phone_ui.refreshが既存ラベルの変化を検知して表示していると分かった。初回から表示がないという当初の見立ては誤りだった。同じ結果を続けて受け取ると文字列が変化せず通知されない点を修正する。変更前のps1_uiへ一時的に戻した専用回帰で「Repeated PS save has no visible success result」、exit1を確認し、作業ファイルは復元した。

タイトルは非DictionaryのJSONを拒否せずゲーム開始へ進める構造だった。またmain._readyは本当のload_stateがfalseでも新規状態の初期化を続けていた。「続きから」が新規ゲームに見える経路を塞ぐ必要がある。

## 実装

- PSシステムのセーブ/ロード選択時に継承元の通知比較値だけを解除し、既存refreshが結果を一度表示する。追加のshow_noticeを重ねず、旧メニューのclose_windowも呼ばない。
- SaveGameService.read_from_pathにファイル読出し/JSON解析/Dictionary確認を集約する。読めない、空、非Dictionary、構文不正なら空Dictionaryを返す。load_from_pathとタイトルから使用する。書込方法/保存形式/既定パスは変更しない。
- タイトルは空/不適合な読出し結果でシーンを変更しない。既存クリア結果の解除フラグ処理は維持する。
- mainの継続読込がfalseなら通常プレイの初期化/進行へ進まず、処理を止めてタイトルへ戻す。GameLaunchStateの一時エラーをタイトルが消費し、「続きから」の選択と既存の翻訳済みエラー文を表示する。エラーは保存データには含めない。
- 実JSONを使う回帰のため、main._save_serviceが設定済みならその依存を使用し、未設定の製品起動では従来どおり通常サービスを生成する。

## 検証

新save_feedback_smokeは一意なuser://tests/配下の実JSONを用い、既定ユーザー保存は書き換えない。保存成功/繰返し成功、サービスの保存拒否/既存ファイル保持、読込拒否/繰返し拒否、切れたJSONの読出し拒否、タイトルの非Dictionary拒否、実load_stateのschema拒否からタイトル復帰、クリア結果フラグ7の解除、通常の建築済み店舗からの継続を確認する。保存拒否は依存でfalseを返す確認であり、ディスク故障を起こした試験ではない。通知キューに既存の店舗イベントが残るため、重複確認はキュー全空ではなく同じ保存結果が二重予約されていないことを検査する。

Godot4.6.3の関連10本成功: save_feedback / load_ui_restore / mobile_resume / ps1_title / ps1_menu_dispatch / renovation_ui / renovation_editor / source_notifications_ui / calendar_ui / source_audio_ui。Python804件成功（外部プラグインの非推奨警告1）、全体headless1205step成功、SCRIPT ERROR/ERROR0。CIへ新回帰を追加した。

## 変更ファイル

`game/scripts/save_game_service.gd`、`main_menu.gd`、`game_launch_state.gd`、`main.gd`、`ps1_ui.gd`、新`save_feedback_smoke.gd`、`.github/workflows/native-staff-regression.yml`、本decision、最新handoff/status、RELEASE_ACCEPTANCE、PROJECT_MEMORY追記。

## 範囲外・配布

新たな原作数値・経営仕様・バランス変更はなく、Museの新規解析を採用していない。load_state内部の全破損schema検証/原子性を保証した変更ではない。原カード互換、原作完全一致の未完、既存未解決6件（U-1〜U-6）は残る。Android実機確認なし。APK/版数を更新せず、配布済0.8.14/code94にPLAY-0252〜0254は未収録。
