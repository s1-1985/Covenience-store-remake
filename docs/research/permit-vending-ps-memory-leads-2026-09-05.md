# 初代PS 販売許可個別判定・自販機店舗・メモリ検証手掛かり 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』を優先。SS情報は明示したものだけ補助利用する。

目的: 攻略本到着前に、販売許可の判定構造、自動販売機の販売フロー、PS実装の将来検証に使える既存コード情報を整理する。

## 1. 販売許可は3種一括boolではなく、商品種別ごとの個別判定

PS上級の長期プレイ記録で、同一店舗立地について:

- `たばこ` は申請可能
- `酒` は申請可能
- `薬品` は申請不可

という状態が複数回記録される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html

具体例1:
- 線路付近に3号店を建設
- 近くの敵3号店が薬品許可を取得済み
- 自店はタバコ・酒を申請して建設
- 薬品は敵店が近いため申請不可と記録

具体例2:
- 町中央に新店舗を建設
- 敵店舗が近い
- `タバコ・酒のみの申請しかできませんでした` と記録

一方、別立地では同じプレイ中に:
- タバコ
- 酒
- 薬品

の3種類すべてを最初に申請して小型店を開業している。

### 確定できる構造

少なくとも初代PSでは販売許可の可否は店舗全体の単一フラグではない。

```text
PermitEligibility
- tobacco: independently evaluated
- alcohol: independently evaluated
- medicine: independently evaluated
```

Evidence: `CONFIRMED-PLAY-PS` for per-permit differential eligibility.

### まだ確定できないこと

この記録だけでは以下は断定しない:

- `medicine > alcohol > tobacco` の順に排他距離が長い
- 競合店が「同種許可を持っている時だけ」ブロックするのか
- 単に競合店舗の存在だけで各許可が別距離判定されるのか
- 各許可の正確な距離

『ザ・コンビニ2』には 5/7/10マスという完全表があるが、初代へは輸入しない。

### 実装要求

```ts
interface PermitDefinition {
  id: 'tobacco' | 'alcohol' | 'medicine';
  fee: number | Unknown;
  eligibilityRule: PermitEligibilityRule;
  exclusionDistance: number | Unknown;
}
```

`store.canAcquireAnyPermit` のような1個のboolへまとめない。

## 2. 自動販売機だけの店でも売上が成立するというPS攻略記録

PS版Wazapの初代ページに、独立投稿として以下がある。

- `自動販売機だけの店でも結構売り上げがでます`
- 別投稿では `小型店舗を設置して店員一人だけ置き、お店の中は自動販売機だけにする。結構儲かる` とされる

Sources:
- https://wazap.com/game/12333/%E6%94%BB%E7%95%A5/?WAZAP_LAYOUT=0
- https://wazap.com/game/12333/cheats/?order=zupped

Evidence: `PROVISIONAL-COMMUNITY-PS / TWO-POSTS`

### 重要な示唆

通常商品棚では:
- 商品取得
- レジ待ち
- 店員による会計

が主要顧客フローになる。

しかし自販機だけの店舗が放置運用で成立するなら、自販機については少なくとも通常棚と完全同一の購入フローを前提にしない方が安全。

実装候補:

```text
FixtureSaleMode
- CHECKOUT_REQUIRED
- SELF_SERVICE_CANDIDATE
```

自販機を `SELF_SERVICE_CANDIDATE` としてデータモデル上区別できるようにする。

### まだ断定しないこと

Wazap本文だけでは:
- レジが本当に0台でも開店できるのか
- 自販機客がレジを完全に通らないのか
- 店員1名が何の役割で必須なのか
- 補充が自動か店員作業か

までは確認できない。

したがって `vending_machine.checkout_required = false` を現時点で固定しない。

攻略本の設備説明、PSコンアカ動画、実機連続観察で最終確認する。

## 3. 初代PSの改造コードは将来の実装検証手掛かりとして隔離保存

PS版として公開されている古い改造コード資料には以下がある。

Sources:
- https://cheatcode.blog.fc2.com/blog-category-1.html
- https://cheatcode.blog.shinobi.jp/_ps/
- https://wazap.com/game/12333/cheats/?p=2

### 公開コード例

資金20億円:
```text
800CD9F8:9400
800CD9FA:7735
```

店員体力回復:
```text
80036F14:0018
```

レジ・補給・警備・清掃・接客100:
```text
8003AA68:6464
8003AA6A:3402
8003AA6C:001E
8003AA6E:A4A2
8003AA70:0020
8003AA72:A4A2
8003AA74:0022
8003AA76:A0A2
8003AA7C:EC98
8003AA7E:0800
```

### 扱い

これらは**ゲーム内データテーブルのアドレスと断定しない**。

コード列を見る限り、単純なRAM値固定だけでなく実行コードを書き換えている可能性があるため、現在のRemakeマスターへ数値として取り込むものではない。

Evidence: `REVERSE-ENGINEERING-LEAD / NOT-GAME-DATA`

### 将来の用途

正規に所有するPS版を検証可能な環境がある場合、これらの公開済みコードは:
- 店員能力更新ルーチンの所在候補
- 体力消費/回復処理の所在候補
- 能力100の上限処理の観察

を行う際の検索起点になり得る。

ただし現段階ではROM解析をPhase 1完了条件にはしない。攻略本・画面・実プレイ証拠で不足値を埋める方針を維持する。

## 4. 初代SS直接プレイで販売許可の改築フローを再確認

SS詳細プレイ記録では:
- `たばこ・酒・薬品` の許可変更は改装時のみ
- 改装せず許可だけ取得することは不可

と明記。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

PS長期プレイの「新店舗建設時に個別許可申請」と合わせると、Permitは少なくとも:

```text
NewStoreFlow -> permit selection
RemodelFlow  -> permit modification
```

の2つの導線を持つ構造が妥当。

プラットフォーム差が残る可能性があるため、画面遷移の完全一致は攻略本/PS説明書で確認する。

## 5. 今回の実装-ready更新

高確度でデータモデルへ反映してよい:

```text
PermitEligibility is per permit type, not one global boolean.
```

先行して拡張ポイントだけ持たせる:

```text
FixtureDefinition.saleMode
- normal_checkout
- self_service_candidate
```

自販機のself-service確定は保留。

改造コードは実装値ではなく研究資料にのみ保持する。

## 6. 次の優先検証

1. PS/SS初代で、同一立地の3許可可否を画面で同時確認し、排他距離の順序があるか検証。
2. 自販機だけの店でレジ0台が可能か、客が会計へ行くか動画で確認。
3. 攻略本到着後、許可料金・距離・自販機の収容力/維持費/利用方法を照合。
4. PSコンアカの新規出店/改築画面で許可項目ごとの費用表示を回収。
