class_name ProgramProgression
extends RefCounted

const LIMITS := [[50000, 100000, 200000, 400000, 500000], [100000000, 200000000, 300000000, 400000000, 600000000], [3000, 8000, 14000, 18000, 20000], [10, 30, 50, 70, 90]]
static func owner_rating(stores: Array, visitors: int, population: int) -> Dictionary:
    if stores.is_empty():
        return {"parts": [0, 0, 0, 0, 0], "total": 0, "annual_sales": 0, "mean_rating": 0}
    var sales := 0
    var rating := 0
    for store in stores:
        var value := int(store["annual_sales"])
        var next := ((sales + value + 2147483648) & 4294967295) - 2147483648
        sales = 2147483647 if sales > 0 and value > 0 and next < 0 else next
        rating += int(store["rating"])
    var mean := rating / stores.size()
    var values := [visitors & 4294967295, sales, population, mean]
    var parts: Array = [2 * stores.size()]
    var total := 2 * stores.size()
    for i in 4:
        var points := 0
        for threshold in LIMITS[i]:
            points += 4 * int(values[i] >= threshold)
        parts.append(points)
        total += points
    return {"parts": parts, "total": 100 if total >= 96 else total, "annual_sales": sales, "mean_rating": mean}
