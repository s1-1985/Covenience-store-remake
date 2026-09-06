# V03 Sep day-2 promotion, inducement and rollover observations — 2026-09-06

Source: user-supplied first-title gameplay video `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4` (V03).

Scope in this pass:

- coarse scan: `00:33:20–00:43:20` at 10-second intervals;
- direct-mail boundary: `00:33:08–00:33:24` at 0.5-second intervals;
- inducement menus: `00:33:20–00:35:02` at 1-second intervals;
- Sep 2 → 3 and Sep 3 → 4 rollovers: fine scans around `00:36:50` and `00:39:40`.

Original video frames are not stored in this repository. Direct values below are `CONFIRMED_VISUAL`; arithmetic/generalization is labelled separately.

## 1. Direct mail is charged when the scheduled event fires

The promotion-selection screen at about `00:33:08`, 1Y Sep 2 09:38, shows only direct mail selected:

- `ダイレクトメール ¥100,000/月`
- `費用合計 ¥100,000/月`
- cash `¥7,429,372`

Returning to live time does not immediately subtract the fee. A store transaction then changes cash to `¥7,430,572` by 09:54. Boundary frames show:

| In-game time | cash | visible state |
|---|---:|---|
| Sep 2 10:00 | `¥7,430,572` | normal map |
| Sep 2 10:02 | `¥7,330,572` | `ダイレクトメールで宣伝活動をおこないました` |

The event-boundary difference is exactly `-¥100,000`. For direct mail in this observed run, payment is therefore at the fixed day-2 10:00 event, not at selection time.

Store comparison screens immediately before and after the event show:

| store | time | yen field | 人気 | 清掃 | 警備 | サービス |
|---|---|---:|---:|---:|---:|---:|
| 本店 | 09:52 | `¥10,900` | 42 | 99 | 82 | 59 |
| 2号店 | 09:52 | `¥37,560` | 37 | 100 | 100 | 68 |
| 本店 | 10:24 | `¥10,900` | 54 | 99 | 82 | 59 |
| 2号店 | 10:24 | `¥38,760` | 49 | 100 | 100 | 68 |

Popularity rises by exactly 12 at both owned stores. The other three displayed ratings do not change. This directly corroborates the previously community-sourced `+12`, day 2, 10:00 rule and confirms that the event affects both visible owned branches.

## 2. Facility selection reserves aid and cancellation refunds it

### Company sample

At Sep 2 10:30:

1. cash before selection: `¥7,330,572`;
2. facility menu: `会社`, `援助額 ¥5,400,000`;
3. on entering location selection: cash `¥1,930,572`;
4. exact entry debit: `¥5,400,000`;
5. cancelling location selection restores cash to `¥7,330,572`.

While the company remains selected, moving across the map alternates between `誘致不可能` and `誘致可能`. Readable possible-location totals include `¥6,800,000`, `¥6,700,000`, `¥6,300,000` and `¥5,900,000` while game time and cash remain paused.

### Pool sample

At Sep 2 11:52 the same flow repeats independently:

1. cash before selection: `¥7,331,292`;
2. facility menu: `プール`, `援助額 ¥1,800,000`;
3. on entering location selection: cash `¥5,531,292`;
4. exact entry debit: `¥1,800,000`;
5. cancelling restores cash to `¥7,331,292`.

Readable possible-location totals include `¥4,200,000`, `¥7,300,000`, `¥6,000,000`, `¥6,200,000`, `¥5,100,000` and `¥3,800,000`.

### Boundary established by the two samples

- The selected facility's displayed aid is reflected in cash immediately when location selection begins.
- Cancellation returns exactly that aid amount.
- The numeric total depends on target location even though facility, time and reserved aid remain unchanged.
- `誘致可能` can be displayed when the quoted total exceeds the post-reservation cash balance; therefore this label must not be implemented as a simple `cash >= quote` test.

The footage does not confirm a placement. It therefore does **not** yet establish the final debit, construction timing, insufficient-funds outcome, or a universal equation for the displayed total. The visual pattern is consistent with the separately sourced `facility aid + target land` hypothesis, but is not by itself proof of that formula.

## 3. Two more ordinary rollovers

### Sep 2 → Sep 3

| date/time | weather | cash | bottom-right yen field |
|---|---|---:|---:|
| Sep 2 23:58 | 雨 | `¥1,752,342` | `¥87,520` |
| Sep 3 00:00 | 曇 | `¥1,752,342` | `¥0` |
| Sep 3 00:02 | 曇 | `¥1,657,998` | `¥0` |

Post-midnight debit: exactly `¥94,344`.

### Sep 3 → Sep 4

| date/time | weather | cash | bottom-right yen field |
|---|---|---:|---:|
| Sep 3 23:58 | 曇 | `¥1,755,243` | `¥147,840` |
| Sep 4 00:00 | 曇 | `¥1,755,643` | `¥0` |
| Sep 4 00:02 | 晴れ | `¥1,661,299` | `¥0` |

A `¥400` transaction lands at the boundary, but the clean 00:00 → 00:02 difference is again exactly `-¥94,344`.

Together with Jul 1 → 2, Jul 2 → 3 and Aug 2 → 3, five ordinary transitions now show the same `¥94,344` post-midnight debit. July 3 → 4 remains a counterexample with additional/different amounts, so the value is a repeated configuration-specific anchor, not a universal hard-coded daily charge.

## 4. Implementation boundary

Safe to implement now:

- direct-mail payment at its trigger event;
- direct-mail +12 popularity application to all supplied owned stores;
- inducement aid reservation on placement entry;
- location-specific quote observations;
- exact aid refund on cancellation.

Still unresolved:

- payment timing of the other four promotion methods;
- promotion target snapshot rules for stores opened/closed near the event;
- inducement total-price formula and successful-placement debit;
- facility construction delay/activation;
- composition of the repeated `¥94,344` debit.

## Next target

Continue V03 after `00:43:20`. Prioritize the next completed facility placement or economic menu, another store-comparison snapshot, identifiable checkout intervals, and the Sep day-4 → next-month report.
