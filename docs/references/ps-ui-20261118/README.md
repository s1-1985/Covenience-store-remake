# PS UI reference implementation — 2026-11-18 JST

The owner's 26 screenshots are the visual specification (`manifest.json`). They supersede the phone UI's invented permanent command column and bottom status band. Existing PS data analysis is reused; this is implementation, not another analysis batch.

`game/scripts/ps1_ui.gd` extends the existing phone service layer. Its 320×240 coordinate space is scaled exactly three times inside the existing 1280×720 viewport, with the game at x160..1120. Rails, direct taps, panning/pinching, and 1/2/4/8 speed remain native Android adaptations.

Implemented: town dropdown hierarchy; store status/commands at right; interior placement, move, swap and sell modes; 5×3 fixture picker; hours, prices and permits; 5 advertising icons; 5×2 facility selector; hiring, dismissal and transfer portraits/stat bars; six shop variants in two rows; store details, graphs and two-column survey; system settings; temporary closing confirmation; location prompt and native store-variant purchase picker.

UI graphics use original PSMOJI0/1, KYOU, CASE_T00, KAO01/02 and SHOPTYP1 TIM pixels. Font advances are 8 for ASCII and 12 for Japanese. HUD strip coloring is adapted to the supplied beige reference (the decoded source strip is blue). Window placement and rows are CONFIRMED_VISUAL measurements; paper edges and external touch hit areas are adaptations. The atlas data is 121 KB before import. `tools/ps1/export_native_ui.py SOURCE.zip` regenerates the textures from the already preserved archive. There is no PS executable/BIOS/emulator runtime dependency.

Profile names/portrait indices/sex and fixture capacity/attention/hourly upkeep reuse existing source-data work on the analysis branch (20261114-staff-roster-growth-data, 20261114-interior-transactions-data, and 20261117 UI/HUD/portrait/texture-runtime-binding directories). The fixture first page follows the supplied screenshot: kinds 35,36,22,23,24 and then shelf sizes.

Settings and all enabled operations call the real simulation/save/audio handlers. Displayed counts and money are live; screenshot sample values are never baked in. Dismissal/transfer daily wage uses scheduled hours; hiring shows the 24-hour base.

## Verification and limits

One rendered Godot smoke covers 25 referenced screen states plus actual location confirmation/store purchase, SE OFF/ON hotspots, move mode, cancel and START. Previous staff-response regression also passes. Source-scene startup and Android export are checked. No Android device was available.

This does not claim a complete restoration of every original screen or mechanic. Branch-store sale remains unavailable (explicit UI message); store monthly graph has previous-month and current-month store totals because the backend does not retain full per-store monthly history. Individual prices and unreferenced stock/notification/acquisition details still include native adaptation. Hire experience text distinguishes free candidates from employed profiles; lifetime experience is not tracked by the existing backend. Main-menu/title and original input state machine are not reconstructed by these screenshots. Existing gameplay/simulation limitations remain.

The rendered test exits successfully but Godot reports an ObjectDB/two-resource cleanup warning on exit; no in-game script errors were observed. Do not call that device testing or pixel-perfect reproduction.
