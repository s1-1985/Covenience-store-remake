# Android再実装の引継ぎ — v0.2.1-source-interior

AGENTS.mdとdecision0208を読む。目的はエミュレータ非依存の初代ザ・コンビニAndroid再現。原作解析の検証件数を増やすことを作業の中心にしない。

前回の0.2.0作業ファイルを復元して7cd3fbbへ保存した上で、原作の敷地・床・壁・入口・24種類の家具入りサンプルを本番へ接続した。原作30レイアウトはgame/data/ps1_interiors.jsonに保持。SourceLayoutChoiceで開店時に4サンプルを選択可能。初期什器と移植在庫は建物と一緒に支払う。同じ小型店のままサンプルだけ変えた場合もtry_buy_store_siteが再構築する。

StoreLayoutには固定壁が入り、編集・移動・再開でも通り抜けられない。原作敷地は屋外を既に含むためhas_outdoor_lotはfalseを返す。この経路では自販機と駐車場をlayout.fixturesに持つ。旧クライアントの追加屋外領域と混ぜない。原作の大型縦長は内部9×11で、既存仮データ8×12とは異なる。

tools/run_recovered_checks.py <Godot4.3> は7本を実行。source_interior_smokeは24配置と小型8配置の営業を検査。recovered_ui_smokeは実画面のサンプル2選択も検査する。reference_simはPYTHONPATH=. python -m unittest discover -s tests。

APKはConveni-Android-v0.2.1-source-interior.apk。パッケージcom.conveniremake.recovered、versionCode23、前回0.2.0と同じ署名。更新用の鍵は前回のConveni-Android-v0.2.0-build-support.zipを保持し、Gitへ入れない。Android実機未確認。旧セーブは旧内装を維持するため、新しい内装は「はじめから」で確認。

残課題: 空レイアウトからの手動開業、原作の配置許可判定、レジ一体宅配便/27番目特殊商品の販売、人物アニメーション/性別、原作メニュー・音源、ライバルの店舗規模と採用選択、全シナリオ。レイアウトと商品の原データを移したことをゲーム全体の完全再現と混同しない。

branch: chatgpt/android-source-interior-20261105。mainおよびClaude管理ブランチを変更・マージしない。
