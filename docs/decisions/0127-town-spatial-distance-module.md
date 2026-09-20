# 0127: 町の空間モデル(店舗間距離)着手 -- `remake_town_spatial.py`新設(タスク#58)

## 背景

決定書0095(タスク#26)は、町・地図の空間シミュレーション(タイル座標を
持つ町マップ、施設配置、距離ベースの商圏重複)そのものを実装することを
明示的に見送った。理由は「`reference_sim`自身も空間モデルを持たない。
これを発明すると、証拠のない数値は推測とタグ付けするという原則を逸脱し、
空間モデルという最も証拠の薄い領域を無根拠に埋めることになる」という
原則的なものだった。

ユーザーから新たに4分割された原資料PDF(実習マニュアル/クイックリファ
レンスの再スキャン)を受け取り、「資料を参考にしながら空間モデルに着手
して」との明示的な指示を受けた。実習マニュアル book pages 6-7を直接
再読し、以下を確認した(いずれも既に`reference_sim/conveni_sim/
baseline_data.py`の`_PERMIT_FEE_AND_DISTANCE_YEN_TILES`のコメントとして
記録済みだったが、値そのものは今回の再読で独立に再確認した):

- 店どうしの距離を示す同心円状の図(book page 7)は、店舗を中心に
  5/7/11/15タイルの4つの輪を示し、それぞれ「店建設可能」「たばこ販売
  可能」「酒類販売可能」「薬類販売可能」に対応する。
- 「販売許可には範囲があり、すでに販売許可を取っている店の範囲内では
  売ることができない」(book page 9)。
- book page 74は、この排他が双方向(自分の許可が近隣ライバル店の同じ
  許可取得を妨げる)であることを確認する具体例を示す。

