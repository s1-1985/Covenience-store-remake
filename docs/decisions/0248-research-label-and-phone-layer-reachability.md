# 0248 — 調査ラベルの原作表記への一致と phone 層の到達可能性（CSRM-005）

## 背景
原作マニュアル p.10 の「調査」の子項目は 店舗別詳細・店舗別収支グラフ・全店収支グラフ・アンケート である（Muse 解析 docs/muse/analysis/2026-11-21-controller-manual.md、CONFIRMED_OFFICIAL）。現行の PS1 UI 層（game/scripts/ps1_ui.gd）は1箇所だけ「店舗別グラフ」と短縮していた。また旧 phone 層（phone_ui.gd）は 店舗・不動産 のトップレベル入口を欠き、調査画面を「店舗成績」と表示するが、出荷フローで到達可能かは未検証だった（同 2026-11-21-manual-ui-crosscheck.md）。

## 決定
- ps1_ui.gd の調査メニューのラベルを原作表記「店舗別収支グラフ」へ合わせる（1行の変更）。
- phone 層については、到達不可能であることを静的・動的の両面で確認したため、コード変更を行わない。到達不可能な表示文字列（「店舗成績」等）はそのまま残すが、今後 phone 層を再び有効化する場合は本決定の確認をやり直すこと。

## 到達可能性の確認根拠
静的確認:
- ゲーム画面の UI クラスは main.gd が preload する ps1_ui.gd のみ（PhoneUIScript）。phone_ui.gd のプレーンなインスタンス化は存在しない（main_menu.gd は make_theme() の静的利用のみ）。
- ps1_ui.gd の layout_screen() は毎回のレイアウトで phone 層の menu / hud / bottom_bar を隠し、コード全体に menu.show() 等で再表示する経路は存在しない。
- ps1_ui.gd の open_window() は "stock" / "town" 以外の ID では phone 側ウィンドウノードを画面外（-5000, -5000）・透明に退避し、自前の surface に描画する。調査の "shop" / "shop_graph" もこの経路で、phone 側の「店舗成績」ウィンドウは表示されない。open_window("shop") / open_window("town") の呼び出し元は存在しない。

動的確認（Godot 4.3 ローカル、`--android-preview` で出荷時 UI 経路を有効化して main シーンを起動）:
- UI インスタンスのスクリプトは res://scripts/ps1_ui.gd で、起動直後から menu / hud / bottom_bar は全て非表示。
- handle_command()（□相当）でメニューを開いても phone メニューは非表示のまま（screen=store）。
- open_window("research") / open_window("shop") のいずれでも phone ウィンドウは位置 (-5000, -5000)・modulate.a=0 の退避状態を維持した。

## 確認
- ラベル変更後に UI 関連 smoke（ps1_ui / ps1_menu_dispatch / ps1_touch_audit / menu_usability）と全体 headless_smoke を実行し、悪化が無いことを確認する（結果は実装報告に記録）。
- APK は作成していない。実機確認は行っていない。
