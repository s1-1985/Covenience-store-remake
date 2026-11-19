# 解析成果の保存方針

2026-11-03、ユーザーから「解析したデータは全てgitへアップ」と指示された。

- 保存先：s1-1985/Covenience-store-remake の chatgpt/ps1-analysis-recovery-20261103。
- 解析コード、根拠、検証結果、生成データ、再現に必要な入力・パッチ・乱数シードを保存する。
- まとまった検証ごとにコミットし、保存内容を読み戻して確認する。
- 巨大な原本は分割保存と復元スクリプトで保持し、サイズ・ハッシュで完全性を確認する。
- 元ファイルへのリンクだけの登録を、実データのバックアップ完了とは呼ばない。
- 実験用入力、到達した原処理、代用した外部境界、未検証部分を記録する。
- 原資料の変更や結果の再解釈では、過去の記録と更新後の結論を区別する。
- 解析成果は専用解析ブランチへ保存する。解析が必要範囲まで済んだら、スマホ版へ反映してAndroid APKをビルドする。
- mainや並行する他者のブランチを勝手に上書き・マージしない。

## 最新の作業優先順位（ユーザー指示、2026-11-13）

- 主作業はPSディスクイメージのデータ解析である。ファイル構造、画像・音声・配置・マスターデータ、原プログラムから仕様を抽出する。
- 解析後は、必要な仕様とデータをスマホ版へ反映してAPKをビルドする。
- 検証は抽出や移植の正しさを確かめるために行う。営業を何百更新も延長したり、検証回数を増やしたりすること自体を成果にしない。
- 通常プレイの再現に必要な未解読データを優先する。解読済みの内容と新しい発見を区別し、未確認事項を明記する。

## 重複防止の追加方針（2026-11-17）

- 作業前に既存報告・JSON・r2モデルを照合し、未解明の問いを特定する。直近報告にないことだけで未解析と判断しない。
- 既知ルールの画像・文字列接続と、新しい仕様解明を分ける。参照追加で済む内容について同じ解析報告・原バイトを繰り返し作らない。
- 未解明の意味・条件・更新経路を優先する。画像接続は具体的な移植上の欠落がある場合に行い、未解明課題の解決件数には加えない。
- 結論を得られなかった調査は未解明のまま記録する。検証は必要最小限とする。
- [直近3件の重複監査・店員+16の限定調査](analysis/20261117-novelty-audit/README.md)：主要仕様は既存成果と重複。新規仕様解明0件、追跡未解明6件のまま。

## 保存済み

- [2026-11-16：現金商品と引出機2種・12内装配置・通常候補と専用通知、R01を限定](analysis/20261116-cash-dispenser-data/README.md)

- [2026-11-16：調査済み状態の月初消去を接続、残件R03解明・固定ID台帳を新設](analysis/20261116-inspection-lifetime-data/README.md)

- [2026-11-16：天候生成と月別表示60対応・144型の判定・4マップ320構成と祭り迂回](analysis/20261116-weather-demand-data/README.md)

- [2026-11-16：調査・買収・売却、初期11店の価格と29店員参照・帳簿初期化](analysis/20261116-acquisition-sale-data/README.md)

- [2026-11-15：ライバル18内装・72配置/マップ接続、初期11店の撤退資産と採用・価格設定](analysis/20261115-rival-management-data/README.md)

- [2026-11-15：余剰資金寄付・アイドル来客記念・祭り、原メッセージと人気の更新範囲](analysis/20261115-donations-milestone-data/README.md)

- [2026-11-15：年次評価5項目・累積来客と年商、4マップと誘致人口72例・100点7条件](analysis/20261115-annual-evaluation-data/README.md)

- [2026-11-15：誘致18種類・21万6000始点の費用、完成客構成と区画外撤去](analysis/20261115-town-project-data/README.md)

- [2026-11-15：街発展・地価、4マップ12000セルの補正と住宅・会社・公共施設・行政更新](analysis/20261115-town-growth-land-data/README.md)

