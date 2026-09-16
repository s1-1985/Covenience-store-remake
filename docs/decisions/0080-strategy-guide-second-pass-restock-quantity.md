# Decision 0080: Second full re-read of the strategy guide scans

## Status

Accepted.

## Context

The user re-uploaded the same 4 strategy-guide PDF scans (this session's container had
been recycled, dropping the earlier copies) and explicitly asked for another full,
maximal-effort read, rejecting deferral: several items decisions 0077/0078 had marked
"illegible at this resolution" should be re-attempted now that the files are available
again, since the earlier "can't read it" conclusion was never independently re-tested.

## What this pass did

Re-read all 115 pages across the 4 files page-by-page, including a fresh, individual
(single-page) re-render of the specific pages decisions 0077/0078 had flagged as
unreadable, to test whether a cleaner render changes the legibility verdict. Also
discovered that the previously-recorded book-page citations in decisions 0077/0078 (e.g.
"オールテクニックガイド, 書籍頁68-79") pointed at the wrong volume: the guide is
physically two bound volumes — "新人店長実習マニュアル/攻略&データブック" (file 1+2,
pages 6-143, its own "第1章-第4章") and "レイアウトデザインセレクション74" (file 3+4,
its own independent page-1 restart, containing a *second* "クイックリファレンス" +
"パーソナルデザインBOOK" + "攻略&データブック" with the real オールテクニックガイド at
pages 66-79 and データリスト at pages 84-95). The earlier citations were transcribed
against the wrong volume's page numbers; this is corrected here, not a new source.

## Decision

**Implemented — `PRODUCT_CATEGORY_PRICING.restock_quantity` (new field, all 26
categories):** decision 0078 left the DATA LIST product table's "1回補給" (restock
quantity) column untranscribed, citing resolution limits. On this pass the same table
(book page 85 of the レイアウトデザインセレクション volume) was re-read in isolation
and found clearly legible. Confidence is raised further by a full cross-check: every
one of the 26 rows' already-confirmed `standard_retail_price_yen`/`cost_rate_pct`/
`margin_rate_pct` values, read independently from this second copy of the table,
matched the existing `baseline_data.py` values exactly (26/26), which is strong
evidence the new `restock_quantity` column was read from the correct cells in the
correct row/column alignment. Added as `Optional[EvidenceValue]` on
`ProductCategoryPricing`, evidence `CONFIRMED_OFFICIAL`.

**Independently re-confirmed, not re-implemented:** re-read the オールテクニックガイド
formula pages (68-79) that decision 0079's runtime implementation was based on. Every
formula already implemented in `store_value.py`/`store_rating.py`/`store_events.py`/
`inducement.py`/`promotion.py` is printed identically on this cleaner second read
(service/security/cleaning value formulas, the security-facility bonus table, the
5-star rank/internal-value table, the 1/6 angry-customer and shoplifting/donation point
values, the promotion decay ≤3-star trigger, the new-store land-cost formula). No code
change follows from this since it only reconfirms decision 0079's existing
implementation; it is recorded here as a fact-check, not left unstated.

**Investigated and explicitly NOT implemented, with the reason recorded rather than
silently dropped:**

- **Fixture x product-category ○/× matrix** (DATA LIST section 2, book pages 86-89 of
  the second volume): now visually legible as a grid, but re-deriving
  `compatible_product_categories` from it would require exact column-to-category
  alignment across a dense 26-column grid with no per-cell labels in the render, which
  is a materially higher misalignment risk than the existing source (each fixture's own
  large-font "取扱商品" text list, already used per decision 0078). Since the matrix
  would only be used to *replace* an already-higher-confidence source, not to fill a gap,
  it was not transcribed.
- **Staff skill growth-ceiling ranges** (DATA LIST section 3, book pages 90-91): this
  table prints, for all 35 candidates, a second number per skill beyond the initial
  value already in `STAFF_CANDIDATES` (an apparent growth ceiling, e.g. "12-36"). This
  is new information no existing field covers. However, a direct cross-check attempt
  failed: 秋本三四郎 (akimoto_sanshiro)'s `academic_background` reads as `70` in the
  already-confirmed `STAFF_CANDIDATES` row (sourced from decision 0078's read of a
  different page), but this second table's same field reads as `65` on this pass. This
  is either a genuine transcription slip on one of the two reads, or a real
  guide-internal inconsistency; either way it means per-row column alignment on this
  particular table cannot currently be trusted at the single-digit level. Per the
  never-silently-overwrite policy, `academic_background` was **not** changed, and the
  growth-ceiling columns were **not** added, rather than risk seeding the roster with
  misaligned numbers under a `CONFIRMED_OFFICIAL` label they would not deserve. Flagged
  in `docs/handoff/chatgpt-review-notes.md` for a dedicated, single-page-at-a-time
  re-verification pass.
- **Customer archetype 10-column behavior-tuning values** (ス/素/マ/集/買/価/距/サ/平/
  休, `CUSTOMER_VISIT_SCHEDULE.behavior_stats_raw`): visually clearer on this pass than
  decision 0078's assessment, but decomposing ~140 rows x 10 columns into individually
  named, `CONFIRMED_OFFICIAL`-labeled fields carries the same alignment risk just
  demonstrated on the smaller staff table above, at roughly 7x the row count. Left as
  the existing raw tuple; not attempted this pass.
- **DATA LIST product table's remaining two trailing numeric columns** (still present
  beyond `restock_quantity`): the guide's own sidebar explains two *concepts*
  (per-shelf max-maintenance/max-capacity, and a single "demand example" figure) but
  does not label which physical column is which with certainty at this resolution. Left
  unmapped, same as decision 0078.

## Evidence boundary

`restock_quantity` is `EvidenceLevel.CONFIRMED_OFFICIAL` citing `STRATEGY_GUIDE`,
justified by the 26/26 cross-check described above. Every item in the "not implemented"
list above is a case where re-reading raised legibility but not alignment confidence;
none were guessed into the codebase.

Tests: `reference_sim/tests/test_strategy_guide_deferred_datasets.py`
(`ProductRestockQuantityTests`) checks all 26 values and that every category has a
non-`None` `restock_quantity`. Full suite: 542 passed, 1 xfailed (pre-existing,
unrelated).
