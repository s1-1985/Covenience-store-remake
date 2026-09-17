# 0087: 未実装の8アルゴリズムを`REMAKE_BALANCED_DEFAULT`として実装する

## 背景

`docs/research/strategy-guide-full-decode-2026-09-16.md`セクション41は、攻略本から
「存在は確定したが数式は未確定」と判定された22項目を列挙している。このうち以下の8項目は
本セッション以前は「実装境界(Protocol/型)のみ存在し、具体的なロジックは一切ない」状態
だった(`customer_demand.py`/`customer_purchase_policy.py`/`staff_rest_recovery.py`等の
Protocolクラスに具象実装が存在しない、または対応モジュール自体が未作成)。

ユーザーから「判明しているパラメーターの数値の傾向から係数を作り、未実装アルゴリズムを
先に一通り実装し、プレイしてみておかしい数値を直す」という方針の提案があり、承認の上で
「全部やるんだよ」と全8項目の実装を明示的に指示された。

この方針は`models.py`の`EvidenceLevel`列挙型に元々存在していた`REMAKE_BALANCED_DEFAULT`
(既存の値だが、本セッション以前は未使用)にちょうど対応する。「捏造しない」という
`reference_sim`全体の原則と矛盾させないため、以下の運用ルールで実装した。

## 決定

### 運用ルール

1. 新規モジュールは`reference_sim/conveni_sim/remake_*.py`という命名で作成し、既存の
   evidence-safeなモジュール(`store_value.py`等、攻略本で数式が確定している8公式)とは
   物理的に別ファイルに分離する。
2. 各モジュールの先頭に「REMAKE_BALANCED_DEFAULT house rule」というコメントブロックを置き、
   (a) 攻略本のどの記述が「要因の存在」を確認しているか、(b) その要因をどう数式に組み合わせた
   かが本モジュール独自の推測であるか、を明記する。理由の要らない箇所には理由を書かない。
3. 既存コードに確定値として書かれている数値(価格・スキル成長量等)を基準点として使う場合は
   その数値を引用し、根拠のない乱数は避ける。
4. 既存モジュールが定義済みのProtocol(`CustomerDemandPolicy`/`CustomerPurchasePolicy`/
   `RestRecoveryBonusPolicy`)がある場合はそれを実装する。Protocolが存在しない領域
   (ライバルAI、地価変動)は新規に最小限のインターフェースを定義する。
5. Protocolの`Context`データクラスに実装に必要な情報(レイアウト座標、敏捷性等)が
   欠けている場合、Protocol自体は変更せず、具象クラスのコンストラクタ引数として
   補う(`staff_id -> agility`の辞書等)。

### 実装した8モジュール

| # | セクション41の項目 | モジュール | 実装対象 |
|---|---|---|---|
| 1 | 商圏による顧客捕捉/顧客分配(一部) | `remake_customer_share.py` | `compute_customer_share_percent` — 人気/サービス/清掃/警備/品揃え/営業時間の加重平均、未確定要因は0扱いせず除外・再正規化、ライバル希釈、悪天候ペナルティ |
| 2 | 価格による購入/来店反応、人気による来店反応、天候・季節需要補正 | `remake_demand_policy.py` | `RemakeBalancedDemandPolicy`(`CustomerDemandPolicy`実装) — 人口比来店率、悪天候来店倍率 |
| 3 | ついで買い確率、価格弾力性 | `remake_purchase_policy.py` | `RemakeBalancedPurchasePolicy`(`CustomerPurchasePolicy`実装) — 主目的購入/ついで買い確率、`CUSTOMER_VISIT_SCHEDULE`の所持金レンジを基準にした価格弾力性 |
| 4 | 社員能力成長量、店長教育補正 | `remake_staff_growth.py` | `RemakeBalancedStaffGrowthResolver` — 未確定スキル×タスクの組へ既存確定値を拡張、教育値ベースのボーナス確率 |
| 5 | 体力消費/回復(敏捷性ボーナス) | `remake_rest_recovery_policy.py` | `RemakeBalancedRestRecoveryBonusPolicy`(`RestRecoveryBonusPolicy`実装) — 敏捷性を確率に線形変換 |
| 6 | 犯罪発生確率、火災/災害発生確率 | `remake_incident_policy.py` | `RemakeBalancedIncidentPolicy` — `store_events.py`の確定的な発生条件判定の上に日次確率を追加 |
| 7 | ライバルAI意思決定 | `remake_rival_policy.py` | `RemakeBalancedRivalPolicy` — 資金/月次損益/人気差/サービス差/商圏重複から拡大・現状維持・撤退を決定 |
| 8 | 地価変動式 | `remake_land_value.py` | `RemakeBalancedLandValuePolicy` — `land_price = base_price * local_development_factor * time_inflation_factor`(攻略本自身が示唆する構造) |

