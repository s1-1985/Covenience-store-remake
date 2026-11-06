# 全反映作業の再開地点 — 終了処理接続

基点は `9a6474575c9456185b3334d65c2d50b6f102ae1c`、ブランチ `chatgpt/android-analysis-integration-20261105`。ユーザーの方針は解析済み内容を一括反映したAndroid本体であり、途中APKは配布しない。main・他管理ブランチは変更しない。

今回の本体変更：都庁・10店・オーナー100点・0時の倒産の終了値と解除bit、原画像4場面、原クレジット102行、保存承諾／辞退／失敗再試行、保存FF、タイトル復帰と極上解除。年次終了は評価通知を消費した時点で立つ。保存FFはJSONのクリア結果であり原カード互換ではない。詳細と限界はdecision0210。

原資料は `../analysis-restored/algorithm-analysis` にある。TIM素材、BGM01〜07のSEQ/VH/VB、SE/VOSのSEP等もそこにある。音声の本体接続はまだ行っていない。抽出ツールはツール依存をオフラインでだけ使い、APKに原CPUを入れない。

次に進める全範囲はfull-integration-environment-interruption.mdを参照。原音源／通知音声、原セーブ37領域とカード鎖の保持・相互変換、未移植操作と通知生成元、原作人物状態の追加照合、最後のAndroidビルド・UI確認が残る。今回の終了画像はPNGとGodotで再生するが、窓の面・原音声終了待ち・物理GPU等は未完として区別している。

現在の作業コピーは `/workspace/scratch/69fb6031f6b8/conveni`。一時環境の存続を前提にせずGitの最新保存を確認して続ける。Godot4.3は `/tmp/conveni-tools/Godot_v4.3-stable_linux.x86_64`。必要なら公式4.3を再配置する。原解析は解析基点2c00ba53のrestore-latest.pyで復元する。

検証完了：Godot4.3の全16本が成功、Python786件は予期しない失敗0／既知の想定失敗1。独立504条件と、実UIの保存失敗・辞退・承諾・FF読込み・倒産・背後通知凍結も確認した。詳細と原画像20枚のSHA256は2026-11-06-ending-checks.json。Androidビルド・実機検証は今回は実施していない。既存のObjectDB終了時警告は残る。
