class_name InventoryState
extends RefCounted

var product_id: String
var fixture_id: String
var stock_units: int
var sale_price_yen: int
var initial_stock_units: int
var restock_unit_cost_yen: int
# Task #68: which product_catalog category this instance was actually
# procured as, when known (try_procure_product() passes its own catalog_id
# argument straight through). Empty for the two pre-catalog prototype
# products in vertical_slice.json's "products" array (prototype-bread/
# prototype-drink predate the catalog system, task #38) -- store_view.gd
# falls back to a display-only guess for those rather than this field
# asserting a category that was never actually recorded.
var catalog_id: String


func _init(product_config: Dictionary) -> void:
    product_id = str(product_config["id"])
    fixture_id = str(product_config["fixture_id"])
    initial_stock_units = int(product_config["initial_stock_units"])
    sale_price_yen = int(product_config["sale_price_yen"])
    restock_unit_cost_yen = int(product_config["restock_unit_cost_yen"])
    catalog_id = str(product_config.get("catalog_id", ""))
    assert(not product_id.is_empty() and not fixture_id.is_empty())
    assert(initial_stock_units >= 0 and sale_price_yen >= 0 and restock_unit_cost_yen >= 0)
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
