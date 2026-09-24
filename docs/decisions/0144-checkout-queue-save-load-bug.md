# 0144: セーブ/ロードの未クリアなチェックアウト待ち行列バグ修正(タスク#74)

## 背景

タスク#73(採用前レジュメ能力バンド)がマージされた後、ユーザーから
「セーブ/ロードの保存データにギャップがないか直接確認」との指示が
あった。`game/scripts/save_game_service.gd`(薄いI/Oラッパー)自体は
問題なく、実際のセーブ/ロード状態変換ロジックは`vertical_slice_
simulation.gd`の`save_state()`/`load_state()`にある。

`save_state()`自身の既存コメントは、意図的に保存しない2つの項目を
既に明記していた(来店客の途中経路・什器補充の途中進捗、およびタスク#48
の店員スキル成長——いずれもドキュメント化済みの既知のギャップ)。今回、
`reset()`と`load_state()`を1行ずつ突き合わせる形で直接監査したところ、
**ドキュメント化されていない実際のバグ**を発見した:

`reset()`は`layout.reset()`/`inventory.reset()`/`economy.reset()`/
`customers.reset()`/`staff.reset()`/`event_log.reset()`の直後に
`_checkout_queue.clear()`を呼んでいるが、`load_state()`は同じ6つの
resetを呼びながら**`_checkout_queue.clear()`だけが欠落していた**。

`_checkout_queue`はレジ待ち行列(客のID文字列のFIFO配列、タスク#36)。
セーブ時点で2人目の客がこの待ち行列に入っていた場合、ロード後も
その客IDが`_checkout_queue`に残ったままになる。しかし`customers.
reset()`は既に実際の客レコードを全て破棄済みのため、次に`step()`/
`tick_idle_for_demand()`経由で`_dispatch_checkout_queue()`が呼ばれた
際、`_checkout_queue.pop_front()`で取り出した古い客IDを
`CustomerRoster.customer(customer_id)`(生の辞書アクセス`customers[
customer_id]`、存在しないキーは`null`を返す)に渡し、その`null`に
対して`customer.phase = "checkout"`を実行しようとしてクラッシュする
——実際にプレイして初めて踏むタイプの、テストでは今まで発見されて
いなかった再現性のあるクラッシュバグである。

## 決定

### `load_state()`に`_checkout_queue.clear()`を追加

`reset()`と全く同じ位置(`staff.reset()`の直後)に1行追加した。これで
両関数のリセット対象が完全に一致する。

## テスト

- `reference_sim`フルスイート739件パス/1件xfail(新規コントラクトテスト
  1件)。`reset()`/`load_state()`両方の本体テキストに`_checkout_queue.
  clear()`が実際に存在することを文字列レベルで検証する。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないためCIで
  検証。バグを実際に再現する新規シナリオを追加:
  - タスク#36の並行客シナリオと同じ手法(同一商品計画を持つ2人の客を
    同時に入店させる)で、2人目の客が実際に`_checkout_queue`に入る
    (待ち行列が空でなくなる)まで進める。
  - その時点で`save_state()`を呼び、新しいシミュレーションインスタンス
    に`load_state()`する。
  - ロード後の`_checkout_queue`が空であることを確認。
  - さらにロード後のシミュレーションを客が全員精算完了するまで進め、
    (修正前なら発生していたはずの)クラッシュなく正常に完走すること
    を確認する——これが本来の回帰テスト。

## 対象ファイル

- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 監査の副産物(このタスクで確認し、問題なしと判断した範囲)

`_checkout_queue`以外にも、`reset()`が触れる全サブシステム
(`layout`/`inventory`/`economy`/`customers`/`staff`/`event_log`)の
`snapshot()`/`restore_snapshot()`実装、`town`(人口・店舗数、実行時に
変更されることがない)、`_player_store_position`/`_rival_stores`
(configから固定、実行時不変)を確認したが、他に同種のギャップは
見つからなかった。`economy_state.gd`の`restore_snapshot()`は
`_settled_customer_ids`を意図的にクリアする理由を既に明記しており
(客ロースターが復元されないため、IDの使い回しで新規客が精算不能に
ならないようにするため)、模範的な実装だった。

## 明示的に対象外

- 客・店員の途中経路や店員スキル成長など、既にコード内コメントで
  「意図的に未保存」と明記されている既知のギャップの解消は今回の対象外
  (別途、タスク#48の決定0117が参照する形で扱われるべき将来の課題)。
- `reference_sim`側への同等ロジックの移植は行っていない——
  `reference_sim`にはこのクライアントの`_checkout_queue`に相当する
  リアルタイム待ち行列の実行モデル自体が存在しない。
