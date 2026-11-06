class_name ProgramRules
extends RefCounted

# CONFIRMED_BINARY: checkout.service_gate, staff_energy, inventory_callers.
static func checkout_ready(register_skill: int, customer_threshold: int, rng) -> bool:
    if rng.randi_range(1, 100) > register_skill:
        return false
    return rng.randi_range(1, 100) <= customer_threshold

static func refill_amount(ability: int, rng) -> int:
    if rng.randi_range(1, 100) > ability:
        return 0
    return ability / 10 + 1

static func working_energy(energy: int, rng) -> int:
    return energy - 1 if energy > 0 and rng.randi() & 3 == 0 else energy

static func resting_energy(energy: int, maximum: int, improved: bool, rng) -> int:
    if energy >= maximum:
        return energy
    return energy + 1 if improved or rng.randi() & 1 == 0 else energy
