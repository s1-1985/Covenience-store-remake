# A-2: 同時接客・行列幾何・入力→営業状態境界の照合（2026-11-21）

- 対象リポジトリ: `s1-1985/Covenience-store-remake`
- 実装対象ブランチ: `chatgpt/ps-ui-touch-audit-20261119`
- 基準コミット: `9dfa80b98bf584b90d2a5a53b46ad67dc49838af`
- 方法: GitHub 経由のテキスト読み取りのみ。コード・テストの実行はしていない。本書の「実装の状態」はコードの読み取りによる確認であり、「テスト成功」はリポジトリ内記録の引用。
- 位置づけ: 初回棚卸し §10 のバックログ A-2。最新引継ぎ `docs/handoff/2026-11-21-live-staff-traits.md` の「続き」が指名した監査テーマ（「原状態/同時接客と行列幾何、入力から営業状態への未接続境界を既存解析と照合」）の実施結果。
- 読んだもの: PROJECT_MEMORY §4〜§11・§17、`docs/research/` の checkout-staff-dispatch-evidence-2026-09-05、staff-checkout-task-arbitration-2026-09-06、staff-ai-queue-recovery-and-parameter-damage-2026-09-06、customer-patience-evidence-2026-09-05、customer-abandonment-2026-11-20 README、stockout-refill-2026-11-21 README、`reference_sim/conveni_sim/` の checkout.py・customer.py・store_step.py・store_runtime.py・checkout_selection_policy.py・checkout_service_timing.py・checkout_pre_service_departure.py・checkout_anger_timing.py・staff.py・traffic.py、`game/scripts/domain/` の checkout_timing.gd・customer_state.gd・program_geometry.gd・program_people.gd、テスト test_staff_checkout.py・test_known_issues.py・test_multi_customer_checkout_load.py。
- 未読（残件として明記）: `game/scripts/vertical_slice_simulation.gd`（349KB）内の `_program_wait_at_checkout` と `_advance_customer`。本書の Godot 側の忍耐・断念閾値に関する記述は、この2関数の範囲では未検証。

## 1. 結論の要約

| サブテーマ | 分類 | 要点 |
|---|---|---|
| 同時接客の構造 | 整合（解明済みに反しない） | 原作確定分は「非FIFO」「2人打ちレジの存在」「競合時の片方離脱」まで（いずれもコミュニティ観測レベル）。実装の容量パラメータ化とポリシー差し替え構造は、原作解析側が求めた「容量は設定可能に、式は発明しない」という安全要件に一致 |
| 同時接客の数値（会計時間式・割込み閾値・競合敗北時の滞在時間） | **未解明** | 原作側がすべて UNKNOWN と明記。実装も式を持たずポリシー注入にしている（正しい規律）。ただし Godot 非native経路の仮値2件は §4 の注意あり |
| 行列幾何 | **未解明（原作）／実装は発明なし** | 原作解析が "queue geometry" を Still unknown と宣言。アンカー・間隔・方向・最大長の証拠は存在しない。実装は Python 側に幾何を持たず、Godot 側は復元済み経路探索＋占有から創発させており、間隔定数の発明は見つからなかった |
| 固定客スロット（原20）との同一性 | 検証不足 | 原作に20固定客スロットがあることは前提として記述されるが、全スロットにわたる購入経路の一致は未証明（stockout README が明記） |
| 入力→営業状態の未接続境界 | **実装側の実欠陥2件を特定** | レビューメモ項目3（force_eject が接客中の割当を解放しない）と項目12（cancel_customer が次の refresh で無効化される）が、現行コードでも未修正のまま残存。どちらもテストなし。→ CSRM-004 で指示書化 |
| 待ち断念（abandonment）の原条件 | 解明済み・反映済み（検証は記録ベース） | 原EXE実行による132条件が確定し本体接続済み（customer-abandonment-2026-11-20）。自然発生頻度・実秒待ち時間は測定対象外と明記 |

## 2. 同時接客

### 2.1 原作側の確定範囲

