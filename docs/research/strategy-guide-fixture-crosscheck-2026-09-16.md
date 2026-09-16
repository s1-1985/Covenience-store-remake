# 攻略本フルデコード vs 既存データ クロスチェック（2026-09-16）

対象コミット: `s1-1985/covenience-store-remake` `claude/code-review-6s2a9n` ブランチ、
`docs/research/strategy-guide-full-decode-2026-09-16.md` 取り込み作業時点。

本メモは `docs/research/strategy-guide-full-decode-2026-09-16.md`（Codex が攻略本スキャン
から抽出した実装可能データ）を `reference_sim/conveni_sim/baseline_data.py` へ取り込む際に
発見した、既存の確認済み値との数値不一致・対応不明点を記録する。攻略本ガイド自身の方針
（該当ファイル section 0/17/44）に従い、**既存の確認済み値は上書きしない**。差分はここに残し、
判断が必要な項目として扱う。

## 1. ベンチのメンテナンス費（数値矛盾・未解決）

- 既存値: `168` 円/日 (`WIKI` 出典、`EvidenceLevel.CONFIRMED_COMMUNITY`)
- 攻略本値: `160` 円/日（`strategy-guide-full-decode-2026-09-16.md` 4.5 節、家具データ表）
- 対応: `baseline_data.py` の `bench` エントリでは既存の `168` を維持し、攻略本値では上書き
  していない。両出典とも購入価格・footprint・attention 等の他フィールドとは矛盾していない。
- 要判断: どちらが実機の正しい値か未検証。日本語版/PS版とSS版の版差、または攻略本の誤植・
  Wiki側の伝聞誤りの可能性がある。動画等の一次証拠での再確認が必要。

## 2. 宣伝（プロモーション）の人気上昇値（数値矛盾・未解決）

`PROMOTIONS` の `airship` / `radio` / `tv` について、費用・発火日・発火時刻は攻略本と既存値が
完全一致するが、`popularity_gain` のみ食い違う。

| id | 費用 (既存/攻略本、両者一致) | 発火日/時刻 (両者一致) | 既存 popularity_gain | 攻略本 popularity_gain |
|---|---|---|---|---|
| airship | 1,000,000 | 毎月3日 15:00 | +30 | +40 |
| radio | 3,000,000 | 毎月1日 17:00 | +50 | +60 |
| tv | 5,000,000 | 毎月1日 19:00 | +100 | +90 |

- 既存値の出典: `docs/research/promotion-cost-popularity-and-timing-2026-09-06.md`
  （初代Wiki準拠、evidence level "B+ / FIRST-TITLE-DEDICATED-COMMUNITY-DATA"）。
- 対応: `baseline_data.py` の `PROMOTIONS` は変更していない（既存の `CONFIRMED_COMMUNITY` 値
  を維持）。
- 要判断: 費用・タイミングが完全一致するため出典の信頼性自体は高いと考えられるが、
  `popularity_gain` だけ異なる理由は不明。攻略本のOCR誤読、初代Wiki側の伝聞誤り、あるいは
  実機のバージョン差の可能性がある。どちらを正とするかは一次証拠（動画等）での再確認が必要。

## 3. 店舗建物サイズの対応関係（不明・今回は未実装）

- 既存 `STORE_VARIANTS` の `small_top`: `construction_price_yen=6,000,000`,
  `editable_floor=(8, 13)`（`PS small-store visual reconstruction` 出典）。
- 攻略本 `store_1`: 建物代 `6,000,000`（一致）、店内 `7x10`、店舗外形 `9x10`、
  建物面積 `100`、建物全体 `70`、駐車場 `40`、店外スペース `30`。
- 既存の `(8, 13)` (=104マス) は、攻略本の「店内 7x10」(=70マス) にも「店舗外形 9x10」
  (=90マス) にも一致しない。列の意味（店内可編集フロア/建物外形/最大外部スペース等）の対応
  関係が確定できないため、今回の実装パスでは店舗建物データ（Section 1）への攻略本値の反映を
  見送った。
- 要判断: 攻略本の列見出しと既存データの `editable_floor` が同じ概念を指しているかどうか
  Codex側で確認が必要。確認できれば `STORE_VARIANTS` に `store_1`〜`store_5` 系の情報を
  追加できる。

## 今回クロスチェックで独立確認できた一致（参考）

以下は既存の確認済み値と攻略本値が完全一致し、出典の信頼性を相互に裏付けたもの。
`baseline_data.py` では、これらの一致を根拠に、従来 `None` だった未確認フィールド
（`purchase_price_yen` / `placement` / 一部 `footprint`）のみを追加した。

- `copier_a`（小型コピー機）: capacity 20 / attention 10 / purchase_price 1,500 /
  maintenance 1,200 で一致。
- `copier_b`（中型コピー機）: capacity 40 / attention 15 / purchase_price 2,000 /
  maintenance 1,440 で一致。
- `potted_plant`: footprint (1,1) / maintenance 120 で一致。
- `fountain` / `parking_ground` / `parking_two_story` / `parking_tower`: footprint・
  maintenance・parking_capacity で一致。
