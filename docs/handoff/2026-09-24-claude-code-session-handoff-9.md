# 2026-09-24 セッション引き継ぎ(タスク#75〜#81・再現忠実性の再検証ループ・
Android向け初回ビルド)

このファイルは`CLAUDE.md`の運用ルールに従い、`docs/handoff/`配下で最新の
引き継ぎ文書として扱う。`2026-09-24-claude-code-session-handoff-8.md`
(このセッションより前のもの、アセット取り込みパイプラインの話)と矛盾する
記載があれば、こちらを優先する。ただし8節の内容(アセット取り込み)自体は
このセッションでは一切触っていないため、8節の情報は引き続き有効。

## 0. 次セッションが読むべき順序

1. **`CLAUDE.md`**(プロジェクトルート)。
2. **`PROJECT_MEMORY.md`** — 第19節のタスク#75〜#81のログ(このセッションの
   全実装がここに詳細記録済み。このファイルはそれを繰り返さず、要点と
   「次に何をすべきか」だけをまとめる)。
3. **このファイル**。特に2節(再現忠実性の再検証パターン)・4節(Android
   ビルド環境の再現方法)・5節(未着手候補)。
4. 必要に応じて`docs/decisions/0145〜0151-*.md`(このセッションで書いた
   決定書、タスク番号と1:1対応)。

## 1. このセッションで実装したタスクの一覧(詳細はPROJECT_MEMORY.md第19節)

| タスク# | 内容 | PR | 決定書 |
|---|---|---|---|
| #75 | カレンダー表示+ゲームオーバー画面のUI配線 | #252 | 0145 |
| #76 | UIテーマ(`ui_theme.tres`)による見た目のビジュアルポリッシュ | #253 | 0146 |
| #77 | カレンダー表示形式を公式スクリーンショット(`01年目01月01日`)に一致させる修正 | #254(#78と合併) | 0147 |
| #78 | 内装編集コマンドを確認済みの5コマンド(配置/移動/入れ替え/売却/終了)に揃える(入れ替え・売却・終了を新規実装) | #254 | 0148 |
| #79 | 手動補充UIを「対象棚を選択→在庫が閾値以下でのみ有効化」の文脈依存型に作り直す | #255 | 0149 |
| #80 | タスク#79の証拠をCONFIRMED_COMMUNITY→CONFIRMED_OFFICIALへ格上げ(攻略本全文書き起こしとの照合で独立裏付けを発見) | #256 | 0150 |
| #81 | Android向けエクスポートパイプラインを初めて構築、デバッグAPKをユーザーへ直接送付 | #257(マージ済み) | 0151 |