- [2026-11-15：既存店改装と出店4経路の現金・帳簿差、初期11店資産と36サイズ変更・3保存系列](analysis/20261115-remodel-accounting-data/README.md)

- [2026-11-14：内装53什器・27商品・30配置の購入返金、4197商品差額と標準出店6件](analysis/20261114-interior-transactions-data/README.md)

- [2026-11-14：土地・建物82行と11564区画の取得費、6段階の建築費・出店時の街セル更新](analysis/20261114-land-construction-cost-data/README.md)

- [2026-11-14：販売許可3種類、制限再構築と全11564出店候補、30配置・64費用組合せ](analysis/20261114-permit-siting-data/README.md)

- [2026-11-14：宣伝5種類・32選択、5倍資金条件と継続設定、原「人気」欄と日次補正](analysis/20261114-advertising-popularity-data/README.md)

- [2026-11-14：強盗・火災の条件、全53什器と30配置、被害表示と現金・客・店員の後処理](analysis/20261114-robbery-fire-data/README.md)

- [2026-11-14：防犯・周辺施設のセル加算、客144件と初期11店舗、万引き被害通知](analysis/20261114-security-theft-data/README.md)

- [2026-11-14：駐車3什器・30レイアウト・初期11店舗と部分入店の需要減算](analysis/20261114-parking-arrival-data/README.md)

- [2026-11-14：客144購買型の待機・会計・混雑警告と全配属店員への能力低下](analysis/20261114-checkout-waiting-data/README.md)

- [2026-11-14：店員35人・4マップの配属、原能力名と成長・休憩・年次処理](analysis/20261114-staff-roster-growth-data/README.md)

- [2026-11-14：41什器の補充閾値・満杯までの継続・在庫不足の2集計](analysis/20261114-restocking-stockout-data/README.md)

- [2026-11-14保存：価格設定・144購買型の店選び・店舗指標の持越し](analysis/20261113-pricing-store-choice-data/README.md)

- [2026-11-13：営業時間7区分・53什器の維持費と人件費の丸め順](analysis/20261113-operating-cost-data/README.md)

- [2026-11-13：床画像・清掃能力指標・汚れ発生と警告判定の接続](analysis/20261113-floor-cleaning-data/README.md)

- [2026-11-13：通常店内の人物描画・休憩姿勢・区間末尾の向きと入力別更新](analysis/20261113-actor-render-data/README.md)

- [2026-11-13：店員・決済イベントから効果音16本／ボイス12本と元サンプルへの連結](analysis/20261113-staff-sound-data/README.md)

- [2026-11-13：季節・来店判定・追加購買と通常選択から除外される2商品枠](analysis/20261113-seasonal-demand-data/README.md)

- [2026-11-13：商品27件・什器53件・現金の識別と方向/月別在庫画像](analysis/20261113-product-stock-data/README.md)

- [2026-11-13：建物・客構成・購買型・外見の連結と人口計算の扱い](analysis/20261113-customer-data/README.md)

- [2026-11-13：ディスク77ファイル・TIM34画像・外部配置の構造解析](analysis/20261113-disc-data-extraction/README.md)

- [2026-11-13：新ライバル店の初日営業と日次決算](analysis/20261113-new-rival-operation/README.md)

- [2026-11-13：自然月次・ライバル出店・会社建築と11,688更新、店舗順モデル修正](analysis/20261113-next-month/README.md)

- [2026-11-13：自然営業200更新・最新10,488更新と復元再開検証](analysis/20261113-operating-continuation/README.md)

- [2026-11-13：人物57描画・12移動と音声開始前の追加描画](analysis/20261113-actor-frame-timeline/README.md)

- [2026-11-12：通常営業800更新・時計20560、日次決算と全証跡の再展開検証](analysis/20261112-operating-continuation/README.md)

- [2026-11-12：人物レコードから544個の原描画パケットと原テクスチャー14画像へ接続](analysis/20261112-actor-packets/README.md)

