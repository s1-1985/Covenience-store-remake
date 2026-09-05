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

- police box: 400,000 yen
- company: 5,400,000 yen
- vocational school: 4,800,000 yen
- university: 9,800,000 yen

Evidence: `CONFIRMED_VISUAL` from the long-run gameplay footage.

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

## High-priority measurements still to extract

1. checkout service duration by identifiable staff/register context
2. customer arrivals per in-game time window
3. staff stamina before/after repeated checkout/replenish/clean work
4. customer checkout patience / abandonment timing
5. replenishment and cleaning action durations
6. day-4 to month-end transitions with sales/cost figures visible

Measurement rule: one isolated occurrence is an observation; repeated independent occurrences are required before promoting a numeric rule into the executable baseline.