- 会計順序は厳密な FIFO ではない（後着客が先に会計される場合がある）。証拠レベル CONFIRMED-COMMUNITY / B+。ただし「誰を優先するか」の選択式は UNKNOWN（候補: 距離、接触位置、到達セル、内部客ID、レジ向き。いずれも仮説）。
- 2人打ちレジ（1台を2人で打つ形態）が存在する（CONFIRMED-COMMUNITY）。原作解析側の安全要件は「`simultaneous_staff_capacity` を設定可能にし、特定の什器行へ容量を割り当てるのは什器マスター完全復元まで行わない」。
- 複数の店員が同時にレジへ向かうと、片方が休憩室へ戻りしばらく出てこない場合がある。開始した店員の体力がわずかだとその店員もすぐ離れ、レジが無人になる場合がある（CONFIRMED-COMMUNITY / B+）。ただし「必ず戻るか」「滞在時間」「体力の関与」は UNKNOWN。
- 待ち客がいても店員は補充等を優先し、ぎりぎりまでレジへ向かわない（CONFIRMED-COMMUNITY）。割込み閾値（待ち人数・時間）の正確な値は未確定。
- 接客時間はレジ能力に強く依存するが、数値式は存在しない。「No seconds/ticks-per-skill formula should be invented yet」と明記。
- 配置店員は1店舗最大3人。

### 2.2 実装側の状態

Python（`reference_sim/conveni_sim/checkout.py`、`CheckoutStationRuntime`）:

- 什器ごとに1インスタンス。同時接客はコンストラクタ引数 `simultaneous_staff_capacity`（≥1）で容量化され、原作解析の安全要件どおり特定什器への固定割当てはしていない。
- 正本は `_active_by_staff`（staff_id → customer_id）。ガード: 店員は同時に1客まで、客は同時に1人の担当まで、容量超過は `CheckoutCapacityError`。他タスク中・他レジ担当中の店員の開始は拒否（メモ項目2の修正が現行コードに存在）。
- サービス時間そのものは本クラスに無く、呼び出し側が `finish_service` を明示する設計。時間は差し替え可能な `CheckoutServiceTimingCoordinator`（ポリシー）側。選択順も `CheckoutCustomerSelectionPolicy` のポリシー注入で、非FIFOを許す構造。
- テスト: `test_staff_checkout.py` が容量1での第2店員拒否、容量2での同時2件、到着順≠会計順、時間の発明なし（10 tick 後も接客継続）等を固定。`test_multi_customer_checkout_load.py` が容量1・4客の完走を固定。

Godot（`game/scripts/domain/program_people.gd`、native復元経路）:

- `service()`: 同一什器に向いた待機客を、レジ位置にいる未接客の店員が接客。tick ごとに `source_served` がリセットされ、店員1人あたり1 tick に1客まで。複数店員が同じ什器で別々の客を同時接客できる。
- 容量ゲート `gate()`: 稼働レジ店員数が「什器幅 − 1」に達すると追加の店員は開始しない。幅は復元した什器データのフィールド由来で、発明した定数ではない。

### 2.3 判定

構造は原作の確定範囲と整合し、未解明の数値（時間式・割込み閾値・選択式）を実装が発明していない点も規律どおり。**同時接客は「構造=整合、数値=未解明（原作側）」** と分類する。実装側に是正すべき点は本サブテーマでは見つからなかった。

## 3. 行列幾何

### 3.1 原作側の確定範囲

- `checkout-staff-dispatch-evidence-2026-09-05.md` の "Still unknown" に **"queue geometry and impatience thresholds"** と明記。PROJECT_MEMORY §17 でも "Checkout queue behavior and abandonment/anger conditions" は Priority A の研究ギャップとして残置。
- 数値として存在するのは2つだけ: 原作に **20の固定客スロット** があること（原EXE解析由来の前提記述。スロットと行列位置の対応の詳細はなし）、攻略ガイド系の助言「レジ前は2タイル程度、通常通路は最低1タイル」（観測・助言レベルで、行列アンカーの実測ではない）。
- 後着客の先会計ケースで「待機セル」を記録する検証計画はあるが未実施。

### 3.2 実装側の状態

