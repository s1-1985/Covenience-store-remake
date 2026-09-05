# V03 day-4 rollover and July month-end observations — 2026-09-06

Scope: user-supplied first-title gameplay video `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4` (V03). Direct visual observations only; no original frames are stored.

## Coverage in this pass

- coarse scan: `00:11:50–00:18:00`
- fine scan: `00:13:32.00–00:13:35.75` around July day 3 → day 4
- fine scan: `00:16:30.00–00:16:46.50` around July day 4 → August day 1 / month-end UI

Evidence level for direct values below: `CONFIRMED_VISUAL` unless marked otherwise.

## July day 3 → day 4 rollover does not repeat the earlier 94,344-yen pattern exactly

Fine samples:

| Video time | In-game date/time | Weather | Cash | Bottom-right yen field |
|---|---|---|---:|---:|
| ~00:13:32.50 | 01年目07月03日 23:52 | 曇 | 10,628,434 | 98,240 |
| ~00:13:33.00 | 01年目07月03日 23:54 | 曇 | 10,628,434 | 98,240 |
| ~00:13:33.50 | 01年目07月03日 23:58 | 曇 | 10,631,634 | 101,440 |
| ~00:13:34.00 | 01年目07月04日 00:00 | 曇 | 10,629,834 | 0 |
| ~00:13:34.50 | 01年目07月04日 00:04 | 雨 | 10,534,590 | 0 |

Consequences:

1. The bottom-right yen field again resets to zero at exactly `00:00`.
2. A `+3,200 yen` cash increase occurs before midnight together with the bottom-right field increasing from `98,240` to `101,440`; this is consistent with a store transaction but the field label is still not directly confirmed.
3. Unlike the two previous ordinary rollovers, cash is already `1,800 yen` lower at the exact `00:00` frame (`10,631,634 → 10,629,834`).
4. A further `95,244 yen` debit is visible by `00:04` (`10,629,834 → 10,534,590`).
5. Total visible cash reduction from the last pre-midnight sample to `00:04` is therefore `97,044 yen`.
6. The earlier repeated `94,344 yen` post-midnight debit is **not a universal fixed daily constant** under the observed state. Its components remain unresolved.
7. Weather again changes immediately after midnight, this time `曇 → 雨`, strengthening the observation that weather refresh can occur just after the date-change frame rather than atomically at `00:00`.

The cause of the extra `1,800 yen` and the `+900 yen` increase in the post-midnight debit relative to the prior two days is unknown. Do not label either as wages, maintenance, procurement, or rent without a matching breakdown.

## July day 4 → August day 1 month-end transition

Fine samples:

| Video time | In-game date/time | Cash | Bottom-right yen field | Visible UI |
|---|---|---:|---:|---|
| ~00:16:31.5 | 01年目07月04日 23:58 | 10,560,710 | 70,160 | normal store view |
| ~00:16:32.0 | 01年目08月01日 00:02 | 9,232,784 | 0 | store-rank notification |
| ~00:16:36.5 onward | 01年目08月01日 ~00:32+ | ~9.23M | 3,000+ | monthly report notification |

Direct observations:

- Month rollover changes representative day `04 → 01` and month `07 → 08`.
- The bottom-right yen field resets from `70,160` to `0` across month rollover, matching ordinary-day reset behavior.
- Cash falls from `10,560,710` at July 4 23:58 to `9,232,784` by August 1 00:02, a visible difference of `1,327,926 yen`. This must not yet be equated directly to the monthly report's `収支` value because other event ordering/components may be involved.

## Store-rank notification

Immediately after the month rollover a notification appears:

- `マミーマート 本店`
- `店のランクが`
- `★☆☆☆☆になりました` (one filled/red star visually followed by four unfilled stars)

This confirms at least a five-step/star presentation for store rank and an explicit rank-change notification at month boundary in this run.

Important timing observation: while this rank notification remains visible, the displayed game clock continues advancing (`00:02 → 00:06 → 00:10 → ...`). Therefore **not every notification freezes game time**. This narrows the earlier observation: the rival-promotion modal was observed pausing time, but notification behavior is message/UI-type dependent.

## July monthly report values

A subsequent report panel directly shows:

| Field | 前月 | 前々月比 |
|---|---:|---:|
| 収支 | -1,409,808 yen | +611,600 yen |
| 他経費 | 500,000 yen | -7,700,000 yen |
| 町人口 | 2,262人 | +156人 |

Cross-check against the prior June report already recovered from V03:

- previous `収支`: `-2,021,408` → July `-1,409,808`; arithmetic difference is exactly `+611,600`.
- previous `他経費`: `8,200,000` → July `500,000`; arithmetic difference is exactly `-7,700,000`.
- previous `町人口`: `2,106` → July `2,262`; arithmetic difference is exactly `+156`.

This validates that the displayed `前々月比` column is an actual arithmetic delta versus the previously displayed month for these three fields in the observed run.

## Implementation implications

- Do not hard-code `94,344 yen/day`; third ordinary rollover disproves universality under the same visible store.
- Model midnight processing as potentially ordered sub-events rather than one atomic debit until components are recovered.
- Keep weather refresh as a post-date-change event candidate.
- Store rank should be represented separately from store name and can emit a month-boundary notification.
- Notification windows require type-specific pause policy; `rival promotion` and `rank change/month report` do not share one universal time-freeze behavior in the observed footage.
- Monthly report `前々月比` is now directly validated as an arithmetic delta for `収支`, `他経費`, and `町人口` in consecutive reports.

## Next targets

1. Find the cost breakdown explaining `94,344`, `95,244`, and the exact-midnight `1,800` event.
2. Locate a direct label for the bottom-right yen field.
3. Fine-scan `00:18:00+` for additional menus, staff stats, checkout timing, and later month/day transitions.
4. Capture another store-rank change to identify the exact trigger and whether rank updates only at month boundaries.
5. Continue collecting monthly reports to test whether `前々月比` arithmetic remains exact across more months.
