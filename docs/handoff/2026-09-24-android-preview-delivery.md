# Android Japanese preview delivery

Based on main 0e4a42e (includes top HUD and original floor/wall changes).
See decision 0154. Package com.conveniremake.preview, version 0.1.1-preview.

The client remains a vertical slice. Original scenarios and full opening/multi-store
flows are incomplete. Do not call this a complete recreation. Android uses a
200-million-yen beginner cash anchor with a free furnished test shop; the latter
is REMAKE_BALANCED_DEFAULT. Existing regression config remains at 1000 yen.

Japanese text: game/locale/ja.po. Bundled font subset: game/fonts/ConveniJP.ttf;
regenerate when adding glyphs. Android scene flow test:
`godot --headless --path game --script res://scripts/android_preview_smoke.gd -- --android-preview`
Use an isolated XDG_DATA_HOME. Desktop source tests remain English by default.
No binary app or signing key is committed. Source is proposed in a draft PR;
main must not be merged without user instruction. Actual phone installation
still needs the user's device.
