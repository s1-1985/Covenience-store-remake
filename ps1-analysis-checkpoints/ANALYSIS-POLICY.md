# 解析成果の保存方針

2026-11-03、ユーザーから「解析したデータは全てgitへアップ」と指示された。

- 保存先：s1-1985/Covenience-store-remake の chatgpt/ps1-analysis-recovery-20261103。
- 解析コード、根拠、検証結果、生成データ、再現に必要な入力・パッチ・乱数シードを保存する。
- まとまった検証ごとにコミットし、保存内容を読み戻して確認する。
- 巨大な原本は分割保存と復元スクリプトで保持し、サイズ・ハッシュで完全性を確認する。
- 元ファイルへのリンクだけの登録を、実データのバックアップ完了とは呼ばない。
- 実験用入力、到達した原処理、代用した外部境界、未検証部分を記録する。
- 原資料の変更や結果の再解釈では、過去の記録と更新後の結論を区別する。
- 解析成果は専用解析ブランチへ保存する。解析が必要範囲まで済んだら、スマホ版へ反映してAndroid APKをビルドする。
- mainや並行する他者のブランチを勝手に上書き・マージしない。

## 最新の作業優先順位（ユーザー指示、2026-11-13）

- 主作業はPSディスクイメージのデータ解析である。ファイル構造、画像・音声・配置・マスターデータ、原プログラムから仕様を抽出する。
- 解析後は、必要な仕様とデータをスマホ版へ反映してAPKをビルドする。
- 検証は抽出や移植の正しさを確かめるために行う。営業を何百更新も延長したり、検証回数を増やしたりすること自体を成果にしない。
- 通常プレイの再現に必要な未解読データを優先する。解読済みの内容と新しい発見を区別し、未確認事項を明記する。

## 保存済み

- [2026-11-14：41什器の補充閾値・満杯までの継続・在庫不足の2集計](analysis/20261114-restocking-stockout-data/README.md)

- [2026-11-14保存：価格設定・144購買型の店選び・店舗指標の持越し](analysis/20261113-pricing-store-choice-data/README.md)

- [2026-11-13：営業時間7区分・53什器の維持費と人件費の丸め順](analysis/20261113-operating-cost-data/README.md)

- [2026-11-13：床画像・清掃能力指標・汚れ発生と警告判定の接続](analysis/20261113-floor-cleaning-data/README.md)

- [2026-11-13：通常店内の人物描画・休憩姿勢・区間末尾の向きと入力別更新](analysis/20261113-actor-render-data/README.md)

- [2026-11-13：店員・決済イベントから効果音16本／ボイス12本と元サンプルへの連結](analysis/20261113-staff-sound-data/README.md)

- [2026-11-13：季節・来店判定・追加購買と通常選択から除外される2商品枠](analysis/20261113-seasonal-demand-data/README.md)

- [2026-11-13：商品27件・什器53件・現金の識別と方向/月別在庫画像](analysis/20261113-product-stock-data/README.md)

- [2026-11-13：建物・客構成・購買型・外見の連結と人口計算の扱い](analysis/20261113-customer-data/README.md)

- [2026-11-13：ディスク77ファイル・TIM34画像・外部配置の構造解析](analysis/20261113-disc-data-extraction/README.md)

- [2026-11-13：新ライバル店の初日営業と日次決算](analysis/20261113-new-rival-operation/README.md)

- [2026-11-13：自然月次・ライバル出店・会社建築と11,688更新、店舗順モデル修正](analysis/20261113-next-month/README.md)

- [2026-11-13：自然営業200更新・最新10,488更新と復元再開検証](analysis/20261113-operating-continuation/README.md)

- [2026-11-13：人物57描画・12移動と音声開始前の追加描画](analysis/20261113-actor-frame-timeline/README.md)

- [2026-11-12：通常営業800更新・時計20560、日次決算と全証跡の再展開検証](analysis/20261112-operating-continuation/README.md)

- [2026-11-12：人物レコードから544個の原描画パケットと原テクスチャー14画像へ接続](analysis/20261112-actor-packets/README.md)

- [2026-11-11：同一読込確認画面での再試行2条件、正常カード交換後の原デコード・営業復帰](analysis/20261111-load-retry/README.md)

- [2026-11-11：通常営業600更新・次の日次決算と台帳資金突合、最新時計18960](analysis/20261111-operating-continuation/README.md)

- [2026-11-11：営業UIから破損セーブ2条件を拒否・取消し復帰、加算値保存の改変は原デコードへ到達](analysis/20261111-corrupt-load/README.md)

- [2026-11-05：生カード割当・分散14ブロックでの原保存/読込・別実装との相互検証、最新時計17760](analysis/20261105-card-image/README.md)

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
