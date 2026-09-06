# シナリオ開始時ライバル店舗構成調査 2026-09-06

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 初級/中級/上級で開始時のライバル店舗構成が同一ではない可能性を整理する。
- シナリオ定義に `initial_rival_store_count` / `initial_rival_store_roles` を持たせる根拠を作る。
- 後続作の初期配置を混入させない。

---

## 1. 中級は開始時点でライバル3店舗という直接プレイ記録

PS版中級の連続プレイ記録では、開始直後について次の流れが明記されている。

- 初級より町が閑散としている。
- プレイヤーが本店を建設。
- ライバル2号店、3号店を買収。
- 筆者が「ライバル店は最初3店舗ありました」と明記。
- そのうち2店舗を買収したため、残るライバルは本店中心の状態になる。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: `B+ / DIRECT-PLAY-PS / EXPLICIT-START-STATE`

### 現時点で安全に置ける中級baseline

```text
scenario = MIDDLE
initial_rival_store_count = 3
initial_rival_store_roles = [HQ, BRANCH, BRANCH]
```

少なくとも「中級開始時はライバル本店1店舗だけ」とする実装は、上記記録と矛盾する。

### 未確定

- 3店舗の正確な座標
- 2号店/3号店の店舗サイズ
- 初期店員構成
- 初期販売許可
- 初期内装
- 初期価格設定/営業時間
- PS通常版/Best/Major Wave、SS版で完全一致するか

したがって今回は**店舗数と本支店構造だけ**を仕様候補へ昇格し、各店舗の完全snapshotは未確定のままとする。

---

## 2. 上級は開始時点でライバル本店のみという直接プレイ記録

PS版上級の連続プレイ記録では冒頭で、開始時について「ライバル店も本店のみ」と明記される。その後、時間経過によってライバルが支店を出し、2年目にはライバル3店舗へ増えている。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

証拠レベル: `B+ / DIRECT-PLAY-PS / EXPLICIT-START-STATE`

### 現時点で安全に置ける上級baseline

```text
scenario = ADVANCED
initial_rival_store_count = 1
initial_rival_store_roles = [HQ]
rival_can_open_branches_after_start = true
```

これは既存研究の「ライバルAIは支店出店→撤退→別地点へ再出店を繰り返す」と整合するが、今回の新規差分は**上級開始時に支店が存在しない**点である。

### 未確定

- 上級開始時ライバル本店の正確な座標
- 本店の店舗サイズ/内装/店員/営業方針
- 最初の支店出店までの条件式
- 出店判断の資金条件
- 出店候補地評価式
- SS版での一致

---

## 3. 中級と上級で開始時の競争圧が異なる

今回の2本のPSプレイ記録を合わせると、少なくとも:

```text
MIDDLE   : rival = HQ + 2 branches
ADVANCED : rival = HQ only
```

という差がある。

これは「難易度が上がるほど開始時ライバル店舗数も単純増加する」という設計ではないことを示す。上級は開始資産1.5億円・オーナー評価★5という別の長期目標を持ち、開始時の町もより閑散としているため、難易度差は店舗数以外の町発展・評価・長期経済にも分散していると考えるのが安全である。

ただし、ここから具体的な難易度補正式を逆算してはいけない。

---

## 4. 初級について今回新たに確定できなかったこと

初級のPSプレイ記録では開始直後にライバル2号店を買収した例があるため、少なくともライバル支店が初期に存在することは支持される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini.html

しかし今回確認した記録だけでは、「初級開始時ライバルが正確に何店舗か」を明示する文言までは得られなかった。

よって:

```text
BEGINNER.initial_rival_store_count = UNKNOWN
BEGINNER.initial_rival_has_branch = true  // evidence exists
```

とし、数は固定しない。

証拠レベル:
- 初級開始時に買収可能なライバル支店あり: `B / DIRECT-PLAY-PS`
- 初級開始時ライバル総店舗数: `UNKNOWN`

---

## 5. 実装への反映方針

シナリオ初期状態を共通固定値にせず、少なくとも以下をシナリオ別データとして持てる構造が必要である。

```text
ScenarioInitialState {
  player_cash,
  initial_town_state,
  rival_stores[],
  scenario_objective,
  scenario_evaluation_rule
}
```

`rival_stores[]` は将来的に以下を保持可能にしておく。

```text
RivalStoreSeed {
  role: HQ | BRANCH,
  position,
  store_size,
  permits,
  staff,
  layout,
  business_policy
}
```

ただし今回確定したのは中級/上級の**開始店舗数とrole構成の一部**だけであり、UNKNOWNフィールドを推測で埋めない。

---

## 6. 版境界

今回の直接証拠はPS実プレイ記録である。

- SS版への自動昇格は禁止。
- PC版、ザ・コンビニ2/3/200X/DS等の初期配置は参照しない。
- PS通常版/Best/Major WaveのROM差が未解決のため、厳密には `PS revision unknown` とする。

---

## 7. 次に確認すべき証拠

優先度順:

1. 初級開始直後の原作画面でライバル総店舗数を直接数える。
2. 中級開始直後のマップ画面で本店+2支店の位置を確定する。
3. 上級開始直後のマップ画面でライバル本店のみであることを一次画面確認する。
4. SS版でも各シナリオ開始直後を比較する。
5. 各初期ライバル店のサイズ・販売許可・店員・営業時間・価格率を採取する。

---

## 8. 現時点の結論

今回新たに実装候補へ上げられるのは以下である。

- PS中級: 開始時ライバル3店舗（本店1 + 支店2） `B+`
- PS上級: 開始時ライバル1店舗（本店のみ） `B+`
- PS上級: 開始後に支店を増やす `B+`
- PS初級: 開始時に少なくとも買収可能なライバル支店が存在 `B`
- PS初級のライバル総店舗数: `UNKNOWN`

この差分により、シナリオ初期化処理を1つの共通ライバル配置で済ませる設計は避けるべきことが明確になった。完全な初期マップsnapshotはまだ未復元であるため、シナリオ開始状態全体の最終固定には至っていない。
