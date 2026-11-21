# CSRM-004: レビューメモ項目3・12の解消（force_eject と cancel_customer の整合性）

- 引き継ぎID: CSRM-004
- 版番号: 1
- 優先順位: 3（CSRM-003 は文書運用で軽微なため、実質的には本指示書を先に実施してよい）
- 対象リポジトリ: `s1-1985/Covenience-store-remake`
- 実装対象ブランチ: `chatgpt/ps-ui-touch-audit-20261119`
- 基準コミット: `9dfa80b98bf584b90d2a5a53b46ad67dc49838af`
- 状態: ready（期待動作を本指示書で定義済み。原作の解釈・数値は不要）

## 目的と背景

Muse の解析 A-2（`docs/muse/analysis/2026-11-21-simultaneous-service-queue.md` §5、`muse/analysis` ブランチ）で、`docs/handoff/chatgpt-review-notes.md` の未解決メモ項目のうち、レジまわりの2件が現行コードでも残存していることをコード読み取りで確定した。

- **項目3**: `CustomerLifecycleHarness.force_eject()` がチェックアウト側の接客割当（`CheckoutStationRuntime._active_by_staff`）を解放しない。接客中の客を eject すると、店員のスロットと CHECKOUT タスクが占有されたままになる。
- **項目12**: `CheckoutStationRuntime.cancel_customer()` が `CustomerSession` の状態を変更しないため、次の `refresh_waiting()` で取り消した客が待ち列へ復活する。refresh は通常運用で頻繁に呼ばれるため、取り消しが静かに無効化される。

どちらもテストが存在せず、`test_staff_checkout.py` が固定しているのは「待ち客のみの eject」という狭い範囲だけである。本指示書は、推測で結果（ペナルティ等）を発明せずに、ハーネス間の整合性だけを是正する。

## 根拠資料と確度

- `docs/muse/analysis/2026-11-21-simultaneous-service-queue.md` §5（Muse が基準コミットのコードを精読して確定）
- `docs/handoff/chatgpt-review-notes.md` メモ項目3・項目12（項目12は「補足」とされているが、挙動としては項目3と対になる欠陥）
- 現行コード: `reference_sim/conveni_sim/customer.py`（`force_eject`）、`reference_sim/conveni_sim/checkout.py`（`cancel_customer`、`refresh_waiting`、`finish_service`）、`reference_sim/conveni_sim/store_runtime.py`（`finish_checkout_sale` の精算→完了の順序）

## 対象ファイル

- `reference_sim/conveni_sim/customer.py`、`reference_sim/conveni_sim/checkout.py`（主たる修正箇所。どちらに結合を持たせるかは具体的な変更内容の範囲で選んでよい）
- 必要に応じて `reference_sim/conveni_sim/store_runtime.py`、`reference_sim/conveni_sim/store_step.py`（合成経路の調整が必要な場合）
- テスト: `reference_sim/tests/test_known_issues.py` への回帰テスト追加、または関連テストファイル（`test_staff_checkout.py` 等）
- 新規作成: `docs/implementation/CSRM-004.md`（実装報告）、決定記録（新規番号 0239 以降）
- 追記: `PROJECT_MEMORY.md` 第19節（末尾チェックポイントログ）

## 具体的な変更内容

### 項目3（force_eject と接客割当）

1. 接客中（`_active_by_staff` に載っている）客が `force_eject` された場合、その接客割当が解放され、担当店員が roster 上も IDLE へ戻るようにする。待ち客のみの場合の既存挙動（refresh で待ち列から外れる）は変えない。
2. eject 済みの客について、後から時間完了経路（`finish_checkout_sale` → `finish_service`）が走っても、**精算だけが済んで例外が上がる部分適用にならない** ようにする。具体的な作法（完了経路側で eject 済みを検出して精算を止める／eject 側で完了不能を保証する等）は実装側で選び、決定記録に理由を書くこと。eject された客のバスケットが精算されることは、どの経路でも起きてはならない。
3. eject に伴うペナルティ・売上・評価への影響は、既存の確定済み仕様（断念・退店の原条件）がある範囲でのみ扱い、新たに発明しない。不明な範囲は「推測しない」現行方針（`cancel_customer` の docstring 等）を維持する。

