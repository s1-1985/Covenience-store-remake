# CSRM-006 実装報告: §21.3 転記データの reference_sim への記録

## 採用した指示書

- 指示書: `docs/muse/ready/CSRM-006.md` 版2（`muse/analysis` ブランチ、コミット `fc9f791d4e1319cd4b6971fbc897a6b18cc8373f`）
- 基準コミット: `7f87932f0cf1117b5464243e1b9a91fb2e4cd89f`（ブランチ `chatgpt/ps-ui-touch-audit-20261119`、ChatGPT チェーンと CSRM-007 のマージ後）
- 実施ブランチ: `claude/csrm-006-restack`
- 状態: 実装完了。マージはユーザーの承認待ち
- 実施者についての注記: ユーザーの 2026-11-22 の決定により Muse が実装した。
- 積み直しについての注記: 本ブランチは PR #279（旧 `claude/csrm-006-impl`）の内容を、マージ済みのラインへ積み直したものである。記録内容・テスト・decision0247 は #279 と同一で、#279 の配下に含まれていた破棄済みの CSRM-003/004 コミットは含まない。decision0247 の「確認」に記載のテスト内訳は #279 実施時点のものであり、本積み直しの基準での結果は下記テスト欄に記す。

## 着手前確認の結果（指示書の必須確認）

候補ファイルを全て走査し、3件とも既存記録が無いことを確認した。

- DATA 4 来客数表: `arrival_schedule.py`（到着スケジュールのデータ構造のみ）、`traffic.py`（エージェント移動・混雑のみ）、`remake_demand_policy.py`（REMAKE_BALANCED_DEFAULT の需要ポリシーで、表の転記ではない）。表の数値（560/2620 等）は全モジュールに存在しない。
- 駅間隔ルール: `inducement.py` は誘致配置と費用の計算のみで、駅の間隔・本数に関する記録は無い。
- シナリオ開始データ: `scenario_initial_state.py`、`scenario_policies.py`、`scenario_initial_rival_topology.py` および conveni_sim 全体に、極上・開始人口（2179/1880/2849/1416）・買収額（46,721,490）の記録は無い。

## 変更ファイル

- `reference_sim/conveni_sim/baseline_data.py`
  - 出典定数 `QUICK_REFERENCE_SCENARIO_DATA`、`QUICK_REFERENCE_DATA4` を追加。
  - `SCENARIOS` に極上（supreme）を追加。開始資金 ¥150,000,000、クリア条件は出典に記載が無いため objective=None（不明）として記録。
  - `DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS`（21行、推定対応・駅数値 UNCERTAIN の注記付き、住宅(小A)の夕は None）。
  - `DATA4_VISITOR_COUNTS_DAYTIME_ROWS`（30行、建物対応なし・掲載順のみ）。
  - `STATION_SPACING_RULE`（線路2本・各2駅まで・間隔40エリア以上。人口5000人条件との関係 UNCERTAIN の注記付き）。
  - `SCENARIO_STARTING_POPULATIONS`（初級2,179／中級1,880／上級2,849（桁 UNCERTAIN 注記）／極上1,416）。
  - `BEGINNER_RIVAL_START`（本店 人気20・警備89・清掃30・サービス30、2号店 人気20・警備58・清掃30・サービス31・買収 ¥46,721,490、交番2・消防署1）。
  - いずれも参照専用で、需要・配置・シナリオの挙動へは接続していない。
- `reference_sim/tests/test_section213_records.py`: 新規作成（転記値を固定するテスト11件）。
- `docs/decisions/0247-section213-reference-records.md`: 新規作成（記録形式の決定）。
- `PROJECT_MEMORY.md`: 第19節末尾へチェックポイントを追記。

## 指示書からの逸脱

- なし。記録形式（素のタプル＋出典コメント、極上の objective=None 表現）は指示書の範囲内の実装側選択であり、理由を decision0247 に記録した。なお指示書の完了条件の1項目で DATA 4 の (a)/(b) 表記が §1 と入れ替わっている箇所があるが、§1 の定義（(a)=朝〜夜側30行・対応なし、(b)=深夜〜早朝側21行・推定対応）に従って記録した。

## テスト・ビルド結果

- 着手前（マージ済みライン = チェーン先端 + CSRM-007）: Python 793件全成功。
- 完了後: Python 804件全成功（本ブランチと同一内容を Muse がローカルで事前に確認済み）。
- Godot・APK: 対象外（game/ を変更していないため）。

## 未解決の質問

- なし。
