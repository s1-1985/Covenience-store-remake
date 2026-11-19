extends RefCounted
# CONFIRMED_BINARY: 80048728 scale, 80047C00 bitmap; see decision0219.
const MISSING := -2147483648
static func plan(history: Array, chain: Array, counts: Array) -> Dictionary:
    var values: Array = []
    var averages: Array = []
    var maximum := 1
    for i in mini(60,mini(history.size(),mini(chain.size(),counts.size()))):
        if history[i] == null or chain[i] == null or int(history[i]) == MISSING or int(chain[i]) == MISSING or int(counts[i]) <= 0: break
        var value := int(history[i])
        var average: int = int(chain[i]) / int(counts[i])
        values.append(value)
        averages.append(average)
        maximum = maxi(maximum,maxi(absi(value),absi(average)))
    var axis: int = maxi(1,(maximum+999999)/1000000)*1000000
    var oldest := values.duplicate()
    oldest.reverse()
    return {"valid":values.size(),"averages":averages,"axis_yen":axis,"oldest_first":oldest}
static func height(value: int, axis: int) -> int:
    var units: int = value / 10000
    return mini(56,absi(units)*56/(axis/10000))
