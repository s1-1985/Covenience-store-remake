# 初代公式再配信・PS説明書・実機スクリーンショット追加証拠 2026-09-05

対象: 1997 PS/SS『ザ・コンビニ ～あの町を独占せよ～』のみ。

目的: 攻略本到着待ちの間に、現在アクセス可能な一次寄りソースとPS実機画像から、既存研究にない実装・検証ルートと直接観測値を追加する。

## 1. 2026年「コンソールアーカイブス」版を公式検証ルートへ追加

HAMSTERの公式「コンソールアーカイブス」で本作が2026-07-23にNintendo Switch 2 / PlayStation 5向けに配信されている。

公式ページ記載:
- タイトル: コンソールアーカイブス ザ・コンビニ ～あの町を独占せよ～
- 当時のブランド: ヒューマン
- 当時の発売年: 1997
- ゲーム本編は日本版ROMのみ収録
- オプションメニューとマニュアルは日本語/英語/フランス語/イタリア語/ドイツ語/スペイン語対応
- 価格 1,200円

重要性:
- Web上の二次情報だけでなく、現行ハード上で原作ROM挙動を再検証できる公式ルートが存在する。
- 今後、PS/SS差・イベント条件・数値丸め・AI優先順位など、攻略本だけでは決着しにくい項目の再現テスト用として有力。
- ただし公式ページは「32ビット家庭用ゲーム機」「日本版ROM」としか書いておらず、内部でPS ROMかSS ROMのどちらを採用したかはこのページだけでは断定しない。

Sources:
- https://www.consolearchives.com/title/csa-0023/
- https://store.playstation.com/ja-jp/concept/10017477

Confidence: `OFFICIAL-CURRENT-RELEASE`

## 2. PS1版の説明書画像がWeb上で現存

「PSのトリセツ」にPS1版『ザ・コンビニ ～あの町を独占せよ～』の説明書画像ページが存在する。

確認済み:
- 対象がPS1版であることを明記
- 日本語説明書画像を掲載
- 2026-03-07公開

このソースは画像主体のため、現時点では本文数値を自動抽出せず、以下の一次寄り項目の照合ルートとして使う:
- コマンド階層
- 新規出店/改築/許可申請の画面遷移
- 店員雇用/異動の項目名
- 調査/宣伝/誘致などの正式メニュー名
- 店舗/什器配置時の操作説明
- シナリオ説明

Source:
- https://psinstructionmanual.com/theconveni/

Confidence: `MANUAL-SCAN-ROUTE / PS-SPECIFIC`

## 3. PS実機スクリーンショット: 店舗選択時の小型店価格6,000,000円を直接確認

ピコピコ大百科のPS1版ページに、1997 PS版の実機スクリーンショットが4枚掲載されている。

店舗選択画面の直接観測:
- 日時: 1年目1月1日 00:00
- 所持金: 180,000,000円
- 「店舗を選んで下さい」画面
- 6つの店舗外観候補が表示
- 左上候補選択時に `¥6,000,000` と表示

このため、PS版小型店候補の建設価格6,000,000円は画像で再確認できた。

後続画面の直接観測:
- 1年目1月1日 01:52
- 所持金: 173,997,900円
- 本店内装画面が表示
- 店舗建物と既定レイアウト/商品棚群が既に存在

店舗選択時180,000,000円から01:52時点173,997,900円までの差は6,002,100円。

```text
180,000,000 - 173,997,900 = 6,002,100
```

6,000,000円の店舗価格との差分2,100円が、営業時間中の人件費/維持費/初期処理など何に由来するかは未確定なので固定しない。

また、既知の初級開始資金200,000,000円と画面上180,000,000円の20,000,000円差については、店舗選択前に土地購入が済んでいる可能性が高いが、この4枚だけでは直前の土地購入画面がないため `land_price = 20,000,000` と断定しない。

Sources:
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://www.gavas.jp/upload/save_image/9180_2.jpg
- https://www.gavas.jp/upload/save_image/9180_3.jpg

