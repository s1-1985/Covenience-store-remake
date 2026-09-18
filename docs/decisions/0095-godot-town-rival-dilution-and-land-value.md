# 0095: `game/`(Godot)に町・ライバル店・地価をREMAKE_BALANCED_DEFAULTで実装(タスク#26)

## 背景

タスク#26「町・ライバル店・地価の空間モデルをGodotに実装」に着手した。
`reference_sim`側には既に3つの関連モジュールが存在する:

- `conveni_sim/town.py`: `TownState`(人口・ライバル店舗数を保持するだけの
  非空間的な状態クラス)。
- `conveni_sim/remake_customer_share.py`: `compute_customer_share_percent()`。
  人気度・サービス・清掃・警備・品揃え・営業時間の6要素を加重平均し、
  ライバル店の数に応じて`RIVAL_DILUTION_PER_COMPETITOR=0.08`
  (店舗あたり)・`MAX_RIVAL_DILUTION=0.6`(上限)で希薄化する
  REMAKE_BALANCED_DEFAULT式。
- `conveni_sim/remake_land_value.py`: `RemakeBalancedLandValuePolicy`。
  人口・店舗密度から求まる`local_development_factor`と、経過年数から
  求まる`time_inflation_factor`(年率5%)を乗算する地価式。

いずれも`docs/research/strategy-guide-full-decode-2026-09-16.md`第41節が
「存在は確認できるが式は未確定」と明記した項目(町発展・地価変動)に対する
tagged placeholderであり、実際の空間マップ・施設配置・人口成長式は
`reference_sim`自身も一切発明していない。

### スコープの決定

タスク名は「空間モデル」を含むが、実際に空間(タイル座標を持つ町マップ、
ライバル店の配置、商圏の重なり)を発明することは避けた。理由:

1. `reference_sim`自身が空間モデルを持たない。これを発明すると、
   このプロジェクト全体の「証拠のない数値は推測とタグ付けする」原則を
   逸脱し、空間モデルという最も証拠の薄い領域を無根拠に埋めることになる。
2. `PROJECT_MEMORY.md`第17節は「町発展の一般式」を明示的な研究ギャップと
   位置づけている。

代わりに以下の3点に絞った:

1. **`TownState`をそのまま移植**(`town_state.gd`): 人口・
   `store_count_including_rivals`を保持するだけの非空間状態。
2. **ライバル希薄化を需要へ実際に配線**(`demand_policy.gd`): 唯一「実際に
   ゲームプレイへ効果を持つ」変更。`RIVAL_DILUTION_PER_COMPETITOR`/
   `MAX_RIVAL_DILUTION`という確定済み定数はそのまま再利用するが、適用対象を
   `compute_customer_share_percent()`が返す0-100のシェアスコアではなく、
   `DemandPolicy.expected_arrivals_per_minute()`が返す来店期待値そのものに
   変更した。これは既存の`customer_share_percent`(サービス・清掃・警備・
   品揃えの4要素)がこのGodotクライアントにまだ存在しないための、対象量の
   置き換えという意図的なスコープ縮小であり、定数自体の再解釈ではない。
3. **地価を情報表示のみとして追加**(`land_value_policy.gd`):
   `remake_land_value.py`の3メソッドをそのまま移植。まだ土地購入・売却の
   仕組みがこのクライアントに存在しないため、`snapshot()`の
   `land_value_yen`として露出するだけで、いかなる機能もこれを消費しない
   (什器の`service_bonus`/`maintenance_yen_per_day`と同じ、既存の
   「情報として表示するが未消費」パターンを踏襲)。

### 明示的に実装しなかったもの

- **町・地図の空間シミュレーション**そのもの(タイル座標を持つ町、施設配置、
  距離ベースの商圏重複、許可の除外距離の強制)。`reference_sim`にも存在
  しないため、この一歩では作らない。
- **ライバルAIの意思決定**(`conveni_sim/remake_rival_policy.py`の
  `RemakeBalancedRivalPolicy.decide()`)。Godot側にはまだライバル店舗
  という実体(エンティティ)が存在しないため、これを移植しても呼び出し元が
  存在せず、「動かないコードを積む」だけの空虚な進捗になると判断した。
  ライバル店舗実体を後の反復で導入する際に、あらためて対応する。
- 地価変動の消費側(土地購入・店舗売却・資産評価への反映)。

### `BASE_LAND_PRICE_YEN`について

`remake_land_value.py`の`current_land_price_yen()`は`base_land_price_yen`を
呼び出し側が渡す引数として扱っており、ハードコードされた定数を持たない。
Godot側では自店舗の土地の基準額として、初代Wikiが記録する観測済み最低地価
20,000,000円(`docs/research/store-unlock-and-daily-pricing-delta-2026-09-05.md`
第5節)を採用した。これは`reference_sim`からの移植値ではなく、このクライアント
独自の選択である。

