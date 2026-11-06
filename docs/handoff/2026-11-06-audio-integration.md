# 全反映再開地点 — 原音源接続

ユーザーは「解析済みを全て実装。中断で未保存作業を失わないように」と指示している。途中APKは配布せず、実装・検証・GitHub保存を繰り返して続行する。基点は4380edd9（XA130資産と抽出ツールの検証済み保存）。作業一覧はfull-integration-status.json。

## 今回の変更

原作BINを再取得しSHA256を確認、XA130件は原セクター数とPCM長を全件確認して保存済み。原SEQ/VABからBGM7曲、SE16、VOS12も変換し、source_audio.jsonに元音色とハッシュを保持した。オフラインrender_source_sequences.pyはTinySoundFont0.3.7 / NumPy2.3.5 / FFmpeg6.1.1を使う。SoundFontのADSR・音色補間・NRPN・リバーブに実機差があり、原音完全一致とはしない。

原設定SE/BGM1..3/月次報告の3項目を実UIへ接続。月次報告OFFでも経理は実行。通知の予約済み音声を再生し、タイマー0では閉じずCD音声終了で閉じる。タイトルBGM0、終了60/61、クレジットBGM6も接続。終了固定フレームと音声完了の両方を待つ。source_audio_smokeの独立426条件と165資産、source_audio_ui_smokeの実UI操作は個別成功。

## 検証作業中の注意

Python788件は予期しない失敗0・既知想定失敗1。Godotの全回帰を実行中。source_audio_smokeは個別で成功する一方、全回帰の2番目にすると終了時に4音声リソース残存ERRORが出ることがある。機能assertは成功しているが、これを無視して全回帰成功としない。SoundManager._exit_treeでストリームを解放し、テスト末尾で全音声停止・2フレーム待機を追加済み。/tmp/conveni-audio-*ログで調査中。終了シーン旧smokeは音声完了を明示してから固定フレームを進めるよう更新した。

軽量Godotテンプレートにogg/vorbisモジュールを追加。現行APKの公式4.3テンプレートにもある機能だが、新APK生成・Android実機確認はまだ実施しない。

## 次に続ける全範囲

1. 上記Godot終了時の音声リソース残存を解消し、18本の全回帰とPython788件を保存する。
2. 人物・営業の原メイン音声フラグ全生成元を接続する。program_audio.gdの原選択ルールはあるが、生成元の全移植ではない。既存event_sfxの未移植箇所には合成音が残る。
3. 原セーブ37領域・checksum・カード鎖・未知バイトの保持と、実ゲーム対応/取込書出しUI。
4. 操作保持規則・従業員選択・価格/許可/改装/通知生成元等の未反映を原モデルと照合する。
5. 全体が揃ってから同一署名AndroidビルドとUI確認。全反映完了を偽らない。

## 再現環境

作業コピー /workspace/scratch/69fb6031f6b8/conveni。
解析 ../analysis-restored/algorithm-analysis（解析基点2c00ba53から復元可能）。
BIN ../disc-input/SLPS_00782(1).BIN（Library元ID libfile_8685cd6980f881918539115b2c525df7）。
Godot /tmp/conveni-tools/Godot_v4.3-stable_linux.x86_64。
オフラインPython追加依存はPYTHONPATH=/tmp/conveni-tools/python。ゲームには含めない。
GitHubにはこの作業ブランチへ保存する。main688876a4・他PR270/271を勝手に変更しない。
