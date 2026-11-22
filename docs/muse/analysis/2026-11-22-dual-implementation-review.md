# 二重実装の比較レビュー（CSRM-001〜004）

作成: 2026-11-22（Muse）
対象: ChatGPT チェーン（PR #272 = chatgpt/source-operating-audio-20261121 @ eaaab30b、PR #273 = chatgpt/muse-runtime-consistency-20261121 @ 6705aa92）と、Muse 側（PR #277 CSRM-004、PR #278 CSRM-003、ローカル完了の CSRM-002）の比較。ユーザーの指示によりシート単位で推奨を出す。

## 検証方法
- ChatGPT 側 PR #272/#273 の tarball を取得し、実装報告・決定記録・主要コードを直接読んだ。
- ChatGPT 側の Python テストをローカルで実行: 793件全成功（OK）を確認。
- Godot 側の不具合主張は、修正前コード（PR #272 時点の try_eject_customer）と修正後（change_state 接続）を確認した。

## CSRM-001（APK 0.8.9）→ ChatGPT 側を採用
- ChatGPT 側のみ実装が存在する。APK 0.8.9（code89、package 据置、apksigner 検証・SHA256 記録済み）に decision0238 を収録。
- 逸脱は開示済みで、ユーザーの直接指示による別作業（LEGACY-0239 音声4項目）が同梱され、0238 単独 APK は作られていない。指示書の目的（0238 の APK 収録と正直な検証記録）は満たされている。チェーンは 0.8.13 まで継続。
- Muse 側は環境制約（署名鍵なし、スリムテンプレートのソースビルド不可）で未実施。失うものはない。

## CSRM-002（テスト基線）→ ChatGPT 側を採用
- 項目A: ChatGPT 側は step 全体のチェックポイント/復元（在庫・現金・セッション・入れ子リスト・Random 状態まで復元し、再試行まで確認）。Muse 側は時計のみの復元で、指示書の固定テストには合うが範囲が狭い。ChatGPT 側が明確に強い。
- 項目B: 両者とも「陳腐化した文字列期待値」で一致。
- 項目C 町寸法: ChatGPT 側は ANDROID_PS_UI_HANDOFF の仕様に基づき 12.0 ちょうどへ是正。Muse 側はズーム下限 8.0 以上へ是正。仕様値を固定する ChatGPT 側の方が回帰ガードとして強い。
- 項目C 調査記録: 両者独立に同じ結論（買収後の調査キー消去が現行仕様、期待値が旧い）。ChatGPT 側は 2026-11-20 rival-inspection 引継ぎを根拠に挙げている。
- 未完点（ChatGPT 側が正直に分離）: 全体 headless_smoke は末尾 passed へ到達するが、途中で `_step_manager_reports`（vertical_slice_simulation.gd:893 付近）の `config.source_catalog` 欠落 SCRIPT ERROR が5回出るため、指示書の完了条件では未達としている。残る論点は「カタログ無しの旧構成を引き続きサポートするか、テスト構成を本体へ移行するか」。Muse の見解: 実ゲームの構成では source_catalog は常に存在し（_recovery への merge 経路）、同ファイル内には has() で守る前例もあるため、無防備アクセス側を守るのが小さく正しい。後継の小指示書（CSRM-007 候補）として切り出す。
- Muse 側 CSRM-002 は push しない（上記論点の分析のみ後継指示書へ引き継ぐ）。

## CSRM-003（U-ID 運用）→ ChatGPT 側を採用
- ChatGPT 側は 2026-11-21 に適用開始（decision0241 が最初の適用文書）し、後続の決定 0242〜0246 まで運用が組み込まれている。Muse 側 PR #278 は同内容の重複（文書のみ）であり、両方を入れると PROJECT_MEMORY 追記が二重になる。PR #278 は superseded として閉じるのがよい。

## CSRM-004（メモ項目3・12）→ ChatGPT 側を採用
- Python: ChatGPT 側はセッション状態へ統合した方式（CHECKOUT_CANCELLED 状態 + settlement_blocked の持続、明示 resume のみ復帰、purchases.settle 側にも古い完了通知への防御）。Muse 側の tombstone 方式がカバーするケースを包含し、防御が深い。
- Godot: **ChatGPT 側が実在の不具合を検出し、Muse のパイロット確認はそれを見落とした。** try_eject_customer は phase を leaving へ変えるだけで、原プログラム側の状態（状態3・旧目標）が残り、次の native 更新で退店客が精算され得た。Muse の確認は phase/列/担当者の層だけを見て「相当不具合なし」と誤判定した。ChatGPT 側は ProgramPeople.change_state(customer, 5) へ接続して原退店経路へ遷移させ、専用 smoke（ejection_consistency_smoke）を CI へ追加した。
- Muse 側 PR #277 は superseded として閉じるのがよい。

## 番号の衝突
- ChatGPT チェーンが決定 0239〜0246 を使用済み。Muse 側の決定番号は衝突する: CSRM-004 の 0239（PR #277、閉じる前提なら実害なし）、CSRM-006 の 0240（反映中）→ 0247 へ振り直し、CSRM-005 の 0242（ローカル）→ 0248 へ振り直す。

## 対象外
- ChatGPT チェーン後段（PR #274〜#276、音声フラグ・財務幅・日次コスト、0.8.11〜0.8.13）は CSRM 指示書外の作業であり、本レビューの対象に含めていない（未レビュー）。