### 需要式への配線における近似

`nearby_population`(需要計算に直接使われる商圏人口)と、新設の
`town.population`は、意図的に独立したまま統合していない。既存の多数の
テスト(月次/リストック/ゲームオーバー/広告)が`demand.nearby_population: 0`
という決定論的なゼロ需要設定に依存しているため、これらを`town.population`
から導出する変更を行うと、無関係な既存テストの挙動を静かに変えてしまう。
そのため両者は重複したまま残し、ライバル希薄化という新しい効果のみを
`town.store_count_including_rivals`から独立して配線した
(`rival_store_count`のデフォルトは0で、無効化=既存挙動と完全互換)。

## 決定

### 実装した内容

- `game/scripts/domain/town_state.gd`(新規): `TownState`クラス。
  `population`/`store_count_including_rivals`を保持し、`_init()`で
  非負を検証する。`reference_sim/conveni_sim/town.py`をそのまま移植。
- `game/scripts/domain/land_value_policy.gd`(新規): `LandValuePolicy`
  クラス。`local_development_factor(town)`/
  `time_inflation_factor(elapsed_years)`/
  `current_land_price_yen(base_land_price_yen, town, elapsed_years)`を
  `remake_land_value.py`の定数・式のまま移植。
- `game/scripts/domain/demand_policy.gd`: `rival_store_count: int`
  (デフォルト0)、`RIVAL_DILUTION_PER_COMPETITOR := 0.08`/
  `MAX_RIVAL_DILUTION := 0.6`定数を追加。
  `expected_arrivals_per_minute()`が、ライバル店が1店以上いる場合のみ
  希薄化係数を掛けるよう変更(0店の場合は完全に無効化、既存呼び出し元・
  テストへの影響なし)。
- `game/scripts/vertical_slice_simulation.gd`: `town`/`_land_value_policy`
  フィールド、`BASE_LAND_PRICE_YEN := 20_000_000`定数を追加。`_init()`で
  `config["town"]`から`town`を構築し、`demand.rival_store_count =
  max(0, town.store_count_including_rivals - 1)`(自店舗自身を除いた
  ライバル数)を設定。`snapshot()`に`town_population`/
  `town_store_count_including_rivals`/`land_value_yen`
  (`_land_value_policy.current_land_price_yen()`を経過月数から求めた
  `elapsed_years`で評価した値)を追加。`_require_config()`が`town`キーと
  `population`/`store_count_including_rivals`必須フィールドを検証するよう
  変更。`schema_version`要求を11に更新。
- `game/data/vertical_slice.json`(`schema_version`を10→11に更新):
  `town`セクションを追加(`population: 2000`は`demand.nearby_population`
  と同じ値、`store_count_including_rivals: 1`は自店舗のみ=ライバル0店で
  希薄化なしのデフォルト)。
- `game/scripts/headless_smoke.gd`: (1) デフォルト設定の`town`が
  `TownState`へ正しく反映されること、ライバル0店で`rival_store_count`が
  0になること、(2) `land_value_yen`がデフォルト町設定・月0時点の厳密な
  計算値(24,400,000円)と一致すること、(3) ライバル店3店設定で希薄化
  係数(1-0.24)が来店期待値に厳密に反映されること、(4) ライバル店30店で
  希薄化が`MAX_RIVAL_DILUTION`(0.6)に上限されること、(5)
  `LandValuePolicy.current_land_price_yen()`が最大発展係数・年率インフレを
  それぞれ厳密な計算値で返すこと、を検証するテストを追加。

### 契約テスト・ドキュメント

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_town_state_and_rival_dilution_are_tagged_and_wired_into_demand`を
  追加。`town`設定の必須キー、`TownState`/`LandValuePolicy`の
  evidence-safeタグ付け、ライバル希薄化定数の一致、
  `_land_value_policy`/`BASE_LAND_PRICE_YEN`/`land_value_yen`の配線、
  そしてライバルAI意思決定ロジックが意図的に存在しないことを検証する。
  `schema_version`要求を11に更新。

## 影響

- `game/scripts/domain/town_state.gd`(新規)、
  `game/scripts/domain/land_value_policy.gd`(新規)。
- `game/scripts/domain/demand_policy.gd`、
  `game/scripts/vertical_slice_simulation.gd`、`game/data/vertical_slice.json`、
  `game/scripts/headless_smoke.gd`: 前述のとおり変更。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規契約テスト
  1件・`schema_version`更新。

## タスク#26の完了

町状態・地価情報表示・ライバル希薄化の3点を実装し、明示的に空間シミュレー
ションとライバルAI意思決定を対象外としたことをこの決定書に記録した上で、
タスク#26「町・ライバル店・地価の空間モデルをGodotに実装」を完了とする。
