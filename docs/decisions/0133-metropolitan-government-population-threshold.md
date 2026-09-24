# 0133: 都庁誘致(初級クリア条件)の人口閾値をCONFIRMED_OFFICIALへ格上げ(タスク#64)

## 背景

`docs/research/quick-reference-guide-part2-2026-09-19.md`§3.9(書籍頁80-83、マップ攻略)は、
初級シナリオのクリア条件「都庁を誘致する」について、攻略本クイックリファレンス本文が
「**20000人の人口を集めれば、役所用地に都庁が建設される**」と直接明記していることを確認して
いた。これは`docs/research/facility-induction-crosscheck-2026-09-05.md`§7がPROVISIONALと
していた「都庁が町人口2万人超で自動出現」を裏付ける新証拠であり、同研究文書自身が
「CONFIRMED_OFFICIALへ昇格できる新証拠」と明記していたが、コード側は未反映のままだった。

`baseline_data.SCENARIOS`の`beginner.objective`フィールドは、文字列ラベル
`"metropolitan_government_after_population_threshold"`のみを保持し、証拠レベルは
`CONFIRMED_COMMUNITY`(wikiソース)、かつ実際の閾値(20000)はどこにも数値として存在しな
かった。

## 決定

### `beginner.objective`の証拠レベルをCONFIRMED_OFFICIALへ格上げ

出典を`SCENARIO_GUIDE`(wiki)から新設の`QUICK_REFERENCE_GUIDE_MAP_CLEAR_CONDITIONS`
(攻略本クイックリファレンス書籍頁80-83の本文引用)に変更し、証拠レベルを
`CONFIRMED_OFFICIAL`に更新した。

### `store_events.METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD`(新規、20,000)

`store_events.py`に定数と`metropolitan_government_is_induced(town_population: int) -> bool`
関数を追加した。既存の`magazine_or_contest_event_is_eligible`等と同じ薄い純粋関数パターン。

## テスト

- `test_baseline.py`: `beginner.objective`が`CONFIRMED_OFFICIAL`になったことを検証する
  新規テスト。
- `test_store_events.py`: 新関数・定数の閾値ちょうど/未満/負数境界テスト3件。
- `reference_sim`フルスイート730件パス/1件xfail(既存の無関係なxfail1件は変化なし)。

## 対象ファイル

- `reference_sim/conveni_sim/baseline_data.py`
- `reference_sim/conveni_sim/store_events.py`
- `reference_sim/tests/test_baseline.py`
- `reference_sim/tests/test_store_events.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `game/`(Godotクライアント)への配線は行っていない。現在`game/`にはシナリオ選択機構が
  存在せず(decision 0095/0131と同じ境界)、`clear_condition_met`は中級シナリオ相当の
  「自社店舗数10店舗」条件のみをハードコードして実装している(task #30)。初級固有の
  人口閾値クリア条件をGodot側で判定する仕組みは、シナリオ選択機構ができてから改めて
  取り組む。
- 「コンビニコンテストの当選確率は清潔度に依存する」という別の新知見
  (`strategy-guide-shopkeeper-manual-part2-2026-09-19.md`§3.2)は、原典が定性的な
  アドバイス(「清掃値を常にMAXにしておく」)のみで具体的な数値・確率式を示していないため、
  今回は実装対象外とした。`store_events.py`の`magazine_or_contest_event_is_eligible`は
  既に「実際に選ばれるかは別途」として当選ドローをモデル化しない設計(decision 0099)を
  踏襲しており、この方針は変更していない。
