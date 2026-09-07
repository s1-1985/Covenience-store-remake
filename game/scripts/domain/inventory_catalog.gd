class_name InventoryCatalog
extends RefCounted

const InventoryStateScript := preload("res://scripts/domain/inventory_state.gd")

var products: Dictionary = {}
var product_order: Array[String] = []
var _product_configs: Array


func _init(product_configs: Array) -> void:
    _product_configs = product_configs.duplicate(true)
    assert(not _product_configs.is_empty())
    reset()


func reset() -> void:
    products.clear()
    product_order.clear()
    for product_config in _product_configs:
        var product: InventoryState = InventoryStateScript.new(product_config)
        assert(not products.has(product.product_id))
        products[product.product_id] = product
        product_order.append(product.product_id)


func get_product(product_id: String) -> InventoryState:
    assert(products.has(product_id))
    return products[product_id]


func try_take_one(product_id: String) -> Dictionary:
    var product := get_product(product_id)
    if not product.try_take_one():
        return {}
    return {
        "product_id": product.product_id,
        "quantity": 1,
        "unit_price_yen": product.sale_price_yen,
    }


func total_stock_units() -> int:
    var total := 0
    for product in products.values():
        total += product.stock_units
    return total


func has_stock() -> bool:
    return total_stock_units() > 0


func expected_full_sellout_revenue_yen() -> int:
    var total := 0
    for product in products.values():
        total += product.initial_stock_units * product.sale_price_yen
    return total
