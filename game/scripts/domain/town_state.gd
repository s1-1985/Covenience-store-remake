class_name TownState
extends RefCounted

# Mirrors reference_sim/conveni_sim/town.py's TownState exactly: this is
# deliberately just tracked state, not a town/map spatial simulation.
# reference_sim has no spatial model of the town map, facility placement, or
# population growth rules, and this client does not invent one either
# (PROJECT_MEMORY.md section 17: "町発展の一般式" is an explicit research
# gap, not something to guess). A caller (config, or a future town/map
# layer) is responsible for keeping these two numbers current.

var population: int
var store_count_including_rivals: int


func _init(town_config: Dictionary) -> void:
    population = int(town_config["population"])
    store_count_including_rivals = int(town_config["store_count_including_rivals"])
    assert(population >= 0)
    assert(store_count_including_rivals >= 0)
