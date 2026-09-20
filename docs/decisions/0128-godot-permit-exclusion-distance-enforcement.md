# 0128: 販売許可の排他距離ルールをGodot側で実際に配線(タスク#59)

## 背景

決定書0127(タスク#58)は`reference_sim`側に`remake_town_spatial.py`を
新設し、実習マニュアル book pages 6-7の距離図(店舗建設5マス、たばこ/
酒類/薬類の販売許可排他距離7/11/15マス、いずれもCONFIRMED_OFFICIAL)を
実際に距離計算へ適用する純粋関数を用意した。ただし同決定書は明示的に
「Godot版(`game/`)への移植は行っていない。特にtry_purchase_permit()
への実際の排他距離チェックの配線は、ライバル店エンティティ(位置・
保有許可)をこのクライアントにまず追加する必要があり、これは別タスク
とする」としていた。

この`exclusion_distance_tiles`という値自体は`game/data/vertical_slice.json`
の各permitエントリに(タスク#26の時点から)evidence_noteとして
「not enforced here: no town/rival spatial model exists in this client
yet (see task #26)」と明記されたまま、実際の数値フィールドとしては
一切存在していなかった。

## 決定

### `game/scripts/domain/town_spatial.gd`を新設

`remake_town_spatial.py`のうち、Godot側に実際の呼び出し元が存在する
部分(`can_acquire_permit_at()`とその内部で使う`chebyshev_distance_tiles()`)
のみを移植した。`trade_area_overlap_ratio()`はGodot側にライバルAIの
判断ループが存在しないため移植していない(reference_sim側の「呼び出し元の
ないコードを積まない」という原則をGodot側でも踏襲)。

### `VerticalSliceSimulation`への配線

- `_player_store_position: Vector2i`: プレイヤー自身の店舗の位置。この
  クライアントには町・地図の空間シミュレーション自体が存在しない
  (決定書0095)ため、これは実在するマップ上の座標ではなく、距離計算の
  ための基準点に過ぎないREMAKE_BALANCED_DEFAULTな原点(`[0, 0]`)である。
- `_rival_stores: Array[Dictionary]`: `town.rival_stores`から構築される
  ライバル店のロースター(id・位置・保有許可)。既定シナリオでは空配列
  (`store_count_including_rivals=1`が「自店舗のみ」を意味するのと同じ
  規約で、no-op)。どの位置に何軒のライバル店が存在し、どの許可を保有
  するかを示す情報源は一切存在しないため、このプロジェクト自身が
  勝手に埋めることはせず、呼び出し元(設定ファイル、またはテスト)が
  供給した値のみを反映する。
- `try_purchase_permit()`: 新規`_can_acquire_permit(permit_id)`ヘルパーを
  経由して、`_rival_stores`のうち当該許可を既に保有する店舗の位置を
  抽出し、`TownSpatial.can_acquire_permit_at()`へ渡す。既存のcash/
  already-held等のガードと同じ位置(残高チェックより前)に追加した。

### `game/data/vertical_slice.json`の更新

- 各permitエントリへ`exclusion_distance_tiles`(7/11/15)を実際の数値
  フィールドとして追加し、evidence_noteを「now enforced」に更新。
- `town`セクションへ`player_store_position: [0, 0]`と`rival_stores: []`
  (既定は空、no-op)、および新規`town_spatial_evidence_note`を追加。

## テスト

- `game/scripts/headless_smoke.gd`: 新規シナリオ2件を追加。(1)
  近傍(距離6、半径7未満)のライバルがたばこを保有している場合に
  `try_purchase_permit("tobacco")`が拒否されること、同じライバル構成でも
  酒類(半径11)・薬類(半径15)は無関係なため受理されること。(2)
  ライバルをちょうど境界(距離7、半径7)に置いた場合はたばこが受理される
  こと(排他は「未満」であり「以下」ではない、という境界条件の検証)。
  Godot 4.3公式バイナリで1106ステップ(タスク#58時点の1046から、新規
  シナリオ分増加)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_permit_exclusion_distance_is_wired_and_confirmed_official`を
  追加。evidence_noteのタグ、`exclusion_distance_tiles`の数値、
  `town_spatial.gd`/`vertical_slice_simulation.gd`の配線文字列を検証。
  フルスイート697件(新規テスト関数1件追加)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/domain/town_spatial.gd`(新規)。
- `game/scripts/vertical_slice_simulation.gd`: `_player_store_position`/
  `_rival_stores`フィールド、`_can_acquire_permit()`を新規追加。
  `try_purchase_permit()`/`_require_config()`/`_init()`を更新。
- `game/data/vertical_slice.json`: 各permitエントリへ
  `exclusion_distance_tiles`を追加。`town`セクションへ
  `player_store_position`/`rival_stores`/`town_spatial_evidence_note`を
  追加。
- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  テストを追加。

## 明示的に対象外とした限界

- 店舗建設の最小距離ルール(5マス、`TownSpatial.
  STORE_CONSTRUCTION_MIN_DISTANCE_TILES`)は`town_spatial.gd`に移植した
  ものの、Godot側では一切配線していない――`try_expand_chain()`に実際の
  店舗配置メカニクス(座標を指定して新店舗を建てる操作)が存在しない
  ため、適用対象がない。
- `trade_area_overlap_ratio()`(商圏重なり比率)はGodot側に移植して
  いない――ライバルAIの判断ループ自体がこのクライアントに存在しない
  ため、呼び出し元がない。
- ライバル店の実際のスポーン・配置・保有許可の決定ロジックは実装して
  いない。`_rival_stores`は設定ファイル(またはテスト)が供給した
  静的なデータをそのまま反映するのみで、このクライアント自身がライバル
  店を生成・移動・行動させることは一切ない。
- 治安施設(交番/消防署)のセキュリティボーナスは、本タスクが対応した
  「点対点距離」とは異なる計算(施設の足跡矩形と店舗の半径円との面積
  重なり)が必要であり、今回も対応していない。
