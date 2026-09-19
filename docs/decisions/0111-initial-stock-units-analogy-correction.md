# 0111: `product_catalog`の`initial_stock_units`を類推ベースの値へ是正(タスク#42、是正)

## 背景

PR #212(タスク#41、什器カタログ拡充)のマージ後、ユーザーから改めて
指摘を受けた(意訳):「このプロジェクトは初代ザ・コンビニの再現であり、
攻略本などから解読しきれなかった情報であっても、他の確認済みデータを
元にした類推で進めるべきであって、根拠のない独自要素を勝手に加えては
ならない。直近の作業がそれをやっている気がする」。

確認したところ、このリポジトリには`CLAUDE.md`が一切存在せず、この原則
自体がどこにも明文化されていなかった。タスク#39〜#41を棚卸しした結果、
以下が判明した:

- **タスク#39(該当)**: `product_catalog`に追加した26エントリ全ての
  `initial_stock_units`を、カテゴリごとの規模差(価格50円〜1500円、
  `PRODUCT_CATEGORY_PRICING`側のCONFIRMED_OFFICIALな`max_capacity`は
  10〜120と幅広い)を一切無視して、一律「10」という既存のたばこエントリの
  前例に倣っただけの数値にしていた。実際には同じ`PRODUCT_CATEGORY_PRICING`
  の同じ行に、カテゴリごとのCONFIRMED_OFFICIALな`max_capacity`(什器の
  最大収容力)が既に存在しており、これを無視して無関係な固定値を採用した
  ことになる。これはまさに「類推できる他データがあるのに、根拠のない値を
  発明した」ケースに該当すると判断した。
- **タスク#40(問題なし)**: `RestockTiming`はタスク#33で既にユーザー承認
  済みの`CheckoutTiming`の反比例スケーリングという「形」をそのまま再利用
  したものであり、新たな根拠なき発明ではない。基準値`REFERENCE_
  REPLENISHMENT_SKILL := 13`も35名の確認済みcandidateデータの中央値から
  導出しており、これも類推的な導出である。
- **タスク#41(問題なし)**: 27什器全てCONFIRMED_OFFICIALなデータの純粋な
  移植で、数値の発明は一切なし。

## 決定

### `initial_stock_units`をカテゴリごとの`max_capacity`から導出する値へ変更

`product_catalog`の26エントリ全て(タスク#39で追加した25エントリ、および
一貫性のためタスク#32の既存たばこエントリも含む)について、
`initial_stock_units`を一律「10」から、そのカテゴリ自身の
CONFIRMED_OFFICIAL `max_capacity`値(`PRODUCT_CATEGORY_PRICING`の同じ
ソース行)に変更した。たばこは10→40。

これは依然として「新規に仕入れた商品は、そのカテゴリの什器最大収容力
まで満たして開始する」というこのプロジェクト独自の仮定であり、
`REMAKE_BALANCED_DEFAULT`タグは引き続き必要である(攻略本が実際の発注
ロット数を述べているわけではない)。しかし採用する**数値自体**は、もはや
無関係な固定値ではなく、そのカテゴリに実在するCONFIRMED_OFFICIALなデータ
から導出されたものになった。これが「類推による推定」と「根拠のない発明」
の違いであり、今回の是正の核心。

`evidence_note`も、この導出根拠(該当カテゴリの`max_capacity`)を明記する
形に全26エントリ分書き換えた。`max_capacity`は依然として什器の在庫上限
として強制されるわけではない(このクライアントに在庫上限チェック自体が
存在しない)ため、その旨も明記した。

### `headless_smoke.gd`のハードコードされた副作用の修正

上記の変更をテストした際、`headless_smoke.gd`の許可証ゲート済み商品仕入れ
テストが2箇所で壊れていることが判明した:

- `var expected_procurement_cost := 10 * 175`(たばこの旧`initial_stock_
  units=10`と`restock_unit_cost_yen=175`を直接埋め込んだ期待値)
- `permit_simulation.inventory.get_product("tobacco-1").stock_units != 10`
  (同じく`10`を直接埋め込み)

どちらも`config["product_catalog"]`からたばこエントリを動的に検索して
`initial_stock_units`/`restock_unit_cost_yen`を読み取る形に修正した。
これにより、今後カタログ側の数値が再び変わっても、このテストが無関係な
理由で壊れることはなくなる(これ自体も「他ファイルに同じ値を無根拠に
複製しない」という今回の是正の精神に沿った副次的な改善)。

### `CLAUDE.md`の新設

このリポジトリには`CLAUDE.md`が一切存在せず、今回ユーザーが指摘した
「確認済みデータからの類推を、根拠のない発明より優先する」という優先順位
が、どのセッションにも自動的に伝わる場所に書かれていなかった。プロジェクト
ルートに`CLAUDE.md`を新設し、以下を明記した:

1. このプロジェクトが初代ザ・コンビニ(PS/SS版、1997年)の忠実な再現で
   あること。
2. データ・メカニクスの根拠の優先順位: (1)確認済み証拠 → (2)他の確認済み
   関連データからの類推 → (3)このプロジェクト独自の発明(タグ必須)、
   の順で優先すること。(3)に飛ぶ前に、同じソース行や同じ対象の他の
   確認済みフィールドに使える数値がないか必ず確認すること。
3. (3)に該当する場合の`REMAKE_BALANCED_DEFAULT`タグ付け規律(コード内
   コメント・JSON evidence_note・テストの3箇所全て、決定書だけでは
   不十分)。
4. `PROJECT_MEMORY.md`/`docs/handoff/`の参照方法。

`PROJECT_MEMORY.md`第15節にも同じ優先順位ルールを明文化し、今回の是正
自体をその場で参照できるようにした。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`:
  `test_product_category_catalog_expansion_ports_confirmed_reference_sim_
  pricing`に、全26エントリの`initial_stock_units`が`PRODUCT_CATEGORY_
  PRICING`の対応カテゴリの`max_capacity`と一致することを検証するアサー
  ションを追加(たばこエントリも含む)。フルスイート657件(データ件数
  変化なし、フィールド値のみ是正)、xfail 1件、全てPASS。
- `headless_smoke.gd`: 上記2箇所のハードコード修正後、Godot 4.3公式
  バイナリで734ステップ変化なくPASSすることを確認(たばこの仕入れコストが
  1,750円→7,000円に変わったが、この時点の残高は数百万円台のため影響なし)。

## 実装ファイル

- `CLAUDE.md`(新規、プロジェクトルート): 是正の根本原因(規律の不在)への
  恒久対応。
- `PROJECT_MEMORY.md`: 第15節に優先順位ルールを明文化、第19節に本タスクの
  記録を追加。
- `game/data/vertical_slice.json`: `product_catalog`全26エントリの
  `initial_stock_units`/`evidence_note`を是正。
- `game/scripts/headless_smoke.gd`: たばこ関連の2箇所のハードコードされた
  期待値を、設定から動的に読み取る形へ修正。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 検証
  アサーションを追加。
