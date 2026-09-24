# 0134: 「お客に怒られる」の1/6確率ランク減点をgame/へ配線(タスク#65前半)

## 背景

ユーザーから再共有された4分割PDFのうち、バックグラウンドの全ページ文字起こしエージェントが
PDF4(`d9b60a50-downloadfile3.PDF`)の10〜24ページを「これまで見たことのない第三の攻略本
(『攻略&データブック』オールテクニックガイド+データリスト)」と報告した。該当ページ
(印刷頁74-75)を400dpiで自ら再展開・直接確認したところ、店舗ランクの月次増減表の直後に
以下の一文があることを確認した:

「※上記の条件以外に、お客に怒られる=1/6の確率で-1、万引き=-1、寄付イベント=+5」

`reference_sim/conveni_sim/store_rating.py`を確認したところ、この3つの数値
(`ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY = (1, 6)`、`ANGRY_CUSTOMER_DOWNGRADE_POINTS = -1`、
`SHOPLIFTING_DOWNGRADE_POINTS = -1`、`DONATION_UPGRADE_POINTS = 5`)は既に**過去のセッションで
CONFIRMED_OFFICIALとして定数化済み**であり、今回の再確認は完全な一致(CONFIRMS)だった
(`game/scripts/domain/store_rating.gd`側にも同じ定数が既に移植済み)。ただし
`store_evaluation.py`の`apply_point_delta()`もGodot版store_rating.gdの各定数も、
**実際に発火するトリガーに一切配線されていなかった**(`reference_sim`側の
`CheckoutAngerPenaltyRuntime`は記録専用でresolve()に外部フロアが必要な設計、`game/`側は
定数を保持するのみ)。

decision 0096(タスク#27)は「これらのイベント自体がまだ配線されていないため未実装」と
明記していたが、その後タスク#49(2026-09-19)で`checkout_anger_triggered`イベントが
`game/scripts/vertical_slice_simulation.gd`に実際に配線され、毎チェックアウトで発火する
実トリガーとして存在するようになった。つまり「怒った客」に関しては、decision 0096が
配線待ちとしていた前提条件が既に満たされている。万引き・寄付イベントは`game/`に
該当メカニクス自体が存在しないため、引き続き未配線のままとする。

## 決定

### `game/scripts/domain/store_rating.gd`

`ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_NUMERATOR := 1`/
`ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_DENOMINATOR := 6`を追加した
(`reference_sim`の`(1, 6)`タプルに相当する名前付き定数、Godot側に欠けていた)。

### `game/scripts/vertical_slice_simulation.gd`

`checkout_anger_triggered`が発火するブロック内で、既存の-2スキルペナルティ適用の直後に
1/6の確率ロールを追加し、成立すれば`internal_rating_value`に`ANGRY_CUSTOMER_DOWNGRADE_POINTS`
(-1)を適用(0-100にクランプ)、`star_rating`も再計算する。乱数はタスク#55の「共有デマンド
RNGを再利用する(新規ストリームを作らない)」という既存方針を踏襲し、`_demand_rng`を再利用
する。記録イベント`checkout_anger_triggered`に`rating_penalty_applied`(bool)と
`internal_rating_value`を追加した。

## テスト

`headless_smoke.gd`の既存タスク#49/#51用シナリオ(`rng_seed: 19`)を再利用し、
`checkout_anger_triggered`イベントに`rating_penalty_applied`フィールドが存在し、
真偽値型であることを検証する(具体的な乱数結果そのものはシード依存のため、配線が
実際に実行されたことの証明として型・存在チェックに留める)。`internal_rating_value`が
負にならないことも検証する。

## 対象ファイル

- `game/scripts/domain/store_rating.gd`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/headless_smoke.gd`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `reference_sim`側は変更していない。`CheckoutAngerPenaltyRuntime`/
  `StoreEvaluation.apply_point_delta`は既に存在するが、`reference_sim`にはこの2つを
  実際に結びつける実行ループ(`minimal_day_scenario.py`はcaller-drivenのオプトイン設計)
  が元々存在せず、Python側で無理に統合するより、実際にプレイ可能な`game/`側の具体的な
  ギャップを埋めることを優先した。
- 万引き(`SHOPLIFTING_DOWNGRADE_POINTS`)・寄付(`DONATION_UPGRADE_POINTS`)は、
  `game/`に万引き発生・寄付発生のメカニクス自体が存在しないため、今回も未配線のまま
  (decision 0096の該当部分は依然として有効)。
- ランク増減表そのもの(価格/サービス/セキュリティ/清掃/売上のしきい値)は、今回の
  再確認で完全に一致(CONFIRMS)したため変更していない。
