class_name OperatingStatement
extends RefCounted

# CONFIRMED_BINARY: SLPS_007.82 80029918..80029D30.
# A five-column operating ledger is scaled x8; cash receives the remaining
# seven copies of its profit. Cash balance changes themselves are not a ledger.
# Evidence and small source-derived examples: docs/decisions/0206-*.md.
const MONTH_MULTIPLIER := 8
const EXPENSE_FIELDS := ["maintenance_yen", "wages_yen", "promotion_yen", "goods_yen"]


static func project(representative: Dictionary) -> Dictionary:
    var period := representative.duplicate(true)
    var monthly := {}
    var expenses := 0
    for field in EXPENSE_FIELDS:
        var amount := int(period.get(field, 0))
        period[field] = amount
        expenses += amount
        monthly[field] = amount * MONTH_MULTIPLIER
    var sales := int(period.get("sales_yen", 0))
    period["sales_yen"] = sales
    monthly["sales_yen"] = sales * MONTH_MULTIPLIER
    var profit := sales - expenses
    return {
        "representative": period,
        "monthly": monthly,
        "four_day_net_result_yen": profit,
        "month_result_yen": profit * MONTH_MULTIPLIER,
        "adjustment_yen": profit * (MONTH_MULTIPLIER - 1),
    }