### 項目12（cancel_customer と refresh の整合性）

4. `cancel_customer()` で取り消した客が、その後の `refresh_waiting()` で待ち列へ復活しないようにする。セッション状態側に取り消しを反映させるか、チェックアウト側で取り消し済みを保持するかは実装側で選ぶが、**「取り消しは呼び出し側の意図として永続する」** ことを完了条件とする。
5. 取り消し後に同じ客が正規の経路で再度待ち列へ入る場合（状態遷移を伴う再入場）まで妨げてはならない。再入場の可否はセッション状態の遷移で判断できる設計にすること。

### 共通

6. 項目3・12それぞれについて回帰テストを追加する（`test_known_issues.py` の既存項目と同じ流儀で、メモ項目番号をテスト名または docstring に明記する）。
7. Godot 側（`game/scripts/domain/` の客状態・接客まわり）に同型の問題（退店・取消と接客割当の不整合）がないかを確認し、結果を実装報告に記録する。Godot 側の修正が必要と判明した場合は、その範囲も本指示書に含めるが、判断根拠を決定記録に残すこと。

## スコープ外

- 原作の解釈・数値が必要な変更（接客時間式、割込み閾値、断念条件の変更など）
- メモ項目3・12以外の未解決メモ項目（7、9、15〜18、22の要判断分など）の解消
- 行列幾何・客スロット同一性に関する変更（原作側が未解明のため対象外）

## 完了条件

- [ ] 入力例と期待結果（項目3）: 接客中の客へ `force_eject` を実行する。期待結果: 当該店員の接客割当が解放され roster タスクが IDLE に戻り、その後の `refresh_waiting()`・時間完了経路でも精算が発生しない
- [ ] 入力例と期待結果（項目12）: 待ち客へ `cancel_customer()` を実行し、その後 `refresh_waiting()` を複数回呼ぶ。期待結果: その客は待ち列へ戻らない。再入場はセッション状態の正規遷移を伴う場合に限る
- [ ] 項目3・12の回帰テストが追加され、Python 全テストが成功する（CSRM-002 が未実施の場合は、既存基線＝786成功／既存2失敗／想定失敗1 からの悪化がないこと。失敗が残る場合はテスト名を実装報告に列挙）
- [ ] 待ち客のみの eject に関する既存テスト（`test_staff_checkout.py`）を含む関連テスト群が引き続き成功する
- [ ] Godot 側の同型問題の確認結果が実装報告に記録されている
- [ ] 実装報告 `docs/implementation/CSRM-004.md` と決定記録が作成され、PROJECT_MEMORY 第19節（末尾ログ）へ追記されている

## 必須のテスト・ビルド・回帰確認

- Python: `reference_sim` の全テスト（着手前・完了後）
- Godot: 変更が Godot 側に及ぶ場合のみ、関連 smoke と広域 `headless_smoke`（既存失敗の扱いは CSRM-002 と同じ）
- APK ビルドは本指示書では必須としない

## 既知のテスト失敗（基準コミット時点）

- Python: 789件中 786成功／既存2失敗（テスト名は未記録）／想定失敗1（メモ項目11。CSRM-002 の対象）
- 全体 headless: 旧町パネル寸法条件で失敗（CSRM-002 の対象）
- 本指示書の作業でこれらを解消する必要はないが、悪化させないこと

## 依存する指示書

- なし。CSRM-001〜003 と独立。ただし CSRM-002 と同時期に実施する場合は、テスト基線の記録が混ざらないよう、着手順と各時点の失敗一覧を実装報告で区別すること。

## ユーザー判断が必要な項目

- なし。
