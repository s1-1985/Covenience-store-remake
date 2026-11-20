extends RefCounted

# CONFIRMED_BINARY 80027C80..800280BC. The old analysis bridge mislabels
# absolute8012BF60 as C6C; relative to8012B2F8 it is C68 (evaluation).
const CASH_TRIGGER := 1500000000
const CASH_TARGET := 1000000000
const RATING_GAIN := 5

static func amount(cash: int, period: int, hour: int, minute: int) -> int:
    return cash-CASH_TARGET if period==1 and hour==0 and minute==0 and cash>CASH_TRIGGER else 0

static func next_rating(rating: int, active: bool, owner: int, company: int, donated: bool) -> int:
    return mini(100,rating+RATING_GAIN) if donated and active and owner==company else rating
