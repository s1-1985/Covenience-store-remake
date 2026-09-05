# Claude Code と ChatGPT の分担ルール

このリポジトリは ChatGPT と Claude Code が**並行して**作業する。両者が同時に走っていても事故が起きないように、触る領域を物理的に分ける。

## なぜ分けるか(実際に起きたこと)

2026-09-05、Claude Code が `reference_sim/conveni_sim/store_runtime.py` の状態ガードを修正している最中に、ChatGPT 側が同じファイルへ `1ef14e4 "Compose operating time into store runtime"` で機能追加していた。数時間で `main` が4回進んだ。衝突しなかったのは編集箇所がたまたま離れていたからで、同じ関数を触っていれば普通にコンフリクトしていた。

同時作業で起きうる弊害:

1. レビュー結果が報告した時点で既に古い(指摘対象のコードが書き換わっている)
2. 同じバグを両者が別々の方法で直し、重複したガードや矛盾した実装が残る
3. ChatGPT はブラウザ経由だと Claude Code のオープンPRを認識していない
4. 同一ファイル同一箇所のマージコンフリクト

## 担当領域

| 領域 | 担当 | 補足 |
|---|---|---|
| `reference_sim/conveni_sim/` (本体コード) | **ChatGPT** | Claude Code は原則書き込まない |
| `reference_sim/tests/` | **Claude Code** | テストの追加・修正 |
| `docs/research/` | **ChatGPT** | 調査ドキュメント |
| `docs/decisions/` | **ChatGPT** | 設計判断の記録 |
| `docs/handoff/` | **Claude Code** | 申し送り・レビュー結果 |
| `PROJECT_MEMORY.md` | **ChatGPT** | 方針の正本 |

例外: ChatGPT がテストを書くこと、Claude Code が本体コードを直すことを禁止はしない。ただし**その回だけの明示的な依頼があるときに限る**。デフォルトは上の表。

## Claude Code の作業手順

1. 作業前に必ず `git fetch origin main` して**最新の main からブランチを切る**。古いブランチの上に積まない。
2. 作業単位を小さくし、短時間でマージまで持っていく。長期ブランチを持たない。
3. **レビュー結果・指摘には必ず対象コミットSHAを明記する**。「`0d30789` 時点のコードに対する指摘」と書く。これが無いと、受け取った側は指摘が古くなっているか判定できない。
4. バグを見つけたら、**直すのではなくテストで再現させる**。詳細は次節。

## バグを見つけたときの受け渡し方式

Claude Code は本体コードを直さず、**失敗するテストを `xfail` として `reference_sim/tests/` に追加する**。

```python
@unittest.expectedFailure
def test_xxx_is_currently_broken(self):
    """既知のバグ: <1行で症状>。詳細は docs/handoff/chatgpt-review-notes.md の項目N。"""
    ...
```

この方式の利点:

- 指摘が「文章」ではなく**実行可能な再現手順**になるので、解釈のズレが起きない
- ChatGPT が直すと `xfail` が `XPASS` に変わるため、**直ったことが機械的に判定できる**
- 本体コードに触らないので、ChatGPT の作業と衝突しない

ChatGPT 側は修正後、`@unittest.expectedFailure` デコレータを外して通常のテストに戻す。

## 報告先

- 実行可能な再現テスト → `reference_sim/tests/`
- 判断・解釈が必要な指摘(元資料の読み方、設計方針、証拠レベルの妥当性など) → `docs/handoff/chatgpt-review-notes.md`

Claude Code が判断できないものは断定しない。「事実として確認したこと」と「未検証・要判断」を必ず分けて書く。
