class_name InventoryState
extends RefCounted

var product_id: String
var fixture_id: String
var stock_units: int
var sale_price_yen: int
var initial_stock_units: int


func _init(product_config: Dictionary) -> void:
    product_id = str(product_config["id"])
    fixture_id = str(product_config["fixture_id"])
    initial_stock_units = int(product_config["initial_stock_units"])
    sale_price_yen = int(product_config["sale_price_yen"])
    assert(not product_id.is_empty() and not fixture_id.is_empty())
    assert(initial_stock_units >= 0 and sale_price_yen >= 0)
    reset()


func reset() -> void:
    stock_units = initial_stock_units


func try_take_one() -> bool:
    if stock_units <= 0:
        return false
    stock_units -= 1
    return true


func add_explicit_units(quantity: int) -> void:
    assert(quantity > 0)
    stock_units += quantity
