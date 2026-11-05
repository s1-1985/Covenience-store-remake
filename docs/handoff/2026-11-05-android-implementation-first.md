# Android実装優先への切替と0.1.20

ユーザー指示：初代のAndroidアプリを完成させることが目的。解析・検証は実装を進めるために使い、更新数や大量ログを目的化しない。ルートAGENTS.mdを読む。

基点は未マージPR #270の `0c15eeb401441c00ab48a0af13da8bd70d2a1b78`。この時点で最新mainよりゲーム本体が大きく進んでいる。mainだけを見て古い機能を作り直さない。PR #270やClaude管理ブランチは未マージ・未変更。

今回、原作で照合済みの月末台帳式をGodotの `OperatingStatement` へ移した。賞金・強盗などの現金変動を営業利益として繰り返し計上する問題を修正。全店売上の取消しも反映する。スマホの調査→全店収支グラフに今月と先月の内訳を追加。詳細・限界はdecision 0206。

ビルド済み0.1.20-previewは公式Godotテンプレート版で約26MiB。独自縮小テンプレート版0.1.19より大きいが、解析データやエミュレータは入っていない。実機インストールは未確認。新しいdebug署名は古い配布版と一致する保証がない。鍵はコミットしていない。

次回も `game/` を進める。優先候補は、解析済みのライバル営業・撤退ルールを現在の仮ルールへ反映すること、原作の町・店舗データとの接続、Android操作上の不具合。解析ブランチの自然営業更新だけを延々と追加する作業へ戻らない。

通常の実行・テスト：Godot 4.3でimport後、headless_smoke.gd、operating_statement_smoke.gd、android_preview_smoke.gd（-- --android-preview）。Pythonはreference_simでunittest discover。結果は同じディレクトリのbuild-result JSONを参照。
