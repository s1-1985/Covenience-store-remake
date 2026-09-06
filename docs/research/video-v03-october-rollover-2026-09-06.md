# V03 September-to-October rollover observations — 2026-09-06

Source: user-supplied first-title gameplay video `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4` (V03).

Scope in this pass:

- coarse scan: `00:43:20–00:53:20` at 10-second intervals;
- Sep day 4 → Oct day 1: `00:43:42–00:44:02` at 0.5-second intervals plus scene-change review;
- Oct day 1 → day 2: `00:46:42–00:46:56` at 0.5-second intervals;
- Oct day 2 → day 3: `00:50:36–00:50:54` at 0.5-second intervals.

Original video frames are not stored in this repository. Direct values below are `CONFIRMED_VISUAL`; arithmetic and generalization are labelled separately.

## 1. September day 4 rolls into October day 1

Boundary frames show:

| video time | in-game date/time | weather | cash | bottom-right yen field | visible state |
|---|---|---|---:|---:|---|
| about `00:43:48.0` | 1Y Sep 4 23:58 | 晴れ | `¥1,678,659` | `¥162,650` | normal store view |
| about `00:43:49.0` | 1Y Oct 1 00:02 | 雨 | `¥806,328` | `¥0` | store-rank notification |

The visible cash difference across the sampled boundary is `-¥872,331`. This must not be equated directly with the monthly `収支` value below: the footage does not expose the hidden settlement components between the two displayed states.

The bottom-right store yen field resets to zero at the month boundary, consistent with earlier day and month transitions.

## 2. October notifications and monthly report

### Store rank

At about `00:43:49.0`, the notification reads:

`マミーマート2号店 店のランクが ★☆☆☆☆ になりました`

The in-game clock continues from 00:02 through at least 00:22 while this notification remains visible. This is another direct example of a notification type that does not pause live time.

### Monthly-sales threshold

At about `00:43:53.5`, the next notification reads:

`マミーマート2号店 前月の売り上げが 400万円を越えました`

This confirms a branch-specific monthly-sales threshold event at `¥4,000,000`, extending the previously observed `¥3,000,000` threshold event. The footage does not establish whether thresholds are cumulative milestones, mutually exclusive tiers, or whether all crossed tiers are emitted.

### September report shown in October

At about `00:43:57.3`, the monthly report shows:

| field | previous month | comparison shown |
|---|---:|---:|
| 収支 | `-¥889,128` | `-¥51,800` |
| 他経費 | `¥6,200,000` | `+¥5,700,000` |
| 町人口 | `2,401人` | `+63人` |

The arithmetic comparisons match the August report already recorded in `video-v03-aug-sep-runtime-2026-09-06.md`:

- `-889,128 - (-837,328) = -51,800`;
- `6,200,000 - 500,000 = +5,700,000`;
- `2,401 - 2,338 = +63`.

This independently reinforces that the report's comparison column is an arithmetic delta from the preceding displayed month. It does not identify the composition of `収支` or `他経費`.

## 3. Two more ordinary daily rollover samples

### Oct day 1 → day 2

| in-game date/time | weather | cash | bottom-right yen field |
|---|---|---:|---:|
| Oct 1 23:58 | 雨 | `¥877,783` | `¥145,170` |
| Oct 2 00:00 | 雨 | `¥877,783` | `¥0` |
| Oct 2 00:06 | 快晴 | `¥783,439` | `¥0` |

The post-boundary debit is exactly `¥94,344`. Weather changes only after the 00:00 frame.

### Oct day 2 → day 3

| in-game date/time | weather | cash | bottom-right yen field |
|---|---|---:|---:|
| Oct 2 23:56 | 快晴 | `¥754,844` | `¥162,550` |
| Oct 3 00:00 | 快晴 | `¥754,844` | `¥0` |
| Oct 3 00:04 | 晴れ | `¥660,500` | `¥0` |

The post-boundary debit is again exactly `¥94,344`; weather again updates after the 00:00 frame.

Together with the five ordinary samples previously registered, seven ordinary transitions now show the same `¥94,344` debit. The July day 3 → day 4 counterexample remains, so the number is a repeated configuration/state anchor and must not be implemented as a universal daily constant.

## 4. UI/reference-frame candidates

No frames are committed. Metadata for later local reference extraction:

| video ID | timestamp | screen type | target | suggested crop | quality | duplicate | use | redraw features |
|---|---:|---|---|---|---|---|---|---|
| V03 | `00:43:49.0` | notification | 2号店 rank-up / manager portrait | beige dialog plus green portrait square and six-star row | medium-high; clean overlay | layout duplicate, text/state distinct | `reference` | parchment texture, dark lower shadow, red active star, black inactive stars |
| V03 | `00:43:53.5` | notification | 2号店 monthly sales over ¥4M | beige dialog plus portrait and three text lines | medium-high; clean overlay | same frame family, unique text | `reference` | same dialog geometry; threshold number centered on last line |
| V03 | `00:43:57.3` | monthly report | September report | full report panel only | medium; cursor overlaps comparison column | report-family duplicate, values distinct | `redraw-needed` | two-column headings, three metric rows, brown lower border/shadow |

V02 remains the preferred source for final UI and art reference because it has cleaner high-resolution menu coverage. These V03 candidates are evidence anchors and fallback redraw references.

## 5. Boundaries and next target

Safe conclusions:

- a `¥4,000,000` branch-month sales notification exists;
- a one-star store-rank notification can coexist with advancing game time;
- September's report values and comparison arithmetic are directly readable;
- two additional ordinary rollovers apply the same post-midnight `¥94,344` debit;
- weather can retain the prior value at 00:00 and update in the following displayed minutes.

Still unresolved:

- threshold-event tiering and whether multiple crossed thresholds queue;
- decomposition of monthly settlement and `他経費`;
- decomposition of the repeated `¥94,344` debit;
- why the July day 3 → day 4 sample differs;
- checkout duration and abandonment behavior in this crowded branch.

Next V03 target is `00:53:20–00:59:59.999`. V02 `00:00:00–00:10:00` remains higher priority as soon as its Library transfer recovers.
