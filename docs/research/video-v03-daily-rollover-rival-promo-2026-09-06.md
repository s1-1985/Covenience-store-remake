# V03 daily rollover and rival-promotion observations — 2026-09-06

Scope: user-supplied first-title gameplay video `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4` (V03). This note records direct visual observations only and does not store original game frames.

## Coverage in this pass

- `00:05:10–00:11:50`: coarse scan at 5-second resolution.
- `00:06:53–00:06:59`: fine scan at 0.5-second resolution around a rival promotion modal.
- `00:07:34–00:07:42`: fine scan at 0.5-second resolution around July day 1 → day 2 rollover.
- `00:10:46–00:10:52`: fine scan at 0.5-second resolution around July day 2 → day 3 rollover.

Evidence level for all direct values below: `CONFIRMED_VISUAL` unless explicitly marked as inference.

## Rival store promotion event

Around video `00:06:53–00:06:58`, during in-game `01年目07月01日 [快晴]`, a modal appears with the message:

- `ライバル店が 宣伝活動をおこなっています`

Fine samples show the modal while the displayed game clock remains in the `19:02–19:30` range despite several seconds of video elapsing; after the modal disappears the game resumes at about `19:34`.

This confirms a rival-store advertising/promotion event and strengthens the already-observed rule that modal notifications pause normal game-time progression.

The exact rival promotion type, cost, duration and numerical effect remain unknown.

## Ordinary day rollover: July day 1 → day 2

Fine samples around video `00:07:34–00:07:42`:

| Approx. video time | In-game date/time | Weather | Cash | Bottom-right store value |
|---|---|---|---:|---:|
| 00:07:38.0 | 01年目07月01日 23:52 | 快晴 | 11,211,322 | 84,900 |
| 00:07:38.5 | 01年目07月01日 23:56 | 快晴 | 11,211,322 | 84,900 |
| 00:07:39.0 | 01年目07月02日 00:00 | 快晴 | 11,211,322 | 0 |
| 00:07:39.5 | 01年目07月02日 00:04 | 曇 | 11,116,978 | 0 |

Directly observed consequences:

1. The representative day changes from `01日` to `02日` at `00:00` without a month-summary popup.
2. The bottom-right yen value resets from `84,900` to `0` exactly at the date rollover.
3. Cash is unchanged at the `00:00` frame, then becomes `11,116,978` by `00:04`.
4. The resulting visible debit is `94,344 yen`.
5. Weather also changes from `快晴` to `曇` immediately after midnight.

## Ordinary day rollover: July day 2 → day 3

Fine samples around video `00:10:46–00:10:52`:

| Approx. video time | In-game date/time | Weather | Cash | Bottom-right store value |
|---|---|---|---:|---:|
| 00:10:47.5 | 01年目07月02日 23:56 | 曇 | 10,663,328 | 80,510 |
| 00:10:48.0 | 01年目07月03日 00:00 | 曇 | 10,663,328 | 0 |
| 00:10:48.5 | 01年目07月03日 00:02 | 曇 | 10,568,984 | 0 |

Directly observed consequences:

1. The bottom-right yen value again resets to `0` at `00:00`.
2. Cash again remains unchanged at the exact `00:00` frame and is debited immediately afterward.
3. The debit is again exactly `94,344 yen` (`10,663,328 - 10,568,984`).

## Repeated daily-debit anchor

Two independent ordinary day rollovers in the same month show the same post-midnight cash debit:

- July day 1 → day 2: `94,344 yen`
- July day 2 → day 3: `94,344 yen`

This is now a repeated numeric observation, not a one-off. However, it is **not yet safe to label the 94,344 yen as one specific cost category**. It may be a composite daily operating charge (maintenance, labor, rent/other fixed costs, etc.). The component formula remains unresolved until menus/reports expose the corresponding daily cost breakdown or another layout/staff configuration provides a differing comparison value.

Evidence: `CONFIRMED_VISUAL` for both debits; interpretation as a composite daily operating charge is `STRONG_INFERENCE` only.

## Bottom-right yen field behavior

Across both ordinary day transitions, the bottom-right store yen field grows during the day and resets to `0` exactly at midnight:

- July day 1 pre-midnight: `84,900` → midnight `0`
- July day 2 pre-midnight: `80,510` → midnight `0`

This strongly suggests a per-day accumulating store metric, plausibly daily sales/revenue, but the UI label has not yet been directly recovered. Keep the field semantically unnamed in executable data until the label is visually confirmed.

Evidence: reset behavior `CONFIRMED_VISUAL`; sales/revenue interpretation `STRONG_INFERENCE`.

## New research implications

- Normal representative-day rollover (`01→02`, `02→03`) is visually different from the previously recovered `04→next-month 01` transition: ordinary rollover has no month-summary popup.
- The exact post-midnight debit occurs after the `00:00` state, not atomically in the same visible frame.
- Weather can refresh immediately after midnight independently of the date-change frame.
- Rival stores can trigger explicit advertising-activity notification events during normal operation.
- Modal notifications visibly suspend the live game clock.

## Still unresolved / next targets

1. Repeat the day 3 → day 4 rollover and compare whether the same `94,344 yen` debit occurs.
2. Find another store configuration/month where the debit differs, then correlate difference with staff/fixture maintenance values.
3. Recover the direct UI label for the bottom-right yen field.
4. Fine-scan high-traffic windows in this covered range for identifiable entry, queue-start, checkout-start and checkout-end events.
5. Continue from `00:11:50+`, prioritizing new menus/events and additional day/month transitions.
