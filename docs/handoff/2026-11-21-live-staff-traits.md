# 引継ぎ: 更新後の人物特性を歩行へ接続

基点0.8.8 `8dadb65e92a507f95f6474f3deb42679fd6b843a`。main `688876a4763c5dd006da8cfc36c7e7960d862e28` と未マージPR270を確認。同じ本体ブランチ `chatgpt/ps-ui-touch-audit-20261119` へ積み、他ブランチは変更していない。

## ゲームの変更
native店員の障害物回避が、初期候補表ではなく雑誌受賞/年初強化後の現在の機敏さを使う。旧体力回復経路にも同じ参照先を使用。native休憩の原回復規則、接客/補充/清掃の成長規則、RNG呼出し数は変更しない。原モデル `staff_loop_selected.py` の現役人物+1B参照と本体との差を修正したもので、原EXEの追加実行はしていない。

## 確認
実装 `238b965e250fb5d42b317b4c97ef4232a8c6ba5b`、テスト実行条件修正 `a65af72a14578066a40448a84d4271846716aa29`。
GitHub Actions [Native staff regression](https://github.com/s1-1985/Covenience-store-remake/actions/runs/44868102242) 成功。
Godot4.6.3: live_staff_traits / source_people / staff_response / source_geometry / staff_lifecycle / annual_personnel / annual_personnel_ui / town_press の8本成功。source_peopleは1000tick中34会計とJSON40tickの乱数/状態継続。Pythonの人物成長/回復4ファイルは21件成功。

新テストの最初の失敗は、旧経路なのにnative乱数器を残したテスト設定。UIの初回失敗は起動引数不足。両方修正済み。CIはSCRIPT ERROR/Assertionを成功文字列とは別に明示検出する。fresh import開始時にカスタムフォントの未importエラー2行が出るが、import後の8実行ではSCRIPT ERROR/ERRORなし。エラーなしの全工程とは表現しない。

全Python/広域headlessは今回は再実行していない。0.8.8で記録した既存2件や町寸法等の不一致は解決扱いにしない。

## Android
今回APKは未作成。配布済み最新版はConveni-v0.8.8.apk/code88で、今回の能力参照修正はまだ入っていない。ローカル実行環境がunavailableのため、Godot実行はGitHub Actionsで代替した。元の署名鍵を使用したAPK再ビルド・端末操作/音/性能確認は未実施。

## 続き
今回の2参照漏れは未反映として繰り返さない。次は原状態/同時接客と行列幾何、入力から営業状態への未接続境界を既存解析と照合。原カード互換/全通知演出/全営業RNG/物理店舗履歴順/全5会計欄/既存未解決項目は残る。原カード互換の不足を「Androidの保存自体がない」と扱わない。総残件数や完了率・所要期間はこの一部監査から算出しない。
