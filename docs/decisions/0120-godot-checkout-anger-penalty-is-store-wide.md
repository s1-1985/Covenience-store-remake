# 0120: チェックアウト怒りペナルティを店員全員へ適用するよう是正(タスク#51)

## 背景

前回のPDF一次資料読み取り(タスク#50、`docs/research/strategy-guide-
shopkeeper-manual-part1-2026-09-19.md`第7節)で、「新人店長実習マニュアル」
book pp.34-35に「お客さんに怒られると店員全員の能力が下がってしまう」という
記述があり、`checkout_anger.gd`(タスク#49、決定書0118)が現在の対応
スタッフ1名のみにペナルティを適用している実装と食い違う可能性がある、と
CONTRADICTS候補として記録されていた(`PROJECT_MEMORY.md`第21.4節)。

本タスクでは、書籍のスキャンPDFに引き続きアクセスできたため、該当ページ
(book p.34-35)を直接再読して裏付けを取った。実際のページテキストは以下の
通り:

> お客さんの生の声「店舗評価を聞く」... お客さんに怒られると店員全員の
> 能力が下がってしまうので踏んだりけったり。

および同ページのコラム「怒られるまえに外へつまみだす」:

> 怒りやすいお客さんは、おじさんやおじいさんに多い。もしレジ前の混雑に
> この人が混じっていたら、カーソルをこの人に合わせて決定ボタン。怒り出す
> まえに"つまみだす"を選んで、お店の外に出してしまうといいぞ。

前者は明確に「店員全員」(store-wide)と述べており、CONFIRMED_OFFICIALな
一次資料として、タスク#49が採用した「対応したスタッフ1名のみ」という
REMAKE_BALANCED_DEFAULTのスコープ限定を上書きするに十分な根拠と判断した。
CLAUDE.mdの優先順位ルール上も、確認済み証拠が独自の簡略化より優先される。

「つまみだす」機構自体(客が怒る前にプレイヤーが先回りして退店させる)は
別途新規メカニクスであり、本タスクの範囲外として次タスク候補に残す。

## 決定

### `VerticalSliceSimulation`の該当チェックアウトフェーズ処理

`staff.checkout_staff()`1名のみに`_checkout_anger.apply_penalty()`を
呼んでいた箇所を、`staff.all_staff()`の全メンバーに対してループ適用する
形へ変更した。`checkout_anger_triggered`イベントのペイロードは、単一の
`"skills"`辞書から、スタッフIDをキーとした`"skills_by_staff"`辞書へ変更
(どの客がどのスタッフを担当していたかを示す`"staff_id"`フィールド自体は
引き続き保持)。

`checkout_anger.gd`自体(`apply_penalty(staff_member)`関数のシグネチャ・
-2の値・床0の値・発火閾値の倍率)は変更していない——今回の是正はあくまで
「誰に適用するか」というスコープの問題であり、ペナルティの中身
(REMAKE_BALANCED_DEFAULTの発火閾値・CONFIRMED_COMMUNITYの-2という数値)
自体は従来通り。

## テスト

- `game/scripts/headless_smoke.gd`: 既存のチェックアウト怒りシナリオに、
  「チェックアウトを担当していない、もう1名のスタッフ」の5スキルも
  同様に-2されていることを検証するアサーションを追加(担当スタッフだけで
  なく、店舗全体に適用されていることを直接確認)。Godot 4.3公式バイナリで
  831ステップ(タスク#50時点と同じ、新規シナリオを追加していないため)
  でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 既存の
  `test_checkout_anger_penalty_is_wired_into_checkout_service`に、
  `for angered_staff_member in staff.all_staff():`というループ構造の存在
  確認、`checkout_anger_evidence_note`が`CONFIRMED_OFFICIAL`および
  「店舗全員へ適用」という記述を含むことの確認、`headless_smoke.gd`の
  新規アサーション文言の存在確認を追加。フルスイート663件、xfail 1件、
  全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`: チェックアウトフェーズの
  怒りペナルティ適用ループを全スタッフへ拡張、コメント・イベント
  ペイロードを更新。
- `game/data/vertical_slice.json`: `simulation.checkout_anger_evidence_note`
  を、店舗全体への適用が確認済みである旨を反映するよう更新。
- `game/scripts/headless_smoke.gd`: 非担当スタッフの検証アサーションを
  追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 上記の
  検証アサーションを追加。
- `PROJECT_MEMORY.md`第11節(広告の人気度、タスク#50読み取り中に発見した
  別の陳腐化——航空船/ラジオ/テレビCMの人気度上昇値がwiki由来の古い数値
  のままだった)も本コミットで併せて是正した(コードは既に正しい値
  (+40/+60/+90)を持っており、`PROJECT_MEMORY.md`のみが古い値
  (+30/+50/+100)を表示していた)。

## 明示的に対象外とした限界

- 「つまみだす」(怒る前に客を強制退店させる)機構は、今回発見した同じ
  ページに存在が明記されている新規メカニクスだが、本タスクでは実装せず
  次タスク候補として残した。
- ベンチ維持費の168(クイックリファレンス由来の間接値)vs 160
  (実習マニュアル由来の直接値、既存コードの値)の食い違いについても、
  実習マニュアルbook p.118を直接再読して確認した——「維持費 160」と
  明記されており、既存コードの160は正しい。`PROJECT_MEMORY.md`第21.4節
  から解決済みとして除外した(コード変更なし)。
