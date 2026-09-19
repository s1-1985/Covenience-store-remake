# 0121: 「つまみだす」(怒る前の客の強制退店)をUIから実行可能に(タスク#52)

## 背景

タスク#51で「新人店長実習マニュアル」book p.35を直接再読した際、同じページの
コラム「怒られるまえに外へつまみだす」に、以下の明文があることを確認した:

> 怒りやすいお客さんは、おじさんやおじいさんに多い。もしレジ前の混雑にこの
> 人が混じっていたら、カーソルをこの人に合わせて決定ボタン。怒り出すまえに
> "つまみだす"を選んで、お店の外に出してしまうといいぞ。

これはCONFIRMED_OFFICIALな一次資料であり、`PROJECT_MEMORY.md`第21.3節に
未実装のNEW発見として記録されていた。タスク#51は(店員全員への)怒りペナルティ
のスコープ是正のみで、この「つまみだす」アクション自体の実装は次タスク候補
として明示的に対象外にしていた。本タスクではその実装に着手した。

## 決定

### `VerticalSliceSimulation.try_eject_customer(customer_id: String) -> bool`(新規)

対象は`"waiting_checkout"`または`"checkout"`フェーズの客のみ(書籍の
「レジ前の混雑」という表現に対応。まだ買い物中の客は対象外)。

- `"waiting_checkout"`の場合: `_checkout_queue`から該当客IDを除去。
- `"checkout"`の場合: `staff.checkout_staff().state`を`"idle"`に戻す
  (レジ担当スタッフを即座に解放)。
- いずれの場合も、客のフェーズを既存の`"leaving"`(退店中)へ遷移させ、
  既存の`layout.find_path(..., layout.exit)`で出口までの経路を設定する
  ――ノーセール退店(売り切れ時)と全く同じ既存パターンを再利用し、新しい
  アニメーション/フェーズを発明していない。
- `customer_ejected`イベントを記録(`had_unsettled_basket`フィールドで
  未精算のカゴの有無を記録)。
- 既に精算済み(退店中)の客や未知の客IDに対しては`false`を返す。

**REMAKE_BALANCED_DEFAULT choice**: 退店させられた客が既にカゴに入れていた
商品(`try_take_one()`で既に在庫から差し引かれている)は、棚へ戻さない。
書籍にはどちらの扱いかの明記がなく、このクライアントには「ピックアップを
取り消す」仕組み自体が他に一切存在しないため、新たに発明するより「持った
まま出て行く」(=実質的な万引き相当のロス)という最小限の解釈を採用した。
メカニクス自体(つまみだす、という行為が存在すること)はCONFIRMED_OFFICIAL
だが、この「商品ロス」の扱いだけはこのプロジェクト独自の発明である。

### UIへの接続

タスク#38が確立した「経済アクションは必ずUIから到達可能でなければならない」
という規律(決定書0107、テスト`test_economy_actions_are_reachable_from_
the_ui_not_only_headless_smoke`)に倣い、バックエンドの`try_eject_customer`
だけでなく、STORE STATUSパネルに新規`EjectCustomerOption`
(OptionButton)+`EjectCustomerButton`を追加した。

`FixtureCatalogOption`等の既存カタログ選択肢とは異なり、退店可能な客の
集合は毎ティック自動的に変化する(客が自然にレジへ到達・退店していく
ため、明示的なプレイヤー操作後にしか再構築されない他の選択肢とは性質が
違う)。そのため`_refresh_eject_customer_option()`は`_ready()`後の明示的
呼び出しだけでなく、毎ティック呼ばれる既存の`_refresh_ui()`からも呼び出す
形にした。

## テスト

- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。(a) 買い物中の客・
  未知の客IDに対する拒否、(b) レジ対応中の客を退店させると即座にレジが
  解放されること、(c) 二重退店の拒否、(d) 退店した客が最終的に売上を
  一切計上しないこと、(e) 退店させなかったもう1名の客は正常に売上計上
  されること、を検証。また既存のタスク#38 UIシナリオ(`economy_ui_scene`)
  に、実際のOptionButton/Button経由での退店操作も追加。Godot 4.3公式
  バイナリで897ステップ(タスク#51時点の831から、新規シナリオ2件分
  増加)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_eject_customer_action_is_wired_and_confirmed_official`を追加。
  evidence_noteのCONFIRMED_OFFICIAL/REMAKE_BALANCED_DEFAULTタグ、
  バックエンド関数の存在・配線、HUDノード・ハンドラの存在を検証。
  フルスイート664件(新規テスト関数1件追加)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`: `try_eject_customer()`を
  新規追加。
- `game/data/vertical_slice.json`: `simulation.eject_customer_evidence_note`
  を新規追加。
- `game/scenes/main.tscn`: `EjectCustomerOption`/`EjectCustomerButton`
  ノードを追加。
- `game/scripts/main.gd`: `_refresh_eject_customer_option()`/
  `_on_eject_customer_pressed()`を新規追加し、`_refresh_ui()`・`_ready()`
  から配線。
- `game/scripts/headless_smoke.gd`: 新規シナリオ2件(バックエンド直接・
  UI経由)を追加、構造チェックの対象ノードリストへ2件追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- 書籍が示唆する「レジ前の混雑にいる客にカーソルを合わせる」という
  マップ上のクリック選択UIは実装していない。既存の他の経済アクションと
  同じOptionButton+Buttonパターンを再利用しており、`store_view.gd`上の
  客スプライトを直接クリックする入力モードは新規に発明していない。
- 「怒りやすい客はおじさん・おじいさんに多い」という客の年齢層による
  怒りやすさの傾向は、この客観察AIの補助情報として実装していない
  (このクライアントの顧客モデルにはまだ年齢層/属性ごとの個体差自体が
  導入されていないため)。単に「対象フェーズの客なら誰でも退店させられる」
  という、書籍のメカニクス自体(退店アクションの存在)のみを実装した。
