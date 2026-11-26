# 0.8.14 — 通常操作を優先した修正

最新共同ラインb75fef5までにPR276の自分の変更とCSRM-005/006/007が採用済み。未マージPR284のHEAD efa76ff09b88123e2c2e36f1fcdab599c2b11a84へカメラ修正を積む。branch chatgpt/playability-camera-20261126。PRは作成後追記。main/他ブランチへ変更せずマージ未実施。

営業中の床更新で店内ズーム/移動位置が失われる症状を変更前に再現。設定辞書全体の店舗判別と旧phone配置による毎回のtransform上書きを修正した。指ピンチ/パンを維持し、店舗/寸法変更時だけfit/centerする。原ゲームルールは変更なし。

全体headless1205step、SCRIPT ERROR/ERROR0件。Python804件成功、操作/営業関連Godot9本成功（7200tick営業/保存/買収を含む）。旧カタログ欠落はdecision0249で解消済みであり再び未解決として引き継がない。

APK0.8.14/code94従来署名。既存PR284レール修正も収録した検証版。実機/実聴未確認。最新の完成確認はdocs/RELEASE_ACCEPTANCE.md、元要件の未完はfull-integration-status.jsonとU-1〜U-6。APK作成やテスト件数を完成扱いにせず、通常操作→継続/保存→残る原作差を優先する。
