# 連続解析：次の日次決算と原カード呼出しの接続

2026-11-04、ユーザーの継続指示を受け、前回の時計14640・累積7328更新から開始した。
保存元は解析専用ブランチのコミット08a9795874c80b9dae9cb05036dbd1c5bc927ce8。
mainやゲーム実装へ変更を加えず、本フォルダへ解析を分離する。

## 自然営業

continue-long.pyは200更新ずつ3区間を連鎖させ、時計15840の次の日次決算を目指す。
途中の時計・現金・配属・乱数は変更しない。区間ごとに原処理と既存モデルを比較し、
現金書込みと店舗元帳から独立に資金を再構成して、RAM保存状態とともに保持する。
long-continuation-status.jsonが完了した区間だけを列挙する。all_passed=falseの場合、
未完了の残り区間まで検証済みとは扱わない。

最初の200更新は14640→15040、最終自社資金98,716,741・他社153,777,641まで一致した。
従業員全体処理・客処理を各600回、フレーム400回照合した。
次の区間へ継続している。各区間の.audit.json、evidence/の全比較記録とCPU状態が再開根拠である。

## タイトルから原カード判定・原ファイル読込みまで：10条件

従来のタイトル検証で代用していた7B1F8/7AB2Cの完了値・データ注入を取り除いた。
タイトル51174→51524から原7B1F8、原7AB2Cのmode0/1、原チェックサム5188Cを実行し、
成功時は原デコードとプレイ復帰まで進む。
代用は明記したBIOSファイル・イベント端点と、従来の描画・音声SDK境界に限定する。
原7E57Cのメモリーコピーは代用せず実行する。

入力ファイルは時計14640の原エンコーダ6B81C→原ライタ7ADF8の2区画から作った114,688バイト。
末尾9,812バイトは原CPU RAM由来で保持する。テスト条件のheader_mutation/tail_mutationのみ、
対象範囲を明示的に変更した診断ファイルを用いる。

| 条件 | 期待結果 |
|---|---|
| 正常 | 原ファイル892回読込み、チェックサム受理、営業へ復帰 |
| チェックサム不一致 | 本文は原ファイルから読むが受理せずタイトルへ戻る |
| 対象ファイルなし | 原状態2、読込みせずメッセージ1e1 |
| post応答3 | 原状態3、読込みせずメッセージ1f5 |
| info応答2継続 | 原処理が30回試行して状態4、メッセージ1dd |
| info応答1継続 | 原処理が3回試行して状態5、メッセージ1df |
| infoが2回busy後に成功 | タイトルからの単一要求内で回復し営業へ復帰 |
| postが2回busy後に成功 | タイトルからの単一要求内で回復し営業へ復帰 |
| ファイル先頭512バイトをゼロ化 | 論理BIOS条件下では本文読込み・営業復帰が一致 |
| 本文末尾9,812バイトをa5に変更 | 全本文を読み、保存対象ペイロードは変えず営業へ復帰 |

最後の2条件から物理カードのヘッダ検証仕様まで推定しない。論理ファイルAPIの下での原ゲーム側の挙動である。
ファイルのデータ注入・状態注入は7B1F8/7AB2Cで行っていない。
各読込モードもカード状態を再取得するため、正常経路のinfo/load/post要求は初期判定を含め各3回。
busy2回からの回復では対象要求だけがさらに2回増える。

10条件は2つのCPUで呼出し・ファイルI/O・データ・描画と既存の独立親モデルを比較した。
代表側で原カード関数22回、128バイト読込み5,352回。2CPUを別々の自然営業条件として重複計上しない。
title-chain-coverage.jsonが全10条件と明示した期待値の再監査結果。
個別の*.jsonには全BIOS引数・結果、I/O、原関数の呼出し元・復帰状態、描画記録を残す。

## 再現・制約

原r2 ZIPを復元し、前回のmain-05.jsonとram.zlibをalgorithm-analysis/source/opened-snapshots-20261028へ重ねる。
Unicorn 2.1.4等の実行環境は前回と同じ作業環境である。

```sh
python continue-long.py /path/to/algorithm-analysis
python native-title-card-chain.py /path/to/algorithm-analysis TOWN0001-ci-main-05-single success bad_checksum init_error_2
python native-title-card-chain.py /path/to/algorithm-analysis TOWN0001-ci-main-05-single init_error_3 init_error_4 init_error_5 info_busy_twice post_busy_twice
python native-title-card-chain.py /path/to/algorithm-analysis TOWN0001-ci-main-05-single header_mutation tail_mutation
python summarize-title-chain.py
```

原タイトル検証の差分はtitle-driver.patch。原ZIPのソースを上書きせず、別モジュールで指定箇所のみ置き換える。
タイトル状態1は明示した試験入口であり、営業中の終了操作からタイトルまで連続した証明ではない。
物理カードの割当・シリアル通信、BIOS命令、過去VRAM/SPU/IRQの完全復元は対象外。
ペアはUnicornと原の子関数を共有し、独立CPU実装2種類の証明とはしない。

## 開発中に却下した比較

最初のカードアダプタでは7E57Cまで一律に代用し、カード外のスタック上のコピー先が
両親処理で64バイト違う120件を全I/O同一条件に含めて失敗した。
development-memcpy-scope.failure.jsonとログを保存し、最終版では7E57Cを原実行に戻した。
この相違を正規化して一致させたものではない。

保存UIの初回診断では、画面中にも乱数を凍結する過剰な条件で失敗した。
development-save-ui-frozen.logを保持する。以後、店舗・従業員・資金・時計の保存を確認し、
UI中の乱数は変更前後を別記録する。自然営業の継続処理では乱数の注入を行わない。
保存UIの検証結果は完了時のnative-save-ui-summary.jsonに別記する。
