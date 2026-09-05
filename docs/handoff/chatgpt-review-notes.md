# ChatGPTへの申し送りメモ

Claude Codeによるコードレビューで気づいた事項を、ChatGPTに渡すためにここへ溜めていく。
運用: 新しい気づきは `## 未対応` の下に追記する。ChatGPT側で対応されたら `## 対応済み` に移動し、対応したPR/コミットを記載する。単発のドキュメントではなく、このファイル自体を都度更新していく。

各項目は「事実として確認したこと」と「推測・要確認事項」を分けて書く。
指摘には必ず**対象コミットSHA**を書く(コードが動くので、SHAが無いと指摘が古いか判定できない)。

実行可能な再現テストは `reference_sim/tests/test_known_issues.py` に `xfail` として置いてある。
修正すると XPASS に変わるので、`pytest -q -rxX` で直ったことが機械的に分かる。
分担ルールは `docs/handoff/roles-and-workflow.md` を参照。

---

## 未対応

### 1. beginnerシナリオの初期資産2億円の証拠レベルがコードとドキュメントで矛盾している

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/baseline_data.py` の `SCENARIOS`(193行)。`15222a1` 時点から変化がないことを確認済み。
- 事実: `baseline_data.py` は次のように定義している。

  ```python
  ScenarioDefinition(
      "beginner",
      EvidenceValue(200_000_000, EvidenceLevel.CONFIRMED_VISUAL, "Official/current PS screenshot"),
      ...
  )
  ```

  つまりコードは「初級開始資産2億円」の証拠レベルを `CONFIRMED_VISUAL`(画面や公式資料で直接確認済み)として記録している。

- 一方、同じ数値を扱う `docs/research/ui-consistency-audit-2026-09-05.md`(PR #27でマージ済み)は、初級2億円の証拠レベルを `CORROBORATED-FIRST-TITLE`(複数のコミュニティ資料の相互確認。visual確認ではない)としている。さらに同ドキュメントは、実際に確認できる公式スクリーンショット(gavas.jpの画像)に写っている所持金は **180,000,000円** であり、200,000,000円ではないと明記し、「このスクリーンショットを根拠に `starting_cash = 180_000_000` としてはいけない」という研究ルールまで書いている。
- `intermediate`/`advanced`の1.5億円は同じ調査から来ているはずだが、`baseline_data.py`側では `EvidenceLevel.CONFIRMED_COMMUNITY` になっており、`beginner`だけ `CONFIRMED_VISUAL` になっている。この非対称性も不自然。
- 推測: おそらく「2億円」という数値自体はコミュニティ資料の相互確認(CORROBORATED)止まりで、`CONFIRMED_VISUAL`への格上げは誤りではないか。あるいは、私が把握していない別の公式スクリーンショット根拠が実在するのかもしれない(未検証)。
- 確認していないこと: `"Official/current PS screenshot"` というnoteが具体的にどの画像を指すのか、その画像に本当に2億円という数値が写っているのかは、URLが示されておらず私は検証できていない。

### 2. `CheckoutStationRuntime.begin_service` が、他タスク中のstaffへの割当てを防いでいない

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/checkout.py` の `begin_service`(97-99行)
- 再現テスト: `tests/test_known_issues.py::test_begin_service_must_not_silently_steal_a_replenishing_staff`
- 事実: ガードは次の1条件のみ。

  ```python
  if staff_state.task is StaffTask.CHECKOUT and staff_state.target_id not in (None, self.fixture_id):
      raise ValueError("staff member is already assigned to another checkout")
  ```

  staffの現在のタスクが `StaffTask.REPLENISH` や `StaffTask.CLEAN` であっても、このガードは素通りし、`self.staff.assign_task(staff_id, StaffTask.CHECKOUT, ...)` が呼ばれてタスクが無条件に上書きされる。