- Python: 行列は論理リスト `_waiting`（到着順保持、新規は末尾追加）のみ。行列位置・間隔・方向の定数は存在しない。最大行列長の上限も無い（上限があるのは同時接客数だけ）。移動は `traffic.py` の BFS 最短路で什器の対話セルへ向かい、同セルの競合は双方 BLOCKED（優先規則なし）。`CongestionPolicy` の docstring 自身が「原作定数ではない設定可能なハーネスポリシー」と明記。
- Godot: `program_geometry.gd`（CONFIRMED_BINARY）の勾配経路探索とセル占有から行列が創発する。使用側セルの方向符号化（10000〜10003）、占有カウント、 blocked 時の側方移動と確率ロールは復元プログラム側の仕組みで、行列の間隔定数のような発明は読み取り範囲では見つからなかった。待ちが限界に達した場合の断念は `_program_wait_at_checkout` 経由（未読のため閾値は未検証、§冒頭の残件参照）。

### 3.3 判定

**行列幾何は原作側が未解明であり、実装がそれを発明で埋めていないことは確認できた。** したがって「原作と違う」と言える箇所は現時点では存在しない。残る論点は、(a) 20固定客スロットと現行の客管理（Python のセッション、Godot の客ロスター）の同一性の証明が未完であること（検証不足）、(b) `vertical_slice_simulation.gd` の未読2関数に忍耐・断念の閾値が仮置きされていないかの未確認、の2点。(b) は次回の読み取り対象とする。

## 4. Godot 非native経路の仮値2件への注意

いずれも `REMAKE_BALANCED_DEFAULT` のタグ付け自体は確認できた。ただし性質が異なる。

1. `game/scripts/domain/checkout_timing.gd` の会計 tick 式（レジ能力への反比例マッピング）: 原作解析が「数値式を発明するな」と明記した領域への仮値。タグ付け済みであり、規律違反ではない。ただし CLAUDE.md の規律ではタグは「コードコメント・evidence_note・テストアサーション」の3箇所が必要とされる。本監査で確認できたのはコードコメントのみ。残り2箇所の有無は未確認（次回確認事項）。
2. `game/scripts/domain/program_people.gd` の `unattended_checkout()`: 「レジに客がいて担当店員がいない場合、補充・清掃中の店員をレジへ回す」という仮仕様で、タグ付け済み。しかし原作の確定観測は逆方向である（§2.1: 店員は待ち客がいてもぎりぎりまでレジへ向かわない。割込み閾値は UNKNOWN）。閾値が未解明である以上「即時回す」も「回さない」も原作とは断定できないが、**観測された傾向と仮仕様の挙動方向が食い違う** ことは記録しておく。実機プレイの体感（レジが無人になりにくい等）に影響しうる。扱いはユーザーの裁定事項として §7 に分離する（Muse からは変更を指示しない）。

## 5. 入力→営業状態の未接続境界（実欠陥2件）

「入力から営業状態への未接続境界」の具体例として、レビューメモ（`docs/handoff/chatgpt-review-notes.md`）の未解決項目のうち、レジまわりの2件を現行コードで検証した。どちらもメモの記述どおりに残存していた。

### 5.1 メモ項目3: force_eject が接客中の割当を解放しない

- `reference_sim/conveni_sim/customer.py` の `CustomerLifecycleHarness.force_eject()` は、セッション状態を EJECTING に変え traffic の目標を出口へ向けるだけで、チェックアウト側への参照を持たない。`store_runtime.py`・`store_step.py`・各コーディネータにも、`force_eject` と `checkout.cancel_customer()` を結ぶ処理はない。
- 待ち客だけの場合は状態変化により `refresh_waiting()` から外れる（この狭い範囲は `test_staff_checkout.py` の `test_ejected_waiter_is_removed_without_guessing_penalty` で固定済み）。
- **接客中（`_active_by_staff` に載っている）客を eject すると、割当が残り続け、店員のスロットと CHECKOUT タスクが占有されたままになる。** 後から `finish_service` を呼ぶと割当は外れるが例外が上がる。さらに `StoreRuntimeHarness.finish_checkout_sale()` は精算を先に行ってから `finish_service` を呼ぶ構成のため、eject 済みの接客中客に対して時間完了が走ると「精算だけ済んで例外」という部分適用になりうる（これは2関数の合成からの推論で、実行確認ではない）。
- 対応するテストは存在しない（`test_known_issues.py` に項目3のテストなし）。

