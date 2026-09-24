# 0154: Japanese Android playable preview

## Background

User requested a first-title recreation installable/playable on Android. The
existing client can export to APK but is a vertical slice with English menus,
small buttons and a 1,000-yen regression-test budget. This change builds on
main 0e4a42e, retaining tasks 82/83's top HUD and video-derived floor/wall sprites.

## Changes

- Japanese gettext UI, including formatted messages and displayed catalog names.
  IDs and save data remain unchanged. A small number of diagnostic IDs/logs are
  still English; this is not a claim of complete localization.
- Bundled Noto Sans JP font from google/fonts ofl/notosansjp, weight instantiated
  at 400 and subset with fontTools to current UI/data plus ASCII/kana/full-width
  characters. SIL OFL included; add glyphs when extending user-facing text.
- Android-only larger text/buttons, section shortcuts, quick save, landscape.
- Separate package com.conveniremake.preview, version 0.1.1-preview/code 2,
  avoids signature conflicts with the prior com.conveniremake.app debug build.
- Android preview cash uses the researched beginner anchor of 200,000,000 yen
  (ui-consistency-audit-2026-09-05.md). The furnished shop remains granted for
  free: REMAKE_BALANCED_DEFAULT, disclosed in config/code/test. This is not the
  original full beginner setup. Regression config retains 1,000 yen.

## Validation

- Python: 746 tests, 745 pass and one pre-existing expected failure.
- Godot 4.3 headless smoke: pass (1240 steps).
- Real-scene flow with --android-preview: Japanese catalog/font, New Game,
  funded start, calendar, customer sale, shortcuts, quick save, load, town,
  title and Continue. Run in a separate XDG_DATA_HOME to protect user saves.
- Rendered with Godot on a virtual display. APK signing/data checks occur in
  delivery. No Android device is connected; hardware behavior is unverified.

## Limits

A development playtest, not a complete recreation: original scenarios, full
opening flow, full multi-store geography and many mechanics remain unfinished.
Do not publish APKs or signing keys to this public source repository. New debug
key is retained privately alongside the user's delivery for future updates.