Confidence:
- small-store selected price 6,000,000: `CONFIRMED-SCREENSHOT-PS`
- pre-store-selection cash 180,000,000: `CONFIRMED-SCREENSHOT-PS`
- post-build 01:52 cash 173,997,900: `CONFIRMED-SCREENSHOT-PS`
- 20,000,000 land interpretation: `INFERENCE-DO-NOT-FIX`

## 4. 6店舗候補UIを直接確認

同じPSスクリーンショットでは、店舗選択画面に2行×3列の合計6候補が表示される。

見た目上:
- 左列: 小型系2方向
- 中列: 中型系2方向
- 右列: 大型系2方向

という既存仮説と整合する。

ただし画像1枚では各候補の正式呼称・全価格・全床寸法までは取得できない。攻略本データ表が到着したら、6候補を `StoreVariantDefinition` へ確定させる。

Confidence: `CONFIRMED-SCREENSHOT-PS` for six visible candidates; class/orientation mapping remains `PROVISIONAL`.

## 5. 初代PS公式系紹介文に「千客万来100万人」目標が存在

旧ゲームアーカイブス版の紹介文を保持するPS Dealsミラーと、PS版紹介サイトのゲーム概要に、オーナーへ要求される目標の例として:
- 都庁を誘致
- チェーン店を10店舗
- `千客万来100万人`

が列挙される。

既知のマップ目標:
- 初級 = 都庁/人口20,000
- 中級 = 10店舗
- 上級 = オーナー評価★5

したがって `千客万来100万人` は既知3モードのうち初級・中級には対応しない。隠し「極上」など別目標である可能性が高いが、現時点でマップとの対応を直接示す証拠はない。

実装上は次のように保留する:

```text
ObjectiveCandidate {
  id: cumulative_visitors_1m,
  threshold: 1_000_000,
  source: PS archive description,
  scenario_assignment: unresolved
}
```

Sources:
- https://psdeals.net/jp-store/game/2451147/%E3%82%B6%E3%82%B3%E3%83%B3%E3%83%93%E3%83%8B-%E3%81%82%E3%81%AE%E7%94%BA%E3%82%92%E7%8B%AC%E5%8D%A0%E3%81%9B%E3%82%88
- https://www.gavas.jp/products/detail.php?product_id=9180

Confidence:
- 1,000,000-visitor objective wording exists: `CONFIRMED-DESCRIPTION`
- assignment to 極上: `UNRESOLVED / HIGH-PRIORITY-CHECK`

## 6. 極上マップの終了条件はWeb資料間でも未解決

PS長期プレイ/コミュニティ資料では:
- 初級・中級・上級クリアで極上解禁は複数ソース一致
- 極上を実際にクリアしたというPSレビューは存在
- 一方、別プレイヤーは極上到達後に「これクリアとか終わりあるのかな」と書いており、条件がUI上分かりにくい可能性がある
- 極上クリア経験者の攻略記述では店舗評価★5を維持できる構成を推奨するが、それが勝利条件そのものとは書いていない

よって極上の勝利条件を★5に再利用するのは危険。`千客万来100万人` 候補を攻略本で最優先照合する。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-momoko/momo-the-conbini.html
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://medaka.5ch.net/test/read.cgi/game90/1232352001

Confidence: `UNRESOLVED-BUT-NARROWED`

## 7. 攻略本到着前の次優先調査

1. PS説明書画像から正式UI遷移を手作業で照合
2. Console Archives公式スクリーンショット/動画からPS/SS差のヒントを回収
3. 6店舗候補の別選択状態スクリーンショットを探索し、中型/大型の建設価格を画像確定
4. `千客万来100万人` と極上マップの対応を探索
5. 古いPS長期プレイ記録から土地価格・許可・誘致・イベントを追加抽出
6. 攻略本到着後に店舗/什器/商品/店員/町施設の完全表へ置換

## 結論

攻略本待ちでも一次寄り証拠の回収余地は残っている。特に2026年公式再配信は原作ROM再検証の新しいルートであり、PS説明書画像は正式UI仕様の照合に使える。さらにPS実機スクリーンショットで小型店6,000,000円を独立再確認できた。`千客万来100万人` は極上勝利条件候補として重要だが、攻略本または直接プレイ画面で対応関係を確定するまで保留する。
