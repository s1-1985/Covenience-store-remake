# 再開用：原作データを使うAndroidゲーム v0.2.0

目的は初代ザ・コンビニをエミュレータなしのAndroidゲームにすること。AGENTS.md、decision 0207を読む。45851caの更新版本体へ実装を積んだ。main／ClaudeのPR #270はそのまま。

本番開始はGuideStartingStore.apply→ProgramTownでTOWN0001に切り替える。TownView／StoreViewは原作の画像を使う。ProgramTownは月末処理を移植、ProgramRulesは作業判定、ProgramRivalsは赤字撤退と候補地走査。ライバルの各店は子VerticalSliceSimulationで在庫・人員・損益を持つ。エミュレーション依存はない。月損失を幾何的な圧力値で代用しない。

既存smokeは固定座標と旧マップを検査しているためtest-only legacy_guide_fixtureメタを設定。本番側はrecovered_runtime_smoke（全町セルの照合）、recovered_game_smoke（出店→10日営業→JSON保存→誘致→買収）、recovered_ui_smoke（実シーン新規開始→土地→建設→営業・町表示）で別に検査する。tools/run_recovered_checks.py <Godot4.3の絶対パス> を利用可能。Pythonはreference_simでPYTHONPATH=. python -m unittest discover -s tests -v。

LCGのrandi_range／randfは必ずself.randi()を呼ぶ。同名Godotグローバルを呼ぶと再現可能な乱数にならない。範囲・浮動小数呼び出しの既知系列もsmokeにある。

APK：Conveni-Android-v0.2.0-recovered.apk（約28MB）、Library ID libfile_2fc114b4b7188191b5cc8e43a6b7bb7f。元ディスク／EXE／BIOSは入っていない。com.conveniremake.recoveredなので以前のpreviewと共存する。次回の上書き更新ではConveni-Android-v0.2.0-build-support.zip（Library ID libfile_8d12316e7a848191816c8ee5de156833）の同じdebug署名鍵を使う。秘密鍵をGitへ入れない。Android実機は未確認。

画面記録docs/screenshots/2026-11-05-recovered-{town,store}.pngはGodotのAndroid表示をLinux/OpenGLで描いたもので、実機画面ではない。

次は未統合の原作レイアウトと開店手順を本体へ移すことを優先する。特に入口・屋外が既存クライアントの上側配置、原作は小型縦長で左側配置。原作の全30レイアウト／無料ではない初期什器・商品の会計／ライバル出店時のサイズ・配置・採用／原作メニュー・音源・アニメーションは残る。ここを完了扱いしない。ユーザーは解析検証のみを増やす進め方を望んでいない。

解析入力の復元は既存analysisブランチ2c00ba53とrestore-latest.py。資料を復元した場合も原作画像と小さな表だけをtools/ps1/export_recovered_runtime.pyで本体へ渡す。巨大チェックポイントを本体ブランチやAPKへコピーしない。
