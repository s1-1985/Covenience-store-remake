# 0239 — レジ接客割当と取消の整合性（メモ項目3・12）

## 背景
`docs/handoff/chatgpt-review-notes.md` のメモ項目3・12は、reference_sim のレジまわりで長く未解決だった。項目3: 接客中（`CheckoutStationRuntime._active_by_staff` に載っている）客が `CustomerLifecycleHarness.force_eject()` されても接客割当が解放されず、さらに `StoreRuntimeHarness.finish_checkout_sale()` が精算を適用してから `finish_service()` の例外で止まる部分適用になっていた。項目12: `cancel_customer()` が待ち列と割当を外すだけでセッション状態を変えないため、次の `refresh_waiting()` が WAITING_CHECKOUT のままの客を再登録し、取り消しが静かに無効化されていた。どちらもテストが無かった。解析の確定は `docs/muse/analysis/2026-11-21-simultaneous-service-queue.md` §5（`muse/analysis` ブランチ）、実装指示は CSRM-004 版1。

## 決定
- 結合はチェックアウト側に置く。`refresh_waiting()` の冒頭で、セッションが WAITING_CHECKOUT を離れた接客割当を解放する（`_release_stale_services()`、担当店員は IDLE へ戻す）。待ち客のみの eject が refresh で外れる既存挙動と対称な作法であり、`begin_service()` の容量判定も同じ refresh を経るため、解放された枠はそのまま再利用できる。
- `finish_checkout_sale()` は接客中客の解決前に `checkout.refresh_waiting()` を呼び、eject 済みなら精算前に KeyError で止める。eject された客のバスケットはどの経路でも精算されない。
- 取り消しの永続化はチェックアウト側の取消集合で持ち、セッション状態は変更しない。取消はセッションが WAITING_CHECKOUT に留まる間だけ入列を抑止し、セッションが別状態へ遷移した時点で失効する。再入場の可否はセッション状態の遷移で判断する（CSRM-004 の完了条件）。ペナルティ・売上・評価への影響は従来どおり発明しない。

## 根拠
原作の数値・解釈は不要な整合性の欠陥であり、根拠は現行コードの精読（上記解析 §5）とレビューメモ項目3・12。修正前に再現テスト4件が失敗すること（接客割当の残留、取消の復活、精算の部分適用）を確認し、修正後に全て成功へ転じた。

## 確認
- 回帰テスト: `tests/test_staff_checkout.py` に項目3（接客中 eject の割当解放）と項目12（取消の非復活、到着前 cancel の過剰ブロック防止）を追加、`tests/test_known_issues.py` に項目3（finish_checkout_sale で精算が発生しないこと）を追加。
- Python 全テスト: 793件（着手前基線789件）。790成功／既存2失敗／想定失敗1で、基線からの悪化なし。既存2失敗は今回初めて名前を特定した: `test_game_vertical_slice_contract.GameVerticalSliceContractTests.test_slim_engine_template_keeps_what_the_game_uses` と `test_store_site_is_chosen_freely_with_a_land_price_per_site`（CSRM-002 の対象、そのまま維持）。
- Godot 側の同型確認: `game/scripts/vertical_slice_simulation.gd` の `try_eject_customer()` は待ち客なら `_checkout_queue` から除去し、接客中ならレジ担当を idle へ戻しており、同型の不整合は無い。`_checkout_queue` への登録はフェーズ遷移時の一回限り（`_advance_customer`）で、refresh 式の再登録経路が無いため項目12型の復活も起きない。断念経路 `_program_wait_at_checkout()` も除去と idle 化を対で行う。Godot 側の変更は不要と判断した。

## 範囲外
接客時間式・割込み閾値・断念条件など原作の解釈や数値を要する変更、メモ項目3・12以外の未解決項目、行列幾何と客スロット同一性。APK は作成していない（CSRM-004 では必須とされていない）。実機確認は行っていない。本実装はユーザーの 2026-11-22 の指示による Muse 実装のパイロットであり、マージはユーザーの承認待ちである。
