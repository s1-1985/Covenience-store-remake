class_name EconomyState
extends RefCounted

var cash_yen: int
var completed_sales: int
var sale_records: Array[Dictionary] = []
var expense_records: Array[Dictionary] = []
var month_end_records: Array[Dictionary] = []
var _initial_cash_yen: int
var _next_sale_sequence := 1
var _settled_customer_ids: Dictionary = {}


func _init(economy_config: Dictionary) -> void:
    _initial_cash_yen = int(economy_config["initial_cash_yen"])
    assert(_initial_cash_yen >= 0)
    reset()


func reset() -> void:
    cash_yen = _initial_cash_yen
    completed_sales = 0
    sale_records.clear()
    expense_records.clear()
    month_end_records.clear()
    _settled_customer_ids.clear()
    _next_sale_sequence = 1


func settle_basket(
    customer_id: String,
    minute_of_day: int,
    lines: Array[Dictionary]
) -> Dictionary:
    assert(not customer_id.is_empty())
    assert(minute_of_day >= 0 and minute_of_day < 24 * 60)
    assert(not lines.is_empty() and not _settled_customer_ids.has(customer_id))
    var total_yen := 0
    for line in lines:
        assert(line.has("product_id") and not str(line["product_id"]).is_empty())
        var quantity := int(line["quantity"])
        var unit_price_yen := int(line["unit_price_yen"])
        assert(quantity > 0 and unit_price_yen >= 0)
        total_yen += quantity * unit_price_yen
    var record := {
        "transaction_id": "prototype-sale-%d" % _next_sale_sequence,
        "customer_id": customer_id,
        "minute_of_day": minute_of_day,
        "lines": lines.duplicate(true),
        "total_yen": total_yen,
    }
    _next_sale_sequence += 1
    _settled_customer_ids[customer_id] = true
    sale_records.append(record)
    cash_yen += total_yen
    completed_sales = sale_records.size()
    return record.duplicate(true)


func last_sale_record() -> Dictionary:
    if sale_records.is_empty():
        return {}
    return sale_records.back().duplicate(true)


func sale_record_for_customer(customer_id: String) -> Dictionary:
    for record in sale_records:
        if record["customer_id"] == customer_id:
            return record.duplicate(true)
    return {}


func recorded_revenue_yen() -> int:
    var total := 0
    for record in sale_records:
        total += int(record["total_yen"])
    return total


func record_explicit_expense(
    expense_type: String,
    minute_of_day: int,
    amount_yen: int,
    details: Dictionary = {}
) -> Dictionary:
    # Task #78: amount_yen may be negative to record a rebate (e.g.
    # try_sell_fixture()'s partial refund) through this same ledger rather
    # than adding a second, parallel "income" record type -- every existing
    # caller before this task always passed a non-negative amount, so
    # relaxing this assert changes no prior caller's behavior.
    assert(not expense_type.is_empty())
    assert(minute_of_day >= 0 and minute_of_day < 24 * 60)
    var record := {
        "expense_id": "prototype-expense-%d" % (expense_records.size() + 1),
        "expense_type": expense_type,
        "minute_of_day": minute_of_day,
        "amount_yen": amount_yen,
        "details": details.duplicate(true),
    }
    expense_records.append(record)
    cash_yen -= amount_yen
    return record.duplicate(true)


func recorded_expenses_yen() -> int:
    var total := 0
    for record in expense_records:
        total += int(record["amount_yen"])
    return total


func record_month_end_settlement(
    minute_of_day: int,
    amount_yen: int,
    details: Dictionary = {}
) -> Dictionary:
    assert(minute_of_day >= 0 and minute_of_day < 24 * 60)
    var record := {
        "settlement_id": "prototype-month-end-%d" % (month_end_records.size() + 1),
        "minute_of_day": minute_of_day,
        "amount_yen": amount_yen,
        "details": details.duplicate(true),
    }
    month_end_records.append(record)
    cash_yen += amount_yen
    return record.duplicate(true)


func snapshot() -> Dictionary:
    return {
        "cash_yen": cash_yen,
        "sale_records": sale_records.duplicate(true),
        "expense_records": expense_records.duplicate(true),
        "month_end_records": month_end_records.duplicate(true),
        "next_sale_sequence": _next_sale_sequence,
    }


func restore_snapshot(data: Dictionary) -> void:
    cash_yen = int(data["cash_yen"])
    sale_records.assign(data["sale_records"])
    expense_records.assign(data["expense_records"])
    month_end_records.assign(data["month_end_records"])
    completed_sales = sale_records.size()
    _next_sale_sequence = int(data["next_sale_sequence"])
    # Deliberately cleared, not rebuilt from the restored sale_records'
    # customer_ids: the caller's customer roster is not restored by this
    # snapshot (see VerticalSliceSimulation.load_state()'s own note on
    # this) and always restarts its id sequence from "<prefix>-1", so a
    # historical sale settled under that same recycled id would otherwise
    # permanently block the freshly-admitted customer of the same name
    # from ever completing a sale after load.
    _settled_customer_ids.clear()
