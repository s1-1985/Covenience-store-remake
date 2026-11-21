# 0243 — 取消・強制退店と未払い精算の整合性

- 採用指示書: muse/analysis / 2b3e990aacf69487520ca1ffd7b6519df7285fdb / docs/muse/ready/CSRM-004.md v1
- 基準コミット: eaaab30bdafda034467f6d54d2886cd13d282f99
- 実装ブランチ: chatgpt/muse-runtime-consistency-20261121
- PR: 作成後追記
- マージ: 未実施、Museレビュー待ち

## 実装

force_eject時に登録済みレジへ通知し、担当者と待機割当を即時解放。cancel_customerはCHECKOUT_CANCELLED状態とsettlement_blockedを持続し、refreshだけで復帰させない。明示resume_checkoutだけが通常の接近経路へ戻せる。これらは参照ハーネスの技術的状態で、PS由来の追加ルールとはしない。

完了処理・セルフ精算・低層purchases.settleへ防御を追加し、古い時間完了通知でも強制退店客を精算しない。罰金・返金・商品返却等は追加しない。回帰4件を追加した。

Godot本体にも相当不具合を確認。try_eject_customerがphaseだけ変更して原状態3/旧目標を残し、次のnative更新で会計できた。既存ProgramPeople.change_state(customer,5)へ接続し、原退店経路へ遷移。nativeレジ担当者は人物ごとの割当モデルではないためPythonのIDLEを機械的に移植していない。新しいejection_consistency_smokeでは会計直前退店、未払い保持、現金/売上不変、JSON再開と乱数/位置一致、退出完了を確認。CI対象へ追加。

## 完了条件・逸脱

逸脱なし。対象回帰とAndroidビルド完了。広域headlessに残る別の構成欠落をCSRM-002へ分離。実機動作/実聴は未確認。Museレビュー待ち。