- 実機で再現済み: `assign_task("s1", REPLENISH, target_id="bread-slot")` の直後に `begin_checkout_service("checkout", staff_id="s1", customer_id="c1")` を呼ぶと、例外は出ず `task=replenish target=bread-slot` → `task=checkout target=checkout` に書き換わる。
- **注意**: `0d30789 "fix: lock active checkout staff from generic reassignment"` はこの問題とは**逆方向**の修正。あちらは「一般のタスクポリシーがCHECKOUT中のstaffを奪う」のを `store_step.py` 側で防ぐもので、`begin_service` が他作業中のstaffを奪う経路は塞がれていない。
- 推測: 「CHECKOUT以外のタスク中はチェックしない」のが意図的な設計(呼び出し側の責務)なのか考慮漏れなのかは、設計意図を知る側でないと判断できない。

### 3. `force_eject` が checkout の `_active_by_staff` を解放しない

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/customer.py` の `force_eject`(182-191行)と `checkout.py` の `_active_by_staff`
- 事実(実機で確認): チェックアウト対応中の顧客を `force_eject` すると、顧客は `ejecting` になるが `checkout.customer_being_served_by("s1")` はその顧客を返し続け、staffは `task=checkout` のまま残る。`force_eject` からは `cancel_customer` が呼ばれない。
- **前回メモの訂正**: 前回「permanently locked(永久にロック)」と書いたが、これは不正確だった。実際には `finish_service(staff_id)` を呼ぶと `ValueError("active checkout customer is no longer waiting")` を送出しつつ、その副作用で `release_to_idle` が走りstaffは解放される(`task=idle` になることを確認済み)。したがって「永久ロック」ではなく「例外と引き換えにしか解放されない」が正しい。
- 推測: 例外を出しながら副作用で状態を戻すAPIは意図的とは考えにくいが、`force_eject` 側で `cancel_customer` を呼ぶべきか、`finish_service` の異常系を整理すべきかは設計判断。xfailテストは書いていない(どちらの挙動を「正しい」とするか私には決められないため)。

### 4. `CheckoutServiceTimingEvaluation.sale` の型注釈と実際の値が違う

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/checkout_service_timing.py`(42行の注釈、127-132行の実装)
- 再現テスト: `tests/test_known_issues.py::test_checkout_timing_completion_returns_the_declared_sale_type`
- 事実(実機で確認): `sale` の注釈は `Optional[CheckoutSaleResult]` で `CheckoutSaleResult` をimportしているが、`evaluate_staff` が代入するのは `runtime.finish_checkout_sale()` の戻り値、すなわち `CheckoutSaleCompletion`。実行時の型は `CheckoutSaleCompletion` で、`isinstance(sale, CheckoutSaleResult)` は `False`。
- 影響: 注釈を信じて `evaluation.sale.service_started` を読むと `AttributeError: 'CheckoutSaleCompletion' object has no attribute 'service_started'`(実際に発生することを確認)。型チェッカを導入すれば静的にも検出される。
- 要判断: 注釈を `CheckoutSaleCompletion` に直すのか、`service_started` を保持して `CheckoutSaleResult` を返すよう実装を直すのかは設計判断。

### 5. `apply_promotion` に多重適用ガードが無い

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/promotion.py` の `apply_promotion`(291-323行)
- 再現テスト: `tests/test_known_issues.py::test_promotion_cannot_be_applied_twice`
- 事実(実機で確認): 発火済み(`fired=True`)の同じ `ScheduledPromotion` を `apply_promotion` に2回渡すと、人気度が2回加算される(direct_mail gain=12 で 10 → 22 → 34)。`pop_due` は `fired` を見て一度しか返さないが、`apply_promotion` 自体には「適用済み」の概念が無い。
- 同じファイル/近隣クラスの `StorePopularityRuntime.resolve_decay_opportunity` と `StoreStaffRoster.resolve_growth_opportunity` は「already resolved」ガードを持っており、`apply_promotion` だけ一貫性が無い。

### 6. `apply_promotion` が未登録店舗IDで部分適用のまま中断する

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/promotion.py` の `apply_promotion`(304-318行)
- 再現テスト: `tests/test_known_issues.py::test_promotion_with_unknown_store_does_not_partially_apply`
- 事実(実機で確認): `target_store_ids=["store-1", "ghost-store"]` を渡すと、`store-1` の人気度を加算した後に `ghost-store` で生の `KeyError` が出る。既に加算された `store-1` はロールバックされない(10 → 60 のまま)。
- 補足: 同クラスの他メソッド(`set_rating`, `record_decay_opportunity`)は未登録IDに対し `KeyError(f"unknown store id: ...")` と明示メッセージを出しており、ここだけ生のKeyError。事前検証してから適用するのが自然。

