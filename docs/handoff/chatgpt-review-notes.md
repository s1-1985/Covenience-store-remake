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

### 10. グリッドから撤去された什器から商品が売れる

- 対象コミット: `554d78d` / `reference_sim/conveni_sim/store_grid.py` の `remove_fixture`(213-217行)
- 再現テスト: `tests/test_known_issues.py::test_a_fixture_removed_from_the_grid_cannot_still_sell_goods`
- 事実(実機で確認): 顧客が棚へ向かっている途中で `grid.remove_fixture("shelf")` を呼ぶと、`grid.placements` は空になるにもかかわらず、顧客はその棚の元interaction cellに到着して `at_merchandise` になる。そこから `customer_pick_and_continue` が成功し、在庫が 5 → 4 に減り、`settle_self_service` で売上120円が計上され、現金が 1,000,000 → 1,000,120 になった。
- 原因(コードから読み取れる範囲): `remove_fixture` は `_placements` から消すだけで、(a) その什器を目標にしている `TrafficAgent`、(b) その什器に紐づく在庫スロット、(c) 進行中の顧客セッションの `current_merchandise_fixture_id` のいずれとも連動していない。`traffic.tick()` は既存の `path` を消費し続けるため、経路の再計算が起きず「存在しない什器に到着」する。
- 補足: `remove_fixture` は現状どこからも呼ばれておらず(カバレッジ0%)、今すぐの実害はない。ただし模様替え/什器撤去を実装した時点で表面化する。
- 要判断: 撤去時に在庫スロットも消すのか、顧客を強制退店させるのか、そもそも顧客がいる間は撤去を拒否するのかは設計判断。テストは「撤去後の購入は拒否されるべき」という最小限の期待だけを書いてある。

### 11. `StoreStepOrchestrator.step()` が途中で例外を投げると、時計だけ進んだ状態が残る

- 対象コミット: `554d78d` / `reference_sim/conveni_sim/store_step.py` の `step`(88-149行)
- 再現テスト: `tests/test_known_issues.py::test_a_failing_purchase_phase_does_not_leave_the_clock_advanced`
- 事実(実機で確認): `step()` は最初に `advance_game_minutes` を実行し、その後に需要評価・traffic・購入評価・staffタスク・チェックアウト選択を順に行う。購入評価で例外が出ると(例: `CHECKOUT_REQUIRED` のofferなのに顧客に `checkout_fixture_id` が無い)、時計は既に進んでいるのに後段のstaffタスク/チェックアウト選択フェーズは実行されない。実測で `0 → 1` 分進んだ状態で `ValueError` が送出された。
- 影響: 呼び出し側が同じ `step(1)` をリトライすると、ゲーム内時間が二重に進む。複数顧客がいる場合、先に評価された顧客だけ購入が確定した中途半端な状態も残る。
- 要判断: 時計の前進を最後に回すのか、フェーズ単位で例外を捕捉して結果に含めるのか、`step()` 全体をアトミックにするのかは設計判断。テストは「例外時に時計が進んでいない」という一案だけを期待として書いてある。

### 12. `cancel_customer` は顧客の状態を変えないため、次の `refresh_waiting()` で取り消される(補足)

- 対象コミット: `554d78d` / `reference_sim/conveni_sim/checkout.py` の `cancel_customer`(127-142行)
- 事実(実機で確認): `WAITING_CHECKOUT` のままの顧客に対して `cancel_customer` を呼んで待ち行列から外しても、次に `refresh_waiting()` が走ると同じ顧客が再び待ち行列に入る。`cancel_customer` はセッション状態を変更しないため。
- これはバグとは限らない: docstringは "Detach an ejected/abandoned customer" と書いており、`force_eject`(状態が `EJECTING` になる)と併用する前提なら正しく動く。単独で呼ぶと無効、という API 上の注意点として記録する。
- 参考: `cancel_customer` はカバレッジ0%(テストが1件も無い)。項目3の `force_eject` との連携を整理する際に、併せてテストを追加すると良い。

---

### 13. 撤去されたチェックアウト什器でも会計が完了する(項目10の修正漏れ)

- 対象コミット: `016cc29` / `reference_sim/conveni_sim/store_runtime.py`
- 再現テスト: `tests/test_known_issues.py::test_a_removed_checkout_fixture_cannot_still_complete_a_sale`
- 事実(実機で確認): `100282f "fix: reject purchases from removed fixtures"` は**商品什器からの購入**を塞いだが、**チェックアウト什器の撤去**は塞いでいない。レジ待ちの顧客がいる状態で `grid.remove_fixture("checkout")` した後も、`begin_checkout_service` と `finish_checkout_sale` が両方成功し、売上120円が計上され現金が 5,000,000 → 5,000,120 になった。`grid.placements` には `shelf` しか残っていない。
- `_require_placed_fixture` というヘルパーが新設されたが、チェックアウト系のメソッドからは呼ばれていない。項目10と同じクラスの問題なので、同じ方針で塞ぐのが自然。

