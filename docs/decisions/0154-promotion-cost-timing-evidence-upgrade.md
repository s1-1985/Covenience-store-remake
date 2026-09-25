# 0154: 広告4種のコスト/日時をCONFIRMED_OFFICIALへ格上げ(タスク#84)

## 背景

タスク#83(実素材の床/壁/出入口)完了後、ユーザーから「とりあえずこのまま
どんどん進めてくれ。そして、初代ザ・コンビニの再現ということだけは常に
念頭においてくれ」との指示があった。

次の候補として什器スプライトの実素材化(タスク#83で見つけた
`video_900s.png`/`video_904s.png`)を検討したが、実際に候補領域を切り出して
確認したところ、画面上部の候補群はゲーム内什器ではなく別のUI要素(広告
選択メニューらしき赤バー表示)を誤認している疑いが強いことが判明した。
店舗インスタンスが異なる(自店ではなく「マミーマート2号店」というNPC店舗)
上、動画フレーム1枚だけからグリッド位置・什器種別を確定させるのは
誤認識のリスクが高く、CLAUDE.mdの「データ整合性ルール」に反する誤った
CONFIRMED_VISUAL主張を埋め込みかねないと判断し、慎重を期して今回は
見送った(什器スプライト自体は次タスク候補として残す)。

代わりに、`docs/research/strategy-guide-third-companion-book-full-
extraction-2026-09-24.md`(タスク#65で追加済み、まだ大部分が実装未反映の
資料)の広告表(PDF1 p.36-37、PDF2 p.120-121で完全一致するクロス確認あり)
を確認したところ、`reference_sim/conveni_sim/baseline_data.py`の
`PROMOTIONS`にある新聞広告/飛行船/ラジオCM/テレビCMの`cost_yen`/
`trigger_day`/`trigger_hour`が、現状まだwikiベースの`CONFIRMED_COMMUNITY`
のままであるにもかかわらず、この攻略本の数値と完全に一致していることが
分かった――つまり数値を変更する必要はなく、証拠レベルをより強い一次資料
(公式攻略本、しかも同一書籍内の2ページでクロス確認済み)へ格上げできる、
低リスクで正確な改善機会だった。

## 決定

### `STRATEGY_GUIDE_THIRD_COMPANION`定数を新設

`baseline_data.py`に、既存の`STRATEGY_GUIDE`(「本1.pdf」等、2016-09-16の
別スキャン)とは別の書籍として`STRATEGY_GUIDE_THIRD_COMPANION`を追加した。
「新人店長実習マニュアル」PDF1 p.36-37の広告表がPDF2 p.120-121の
「広告データ」表と完全一致することを明記し、単一ページの読み取りではなく
同一書籍内の独立した2箇所による裏付けであることを示す。

### 4件の`PromotionDefinition`を更新

- `newspaper`: `cost_yen`/`trigger_day`/`trigger_hour`を
  `CONFIRMED_COMMUNITY`(wiki)→`CONFIRMED_OFFICIAL`
  (`STRATEGY_GUIDE_THIRD_COMPANION`)に変更。`popularity_gain`は据え置き
  (wikiの20のみで、攻略本の同表にもこの列の値は明記されていないため)。
- `airship`/`radio`/`tv`: 同じく`cost_yen`/`trigger_day`/`trigger_hour`を
  格上げ。`popularity_gain`は既存のタスク#未詳時点で既に
  `CONFIRMED_OFFICIAL`(`STRATEGY_GUIDE`)済みだったため変更なし。

数値そのものは一切変更していない――全て既存値と攻略本の表が完全一致する
ことを確認した上での証拠レベルのみの更新。

### `game/data/vertical_slice.json`の`evidence_note`を同期

4件のpromotion_catalogエントリの`evidence_note`を上記の格上げ内容に
合わせて更新した。

### 矛盾する発見を記録(解決はしない)

作業中、`reference_sim/conveni_sim/promotion.py`の
`PROMOTION_DECAY_STAR_THRESHOLD`(「オールテクニックガイド」出典、
「ランク評価が3つ星以下の店舗は、1日毎に宣伝の効果が薄れていく」)と、
今回読んだ第三の攻略本の記述(「広告の効果が持続するのは、広告を出した
その日だけ。翌日になると上がった人気度がドンドン下がってしまう」――
星ランクに関係なく全店舗で1日限定効果と読める)が矛盾している可能性を
発見した。CLAUDE.mdの方針に従い、`PROJECT_MEMORY.md`第21.4節に
CONTRADICTS findingとして記録し、どちらか一方を無断で採用することは
しなかった。`promotion.py`の減衰ロジック自体(数値未確定のまま
`PopularityDecayOpportunity`として記録だけする設計)にも一切手を
加えていない。

## テスト

- `reference_sim`: `python -m unittest discover -s tests` / `pytest`
  ともに実行し、既存の`test_promotions_port_confirmed_reference_sim_
  timing_and_apply_at_trigger`が数値(cost_yen/trigger_day/trigger_hour)
  に対する既存アサーションを変更なく通過することを確認(証拠レベル文字列
  自体をアサートしているテストは無かったため、破壊的変更なし)。

## 対象ファイル

- `reference_sim/conveni_sim/baseline_data.py`
- `game/data/vertical_slice.json`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 什器(棚・冷蔵ケース・レジ等)スプライトの実素材化――上記の通り誤認識
  リスクを理由に今回は見送った。次に着手する場合は、単一フレームからの
  推測ではなく、複数フレーム/複数プレイ動画での裏付け、または攻略本の
  什器一覧ページとの照合を組み合わせるべき。
- 広告効果の1日限定減衰ロジックの実装――上記の通り、2つの資料が
  矛盾しているため、どちらかを選んで実装することはしなかった。
- 店舗評価(★1〜5)の増減閾値表(PDF1 p.38-39)の実装――同じ資料内に
  「桁の読み取りに要再検証」という注記があり、より高解像度での再確認が
  必要なため今回は着手しなかった(次タスク候補)。
