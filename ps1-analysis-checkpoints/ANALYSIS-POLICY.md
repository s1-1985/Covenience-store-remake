# 解析成果の保存方針

2026-11-03、ユーザーから「解析したデータは全てgitへアップ」と指示された。

- 保存先：s1-1985/Covenience-store-remake の chatgpt/ps1-analysis-recovery-20261103。
- 解析コード、根拠、検証結果、生成データ、再現に必要な入力・パッチ・乱数シードを保存する。
- まとまった検証ごとにコミットし、保存内容を読み戻して確認する。
- 巨大な原本は分割保存と復元スクリプトで保持し、サイズ・ハッシュで完全性を確認する。
- 元ファイルへのリンクだけの登録を、実データのバックアップ完了とは呼ばない。
- 実験用入力、到達した原処理、代用した外部境界、未検証部分を記録する。
- 原資料の変更や結果の再解釈では、過去の記録と更新後の結論を区別する。
- mainおよびClaude管理ブランチは変更しない。今回の指示は解析継続と専用ブランチ保存であり、
  ゲーム本体への組込みやPR #270のマージを指示したものではない。

## 保存済み

- [2026-11-05：自社店舗一覧・ライバル調査/買収制限・店内復帰後の保存読込み、最新時計17640](analysis/20261105-view-controls/README.md)

- [2026-11-05：月次後120更新、町変化・月次結果画面・通知中のメニュー制限](analysis/20261105-post-monthly/README.md)

- [2026-11-05：チャット再開後600更新・自然な月次決算到達、最新時計17280](analysis/20261105-resumed-daily-close/README.md)

- [2026-11-05：空カード新規保存・エラー再試行・取消しと最新時計16080](analysis/20261105-card-recovery/README.md)

- [2026-11-05：営業入力から原保存/読込UIと原カード処理へ接続、最新時計15960](analysis/20261105-play-save/README.md)

- [2026-11-04の最新再開点：時計15840・累積7928更新](analysis/20261104-long-continuation/README.md)
- [添付ディスク一致・決算終了判定17条件・決算後120更新](analysis/20261104-disc-continuation/README.md)

- [r2原ZIPの全バイト](archives/20261103-r2/README.md)
- [旧成果物の台帳](archive-index/README.md)
- [会話から復旧した補助記録](2026-11-03-session-recovery/README.md)
- [原カード状態判定の再実行](analysis/20261103-native-card-recovery/README.md)
- [原保存ペイロード処理の再実行](analysis/20261103-native-payload-recovery/README.md)
- [原カードファイル処理の再接続](analysis/20261103-native-file-recovery/README.md)

- [ライバル月次処理の再照合](analysis/20261103-rival-monthly/README.md)

- [町成長の全体実行と到達部分照合](analysis/20261103-town-full-flow/README.md)

- [会社・商業施設の増減モデル（原処理33条件一致）](analysis/20261103-town-balance/README.md)

- [営業継続コードと開始状態の確認](analysis/20261103-operating-continuation/README.md)

- [原カード読書きの短いI/O境界試験](analysis/20261103-card-io-boundaries/README.md)

解析継続時は最新コミットと各README・results.jsonを読んで再開地点を確認する。
