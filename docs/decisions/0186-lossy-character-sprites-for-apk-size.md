# 0186: 店員と客の絵を非可逆圧縮にしてAPKを小さくする(タスク#115)

## 背景

APK 0.1.13 は 29.86MiB だった。配布できる上限は 30MiB で、余裕がほとんどない。
APKの中身を測った結果は次のとおり。

| 中身 | 大きさ |
|---|---|
| エンジン本体 libgodot | 20.84MiB |
| 画像(.ctex) | 5.74MiB |
| dex | 2.00MiB |
| その他 | 約0.9MiB |

画像のうち、店員(280枚)と客(168枚)の絵が 4.37MiB を占めていた。
どちらも 160×160 のPNGを可逆圧縮で取り込み、画面では72pxで描いている。

## 決定

- 店員と客の絵を非可逆圧縮(WebP、品質0.7。Godotの標準値)で取り込む。
  - 取り込み設定は `compress/mode=1`。
- その `.import` ファイルをgitで管理する(`.gitignore` の例外に追加)。
  - 町の絵(#111)と同じやり方。
- 什器・商品・UIアイコンは可逆圧縮のままとする。合わせて0.6MiBと小さいため。

結果は次のとおり。

| | 変更前 | 変更後 |
|---|---|---|
| 店員の絵 | 2.58MiB | 0.48MiB |
| 客の絵 | 1.79MiB | 0.31MiB |
| APK | 29.86MiB | 26.29MiB |

## 見た目の確認

- 元画像、品質0.7、品質0.8を、スマホに映る大きさで並べて比べた。見分けがつかなかった。
- xvfbで店内の画面を撮り、店員の絵を確認した。

## 検討した別案(採らなかったもの)

- 画像をインストール後にgitから落とす案。
  - 画像は5.7MiBしかなく、APKの7割はエンジン本体である。そのため効果が小さい。
  - 通信・保存・失敗時の処理が増える。
- 3Dなどを外したエンジンを自前でビルドする案。
  - 効果は大きいが手間も大きい。今回の対応で足りなくなったときに検討する。

## テスト

- `test_character_sprites_are_imported_lossy_to_fit_the_apk`: 店員280枚と客168枚すべてが `compress/mode=1`・`compress/lossy_quality=0.7` であること。`.gitignore` に例外があること。
- pytest、headless_smoke.gd、android_preview_smoke.gd がすべて通る。

## 変更したファイル

- `game/assets/staff/*.png.import`、`game/assets/customers/*.png.import`(新たにgit管理)
- `.gitignore`
- `game/export_presets.cfg`(0.1.14-preview、version code 15)
- `reference_sim/tests/test_game_vertical_slice_contract.py`

## 今回やらないこと

- ゲームのデータや仕組みは何も変えていない。
- エンジンの自前ビルドはしない。
