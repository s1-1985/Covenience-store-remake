# 0245 — 既存解析の月末32bit会計と評価入力を接続

## 背景と根拠

ユーザーの指示に従い自分の過去解析の未反映分を優先するLEGACY-0245。Muse新規解析は採用していない。基点3269c731a4600dd5df3f1de5ac6bb41333bd567e、main688876aと未マージPR270/272/273/274のHEADを確認。ブランチchatgpt/legacy-finance-width-20261121。PRは作成後追記。

既存decision0206-android-operating-ledger.mdは月末8倍/追加7倍を移植したが、原32bitオーバーフローを未反映と明記していた。現行OperatingStatementの加減算・倍率・現金更新も64bitのままだった。

根拠は保管済みのps1-analysis-checkpoints/analysis/20261103-operating-continuation/source-reference/recovered.pyのledger_profit/month_close/store_rating_coreとfinance_close.py。ローカル保管コミットa1f45981ffc1479e9a8e0b4ff429d4fc4cb85ea4。前者のSHA256はgame/tests/fixtures/source_finance_width.jsonに固定。原区間8001CCC0、80029918..29D30、800282FC..28A98。本作業では既存Python復元モデルを実行し、新規の原EXE/ディスク/CPU解析は行っていない。

store_rating_coreは売上D48を「unscaled within-month accumulator、read before midnight close」と明記している。現行_close_store_monthは8倍後の売上を渡していたため、この既存解析との未反映差も訂正する。係数・閾値の新規推測ではない。

## 決定・実装

1. OperatingStatement.projectへ原32bit幅の明示モードを追加。5欄の入力、各欄8倍、損益、損益8倍、追加7倍をsigned32へ正規化する。従来プロトタイプ呼出しは既存幅を維持。
2. native本体の会社/店舗別収支と月末へ接続。最終現金はsigned32(cash+7*profit)へ合わせ、決算記録のcash_afterも実値に一致させる。月次グラフ・年次売上の引数も32bit月額に統一。
3. 月末中断の旧保存が持つ64bit計算済statementは、保存済みrepresentativeの明示5欄から計算し直す。過去の確定済決算は書換えず、現金差から帳簿を推定しない。
4. nativeの店舗評価へ渡すのは8倍前の当月売上signed32とする。符号反転した入力も既存閾値比較へ通す。非nativeの負売上禁止条件は維持。評価表・加点/減点数値は変更しない。
5. Python契約テスト1件の旧「8倍後の変数を渡す」文字列期待を、新しい原入力の呼出しへ訂正。skipや閾値緩和は追加しない。

## 検証

- 既存復元モデル由来24ケース: 各5欄の正負境界、合計/倍率の折返し、現金の符号反転。build_fixture.pyは既存recovered.pyを読むだけでディスク/CPU依存なし。
- finance_width_smoke: 通常1000、400000、268435456、400000000、2147483648の制御した売上入力で、本体の月末、倍率前の評価入力、店舗損益履歴/年次売上、負現金時の終了、前後JSONを確認。旧中断statementの再計算も確認。自然営業でこの売上に達した実測ではない。
- JSONでは数値がfloatへ戻るため、保存レコードの完全比較は両方をJSONデコードした構造で比較し、現金・履歴・各数値は個別確認した。初回の型比較失敗を数値消失と扱わない。
- Godot4.6.3関連10本成功: finance_width / annual_report / annual_report_ui / graph_sale / graph_sale_ui / renovation_editor / donations / rival_advertising / pending_audio / source_people。SCRIPT ERRORなし。finance_widthは上記追加5入力版も再実行成功。
- Python全793件成功、失敗/想定失敗0。外部プラグインの非推奨警告1件。途中の契約文字列不一致1件は上記の根拠付き訂正で解消。
- 広域headlessは1205step末尾passedまで到達。ただし既存config.source_catalog欠落SCRIPT ERROR5回を引き続き検出するため全体合格とはしない。
- APK0.8.12-finance-width/code92、従来touchfix署名v2/v3、変更3gdcとsmoke非同梱を確認。Android実機/実聴は未確認。

## ファイル

operating_statement.gd、store_rating.gd、vertical_slice_simulation.gd、finance_width_smoke.gd/uid、source_finance_width.json、既存Python契約テスト、CI、export_presets、fixture再生成スクリプト、本文、最新handoff/build/status、PROJECT_MEMORY第19節追記。

## 範囲外

原会計全5欄の全生成元/全履歴、日中の全現金加減算の32bit化、旧保存の過去決算修復、原物理店舗順/全営業RNG、原カード形式、全通知、既存未解決6件（U-1〜U-6）は未完。経費第3欄の既存互換対応も維持。本作業を会計全移植と呼ばない。
