# 引継ぎ: 0.8.9 解析済み営業音声の接続

基点9dfa80b98bf584b90d2a5a53b46ad67dc49838af。main688876aと未マージPR270を確認。Museブランチは確認時点で存在しなかった。今回のユーザー直接指示「解析済みの内容の実装を進めて」に基づき、既存資料だけを移植。新しい原作解析は行っていない。

branch: chatgpt/source-operating-audio-20261121。更新版本体chatgpt/ps-ui-touch-audit-20261119をベースとするレビュー用差分。並行PR270/main/元本体ブランチは変更せず、マージ未実施。

即時決済9/万引き成功21/清掃完了24/体力切れ25を原音源へ接続。既存checkout開始22/終了23/会計10/補充24とともにbit順へ集約。取得失敗・部分補充・戻り休憩中の体力0・裏店舗・再描画で誤って追加再生しないことを確認。既存muteイベントの非再送を維持し、原OFF時のフラグ持越しは未移植と明記。

Godot4.6.3関連10本成功（新operating_audio、source_audio/source_audio_ui、stockout_audio/stockout_refill、people_service_ui、source_people、staff_response、abandonment、live_staff_traits）。新規テストは最終manners0で成功。Python全789中786成功/既存2失敗/想定1。初回の追加失敗はlocale清掃完了の訳漏れで修正済み。全headlessの既知町寸法等は今回再実行/解決していない。

APK0.8.9/code89、45,073,676bytes、従来touchfixパッケージ/署名。前回の更新済み機敏さ参照も今回APKへ収録。変更5gdcとテスト非同梱確認。ビルド詳細は2026-11-21-v089-build.json。実機/実聴未確認。

次はMuseの保存済みreadyを優先。今回の4音源接続と既存7bit順を未反映として繰り返さない。その他フラグ/原OFF持越し・全営業RNG・行列幾何・全通知/演出・原カード形式等は残る。
