# SS版リビジョン識別メモ（2026-09-06）

対象は初代『ザ・コンビニ ～あの町を独占せよ～』のセガサターン版のみ。

## 結論

初代SS版には、少なくとも商品コードの異なる2系統が存在する。

- 通常版: `T-4310G`
  - 発売日: 1997-03-20
  - 価格: 5,800円
  - JAN/EAN: 4959143850088
- サタコレ版: `T-4319G`
  - 発売日: 1998-10-22
  - 価格: 2,800円
  - JAN/EAN: 4959143850194

Satakore.com は両者を互いの Alt Version として明示している。
GameFAQs の Saturn Release Data でも同じ2商品コード・発売日が一致する。

Evidence: **CONFIRMED-RELEASE-METADATA**

## 再現調査上の意味

これまでSS版について、販売許可無料取得など一部の裏技/不具合が「一部バージョンでは修正されている可能性」とされる資料があった。
今回、少なくとも通常版とサタコレ版という明確な流通リビジョン境界を識別できたため、今後SS実機証拠には可能な限り以下を付与する。

- `SS-T4310G`
- `SS-T4319G-SATAKORE`
- 判別不能な場合は `SS-REV-UNKNOWN`

ただし現時点では、**どのバグ/仕様差がどちらの版に属するかは未確定**である。
商品コード差だけから内部プログラム差を推定してはならない。

## 実装方針

PS/SS共通baselineには、SSのリビジョン依存挙動を混ぜない。
SS固有再現を行う場合でも、まず通常版を基準候補とし、サタコレ版との差が一次/実機証拠で確認できた項目だけ互換フラグ化する。

推奨例:

```text
platform = SS
revision = T4310G | T4319G | UNKNOWN
compatibility_flags = { ...verified revision-specific behaviors only... }
```

## 未確定

- T-4310G と T-4319G のROM/実行バイナリ差分
- 販売許可無料取得バグがどちらで成立するか
- 日付境界価格変更技がどちらで成立するか
- セーブ互換性
- 説明書・ゲーム内表記差

## Sources

- Satakore.com, The Conveni ~Ano Machi wo Dokusen seyo~ [T-4310G]
  - https://www.satakore.com/sega-saturn-game,,T-4310G,,The-Conveni-Ano-Machi-wo-Dokusen-seyo-JPN.html
- Satakore.com, The Conveni ~Ano Machi wo Dokusen seyo~ (Satakore) [T-4319G]
  - https://www.satakore.com/sega-saturn-game,,T-4319G,,The-Conveni-Ano-Machi-wo-Dokusen-seyo-Satakore-JPN.html
- GameFAQs, Saturn release data
  - https://gamefaqs.gamespot.com/saturn/577712-the-conveni-ano-machi-wo-dokusen-seyo/data

## 著作物保存方針

原作画像、音声、ロゴ、説明書本文の転載は保存しない。本ノートはリビジョン識別用の事実情報と調査上の解釈のみを記録する。
