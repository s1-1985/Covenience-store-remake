# 0126: 店舗データの建物面積内訳(総面積/建物全体/床面積/店外スペース)を移植(タスク#57)

## 背景

`docs/research/strategy-guide-shopkeeper-manual-part2-2026-09-19.md`
第4.1節(book pages 106-109の店舗データ表クロスチェック)は、
`reference_sim/conveni_sim/baseline_data.py`の`STORE_VARIANTS`が既に
`construction_price_yen`/`editable_floor`(店舗内、什器配置グリッド)を
保持している一方で、同じ表の他の列――`総面積`(total area)・
`建物全体`(whole building)・`床面積`(floor area)・
`店外スペース`(exterior space)――は一切`StoreVariant`のフィールドとして
存在しない(移植されていない)ことを指摘していた。これは全6店舗分
CONFIRMED_OFFICIALであり、既存の`本2.pdf`ソース(移植済みの
`construction_price_yen`/`editable_floor`の値の出典)と全項目一致する
ことも確認済みで、単純にデータとして未移植だっただけである
(`PROJECT_MEMORY.md`第21.3節「Facility/scenario data」の一項目)。

## 決定

### `StoreVariant`へ4フィールドを追加

`reference_sim/conveni_sim/models.py`の`StoreVariant`データクラスへ、
`total_area_tiles`/`whole_building_area_tiles`/`floor_area_tiles`/
`exterior_space_tiles`(いずれも`Optional[EvidenceValue] = None`)を追加。
`baseline_data.py`の`STORE_VARIANTS`タプル、全6エントリ(店舗1〜6)へ
研究ドキュメントの表からそのままCONFIRMED_OFFICIALな値を追加した:

| ID | 総面積 | 建物全体 | 床面積 | 店外スペース |
|---|---:|---:|---:|---:|
| small_top / small_bottom | 100 | 70 | 40 | 30 |
| medium_top / medium_bottom | 144 | 108 | 70 | 36 |
| large_top / large_bottom | 196 | 154 | 108 | 42 |

`editable_floor`(什器配置に使う店舗内グリッド)とは別の指標であり、
単純にその幅×高さから導出できる値ではない(例: small_topの
`editable_floor=(5,8)`→40だが`total_area_tiles=100`)ことをテストで
明示的に確認した。

### 「情報として保持するが未消費」のパターンを踏襲

`land_value_yen`(決定書0095)や什器の`service_bonus`/
`maintenance_yen_per_day`が既に確立している「証拠に基づくデータを
消費先の機構が存在する前に先行して保持する」という既存パターンを
そのまま踏襲した。`reference_sim`にもGodot版(`game/`)にも、現状
複数店舗バリアント(店舗1〜6)を選択・切り替える仕組み自体が存在しない
(Godot版は`small_top`のみを固定プロトタイプとして採用、決定書0100参照)
ため、これらの新フィールドはどちらの側でも一切消費されない
――参照専用データとして保持するのみである。この理由により、Godot側
(`game/`)には一切変更を加えていない(移植先は`reference_sim`のみ)。

## テスト

- `reference_sim/tests/test_baseline.py`: 新規
  `test_store_variant_building_area_breakdown_matches_the_guide`を追加。
  全6バリアント分の4フィールドの値とevidence levelを検証し、
  `total_area_tiles`が`editable_floor`の幅×高さの単純な導出値ではない
  ことも確認。フルスイート668件(新規テスト関数1件追加)、xfail 1件、
  全てPASS。
- Godot側(`game/`)は無変更のため、`headless_smoke.gd`は実行のみ
  (前回の1046ステップから変化なし、回帰なしを確認)。

## 実装ファイル

- `reference_sim/conveni_sim/models.py`: `StoreVariant`へ4フィールドを
  追加。
- `reference_sim/conveni_sim/baseline_data.py`: `STORE_VARIANTS`全6
  エントリへ値を追加。
- `reference_sim/tests/test_baseline.py`: 新規テストを追加。

## 明示的に対象外とした限界

- Godot版(`game/`)への移植は行っていない――複数店舗バリアントの
  選択・切り替え機構自体が存在しないため、消費先がない。
- large tier(店舗5/6)の`総面積=196`(=14×14)が既存の内部矛盾フラグ
  (店舗データ表の14×14 vs. 各ケーススタディの16×16キャプション、
  `store_value.py`のコメント参照)を再確認したのみで、解消はしていない
  ――今回のタスクの対象外。
- `建物全体`/`床面積`/`店外スペース`の各数値が具体的に何を消費する
  ゲームメカニクスに使われるべきかは未確定・未実装のままである
  (情報表示すら現時点では行っていない、純粋な参照データ)。