これらの数値(5/7/11/15タイル)自体は`PermitDefinition.exclusion_
distance_tiles`として既にCONFIRMED_OFFICIALで移植済みだったが、実際に
2点間の距離を計算してこの規則を適用する関数はどこにも存在せず、
`game/data/vertical_slice.json`の該当permitのevidence_noteには
「not enforced here: no town/rival spatial model exists in this client
yet (see task #26)」と明記されたままだった。同様に、`TRADE_AREA_RADIUS_
TILES`(来店手段別の商圏半径、book page 31、CONFIRMED_OFFICIAL)と
`RivalPolicyInputs.trade_area_overlap_ratio`(呼び出し元が計算して渡す
ことになっている抽象的な0.0-1.0値)も、実際にその値を計算する手段が
存在しないまま宙に浮いていた。

## 決定

### `reference_sim/conveni_sim/remake_town_spatial.py`を新設

決定書0095が対象外とした「町マップ全体の空間シミュレーション」(マップ
サイズ、施設配置、人口成長式)には一切踏み込まない。その代わり、
「2つの店舗の位置(Position、呼び出し元が既に知っているものとする)が
与えられたときに、既存のCONFIRMED_OFFICIALな距離・半径データをどう
適用するか」という、より狭い純粋関数の層のみを追加した:

- `chebyshev_distance_tiles(a, b)`: 2点間の距離計算。
- `STORE_CONSTRUCTION_MIN_DISTANCE_TILES = 5`: 従来コメントのみだった
  値を、実際にテスト可能な名前付き定数に昇格。
- `can_construct_store_at(candidate, existing_store_positions)`:
  店舗建設の最小距離規則。
- `PERMIT_EXCLUSION_DISTANCE_TILES`: 既存の`PERMITS`から動的に構築
  (数値の二重管理を避ける)。
- `can_acquire_permit_at(permit_id, candidate, other_permit_holder_positions)`:
  販売許可の排他距離規則。
- `TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD`: 既存の`TRADE_AREA_RADIUS_
  TILES`から動的に構築。
- `trade_area_overlap_ratio(position_a, radius_a, position_b, radius_b)`:
  2つの円形商圏の幾何学的重なり比率(標準的な円-円交差面積の公式、小さい
  方の円の面積で正規化)。`remake_rival_policy.RivalPolicyInputs.trade_
  area_overlap_ratio`が要求していた形そのものを、初めて実際に計算できる
  ようにした。

### REMAKE_BALANCED_DEFAULTな設計選択(書籍に明記のない部分)

- **距離指標(チェビシェフ距離)**: 書籍はタイル単位の半径を示すが、
  斜め方向のタイルを1として数えるか(チェビシェフ)、約1.41として数える
  か(ユークリッド)は明記されていない――既存の`exclusion_distance_tiles`
  自身のevidence_noteが既にこの曖昧さを指摘済み。このプロジェクトの
  店内移動が既にステップ単位(斜めも1歩)である慣習に合わせ、チェビシェフ
  距離を採用した。
- **商圏重なり比率の正規化方法**: `TradeAreaRadiusEntry`自身のevidence_
  noteが「重なりの解決方法(比例配分か、近い方が総取りか、等)は書籍に
  一切記載がない」と既に明記している。「小さい方の円の面積に対する
  重なり面積の比率」という幾何学的に自然な正規化を採用したが、これは
  復元されたオリジナル仕様ではない。

### 実際に呼び出し元が存在することの確認

決定書0095は「ライバル店舗という実体が存在しないため、移植しても呼び出し
元が存在せず、動かないコードを積むだけ」という理由でライバルAI
(`remake_rival_policy.py`)の配線を見送っていた。今回、`trade_area_
overlap_ratio()`を実際に`RivalPolicyInputs`へ渡す統合テストを
`test_remake_rival_policy.py`に追加し、この「呼び出し元がない」という
状態を解消した(テストコード自身が呼び出し元であり、空間データが実際に
ライバル判断へ影響することを検証する)。

## テスト

- `reference_sim/tests/test_remake_town_spatial.py`(新規): 確認済み
  定数値、チェビシェフ距離、店舗建設可否、許可取得可否、商圏重なり比率
  (対称性・境界条件・確認済み半径を使った具体例含む)を検証。26件。
- `reference_sim/tests/test_remake_rival_policy.py`: 統合テスト2件を
  追加(離れた店舗は重なり0で競争圧力が発生しないこと、完全に重なる
  店舗では赤字ブランチが撤退し得ること)。
- フルスイート696件PASS、xfail 1件。
- Godot側(`game/`)は無変更のため`headless_smoke.gd`は回帰確認のみ
  (1046ステップ、変化なし)。

## 実装ファイル

- `reference_sim/conveni_sim/remake_town_spatial.py`(新規)。
- `reference_sim/tests/test_remake_town_spatial.py`(新規)。
- `reference_sim/tests/test_remake_rival_policy.py`: 統合テストを追加。

## 明示的に対象外とした限界

- 町マップ全体の空間シミュレーション(マップサイズ、座標系の原点・単位、
  人口成長式)は今回も一切発明していない――決定書0095の判断を継続。
- どの位置に何軒のライバル店が存在するか、各ライバル店がどの販売許可を
  保有しているかは、依然としてどの情報源にも記載がなく、本モジュールは
  一切決めない(呼び出し元が供給する前提のまま)。
- `game/`(Godot版)への移植は行っていない。特に`try_purchase_permit()`
  への実際の排他距離チェックの配線は、ライバル店エンティティ(位置・
  保有許可)をこのクライアントにまず追加する必要があり、これは別タスク
  とする。
- 交番/消防署のセキュリティボーナス(`SecurityFacilityCoverage`、
  PROJECT_MEMORY.md第21.3節で既にCONFIRMED_OFFICIALな式は判明済み)は、
  本モジュールが対応する「店舗間の点対点距離」とは異なる計算(施設の
  足跡矩形と店舗の半径円との面積重なり)が必要であり、今回は対応して
  いない。
