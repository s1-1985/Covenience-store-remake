extends SceneTree

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const CONFIG_PATH := "res://data/vertical_slice.json"
const MAX_STEPS := 256


func _initialize() -> void:
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("vertical slice config did not parse as a dictionary")
        return

    var config: Dictionary = parsed
    var simulation: VerticalSliceSimulation = VerticalSliceSimulationScript.new(config)
    var initial_cash := simulation.cash_yen
    var initial_stock := simulation.stock_units
    var steps := _run_visit(simulation)

    if simulation.customer_phase != "done":
        _fail("vertical slice did not complete within %d steps" % MAX_STEPS)
        return
    if simulation.completed_sales != 1:
        _fail("vertical slice must complete exactly one sale")
        return
    if simulation.stock_units != initial_stock - 1:
        _fail("vertical slice must remove exactly one stock unit")
        return
    if simulation.cash_yen != initial_cash + simulation.sale_price_yen:
        _fail("vertical slice cash did not match the completed sale")
        return

    while simulation.stock_units > 0:
        if not simulation.start_next_customer():
            _fail("completed visit did not allow the next customer")
            return
        steps += _run_visit(simulation)
        if simulation.customer_phase != "done":
            _fail("repeat customer did not complete")
            return

    var sales_after_sellout := simulation.completed_sales
    if not simulation.start_next_customer():
        _fail("sellout visit could not start")
        return
    steps += _run_visit(simulation)
    if simulation.completed_sales != sales_after_sellout:
        _fail("empty shelf visit must not create a sale")
        return
    if simulation.completed_visits != simulation.started_visits:
        _fail("every started visit must complete")
        return

    print("Vertical-slice headless smoke passed in %d steps." % steps)
    quit(0)


func _run_visit(simulation: VerticalSliceSimulation) -> int:
    var steps := 0
    while simulation.customer_phase != "done" and steps < MAX_STEPS:
        simulation.step()
        steps += 1
    return steps


func _fail(message: String) -> void:
    push_error(message)
    quit(1)
