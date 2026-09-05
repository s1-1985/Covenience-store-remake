# V03 August/September runtime observations — 2026-09-06

Source video: `【作業用BGM】ザ・コンビニ 1時間【プレイ動画】_HD_60fps.mp4` (V03, 1280x720, ~59.94 fps).

Scope in this pass: approximately video 00:18:00–00:33:20. Original frames are not stored in this repository.

## Evidence labels

- `CONFIRMED_VISUAL`: directly readable in the supplied gameplay footage.
- `REPEATED_VISUAL`: same numeric/behavioral observation independently repeated in supplied footage.
- `INFERENCE`: arithmetic/context interpretation only; not a directly labelled game rule.

## 1. Normal day rollover: Aug 2 -> Aug 3

Around video `00:22:16–00:22:21`:

- 1Y Aug 2 23:58: cash `¥8,782,130`; lower-right store amount `¥125,720`.
- 1Y Aug 3 00:00: cash is still `¥8,782,130`; lower-right amount resets to `¥0`.
- 1Y Aug 3 00:02: cash becomes `¥8,687,786`.
- Difference: exactly `-¥94,344` after the date boundary.
- This matches the earlier Jul 1 -> Jul 2 and Jul 2 -> Jul 3 `-¥94,344` observations, so the same post-midnight debit is now independently visible on three ordinary transitions.

Evidence: `REPEATED_VISUAL` for the `-¥94,344` ordinary-rollover sample; the expense composition remains unknown.

The same 00:02 frame displays a town-growth notice: `援助の甲斐あって 住宅が建ちました` (wording visually read; use as event meaning rather than a formula). Weather is shown as clear after the boundary.

Evidence: `CONFIRMED_VISUAL`.

## 2. Representative day 4 seasonal notice

Around video `00:25:20+`, at 1Y Aug 4 00:00, a mikoshi-style notification appears:

`今日は夜にお祭りがあります。`

The clock remains at `00:00` for multiple real/video seconds while this notification stays open. This is another notification type that pauses in-game time. It should not be generalized to every notification because the previously observed store-rank notification continued advancing the game clock.

Evidence: `CONFIRMED_VISUAL`.

## 3. Aug -> Sep month rollover and monthly report

Around video `00:29:00–00:29:10`:

- Aug 4 23:58 / Sep 1 00:00 boundary cash: `¥8,722,462`.
- Sep 1 00:02 cash: `¥7,895,456`.
- Visible boundary-to-post-boundary difference: `-¥827,006`.
- Do **not** equate this visible cash delta directly with the monthly report's `収支`; the report value below differs.

Evidence: `CONFIRMED_VISUAL` for both balances; interpretation unresolved.

At Sep 1 00:02, notification for Mammy Mart 2nd store:

`前月の売り上げが 300万円を越えました`

This confirms a store-level previous-month-sales milestone at 3,000,000 yen.

Evidence: `CONFIRMED_VISUAL`.

The following monthly report shows:

| item | previous month | vs. month before |
|---|---:|---:|
| 収支 | `-¥837,328` | `+¥572,480` |
| 他経費 | `¥500,000` | `¥0` |
| 町人口 | `2,338人` | `+76人` |

Arithmetic cross-check against the immediately prior recorded report:

- `-837,328 - (-1,409,808) = +572,480`
- `500,000 - 500,000 = 0`
- `2,338 - 2,262 = +76`

This is a third consecutive monthly-report sample consistent with the displayed comparison column being a direct arithmetic difference from the preceding report for these fields.

Evidence: `CONFIRMED_VISUAL` for displayed values; `REPEATED_VISUAL` for the arithmetic-difference behavior.

## 4. Store comparison screen reveals operational metrics

Around video `00:33:16`, game time 1Y Sep 2 09:50, a two-store comparison table is directly readable.

Column labels after the yen amount are:

- `人気`
- `清掃`
- `警備`
- `サービス`

Rows:

| store | yen amount | 人気 | 清掃 | 警備 | サービス |
|---|---:|---:|---:|---:|---:|
| 本店 | `¥10,900` | 42 | 99 | 82 | 59 |
| 2号店 | `¥37,560` | 37 | 100 | 100 | 68 |

Evidence: `CONFIRMED_VISUAL`.

The yen amount for the currently viewed main store matches the lower-right in-store accumulating yen display (`¥10,900`) at the same period. This strongly suggests that the first yen column and the lower-right store amount are the same per-store running monetary metric, likely same-day sales, but the footage does not expose a direct header for that yen column in this frame. Keep the semantic label unresolved until another screen names it explicitly.

Evidence: `INFERENCE` for meaning; exact numeric equality is visual.

## 5. Direct-mail promotion notice

Around video `00:33:20`, the map displays:

`マミーマート
ダイレクトメールで
宣伝活動をおこないました`

This directly confirms direct mail as one promotion method for the player store. Nearby cash changes cannot yet be used as a clean cost measurement because sales/time also advance around the action.

Evidence: `CONFIRMED_VISUAL`.

## Implementation implications

1. Keep ordinary post-midnight debits as an evidence series, not a universal fixed expense. Three ordinary samples now match `¥94,344`, while the previously recorded day-3 -> day-4 transition differed.
2. Notifications need a per-event pause policy; do not model a single global `modal_pauses_time` rule.
3. Add store runtime/display fields for popularity, cleaning, security and service independently per branch/store.
4. Add store-level monthly-sales milestone triggers; `3,000,000 yen` is now a direct visual threshold sample.
5. Monthly report comparison values can be tested as direct previous-report differences for `収支`, `他経費`, and `町人口`; three consecutive samples now line up arithmetically.

## Next video targets

Continue after approximately `00:33:20` and prioritize:

- direct labels for the first yen column / lower-right yen display;
- additional store comparison snapshots to measure popularity decay and cleaning/security/service changes;
- direct-mail and other promotion costs in isolated no-sale windows;
- checkout timing under visible staff identity/skill context;
- day-4 festival evening traffic and any event-driven customer spike;
- next ordinary and month rollover to expand the debit/report sample set.
