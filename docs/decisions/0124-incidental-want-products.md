# 0124: ついで買い(incidental-want products)の実装、決定書0004の境界を解除(タスク#55)

## 背景

決定書0004(2026-09-05)は、「incidental/add-on purchase probability」を
「Deliberately absent」なものの1つとして明示的に対象外としており、
「These become pluggable policies once guide/video evidence is strong
enough」(=十分な証拠が揃った時点でプラグイン可能なポリシーとして
追加してよい)としていた。タスク#43の監査でもこの境界が改めて確認され、
以後「ユーザーの明示的な判断待ち」として保留され続けてきた
(`PROJECT_MEMORY.md`第21.3節)。

タスク#50〜#54の一連のPDF再読の中で、「クイックリファレンス」book p.9
(顧客の購入品)を直接再読し、以下の記述を確認した:

> 「購入希望商品」と「ついでに欲しい商品」 顧客は購入希望の品を求めて
> 来店する。希望の品を購入した後、時間が許せばそのほかの商品も購入する。
> それぞれの顧客に3品程度の「ついでに欲しい品」があるので、それらを
> 揃えておくことも大切だ。

これはCONFIRMED_OFFICIALであり、決定書0004が要求していた「guide/video
evidence is strong enough」という解除条件そのものである。ただし、
どの商品がどの確率で「ついでに欲しい品」になるかという具体的な公式は
このページにもどこにも存在しない(同じページのグラフは単一プレイの
サンプルデータであり、一般化されたゲームデータ表として扱うべきでは
ないと既に判断済み)。この境界を解除して実装に着手してよいかを
`AskUserQuestion`でユーザーへ確認し、「着手する(推奨)」の回答を得た。

## 決定

### `VerticalSliceSimulation._start_default_customer()`の拡張

需要駆動(自動来店・「次の客を迎える」ボタンの両方が内部で呼ぶ、唯一の
入口)で来店する客について、主目的のプラン(`customers.default_plan()`)
に加えて、新規ヘルパー`_select_incidental_want_product_ids()`が選んだ
最大`INCIDENTAL_WANT_PRODUCT_COUNT`(3)品の「ついでに欲しい品」を
プランの末尾へ追加する。新しいフェーズや機構は一切追加していない――
既存の`planned_product_ids`(複数商品の順次購入)の仕組みをそのまま
再利用しているだけである。

### REMAKE_BALANCED_DEFAULTな設計選択(書籍に明記のない部分)

- **選定方法**: 現在店舗に在庫登録されている商品(`inventory.product_order`)
  のうち、既に主目的プランに含まれていないものから、一様ランダムに選ぶ。
  既存の需要用RNG(`_demand_rng`)を再利用し、新たなRNGストリームは
  発明していない。書籍のグラフ(カテゴリ別のついで買い需要の相対的な
  大きさ)は単一プレイのサンプルデータであり、確定した重み付けテーブル
  として扱うのは不適切と判断し、意図的に不使用とした。
- **個数**: 書籍の「3品程度」を、厳密に3(またはその時点で選択可能な
  候補が3未満ならその数)とした。
- **「時間が許せば」の扱い**: このクライアントには客の滞在時間・
  忍耐力を表すメカニクス自体が一切存在しない(`PROJECT_MEMORY.md`
  第7節は今も未確認のHYPOTHESISのまま)。そのため「時間が許せば」は
  「常に許す」という単純化を採用した――既存の主目的プランも同様に
  無条件で最後まで実行されるため、一貫した扱いである。

### スコープ: 需要駆動の来店のみ

`start_explicit_customer()`(観測リプレイ用の、呼び出し元が指定した
「正確な」プランを再現する経路)は一切変更していない。この経路は
既存のテスト・観測リプレイの決定性を支える重要な契約であり、そこへ
推測に基づく商品を混入させることは、この経路の存在意義そのものと
矛盾する。`CustomerRoster.admit_default()`のシグネチャを、内部で
静的な`_visit_plan_product_ids`を再利用する形から、呼び出し元
(`VerticalSliceSimulation`)が用意した(拡張済みの)プランを受け取る形へ
変更したが、`admit_explicit()`自体は無変更。

## テスト

- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。什器購入+商品
  仕入れで、主目的の2品(prototype-bread/prototype-drink)以外の3品目
  ("incidental-extra-product")を在庫へ追加した上で、(a)
  `start_explicit_customer()`で明示的に指定したプランが一切膨らまない
  こと、(b) `start_next_customer()`で需要駆動的に迎えた客のプランが、
  主目的2品+ついで買い1品(候補がちょうど1つしかないため、RNGシード
  非依存で決定論的に検証可能)の計3品になることを検証。Godot 4.3公式
  バイナリで1009ステップ(タスク#54時点の957から、新規シナリオ分増加)
  でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_incidental_want_products_extend_only_demand_driven_customer_plans`
  を追加。evidence_noteのタグ、バックエンド関数の存在・配線、
  `admit_default()`のシグネチャ変更を検証。フルスイート666件(新規
  テスト関数1件追加)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`:
  `INCIDENTAL_WANT_PRODUCT_COUNT`定数、
  `_select_incidental_want_product_ids()`を新規追加。
  `_start_default_customer()`を更新。
- `game/scripts/domain/customer_roster.gd`: `admit_default()`の
  シグネチャを、呼び出し元からプランを受け取る形へ変更。
- `game/data/vertical_slice.json`:
  `simulation.incidental_want_evidence_note`を新規追加。
- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  テストを追加。

## 明示的に対象外とした限界

- 商品カテゴリごとの「ついで買われやすさ」の重み付けは実装していない
  (上記の通り、書籍のグラフは一般化できるデータではないと判断)。
- 客の滞在時間・忍耐力によってついで買いを諦めるという挙動は実装
  していない(このクライアントにその前提となる時間予算メカニクス自体が
  存在しないため)。
- `start_explicit_customer()`経由の観測リプレイ用の客は、引き続き
  ついで買いの影響を一切受けない(意図的な設計)。
- 棚の「注目度」がついで買いの選定確率に影響するという可能性
  (タスク#43で先送りにされた項目)は、今回も配線していない――今回
  追加したのは「在庫にある商品から一様ランダムに選ぶ」という、最も
  単純なREMAKE_BALANCED_DEFAULTのみ。
