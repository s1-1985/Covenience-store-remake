# 0130: 治安施設(交番/消防署)の空間探索を類推ベースで実装(タスク#61)

## 背景

`reference_sim/conveni_sim/store_value.py`の`SecurityFacilityCoverage`は
既に確認済みのボーナス公式(交番: 1エリアごとに+10、最大+40; 消防署:
1エリアごとに+5、最大+30、店舗周囲16×16エリア範囲内)を実装していたが、
そのクラス自身のdocstringが「施設のどのエリアタイルがその範囲内にある
かを数える空間探索そのものは対象外(out of scope)」と明記していた
――呼び出し元がその個数を既に数えて渡してくることが前提だった。

タスク#60と同じ、ユーザーからの指摘(証拠が完全には揃わなくても、
既に確認済みの関連要素から類推してこのプロジェクト自身が埋めていく、
CLAUDE.md優先順位2/3)を引き続き適用し、この「空間探索」自体を実装した。

必要な確認済みデータは全て既に`baseline_data.py`に揃っていた:

- 交番(police_box)の足跡: `(2, 2)`、CONFIRMED_OFFICIAL。
- 消防署(fire_station)の足跡: `(2, 3)`、CONFIRMED_OFFICIAL。
- 範囲: `SECURITY_FACILITY_RANGE_TILES = 16`(店舗周囲16×16エリア)。

## 決定

### `remake_town_spatial.facility_area_tiles_within_range()`を新規追加

店舗の位置・施設の位置・施設の足跡(幅×高さ)・範囲(タイル数)を受け取り、
その施設の足跡のうち何タイルが店舗からその範囲内(タスク#58で既に採用
した`chebyshev_distance_tiles()`基準)にあるかを数える。この個数を
そのまま`SecurityFacilityCoverage(police_box_area_tiles=..., 
fire_station_area_tiles=...)`へ渡せば、既存の確認済みボーナス公式が
そのまま機能する。

### 証拠レベルの内訳

- **施設の足跡サイズ(2x2/2x3)・範囲(16タイル)・レート(+10/+5)・
  上限(+40/+30)**: いずれもCONFIRMED_OFFICIAL(既存データそのまま)。
- **「16×16エリア範囲内」を「店舗位置からチェビシェフ距離16以内」と
  解釈する**という選択: `store_value.py`自身の既存コメント
  ("within this many tiles of the store")が既にこの解釈を暗黙のうちに
  採用していたものであり、本タスクが新たに導入した解釈ではない――
  ただしこれ自体が書籍の正確な領域形状・基準点を明記したものではない
  ことを明示的に記録した(タスク#58の距離指標に関する既存の曖昧さの
  注記と同種)。

### 統合テスト

`test_remake_town_spatial.py`へ、この新関数の出力を実際に
`SecurityFacilityCoverage`へ渡し、確認済みボーナス公式(+10/タイル、
+5/タイル)が正しく機能することを検証する統合テストを追加した――
`SecurityFacilityCoverage.*_area_tiles`フィールドが実際の位置情報から
計算された値を受け取る、初めての呼び出し元である。

## テスト

- `reference_sim/tests/test_remake_town_spatial.py`: 新規
  `FacilityAreaTilesWithinRangeTests`クラスを追加(8件)。範囲内に完全に
  収まる施設・範囲境界をまたぐ施設・範囲外の施設・より大きい足跡
  (消防署2x3 vs 交番2x2)・範囲0での境界条件・負の足跡/範囲の拒否、
  そして`SecurityFacilityCoverage`との統合を検証。
- フルスイート713件(新規8件)、xfail 1件、全てPASS。
- Godot側(`game/`)は無変更のため`headless_smoke.gd`は回帰確認のみ
  (1106ステップ、変化なし)。

## 実装ファイル

- `reference_sim/conveni_sim/remake_town_spatial.py`:
  `facility_area_tiles_within_range()`を新規追加。
- `reference_sim/tests/test_remake_town_spatial.py`: 新規テストクラスを
  追加。

## 明示的に対象外とした限界

- `game/`(Godot版)への移植は行っていない――このクライアントには
  警備施設(交番/消防署)を町マップ上に誘致・配置する仕組み自体が
  存在しない(`TownState`は非空間的なスカラーのみ、決定書0095)ため、
  実際に呼び出せる場所がまだない。
- 「16×16エリア範囲内」の正確な領域形状(店舗を中心とした正方形か、
  店舗の特定の角を基準とした矩形か等)は今回も解決していない――
  既存のチェビシェフ距離ベースの解釈をそのまま踏襲したのみで、新たな
  資料的裏付けを得たわけではない。
- 施設が実際に町のどこに誘致・配置されるかを決定するロジック(誘致
  条件・確率・配置アルゴリズム)は実装していない――本関数は既に分かって
  いる位置を受け取るのみ。
