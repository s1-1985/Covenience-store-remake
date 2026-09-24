# 0151: Android向けエクスポートパイプラインを初めて構築(タスク#81)

## 背景

ユーザーから「一度自分のスマホにインストールしてみたいね。インストーラー提示できる？」
との依頼を受けた。PROJECT_MEMORY.md section 1で「Target: Android smartphone game」と
明記されているにもかかわらず、このプロジェクトには`export_presets.cfg`が一度も存在
しておらず、Android向けビルドが一度も試みられていなかったことが判明した
(直前のタスクで行った完成度評価でも「Androidとしての製品化はほぼ0%」と指摘した点)。

このサンドボックス環境にはGodotエディタバイナリ・Android SDK・署名用keystoreの
いずれも存在しなかったため、ゼロから一式構築した。

## 決定

### ビルドツールチェーンをスクラッチパッド配下に構築(リポジトリには含めない)

- Godot 4.3-stable Linuxエディタバイナリ(CIが使う`barichello/godot-ci:4.3`
  イメージと同一バージョン)をGitHub Releasesから取得。
- Godot 4.3-stableのエクスポートテンプレート(`android_debug.apk`/
  `android_release.apk`を含む)を取得し、`~/.local/share/godot/export_templates/
  4.3.stable/`に配置。
- Android SDK `cmdline-tools`を`dl.google.com`から取得し、`sdkmanager`で
  `platform-tools`/`build-tools;34.0.0`/`platforms;android-34`をインストール。
  このプロジェクトは純粋なGDScriptのみでネイティブ拡張(GDExtension)を使用して
  いないため、Godotの「Gradle Build」を使わないデフォルトのテンプレートベース
  エクスポート経路で足り、NDK/Gradleは不要と判断した。
- `keytool`(Java 21が既にこの環境にインストール済み)でデバッグ用keystoreを
  生成(Godotのデフォルトエイリアス/パスワード`androiddebugkey`/`android`と
  一致させた。後で判明したが、Godot自身も`android_sdk_path`が未設定の状態で
  一度実行されると、同じデフォルト値で自動的にデバッグkeystoreを生成する)。
- Godotのエディタ設定(`~/.config/godot/editor_settings-4.3.tres`、
  `[gd_resource type="EditorSettings" format=3]`形式)に`export/android/
  android_sdk_path`/`export/android/java_sdk_path`/`export/android/
  debug_keystore*`を設定。これはこのマシン環境固有の設定であり、リポジトリの
  一部ではない。

### `game/export_presets.cfg`を新規作成(コミット対象)

Godot 4.3-stableの`EditorExportPlatformAndroid::get_export_options()`
(godotengine/godotのソース、同バージョンタグで直接確認)に基づき、以下の
方針でプリセットを手書きした(GUIが無いヘッドレス環境のため):

- `gradle_build/use_gradle_build=false`(前述の理由でNDK/Gradle不要な
  デフォルトテンプレート経路を使用)。
- `architectures/arm64-v8a=true`のみ有効(Godotのデフォルトと同じ、
  Vulkanベースの現行Android端末はほぼ全てarm64)。
- `keystore/*`は全て空文字列のまま(machine-localなエディタ設定側の
  デバッグkeystoreにフォールバックさせる設計。keystoreのパス/パスワードを
  リポジトリにコミットしないため)。
- `package/unique_name="com.conveniremake.app"`(このプロジェクトの
  個人利用限定という性質を踏まえた、Google Play登録を前提としない仮の
  パッケージ名)。
- その他のフィールドはGodotのソースコード上のデフォルト値をそのまま踏襲。

### `game/project.godot`に必須のテクスチャ圧縮設定を追加

