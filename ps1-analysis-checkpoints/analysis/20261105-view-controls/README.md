# 店舗一覧・ライバル店操作・店内から復帰後のカード保存

2026-11-05。開始コミットdbfaa0afc506edd8f7a17ab788d1ecc8614fd172。
主系列main-15（時計17520、累積8768更新）から再開した。作業領域の整理後、Gitを新規取得し、
restore-latest.pyで原r2の209部品・153696391バイトと最新CPU状態を復元した。
原EXE SHA256はd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd。
復元の記録はrecovery-audit.json。復元回数は営業更新へ加算しない。

## 最新の自然営業再開点

| 項目 | 開始main-15 | 終了main-16 |
|---|---:|---:|
| 時計 | 17520 | 17640 |
| 累積更新 | 8768 | 8828 |
| 自社資金 | 99006241 | 99005641 |
| 他社資金 | 153125796 | 153132096 |

自然営業は60更新を追加した。自社は仕入600、他社は売上7050・仕入750。
資金書込みの連鎖と各店舗台帳からの別計算が一致した。スタッフ・客の全体処理は各180件、
フレームは120件を比較した。この区間に追加の日次・月次決算はない。
時計・乱数・資金・配属を変更していない。以下のUI操作枝は主系列を置き換えず、60更新へ合算しない。

## 実店舗と選択経路

| 対象 | 実スロット | 所有フラグ | 町の矩形 | 到達した画面 |
|---|---:|---:|---|---|
| 自社本店 | 0 | 0x0001 | (26,12)〜(27,13) | 自社一覧の先頭 |
| 自社2店目 | 2 | 0x0002 | (14,10)〜(15,11) | 一覧2行目→店内表示2→店舗操作60418 |
| ライバル本店 | 1 | 0x8001 | (43,12)〜(44,13) | 町マップ→60D6Cの相手店画面 |

原店舗一覧5F500は1BD78へフィルタ0を渡す。今回の一覧は[0,2]で、
RAMの物理順[0,1,2]とは異なり、ライバル1は含まれない。
独立した一覧親モデルlist-parent-monitor.pyを追加し、実入力で到達した10回の親処理について、
待機・上・下・決定・取消しの5入力分岐と原子関数の呼出し順、対象メモリを照合した。
行0で上を押すと行1へ、行1で下を押すと行0へ循環し、取消しで町表示0へ戻る。
自社2店目の店内で0x80を押すと店舗操作60418に入り、町の全体メニュー5FE54には入らなかった。

これは原子関数を共有する親判断の独立照合である。自社店ゼロ、範囲外行を初期値とする条件や
全グラフィックの独立再現を検証したものではない。原命令列はlist-parent-source.jsonに保持した。

最初は一覧をもう1行進めれば相手店を選べると考えたが、自社本店へ循環した。
その入力・出力・旧ドライバはdevelopment-own-list-wrap/等に保持している。
同ディレクトリの旧case名rivalは試みの名称であり、相手店の検証結果とは扱わない。

## 町から相手店を選び、調査・買収の制限を通す

元のカーソル(14,10)から、右29回・下2回の実入力を供給して(43,12)へ移動した。
座標・所有フラグ・資金を直接変更せず、決定で原60D6Cと原4D6ECへ到達した。
相手店を自社店内として開く経路ではない。最初の取消しでは料金引落しと所有者変更はなかった。

| 操作枝 | 入力元 | 原親処理の結果 | UI料金引落し |
|---|---|---|---:|
| 取消し | 調査前 | cancel | 0 |
| 調査・詳細表示後に閉じる | 調査前 | 既存モデルの識別子lease | 500000 |
| 再度開いて決定 | 調査後 | 情報表示のみ、戻り値2、親はcancel | 0 |
| 調査後に下・決定 | 調査後 | 情報表示のみ、戻り値2、親はcancel | 0 |
| 買収を選ぶ | 調査前 | first_store_guard | 0 |