このほか、確定情報(推測を要さない)として`month_aggregation.py`(4日→月間集計は
攻略本の「1月=4日間×8」という明記された倍率)も同時に実装した。

### 各モジュールの主要な係数根拠

- **顧客分配の重み** (`remake_customer_share.py`): 人気30%・サービス25%・清掃15%・
  警備10%・品揃え10%・営業時間10%。攻略本は「これらが影響する」ことは確認するが重みは
  示さないため、人気を最重要としつつ他要因も無視しない、という定性的な優先順位のみを
  反映した推測配分。
- **来店率** (`remake_demand_policy.py`): 人口の5%/日を基準来店率とし、悪天候で0.6倍。
- **購入確率** (`remake_purchase_policy.py`): 主目的購入90%、ついで買い基本35%。
  価格弾力性の基準は`CUSTOMER_VISIT_SCHEDULE`の所持金レンジ(confirmed data)から
  1,500円を基準予算として使用。
- **成長量** (`remake_staff_growth.py`): 既存の確定成長量テーブル
  (`EVIDENCE_BACKED_UNIT_GROWTH`)を継承し、未確定の(タスク, スキル)組にのみ+1の
  デフォルトを補完。店長教育ボーナスは教育値1ポイントあたり+1%。
- **回復ボーナス** (`remake_rest_recovery_policy.py`): 敏捷性(0-100)をそのまま
  0-100%の確率に線形変換(agility=100で必ず発生)。
- **事件発生率** (`remake_incident_policy.py`): 火災/強盗は日次2%(人気>警備で2倍)、
  万引きは条件成立時に日次5%。
- **ライバルAI** (`remake_rival_policy.py`): 競争圧力 = (人気差 + サービス差)の加重平均 ×
  商圏重複率。赤字かつ高圧力で撤退、黒字かつ資金2,000万円以上かつ低圧力で拡大。
  資金基準は攻略本確定の小型店建設費600万円に運転資金の余裕を加えた推測値。
- **地価変動** (`remake_land_value.py`): 年率5%のインフレと、人口(20,000人で飽和、
  初級シナリオの確定人口目標を援用)・店舗密度(8店舗で飽和)の加重平均による
  局所発展係数(上限3.0倍)の積。

## 影響

- 新規ファイル: `remake_customer_share.py`, `remake_demand_policy.py`,
  `remake_purchase_policy.py`, `remake_staff_growth.py`,
  `remake_rest_recovery_policy.py`, `remake_incident_policy.py`,
  `remake_rival_policy.py`, `remake_land_value.py`, `month_aggregation.py`。
- 既存のevidence-safeなモジュール(`store_value.py`/`store_rating.py`/`store_events.py`/
  `customer_demand.py`/`customer_purchase_policy.py`/`staff_rest_recovery.py`等)は
  一切変更していない。`remake_*.py`は既存のProtocol/確定関数を呼び出す側であり、
  逆方向の依存(evidence-safe層からremake層への依存)は存在しない。
- `store_runtime.py`をはじめとする既存の組み立て役モジュールへの配線は本決定の
  スコープ外(決定書0086と同じ理由: 呼び出し順序の設計は別判断が必要)。
- 全モジュールにユニットテストを追加(`reference_sim/tests/test_remake_*.py`、
  `test_month_aggregation.py`)。既存テストと合わせて`python3 -m unittest discover`が
  全件成功することを確認済み。
- ここに実装した係数は全て`REMAKE_BALANCED_DEFAULT`であり、実プレイでの調整、または
  ディスクイメージ解析等でより強い証拠が得られた場合の置き換えを前提とする。