### 5.2 メモ項目12: cancel_customer がセッション状態を変えず、refresh で復活する

- `checkout.py` の `cancel_customer()` はチェックアウト内部の `_waiting` と `_active_by_staff` だけを変更し、`CustomerSession` の状態（WAITING_CHECKOUT）と `checkout_fixture_id` を変えない。
- `refresh_waiting()` はセッション状態だけで適格判定するため、取り消した客は次の refresh で再び `_waiting` に戻る。refresh は `begin_service()` や各コーディネータの `current_context()` から日常的に呼ばれるため、**取り消しは通常運用の中で静かに無効化される**。
- 対応するテストは存在しない（同上）。

### 5.3 判定と指示書化

2件とも、原作の解釈や数値を必要としない「ハーネス内部の整合性」の欠陥であり、期待動作を仕様として定義できる（eject された客の接客割当は解放されること、取り消しは refresh を跨いで有効であること）。よって ready へ進め、**CSRM-004** として発行した。なお項目3・12はメモ上で長く「解決記載なし」だったもので、今回の検証で現行コードでの残存を確定した。

### 5.4 境界として正常だったもの（参考）

- 入店ゲート（`store_runtime.py` の `admit_customer()`）: 営業状態が不明なら客を生成せず `OPEN_STATE_UNKNOWN` を返す。低レベルの `add_customer()` が意図的にゲートを迂回することは docstring に明記された設計。
- 什器配置境界: 未配置什器への `add_checkout()` は KeyError、精算済み・空バスケットの `begin_checkout_service()` 等は拒否（メモ項目13・14のテストが固定）。
- `store_step.py` の合成順序（時計→休憩/怒り/時間/作業→需要→移動→購入→店員タスク（接客中はロック）→所有権競合の遮断→接客前離脱ゲート→選択）は、閾値を発明しないコーディネータ設計として文書化されている。

## 6. 分類のまとめ（運用の4分類で）

- 解明済み・反映済み: 待ち断念の原条件（132条件、customer-abandonment）。非FIFO の許容、容量のパラメータ化（構造として）。
- 未反映: なし（本テーマでは「解明済みだが未反映」は見つからなかった）。
- 未解明: 行列幾何そのもの、会計時間式、割込み閾値、会計順序の選択式、競合敗北時の休憩室滞在規則、客タイプ別忍耐の数値差。
- 検証不足: 20固定客スロットとの同一性、`vertical_slice_simulation.gd` 未読2関数、`checkout_timing.gd` 仮値の3箇所タグ付けの残り2箇所、Godot native 経路の行列創発が原作の見た目とどこまで合うか（実機未確認を含む）。

## 7. ユーザー判断が必要な項目（分離）

- D-4（新規）: §4-2 の `unattended_checkout` 仮仕様（レジ無人時に補充・清掃から店員を即時回す）について。原作観測の傾向（店員はぎりぎりまでレジへ向かわない）と方向が食い違う仮値である。現状のまま（レジ無人になりにくい現行挙動を維持）か、原作傾向に寄せる検討を将来の調査テーマにするか。実装の着手には影響しないため、判断は急がない。
- D-1・D-2 は初回棚卸し §9 のまま継続（実機確認の運び方、§21.4 矛盾項目の扱い）。

## 8. 次回解析への申し送り

- A-2残件: `vertical_slice_simulation.gd` の `_program_wait_at_checkout` と `_advance_customer` の読み取り（忍耐・断念閾値の仮置き有無、非native経路の客処理）。ファイルが大きいため範囲を絞って読む。
- A-3（§21.3「未実装」リストの現行ブランチ再照合）は予定どおり次回以降。
- `checkout_timing.gd` の REMAKE_BALANCED_DEFAULT 3箇所タグ付け（evidence_note・テスト）の有無の確認は A-2残件と合わせて行う。