- [2026-11-11：同一読込確認画面での再試行2条件、正常カード交換後の原デコード・営業復帰](analysis/20261111-load-retry/README.md)

- [2026-11-11：通常営業600更新・次の日次決算と台帳資金突合、最新時計18960](analysis/20261111-operating-continuation/README.md)

- [2026-11-11：営業UIから破損セーブ2条件を拒否・取消し復帰、加算値保存の改変は原デコードへ到達](analysis/20261111-corrupt-load/README.md)

- [2026-11-05：生カード割当・分散14ブロックでの原保存/読込・別実装との相互検証、最新時計17760](analysis/20261105-card-image/README.md)

- [2026-11-05：自社店舗一覧・ライバル調査/買収制限・店内復帰後の保存読込み、最新時計17640](analysis/20261105-view-controls/README.md)

- [2026-11-05：月次後120更新、町変化・月次結果画面・通知中のメニュー制限](analysis/20261105-post-monthly/README.md)

- [2026-11-05：チャット再開後600更新・自然な月次決算到達、最新時計17280](analysis/20261105-resumed-daily-close/README.md)

- [2026-11-05：空カード新規保存・エラー再試行・取消しと最新時計16080](analysis/20261105-card-recovery/README.md)

- [2026-11-05：営業入力から原保存/読込UIと原カード処理へ接続、最新時計15960](analysis/20261105-play-save/README.md)

- [2026-11-04の最新再開点：時計15840・累積7928更新](analysis/20261104-long-continuation/README.md)
- [添付ディスク一致・決算終了判定17条件・決算後120更新](analysis/20261104-disc-continuation/README.md)

- [r2原ZIPの全バイト](archives/20261103-r2/README.md)
- [旧成果物の台帳](archive-index/README.md)
- [会話から復旧した補助記録](2026-11-03-session-recovery/README.md)
- [原カード状態判定の再実行](analysis/20261103-native-card-recovery/README.md)
- [原保存ペイロード処理の再実行](analysis/20261103-native-payload-recovery/README.md)
- [原カードファイル処理の再接続](analysis/20261103-native-file-recovery/README.md)

- [ライバル月次処理の再照合](analysis/20261103-rival-monthly/README.md)

- [町成長の全体実行と到達部分照合](analysis/20261103-town-full-flow/README.md)

- [会社・商業施設の増減モデル（原処理33条件一致）](analysis/20261103-town-balance/README.md)

- [営業継続コードと開始状態の確認](analysis/20261103-operating-continuation/README.md)

- [原カード読書きの短いI/O境界試験](analysis/20261103-card-io-boundaries/README.md)

解析継続時は最新コミットと各README・results.jsonを読んで再開地点を確認する。

- [2026-11-16：祭りの購買型144、初期11店の除外・営業時間7種と在庫10位置・需要と先頭客の境界](analysis/20261116-festival-profile-boundary-data/README.md)

- [2026-11-17：客の待機断念と全店員の能力低下、共通抽選・買物額の売上加算・word16未確定](analysis/20261117-abandonment-staff-decline-data/README.md)

- [2026-11-17：誘致18施設と83購買型・162対応、第一商品と駐車条件を接続](analysis/20261117-project-customer-cohorts-data/README.md)

- [2026-11-17：万引き前の未決済額、通常退店では精算せず次の客の入店で初期化・原購買型32件の条件付き列](analysis/20261117-customer-cart-lifecycle-data/README.md)

- [2026-11-17：誘致完成音の比較領域を呼出し元へ接続、店舗高さ・年次集計とスタックが重なる条件を特定](analysis/20261117-project-sound-stack-data/README.md)

- [2026-11-17：店員35人と初期29配属、休憩復帰・清掃選択の時計位相と接客能力を接続](analysis/20261117-staff-work-timing-data/README.md)

- [2026-11-17：配属の二巡更新・役割交換時の体力全回復と経験加算、word16の候補/配属処理での非参照範囲](analysis/20261117-staff-assignment-lifecycle-data/README.md)