### 7. 臨時休業を解除しても顧客独占率が0のまま、再計算トリガーも立たない

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/store_runtime.py` の `set_temporary_closure`(107-109行)と `advance_game_minutes`(111-121行)
- 事実(実機で確認): 臨時休業中に日付をまたぐと `apply_share(0, ...)` が呼ばれ、share=0 かつ pending理由がクリアされる。その後 `set_temporary_closure(False)` で再開しても、`store_open=True` に戻る一方で share は 0 のまま、`recalculation_pending` も `False` のまま。次に日付をまたぐまで0が続く。
- **要判断**: これはバグとは限らない。`customer_share.py` のdocstringは「顧客独占率は日付変更時に再計算される」という原作挙動を根拠にしており、その通りなら「再開しても翌日まで0」は原作に忠実。ただし `set_temporary_closure(False)` が何のトリガーも立てない点が意図的かは読み取れない。原作挙動を知る側の判断が必要なため、xfailテストは書いていない。

### 8. シナリオのソースURLに壊れたWikiページ名が3箇所ある

- 対象コミット: `0d30789` / `reference_sim/conveni_sim/baseline_data.py` の `SCENARIOS`(193-195行)
- 再現テスト: `tests/test_known_issues.py::test_scenario_source_urls_are_not_typo_corrupted`
- 事実(パーセントエンコードをデコードして確認): `baseline_data.py` 内のWikiページ名は4種類あり、うち3箇所が `ゲームード攻略` になっている。正しくは `ゲームモード攻略`(「モ」が欠落)。
  - `ゲームモード攻略`(正しい): 3箇所
  - `ゲームード攻略`(壊れている): 3箇所 — `intermediate.objective`、`advanced.initial_cash_yen`、`advanced.objective`
- `beginner` と `intermediate.initial_cash_yen` は正しい方を使っているので、同じ資料を指すはずのURLが2種類混在している状態。
- 判断の余地は無いと考えるが、修正は `conveni_sim/` 配下なのでChatGPT側で行う。

### 9. 証拠レベル(Evidence Level)の定義が3箇所でバラバラ

- 対象コミット: `0d30789`(項目内容は `15222a1` 時点から変化なしを確認済み)
- 事実として確認した3つの出典:
  1. `PROJECT_MEMORY.md` 15節: `CONFIRMED-OFFICIAL` / `CONFIRMED-VISUAL` / `CONFIRMED-COMMUNITY` / `PROVISIONAL` / `HYPOTHESIS` の5値のみを正式ラベルと定めている。
  2. `reference_sim/conveni_sim/models.py` の `EvidenceLevel` enum: `CONFIRMED_OFFICIAL` / `CONFIRMED_VISUAL` / `CONFIRMED_COMMUNITY` / `STRONG_INFERENCE` / `PROVISIONAL` / `HYPOTHESIS` / `REMAKE_BALANCED_DEFAULT` の7値。`STRONG_INFERENCE` と `REMAKE_BALANCED_DEFAULT` は `PROJECT_MEMORY.md` に記載がない。
  3. `docs/research/` 配下のMarkdown内の自由記述: `git grep` で調べた限り、`CONFIRMED-COMMUNITY-FIRST-TITLE` `CORROBORATED-FIRST-TITLE` `STRONG-CORROBORATED` `PROVISIONAL-HIGH-VALUE` など、上記のどちらにも属さない独自の拡張表記が70件以上のファイルにわたって使われている。
- これは今回のセッションで新たに気づいた点ではなく、以前(PR #27のレビュー時)にも確認済みの実態だが、今回コード側(`models.py`)にも独自定義があることを追加で確認した。
- 推測: `models.py`の`EvidenceLevel`(コードで実際にデータへ付与される正式な値)を正とし、`PROJECT_MEMORY.md`側を追従させて更新するのが筋が良さそうだが、これは設計判断であり私が決めることではない。

---

## 対応済み

(まだ無し)
