# 0096: `game/`(Godot)に店舗評価(★ランク)をゲームループへ反映(タスク#27)

## 背景

タスク#27「店舗評価をゲームループへ反映」に着手した。`reference_sim`側には
既に評価関連の3モジュールが揃っていた:

- `conveni_sim/store_rating.py`: 攻略本「オールテクニックガイド」評価関連
  ページ(書籍頁74-75)を直接転記した、内部評価値(0-100)↔★ランク(0-5)の
  変換表と、月次の昇格/降格判定式。**CONFIRMED_OFFICIAL**(このプロジェクト
  独自の推測ではなく、攻略本の数値そのもの)。
- `conveni_sim/store_value.py`: サービス値/セキュリティ値/清掃値の計算式
  (社員のスキル値の平均・合計 × 店舗規模別基準値 + 什器の付加効果)。同じく
  攻略本の直接転記で**CONFIRMED_OFFICIAL**。
- `conveni_sim/store_evaluation.py`: 上記2モジュールを既存のスタッフ/
  グリッド状態と橋渡しするオーケストレーター。

### スコープの決定

`store_evaluation.py`をそのまま移植しようとすると、以下の未整備な前提に
突き当たった:

1. **社員スキル値**: `service_skill`/`security_skill`/`cleaning_skill`の
   実際の値は、`reference_sim/conveni_sim/staff.py`の成長モデル(仕事イベント
   カウント・店長教育補正込み)がなければ埋まらないが、この成長モデル自体は
   `reference_sim`にしか実装されておらず、Godot移植ロードマップ(タスク#21-26)
   には一度も含まれていなかった(見落としではなく、今回気づいた欠落)。
2. **店舗規模区分(size_tier)**: 攻略本は10×10/12×12/14×14の3区分しか
   定義していないが、このvertical sliceの店舗は7×6タイルで、いずれにも
   一致しない。
3. **セキュリティ施設補正**: 交番/消防署の16×16タイル範囲内カバレッジ
   ボーナスは、対応する施設・空間検索がGodot側にまだ存在しない。
4. **価格変更率(price_change_pct)**: 攻略本の昇格/降格表が参照する項目
   だが、このvertical sliceには価格設定機能自体が存在しない。

タスク#26と同じ方針で、これらを「発明せず、静的なプレースホルダーとして
明示タグ付けした上で、実際にゲームループへ反映される最小限の実装」に
絞った:

1. **`store_rating.gd`/`store_value.gd`**: 攻略本の閾値・定数をそのまま
   逐語移植(CONFIRMED_OFFICIAL)。
2. **`StaffState`に3スキルフィールドを追加**: 成長モデルは実装せず、
   config供給の静的値(REMAKE_BALANCED_DEFAULT)とする。
3. **`store.size_tier`をconfigに追加**: "small"を採用(REMAKE_BALANCED_DEFAULT
   の店舗規模マッピング、7×6タイルがいずれの公式区分にも一致しないための
   便宜的選択と明記)。
4. **セキュリティ施設補正は実装しない**: `compute_security_value()`から
   `facility_coverage`パラメータ自体を省略(常にボーナス0相当)。
5. **`price_change_pct`は常に0**: 価格変更機能が存在しないため「基準価格
   からの変化なし」として扱う。

### 明示的に実装しなかったもの

- 社員スキル成長システムそのもの(仕事イベントカウント、店長教育補正、
  スタミナ)。`reference_sim/conveni_sim/staff.py`に存在するが、Godot側は
  今回も含め一度も移植していない別タスクの範囲。
- 交番/消防署のセキュリティ施設補正(空間検索が前提のため)。
- 月次評価以外の単発イベントによる評価増減(お客に怒られる1/6の確率-1、
  万引き-1、寄付+5)。`store_rating.gd`は定数(`ANGRY_CUSTOMER_DOWNGRADE_POINTS`
  等)だけ移植したが、これらのトリガーとなる怒り客/万引きイベント自体が
  Godot側に実装されていないため、呼び出し箇所は用意していない。
- 新規開店時の内部評価値の確定初期値(攻略本は明記していない)。`popularity`
  の前例(決定書0094)に倣い0を採用。

## 決定

### 実装した内容

- `game/scripts/domain/store_rating.gd`(新規): `star_rank_for_internal_value()`、
  `evaluate_monthly_rating_change()`、昇格/降格閾値表(★1-5)、
  `UPGRADE_MIN_CRITERIA_MET`/`UPGRADE_POINTS`/`DOWNGRADE_POINTS_PER_CRITERION`/
  `ANGRY_CUSTOMER_DOWNGRADE_POINTS`/`SHOPLIFTING_DOWNGRADE_POINTS`/
  `DONATION_UPGRADE_POINTS`定数。すべて`store_rating.py`の逐語移植。
- `game/scripts/domain/store_value.gd`(新規): `compute_service_value()`/
  `compute_security_value()`/`compute_cleaning_value()`、
  `STORE_SIZE_VALUE_MULTIPLIER`(small=1.5/medium=1.65/large=1.8)。
  `store_value.py`の逐語移植(セキュリティ施設補正パラメータのみ省略)。
- `game/scripts/domain/staff_state.gd`: `service_skill`/`security_skill`/
  `cleaning_skill`フィールドを追加(config供給、静的、成長なし)。
- `game/scripts/vertical_slice_simulation.gd`: `internal_rating_value`/
  `star_rating`フィールド、`_store_rating`/`_store_value`/`_store_size_tier`
  内部フィールドを追加。`reset()`で`internal_rating_value = 0`から開始。
  `_settle_month_end()`が月末ごとに`_evaluate_store_rating(monthly_sales_yen)`
  を呼ぶよう変更(`monthly_sales_yen`は代表4日間の売上高を`MONTH_MULTIPLIER`
  で月換算した値、既存の4×8集計則(決定書0090)と同じ考え方)。
  `_evaluate_store_rating()`は全社員のスキル値・配置済みアメニティ什器の
  `service_bonus`合計・`_store_size_tier`から3値を算出し、
  `price_change_pct=0`とともに評価式へ渡し、`internal_rating_value`/
  `star_rating`を更新、`store_rating_evaluated`イベントを記録する。
  `try_purchase_fixture()`が什器インスタンスに`catalog_id`を記録するよう
  変更(`service_bonus`をカタログから引けるようにするため)。`snapshot()`に
  `internal_rating_value`/`star_rating`を追加。`_require_config()`が
  `store.size_tier`と各社員の3スキルフィールドを検証するよう変更。
  `schema_version`要求を12に更新。
- `game/data/vertical_slice.json`(`schema_version`を11→12に更新):
  `store.size_tier: "small"`、社員2名に`service_skill: 20`/
  `security_skill: 15`/`cleaning_skill: 15`を追加。潮アメニティ什器3種の
  `evidence_note`を、`service_bonus`が本タスクで消費されるようになった旨に
  更新。
- `game/scripts/headless_smoke.gd`: (1) `star_rank_for_internal_value()`の
  全ブレークポイント、(2) `evaluate_monthly_rating_change()`の昇格・降格
  判定基準数と結果値、(3) `compute_service_value`/`compute_security_value`/
  `compute_cleaning_value`の厳密な計算値、(4) 実際のシミュレーションで
  1ヶ月経過後に`store_rating_evaluated`イベントが1回だけ記録され、その
  `monthly_sales_yen`/`service_value`/`security_value`/`cleaning_value`が
  厳密な期待値と一致し、`star_rating`が常に
  `star_rank_for_internal_value(internal_rating_value)`と整合すること、を
  検証するテストを追加。

### 契約テスト・ドキュメント

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_store_rating_ports_confirmed_guide_thresholds_into_the_monthly_loop`
  を追加。`store.size_tier`・社員スキル config の存在、
  `store_rating.gd`/`store_value.gd`のCONFIRMED_OFFICIALタグ付けと閾値の
  一致、`StaffState`のREMAKE_BALANCED_DEFAULTタグ、月次ループへの配線、
  そしてセキュリティ施設補正が意図的に存在しないことを検証する。
  `schema_version`要求を12に更新。

## 影響

- `game/scripts/domain/store_rating.gd`(新規)、
  `game/scripts/domain/store_value.gd`(新規)。
- `game/scripts/domain/staff_state.gd`、
  `game/scripts/vertical_slice_simulation.gd`、`game/data/vertical_slice.json`、
  `game/scripts/headless_smoke.gd`: 前述のとおり変更。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規契約テスト
  1件・`schema_version`更新。

## タスク#27の完了

攻略本確定済みの★評価式・閾値表を忠実に移植し、月次ゲームループへ実際に
反映した上で、社員スキル成長システムやセキュリティ施設補正など、前提と
なる別領域の未整備な部分を明示的に対象外としたことをこの決定書に記録し、
タスク#27「店舗評価をゲームループへ反映」を完了とする。