- [2026-11-17：誘致32バイトの新規初期化、18開始レコードと原呼出し元72対応の完成通知音29・R05を限定](analysis/20261117-project-initialization-sound-data/README.md)

- [2026-11-17：画像ロード直接39要求→31画像、32転送表・34画像名・53アイコンと画素/パレット重複を接続](analysis/20261117-texture-runtime-binding-data/README.md)

- [2026-11-17：祭りの範囲外需要、原計算から先頭客状態への条件付き加算と6状態の分岐変更・自然到達は未確認](analysis/20261117-festival-customer-state-data/README.md)

- [2026-11-17：街タイル640枠・建物マスター82行・4マップ12000セルを元画像へ接続、原CPU検証0回](analysis/20261117-town-tile-source-data/README.md)

- [2026-11-17：什器53種×4方向と商品画像264番号、宣言のみ6番号を元画像3枚へ接続・原CPU検証0回](analysis/20261117-interior-source-crops-data/README.md)

- [2026-11-17：30配置の壁1060か所と床画像を接続、KABEE背景16部品・320セルを原画素へ対応・原CPU検証0回](analysis/20261117-floor-wall-background-data/README.md)

- [2026-11-17：店員35人の顔と4マップ140参照、未選択の募集中枠を原画像へ接続・原CPU検証0回](analysis/20261117-staff-portrait-source-data/README.md)

- [2026-11-17：UI枠9部品・矩形8種・カーソル・アイコン8枠を原画像へ接続、透明2枠を区別・原CPU検証0回](analysis/20261117-ui-frame-source-data/README.md)

- [2026-11-17：通知画像8分岐・予約34箇所と誘致18施設の15通知アイコンを接続・原CPU検証0回](analysis/20261117-notification-source-data/README.md)

- [2026-11-17：固定通知5・6の呼出し引数を解釈し幅0の描画省略へ接続、宣伝5種を原画像へ対応・原CPU検証0回](analysis/20261117-fixed-notice-advertising-data/README.md)

- 2026-11-17: [通常HUDの原文字列・文字画像・背景接続](analysis/20261117-hud-source-data/README.md)。11文字列・31文字画像・背景1領域、原CPU実行0回。既知ルールの原データ接続として記録。

- 2026-11-17: [商品選択メニューの原画像・表示名・配置](analysis/20261117-product-menu-source-data/README.md)。27画像・27表示名・什器別172枠、原CPU実行0回。既知ルールを原画素・文字列へ接続。

- 2026-11-17: [販売許可画面の原文・表示状態・選択画像](analysis/20261117-permit-dialog-source-data/README.md)。9メッセージ・EXE状態文1件・画像5領域。取得条件は既存11月14日解析を再利用、原CPU実行0回。

- 2026-11-18: [誘致マスター未命名項目の参照調査](analysis/20261118-project-master-xrefs/README.md)。定型表参照4件・共有変数参照17件を索引化。未命名5項目の意味は確定せずR04継続。原CPU実行0回。

- 2026-11-18: [祭りの客状態6：末尾と空き枠](analysis/20261118-festival-state6-tail/README.md)。前回停止位置の先を原処理2呼出しだけで確認。店舗全体保持・枠非再利用を限定入力で接続。自然到達等は未確定、R02は継続。

- 2026-11-18: [異常客状態6の影響3件](analysis/20261118-festival-state6-effects/README.md)。駐車人数・接客対象・編集取消復元を6限定入口で接続。既知規則の再発見と区別し、自然到達は未確定。

- 2026-11-18: [祭り境界の操作前提3件](analysis/20261118-festival-operation-preconditions/README.md)。実資金内の原買収確定・自社店だけの営業時間変更・他店商品15変更を接続し、元は不成立の4店RAMで店3の範囲外書込みを確認。UI/自然経過は未再現、R02継続。

