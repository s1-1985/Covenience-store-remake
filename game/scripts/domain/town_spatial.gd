class_name TownSpatial
extends RefCounted

# Task #59: mirrors reference_sim/conveni_sim/remake_town_spatial.py -- see
# that module's own docstring for the full evidence citation (strategy
# guide's distance diagram, book pages 6-7: a store-construction minimum
# spacing of 5 tiles, plus tobacco/alcohol/medicine permit mutual-exclusion
# radii of 7/11/15 tiles, both CONFIRMED_OFFICIAL). Only the piece with an
# actual caller in this client is ported here (permit-exclusion enforcement
# in VerticalSliceSimulation.try_purchase_permit()); the reference_sim
# module's trade_area_overlap_ratio() has no caller here yet (no rival-AI
# decision loop exists in this client) and is not ported.
#
# REMAKE_BALANCED_DEFAULT: the distance metric (Chebyshev, i.e. a diagonal
# tile counts as 1 step away) is this project's own choice, not confirmed
# by the guide -- see remake_town_spatial.py's own note on the same
# ambiguity.

const STORE_CONSTRUCTION_MIN_DISTANCE_TILES := 5


func chebyshev_distance_tiles(a: Vector2i, b: Vector2i) -> int:
    return maxi(absi(a.x - b.x), absi(a.y - b.y))


# CONFIRMED_OFFICIAL rule (guide book page 9: a store may not acquire a
# permit within that permit's exclusion radius of another store that
# ALREADY holds the same permit). other_permit_holder_positions must
# already be filtered by the caller to stores holding this specific permit.
func can_acquire_permit_at(
    exclusion_distance_tiles: int,
    candidate: Vector2i,
    other_permit_holder_positions: Array[Vector2i]
) -> bool:
    for holder in other_permit_holder_positions:
        if chebyshev_distance_tiles(candidate, holder) < exclusion_distance_tiles:
            return false
    return true
