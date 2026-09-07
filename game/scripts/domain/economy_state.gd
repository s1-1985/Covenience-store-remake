class_name EconomyState
extends RefCounted

var cash_yen: int
var completed_sales: int
var sale_records: Array[Dictionary] = []
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
