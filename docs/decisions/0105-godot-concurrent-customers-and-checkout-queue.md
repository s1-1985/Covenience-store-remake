# 0105: `game/`(Godot)に同時複数顧客・チェックアウト待ち行列を実装(タスク#36)

## 背景

`docs/handoff/2026-09-18-claude-code-session-handoff.md`第3.2節が「対象外・先送り」
としていた3項目のうち、最初の1件。研究ドキュメント
(`docs/research/ss-layout-entrance-register-and-chain-cannibalization-2026-09-06.md`
第2節)は「レジの向きによって客の並ぶ方向が変わる」ことをCONFIRMED-VISUAL級で
記録している一方、`docs/decisions/0004`/`0016`/`0021`/`0024`は「具体的な待ち行列の
順序・幾何形状は未確定」として意図的に未実装のまま据え置いていた。

`reference_sim/conveni_sim/checkout.py`の`CheckoutStationRuntime`は、実は既に
「複数顧客の同時待機」「明示的な(FIFOを強制しない)サービス順選択」を実装済みで、
コメントには「初代のFAQ証拠によれば後着の客が先に案内されることもある」と明記
されている。しかしGodotクライアント(`game/`)側は`CustomerRoster`が
「アクティブな客は常に1人」という制約を持ったままで、この既存のreference_sim側の
設計が一切移植されていなかった。

## 決定

### 二層の入店ゲート

`CustomerRoster`に、意味の異なる2つの入店判定を導入した:

- `can_admit()`(**既存、変更なし**): `active_customer_id.is_empty() or
  active().phase == "done"`。直近に入店した1人だけを見る、元からの単一顧客判定。
  **自動デマンド来店(`demand_admit_if_due()`)だけは、この判定を今回も変更していない**
  (下記参照)。
- `can_admit_concurrent()`(**新規**): `_active_non_done_count() <
  _max_concurrent_customers`。`start_explicit_customer()`(観測/明示投入経路)と
  `start_next_customer()`(「Admit next customer」ボタン)の両方がこちらを使う。

`_max_concurrent_customers`は`vertical_slice.json`の`customer.max_concurrent_customers`
(既定値3)から読む**REMAKE_BALANCED_DEFAULT**値。攻略本/Wikiのどちらにも
「店内に同時に何人まで客がいられるか」を示す記述がないため、この上限自体は
このプロジェクト独自のスコープ判断であり、原作の確定値ではない。

### 自動デマンドだけは単一顧客のまま

`demand_admit_if_due()`(毎ティック自動的に発火しうる受動的な来店判定)は
今回**あえて変更していない**。`headless_smoke.gd`には元々
「demand-driven admission must be blocked while a customer visit is still active」
という既存テストがあり、`reference_sim`側の契約テストもこれを検証していたため、
この既存の単一顧客保証をそのまま維持した。同時複数顧客は
「プレイヤーが明示的に招き入れる」(ボタン操作、または観測/明示投入)経路でのみ
起こる、という切り分け。

### レイアウト編集の安全確認を`all_settled()`に分離

什器購入・移動・回転・許可購入・商品仕入れ・宣伝購入・チェーン拡大・明示補充の
8関数は、従来`not customers.can_admit()`でレイアウト編集をロックしていた。
しかし`can_admit()`は直近1人の客の状態しか見ないため、複数客が同時に存在しうる
今回の変更後は「直近の客は会計済みだが、それより前に入店した客がまだ店内にいる」
場合に誤って編集を許してしまう。そこで`all_settled()`(**新規**、
「入店中の客が1人もいない」)を新設し、この8箇所を`not customers.all_settled()`に
置き換えた。

### チェックアウトの待ち行列

レジ什器・スタッフは従来通り1つしかないため、複数客が同時に会計へ向かっても
サービスは直列化される。`step()`を「客ごとの状態遷移」と「待ち行列の
ディスパッチ」に分離した:

- 客が会計へ向かうルートを歩き終えると、フェーズは`"checkout"`ではなく
  `"waiting_checkout"`になり、`_checkout_queue`(FIFO)に加わる。
- 全客の状態遷移が終わった後、`_dispatch_checkout_queue()`が一度だけ呼ばれ、
  レジスタッフが空いていれば列の先頭客をディスパッチして`"checkout"`へ遷移させ、
  `checkout_ticks_remaining`を設定する。

FIFO順でサービスすること自体は、`CheckoutStationRuntime`のコメントが明記する
通り原作の確定挙動ではない(**REMAKE_BALANCED_DEFAULT**、このプロジェクト独自の
選択)。単一客のシナリオでは「到着した同じティック内に即座に会計開始」という
既存の挙動と完全に一致するため、既存の530ステップの主要シナリオへの影響はない
(このタスクで追加した専用シナリオの分だけステップ数が増える)。

