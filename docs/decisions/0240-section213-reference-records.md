# 0240 — §21.3 転記データの記録形式（CSRM-006）

## 背景
PROJECT_MEMORY §21.3 が「転記済み・コード未記録」とした項目のうち、具体的な転記値があり現行コードに記録が無い3件（DATA 4 来客数表、駅の出現・間隔ルール、シナリオ開始データの拡張）を `reference_sim` へ記録する（CSRM-006 版2）。記録形式の選択が本決定の対象である。着手前の候補ファイル走査（arrival_schedule.py、traffic.py、remake_demand_policy.py、inducement.py、scenario_initial_state.py、scenario_policies.py、scenario_initial_rival_topology.py）では3件とも既存記録は無かった。

## 決定
- DATA 4 は `baseline_data.py` の平常数（`TIME_OF_DAY_BUCKETS_HOURS`）の先例に倣い、出典コメント付きの素のタプルとして記録する。(b) 深夜〜早朝側21行は建物名（推定対応）付き、駅の4桁数値は UNCERTAIN、住宅(小A)の夕は転記自体が UNCERTAIN のため None（不明）とする。(a) 朝〜夜側30行は建物対応を構造的に持たせず、掲載順の行番号のみをキーとする。平日/休日の定性頻度語も併記する。どちらの表も需要・来客の挙動へは接続しない。
- 極上シナリオは `SCENARIOS` へ4件目として追加する。クリア条件は出典（書籍頁83）に記載が無いため、objective の値を None とし、「不明であり invent しない」旨を note に明記する。開始資金 ¥150,000,000 は CONFIRMED_OFFICIAL として記録する。
- 開始人口（4マップ分）と初級のライバル初期値・セキュリティ施設数は、EvidenceValue の記録として `SCENARIO_STARTING_POPULATIONS` と `BEGINNER_RIVAL_START` に分けて置く。上級の開始人口 2,849 は桁の UNCERTAIN 注記を引き継ぐ。
- 駅ルールは定数のみの記録とし、既存の PROVISIONAL な「町人口5000人超で出現」観測との関係が UNCERTAIN である旨をコメントに明記する。配置挙動へは接続しない。

## 根拠
出典は公式クイックリファレンスの転記（docs/research/quick-reference-guide-part2-2026-09-19.md §3.9・§5.4）。確度の濃淡と caveat は同文書と Muse の検証文書（docs/muse/analysis/2026-11-21-section213-data-status.md）に明記されており、本記録はその注記を全て引き継ぐ。上級クリア条件の数値セットは所在確認で反証があり使用不可と判定済みのため、本記録では扱わない。

## 確認
- 転記値を固定するテスト11件を `reference_sim/tests/test_section213_records.py` に追加（行数、代表セルの値、住宅(小A)の夕=None、(a) 側に建物名が結び付いていないこと、極上の objective=None、既存3シナリオの objective 不変、開始人口と初級ライバル初期値）。
- Python 全テスト: 804件（着手前793件）。801成功／既存2失敗／想定失敗1で、基線からの悪化なし。`SCENARIOS` への極上追加による既存消費側（シナリオ初期ライバル構築・テスト群）への影響は無いことを全テストで確認した。

## 範囲外
記録したデータのゲーム挙動への接続、game/ 側への記録、DATA 4 表 (a) の建物対応付けの解決（高解像度スキャンでの再照合が前提）。APK は作成していない。実機確認は行っていない。