タスク#75〜#81は全てマージ済み。`main`はこのハンドオフ執筆時点で
`b7e84b7`(PR #257のマージコミット)まで進んでいる。

## 2. 再現忠実性の再検証パターン(このセッションで繰り返し発生、今後も想定すべき)

このセッションはユーザーから2回、独立に「本当に初代の再現になっているか」
という厳しい指摘を受けた(タスク#77前・タスク#79前)。いずれも:

1. ユーザーが既存UIの一部を名指しで疑問視する。
2. 実際に`docs/research/`配下の該当ファイルを読み直す(思い込みで実装済み
   ロジックを正当化しない)。
3. 「確認済み事実」と「未確認・自前の発明」を明確に切り分けて報告する。
4. 必要なら実装を修正し、REMAKE_BALANCED_DEFAULTタグ or 新しい証拠レベルを
   コード・JSON・テストの3箇所に反映する。

タスク#80ではさらに、**既にリポジトリに存在していたが読まれていなかった
一次資料**(`docs/research/strategy-guide-third-companion-book-full-
extraction-2026-09-24.md`、タスク#65で追加済み、115ページの攻略本全文
書き起こし)を読み直すだけで、独立の裏付けが見つかった。この資料には
今回使った「手動補充」の1論点以外にも、**まだ実装に反映していない大量の
CONFIRMED_OFFICIALデータ**が残っている(5節参照)。次セッションで新しい
機能を実装する前に、この資料を該当箇所だけでも検索してから始めるのが
効率的(このセッションで得た教訓)。

## 3. ユーザーの直近の要求と、まだ着手していないこと

タスク#80マージ後、ユーザーに次の方向性を尋ねたところ
**「バックエンド(セーブ/ロード等)の監査に戻る」**を選択した。これは
タスク#74(決定書0144、save/load監査)の系譜の続き。ただし、この選択の
直後にユーザーから

1. 「完成度は何%か、あと何が足りないか」という質問
2. 「スマホにインストールしてみたい、インストーラーを出せるか」という
   依頼(→タスク#81として実装)

が続けて入ったため、**「バックエンド監査に戻る」というユーザーの選択自体は
まだ実行されていない**。次セッションの最有力候補はこれ。具体的な監査対象は
未確定(前回のsave/load監査であるタスク#74はチェックアウト待ち行列のバグを
発見済み・決定書0144参照)なので、`vertical_slice_simulation.gd`の
`save_state()`/`load_state()`とその他のsnapshot/restore系関数を改めて
line-by-lineで比較するところから再開するとよい。

## 4. Android向けビルド環境の再現方法(タスク#81、重要: このセッションの
ツールチェーンは永続化されていない)

タスク#81でAndroid向けビルドを一から構築したが、**Godotエディタバイナリ・
Android SDK・署名用keystoreはすべてこのサンドボックスの一時領域
(scratchpadディレクトリ、`/tmp/...`配下)に置いた**。セッションが終われば
消える。次にAPKを作り直す必要が出た場合、以下を再実行する必要がある
(詳細手順・根拠は`docs/decisions/0151-android-export-pipeline.md`参照):

1. Godot 4.3-stable Linuxエディタバイナリ(`https://github.com/godotengine/
   godot/releases/download/4.3-stable/Godot_v4.3-stable_linux.x86_64.zip`、
   CIと同一バージョン)。
2. 同バージョンのエクスポートテンプレート(`..._export_templates.tpz`)を
   `~/.local/share/godot/export_templates/4.3.stable/`に展開。
3. Android SDK `cmdline-tools`(`dl.google.com`)→`sdkmanager`で
   `platform-tools`/`build-tools;34.0.0`/`platforms;android-34`を導入
   (このプロジェクトはGDExtension不使用なのでNDK/Gradleは不要、
   `gradle_build/use_gradle_build=false`のテンプレート経路で足りる)。
4. `keytool`でデバッグkeystoreを生成するか、`android_sdk_path`未設定のまま
   一度エクスポートを試みればGodot自身が自動生成する(既定のエイリアス/
   パスワードは`androiddebugkey`/`android`)。
5. `~/.config/godot/editor_settings-4.3.tres`
   (`[gd_resource type="EditorSettings" format=3]`形式、`type="Resource"`
   ではない点に注意——このセッションで一度ハマった)に
   `export/android/android_sdk_path`・`export/android/java_sdk_path`を設定。
6. `cd game && godot --headless --path . --export-debug "Android" build/
   android/ConvenienceStoreRemake.apk`。

**リポジトリ側に既にコミット済みで再利用できるもの**: `game/export_
presets.cfg`(Androidプリセット本体)、`game/project.godot`の
`textures/vram_compression/import_etc2_astc=true`(これが無いとGodotが
理由を表示せずエクスポートに失敗する、既知の表示バグ)、`.gitignore`
(`*.import`・`.godot/`・`game/build/`を除外——このセッションで初めて
追加した、これも参照)。

## 5. 次セッションへの候補

- **バックエンド監査の再開**(3節、ユーザー自身の直近の選択、最優先候補)。
- **攻略本全文書き起こしの未消化データの実装反映**(2節参照)。タスク#80の
  ときにユーザーへ明示的に伝えた候補: 広告5種の正確なコスト/日時/効果表
  (PDF1 p.36-37)、店舗評価(★1〜5)の増減閾値表(PDF1 p.38-39)、
  季節商品タグ(冷たい飲料/アイスクリーム=夏季、温かい飲料/おでん/
  中華まん=冬期、PDF4 DATA1)、建物別・時間帯別客数表(PDF4 DATA4)。
  いずれも`docs/research/strategy-guide-third-companion-book-full-
  extraction-2026-09-24.md`に一次データが既にある。
- **Android実機での操作性パス**(タスク#81の対象外事項として明記済み):
  タッチ操作のヒットターゲットサイズ、画面回転、ランチャーアイコン。
  ユーザーが実際にAPKをインストールして触った後、フィードバックが来る
  可能性が高い。
- **PROJECT_MEMORY.md第21.3節**に残る、このセッションで触れていない
  既存候補群(施設誘致条件、店員の解雇/復帰ロジック等)。

## 6. 作業ブランチについて

`claude/system-implementation-continue-onn5m7`が本セッションの指定ブランチ。
このセッション中のPR(#252〜#257)は全てマージ済み。次セッション開始時は
通常通り

```
git fetch origin main && git checkout -B claude/system-implementation-continue-onn5m7 origin/main
```

でmain最新(`b7e84b7`以降)から再起動すること(このブランチのPRが毎回
マージされるたびに同じ再起動が必要になる、というのが前セッションから
続くパターン)。