### 14. 未配置のチェックアウト什器を指定して顧客を追加できる

- 対象コミット: `016cc29` / `reference_sim/conveni_sim/store_runtime.py` の `add_customer`
- 再現テスト: `tests/test_known_issues.py::test_a_customer_cannot_be_routed_to_an_unplaced_checkout`
- 事実(実機で確認): `merchandise_fixture_ids=("ghost-shelf",)` は `KeyError('ghost-shelf')` で正しく弾かれるのに、`checkout_fixture_id="checkout"`(既に撤去済み)は素通りして顧客が作成される。その顧客は存在しないレジへ向かうことになる。
- 商品什器側と検査が非対称なので、同じ検査を `checkout_fixture_id` にも適用するのが自然。

### 15. マガジンイベントのスキル解決が base cap を無視する(要判断)

- 対象コミット: `016cc29` / `reference_sim/conveni_sim/manager_magazine_event.py` の `resolve_opportunity`(113-115行)
- 事実(実機で確認): `base_skill_caps={StaffSkill.SERVICE: 10}` の店長に対し、`after_skills={StaffSkill.SERVICE: 99}` で解決でき、値が99になる。`manager.runtime_skills[skill] = value` と直接書き込んでおり cap 検査が無い。
- 対比: `StoreStaffRoster.resolve_growth_opportunity` は「normal work growth cannot exceed the known base skill cap」として cap 超えを拒否する。
- **要判断**: 「通常の労働成長(normal work growth)」という限定表現があるので、イベント成長は意図的に cap を超えられる設計かもしれない。その場合はdocstringに明示した方がよい。意図していないならガードが必要。私にはどちらか判断できないため、xfailテストは書いていない。

### 16. マガジンイベントの細かい注意点2件(補足)

- 対象コミット: `016cc29` / `manager_magazine_event.py`
- **店長解雇後の解決**: イベント記録後に `remove_staff("mgr")` してから `resolve_opportunity` を呼ぶと、生の `KeyError('mgr')` が出る。同クラスの `opportunity()` は `KeyError(f"unknown magazine opportunity sequence: ...")` と説明的なメッセージを付けているので、ここだけ不親切。
- **店長交代後の解決**: イベント記録後に `set_manager` で別の店長に変えてから解決すると、**記録時点の店長**のスキルが更新される(現店長ではない)。イベント発生時の人物に適用するのは妥当に見えるが、意図の確認価値はある。

### 17. 誘致(inducement)配置セッションの重複(補足)

- 対象コミット: `016cc29` / `reference_sim/conveni_sim/inducement.py`
- 事実(実機で確認): 同じ施設に対して `InducementPlacementSession` を複数同時に生成でき、その都度 aid が現金から引かれる(400,000円の施設で2セッション作ると800,000円減る)。両方 `cancel()` すれば残高は元に戻ることは確認済み。
- 現状 `confirm()` に相当する機能が無く `cancel()` のみなので、セッションを放置すると現金が引かれたままになる。これはdocstringに明示されている想定内の状態。
- 「1施設1セッション」の制約を課すかどうかは設計判断。配置確定を実装する際に併せて整理するのが自然。

---

## 検証して問題が無かった領域(`554d78d` 時点)

同じ場所を何度も調べ直さないための記録。以下は実際にコードを走らせて確認し、**問題が見つからなかった**。

- **什器の回転とinteraction side**: `interaction_side` 4方向 × `rotation_quarter_turns` 0..3 の全16通りで、interaction cellが回転後の正しい面に生成されることを確認。
- **すれ違い衝突**: 2エージェントが互いの位置へ同時に移動しようとするケースで、すり抜けずに両方ブロックされることを確認。
- **占有されたゴール**: 目標セルが他エージェントに占有されている場合、`ARRIVED` にならず `blocked` になることを確認。
- **金額計算**: 価格不明(`None`)の明細が0円として集計されないこと、`exact_total_yen`/`cash_is_exact` が正しく `None`/`False` に伝播すること、10^15規模の整数でも誤差が出ないこと(Pythonの任意精度整数)を確認。
- **決済ガード**: 空バスケットの決済、二重決済、決済済みバスケットへの追加が、いずれも `ValueError` で拒否されることを確認。
- **深夜跨ぎの営業時間**: `OperatingHours.from_hm(20,0,4,0)` が 19:59=閉、20:00=開、0:00=開、3:59=開、4:00=閉 と正しく判定することを確認。
- **`SubdayClock` の日跨ぎ**: 23:59+1分で `days_crossed=1`、`minute_of_day` が0に戻ること、3日分進めて `days_crossed=3` になることを確認。

