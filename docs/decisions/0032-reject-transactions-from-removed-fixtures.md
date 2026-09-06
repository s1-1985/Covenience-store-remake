# 0032 — 撤去済み什器を新規取引対象にしない

## 状況
Claude Code の coverage-driven debug sweep（PR #117）で、`StoreGrid.remove_fixture()` 後も在庫slotと顧客sessionが残り、顧客が撤去済みの商品棚から購入できる状態不整合が再現された。

この不具合を直すために、原作未確認の「撤去時に在庫をどう処分するか」「接客中の客をどう移動させるか」「撤去操作そのものをいつ禁止するか」を決める必要はない。

## 決定
`StoreRuntimeHarness.customer_pick_and_continue()` は、購入対象slotが紐づくfixture instanceが現在もgridに配置されていることを取引直前に検証する。

配置が無ければ `ValueError` とし、在庫減算・basket追加・売上処理へ進ませない。

このガードは「撤去後の世界状態をどう解決するか」を決めるものではない。撤去済みfixtureへ向かっていた顧客session、残存inventory slot、撤去時の返金・廃棄、撤去可否条件は別のevidence-backed policy/explicit operationとして残す。

## 理由
- grid上に存在しない什器が新しい商品取引を成立させるのはruntime整合性の破壊であり、初代固有の式・係数・AI判断を必要としない。
- inventory slot自体を自動削除すると、原作未確認の在庫処分仕様を発明してしまう。
- 顧客を自動force-ejectすると、撤去時の客挙動を発明してしまう。

よって最小限のtransaction gateだけを追加する。

## 未確定のまま残すもの
- 客が利用中/移動中の什器を撤去できるか
- 撤去時の在庫の扱い、返金、廃棄
- 撤去済み什器を目的地にしていた顧客の再経路探索/退店
- checkout等ほかのfixture種別を稼働中に撤去した場合の扱い
- PS/SS間の差

## 回帰確認
PR #117で追加された `RemovedFixtureKnownIssueTests.test_a_fixture_removed_from_the_grid_cannot_still_sell_goods` を通常テストへ昇格し、撤去後の購入が在庫・basketを変更する前に拒否されることを確認する。
