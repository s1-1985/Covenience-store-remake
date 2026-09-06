# 0036 Observed monthly report and threshold events

## Context

First-title V03 footage now directly confirms a September report displayed after the October rollover with `収支`, `他経費`, and `町人口`, plus arithmetic comparison values against the prior displayed month. The same footage confirms a branch-specific notification that the previous month's sales exceeded ¥4,000,000. Earlier evidence also contains a ¥3,000,000 notification.

The footage does **not** recover the monthly aggregation/settlement formula, the composition of `収支` or `他経費`, or the threshold tiering rules. It is also unknown whether multiple crossed thresholds are queued or only one tier is emitted.

## Decision

Add a monthly-report observation runtime that:

- stores displayed report values as caller-supplied observations;
- computes only direct arithmetic deltas when both current and previous values are known;
- preserves missing report values as `None` rather than zero;
- records sales-threshold notifications explicitly per store/month;
- validates the observed Japanese wording `越えました` as strictly greater than the supplied threshold when sales are known;
- never derives monthly report values from representative-day samples or the cash ledger;
- never infers additional threshold notifications from one observed notification.

## Evidence-safe boundary

The following remain unresolved and must stay outside this runtime until stronger first-title evidence arrives:

- representative-day → monthly aggregation formula;
- monthly settlement ordering and hidden debit/credit components;
- exact meaning/composition of `収支` and `他経費`;
- threshold tier list and whether tiers are cumulative, exclusive, or queued;
- whether threshold notifications pause time or how they are ordered relative to other month-start notifications;
- platform differences between PS and SS.

## Evidence

- `docs/research/video-v03-october-rollover-2026-09-06.md`
- `docs/research/video-v03-aug-sep-runtime-2026-09-06.md`

No sequel values or formulas are used.