### ランダム操作によるファジング(`65ca28c` 時点、新規バグ0件)

不変条件を定義してランダムな操作列を大量に流す方式で4ラウンド実施し、**違反は1件も出なかった**。
検証済みの不変条件と規模:

| ラウンド | 規模 | 内容 | 結果 |
|---|---|---|---|
| 1 | 400シード × 180ステップ | 顧客追加/tick/購入/チェックアウト/決済/補充をランダム実行し、毎ステップ後に8つの不変条件を検査 | 違反0 |
| 2 | 300シード × 200ステップ | **事前条件を満たした操作のみ**を実行し、例外を握りつぶさず記録(正当な拒否と区別するため)。staffタスク・清掃・臨時休業・天候変更も含む | 例外0 |
| 3 | 150シード × ゲーム内14ヶ月 | 日跨ぎ・月跨ぎの長期カレンダーループ、プロモーション発火、日次決算、台帳整合性 | 違反0 |
| 4 | 400シード | 観測タイムラインの時系列制約とreducer、スタミナ/成長機会の状態機械 | 違反0 |

検証した不変条件:

1. 2エージェントが同じセルを占有しない
2. 在庫が `0 <= units <= capacity` を外れない
3. 台帳残高が「初期額 + 既知の入金 - 既知の出金」と常に一致する
4. `next_merchandise_index` と `interacted_fixture_ids` が計画した巡回数を超えない
5. チェックアウトの同時サービス数が `simultaneous_staff_capacity` を超えない
6. 同一顧客が2つのチェックアウトで同時にサービスされない
7. `EXITED`/`EJECTED` に入った顧客がそこから戻らない
8. 決済済みバスケットの明細数が後から変わらない
9. 月サンプルが必ず1..4日、平日3/休日1で構成される
10. 月が正しく繰り上がり、年を跨ぐ
11. スタミナが0..maxを外れない、`RESTING` なら `task=REST`、スタミナ0で `AVAILABLE` にならない
12. 成長機会の解決がスキルを減らさず、base capを超えない

この12項目は `reference_sim/tests/test_invariants.py` に**回帰テストとして常設**した(シード固定・1秒未満)。
今後 `conveni_sim/` を変更したときに不変条件が壊れれば、seedとstep付きで即座に失敗する。

**結論**: 既知の未対応項目を除けば、ランダム操作で検出できる範囲の状態不整合は残っていない。次に掘るなら、ファジングで扱っていない領域(未使用の `remove_fixture` 系、`store_step` の統合フロー、外部ポリシーの実装後)が候補。

### テストカバレッジ(`554d78d` 時点)

`coverage` で計測した結果、`conveni_sim/` 全体で **92%**(2740文中216未到達)。カバレッジが低い順:

| モジュール | カバレッジ | 未到達の主な内容 |
|---|---|---|
| `checkout.py` | 79% | `cancel_customer` 全体(項目12)、各種ガードのエラーパス |
| `store_grid.py` | 86% | `remove_fixture`(項目10)、配置バリデーションのエラーパス |
| `customer_share.py` | 88% | 入力バリデーションのエラーパス |
| `promotion.py` | 89% | 項目5/6の周辺 |

未到達行の多くは「不正な入力を弾くraise文」で、これ自体は異常系テストが無いだけ。ただし `cancel_customer` と `remove_fixture` は**機能まるごと未テスト**であり、実際にその2つから項目10・12が見つかった。

---

## 対応済み

| 項目 | 内容 | 対応コミット |
|---|---|---|
| 2 | `begin_service` が他作業中のstaffを黙って奪う | `65ca28c` |
| 5 | `apply_promotion` に多重適用ガードが無い | `65ca28c` |
| 6 | `apply_promotion` が未登録店舗IDで部分適用 | `65ca28c` |
| 10 | 撤去された什器から商品が売れる(**商品什器のみ**。チェックアウト側は項目13として未対応) | `100282f` |

対応済み項目の再現テストは `@unittest.expectedFailure` が外され、通常テストとして常時実行されている。
`016cc29` 時点で新しく追加された `apply_confirmed_triggered_promotion` についても、
未登録店舗IDでの部分適用が無いこと・同一プロモーションの二重課金が無いことを実機で確認済み(いずれも正しくガードされている)。
