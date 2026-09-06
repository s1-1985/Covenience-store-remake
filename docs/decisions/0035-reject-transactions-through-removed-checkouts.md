# 0035: 撤去済みレジを通る新規取引を拒否する

## Status
Accepted — 2026-09-06

## Context

PR #121 では、grid から撤去済みの商品什器について `customer_pick_and_continue(...)` が販売を継続できないよう、`StoreRuntimeHarness._require_placed_fixture(...)` による配置確認を追加した。

その後のコードレビュー PR #127 で、同じ整合性ガードが checkout 側には接続されていないことが再現された。具体的には、登録済み checkout を grid から撤去した後でも、顧客をその checkout へ新規ルーティングでき、待機中の顧客について checkout service の開始・売上確定も可能だった。

これは初代1997年PS/SS版における「利用中レジを撤去した際の正しい演出・顧客処理」を断定する問題ではない。現状の headless runtime で、grid 上に存在しない fixture を新規の顧客経路・サービス・決済の有効な取引元として扱ってしまう状態不整合である。

## Decision

`StoreRuntimeHarness` の既存配置ガードを checkout 側にも適用する。

- `add_customer(...)` で `checkout_fixture_id` が指定される場合、現在 grid に配置されていることを要求する。
- `begin_checkout_service(...)` は対象 checkout が現在配置中であることを要求する。
- `finish_checkout_sale(...)` は売上を計上する前に対象 checkout が現在配置中であることを要求する。
- `complete_checkout_sale(...)` は上記2境界を再利用するため追加の独自判定を持たない。

## Evidence-safe boundary

この変更では以下を決めない。

- 顧客・店員が利用中の checkout を原作UIで撤去できるか。
- 撤去操作時に待機客を退店・再経路探索・別レジ移動させるか。
- service 開始後に checkout が撤去された場合、原作では会計を完遂するか中断するか。
- 撤去時の返金、補償、人気、評価への影響。

そのため、この runtime は撤去時の自動副作用を発明せず、存在しない fixture を通じて新しい状態変更や売上計上を進めないところで停止する。将来、実機観測で撤去中の具体的遷移が判明した場合は、その明示イベントをこのガードの上位レイヤーへ追加する。

## Sources

- PR #121: 撤去済み商品什器の transaction guard。
- PR #127: checkout 側の未適用を再現したレビューと xfail テスト。
- 初代1997年PS/SS以外の続編仕様・数値は使用しない。
