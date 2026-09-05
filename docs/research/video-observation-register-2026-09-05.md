# Uploaded gameplay video observation register — 2026-09-05

Scope: first-title gameplay footage supplied directly by the user. This file stores factual observations and measurement targets only; it does not embed copyrighted video frames.

## Video sources currently available

1. `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4`
   - approximately 1 hour
   - 1280x720 / ~59.94 fps
   - continuous store operation useful for runtime timing measurements

2. `ザ・コンビニ ～あの町を独占せよ～ コンソールアーカイブス [PS5]_HD(1).mp4`
   - approximately 1h33m36s
   - 1280x720 / 30 fps
   - high-resolution menus and fixture values

3. `【レトロゲーム】ザ・コンビニ  さくさくクリア目指すプレイ.mp4`
   - approximately 1h41m45s
   - 640x360 / 30 fps
   - long-run progression from year 1 into later years

## Direct visual values already recovered

### Copy machines

- Copy machine A
  - capacity: 20
  - attention: 10
  - purchase price: 1,500 yen
  - maintenance: 1,200 yen/day

- Copy machine B
  - capacity: 40
  - attention: 15
  - purchase price: 2,000 yen
  - maintenance: 1,440 yen/day

Evidence: `CONFIRMED_VISUAL` from the high-resolution PS5/current-play footage.

### Town inducement aid

Previously recovered:

- police box: 400,000 yen
- company: 5,400,000 yen
- vocational school: 4,800,000 yen
- university: 9,800,000 yen

Additional V03 direct-menu observations around video 00:02:34–00:02:48, in-game `01年目06月04日 [曇] 16:10`:

- police box (交番): 400,000 yen
- apartment building (マンション): 4,200,000 yen
- event venue (イベント会場): 6,000,000 yen
- sports ground (運動場): 2,000,000 yen
- junior high school (中学校): 5,000,000 yen
- amusement park (遊園地): 9,800,000 yen
- kindergarten (幼稚園): 1,200,000 yen

The menu is paused at 16:10 while the cursor moves among facilities. Placement feedback visibly distinguishes `誘致可能` and `誘致不可能` depending on the selected map tile.

Evidence: `CONFIRMED_VISUAL` from V03.

### Staff runtime observation

A later-year staff screen shows Nagasawa Tatsuya (長沢達也), age 36, with runtime values:

- stamina 85
- education 80
- register 75
- replenishment 65
- security 69
- cleaning 62
- service 75

This is a later-game runtime snapshot, **not an initial staff-master row**. It must be used only as a growth/runtime observation anchor until the initial value and elapsed work history are known.

### Local in-game time progression observation

One continuous section of the one-hour video yields successive samples around:

- 13:16
- 13:24
- 13:32
- 13:40

at roughly one-video-second intervals.

This is a local measurement only. It must not be converted into a universal `1 video second = 8 game minutes` engine constant until speed mode, menus and capture conditions are isolated.

### V03 early continuous-operation samples

Coarse observations from the first five minutes of V03 establish that the game clock advances rapidly during live store operation and stops while town menus are open. Selected samples:

| Video time | In-game date/time | Weather | Cash shown | Bottom-right store value | Notes |
|---|---|---|---:|---:|---|
| 00:01:00 | 01年目06月04日 04:46 | 曇 | 21,086,268 | 0 | store view |
| 00:01:10 | 01年目06月04日 06:24 | 曇 | 21,087,268 | 0 | store view |
| 00:01:20 | 01年目06月04日 07:44 | 曇 | 21,100,268 | — | store view |
| 00:01:30 | 01年目06月04日 09:08 | 曇 | 21,094,668 | 1,200 | store view |
| 00:01:40 | 01年目06月04日 10:40 | 曇 | 21,095,288 | 1,820 | store view |
| 00:01:50 | 01年目06月04日 11:54 | 曇 | 21,107,658 | 2,640 | store view |
| 00:02:00 | 01年目06月04日 13:16 | 曇 | 21,114,898 | 3,890 | store view |
| 00:02:10 | 01年目06月04日 14:32 | 曇 | 21,121,943 | 3,890 | store view |
| 00:02:20 | 01年目06月04日 15:38 | 曇 | 21,120,208 | 3,890 | store view |
| 00:02:30 | 01年目06月04日 16:10 | 曇 | 21,120,308 | — | town menu opened; clock remains 16:10 while navigating inducement UI |

These are observations only; the bottom-right yen figure is intentionally left without a semantic label until the UI meaning is independently verified.

### V03 day-4 to next-month transition

The June day-4 to July day-1 transition is directly visible in V03 around video 00:04:23–00:04:30.

- At approximately video `00:04:24.5`, in-game time is `01年目06月04日 [曇] 23:58`, cash `13,005,668`.
- At approximately video `00:04:25.0`, the display rolls to `01年目07月01日 [曇] 00:00`, cash remains `13,005,668`, and the bottom-right store value has reset to `0`.
- Within the next displayed minutes, weather becomes `[快晴]` and cash becomes `11,142,592`.
- A month summary overlay appears from about video `00:04:25.5` through `00:04:28.5`, showing:
  - 前月 `収支 -¥2,021,408`
  - 前々月比 `-¥914,616`
  - 前月 `他経費 ¥8,200,000`
  - 前々月比 `+¥8,100,000`
  - 前月 `町人口 2,106人`
  - 前々月比 `+120人`

The visible cash decrease from 13,005,668 to 11,142,592 is 1,863,076 yen, which is **not equal** to the displayed previous-month balance of -2,021,408 yen. Therefore no direct equation between the overlay balance and instantaneous cash should be assumed yet.

Evidence: `CONFIRMED_VISUAL` from V03.

### Store-specific customer-count milestone

At approximately video `00:04:50`, in-game `01年目07月01日 [快晴] 04:28`, a modal message appears:

- `マミーマート2号店 1000人目のお客さんがきました`

This confirms at least one store-specific cumulative customer milestone event at 1,000 customers. The reward/penalty effect, if any, is not established by this single observation.

Evidence: `CONFIRMED_VISUAL` from V03.

## V03 coverage ledger added 2026-09-06

- `00:01:00–00:03:00`: scanned at 10-second resolution; `00:02:30–00:03:00` additionally sampled at 2-second resolution around town inducement UI.
- `00:03:50–00:05:10`: scanned at 5-second resolution; `00:04:23–00:04:30` additionally sampled at 0.5-second resolution around month rollover.
- `00:00:00–00:01:00`, `00:03:00–00:03:50`, and `00:05:10+` remain priority unscanned/under-scanned ranges.

## High-priority measurements still to extract

1. checkout service duration by identifiable staff/register context
2. customer arrivals per in-game time window
3. staff stamina before/after repeated checkout/replenish/clean work
4. customer checkout patience / abandonment timing
5. replenishment and cleaning action durations
6. additional day-4 to month-end transitions with sales/cost figures visible, to test whether the observed rollover sequence repeats

Measurement rule: one isolated occurrence is an observation; repeated independent occurrences are required before promoting a numeric rule into the executable baseline.
