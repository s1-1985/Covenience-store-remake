# 原音源と設定・通知・終了音声の接続

## 背景

終了処理版4e04e2cでは原音声が未接続で、通知を仮タイマーで閉じていた。
前の未保存音声変換を再構築し、ユーザーの全反映方針に従って成果を途中保存する。

## 決定と本体動作

- SOUND.XAのLBA1513とEXE 800B8CB8のoffset/channel/lengthを使い、130音声を抽出した。元BINのSHA256確認、各行の選択セクター数、FFmpeg復号後PCMのサンプル数を検査し、PCMハッシュも残す。131行目は実音声を指さないため作らない。
- BGM01..07、SE.SEP16曲、VOS.SEP12曲を元SEQ/SEPとVABの音色からオフライン変換した。元VH/VB・SEQハッシュ、音色32バイト、音域、元ADSR、サンプルハッシュ・ループ情報を残す。
- アプリは165件のOggをGodotで再生し、EXE・ディスク・CPU・SF2合成器を実行時に必要としない。Godot軽量テンプレートのOgg/Vorbisモジュールも有効化した。
- 原ディスパッチのSE0..15、VOS16..27、XA28以降、停止-1、BGM6中の抑止を移植。SE OFFはXAを抑止しない原作の境界を保持する。SE16トラックとVOS12トラックを別管理し、停止-1はSEとXAを停止しVOSを停止しない。
- 原設定のSE・BGM1/2/3・月次報告する/しないをシステム画面へ追加。設定bitsと2/3/4のBGM番号対応を使用。月次報告OFFでも月次経理を実行する。ConfigFileとゲームJSONに設定を保持し、不正な設定の読込みを拒否する。
- 通知消費で予約済みの原音声番号を再生し、CD再生が終わってから原表示状態を閉じる。原タイマー0を終了扱いにしない。タップによる打切りはタッチ画面の既存拡張である。
- タイトルBGM0、終了場面60/61、クレジットBGM6を接続。終了画像の固定フレームと音声の両方の完了を待って次へ進む。ヘッドレス時は復号サンプル数由来の長さを使い、実音声ではAudioStreamPlayer.finishedを使う。

## 出典と検証

原解析2c00ba53のaudio_dispatch.py、save_load_control.py、settings_menu.py、music_control.py、cd_audio_start.py、event_queue.py、notification_display.py、main-audio-selection.asm、progression-scenes.asm、scenario-credits-20261031.asm、title-dispatch-20261028.asm。
形式の補助資料はSony Sound Artist Tool: https://psx.arthus.net/sdk/Psy-Q/DOCS/Devrefs/Sound20.pdf 。

export_audio_cases.pyは独立モデルと原コードのオフライン検証から54ディスパッチ・12設定・360メイン音声選択の期待値を保存する。source_audio_smoke.gdはその426条件と165リソース、SE OFF/XAの分離・除外行・終了時計を検査する。source_audio_ui_smoke.gdは実シーンの設定ボタン・月次報告抑止と経理継続・JSON保存・通知の音声終了・終了画面とクレジットを操作する。追加Python検査は165ファイルのSHA256と原PCM長の不変条件を検査する。
最終の全回帰結果は最新handoff/checksを参照する。

## 完了としない範囲

原音声データを使用しているが、BGM/SE/VOSはSPUの実機録音ではない。REMAKE_BALANCED_DEFAULTとしてSoundFontのADSR近似、ドライ音、補間・ファインチューニング・libsnd固有NRPN差、音量調整を明記した。SPUリバーブや各PCMの実機差分は未完である。元音色値は上書きせず残す。

人物・営業処理が立てるメイン音声フラグの全生成元はまだ接続していない。既存event_sfxの未移植イベントには合成音の仮対応が残る。全解析移植完了・原作音声完全一致・Android実機確認済みとは呼ばない。途中APKは生成しない。
