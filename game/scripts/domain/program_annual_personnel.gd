extends RefCounted
# CONFIRMED_BINARY 8001B194 stores3; 8002A150..A198 takes low signed32
# product before signed /100. Wages are hourly in the original person record.
const DEFAULT_RAISE_PERCENT := 3
static func wage(hourly: int, percent := DEFAULT_RAISE_PERCENT) -> int:
    var product := ((hourly*(100+percent)+0x80000000)&0xffffffff)-0x80000000
    return product/100

# 8002A2F8..A47C processes all35 people in source order, regardless of
# employment/owner. Current stamina, skills and stored ceilings are unchanged.
static func age_person(age: int, rng) -> Dictionary:
    var next := mini(127,age+1)
    var boosted := next>=127
    if not boosted and next>=80:boosted=rng.randi()%5==0
    return {"age":next,"boosted":boosted}
