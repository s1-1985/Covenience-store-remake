# 0244 — 解析済み音声フラグの持越しと店舗別保存

## 背景・採用根拠

ユーザーの2026-11-21指示「Museの解析はまだ実装しなくてよい。あなたが過去に解析して未実装のものから実装」に基づくLEGACY-0244。Muse readyの新規採用ではない。基点6705aa9240c8d8f53fabe19de553b68ceb24e1b3、main688876aと未マージPR270/272/273を確認。実装ブランチchatgpt/legacy-audio-flags-20261121。PRは作成後追記。

過去のdocs/handoff/2026-11-21-operating-audio.mdとdecision0239は、原SE OFF時のフラグ持越しを明確に未移植としていた。現行main._play_event_soundsはローカル変数でフラグを集約してenabled=1で消費し、実際の音声ラッパーだけがSE OFFを拒否するため要求を失っていた。

既存解析の正本: cc342cc2029264a1735694eeb5ee4140b250c4f4 の ps1-analysis-checkpoints/analysis/20261113-staff-sound-data/README.md「営業イベントの対応」。原主処理80023A14..23BBCは音声有効が非0かつ選択店舗一致の場合だけbit0..15を処理して消去する。同資料SHA256は2c76956117c2a664a5b6e4ab4d196276e75450387b88fc9621d453afd9f2d395。既存ProgramAudio.main_requestsとsource_audio fixture426条件にも保持則が実装済み。本作業では新たなディスク/EXE解析を実施していない。

## 決定・変更

- 既知7bit/8イベントの発生時に店舗別u16 source_audio_flagsへORする。イベントログの表示済み位置や描画回数と分離する。
- 選択店舗かつ原SE有効時にだけ既存main_requestsでbit昇順に取り出し、消費したフラグを消す。OFF中と裏店舗は保持し、同一bitは集約。非フラグ音声は従来どおり。
- STORE_FIELDSと既存source_runtime JSONに含め、切替/保存/読込で保持。新店/ゲームリセットは0。旧クライアント保存に項目がなければ0とし、過去ログから推測再生しない。原メモリーカード形式対応とは別。
- Android独自の全体音量ミュートenabledは従来どおりラッパーで抑止する。持越し条件として接続するのは原システム設定のSE OFF（source_settings_bits lowbit0）。独自ミュートを原仕様と同一視しない。
- 新しい音源・発話・バランス数値・全営業RNG消費は追加しない。

## 検証

Python793件成功、失敗/想定失敗0。外部pytestプラグイン非推奨警告1件。
Godot4.6.3でpending_audio / operating_audio / source_audio / source_audio_ui / stockout_audio / stockout_refill / ejection_consistency / people_service_ui / source_people / staff_responseの10本成功、SCRIPT ERRORなし。既存source_audioは426条件の原fixtureを照合。新規pending_audioはOFF3回描画、ON時の10→9→25/一度だけ、別店舗での24集約と選択時消費、JSON復元、旧保存、リセット、clock/RNG不変を検証。最初のテスト設定で本体に存在しない旧rival-02 IDを使い失敗したため、既存テストと同じ(3,3)への実際の出店へ修正。本体の買収規則は変更していない。

広域headlessは1205step末尾passedへ到達。ただし既存_step_manager_reportsのconfig.source_catalog欠落SCRIPT ERROR5回が同じく残り、全体合格とはしない。この件を今回修正したとは数えない。

APK0.8.11-pending-audio/code91を従来touchfix署名で出力、main/vertical_slice_simulationのgdc更新とsmoke非同梱を確認。実機/実聴未確認。詳細2026-11-21-v0811-build.json。

## ファイル

main.gd、vertical_slice_simulation.gd、operating_audio_smoke.gd、新規pending_audio_smoke.gd/uid、export_presets.cfg、native-staff-regression.yml、本文、最新handoff/build/status、PROJECT_MEMORY第19節追記。

## 範囲外・残件

全16bitの生成元、原割込み周期との一致、全通知制御列/演出、SPU音質、原カード形式、全営業RNG/物理スロット履歴順、既存未解決6件（U-1〜U-6）は未完のまま。既存7bitの保持とクライアントJSON保存を全音声の原完全一致とは呼ばない。Museの新しい操作マニュアル解析は今回反映しない。
