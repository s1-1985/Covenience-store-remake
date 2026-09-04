# 店員応募者プール・解雇再雇用・体力回復の追加調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 35人の固有店員を「常時35人一覧」と誤実装しないため、応募者表示/解雇/再雇用の挙動を整理する。
- 解雇を使った体力全回復・レジ担当交代という原作裏技を記録する。
- PS/SSで得た証拠を分離する。

---

## 1. 店員は35人の有限固有候補だが、雇用画面には可変の応募者が出る

初代専用店員Wiki:

- 店員は計35人
- それぞれ固有パラメータ
- 最終的に10店舗×3人運営すると30/35人を使う

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

一方、初代専用裏技ページでは、解雇した店員をすぐ再雇用する際:

- `雇用画面に出てこない場合は何度か開き直す必要がある`

と記録される。

Source:
- https://wikiwiki.jp/theconveni1/%E8%A3%8F%E6%8A%80

証拠レベル: CONFIRMED-COMMUNITY

### 実装上の意味

35人全員を常時雇用UIへ並べるのではなく:

```text
GlobalStaffRoster[35]
  each -> employment_state

ApplicantView
  -> subset / refreshed selection of eligible staff
```

のように、固有人材の状態と現在表示される応募者を分離できる設計が原作に近い。

応募者抽選数・抽選アルゴリズムは未確定。

---

## 2. 解雇→即再雇用で体力が全回復する

初代専用Wikiの裏技:

- 体力が減って休憩を始めた店員を解雇
- すぐ再雇用
- 休憩室へ体力満タンで戻る

Source:
- https://wikiwiki.jp/theconveni1/%E8%A3%8F%E6%8A%80

さらにSaturn版Wazap投稿でも:

- 一度解雇して再雇用すると全回復
- 再雇用すると休憩室に戻る
- レジ無人なのに掃除/補充をしている店員を入れ替える用途にも使える

と記録される。

Source:
- https://wazap.com/cheat/%E5%BA%97%E5%93%A1%E3%81%AE%E4%BD%93%E5%8A%9B%E3%82%92%E5%85%A8%E5%9B%9E%E5%BE%A9/578629/

証拠レベル:
- 解雇再雇用による全回復: CONFIRMED-COMMUNITY
- Wazap投稿自体はSaturn版明記

### baseline方針

これは原作AI/雇用処理の抜け穴であり、Android版で必ずバグ互換する必要はない。

ただし内部状態から分かること:

- 解雇後も固有人物は消滅しない
- 再雇用できる
- 再雇用時に勤務状態/体力が初期化される
- 再雇用時の出現地点は休憩室

は参考になる。

---

## 3. 解雇でレジ担当を強制交代できる

初代専用裏技ページでは:

- レジ打ちが遅いキャラがレジに立ったら解雇
- 他の店員がレジへ回ったら再雇用

という操作が記録される。

Source:
- https://wikiwiki.jp/theconveni1/%E8%A3%8F%E6%8A%80

証拠レベル: CONFIRMED-COMMUNITY

### 意味

プレイヤーはタスク割当を直接命令するUIより、**人事操作を使って自律AIへ間接介入**できる。

baselineでは原作の自律AIを重視し、通常操作として「店員Aを今すぐレジへ」のような現代的直接命令を勝手に追加しない。

将来UX改善として追加する場合は deliberate deviation として記録する。

---

## 4. PS版Q&Aでは応募者が一時的にゼロになるケースが報告される

初代PS版のWazap Q&A:

質問:
- 新規出店しようとすると `募集者がいません` のように表示される

回答群:
- 店員になりたい人がいないので待つ
- 解雇しすぎで一時的に募集者がいなくなった可能性
- 期間を置けば再び出る
- 1年以内には新しい人が出るはず、との回答