- 2026-11-18: [価格確定・在庫保持・時計接続の3件](analysis/20261118-festival-confirm-calendar/README.md)。人員設定の誤認を訂正、原編集確定後も在庫40保持、原時計から祭り演出前へ到達。6限定入口のみ、演出以後・自然到達は未確定。

- 2026-11-18: [祭り演出と復帰後の3処理](analysis/20261118-festival-presentation-return/README.md)。専用演出の120描画待機・音声状態/入力終了を読解。演出後の原決算は先頭客/床/集計を保持、期4のライバル・町更新は本体を通らない。再現3限定入口、全演出・自然到達は未確定。

- 2026-11-18: [店員の年境界・異動・取消3件](analysis/20261118-staff-transfer-year-boundary/README.md)。年2開始の原加齢で人物27のFFFF/69120維持、店舗間異動は同一店配属と異なり体力/経験を保持、店長不足後の取消末尾は書込みを復元しない。原6限定入口、R06/R07未解決。

- 2026-11-18: [未解読3系統の参照調査](analysis/20261118-unresolved-reference-audit/README.md)。店員157定型参照、近傍−1比較16件、商品26比較7件を索引化。新しい意味/解消0件、原CPU0回。新しい手掛かりがなければ同じ局所試験・検索を繰り返さない。

- 2026-11-18: [通常レジの要員選択3接続](analysis/20261118-register-staff-selection/README.md)。6レジ幅2/3→判定上限1/2、複数レジの原集計上書き→前置判定、レジ/清掃の接客時計条件一致を35人へ接続。原5限定入口。大枠の通常仕様は既存成果にあり、細部追加と実装済みを混同しない。

- 2026-11-18: [誘致完成音と年次通知の文脈](analysis/20261118-project-sound-event-contexts/README.md)。原年次集計の共有スタック書込みが完成比較まで生存する限定経路を接続。店舗高さ24/年次売上0・−1・100、通知表示中の完成予約を5条件で確認。診断値を自然到達と混同せずR05継続。解析のみ、APK更新なし。

- 2026-11-18: [祭りの空き客枠：入店・人数・占有3接続](analysis/20261118-festival-empty-slot-lifecycle/README.md)。原範囲外需要が空き枠を活動化し、人数0のまま予算設定・未初期化目的地/経路による位置反映へ進む限定結果を追加。原通常生成1例と比較。原10入口、全営業更新0、自然到達・会計完了は未確定、R02継続。

- 2026-11-18: [人数0の会計・レジ使用・退出3接続](analysis/20261118-zero-quantity-service-exit/README.md)。既観測の人数0を会計/退出の指定位置へ接続し、入金0でも完了/店員使用済み、後続待機、退出後占有消去と枠0再利用を原4入口で確認。単独式は既知。自然な購買/経路/祭り到達は未確定、R02継続、APK変更なし。

- 2026-11-18: [祭りの保存・読込み再集計・営業開始・通知乱数4接続](analysis/20261118-festival-load-order/README.md)。原形式のflag1復元→タイトル末尾の客状態書込み→営業開始のflag0/客状態保持を接続。原の再構築フラグ設定と通知乱数1回も確認。原9入口、カード/UI/最初の主更新は未再現、自然到達未確定、R02継続。

- 2026-11-18: [タイトル/営業中読込みの3差分接続](analysis/20261118-title-ingame-load-difference/README.md)。同じ原ペイロードで、祭り解除の前後と客状態書込み、通知50枠の有効バイト解除、戻り値1用の復帰枝を接続。原11入口＋静的分岐、カード/UI/画像/BGM全体は未再現、自然条件未確定、R02継続。

- 2026-11-19: [店舗別グラフの履歴・軸・描画境界](analysis/20261119-research-graph-history/README.md)。損益60期の共通有効範囲、全店平均を含む100万円刻みの軸、原ビットマップの順序/境界を書込値へ接続。原5完了入口・停止位置準備2回、営業0回。売却/採用経験は既知として再試験せず。既存未解決6件は維持、APK変更なし。

