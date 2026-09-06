# PS版 販売許可の種類別立地判定 2026-09-06

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 既存researchで未確定だった「酒・たばこ・薬の許可判定が同一ルールか」を、初代PS実機プレイ記録から狭める。
- 後続作の排他距離数値は一切流用しない。

主要ソース:
- 藍「ザ・コンビニ 気ままに上級挑戦（前編）」
  - https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html
- 初代PS/SS専用攻略Wiki FAQ
  - https://wikiwiki.jp/theconveni1/FAQ

---

## 1. 同一地点で酒・たばこは申請可能、薬品のみ申請不可のPS実機記録

PS版上級の連続プレイ記録では、線路付近に3号店を新設する際、近隣にライバル3号店が存在し、そのライバル店はすでに薬品の販売許可を取得していた。

その状態でプレイヤー店舗は:

- たばこ: 申請可能
- 酒: 申請可能
- 薬品: 申請不可

となったことが明示されている。

同じプレイ記録の後半でも、別の敵店舗近接地点で「たばこ・酒のみ申請可能」と再度観測される。一方、敵店舗から離れた別地点では、たばこ・酒・薬品の3種を新規出店時に申請できている。

証拠レベル: **B+ / DIRECT-PLAY-PS / REPEATED-WITHIN-LONGPLAY**

この証拠から安全に確定できるのは、少なくともPS版では販売許可適格性を店舗単位の1つのboolとして扱えない、という点である。

```text
PermitEligibility = {
  alcohol: bool,
  tobacco: bool,
  medicine: bool
}
```

同一地点で3値が異なる状態が実際に発生する。

---

## 2. 薬品許可は近隣店の保有許可と競合している可能性が高い

記録者は、近隣のライバル3号店が薬品申請済みであることを理由として、自店舗では薬品を申請できないと説明している。

初代専用FAQでも、敵味方を問わず既存コンビニが近くにあると酒・たばこ等の販売許可が下りづらくなる、とされている。

この2資料を合わせると、許可判定は少なくとも以下を参照する可能性が高い。

```text
PermitEligibility(store_site, permit_type)
  <- nearby convenience stores
  <- permit_type
  <- nearby store permit state ?
  <- distance / district rule ?
```

ただし、近隣店が「同じ許可を保有していること」自体が直接条件なのか、単に許可種別ごとに排他半径が異なるのかは未確定である。

証拠レベル:
- 許可種別ごとに適格性が異なる: **B+**
- 近隣店の同種許可保有が直接ブロック条件: **B- / PLAUSIBLE INTERPRETATION**
- 許可種別ごとの正確な排他距離: **UNKNOWN**

---

## 3. 新規出店時にも販売許可申請が可能なPS証拠

同じPS上級プレイでは、新店舗建設時に:

- たばこ・酒を申請して建設
- 別地点ではたばこ・酒・薬品を最初に申請

という記述がある。

したがってPS版では、販売許可は少なくとも**新規出店フロー内で申請可能**である。

証拠レベル: **B+ / DIRECT-PLAY-PS**

これは既存のSS版「改築フローで申請可能」という証拠と両立する。現時点では次のように扱うのが安全である。

```text
PS:
  new_store -> permit application: confirmed by play record
  remodel   -> permit application: not yet directly confirmed here

SS:
  remodel   -> permit application: confirmed by exploit/play record
  new_store -> permit application: probable, but separate confirmation desired
```

プラットフォームごとのUI階層そのものは引き続き未確定である。

---

## 4. 後続作の距離数値は不採用

後続作には酒・たばこ・薬品ごとの排他距離や申請料が具体的に記録されている資料が存在するが、本researchでは初代PS/SSへ数値を逆輸入しない。

今回確定するのは「同一地点で許可種別ごとに可否が分かれる」という構造だけであり、距離・料金はUNKNOWNのままとする。

---

## 5. 実装ガードレール

現段階で安全なデータ構造:

```text
PermitDefinition
- id: alcohol | tobacco | medicine
- fee: UNKNOWN
- eligibility_rule: per-type

StorePermitEligibility
- alcohol: bool
- tobacco: bool
- medicine: bool

PermitContext
- candidate_site
- nearby_stores[]
- nearby_store_permits[]
- platform_profile
```

禁止事項:
- 3許可をまとめた `can_sell_restricted_goods` 1フラグにする
- 後続作の排他距離を仮値として固定する
- 「薬品だけ厳しい」と一般化する

最後の点について、今回の記録では薬品だけ不可だったが、別地点・別配置で酒またはたばこだけ不可になるケースが存在する可能性は残る。

---

## 6. 残る未確定

1. 酒・たばこ・薬それぞれの正確な排他距離
2. 判定対象が「近隣コンビニそのもの」か「近隣店の同種許可保有」か
3. 自店舗とライバル店舗で判定が完全に同じか
4. 新規申請後、周辺に競合店が建っても許可は維持されるか
5. PS版の改築時追加申請UI
6. SS版の新規出店時申請UI
7. 各許可の正規申請料

---

## 7. 実装開始可否

販売許可の**状態モデルと種類別適格性判定のインターフェース設計は開始可能**。

一方、距離判定・料金・UI配置の最終固定はまだ不可。実装時は距離や料金をデータ駆動かつ未確定値として差し替え可能にしておくべきである。