Source:
- https://wazap.com/question/%E6%96%B0%E3%81%97%E3%81%8F%E5%BA%97%E3%82%92%E5%87%BA%E3%81%9D%E3%81%86%E3%81%A8%E3%81%99%E3%82%8B%E3%81%A8%E3%80%8C%E5%8B%9F%E9%9B%86%E8%80%85%E3%81%8C%E3%81%84%E3%81%BE%E3%81%9B%E3%82%93%E3%80%8D%0D%0A%E3%81%BF%E3%81%9F%E3%81%8F%E5%87%BA%E3%81%A6%E3%81%97%E3%81%BE%E3%81%84%E3%81%BE%E3%81%99%E3%80%82%E3%81%AA%E3%81%9C%E3%81%A0%E3%81%8B%E3%82%8F%2B.../55253/

証拠レベル: PROVISIONAL / PS-Q&A

### 注意

回答はユーザー推測を含み、正確なクールダウン期間を証明しない。

特に `1年以内` を実装値にしてはいけない。

しかし `applicant list can temporarily become empty` という現象自体は質問者のPSプレイで観測されている。

---

## 5. 応募者表示にはランダム/更新要素がある可能性が高い

解雇直後の人物が:

- 雇用画面に出る場合がある
- 出なければ画面を何度か開き直すと出る

という初代Wiki記録は、雇用画面が固定35人表ではなく**候補抽選/ローテーション**を持つことを強く示す。

ただし:

- 画面を開くたび完全再抽選
- 日単位の候補リスト + UI再読込バグ
- ランダム順序

のどれかは未確定。

### baseline候補

```text
StaffCandidate
- id
- employment_state
- temporarily_available
- current_applicant_visible

refreshApplicants()
```

具体確率・人数はUNKNOWN。

---

## 6. 年齢と給料の関係

初代専用店員Wiki:

- 給料は1日あたり
- 雇用画面の表示は24時間営業時の給料
- 営業時間を短くすると異動画面の給料が安くなる
- 基本的に年齢が高いキャラほど給料が高い

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY

### 実装要求

Staffには少なくとも:

```text
age
base_wage
current_effective_wage
```

を分けられる構造が望ましい。

`base_wage = function(age)` と断定はしない。年齢との相関は観測であり、各人物に固定値がある可能性が高い。

---

## 7. 店員体力は完全固定ではなく「わずかに増減」するとの初代Wiki記録

初代店員Wikiでは体力について:

- 高いほど休憩まで長く働ける
- 高体力ほど休憩時間そのものは長めでも、移動時間等を考えると効率が良い
- `わずかに増減する`

と記録される。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY（定性的）

### 未確定

- 年齢で体力上限が変化するか
- 作業経験で体力が成長するか
- 年次更新で変化するか
- イベントによる増減か

よって `stamina_max` を絶対不変の生得値としてハードコードしない。

---

## 8. 内装画面を開くと床汚れが全消去する原作裏技

初代専用裏技Wiki:

- 営業時間外/臨時休業中
- 内装変更画面を開く
- 床の汚れが全て消える

Source:
- https://wikiwiki.jp/theconveni1/%E8%A3%8F%E6%8A%80

証拠レベル: CONFIRMED-COMMUNITY / ORIGINAL-BUG-OR-RESET-BEHAVIOR

### baseline方針

これは互換必須ではない。

ただし、原作内部で内装編集開始時に床状態を再初期化していた可能性を示す歴史的証拠として保持する。

Android版では原則修正し、もし原作互換モードで残す場合だけ明示的に扱う。

---

## 9. 現時点のStaffライフサイクル候補

```text
StaffIdentity (finite 35)
- id / name / age / innate stats
- current skills
- stamina
- employment_status
- assigned_store

ApplicantSystem
- eligible identities
- visible subset
- refresh behavior UNKNOWN

Employment
HIRED -> ASSIGNED -> WORKING/RESTING
HIRED -> FIRED -> ELIGIBLE_AGAIN
FIRED -> REHIRED (can reset stamina in original)
```

### まだ不明

- ライバル雇用中の人物を自社が雇えるか
- ライバル店買収時に店員が自社へ引き継がれる正確なルール
- 35人全員の初期所属/初期応募可否
- 年齢更新・引退・死亡の有無
- 応募者更新周期

これらを攻略本/実機で継続確認する。
