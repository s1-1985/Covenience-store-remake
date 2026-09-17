from __future__ import annotations

REPRESENTATIVE_DAYS_PER_MONTH = 4
MONTH_MULTIPLIER = 8

MONTH_MULTIPLIER_SOURCE = (
    "strategy guide quick reference (\"時間\", book page 2-3): "
    "\"1月=4日間×8\" / \"4日間の収支を8倍することで、1月の収支が決定する。"
    "実質32日間の営業と考えよう。\""
)
"""This is CONFIRMED_OFFICIAL, not a REMAKE_BALANCED_DEFAULT guess: the guide
states the multiplier itself directly. What it does not state is how each
representative day's own net result is computed (which costs are already
netted out, whether day 4 -- a holiday per clock.py's representative-day
typing -- is weighted the same as days 1-3, etc.); this module only turns an
already-known 4-day net result into the displayed monthly figure, matching
monthly_report.py's own pattern of accepting caller-supplied values rather
than deriving them internally.
"""


def aggregate_representative_days_to_month(four_day_net_result_yen: int) -> int:
    """月間収支 = 代表4日間の(経費差引後)純利益 × 8.

    Source: MONTH_MULTIPLIER_SOURCE. `four_day_net_result_yen` is whatever
    the caller's own day-end/representative-day accounting already resolved
    for days 1-4 combined; this function does not itself compute that value.
    """
    return four_day_net_result_yen * MONTH_MULTIPLIER
