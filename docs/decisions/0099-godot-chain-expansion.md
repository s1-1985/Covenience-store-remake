# 0099: `game/`(Godot)に複数店舗(チェーン展開)管理を実装(タスク#30、ロードマップ完了)

## 背景

タスク#30「複数店舗(チェーン展開)管理をGodotに実装」は、自己生成した
Godot移植ロードマップ(タスク#21-30)の最終タスクである。`reference_sim`を
調査したところ、「複数店舗を同時にプレイする」という意味でのフル空間
シミュレーションに対応するものは存在しなかったが、以下の実際にconfirmedな
エビデンスが見つかった:

- `reference_sim/conveni_sim/visitor_milestone.py`の
  `ChainVisitorMilestoneRuntime`: 「プレイヤーのチェーン全体で累計来店客数が
  10,000人に達するごとに、翌日00:00に人気度+100の無料イベントが発生する」
  という**CONFIRMED**な一次資料("first-title PS/SS research")。既に
  evidence-safeな完成した実装として存在していた。
- `reference_sim/conveni_sim/store_events.py`の
  `magazine_or_contest_event_is_eligible()`/`compute_contest_prize_yen()`:
  攻略本のイベント発生条件表からの**CONFIRMED_OFFICIAL**な転記
  (「人口1万人以上 かつ マップ内に5店舗以上」で業界誌掲載/コンビニ
  コンテストの対象となり、賞金は「店舗数(ライバル店を含む)×1000万円」)。
  実際に選ばれるかどうかは「選ばれることもある」という不確定要素であり、
  `reference_sim`自身もそのサイコロを振っていない。
- `PROJECT_MEMORY.md`第14節: コミュニティ情報源による、シナリオ
  「中級: 自社10店舗到達」というクリア条件。この節自体が
  「本節は攻略本/実プレイでの検証が必要」と明記する、他の項目より一段
  信頼度の低い**PROVISIONAL**情報。

一方で、「プレイヤーが実際に2店舗目を開店し、両方の店舗を同時にプレイする」
というフル空間シミュレーション自体は、`reference_sim`にも対応物が存在
しない(タスク#26で町/ライバル店の空間モデルを意図的にスコープ外とした
のと同じ理由)。

## 決定

### スコープの決定

タスク#26/#27と同じ方針で、以下に絞った:

1. **`player_store_count`フィールドを新設**: このvertical sliceは
   プレイヤーの「1店舗目」であるとし、`reset()`時に1から開始する。
2. **`try_expand_chain()`**: 「2号店を出店する」という行為を、実際の
   2店舗目のゲームプレイをシミュレートすることなく、抽象的な経済アクション
   としてモデル化する(タスク#26と同じ「フル空間モデルは作らない」方針)。
   コストはタスク#26で実装済みの`LandValuePolicy.current_land_price_yen()`
   をそのまま再利用する(`_land_value_policy`/`BASE_LAND_PRICE_YEN`/`town`)。
   新しい価格体系を発明するのではなく、既存のインフラを再利用する判断。
   成功すると`player_store_count`が1増え、`chain_expanded`イベントが
   記録される。
3. **`ChainVisitorMilestone`をそのまま移植**: `visitor_milestone.py`の
   ロジック(次の閾値をスキップして観測した場合はassertで拒否し、
   catch-upを発明しない、という設計を含む)を逐語移植。「チェーン全体の
   累計来店客数」は、このクライアントが今のところ1店舗しか実際に
   プレイしないため、その1店舗の`customers.completed_count()`をそのまま
   使う。将来2店舗目が実際にプレイ可能になった時点で、両店舗の合計を渡す
   ようにするだけで、このランタイム自体は変更不要なように設計されている。
4. **`player_store_count >= 10`でクリア条件を満たす**:
   `PLAYER_STORE_COUNT_SCENARIO_TARGET := 10`を
   `_evaluate_terminal_state()`に組み込み、`clear_condition_met`を
   初めて実際にtrueにできるようにした(決定書0091時点では
   `clear_condition_met`は常にfalseだった)。この定数はPROJECT_MEMORY
   第14節自身が「要検証」と明記する情報のため、
   `REMAKE_BALANCED_DEFAULT`よりさらに一段弱い**PROVISIONAL**タグを
   明示的に付けている。
5. **`StoreEvents`(業界誌掲載/コンビニコンテスト)は適格性のみ表示**:
   `magazine_or_contest_event_is_eligible()`/`compute_contest_prize_yen()`
   をそのまま移植し、`snapshot()`に`magazine_or_contest_eligible`/
   `contest_prize_yen`として公開する。`reference_sim`自身が「実際に
   選ばれるか」のサイコロを振っていないのと同じ理由で、このクライアントも
   自動発火・自動付与は一切行わない(情報表示のみ)。

### 明示的に実装しなかったもの

- **2店舗目を実際にプレイできる機能**(独自のレイアウト・在庫・スタッフ・
  経済状態を持つ2つ目の`VerticalSliceSimulation`インスタンスを同時に
  管理し、UIで切り替える、といったマルチストア・アーキテクチャ)。これは
  タスク#26で空間モデルを見送ったのと同じ理由に加え、このクライアントの
  現在のアーキテクチャ(`main.gd`が単一の`simulation`を保持する設計)を
  大きく再設計する必要があり、このタスク単体の範囲を大きく超える。
  `player_store_count`は「チェーンの規模」を表す抽象的なカウンタとして
  扱い、2店舗目以降の実際の店舗運営はモデル化していない。
- **「クリア」時の勝利演出/専用の終了状態**: `clear_condition_met`が
  trueになっても、既存の仕様(決定書0091)通り「100年経過による
  time_limit_exceeded ゲームオーバーを回避する」効果があるのみで、
  勝利を示す専用のゲームオーバー的終了状態は追加していない。この設計は
  タスク#24(決定書0091)の範囲であり、本タスクで再設計しない。
- **業界誌掲載/コンビニコンテストの実際の抽選・発火・賞金付与**。
  `reference_sim`自身が確率式を持たないため、適格性の表示のみに留める。
- **ライバルチェーンの出店/支店買収/閉店といった動的な遷移**
  (`reference_sim/conveni_sim/rival.py`の`RivalChainRuntime`)。これは
  ライバル店という実体自体がGodot側にまだ存在しない(決定書0095と同じ
  理由)ため、今回も対象外とした。

### セーブ/ロードとの整合

`player_store_count`と`ChainVisitorMilestone`の状態(`last_observed_total`/
`next_threshold`/`events`)は、タスク#28で実装した`save_state()`/
`load_state()`にも組み込んだ(セーブしないと、ロード後にチェーン展開の
進捗や来店マイルストーンの進行状況が失われてしまうため)。これに伴い、
`SAVE_SCHEMA_VERSION`を1→2に更新し、`load_state()`の互換性チェックにより
旧バージョンのセーブファイルは(構造検証で失敗させるのではなく)明示的に
「非互換」として拒否されるようにした。

## 実装ファイル

- `game/scripts/domain/chain_visitor_milestone.gd`(新規): `ChainVisitorMilestone`。
- `game/scripts/domain/store_events.gd`(新規): `StoreEvents`。
- `game/scripts/vertical_slice_simulation.gd`: `player_store_count`/
  `_chain_visitor_milestone`/`_store_events`フィールド、
  `PLAYER_STORE_COUNT_SCENARIO_TARGET`定数、`try_expand_chain()`/
  `chain_expansion_cost_yen()`/`_observe_chain_visitor_milestone()`/
  `_fire_due_chain_visitor_milestones()`メソッドを追加。`step()`の
  顧客退店処理から`_observe_chain_visitor_milestone()`を呼ぶよう変更。
  `_advance_minute_of_day()`が日境界処理の後に
  `_fire_due_chain_visitor_milestones()`を呼ぶよう変更。
  `_evaluate_terminal_state()`が`player_store_count`によるクリア条件判定を
  行うよう変更。`snapshot()`/`save_state()`/`load_state()`/
  `_require_save_data()`を拡張。`SAVE_SCHEMA_VERSION`を1→2に更新。
- `game/scripts/headless_smoke.gd`: `ChainVisitorMilestone`/`StoreEvents`の
  単体テスト、`try_expand_chain()`の可否・コスト計算・イベント記録の検証、
  `player_store_count`到達によるクリア条件の検証、実際のシミュレーション上で
  来店マイルストーンが正しく発火し人気度+100が適用されることの検証を追加。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_chain_expansion_ports_confirmed_visitor_milestone_and_store_count_target`
  を追加。`ChainVisitorMilestone`/`StoreEvents`のevidence-safeタグ付けと
  確定定数の一致、`PLAYER_STORE_COUNT_SCENARIO_TARGET`のPROVISIONALタグ、
  地価インフラの再利用、月次ループ/クリア条件への配線を検証する。
  `test_godot_entry_scene_and_scripts_exist`に新規ファイル2件を追加。

## タスク#30、およびGodot移植ロードマップの完了

チェーン全体の来店マイルストーン・店舗数によるシナリオクリア条件・
業界誌/コンテストの適格性表示を実装し、実際の複数店舗同時プレイという
フル機能は明示的に対象外としたことをこの決定書に記録した上で、タスク#30
「複数店舗(チェーン展開)管理をGodotに実装」を完了とする。これにより、
セッション開始時に自己生成したタスク#21-30のGodot移植ロードマップが
全て完了した。