原レコード+2のフラグを本稿では便宜上「調査済み」と呼ぶ。初回の費用支払いで0→1になった。
原4D6ECはフラグ1なら4D8C8で情報表示し、決定または取消しを受けて2を返す。
したがって調査後の画面に、同じ調査・買収の選択メニューが出るという初期想定は誤りだった。
その誤った期待値だけが失敗したログと旧ドライバをdevelopment-*-expectation*等に保持し、
原コードやフラグを変更せず、同じ入力を再検証して情報表示の実際の結果を保存した。
識別子leaseを、賃貸契約や所有権移転の証拠とは解釈しない。

今回の提示買収価格は52704360＝2×(土地23000000＋店舗評価3352180)。この実店舗・時点の値である。
原の土地・店舗評価、資金/資本の処理と親制御は既存SourceAcquisitionMonitorで照合した。
買収制限の枝は、調査前の実保存状態から選んだ。保有資金が提示価格を上回っていても、
相手店の通番1で拒否し、支払い・所有フラグ変更は起きなかった。
調査後の情報画面から買収を選べた、あるいは全モードの全ライバルで同条件を試したとはしない。
実験後の普通の売上・仕入とは分け、UI料金は原1CBC4呼出しとその独立照合で確認した。

## 店内から町へ戻った後の原保存・読込み

自社スロット2の店内状態から、取消しで町へ戻り、0x80で原全体メニューへ入った。
原保存・原読込みのカード経路を接続し、実ファイル114688バイトを生成した。
保存時計17534、選択店舗は0xFFFFFFFF。店内の視点そのものを保存した試験ではない。

保存本文128バイト×892回、原チェックサム、原デコード37領域を照合した。
同じ実ファイルを別の厳密MIPS-I実行系でも原読込み・チェックサム・デコードにかけた。
読込後の町表示0・選択店舗なし、商品27×12・町外観101×4の参照値も一致した。
結果はplay-save/load.json、read-decode.json、loaded-runtime-tables.json等に保持する。
この操作枝の時刻・乱数履歴は主系列main-16とは別である。

## 再現・保存物

原r2とsource-referenceコードを復元し、前回20261105-post-monthly/evidence/にあるmain-15の
jsonとram.zlibを解析source/opened-snapshots-20261028へ重ねる。
Python依存はunicorn 2.1.4、capstone 5.0.7、Pillow 13.0.0。
このフォルダから順に実行する。rootのrestore-latest.pyは現在の最新main-16を復元するため、
今回の入力を再実行する際には上記main-15を追加する。

```sh
python continue-main.py /absolute/path/to/algorithm-analysis
python navigate.py /absolute/path/to/algorithm-analysis own
python navigate.py /absolute/path/to/algorithm-analysis list-wrap
python navigate.py /absolute/path/to/algorithm-analysis rival
python rival-actions.py /absolute/path/to/algorithm-analysis investigate
python rival-actions.py /absolute/path/to/algorithm-analysis reinspect
python rival-actions.py /absolute/path/to/algorithm-analysis info-only-confirm
python rival-actions.py /absolute/path/to/algorithm-analysis guard
python play-save.py /absolute/path/to/algorithm-analysis save
python play-save.py /absolute/path/to/algorithm-analysis load
python audit-save.py /absolute/path/to/algorithm-analysis
python audit-controls.py /absolute/path/to/algorithm-analysis
```

controls-audit.jsonが統合監査。各枝の全比較記録、入力、呼出し列、CPU状態、カード実ファイル、
原命令、初期想定の修正記録を保存する。旧一覧試行を含め、実験枝の更新数を自然営業へ重複計上しない。
Git保存後の全バイト読み戻し結果はgit-readback.jsonで、検証対象コミットと後続の記録保存コミットを区別する。

mainおよびゲーム本体は変更しない。既存のSDK・論理BIOS/カード・GPU/SPU/IRQ境界はモデルのままである。
比較ペアはUnicornと原子関数を共有し、画面画素・実音声・物理カードやゲーム全体の完全再現は主張しない。
次の自然営業はmain-16から続ける。
