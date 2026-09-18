class_name ChainVisitorMilestone
extends RefCounted

# --- CONFIRMED house rule --------------------------------------------------
#
# Ported from reference_sim/conveni_sim/visitor_milestone.py's
# ChainVisitorMilestoneRuntime. First-title PS/SS research supports a free
# popularity +100 event every 10,000 cumulative visitors across the
# player's store chain, firing at 00:00 on the day after the milestone is
# observed. Research has not established whether merely crossing a
# threshold without observing the exact multiple must still fire, nor how
# multiple thresholds crossed in one interval are queued; this port
# therefore only schedules exact observed multiples and refuses to invent
# catch-up behavior for a skipped threshold, exactly like the Python
# source (observe_total_visitors() asserts rather than guesses when a
# threshold is skipped).
#
# "Across the player's store chain" is ported as-is even though this
# client currently plays only one store: cumulative visitors are whatever
# total the caller supplies (currently that single store's completed-visit
# count -- VerticalSliceSimulation._observe_chain_visitor_milestone()), so
# this runtime already generalizes correctly the day a second playable
# store is added, without needing to change.

const THRESHOLD_STEP := 10000
const POPULARITY_GAIN := 100

var last_observed_total: int
var next_threshold: int
var events: Array[Dictionary] = []


func _init() -> void:
    last_observed_total = 0
    next_threshold = THRESHOLD_STEP


func observe_total_visitors(
    total_visitors: int, notified_day_index: int, notified_hour: int
) -> Dictionary:
    assert(total_visitors >= 0)
    assert(total_visitors >= last_observed_total)
    assert(notified_day_index >= 1)
    assert(notified_hour >= 0 and notified_hour <= 23)
    # A skipped threshold (crossed without an exact observed multiple) is
    # unresolved catch-up behavior, not something to invent -- see the
    # Python source's own ValueError for the same condition.
    assert(total_visitors <= next_threshold)
    last_observed_total = total_visitors
    if total_visitors != next_threshold:
        return {}
    var event := {
        "threshold_visitors": next_threshold,
        "observed_total_visitors": total_visitors,
        "trigger_day_index": notified_day_index + 1,
        "trigger_hour": 0,
        "popularity_gain": POPULARITY_GAIN,
        "fired": false,
    }
    events.append(event)
    next_threshold += THRESHOLD_STEP
    return event


func pop_due(now_day_index: int, now_hour: int) -> Array[Dictionary]:
    var due: Array[Dictionary] = []
    for event in events:
        if bool(event["fired"]):
            continue
        var trigger_day_index: int = int(event["trigger_day_index"])
        var trigger_hour: int = int(event["trigger_hour"])
        if now_day_index > trigger_day_index or (
            now_day_index == trigger_day_index and now_hour >= trigger_hour
        ):
            event["fired"] = true
            due.append(event)
    return due
