# V03 October day 4 and bankruptcy observations — 2026-09-06

Source: user-supplied first-title gameplay video `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4` (V03).

Scope in this pass:

- coarse scan: `00:53:20–00:59:59.999` at 5-second intervals;
- Oct day 3 → day 4: `00:55:28–00:55:48` at 0.5-second intervals;
- Oct day 4 → Nov day 1 terminal boundary: `00:59:25–00:59:59.999` at 0.5-second intervals.

Original video frames are not stored in this repository. Direct values below are `CONFIRMED_VISUAL`; arithmetic and interpretation are labelled separately.

## 1. October day 3 → day 4 uses a multi-step cash sequence

| video time | in-game date/time | weather | cash | bottom-right yen field |
|---|---|---|---:|---:|
| about `00:55:32.0` | 1Y Oct 3 23:56 | 晴れ | `¥760,755` | `¥177,130` |
| about `00:55:33.0` | 1Y Oct 4 00:00 | 晴れ | `¥764,375` | `¥0` |
| about `00:55:33.5` | 1Y Oct 4 00:02 | 快晴 | `¥668,591` | `¥0` |
| about `00:55:34.0` | 1Y Oct 4 00:04 | 快晴 | `¥667,151` | `¥0` |
| about `00:55:35.0` | 1Y Oct 4 00:08 | 快晴 | `¥667,151` | `¥4,000` |

Direct arithmetic:

- cash rises by `¥3,620` between the sampled 23:56 and 00:00 frames;
- it then falls by `¥95,784` from 00:00 to 00:02;
- it falls by a further `¥1,440` by 00:04;
- the visible post-00:00 debit is therefore `¥97,224`.

The footage does not identify the components. The pre-boundary rise may include an ordinary checkout that completes across the boundary, but that is not proven and must not be encoded as a special rollover credit.

This is a second direct reason not to implement the repeatedly observed `¥94,344` as a universal constant. Day-4 processing can be multi-step and configuration-dependent. Weather again retains the previous state at exactly 00:00 and changes immediately afterward.

## 2. Negative cash at the month boundary triggers bankruptcy before a monthly report

| video time | in-game date/time | weather | cash | bottom-right yen field | visible state |
|---|---|---|---:|---:|---|
| about `00:59:40.0` | 1Y Oct 4 23:58 | 快晴 | `¥697,211` | `¥189,260` | normal store view |
| about `00:59:40.5` | 1Y Nov 1 00:00 | 快晴 | `-¥121,360` | cleared/hidden | `倒産してしまいました。` |
| about `00:59:41.0` onward | 1Y Nov 1 00:00 | 快晴 | `-¥121,360` | hidden | bankruptcy splash |

The visible cash difference is `-¥818,571`. The footage does not expose the settlement components, so this is an observed boundary delta, not a monthly-cost formula.

In this terminal case:

- the cash field is already negative on the first observed Nov 1 00:00 bankruptcy frame;
- the game shows `倒産してしまいました。` immediately;
- the usual monthly report and rank/sales notifications are not shown before the bankruptcy sequence in the remaining footage;
- a dedicated bankruptcy splash follows over the store view.

This supports an implementation boundary where month-start settlement can lead directly to a terminal bankruptcy state before ordinary month-start report/notification presentation. The exact comparison operator is unresolved because no zero-cash sample exists; implementers should not infer whether zero itself is bankrupt.

## 3. UI/reference-frame candidates

No frames are committed. Metadata for later local reference extraction:

| video ID | timestamp | screen type | target | suggested crop | quality | duplicate | use | redraw features |
|---|---:|---|---|---|---|---|---|---|
| V03 | `00:59:40.5` | terminal dialog | bankruptcy message | central beige message panel including dark lower/right shadow | high; clean text, store visible behind | dialog-frame family duplicate, terminal text unique | `reference` | narrow parchment rectangle, centered dark text, dark offset shadow |
| V03 | `00:59:41.0` | terminal splash | bankruptcy illustration | full centered splash rectangle | medium-high; no cursor overlap | unique | `redraw-needed` | cyan cloudy sky, distressed storefront, large red `倒産` lettering with white/dark outline |

V02 remains the preferred source for final artwork when its transfer recovers. These V03 frames are evidence anchors and redraw references.

## 4. Boundaries and next target

Safe conclusions:

- Oct day 3 → day 4 uses at least two visible post-midnight debits totaling `¥97,224`, not `¥94,344`;
- weather can update after the exact 00:00 frame;
- Nov 1 settlement produces visible negative cash and immediately enters bankruptcy;
- the terminal path suppresses or preempts the usual monthly report in this footage.

Still unresolved:

- the composition and ordering of day-4 and month-start costs;
- whether the `¥3,620` boundary increase is a checkout settlement;
- the precise bankruptcy comparison rule at exactly zero cash;
- whether a monthly report remains accessible after the terminal splash;
- checkout duration and abandonment behavior.

V03 is now fully coarse-scanned except for the two short ledger gaps `00:00:00–00:01:00` and `00:03:00–00:03:50`. V02 `00:00:00–00:10:00` remains the highest-priority next target as soon as transfer succeeds.