### 描画・HUD

- `store_view.gd`の`_draw_customer()`は`simulation.customers.active_customers()`
  (完了していない全客)をループして描画する。同一セルに複数客がいる場合は
  視認性のため小さくオフセットして重ねる(幾何学的な待ち行列位置の再現ではなく、
  見た目上の重なり回避のみ)。
- `main.gd`のCustomer行は「N active — id: phase, id: phase, ...」の形式で
  全アクティブ客を要約表示する。
- `snapshot()`に`active_customers`配列フィールドを新設。既存の
  `customer_id`/`customer_phase`/`customer_basket_*`は後方互換のため
  `customers.active()`(直近の客)基準のまま変更していない。

### スキーマバージョン

`customer`セクションに新規必須フィールド`max_concurrent_customers`を追加した
ため、`vertical_slice.json`の`schema_version`を12→13に更新
(`VerticalSliceSimulation._require_config()`のアサートも同期)。

## テスト

- `headless_smoke.gd`:
  - `manual_admit_simulation`シナリオ: `start_next_customer()`が客が1人
    アクティブな状態でも2人目を受け入れられること、上限到達後は拒否される
    ことを検証。
  - `concurrent_simulation`シナリオ: 同一プランの客2人を明示投入し、
    (1) 2人目が上限到達時に拒否されること、(2) 全ステップを通じて
    `"checkout"`フェーズの客が同時に2人以上存在しないこと(単一レジの
    直列化)、(3) 少なくとも1ティックは「1人が会計中、もう1人が
    `waiting_checkout`」の重複状態を観測すること(待ち行列が実際に機能する
    ことの証明)、(4) 両者とも売上を完了すること、を検証。
  - 全体で614ステップ(既存530 + 新規84)でPASS。
  - Godot 4.3公式バイナリで実行して確認。
- Xvfb + 実Godotバイナリで`main.tscn`を実際にレンダリングし、「Admit next
  customer」を2回相当操作して「2 active — customer-1: to_shelf, customer-2:
  to_shelf」がHUDに表示されることをスクリーンショットで目視確認。
- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  - 既存の`test_customer_visits_are_retained_without_inventing_concurrent_arrivals`
    を`test_customer_visits_are_retained_and_passive_demand_flow_stays_single_customer`
    へ改名し、"no concurrent arrivals anywhere"という古い主張を「自動デマンドだけは
    単一顧客のまま」という正確な主張に訂正。
  - 新規`test_concurrent_customers_are_supported_via_the_explicit_admission_path`
    を追加し、上記の設計(二層ゲート/all_settled分離/待ち行列/描画・HUD)を
    フィールド単位で検証。
  - `test_register_skill_checkout_timing_is_a_tagged_remake_default`の
    インデント依存の文字列一致を、`_dispatch_checkout_queue()`への移動後の
    実コードに合わせて更新。
  - `schema_version`の期待値を12→13へ更新。
  - フルスイート652件(xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/domain/customer_roster.gd`: `can_admit_concurrent()`/
  `all_settled()`/`active_customers()`/`customer(id)`を新設。
- `game/scripts/vertical_slice_simulation.gd`: `step()`を客ごとの遷移と
  `_dispatch_checkout_queue()`に分離。8箇所の編集ロックを`all_settled()`へ。
  `start_next_customer()`/`start_explicit_customer()`を`can_admit_concurrent()`へ。
  `snapshot()`に`active_customers`を追加。
- `game/scripts/store_view.gd`: 全アクティブ客を描画。
- `game/scripts/main.gd`: Customer行の要約表示、`all_settled()`/
  `can_admit_concurrent()`への置き換え。
- `game/data/vertical_slice.json`: `customer.max_concurrent_customers`を追加、
  `schema_version`を13へ。
- `game/scripts/headless_smoke.gd`: 新規シナリオ2件を追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 既存テストの
  改名・訂正、新規テスト追加、`schema_version`/インデント依存文字列の更新。

## 明示的に対象外とした限界

- 待ち行列の**幾何学的な位置**(専用の列セル)は実装していない。研究ノートが
  「正確な列の座標は未確定」と明記しているため、`waiting_checkout`の客は
  会計インタラクションセルに留まり、描画側で視認性のためオフセットするのみ。
- レジの向きによる列の方向(研究ノート第2節のCONFIRMED-VISUAL証拠)は未反映。
  現状のレジ什器はまだ`queue_entry_position_or_edge`のような向き依存の
  フィールドを持たない。
- サービス順は最終的にFIFO(REMAKE_BALANCED_DEFAULT)。原作が「後着優先も
  ありうる」ことを示唆する以上、これは確定挙動の主張ではない。
- 3.2節の残り2項目(サンプルレイアウト読み込み、什器attention差別化)は
  今回も対象外。
