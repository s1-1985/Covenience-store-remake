# ChatGPTへの申し送りメモ

Claude Codeによるコードレビューで気づいた事項を、ChatGPTに渡すためにここへ溜めていく。
運用: 新しい気づきは `## 未対応` の下に追記する。ChatGPT側で対応されたら `## 対応済み` に移動し、対応したPR/コミットを記載する。単発のドキュメントではなく、このファイル自体を都度更新していく。

各項目は「事実として確認したこと」と「推測・要確認事項」を分けて書く。

---

## 未対応

### 1. beginnerシナリオの初期資産2億円の証拠レベルがコードとドキュメントで矛盾している

- 対象: `reference_sim/conveni_sim/baseline_data.py` の `SCENARIOS`(`beginner`行)
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

- 対象: `reference_sim/conveni_sim/checkout.py` の `begin_service`(97-99行付近)
- 事実: ガードは次の1条件のみ。

  ```python
  if staff_state.task is StaffTask.CHECKOUT and staff_state.target_id not in (None, self.fixture_id):
      raise ValueError("staff member is already assigned to another checkout")
  ```

  staffの現在のタスクが `StaffTask.REPLENISH` や `StaffTask.CLEAN` であっても、このガードは素通りし、`self.staff.assign_task(staff_id, StaffTask.CHECKOUT, ...)` が呼ばれてタスクが無条件に上書きされる。
- 失敗シナリオ: `roster.assign_task("s1", StaffTask.REPLENISH, target_id="shelf-A")` した直後に `checkout.begin_service("s1", "c1")` を呼ぶと、s1のタスクはCHECKOUTに上書きされ、REPLENISH中だったという記録が失われる。`reference_sim/tests/test_staff_checkout.py` にはこの組み合わせ(REPLENISHにアサイン済みのstaffへのbegin_service呼び出し)を検証するテストが無い。
- 推測: 「CHECKOUT以外のタスク中はチェックしない」のが意図的な設計(呼び出し側の責務)なのか、単なる考慮漏れなのかは、設計者の意図を確認しないと判断できない。

### 3. `force_eject` が checkout の `_active_by_staff` を解放しない

- 対象: `reference_sim/conveni_sim/customer.py` の `force_eject`(165-174行)と `reference_sim/conveni_sim/checkout.py` の `_active_by_staff`
- 事実: `force_eject` は顧客セッションを `EJECTING` にするだけで、`CheckoutStationRuntime._active_by_staff` を経由した解放は行わない。もしその顧客が既にstaffにチェックアウト対応されている最中(`_active_by_staff`に登録済み)にforce_ejectされた場合、`checkout.finish_service(staff_id)` が呼ばれない限りstaffは `task=CHECKOUT` のまま解放されない。`checkout.cancel_customer(customer_id)` を呼べば解放できるが、`force_eject`からは自動的に呼ばれない。
- 推測: `store_runtime.py` 経由で顧客を退店させるヘルパーが今のところ無いため、「force_ejectする側が対象のcheckoutを把握してcancel_customerも呼ぶ」ことをどう保証するかは未設計。

### 4. 証拠レベル(Evidence Level)の定義が3箇所でバラバラ

- 事実として確認した3つの出典:
  1. `PROJECT_MEMORY.md` 15節: `CONFIRMED-OFFICIAL` / `CONFIRMED-VISUAL` / `CONFIRMED-COMMUNITY` / `PROVISIONAL` / `HYPOTHESIS` の5値のみを正式ラベルと定めている。
  2. `reference_sim/conveni_sim/models.py` の `EvidenceLevel` enum: `CONFIRMED_OFFICIAL` / `CONFIRMED_VISUAL` / `CONFIRMED_COMMUNITY` / `STRONG_INFERENCE` / `PROVISIONAL` / `HYPOTHESIS` / `REMAKE_BALANCED_DEFAULT` の7値。`STRONG_INFERENCE` と `REMAKE_BALANCED_DEFAULT` は `PROJECT_MEMORY.md` に記載がない。
  3. `docs/research/` 配下のMarkdown内の自由記述: `git grep` で調べた限り、`CONFIRMED-COMMUNITY-FIRST-TITLE` `CORROBORATED-FIRST-TITLE` `STRONG-CORROBORATED` `PROVISIONAL-HIGH-VALUE` など、上記のどちらにも属さない独自の拡張表記が70件以上のファイルにわたって使われている。
- これは今回のセッションで新たに気づいた点ではなく、以前(PR #27のレビュー時)にも確認済みの実態だが、今回コード側(`models.py`)にも独自定義があることを追加で確認した。
- 推測: `models.py`の`EvidenceLevel`(コードで実際にデータへ付与される正式な値)を正とし、`PROJECT_MEMORY.md`側を追従させて更新するのが筋が良さそうだが、これは設計判断であり私が決めることではない。

---

## 対応済み

(まだ無し)
