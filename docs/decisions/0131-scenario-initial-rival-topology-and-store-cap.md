# 0131: シナリオ初期ライバル構成 + 自社/ライバル合計店舗上限(タスク#62)

## 背景

前回セッション(タスク#59〜#61)終了時のhandoff(`docs/handoff/2026-09-20-claude-code-session-
handoff-7.md`)第5節は、次の候補の一つとして「ライバル店の実際のスポーン・行動ロジック
(いつ・どこにライバル店が出現するか)」を挙げていた。`remake_rival_policy.py`の判断ロジック
(EXPAND/HOLD/RETREAT)は既に存在するが、シナリオ開始時にライバルが何店舗・どんな役割
(本店/支店)で存在するかは`baseline_data.SCENARIOS`に一切データがなかった。

新規に`docs/research/scenario-initial-rival-topology-2026-09-06.md`(既存だが未実装のまま
残っていた研究文書)を確認したところ、PS版の中級・上級それぞれの長期プレイ記録から、開始時
ライバル構成が明示的に異なることが分かった:

- **中級**: 「ライバル店は最初3店舗ありました」と明記(本店1+支店2)。証拠レベル`B+`。
- **上級**: 「ライバル店も本店のみ」と開始時点を明記、2年目までに支店を増やし3店舗になる
  という経過も記録。証拠レベル`B+`。
- **初級**: 開始直後に支店を買収した記録はあるが、総店舗数を明示する記述は見つからず、
  `UNKNOWN`のまま。

また同時に、別の複数研究文書(`docs/research/first-title-wiki-full-scan-delta-2026-09-05.md`
のwiki記述、`docs/research/ps-longplay-rival-economy-events-2026-09-05.md`のPS長期プレイ
記録)が、**プレイヤー+ライバル合計10店舗**でそれ以上新規出店できなくなるという同一の制約を
独立に2箇所で確認していた。これは中級シナリオの「10店舗達成」クリア条件(`baseline_data.
SCENARIOS`の`objective`フィールド)とは別の、マップ全体にかかる建設上限のハード制約である。

いずれも座標・店舗サイズ・店員構成・出店タイミング式・出店候補地評価式などは未確定のまま
(研究文書自身が明記)であり、これらを推測で埋めることはしていない。

## 決定

### `ScenarioDefinition`に確認済みのライバル構成フィールドを追加

`models.py`の`ScenarioDefinition`へ、いずれも`Optional[EvidenceValue]`(未確認のシナリオでは
`None`のまま)として3フィールドを追加した:

- `initial_rival_store_roles`: 役割の並び(`("headquarters", "branch", "branch")`等)。
  中級・上級のみ値あり。
- `initial_rival_branch_exists`: 総数不明だが支店の存在自体は確認できる場合の真偽値。
  初級のみ値あり。
- `rival_can_open_branches_after_start`: 開始後に支店を増やす挙動が確認できる場合の真偽値。
  上級のみ値あり。

`baseline_data.SCENARIOS`の3エントリをこれに従って更新した(いずれもCONFIRMED_COMMUNITY、
出典は研究文書が引用する2本のPS長期プレイ記録)。

### `scenario_initial_rival_topology.seed_rival_chain_for_scenario()`を新規追加

確認済みの役割構成を、既存の`rival.RivalChainRuntime`へそのまま投入するヘルパー関数。
`initial_rival_store_roles`が`None`のシナリオ(初級)は`None`を返し、無理に埋めない。

各店舗の`location_id`(オープン時に必須の不透明なキー文字列)には`f"{scenario_id}_seed_{n}"`
という仮のプレースホルダーを与えている――これは町マップ上の実際の位置を主張するものではない
(座標自体が研究文書上UNKNOWN)。`rival.py`の`location_id`は元々空間座標ではなく不透明な
識別子として設計されている(空間座標を扱うのは別モジュールの`remake_town_spatial.py`)ため、
この仮キーの付与はREMAKE_BALANCED_DEFAULTタグを要する新規発明ではなく、単なる内部管理用の
命名と位置付けている。

### `town.TOTAL_STORE_CAP_INCLUDING_RIVALS`と`TownState.has_capacity_for_new_store()`を新規追加

CONFIRMED_COMMUNITY(wiki + PS長期プレイの独立2件)の「合計10店舗上限」を`town.py`に定数
として追加し、`TownState`に非破壊的な判定メソッド`has_capacity_for_new_store()`を追加した。
このクラスの既存設計(呼び出し元が状態を追跡する)に合わせ、上限チェックのみを行い、店舗数の
増減自体は呼び出し元に委ねる。

## テスト

- `reference_sim/tests/test_baseline.py`: `SCENARIOS`の新規フィールド(役割構成・支店存在・
  開始後拡大フラグ)を検証するテストを追加。
- `reference_sim/tests/test_town.py`: 上限ちょうど/超過で`has_capacity_for_new_store()`が
  `False`を返すこと、定数値が10であることを検証するテストを追加。
- `reference_sim/tests/test_scenario_initial_rival_topology.py`: 新規テストファイル。初級が
  `None`を返すこと、中級が本店1+支店2を`RivalChainRuntime`へ正しく投入すること、上級が本店
  のみを投入すること、投入後も既存の`close_store()`/`open_store()`が通常通り機能すること、
  未知のシナリオIDで`KeyError`になることを検証。
- フルスイート722件(新規9件)、xfail 1件、全てPASS。
- Godot側(`game/`)は無変更のため未検証(そもそも本タスクはreference_sim限定、下記参照)。

## 実装ファイル

- `reference_sim/conveni_sim/models.py`: `ScenarioDefinition`に3フィールド追加。
- `reference_sim/conveni_sim/baseline_data.py`: `SCENARIOS`の3エントリを更新、出典定数
  `SCENARIO_INITIAL_RIVAL_TOPOLOGY`を追加。
- `reference_sim/conveni_sim/town.py`: `TOTAL_STORE_CAP_INCLUDING_RIVALS`定数と
  `TownState.has_capacity_for_new_store()`を追加。
- `reference_sim/conveni_sim/scenario_initial_rival_topology.py`: 新規ファイル、
  `seed_rival_chain_for_scenario()`を追加。
- `reference_sim/tests/test_baseline.py`, `test_town.py`,
  `test_scenario_initial_rival_topology.py`(新規): テスト追加。

## 明示的に対象外とした限界

- `game/`(Godot版)への配線は行っていない――`VerticalSliceSimulation`にはシナリオ選択も
  複数ライバル店舗を実際に配置する仕組みも存在しない(決定書0095/0128の既存境界通り)。
- 初級シナリオの正確な初期ライバル総店舗数は依然`UNKNOWN`のまま――推測で埋めていない。
- 中級・上級とも、各ライバル店の正確な座標・店舗サイズ・店員構成・販売許可・営業方針は
  依然`UNKNOWN`のまま――`RivalStoreSeed`のような完全なスナップショット型は導入していない
  (研究文書自身が「完全な初期マップsnapshotはまだ未復元」と明記)。
- ライバルの閉店後の再出店(いつ・どこへ)の具体的な待機時間・資金条件・立地評価式は
  依然`UNKNOWN`のまま――今回は初期構成と店舗数上限のみを対象とし、再出店ロジック自体の
  REMAKE_BALANCED_DEFAULT実装は別タスクとして先送りした。
- `remake_rival_policy.RemakeBalancedRivalPolicy`(EXPAND/HOLD/RETREAT判断)と本タスクの
  シード機能はまだ統合していない――シードされた`RivalChainRuntime`に対して実際に
  EXPAND/RETREAT判断を適用し、店舗上限(`TownState.has_capacity_for_new_store()`)を
  参照しながら新規出店/閉店を実行する統合ループは別タスク。
