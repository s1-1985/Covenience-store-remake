class_name OperatingStatement
extends RefCounted

# CONFIRMED_BINARY: SLPS_007.82 80029918..80029D30.
# A five-column operating ledger is scaled x8; cash receives the remaining
# seven copies of its profit. Cash balance changes themselves are not a ledger.
# Evidence and small source-derived examples: docs/decisions/0206-*.md.
const MONTH_MULTIPLIER := 8
const EXPENSE_FIELDS := ["maintenance_yen", "wages_yen", "promotion_yen", "goods_yen"]


# CONFIRMED_BINARY: recovered.py ledger_profit/month_close and finance_close.py
# (8001CCC0, 80029918..29D30) use signed 32-bit words. The older prototype
# path stays available; native source callers opt into the recovered width.
static func signed32(value: int) -> int:
    return ((value + 0x80000000) & 0xffffffff) - 0x80000000


static func close_cash(cash: int, adjustment: int) -> int:
    return signed32(signed32(cash) + signed32(adjustment))


static func project(representative: Dictionary, source_width := false) -> Dictionary:
    var period := representative.duplicate(true)
    var monthly := {}
    var expenses := 0
    for field in EXPENSE_FIELDS:
        var amount := int(period.get(field, 0))
        if source_width:
            amount = signed32(amount)
        period[field] = amount
        expenses += amount
        monthly[field] = signed32(amount * MONTH_MULTIPLIER) if source_width else amount * MONTH_MULTIPLIER
    var sales := int(period.get("sales_yen", 0))
    if source_width:
        sales = signed32(sales)
    period["sales_yen"] = sales
    monthly["sales_yen"] = signed32(sales * MONTH_MULTIPLIER) if source_width else sales * MONTH_MULTIPLIER
    var profit := signed32(sales - expenses) if source_width else sales - expenses
    return {
        "representative": period,
        "monthly": monthly,
        "four_day_net_result_yen": profit,
        "month_result_yen": signed32(profit * MONTH_MULTIPLIER) if source_width else profit * MONTH_MULTIPLIER,
        "adjustment_yen": signed32(profit * (MONTH_MULTIPLIER - 1)) if source_width else profit * (MONTH_MULTIPLIER - 1),
    }