- 2026-11-19: [未解決R02・R05：営業復帰と完成音の値の由来](analysis/20261119-unresolved-resume-project-followup/README.md)。従来未解決を先行。タイトル復帰後の原営業ロジック2回と営業中読込の1回を接続、HUD除外。月次通知2条件と正の月次入力→原決算の桁あふれ→年次比較→完成音34を接続。最終再現5条件・原入口29件、全面解消0・6件継続。自然到達未確定、APK変更なし。

- 2026-11-19: [R02：通常生成の入店待ち客・祭り後保存時刻](analysis/20261119-festival-active-admission-save/README.md)。原生成の人数2の客も需要別名書込みで入店初期化を飛ばす比較を追加。祭り後の2分更新→決算早期復帰→原メニュー選択後エンコード→非境界時刻のタイトル再集計を接続。最終原入口22件、全営業0。カード/UI/自然到達・買物中の客は未確認、6件継続。APK変更なし。

- 2026-11-19 方針変更：ユーザー指示で既存未解決6件は一旦保留し、それ以外の通常画面・操作・データを優先。未解決を解消扱いにはしない。
- 2026-11-19: [アンケート上位8件・同数順・空欄・表示位置](analysis/20261119-survey-ranking-ui/README.md)。左右独立の27商品順位、0件非表示、原座標を原3条件で照合。月初リセット/商品名/実績更新は既知として再利用。文字描画は引数捕捉、営業0。APK未変更。

- 2026-11-19: [店舗詳細パネルの表示参照・星・座標・許可](analysis/20261119-store-detail-panel-ui/README.md)。D5C先月売上、C68÷20の星、原清掃/警備/サービス指標、3許可の固定アンカーを接続。原詳細4条件＋既存準備3、描画6子関数は引数捕捉。既知計算式の再解読と区別。未解決6件は保留、APK未変更。

- 2026-11-19: [商品価格UIの平均・定価/UP/OFF・個別表示](analysis/20261119-price-policy-display/README.md)。26設定値の平均と26差分の平均を別々に整数化し、平均41%でも定価となる通常入力を接続。原表示8条件、入力前で停止・描画7子関数は捕捉、営業0。単価/編集確定則は既知として再利用。未解決6件保留、APK変更なし（床修正版22ba479は別作業で実装済み）。

- 2026-11-19: [システム設定と音源・SE/報告フラグ](analysis/20261119-system-settings-runtime/README.md)。BGM1/2/3→音源要求2/3/4、SE/報告ビットの有効フラグ反転、SE OFFでも別音声要求28が呼出しへ進む分岐を接続。原6限定入口、実音声/UI/カード/営業0。既知保存欄を再利用。未解決6件保留、APK未変更。

- 2026-11-19: [宣伝UIのカーソル・複数選択・費用・明暗](analysis/20261119-advertising-selection-display/README.md)。未選択TVの費用500万円とDM＋新聞の合計60万円を独立表示、選択RGB128/64と原アイコンY88・カーソル座標を接続。原表示3条件、準備ABI訂正1回。宣伝マスター/確定則/元画素は既知として再利用。未解決6件保留、APK未変更。

- 2026-11-19: [誘致UIの5列/4列・ページ遷移・18画像対応](analysis/20261119-facility-selection-pages/README.md)。前半10件5列・後半8件4列、上下段を維持する左右4境界、共通アイコンと原座標を接続。原表示2＋入力4入口、GPU/営業/着工/完成0。既知費用/画像ロードを再利用、未解決6件保留、APK未変更。

- 2026-11-19: [設備一覧の固定24時間維持費・39件とAndroid差分](analysis/20261119-equipment-catalog-display/README.md)。原画面の維持費は営業時間でなく24倍、原39件対Android37件の欠落5/混入3を特定。許可明暗・原アイコン/座標を4限定表示で接続。旧equipment_choiceのページ/操作は再解読せず、未解決6件保留、営業/配置/APK変更なし。
