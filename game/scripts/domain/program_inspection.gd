extends RefCounted
# CONFIRMED_BINARY:2359C monthly reset;60FBC quote;61184 real company fee.
static func expires(period: int, hour: int, subhour: int) -> bool:
    return period==1 and hour==0 and subhour==0
static func fee(flag: int) -> int:
    return 0 if flag==1 else 500000
static func affordable(cash: int, cost: int) -> bool:
    return cash>=cost
