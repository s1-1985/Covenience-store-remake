class_name ProgramRandom
extends RefCounted

# CONFIRMED_BINARY SLPS_007.82 LCG, shared by the recovered runtime.
var seed := 0
var state: int:
    get:
        return seed
    set(value):
        seed = value & 0xffffffff

func randi() -> int:
    seed = (seed * 1103515245 + 12345) & 0xffffffff
    return (seed >> 16) & 0x7fff

func randi_range(low: int, high: int) -> int:
    assert(high >= low)
    return low + self.randi() % (high - low + 1)

func randf() -> float:
    return float(self.randi()) / 32768.0
