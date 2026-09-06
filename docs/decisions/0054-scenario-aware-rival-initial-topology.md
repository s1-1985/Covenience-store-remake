# Decision 0054: シナリオ別ライバル初期構成を証拠制約として分離する

## Status

Accepted.

## Context

`docs/research/scenario-initial-rival-topology-2026-09-06.md` で、1997年PlayStation版の開始時ライバル店舗構成について次が直接プレイ記録から支持された。

- 中級: 本店1 + 支店2の計3店舗。
- 上級: 本店1のみ。
- 初級: 開始時に少なくとも買収可能な支店が存在するが、総店舗数は未確定。

一方で正確な座標、店舗サイズ、内装、店員、販売許可、営業時間、価格方針は未復元である。また今回の証拠はPS版であり、SS版へ自動適用できない。

既存 `RivalChainRuntime` は開店・閉店・買収の明示状態遷移を表現できるが、シナリオ開始時の構成差を表す層は持っていなかった。

## Decision

シナリオ初期化を共通固定配置にせず、`scenario_initial_state.py` に以下の境界を置く。

- `FirstTitlePlatform` と `FirstTitleScenario` を明示する。
- `RivalTopologyEvidence` で、完全に確定した場合のみ `exact_roles` を持つ。
- 総数が未確定でも存在だけ確認できた役割は `required_roles` で保持する。
- PS中級は `[HQ, BRANCH, BRANCH]`、PS上級は `[HQ]` を exact とする。
- PS初級は exact count を `None` のままにし、少なくとも `BRANCH` 1店舗を required とする。
- SS版は今回のPS証拠を継承せず、全シナリオとも topology 制約を未知のままにする。
- 実際の store ID / location は `RivalStoreSeed` として caller/data から供給する。未確認座標のplaceholderを生成しない。
- runtime構築前に、回収済みのrole/count事実だけを検証する。

## Consequences

攻略本・動画・SS実機確認から座標や店舗属性が追加された場合、シナリオデータ側を拡張して `RivalChainRuntime` へ渡せる。ライバルAIの出店条件や座標選定式を今回の開始状態から逆算する必要はない。

## Explicitly unresolved

- PS初級の正確な開始ライバル総数。
- PS各シナリオの正確な初期座標。
- PS通常版/Best/Major Wave間の差。
- SS版のシナリオ別初期構成。
- 初期店舗のサイズ、内装、店員、販売許可、営業時間、価格設定。
- 上級開始後の最初の支店出店条件・時期・場所選定式。

これらは観測または攻略本根拠が入るまで推測で埋めない。