Android向けエクスポートは`ResourceImporterTextureSettings::should_import_
etc2_astc()`が真であることを要求するが、このプロジェクトの`project.godot`は
デスクトップ向け設定(`renderer/rendering_method.mobile="gl_compatibility"`)
しか持っておらず、テクスチャのETC2/ASTC圧縮インポートが有効になっていな
かった。これが原因で、Godotの`can_export()`検証が**エラーメッセージ無しで**
`valid=false`を返す(Godot本体の既知の表示バグ: `has_valid_project_
configuration()`内の該当チェックだけ`err`に何も追記せず`valid=false`だけ
セットする)という分かりにくい失敗を引き起こしていた。原因はGodotの
C++ソース(`editor/export/editor_export_platform.cpp`の`can_export()`が
呼ぶ`platform/android/export/export_plugin.cpp`の`has_valid_project_
configuration()`)を直接読んで特定した。

`[rendering]`セクションに`textures/vram_compression/import_etc2_astc=true`
を追加して解決した。これは純粋なエンジン/ビルド設定であり、ゲームデータや
メカニクスではないため、`ui_theme.tres`や`renderer/rendering_method.mobile`
と同じ理由でREMAKE_BALANCED_DEFAULTタグは不要と判断した。

### `.gitignore`を新規作成

このリポジトリには`.gitignore`が一度も存在しておらず、今回テクスチャの
再インポートを行った結果、`game/assets/`配下に666個の`*.png.import`
サイドカーファイルと`game/.godot/`(エディタキャッシュ)が未追跡ファイルとして
大量に出現した。過去のタスクでは誰もGodotエディタでの実際のインポートを
リポジトリのワーキングツリー上で実行していなかったため、これまで気づかれて
いなかった問題である。`.godot/`・`*.import`・ビルド成果物(`game/build/`)・
Python生成物(`__pycache__`等)を除外する`.gitignore`を追加した。

## 成果物

このタスクの直接の成果物として、ビルドした`ConvenienceStoreRemake.apk`
(約30MB、v1/v2/v3署名スキームで検証済み)をユーザーへ直接送付した。
このAPKファイル自体はリポジトリにはコミットしていない(バイナリ成果物であり、
`export_presets.cfg`から再現可能なため)。

## テスト

- `apksigner verify --verbose`でv1/v2/v3署名スキームが全て有効であることを
  確認。
- `aapt dump badging`でパッケージ名・バージョン・対象SDKバージョンが意図通り
  であることを確認。
- `reference_sim`側のテストはこのタスクの変更(`project.godot`のレンダリング
  設定1行、新規`export_presets.cfg`、新規`.gitignore`)に影響されないため、
  既存の745件パス状態を変更しない(Pythonコードは一切変更していない)。
- Godot側は、このタスクの中でエクスポートそのものが最終的に成功した
  (`export: end`、終了コード0、生成されたAPKの署名検証も通過)ことをもって
  実地で検証済み。`headless_smoke.gd`固有の新規アサーションは追加していない
  (ビルド設定タスクであり、ゲームプレイロジックの変更を伴わないため)。

## 明示的に対象外とした限界

- **これはデバッグ(自己署名)ビルドである。** Google Playへの配布や
  正式なリリース署名は範囲外(CLAUDE.mdのdistribution scopeの通り、この
  プロジェクトは個人利用限定であるため、そもそも不要)。
- タッチ操作は`store_view.gd`が既に`InputEventScreenTouch`を処理している
  ため最低限動作するはずだが、実機での操作性の検証(ボタンサイズ、
  スクロール、画面回転対応等)はこのタスクの範囲外。UIは既存の
  「サイドバー型デバッグツール」レイアウトのまま。
- アイコン(`launcher_icons/*`)は未設定のため、Godotのデフォルトアイコンが
  使われる。
- CI(`.github/workflows/`)にAndroidエクスポートジョブを追加することは
  今回のスコープ外(ユーザーからの依頼は「一度手元にインストールしたい」
  という単発の確認であり、継続的なAPK配布パイプラインの要求ではなかった
  ため)。将来的に必要になれば別タスクとする。
