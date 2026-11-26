# 0187: 使わない機能を外したGodotエンジンでAPKを作る(タスク#116)

## 背景

タスク#115の後も、APK(26.29MiB)の約7割はGodotエンジン本体(`libgodot_android.so`)だった。
これまでは公式の debug テンプレートを使っていた。その中身は次のとおり。

| | 展開後 | APK内(圧縮後) |
|---|---|---|
| 公式 debug テンプレート | 65.5MB | 22.1MB |
| 公式 release テンプレート | 60.1MB | 19.1MB |

このゲームがエンジンで使っているものは次だけである。

- 2Dの描画(`gl_compatibility`)
- GUI部品(OptionButton・SpinBox を含む)
- GDScript
- PNG・WebPのテクスチャ
- TTFフォント1つ
- 合成した効果音(AudioStreamWAV)

3D、Vulkan、ネットワーク、正規表現、音声ファイルや3Dモデルの読み込みは使っていない。

## 決定

Godot 4.3-stable をソースから自前でビルドする。ビルド方法は `tools/build_godot_templates.sh` にまとめた。

主な設定は次のとおり。

- `disable_3d=yes`、`vulkan=no`(OpenGL/GLES3だけ残す)
- `modules_enabled_by_default=no` として、次のモジュールだけ有効にする。
  - gdscript、freetype、webp(#115の非可逆テクスチャ用)
  - svg(標準テーマのアイコン用)
  - text_server_fb
- `optimize=size`、`production=yes`、`deprecated=no`、`brotli=no`

Android用の手順は次のとおり。

- ビルドした `.so` を strip する。
- 公式 `android_release.apk` テンプレートの中の `.so` と入れ替える。
- 結果を `build/templates/android_release.apk` に置く。
- Java側は公式のまま。JNI関数37個が公式と同じであることを確認した。

書き出しは次のとおり。

- `export_presets.cfg` の `custom_template/release` を上のファイルに向ける。
- `--export-release` で書き出す。
- 署名はこれまでと同じデバッグ用キーで行う(`GODOT_ANDROID_KEYSTORE_RELEASE_*` 環境変数)。上書きインストールできるようにするため。

文字の表示エンジンは次のとおり。

- ICU/HarfBuzz版(text_server_adv)をやめ、簡易版(text_server_fb)にした。
- 日本語の折り返しは、`AUTOWRAP_WORD_SMART` が1行に入らないときに文字単位で折り返すことで行われる。
  - 簡易版は空白以外の区切りを知らないため、この仕組みに頼る。
- 禁則処理(句読点を行頭に置かない等)はしない。

## 結果

| | 変更前 | 変更後 |
|---|---|---|
| libgodot_android.so(展開後) | 65.5MB | 33.7MB |
| libgodot_android.so(APK内) | 22.1MB | 10.0MB |
| APK | 26.29MiB | 16.31MiB |

## 確かめたこと

同じ設定でLinux版(`template_debug`)もビルドし、次を確認した。

- headless_smoke.gd と android_preview_smoke.gd が通る。
- 11画面を撮り、公式エンジンと比べた。
  - 違いは文字の位置の数ピクセルだけだった。
  - 日本語の表示・折り返しに崩れはなかった。

確かめていないことは次のとおり。

- Android実機での起動は、この環境では確かめられない(KVMがなくエミュレータが動かない)。
- 公式テンプレートの0.1.14を、戻せる版として残す。

## テスト

- `test_slim_engine_template_keeps_what_the_game_uses` は次を確かめる。
  - ビルド設定に必要なモジュールが入っている。
  - 書き出し設定が自前テンプレートを指している。
  - ゲームが、外した機能を使っていない。
    - 3Dノード、Navigation、RegEx、HTTPRequest は使っていない。
    - ogg・mp3・wav・jpg・glb・gltf・svg・webp の素材ファイルもない。
- CIの2つのsmokeは、これまでどおり公式4.3で動く。

## 変更したファイル

- `tools/build_godot_templates.sh`(新規)
- `game/export_presets.cfg`(release テンプレート、0.1.15-preview、version code 16)
- `reference_sim/tests/test_game_vertical_slice_contract.py`

## 今回やらないこと

- テンプレートのファイル(13MB)はgitに入れない。`build/` は `.gitignore` の対象である。
  - 別の環境では、まず上のスクリプトでビルドする。
- 使わないクラスを個別に外す `build_profile` は使わない。
  - 4.3では登録を外すだけで、コードは残るため。
- `libc++_shared.so`(APK内1.7MB)はそのまま。
